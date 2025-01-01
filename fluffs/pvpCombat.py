import discord
from discord.ext import commands
import os
from sqlalchemy import select, update, delete

from database.fluffs_db import Database, FluffUserTable, MasterFluffTable
import logging

class FluffPvPCombat(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot
    logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.db = Database()
        self.bot.loop.create_task(self.db.init_db())

    fluffCommandGroup = discord.SlashCommandGroup(name="fluff-combat", description="Fluff Commands") # create a group of slash commands
    @fluffCommandGroup.command(name="battle", description="Challenge another trainer to a Fluff battle")
    async def battle(self, ctx):
        await ctx.respond("Battle command")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(FluffPvPCombat(bot)) # add the cog to the bot