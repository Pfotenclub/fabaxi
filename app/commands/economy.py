import discord
from discord.ext import commands
import os

from db.economy import EconomyBackend

class Economy(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    
    coins = discord.SlashCommandGroup(name="coins", description="Commands related to Pfotenclub Economy") # create a slash command group

    @coins.command(name="balance", description="Check your coin balance") # create a slash command in the coins group
    async def balance(self, ctx: discord.ApplicationContext): # this is the method that will be called when the command is used
        await ctx.respond(f"Your current balance is: {await EconomyBackend().get_balance(user_id=ctx.author.id, guild_id=ctx.guild.id)} coins.") # respond with the user's balance
    
    
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Economy(bot)) # add the cog to the bot