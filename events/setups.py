import discord
from discord.ext import commands

class Setups(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_member_join(self, member): # this is called when a member joins the server
        role_ids = [1234567890, 2345678901, 3456789012]  # Ersetzen Sie dies durch Ihre Rollen-IDs
        for role_id in role_ids:
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Setups(bot)) # add the cog to the bot