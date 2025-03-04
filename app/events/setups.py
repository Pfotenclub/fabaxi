import time
import discord
from discord.ext import commands
import random
import threading
from dotenv import load_dotenv
import os
load_dotenv()

class Setups(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    def cog_unload(self):
        self.change_status.cancel()

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_member_join(self, member): # this is called when a member joins the server
        role_ids = [1230984456186237008, 1229073628658794688, 1341774758076874832]  
        for role_id in role_ids:
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)


    @commands.Cog.listener("on_ready")
    async def printOnline(self):
        print(f"Bot is online as {self.bot.user}")

        
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Setups(bot)) # add the cog to the bot