import logging
import os

from discord.ext import commands
from dotenv import load_dotenv

from db.temp_voice import TempVoiceBackend

load_dotenv()


class TempVoice(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler()])

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        joinToCreateVoice = int(os.getenv("JOINTOCREATEVOICE"))
        joinToCreateParent = int(os.getenv("JOINTOCREATEPARENT"))



#################################################################
# Because of the many possible cases, I commented each case, also see: https://preview.redd.it/imeanitsnotwrong-v0-qe3ttm00ledf1.png?auto=webp&s=e7c7ea52cbd63f70b62cc4f2c3f3e1b476e31200
        if before.channel is None: # if member was not in a voice channel before
            if after.channel is not None: # but is in a voice channel now (connect)
                if after.channel.id == joinToCreateVoice: # and if member joined the joinToCreateVoice channel
                    await createTempVoice(self.bot, joinToCreateParent, member)  # create a temporary voice channel for the member (and move them there but thats done in the function)
        
        elif after.channel is None: # if member left a voice channel (disconnect)
            if before.channel.category_id != joinToCreateParent: # if member was not !!in the category!! of the temp channels before
                return  # do nothing - we only care about temp channels
            if before.channel.id == joinToCreateVoice: # if member was in the joinToCreateVoice channel before
                return  # do nothing - joinToCreateVoice is not a temp channel
            if len(before.channel.members) == 0:
                await deleteTempVoice(self.bot, before.channel.id)  # delete the temporary voice channel if it is empty

        
        elif before.channel and after.channel: # if member moved from one voice channel to another - could also do it in a else but this is better for readability
            if before.channel.category_id != joinToCreateParent and after.channel.category_id != joinToCreateParent: # if member moved from a channel outside the temp category to another channel outside the temp category
                return  # do nothing - we only care about temp channels
            if before.channel.category_id != joinToCreateParent and after.channel.category_id == joinToCreateParent: # if member moved from a channel outside of the temp category to a temp channel
                if after.channel.id == joinToCreateVoice: # if the new channel is the joinToCreateVoice channel
                    await createTempVoice(self.bot, joinToCreateParent, member)  # create a temporary voice channel for the member
            elif before.channel.category_id == joinToCreateParent and after.channel.category_id != joinToCreateParent: # if member moved from a temp channel to a normal channel
                if before.channel.id == joinToCreateVoice: # if member moved from the joinToCreateVoice channel
                    return  # do nothing - joinToCreateVoice is not a temp channel, and also to make sure it doesn't get deleted lol
                elif len(before.channel.members) == 0: # if member was the last one in the channel
                    await deleteTempVoice(self.bot, before.channel.id)  # delete the temporary voice channel
            elif before.channel.category_id == joinToCreateParent and after.channel.category_id == joinToCreateParent: # if member moved from a temp channel to another temp channel
                if before.channel.id == joinToCreateVoice: # if member moved from the joinToCreateVoice channel
                    return  # do nothing - joinToCreateVoice is not a temp channel and user was probably moved by the bot
                if before.channel.id != joinToCreateVoice and after.channel.id == joinToCreateVoice: # if member moved to the joinToCreateVoice channel
                    if len(before.channel.members) == 0: # if member was the last one in the channel he left
                        await deleteTempVoice(self.bot, before.channel.id)  # delete the temporary voice channel
                    await createTempVoice(self.bot, joinToCreateParent, member)  # create a temporary voice channel for the member
                if before.channel.id != joinToCreateVoice and after.channel.id != joinToCreateVoice: # if member moved from a temp channel to another temp channel
                    if len(before.channel.members) == 0: # if member was the last one in the channel he left
                        await deleteTempVoice(self.bot, before.channel.id)  # delete the temporary voice channel
#################################################################
def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(TempVoice(bot))  # add the cog to the bot
#################################################################
# helper functions for creating and deleting temp voice channels
async def createTempVoice(bot, joinToCreateParent, member):
    category = bot.get_channel(joinToCreateParent)  # get the category
    channel = await category.create_voice_channel(f"🔊・{member.display_name}'s Channel", user_limit=10)  # create the channel with 10 slots
    await TempVoiceBackend().create_temp_voice(member.id, channel.id, member.guild.id)  # save the channel id to the database
    await member.move_to(channel)  # move the member to the channel
    return channel


async def deleteTempVoice(bot, tempVoiceId):
    channel = bot.get_channel(tempVoiceId)  # get the channel
    await channel.delete()  # delete the channel
    await TempVoiceBackend().delete_temp_voice(tempVoiceId)  # delete the channel from the database
    return channel
