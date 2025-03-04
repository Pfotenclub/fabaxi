import discord
from discord.ext import commands
import os
import json
import nltk
from nltk.corpus import words
nltk.download("words")

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
data_path = None

if environment == "DEV": data_path = "./../data"
elif environment == "PROD": data_path = "/db"

class Minigames(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        
    @commands.command(name="counting")
    @commands.is_owner()
    async def startCounting(self, ctx: commands.Context):
        countChannel = None
        if environment == "DEV": countChannel = 1335743804346470411
        elif environment == "PROD": countChannel = 1337733289695514725
        if ctx.channel.id != countChannel: return await ctx.send("You can only start counting in the counting channel!")

        countJson = None
        with open(os.path.join(data_path, "count.json"), "r") as file: countJson = json.load(file)
        
        if countJson["status"] == "stopped":
            countJson["status"] = "starting"
            countJson["count"] = 0
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
            await ctx.respond("Counting is starting soon. Please wait.")
        elif countJson["status"] == "running": await ctx.send(f"The current count is {countJson['count']}.")
        elif countJson["status"] == "starting": await ctx.send("Counting is starting soon. Please wait.")

    @discord.Cog.listener("on_message")
    async def countingGame(self, message):
        if message.author.bot: return
        countChannel = None
        if environment == "DEV": countChannel = self.bot.get_channel(1335743804346470411)
        elif environment == "PROD": countChannel = self.bot.get_channel(1337733289695514725)
        if message.channel != countChannel: return

        countJson = None
        with open(os.path.join(data_path, "count.json"), "r") as file: countJson = json.load(file)
        
        if countJson["status"] == "stopped": return
        if message.content.startswith("?"): return
        elif countJson["status"] == "starting":
            if message.content != "1": 
                await message.channel.send("Dang! You didn't start at 1. Type 1 to start counting.")
                return message.add_reaction("❌")
            countJson["status"] = "running"
            countJson["count"] = 1
            countJson["lastAuthor"] = message.author.id
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
            await message.add_reaction("✅")
        elif countJson["status"] == "running":
            if message.content.isnumeric() == False: 
                await message.channel.send("Hmpf, That's not a number! You can only count with numbers!\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
                await message.add_reaction("❌")

            elif message.author.id == countJson["lastAuthor"]:
                await message.channel.send(f"{message.author.mention}, you can't count twice in a row!\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
                await message.add_reaction("❌")
                
            elif int(message.content) != countJson["count"] + 1:
                await message.channel.send(f"{message.author.mention}, you typed the wrong number! Your count should be {countJson['count'] + 1}.\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
                await message.add_reaction("❌")

            else:
                countJson["count"] += 1
                countJson["lastAuthor"] = message.author.id
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
                await message.add_reaction("✅")


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Minigames(bot)) # add the cog to the bot
