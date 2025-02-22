import discord
from discord.ext import commands
import pickle
import os
from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
class TempVoice(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        joinToCreateParent = None
        joinToCreateVoice = None
        if environment == 'DEV':
            joinToCreateVoice = 1234040036299640844
            joinToCreateParent = 1234039999775772768
        elif environment == 'PROD':
            joinToCreateVoice = 1229081255115624549
            joinToCreateParent = 1058459667887575131
        
        # if member was not in a voice channel before
        if before.channel is None:
            # if member is in a voice channel now
            if after.channel is not None:
                # if the member joined the joinToCreateVoice channel
                if after.channel.id == joinToCreateVoice:
                    await createTempVoice(self.bot, joinToCreateParent, member) # create a temporary voice channel for the member
        # if member left a voice channel (disconnect)
        elif after.channel is None:
            # if member was not in the category of the temp channels before
            if before.channel.category_id != joinToCreateParent:
                return # do nothing - we only care about temp channels
            # if member was in the joinToCreateVoice channel before
            if before.channel.id == joinToCreateVoice:
                return # do nothing - joinToCreateVoice is not a temp channel
            if len(before.channel.members) == 0:
                await deleteTempVoice(self.bot, before.channel.id) # delete the temporary voice channel if it is empty
        
        # if member moved from one voice channel to another - could also do it in a else but this is better for readability
        elif before.channel and after.channel:
            # if member moved from a normal channel to another normal channel
            if before.channel.category_id != joinToCreateParent and after.channel.category_id != joinToCreateParent:
                return # do nothing - we only care about temp channels
            # if member moved from a normal channel to a temp channel
            if before.channel.category_id != joinToCreateParent and after.channel.category_id == joinToCreateParent:
                # if member moved to the joinToCreateVoice channel
                if after.channel.id == joinToCreateVoice: 
                    await createTempVoice(self.bot, joinToCreateParent, member) # create a temporary voice channel for the member
            # if member moved from a temp channel to a normal channel
            elif before.channel.category_id == joinToCreateParent and after.channel.category_id != joinToCreateParent:
                # if member moved from the joinToCreateVoice channel
                if before.channel.id == joinToCreateVoice:
                    return # do nothing - joinToCreateVoice is not a temp channel
                # if member was the last one in the channel
                elif len(before.channel.members) == 0:
                    await deleteTempVoice(self.bot, before.channel.id) # delete the temporary voice channel
            # if member moved from a temp channel to another temp channel
            elif before.channel.category_id == joinToCreateParent and after.channel.category_id == joinToCreateParent:
                # if member moved from the joinToCreateVoice channel
                if before.channel.id == joinToCreateVoice:
                    return # do nothing - joinToCreateVoice is not a temp channel and user was probably moved by the bot
                # if member moved to the joinToCreateVoice channel
                if before.channel.id != joinToCreateVoice and after.channel.id == joinToCreateVoice:
                    # if member was the last one in the channel he left
                    if len(before.channel.members) == 0: await deleteTempVoice(self.bot, before.channel.id) # delete the temporary voice channel
                    await createTempVoice(self.bot, joinToCreateParent, member) # create a temporary voice channel for the member
                # if member moved from a temp channel to another temp channel
                if before.channel.id != joinToCreateVoice and after.channel.id != joinToCreateVoice:
                    # if member was the last one in the channel he left
                    if len(before.channel.members) == 0: await deleteTempVoice(self.bot, before.channel.id) # delete the temporary voice channel


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(TempVoice(bot)) # add the cog to the bot



async def createTempVoice(bot, joinToCreateParent, member):
    category = bot.get_channel(joinToCreateParent) # get the category
    channel = await category.create_voice_channel(f"{member.display_name}'s Channel", user_limit=10) # create the channel with 5 slots
    pickle.dump((channel.id, member.id), open(f"temp-voice-ids/{channel.id}.pkl", "wb")) # save the channel id and member id to a file
    await member.move_to(channel) # move the member to the channel
    return channel


async def deleteTempVoice(bot, tempVoiceId):
    channel = bot.get_channel(tempVoiceId) # get the channel
    await channel.delete() # delete the channel
    os.remove(f"temp-voice-ids/{channel.id}.pkl") # remove the file
    return channel