from discord.ext import commands, tasks
import discord
from sqlalchemy import select, update, delete
from database.karma_db import Database, KarmaTable, RewardsTable


class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.bot.loop.create_task(self.db.init_db())
        self.give_voice_karma.start()

    def cog_unload(self):
        self.give_voice_karma.cancel()

    @discord.Cog.listener()
    async def on_guild_join(self, guild):
        async with self.db.get_session() as session:
            for member in guild.members:
                if not member.bot:
                    result = await session.execute(
                        select(KarmaTable).filter_by(user_id=member.id, guild_id=guild.id)
                    )
                    if result.scalars().first() is None:
                        session.add(KarmaTable(user_id=member.id, guild_id=guild.id))
            await session.commit()

    @discord.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        user_id = message.author.id
        async with self.db.get_session() as session:
            result = await session.execute(
                select(KarmaTable).filter_by(user_id=user_id, guild_id=guild_id)
            )
            karma_entry = result.scalars().first()
            current_time = message.created_at.timestamp()
            if not karma_entry:
                session.add(
                    KarmaTable(user_id=user_id, guild_id=guild_id, karma=1, timestamp_last_message=current_time))
            elif karma_entry.timestamp_last_message < current_time - 60:
                stmt = (
                    update(KarmaTable)
                    .where(KarmaTable.user_id == user_id, KarmaTable.guild_id == guild_id)
                    .values(karma=KarmaTable.karma + 1, timestamp_last_message=current_time)
                )
                await session.execute(stmt)
            await session.commit()

    @tasks.loop(minutes=1)
    async def give_voice_karma(self):
        async with self.db.get_session() as session:
            for guild in self.bot.guilds:
                for channel in guild.voice_channels:
                    active_users = [
                        member
                        for member in channel.members
                        if not member.bot and not member.voice.self_mute and not member.voice.self_deaf
                    ]
                    if len(active_users) >= 2:
                        for user in active_users:
                            result = await session.execute(
                                select(KarmaTable).filter_by(user_id=user.id, guild_id=guild.id)
                            )
                            karma_entry = result.scalars().first()
                            if not karma_entry:
                                session.add(KarmaTable(user_id=user.id, guild_id=guild.id, karma=1))
                            else:
                                stmt = (
                                    update(KarmaTable)
                                    .where(KarmaTable.user_id == user.id, KarmaTable.guild_id == guild.id)
                                    .values(karma=KarmaTable.karma + 1)
                                )
                                await session.execute(stmt)
            await session.commit()

    async def manage_karma_rewards(self, guild_id, user_id):
        async with self.db.get_session() as session:
            rewards = await session.execute(select(RewardsTable).filter_by(guild_id=guild_id))
            rewards = rewards.scalars().all()
            user_karma = await session.execute(
                select(KarmaTable.karma).filter_by(user_id=user_id, guild_id=guild_id)
            )
            user_karma = user_karma.scalar_one_or_none()

            guild = self.bot.get_guild(guild_id)
            member = guild.get_member(user_id)
            if not member:
                return

            for reward in rewards:
                role = guild.get_role(reward.role_id)
                if not role:
                    continue
                if user_karma >= reward.karma_needed and role not in member.roles:
                    await member.add_roles(role)
                elif user_karma < reward.karma_needed and role in member.roles:
                    await member.remove_roles(role)

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        emoji_id = payload.emoji.id

        if message_author.bot:  # Ignore bots
            return

        upvote_emoji = 1199472652721586298
        downvote_emoji = 1199472654185418752
        if emoji_id not in {upvote_emoji, downvote_emoji}:
            print("Ignoring")
            return

        guild_id = payload.guild_id
        async with self.db.get_session() as session:
            user_karma = await session.scalar(
                select(KarmaTable).where(
                    KarmaTable.user_id == message_author.id,
                    KarmaTable.guild_id == guild_id,
                )
            )

            if emoji_id == upvote_emoji:
                if user_karma:
                    user_karma.karma += 1
                else:
                    session.add(
                        KarmaTable(
                            user_id=message_author.id,
                            guild_id=guild_id,
                            karma=1,
                        )
                    )
                print("Upvoted")
            elif emoji_id == downvote_emoji:
                if user_karma and user_karma.karma > 0:
                    user_karma.karma -= 1
                    print("Downvoted")
                else:
                    print("Downvoted but no karma to remove")

            await session.commit()

    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        emoji_id = payload.emoji.id

        if message_author.bot:
            return

        upvote_emoji = 1199472652721586298
        downvote_emoji = 1199472654185418752
        if emoji_id not in {upvote_emoji, downvote_emoji}:
            print("Ignoring")
            return

        guild_id = payload.guild_id
        async with self.db.get_session() as session:
            user_karma = await session.scalar(
                select(KarmaTable).where(
                    KarmaTable.user_id == message_author.id,
                    KarmaTable.guild_id == guild_id,
                )
            )

            if not user_karma:
                return

            if emoji_id == upvote_emoji:
                if user_karma.karma > 0:
                    user_karma.karma -= 1
                    print("Upvote removed")
                else:
                    print("Upvote removed but no karma to remove")
            elif emoji_id == downvote_emoji:  # Remove downvote logic
                user_karma.karma += 1
                print("Downvote removed")

            await session.commit()

    @commands.command(name="givekarma")
    @commands.has_permissions(administrator=True)
    async def give_karma(self, ctx, member: discord.Member, amount: int):
        """Gives karma to a specified user."""
        if member.bot:
            await ctx.send("Bots cannot receive karma!")
            return
        async with self.db.get_session() as session:
            stmt = (
                update(KarmaTable)
                .where(KarmaTable.user_id == member.id, KarmaTable.guild_id == ctx.guild.id)
                .values(karma=KarmaTable.karma + amount)
            )
            await session.execute(stmt)
            await session.commit()
        await ctx.send(f"Gave {amount} karma to {member.mention}!")

    @commands.command(name="removekarma")
    @commands.has_permissions(administrator=True)
    async def remove_karma(self, ctx, member: discord.Member, amount: int):
        """Removes karma from a specified user."""
        if member.bot:
            await ctx.send("Bots cannot lose karma!")
            return
        async with self.db.get_session() as session:
            stmt = (
                update(KarmaTable)
                .where(KarmaTable.user_id == member.id, KarmaTable.guild_id == ctx.guild.id)
                .values(karma=KarmaTable.karma - amount)
            )
            await session.execute(stmt)
            await session.commit()
        await ctx.send(f"Removed {amount} karma from {member.mention}!")

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Displays the leaderboard for the server."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(KarmaTable)
                .where(KarmaTable.guild_id == ctx.guild.id)
                .order_by(KarmaTable.karma.desc())
                .limit(10)
            )
            top_users = result.scalars().all()
        if not top_users:
            await ctx.send("No leaderboard data available.")
            return
        leaderboard = "\n".join(
            [f"{i + 1}. <@{user.user_id}> - {user.karma} karma" for i, user in enumerate(top_users)]
        )
        await ctx.send(f"**Leaderboard:**\n{leaderboard}")

    @commands.command(name="clearleaderboard")
    async def clear_leaderboard(self, ctx):
        """Clears the leaderboard for the server."""
        async with self.db.get_session() as session:
            stmt = delete(KarmaTable).where(KarmaTable.guild_id == ctx.guild.id)
            await session.execute(stmt)
            await session.commit()
        await ctx.send("Leaderboard has been cleared!")

    @commands.command(name="karma")
    async def check_karma(self, ctx, member: discord.Member = None):
        """Check karma for a user."""
        member = member or ctx.author
        async with self.db.get_session() as session:
            result = await session.execute(
                select(KarmaTable.karma).filter_by(user_id=member.id, guild_id=ctx.guild.id)
            )
            karma = result.scalar_one_or_none()
        await ctx.send(f"{member.display_name} has {karma or 0} karma.")

    @commands.command(name="add_reward")
    @commands.has_permissions(manage_roles=True)
    async def add_reward(self, ctx, role: discord.Role, karma_needed: int):
        """Add a reward role for karma."""
        async with self.db.get_session() as session:
            session.add(RewardsTable(role_id=role.id, guild_id=ctx.guild.id, karma_needed=karma_needed))
            await session.commit()
        await ctx.send(f"Added {role.name} as a reward for {karma_needed} karma.")

    @commands.command(name="remove_reward")
    @commands.has_permissions(manage_roles=True)
    async def remove_reward(self, ctx, role: discord.Role):
        """Remove a reward role for karma."""
        async with self.db.get_session() as session:
            await session.execute(
                delete(RewardsTable).where(RewardsTable.role_id == role.id, RewardsTable.guild_id == ctx.guild.id)
            )
            await session.commit()
        await ctx.send(f"Removed {role.name} from the reward roles.")

    @commands.command(name="rewards")
    async def list_rewards(self, ctx):
        """List all reward roles for karma."""
        async with self.db.get_session() as session:
            results = await session.execute(
                select(RewardsTable).filter_by(guild_id=ctx.guild.id)
            )
            rewards = results.scalars().all()
        if not rewards:
            await ctx.send("No rewards have been set.")
        else:
            rewards_list = "\n".join(
                [f"{ctx.guild.get_role(reward.role_id).name}: {reward.karma_needed} karma" for reward in rewards]
            )
            await ctx.send(f"Reward roles:\n{rewards_list}")


def setup(bot):
    bot.add_cog(Karma(bot))
