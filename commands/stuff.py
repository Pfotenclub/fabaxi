import discord
from discord.ext import commands
import os

class Stuff(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    @discord.slash_command(name="ping", description="Pong!")
    async def pull(self, ctx):
        await ctx.respond("Pong!")
    @discord.slash_command(name="stuff", description="Some stuff")
    async def stuff(self, ctx):
        if ctx.author.id != 327880195476422656: return await ctx.respond("You are not allowed to use this command")
        await ctx.defer()
        for member in ctx.guild.members:
            if member.bot:
                continue
            await member.add_roles(ctx.guild.get_role(1341774758076874832))
            print(f"Gave role to {member.name}")
        await ctx.send("Done")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Stuff(bot)) # add the cog to the bot