import discord
from discord.ext import commands
import os
import json
import random
import nltk
from asyncio import sleep
from nltk.corpus import words
nltk.download("words")

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
data_path = None

if environment == "DEV": data_path = os.path.dirname(os.path.abspath(__file__))
elif environment == "PROD": data_path = "/db"

class Minigames(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.command(name="guessthenumber")
    @commands.is_owner()
    async def guessTheNumber(self, ctx: commands.Context):
        gtnChannel = None
        if environment == "DEV": gtnChannel = 1462546129106501837
        elif environment == "PROD": gtnChannel = 1462546344064586031
        if ctx.channel.id != gtnChannel:
            await ctx.send("You can only start Guess The Number in the Guess The Number channel!")
            return

        guessJson = None
        with open(os.path.join(data_path, "guessthenumber.json"), "r") as file: guessJson = json.load(file)

        if guessJson["status"] == "stopped":
            guessJson["status"] = "running"
            guessJson["number"] = random.randint(1, 100)
            guessJson["guesses"] = {}
            with open(os.path.join(data_path, "guessthenumber.json"), "w") as file: json.dump(guessJson, file)
            await ctx.send("Guess The Number has started! Try to guess the number between 1 and 100!")
        elif guessJson["status"] == "running": await ctx.send("Guess The Number is already running! To stop it, please use the command `!stopguessthenumber`.")
    
    
    @commands.command(name="stopguessthenumber")
    @commands.is_owner()
    async def stopGuessTheNumber(self, ctx: commands.Context):
        gtnChannel = None
        if environment == "DEV": gtnChannel = 1462546129106501837
        elif environment == "PROD": gtnChannel = 1462546344064586031
        if ctx.channel.id != gtnChannel: return await ctx.send("You can only stop Guess The Number in the Guess The Number channel!")

        guessJson = None
        with open(os.path.join(data_path, "guessthenumber.json"), "r") as file: guessJson = json.load(file)

        if guessJson["status"] == "stopped":
            await ctx.send("Guess The Number is already stopped.")
        else:
            guessJson["status"] = "stopped"
            guessJson["number"] = 0
            guessJson["guesses"] = {}
            with open(os.path.join(data_path, "guessthenumber.json"), "w") as file: json.dump(guessJson, file)
            await ctx.send("Guess The Number has been stopped. To start it again, please use the command `!guessthenumber`.")
    
    async def guessTheNumberGame(self, message):
        if message.author.bot: return
        gtnChannel = None
        if environment == "DEV": gtnChannel = self.bot.get_channel(1462546129106501837)
        elif environment == "PROD": gtnChannel = self.bot.get_channel(1462546344064586031)
        if message.channel != gtnChannel: return

        guessJson = None
        with open(os.path.join(data_path, "guessthenumber.json"), "r") as file: guessJson = json.load(file)

        if guessJson["status"] == "stopped": return
        if message.content.startswith("?") or message.content == "!guessthenumber" or message.content == "!stopguessthenumber": return

        elif guessJson["status"] == "running":
            if "guesses" not in guessJson or not isinstance(guessJson["guesses"], dict):
                guessJson["guesses"] = {}
            user_id = str(message.author.id)
            if user_id not in guessJson["guesses"]:
                guessJson["guesses"][user_id] = 0
                with open(os.path.join(data_path, "guessthenumber.json"), "w") as file: json.dump(guessJson, file)

            if message.content.isnumeric() == False:
                await message.add_reaction("❌")
                guessJson["guesses"][user_id] = guessJson["guesses"].get(user_id, 0) + 1
                with open(os.path.join(data_path, "guessthenumber.json"), "w") as file: json.dump(guessJson, file)
                return await message.channel.send("That's not a number! Please guess a number between `1` and `100`.")
            
            guess = int(message.content)

            if guess < 1 or guess > 100:
                await message.add_reaction("❌")
                guessJson["guesses"][user_id] = guessJson["guesses"].get(user_id, 0) + 1
                await message.channel.send("Your guess is out of bounds! Please guess a number between `1` and `100`.")

            elif guess < guessJson["number"]:
                await message.add_reaction("❌")
                guessJson["guesses"][user_id] = guessJson["guesses"].get(user_id, 0) + 1
                await message.channel.send(f"{message.author.mention}, the searched number is higher!")

            elif guess > guessJson["number"]:
                await message.add_reaction("❌")
                guessJson["guesses"][user_id] = guessJson["guesses"].get(user_id, 0) + 1
                await message.channel.send(f"{message.author.mention}, the searched number is lower!")
            else:
                await message.add_reaction("✅")
                if user_id in guessJson["guesses"]:
                    if guessJson["guesses"][user_id] + 1 == 1:
                        await message.channel.send("Damn")
                        await sleep(1)
                        await message.channel.send("You... guessed in 1 try?")
                        await sleep(1)
                        await message.channel.send("Impressive!")
                        await sleep(1)
                        await message.channel.send("Now go buy a lottery ticket or something.")
                await message.channel.send(f"Congratulations {message.author.mention}! You guessed the correct number in {guessJson['guesses'][user_id] + 1} tries!")
                guessJson["status"] = "running"
                guessJson["number"] = random.randint(1, 100)
                guessJson["guesses"] = {}
                await message.channel.send("A new round has started! Try to guess the new number between `1` and `100`!")
            with open(os.path.join(data_path, "guessthenumber.json"), "w") as file: json.dump(guessJson, file)
##########################################################################
    # Command to Control the Counting Minigame
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
            await ctx.send("Counting will start soon... Please type `1` to start counting!")
        elif countJson["status"] == "running": await ctx.send(f"The current count is {countJson['count']}. To stop counting, please use the command `!stopcounting`.")
        elif countJson["status"] == "starting": await ctx.send("Counting is about to start! Please type `1` to start counting!")
    
    @commands.command(name="stopcounting")
    @commands.is_owner()
    async def stopCounting(self, ctx: commands.Context):
        countChannel = None
        if environment == "DEV": countChannel = 1335743804346470411
        elif environment == "PROD": countChannel = 133773328969551472
        if ctx.channel.id != countChannel: return await ctx.send("You can only stop counting in the counting channel!")
        
        countJson = None
        with open(os.path.join(data_path, "count.json"), "r") as file: countJson = json.load(file)

        if countJson["status"] == "stopped":
            await ctx.send("Counting is already stopped.")
        else:
            countJson["status"] = "stopped"
            countJson["count"] = 0
            countJson["lastAuthor"] = None
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
            await ctx.send("Counting has been stopped. To start counting again, please use the command `!counting`.")
    
    async def countingGame(self, message):
        if message.author.bot: return
        countChannel = None
        if environment == "DEV": countChannel = self.bot.get_channel(1335743804346470411)
        elif environment == "PROD": countChannel = self.bot.get_channel(1337733289695514725)
        if message.channel != countChannel: return

        countJson = None
        with open(os.path.join(data_path, "count.json"), "r") as file: countJson = json.load(file)
        
        if countJson["status"] == "stopped": return
        if message.content.startswith("?") or message.content == "!counting" or message.content == "!stopcounting": return
        elif countJson["status"] == "starting":
            if message.content != "1":
                await message.add_reaction("❌")
                return await message.channel.send("Dang! You didn't start at 1. Type `1` to start counting.")
            countJson["status"] = "running"
            countJson["count"] = 1
            countJson["lastAuthor"] = message.author.id
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
            await message.add_reaction("✅")
        elif countJson["status"] == "running":
            if message.content.isnumeric() == False: 
                await message.add_reaction("❌")
                await message.channel.send("Hmpf, That's not a number! You can only count with numbers!\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)

            elif message.author.id == countJson["lastAuthor"]:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention}, you can't count twice in a row!\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
                
            elif int(message.content) != countJson["count"] + 1:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention}, you typed the wrong number! Your count should be {countJson['count'] + 1}.\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)

            else:
                await message.add_reaction("✅")
                countJson["count"] += 1
                countJson["lastAuthor"] = message.author.id
                with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
##########################################################################
    @discord.Cog.listener("on_message")
    async def on_message(self, message):
        await self.countingGame(message)
        await self.guessTheNumberGame(message)


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Minigames(bot)) # add the cog to the bot
