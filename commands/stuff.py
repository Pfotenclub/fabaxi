import discord
from discord.ext import commands
import os
import git

class Stuff(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    @discord.slash_command(name="pull", description="This is a test command", guild_ids=[1001916230069911703])
    async def pull(self, ctx):
        # Pull code from GitHub repo

        repo_url = "https://github.com/your_username/your_repo.git"
        repo_dir = "/path/to/your/repo"

        if not os.path.exists(repo_dir):
            git.Repo.clone_from(repo_url, repo_dir)
        else:
            repo = git.Repo(repo_dir)
            repo.remotes.origin.pull()
        await ctx.send("This is a test command")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Stuff(bot)) # add the cog to the bot