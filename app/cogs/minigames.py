import discord
from discord.ext import commands
import os
import json
import random
from asyncio import sleep

from app.core.config import COUNTING_CHANNEL_ID, DATA_DIR, GTN_CHANNEL_ID


def _load_gtn_state():
    path = os.path.join(DATA_DIR, "guessthenumber.json")
    if not os.path.exists(path):
        os.makedirs(DATA_DIR, exist_ok=True)
        default_state = {"status": "stopped", "number": 0, "guesses": {}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_state, f)
        return default_state
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_gtn_state(data):
    path = os.path.join(DATA_DIR, "guessthenumber.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _load_count_state():
    path = os.path.join(DATA_DIR, "count.json")
    if not os.path.exists(path):
        os.makedirs(DATA_DIR, exist_ok=True)
        default_state = {"status": "stopped", "count": 0, "lastAuthor": None}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_state, f)
        return default_state
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_count_state(data):
    path = os.path.join(DATA_DIR, "count.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


class Minigames(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
##########################################################################
# Commands to Control the Guess The Number Minigame
    @commands.command(name="guessthenumber")
    @commands.is_owner()
    async def guessTheNumber(self, ctx: commands.Context):
        if ctx.channel.id != GTN_CHANNEL_ID:
            await ctx.send("You can only start Guess The Number in the Guess The Number channel!")
            return

        guessJson = _load_gtn_state()

        if guessJson["status"] == "stopped":
            guessJson["status"] = "running"
            guessJson["number"] = random.randint(1, 100)
            guessJson["guesses"] = {}
            _save_gtn_state(guessJson)
            await ctx.send("Guess The Number has started! Try to guess the number between 1 and 100!")
            await ctx.message.delete()
        elif guessJson["status"] == "running":
            await ctx.send("Guess The Number is already running! To stop it, please use the command `!stopguessthenumber`.")
            await ctx.message.delete()

    @commands.command(name="stopguessthenumber")
    @commands.is_owner()
    async def stopGuessTheNumber(self, ctx: commands.Context):
        if ctx.channel.id != GTN_CHANNEL_ID:
            return await ctx.send("You can only stop Guess The Number in the Guess The Number channel!")

        guessJson = _load_gtn_state()

        if guessJson["status"] == "stopped":
            await ctx.send("Guess The Number is already stopped.")
        else:
            guessJson["status"] = "stopped"
            guessJson["number"] = 0
            guessJson["guesses"] = {}
            _save_gtn_state(guessJson)
            await ctx.send("Guess The Number has been stopped. To start it again, please use the command `!guessthenumber`.")
            await ctx.message.delete()

    async def guessTheNumberGame(self, message):
        if message.author.bot:
            return
        if message.channel.id != GTN_CHANNEL_ID:
            return

        guessJson = _load_gtn_state()

        if guessJson["status"] == "stopped": return
        if message.content == "!guessthenumber" or message.content == "!stopguessthenumber": return

        if message.content.startswith("?"):
            if random.randint(1, 1000) == 1:
                if random.randint(1, 100) <= 50: await message.channel.send("Psst... Want a hint? The number is between `1` and `100`!")
                else: await message.channel.send("Psst... You know, I can still read your messages, right?")


        elif guessJson["status"] == "running":
            if "guesses" not in guessJson or not isinstance(guessJson["guesses"], dict):
                guessJson["guesses"] = {}
            user_id = str(message.author.id)
            if user_id not in guessJson["guesses"]:
                guessJson["guesses"][user_id] = 0
                _save_gtn_state(guessJson)

            if message.content.isnumeric() == False:
                await message.add_reaction("❌")
                guessJson["guesses"][user_id] = guessJson["guesses"].get(user_id, 0) + 1
                _save_gtn_state(guessJson)
                return await message.channel.send("That's not a number! Please guess a number between `1` and `100`.")
            
            guess = int(message.content)

            if guess == 69: await message.channel.send("🤨")
            elif guess == 621:
                furrynumber = random.randint(1, 100)
                if furrynumber < 10: await message.channel.send("When you already give us that number, you are now obliged to tell us your favorite e621 tags :) Come on! Don't be shy!")
                elif furrynumber < 30: await message.channel.send("...Why?")
                elif furrynumber < 40: await message.channel.send("I hate my life... And I don't even have one")
                elif furrynumber < 50: await message.channel.send("Furries are people too... I guess")
                elif furrynumber < 60: await message.channel.send("Ew, gross")
                elif furrynumber < 70: await message.channel.send("I hate furries")
                elif furrynumber < 80: await message.channel.send("Why couldn't I just become an accountant instead...")
                elif furrynumber < 90: await message.channel.send("Just no.")
                else: await message.channel.send("Furry!")
            elif guess == 101: await message.channel.send("Quite the overachiever, aren't we?")
            elif guess == 0: await message.channel.send("Going for the underdog strategy, I see.")
            elif guess == 99: await message.channel.send("Quite an edger, aren't we?")
            elif guess == 1: await message.channel.send("Starting at the very beginning, I see. Just like in life :)")
            elif guess == 42: await message.channel.send("The ultimate answer to everything :3")
            elif guess == 73: await message.channel.send("Ah, a fellow Big Bang Theory fan!")

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
            _save_gtn_state(guessJson)
##########################################################################
# Commands to Control the Counting Minigame
    @commands.command(name="counting")
    @commands.is_owner()
    async def startCounting(self, ctx: commands.Context):
        if ctx.channel.id != COUNTING_CHANNEL_ID:
            return await ctx.send("You can only start counting in the counting channel!")

        countJson = _load_count_state()
        
        if countJson["status"] == "stopped":
            countJson["status"] = "starting"
            countJson["count"] = 0
            _save_count_state(countJson)
            await ctx.send("Counting will start soon... Please type `1` to start counting!")
            await ctx.message.delete()
        elif countJson["status"] == "running":
            await ctx.send(f"The current count is {countJson['count']}. To stop counting, please use the command `!stopcounting`.")
            await ctx.message.delete()
        elif countJson["status"] == "starting":
            await ctx.send("Counting is about to start! Please type `1` to start counting!")
            await ctx.message.delete()
    
    @commands.command(name="stopcounting")
    @commands.is_owner()
    async def stopCounting(self, ctx: commands.Context):
        if ctx.channel.id != COUNTING_CHANNEL_ID:
            return await ctx.send("You can only stop counting in the counting channel!")
        
        countJson = _load_count_state()

        if countJson["status"] == "stopped":
            await ctx.send("Counting is already stopped.")
            await ctx.message.delete()
        else:
            countJson["status"] = "stopped"
            countJson["count"] = 0
            countJson["lastAuthor"] = None
            _save_count_state(countJson)
            await ctx.send("Counting has been stopped. To start counting again, please use the command `!counting`.")
            await ctx.message.delete()
##########################################################################
# The Counting Minigame Logic
    async def countingGame(self, message):
        if message.author.bot: return
        if message.channel.id != COUNTING_CHANNEL_ID:
            return

        countJson = _load_count_state()
        
        if countJson["status"] == "stopped": return
        if message.content.startswith("?") or message.content == "!counting" or message.content == "!stopcounting": return
        elif countJson["status"] == "starting":
            if message.content != "1":
                await message.add_reaction("❌")
                return await message.channel.send("Dang! You didn't start at 1. Type `1` to start counting.")
            countJson["status"] = "running"
            countJson["count"] = 1
            countJson["lastAuthor"] = message.author.id
            _save_count_state(countJson)
            await message.add_reaction("✅")
        elif countJson["status"] == "running":
            if message.content.isnumeric() == False: 
                await message.add_reaction("❌")
                await message.channel.send("Hmpf, That's not a number! You can only count with numbers!\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                _save_count_state(countJson)

            elif message.author.id == countJson["lastAuthor"]:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention}, you can't count twice in a row!\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                _save_count_state(countJson)
                
            elif int(message.content) != countJson["count"] + 1:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention}, you typed the wrong number! Your count should be {countJson['count'] + 1}.\nWe will start over at `1`.")
                countJson["count"] = 0
                countJson["lastAuthor"] = message.author.id
                countJson["status"] = "starting"
                _save_count_state(countJson)

            else:
                await message.add_reaction("✅")
                countJson["count"] += 1
                countJson["lastAuthor"] = message.author.id
                _save_count_state(countJson)
##########################################################################
    @discord.Cog.listener("on_message")
    async def on_message(self, message):
        await self.countingGame(message)
        await self.guessTheNumberGame(message)


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Minigames(bot)) # add the cog to the bot
