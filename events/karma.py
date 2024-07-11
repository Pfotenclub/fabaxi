import discord
from discord.ext import commands

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command(name="karma", description="Check your karma!")
    async def pull(self, ctx):
        await ctx.respond("You have 0 karma!")

def setup(bot):
    bot.add_cog(Karma(bot))