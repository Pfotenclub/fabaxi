import logging

import discord
from discord.ext import commands, tasks
from sqlalchemy import select

from db.tables import RewardsTable
from db.user_karma import UserKarma

class Karma(commands.Cog):
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler()])

    def __init__(self, bot):
        self.bot = bot
        self.give_voice_karma.start()

    def cog_unload(self):
        self.give_voice_karma.cancel()

    @discord.Cog.listener()
    async def on_guild_join(self, guild):
        for member in guild.members:
            if not member.bot:
                await UserKarma().create_user_record_in_karma(member.id, guild.id)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.bot or message.channel.id == 1229062537954332782 or  # commands channel
                message.channel.id == 1337733289695514725 or  # counting channel
                message.channel.id == 1339010562964586647 or  # cult leader channel
                message.channel.id == 1283842433284837396  # burgeramt channel
        ):
            return

        await UserKarma().handle_message_karma(user_id=message.author.id, guild_id=message.guild.id,
            timestamp=message.created_at.timestamp(), )

    @tasks.loop(minutes=1)
    async def give_voice_karma(self):
        try:
            for guild in self.bot.guilds:
                for channel in guild.voice_channels:
                    active_users = [member for member in channel.members if
                        not member.bot and not member.voice.self_mute and not member.voice.self_deaf]
                    if len(active_users) >= 2:
                        for user in active_users:
                            await UserKarma().adjust_karma_for_user(user.id, guild.id, amount=1)
        except Exception as e:
            logging.error(f"Error during voice karma loop: {e}")

    async def manage_karma_rewards(self, guild_id, user_id):
        try:
            rewards = await UserKarma().list_rewards(guild_id)
            user_karma = await UserKarma().get_user_karma(user_id, guild_id)

            if user_karma is None:
                logging.warning(f"No karma found for user_id={user_id} in guild_id={guild_id}")
                return

            guild = self.bot.get_guild(guild_id)
            member = guild.get_member(user_id)
            if not member:
                logging.warning(f"Member not found in guild_id={guild_id} for user_id={user_id}")
                return

            for reward in rewards:
                role = guild.get_role(reward.role_id)
                if not role:
                    logging.warning(f"Role ID {reward.role_id} not found in guild {guild_id}")
                    continue

                if user_karma >= reward.karma_needed and role not in member.roles:
                    await member.add_roles(role)
                    logging.info(f"Added role {role.name} to user {member.name}")
                elif user_karma < reward.karma_needed and role in member.roles:
                    await member.remove_roles(role)
                    logging.info(f"Removed role {role.name} from user {member.name}")
        except Exception as e:
            logging.error(f"Error managing karma rewards: {e}")

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.bot:
            return

        await UserKarma.handle_reaction_change(message_author=message.author, guild_id=payload.guild_id,
            emoji_id=payload.emoji.id, is_addition=True)
        print(f"Reaction added: {payload.emoji.id}")

    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.bot:
            return

        await UserKarma.handle_reaction_change(message_author=message.author, guild_id=payload.guild_id,
            emoji_id=payload.emoji.id, is_addition=False)

    @discord.slash_command(name="adjustkarma", contexts={discord.InteractionContextType.guild})
    @discord.ext.commands.has_guild_permissions(administrator=True)
    async def give_karma(self, ctx, member: discord.Member, amount: int):
        """Adjusts karma of a specified user by provided amount."""
        if member.id == ctx.author.id:
            return await ctx.respond("You cannot adjust your own karma!")
        if member.bot:
            return await ctx.respond("Bots cannot receive karma!")

        await UserKarma().adjust_karma_for_user(member.id, ctx.guild.id, amount)
        await ctx.respond(f"Gave {amount} karma to {member.mention}!")

    @discord.slash_command(name="leaderboard", contexts={discord.InteractionContextType.guild})
    async def leaderboard(self, ctx):
        """Displays the leaderboard for the server."""
        await ctx.defer()
        embed = discord.Embed(title="Karma Leaderboard", color=discord.Color.blurple())
        top_users = await UserKarma().get_karma_leaderboard(ctx.guild.id, 10)

        if not top_users:
            await ctx.respond("No leaderboard data available.")
            return

        for row in top_users:
            user = ctx.guild.get_member(row.user_id)
            embed.add_field(name=user, value=row.karma, inline=False)

        await ctx.respond(embed=embed)

    @discord.slash_command(name="clearleaderboard", contexts={discord.InteractionContextType.guild})
    @discord.ext.commands.has_guild_permissions(administrator=True)
    async def clear_leaderboard(self, ctx):
        """Clears the leaderboard for the server."""
        await UserKarma().clear_karma_leaderboard(ctx.guild.id)
        await ctx.respond("Leaderboard has been cleared!")

    @discord.slash_command(name="karma", contexts={discord.InteractionContextType.guild})
    async def check_karma(self, ctx, member: discord.Member = None):
        """Check karma for a user."""
        member = member or ctx.author
        karma = await UserKarma().get_user_karma(member.id, ctx.guild.id)
        await ctx.respond(f"{member.display_name} has {karma or 0} karma.")

    @discord.slash_command(name="add_reward", contexts={discord.InteractionContextType.guild})
    @discord.ext.commands.has_guild_permissions(manage_roles=True)
    async def add_reward(self, ctx, role: discord.Role, karma_needed: int):
        """Add a reward role for karma."""
        async with self.db.get_session() as session:
            session.add(RewardsTable(role_id=role.id, guild_id=ctx.guild.id, karma_needed=karma_needed))
            await session.commit()
        await ctx.respond(f"Added {role.name} as a reward for {karma_needed} karma.")

    @discord.slash_command(name="remove_reward", contexts={discord.InteractionContextType.guild})
    @discord.ext.commands.has_guild_permissions(manage_roles=True)
    async def remove_reward(self, ctx, role: discord.Role):
        """Remove a reward role for karma."""
        await UserKarma().remove_reward(role.id, ctx.guild.id)
        await ctx.respond(f"Removed {role.name} from the reward roles.")

    @discord.slash_command(name="rewards", contexts={discord.InteractionContextType.guild})
    async def list_rewards(self, ctx):
        """List all reward roles for karma."""
        async with self.db.get_session() as session:
            results = await session.execute(select(RewardsTable).filter_by(guild_id=ctx.guild.id))
            rewards = results.scalars().all()
        if not rewards:
            await ctx.respond("No rewards have been set.")
        else:
            rewards_list = "\n".join(
                [f"{ctx.guild.get_role(reward.role_id).name}: {reward.karma_needed} karma" for reward in rewards])
            await ctx.respond(f"Reward roles:\n{rewards_list}")

    @remove_reward.error
    @add_reward.error
    @clear_leaderboard.error
    @give_karma.error
    async def on_command_error(self, ctx, error):
        """Handles errors """
        embed = discord.Embed(title="Error", description="Something went wrong while executing the command.",
            color=discord.Color.red())

        if isinstance(error, commands.MissingPermissions):
            embed.add_field(name="Permission Denied", value="You lack the required permissions to run this command.",
                inline=False)
        elif isinstance(error, commands.MemberNotFound):
            embed.add_field(name="Member Not Found", value="The specified member could not be found.", inline=False)
        elif isinstance(error, commands.CommandInvokeError):
            embed.add_field(name="Command Error", value=str(error.original), inline=False)
        else:
            embed.add_field(name="Unknown Error", value="An unexpected error occurred. Please contact an admin.",
                inline=False)

        try:
            await ctx.respond(embed=embed, ephemeral=True)
        except discord.HTTPException:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Karma(bot))
