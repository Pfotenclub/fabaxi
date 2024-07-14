import discord
from discord.ext import commands
import aiosqlite

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./../data/karma.db"

    @discord.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM karma WHERE user_id = ?", (message.author.id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await db.execute("INSERT INTO karma (user_id, karma, timestamplastmessage) VALUES (?, 1, ?)", (message.author.id, message.created_at.timestamp()))
                    await db.commit()
                elif row[2] < message.created_at.timestamp() - 60:
                    await db.execute("UPDATE karma SET karma = karma + 1, timestamplastmessage = ? WHERE user_id = ?", (message.created_at.timestamp(), message.author.id))
                    await db.commit()
            async with db.execute("SELECT * FROM karma") as cursor:
                async for row in cursor:
                    print(row)
                
    @discord.Cog.listener()
    async def on_ready(self):
        await setup_db(self.db_path)
        

    @discord.slash_command(name="karma", description="Check your karma!")
    async def pull(self, ctx):
        await ctx.defer()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT karma FROM karma WHERE user_id = ?", (ctx.author.id,)) as cursor:
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
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM karma ORDER BY karma DESC LIMIT 10") as cursor:
                rows = await cursor.fetchall()
                leaderboard = "\n".join([f"{ctx.guild.get_member(row[0]).display_name}: {row[1]}" for row in rows])
            await db.commit()
        await ctx.respond(f"Karma leaderboard:\n{leaderboard}")

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
        await ctx.defer()
        if user == ctx.author:
            await ctx.respond("You can't give karma to yourself!")
            return
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM karma WHERE user_id = ?", (user.id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await db.execute("INSERT INTO karma (user_id, karma, timestamplastmessage) VALUES (?, ?, ?)", (user.id, amount, discord.utils.utcnow().timestamp()))
                    await db.commit()
                else:
                    await db.execute("UPDATE karma SET karma = karma + {amount}, timestamplastmessage = ? WHERE user_id = ?", (discord.utils.utcnow().timestamp/(), user.id))
                    await db.commit()
        await ctx.respond(f"Gave {amount} karma to {user.display_name}!")
async def setup_db(db_path):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS karma (user_id INTEGER PRIMARY KEY, karma INTEGER DEFAULT 0, timestamplastmessage INTEGER)")
        await db.commit()

def setup(bot):
    bot.add_cog(Karma(bot))