import discord
from discord.ext import commands
from db.temp_voice import TempVoiceBackend
import os
from dotenv import load_dotenv
load_dotenv()

environment = os.getenv("ENVIRONMENT")
if environment == "DEV":
    botGuildId = os.getenv("DEV_SERVER")
elif environment == "PROD":
    botGuildId = os.getenv("PROD_SERVER")

joinToCreateVoice = int(os.getenv("JOINTOCREATEVOICE"))
joinToCreateParent = int(os.getenv("JOINTOCREATEPARENT"))

tempVoiceCmdIds = {
    0 : "Rename",
    1 : "Limit",
    2 : "Lock",
    3 : "Unlock",
    4 : "Claim"
}

class TempVoiceInterface(discord.ui.Button): # Button for the Temp Voice Interface
    def __init__(self, cmdId : int): # cmdId is the command id
        super().__init__( # create the button
            label=tempVoiceCmdIds[cmdId], # set the label to the command name
            style=discord.ButtonStyle.secondary, # set the style to secondary
            custom_id=str(cmdId), # set the custom id to the command id
        )

    async def callback(self, interaction: discord.Interaction): # when the button is clicked
        cmdId = int(self.custom_id) # get the command id
        if interaction.user.voice is None: return await interaction.response.send_message("You must be in a voice channel to use this command!", ephemeral=True)
        userChannel = interaction.user.voice.channel
        if cmdId == 4:
            await ClaimChannel().callback(interaction)
        
        if userChannel.category_id != joinToCreateParent: return await interaction.response.send_message("You must be in a temporary voice channel to use this command!", ephemeral=True)

        noChannelOwnerText = "You must be the channel owner to use this command!"
        if not await memberIsChannelOwner(userChannel.id, interaction.user.id): # if the member is not the channel owner
                return await interaction.response.send_message(noChannelOwnerText, ephemeral=True) # send a message that the member does not have a temporary voice channel
        if cmdId == 0: # if the command id is 0
            await interaction.response.send_modal(RenameChannel(title="Rename your voice channel")) # send the rename channel modal
        elif cmdId == 1: # if the command id is 1
            await interaction.response.send_modal(LimitChannel(title="Set Userlimit")) # send the limit channel modal
        elif cmdId == 2: # if the command id is 2
            await LockChannel().callback(interaction) # lock the channel
        elif cmdId == 3: # if the command id is 3
            await UnlockChannel().callback(interaction) # unlock the channel

class TempVoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="temp-voice-interface", guild_ids=[botGuildId], description="Sends the message for the voicechannel Interface (Only Bot Owner)")
    async def rolebutton(self, ctx: discord.ApplicationContext): # when the command is called
        if ctx.author.id != 327880195476422656: # if the author is not the bot owner
            return await ctx.respond("You are not the Bot Owner!", ephemeral=True) # send a message that the author is not the bot owner
        view = discord.ui.View(timeout=None) # create a view

        embed = discord.Embed( # create an embed
            title="Temp Voice Interface", # set the title
            description="This Interface can be used to configure the temporary voice channels!", # set the description
            color=0x1abc9c, # set the color
            thumbnail="https://img.icons8.com/?size=100&id=aKW2O80wacNj&format=png&color=000000"
        )

        embed.set_footer(text="⚙️ Click on the buttons to use the interface!") # set the footer

        for cmdId in tempVoiceCmdIds: # for every command id
            view.add_item(TempVoiceInterface(cmdId)) # add the button to the view
        await ctx.send(embed=embed, view=view) # send the embed with the view
        await ctx.respond("Message sent!", ephemeral=True) # send a message that the message was sent
    
    @commands.Cog.listener() # when the bot is ready
    async def on_ready(self): # when the bot is ready
        view = discord.ui.View(timeout=None) # create a view
        for cmdId in tempVoiceCmdIds: # for every command id
            view.add_item(TempVoiceInterface(cmdId)) # add the button to the view
        self.bot.add_view(view) # add the view to the bot

class RenameChannel(discord.ui.Modal): # Modal for renaming the channel
    def __init__(self, *args, **kwargs) -> None: # when the modal is created
        super().__init__( # create the modal
            discord.ui.InputText( # create an input text
                label="Choose a new name for your channel!", # set the label
                placeholder="Leave blank to reset", # set the placeholder
                required=False, # set required to false
            ),
            *args,
            **kwargs,
        )
    async def callback(self, interaction: discord.Interaction): # when the modal is submitted

        channel = interaction.user.voice.channel # get the channel
        if channel is not None: # if the channel exists
            try:
                if self.children[0].value: # if the value is not empty
                    await channel.edit(name=self.children[0].value) # set the name to the value
                else: 
                    await channel.edit(name=f"{interaction.user.display_name}'s Channel") # set the name to the default name

                embed = discord.Embed( # create an embed
                title="Update successful!", # set the title
                description=f"Your channel is now named {channel.name}!", # set the description
                color=interaction.user.top_role.color, # set the color
                thumbnail="https://img.icons8.com/?size=100&id=oJQSZNne5Rp0&format=png&color=000000"
                )
                await interaction.response.send_message(embeds=[embed], ephemeral=True) # send the embed
            except discord.HTTPException as e:
                if e.status == 429: # if the error is a rate limit error
                    await interaction.response.send_message("You've ran into the Discord rate limit!\nPlease try again in 10 minutes.", ephemeral=True) # send a rate limit message
                else:
                    raise e # raise the error if it is not a rate limit error

class LimitChannel(discord.ui.Modal): # Modal for setting the user limit
    def __init__(self, *args, **kwargs) -> None: # when the modal is created
        super().__init__( # create the modal
            discord.ui.InputText(  # create an input text
                label="Choose the new limit for your channel!", # set the label
                placeholder="Leave blank to reset the limit", # set the placeholder
                required=False, # set required to false
                max_length=2, # set the max length to 2
            ),
            *args,
            **kwargs,
        )
    async def callback(self, interaction: discord.Interaction): # when the modal is submitted
            
            channel = interaction.user.voice.channel # get the channel
            if not self.children[0].value: # if the value is empty
                self.children[0].value = "10" # set the value to 10 
                await channel.edit(user_limit=10) # set the limit to 10
            elif self.children[0].value.isnumeric(): # if the value is a number
                await channel.edit(user_limit=int(self.children[0].value)) # set the limit to the value
            else:
                return await interaction.response.send_message("Please enter a valid number! (1 - 99)", ephemeral=True) # send a message that the value is not a number
            embed = discord.Embed( # create an embed
                    title="Update successful!", # set the title
                    description=f"Your channel now has a limit of {channel.user_limit}!", # set the description
                    color=interaction.user.top_role.color, # set the color
                    thumbnail="https://img.icons8.com/?size=100&id=2v99zq45tmel&format=png&color=000000"
                )
            await interaction.response.send_message(embeds=[embed], ephemeral=True) # send the embed

class ClaimChannel():
    async def callback(self, interaction: discord.Interaction): # when the command is called

        

        userChannel = interaction.user.voice.channel
        if await memberIsChannelOwner(userChannel.id, interaction.user.id): # if the member is the channel owner
            return await interaction.response.send_message("You already have a temporary voice channel!", ephemeral=True) # send a message that the member already has a temporary voice channel

        for member in interaction.user.voice.channel.members: # for every member in the channel
            if member.id == await TempVoiceBackend().get_owner_id(userChannel.id): # if the member id is the same as the member id
                return await interaction.response.send_message("The channel owner is already in the temporary voice channel!", ephemeral=True) # send a message that the channel owner is already in the channel
        
        await TempVoiceBackend().change_channel_owner_id(userChannel.id, interaction.user.id) # change the channel owner id

        await interaction.user.voice.channel.edit(name=f"{interaction.user.display_name}'s Channel") # set the name of the channel to the member's name

        embed = discord.Embed( # create an embed
            title="Temporary voice channel claimed!", # set the title
            description="You have successfully claimed the temporary voice channel!", # set the description
            color=interaction.user.top_role.color, # set the color
            thumbnail="https://img.icons8.com/?size=100&id=2HUccuweutbu&format=png&color=000000"
        )
        await interaction.respond(embed=embed, ephemeral=True) # send the embed

class LockChannel():
    async def callback(self, interaction: discord.Interaction): # when the command is called
        
        channel = interaction.user.voice.channel # get the channel
        
        permissions = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=False),
            interaction.user: discord.PermissionOverwrite(connect=True)
        }
        await channel.edit(overwrites=permissions) # set the permissions
        embed = discord.Embed( # create an embed
            title="Update successful!", # set the title
            description="Your temporary voice channel has been successfully locked!", # set the description
            color=interaction.user.top_role.color, # set the color
            thumbnail="https://img.icons8.com/?size=100&id=znpDNZWhQe6p&format=png&color=000000"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True) # send the embed

class UnlockChannel(): # when the command is called
    async def callback(self, interaction: discord.Interaction): # when the command is called
        
        channel = interaction.user.voice.channel # get the channel
        permissions = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=True),
        }
        await channel.edit(overwrites=permissions)
        embed = discord.Embed( # create an embed
            title="Update successful!", # set the title
            description="Your temporary voice channel has been successfully unlocked!", # set the description
            color=interaction.user.top_role.color, # set the color
            thumbnail="https://img.icons8.com/?size=100&id=bmqc7DrIxfXZ&format=png&color=000000"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True) # send the embed

def setup(bot):
    bot.add_cog(TempVoiceCog(bot))

async def memberIsChannelOwner(channel_id, member_id):
    if await TempVoiceBackend().get_owner_id(channel_id=channel_id) == member_id:
        return True
    return False