import discord
from discord.ext import commands
import aiosqlite

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/karma.db"

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS karma (user_id INTEGER PRIMARY KEY, karma INTEGER DEFAULT 0)")
            await db.commit()
        
    @discord.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        

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
        await ctx.send(f"Your karma is {karma}!")

def setup(bot):
    bot.add_cog(Karma(bot))