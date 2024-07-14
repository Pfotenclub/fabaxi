import discord
from discord.ext import commands, tasks
import aiosqlite

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./../data/karma.db"
        self.rewards_db_path = "./../data/rewards.db"
        self.give_voice_karma.start()
    
    def cog_unload(self):
        self.give_voice_karma.cancel()
    
    @discord.Cog.listener()
    async def on_guild_join(self, guild):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS guild_{0} (user_id INTEGER PRIMARY KEY, karma INTEGER DEFAULT 0, timestamplastmessage INTEGER)".format(guild.id))
            await db.commit()

    @discord.Cog.listener()
    async def on_message(self, message):
        print(message.content)
        if message.author.bot: # Ignore bots
            return
        guild_id = message.guild.id
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild_id), (message.author.id,)) as cursor: # Get User's Entry
                row = await cursor.fetchone()
                if row is None: # If user doesn't have an entry, create one
                    await db.execute("INSERT INTO guild_{0} (user_id, karma, timestamplastmessage) VALUES (?, 1, ?)".format(guild_id), (message.author.id, message.created_at.timestamp()))
                    await db.commit()
                elif row[2] < message.created_at.timestamp() - 60: # If user has an entry, but hasn't sent a message in the last minute, give them karma
                    await db.execute("UPDATE guild_{0} SET karma = karma + 1, timestamplastmessage = ? WHERE user_id = ?".format(guild_id), (message.created_at.timestamp(), message.author.id))
                    await db.commit()
                    give_rewards(self, guild_id, message.author.id)
            async with db.execute("SELECT * FROM guild_{0}".format(guild_id)) as cursor: # Print all entries
                async for row in cursor:
                    print(row)
                
    @discord.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        #user = await self.bot.fetch_user(payload.member.id)
        print("Recieved from {0}".format(message_author))
        emoji_id = payload.emoji.id
        if message_author.bot: # Ignore bots
            return
        if emoji_id != 1199472652721586298 and emoji_id != 1199472654185418752: # Ignore reactions that aren't the ones we're looking for
            print("Ignoring")
            return
        guild_id = payload.guild_id
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild_id), (message_author.id,)) as cursor:
                row = await cursor.fetchone()
                if emoji_id == 1199472652721586298: # When the user reacts with the upvote emoji
                    await db.execute("UPDATE guild_{0} SET karma = karma + 10 WHERE user_id = ?".format(guild_id), (message_author.id,))
                    await db.commit()
                    give_rewards(self, guild_id, message_author.id)
                elif emoji_id == 1199472654185418752: # When the user reacts with the downvote emoji
                    if row[1] == 0:
                        return print("Downvoted but no karma to remove")
                    await db.execute("UPDATE guild_{0} SET karma = karma - 10 WHERE user_id = ?".format(guild_id), (message_author.id,))
                    await db.commit()
                    print("Downvoted")

    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        print("Recieved from {0}".format(message_author))
        emoji_id = payload.emoji.id
        if message_author.bot: # Ignore bots
            return
        if emoji_id != 1199472652721586298 and emoji_id != 1199472654185418752: # Ignore reactions that aren't the ones we're looking for
            print("Ignoring")
            return
        guild_id = payload.guild_id
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild_id), (message_author.id,)) as cursor:
                row = await cursor.fetchone()
                if emoji_id == 1199472652721586298: # When the user removes the upvote emoji
                    if row[1] == 0:
                        return print("Upvote removed but no karma to remove")
                    await db.execute("UPDATE guild_{0} SET karma = karma - 10 WHERE user_id = ?".format(guild_id), (message_author.id,))
                    await db.commit()
                    print("Upvote removed")
                elif emoji_id == 1199472654185418752: # When the user removes the downvote emoji
                    await db.execute("UPDATE guild_{0} SET karma = karma + 10 WHERE user_id = ?".format(guild_id), (message_author.id,))
                    await db.commit()
                    print("Downvote removed")
    
    @tasks.loop(minutes=1)
    async def give_voice_karma(self):
        print("Looping")
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                real_users = [member for member in channel.members if not member.bot]
                if len(real_users) >= 2:
                    active_users = [member for member in real_users if member.voice.self_mute == False and member.voice.self_deaf == False]
                    if len(active_users) >= 2:
                        for user in active_users:
                            print("User: {0}".format(user))
                            async with aiosqlite.connect(self.db_path) as db:
                                async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild.id), (user.id,)) as cursor:
                                    row = await cursor.fetchone()
                                    if row is None:
                                        await db.execute("INSERT INTO guild_{0} (user_id, karma, timestamplastmessage) VALUES (?, 1, ?)".format(guild.id), (user.id, discord.utils.utcnow().timestamp()))
                                        await db.commit()
                                    elif row[2] < discord.utils.utcnow().timestamp() - 60:
                                        await db.execute("UPDATE guild_{0} SET karma = karma + 1, timestamplastmessage = ? WHERE user_id = ?".format(guild.id), (discord.utils.utcnow().timestamp(), user.id))
                                        await db.commit()

    @discord.Cog.listener()
    async def on_ready(self):
        await setup_db(self, self.db_path, self.rewards_db_path) # Setup the database

    @discord.slash_command(name="karma", description="Check your karma!")
    async def getkarma(
        self,
        ctx,
        user: discord.Option(discord.Member, description="The user to check the karma of!", required=False) # type: ignore
    ):
        await ctx.defer()
        guild_id = ctx.guild.id
        async with aiosqlite.connect(self.db_path) as db:
            if user:
                async with db.execute("SELECT karma FROM guild_{0} WHERE user_id = ?".format(guild_id), (user.id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        karma = 0
                    else:
                        karma = row[0]
                await db.commit()
                await ctx.respond(f"{user.display_name}'s karma is {karma}!")
            else:
                async with db.execute("SELECT karma FROM guild_{0} WHERE user_id = ?".format(guild_id), (ctx.author.id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        karma = 0
                    else:
                        karma = row[0]
                await db.commit()
                await ctx.respond(f"Your karma is {karma}!")

    @discord.slash_command(name="leaderboard", description="Check the karma leaderboard!")
    async def leaderboard(self, ctx):
        await ctx.defer()
        guild_id = ctx.guild.id
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM guild_{0} ORDER BY karma DESC LIMIT 10".format(guild_id),) as cursor:
                    rows = await cursor.fetchall()
                    leaderboard = "\n".join([f"{ctx.guild.get_member(row[0])}: {row[1]}" for row in rows])
                await db.commit()
            await ctx.respond(f"Karma leaderboard:\n{leaderboard}")
        except Exception as e:
            ctx.respond(f"An error occurred: {e}")

    @discord.slash_command(name="givekarma", description="Give karma to a user!")
    async def givekarma(
        self, 
        ctx, 
        user: discord.Option(discord.Member, description="The user to give karma to!", required=True), # type: ignore
        amount: int = 1
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You must be an administrator to give karma!", ephemeral=True)
            return
        if user.bot:
            await ctx.respond("You can't give karma to bots!", ephemeral=True)
            return
        await ctx.defer()
        guild_id = ctx.guild.id
        if user == ctx.author:
            await ctx.respond("You can't give karma to yourself!")
            return
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild_id), (user.id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await db.execute("INSERT INTO guild_{0} (user_id, karma, timestamplastmessage) VALUES (?, ?, ?)".format(guild_id), (user.id, amount, discord.utils.utcnow().timestamp()))
                    await db.commit()
                else:
                    await db.execute("UPDATE guild_{0} SET karma = karma + ?, timestamplastmessage = ? WHERE user_id = ?".format(guild_id), (amount, discord.utils.utcnow().timestamp(), user.id))
                    await db.commit()
        await ctx.respond(f"Gave {amount} karma to {user.display_name}!")

    @discord.slash_command(name="removekarma", description="Remove karma from a user!")
    async def removekarma(
        self, 
        ctx, 
        user: discord.Option(discord.Member, description="The user to remove karma from!", required=True), # type: ignore
        amount: int = 1
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You must be an administrator to remove karma!", ephemeral=True)
            return
        if user.bot:
            await ctx.respond("You can't remove karma from bots!", ephemeral=True)
            return
        await ctx.defer()
        guild_id = ctx.guild.id
        if user == ctx.author:
            await ctx.respond("You can't remove karma from yourself!")
            return
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild_id), (user.id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await db.execute("INSERT INTO guild_{0} (user_id, karma, timestamplastmessage) VALUES (?, 0, ?)".format(guild_id), (user.id, discord.utils.utcnow().timestamp()))
                    await db.commit()
                    await ctx.respond(f"{user.display_name} has no karma to remove!")
                elif row[1] - amount < 0:
                    await db.execute("UPDATE guild_{0} SET karma = 0, timestamplastmessage = ? WHERE user_id = ?".format(guild_id), (discord.utils.utcnow().timestamp(), user.id))
                    await db.commit()
                    await ctx.respond(f"Removed {row[1]} karma from {user.display_name}!")
                else:
                    await db.execute("UPDATE guild_{0} SET karma = karma - ?, timestamplastmessage = ? WHERE user_id = ?".format(guild_id), (amount, discord.utils.utcnow().timestamp(), user.id))
                    await db.commit()
                    await ctx.respond(f"Removed {amount} karma from {user.display_name}!")

    @discord.slash_command(name="addreward", description="Add a role reward!")
    async def addreward(
        self,
        ctx,
        role: discord.Option(discord.Role, description="The role to add as a reward", required=True), # type: ignore
        karma_needed: discord.Option(int, description="The amount of karma needed to get the role", required=True) # type: ignore
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You must be an administrator to add rewards!", ephemeral=True)
            return
        await ctx.defer()
        guild_id = ctx.guild.id
        async with aiosqlite.connect(self.rewards_db_path) as db:
            async with db.execute("SELECT * FROM guild_{0} WHERE role_id = ?".format(guild_id), (role.id,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    await ctx.respond("This role is already added as a reward!")
                    return
                await db.execute("INSERT INTO guild_{0} (role_id, karma_needed) VALUES (?, ?)".format(guild_id), (role.id, karma_needed))
                await db.commit()
        await ctx.respond(f"Added {role.name} as a reward for {karma_needed}!")
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id FROM guild_{0} WHERE karma >= ?".format(guild_id), (karma_needed,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    user_id = row[0]
                    member = ctx.guild.get_member(user_id)
                    if member:
                        await member.add_roles(role)

async def setup_db(self, db_path, rewards_db_path):
    async with aiosqlite.connect(db_path) as db:
        for guild in self.bot.guilds:
            await db.execute("CREATE TABLE IF NOT EXISTS guild_{0} (user_id INTEGER PRIMARY KEY, karma INTEGER DEFAULT 0, timestamplastmessage INTEGER)".format(guild.id))
            for member in guild.members:
                if not member.bot:
                    async with db.execute("SELECT * FROM guild_{0} WHERE user_id = ?".format(guild.id), (member.id,)) as cursor:
                        row = await cursor.fetchone()
                        if row is None:
                            await db.execute("INSERT INTO guild_{0} (user_id, karma, timestamplastmessage) VALUES (?, 0, 0)".format(guild.id), (member.id,))
            await db.commit()
    async with aiosqlite.connect(rewards_db_path) as db:
        for guild in self.bot.guilds:
            await db.execute("CREATE TABLE IF NOT EXISTS guild_{0} (role_id INTEGER PRIMARY KEY, karma_needed INTEGER)".format(guild.id))

def give_rewards(self, guild_id, user_id):
    print("No rewards to give")

def remove_rewards(self, guild_id, user_id):
    print("No rewards to remove")

def setup(bot):
    bot.add_cog(Karma(bot))