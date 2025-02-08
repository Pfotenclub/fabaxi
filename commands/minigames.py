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
        
        
    
    minigamesCommandGroup = discord.SlashCommandGroup(name="minigames", description="A selection of minigames to play with your friends.")
    @minigamesCommandGroup.command(name="wordmorphing", description="Morph your Words.")
    async def wordmorphing(self, ctx):
        
        morphingChannel = None
        if environment == "DEV": morphingChannel = 1337753714294784113
        elif environment == "PROD": morphingChannel = 1337751857518477363
        if ctx.channel_id != morphingChannel: return await ctx.respond("You can only start word morphing in the word morphing channel!", ephemeral=True)

        morphingJson = None
        with open(os.path.join(data_path, "morphing.json"), "r") as file: morphingJson = json.load(file)

        if morphingJson["status"] == "stopped":
            morphingJson["status"] = "starting"
            morphingJson["word"] = []
            with open(os.path.join(data_path, "morphing.json"), "w") as file: json.dump(morphingJson, file)
            await ctx.respond("Word Morphing is starting soon. Please wait.")
        elif morphingJson["status"] == "running": await ctx.respond(f"With this command you can restart the game. Not implemented yet :)")
        elif morphingJson["status"] == "starting": await ctx.respond("Word Morphing is starting soon. Please wait.")

    @discord.Cog.listener("on_message")
    async def morphingGame(self, message):
        if message.author.bot: return
        morphingChannel = None
        if environment == "DEV": morphingChannel = self.bot.get_channel(1337753714294784113)
        elif environment == "PROD": morphingChannel = self.bot.get_channel(1337751857518477363)
        if message.channel != morphingChannel: return

        morphingJson = None
        with open(os.path.join(data_path, "morphing.json"), "r") as file: morphingJson = json.load(file)
        word_list = words.words()

        if morphingJson["status"] == "stopped": return
        if message.content.startswith("!"): return

        if morphingJson["status"] == "starting":
            if message.content.lower() not in word_list:
                await message.channel.send("That's not a word! Please type a valid word to start the game.")
                return
            morphingJson["status"] = "running"
            morphingJson["usedWords"].append(message.content)
            morphingJson["lastAuthor"] = message.author.id
            await message.add_reaction("✅")
            with open(os.path.join(data_path, "morphing.json"), "w") as file: json.dump(morphingJson, file)
        elif morphingJson["status"] == "running":
            if message.author.id == morphingJson["lastAuthor"]: 
                return await message.channel.send(f"{message.author.mention}, you can't type two words in a row!")
            if message.content.lower() not in word_list:
                await message.channel.send("That's not a word! Please type a valid word.")
                return
            for word in morphingJson["usedWords"]:
                if message.content.lower() == word.lower():
                    await message.channel.send(f"{message.author.mention}, this word has already been used!")
                    morphingJson["lastAuthor"] = message.author.id
                    with open(os.path.join(data_path, "morphing.json"), "w") as file: json.dump(morphingJson, file)
                    return
        
            if isOneCharacterDifferent(morphingJson["usedWords"][-1].lower(), message.content.lower()) == False: return await message.channel.send(f"{message.author.mention}, your word must be one character different from the last word!")

            morphingJson["usedWords"].append(message.content)
            morphingJson["lastAuthor"] = message.author.id
            with open(os.path.join(data_path, "morphing.json"), "w") as file: json.dump(morphingJson, file)
            await message.add_reaction("✅")

            
            
    
    @minigamesCommandGroup.command(name="counting", description="Count up!")
    async def counting(self, ctx):
        countChannel = None
        if environment == "DEV": countChannel = 1335743804346470411
        elif environment == "PROD": countChannel = 1337733289695514725
        if ctx.channel_id != countChannel: return await ctx.respond("You can only start counting in the counting channel!", ephemeral=True)

        countJson = None
        with open(os.path.join(data_path, "count.json"), "r") as file: countJson = json.load(file)
        
        if countJson["status"] == "stopped":
            countJson["status"] = "starting"
            countJson["count"] = 0
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
            await ctx.respond("Counting is starting soon. Please wait.")
        elif countJson["status"] == "running": await ctx.respond(f"The current count is {countJson['count']}.")
        elif countJson["status"] == "starting": await ctx.respond("Counting is starting soon. Please wait.")

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
        if message.content.startswith("!"): return
        elif countJson["status"] == "starting":
            if message.content != "1": 
                await message.channel.send("Dang! You didn't start at 1. Type 1 to start counting.")
                return message.add_reaction("❌")
            countJson["status"] = "running"
            countJson["count"] = 1
            countJson["lastAuthor"] = message.author.id
            await message.add_reaction("✅")
            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)
        elif countJson["status"] == "running":
            if message.content.isnumeric() == False: 
                await message.channel.send("Hmpf, That's not a number! You can only count with numbers!\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                await message.add_reaction("❌")

            elif message.author.id == countJson["lastAuthor"]:
                await message.channel.send(f"{message.author.mention}, you can't count twice in a row!\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                await message.add_reaction("❌")
                
            elif int(message.content) != countJson["count"] + 1:
                await message.channel.send(f"{message.author.mention}, you typed the wrong number! Your count should be {countJson['count'] + 1}.\nWe will start over at 1.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                await message.add_reaction("❌")

            else:
                countJson["count"] += 1
                countJson["lastAuthor"] = message.author.id
                await message.add_reaction("✅")

            with open(os.path.join(data_path, "count.json"), "w") as file: json.dump(countJson, file)


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Minigames(bot)) # add the cog to the bot

def isOneCharacterDifferent(word1, word2):
    # One character difference
    if len(word1) == len(word2):
        differences = sum(1 for a,b in zip(word1, word2) if a != b)
        return differences == 1
    # One character added
    elif len(word1) + 1 == len(word2):
        for i in range(len(word2)):
            if word1 == word2[:i] + word2[i+1:]:
                return True
    # One character removed
    elif len(word1) == len(word2) + 1:
        for i in range(len(word1)):
            if word2 == word1[:i] + word1[i+1:]:
                return True
    return False