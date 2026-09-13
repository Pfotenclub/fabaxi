import logging
import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from db.temp_voice import TempVoiceBackend
from app.core.config import JOIN_TO_CREATE_PARENT, JOIN_TO_CREATE_VOICE
from ext.system import default_embed, is_owner

joinToCreateVoice = JOIN_TO_CREATE_VOICE
joinToCreateParent = JOIN_TO_CREATE_PARENT

tempVoiceCmdIds = {0: "Rename", 1: "Limit", 2: "Lock", 3: "Unlock", 4: "Claim"}


class CooldownSetter:
    def __init__(self):
        self.user_dict = {}
        self.timeout_set = 5

    def i_did_smth_too_fast(self, user):
        the_time_i_did_something = time.time()
        if user.id in self.user_dict:
            if the_time_i_did_something - self.user_dict[user.id] < self.timeout_set:
                return True
            else:
                self.user_dict[user.id] = the_time_i_did_something
                return False
        self.user_dict[user.id] = the_time_i_did_something
        return False


class TempVoiceInterface(discord.ui.Button):
    def __init__(self, cmdId: int):
        super().__init__(
            label=tempVoiceCmdIds[cmdId],
            style=discord.ButtonStyle.secondary,
            custom_id=str(cmdId),
        )

    async def callback(self, interaction: discord.Interaction):
        cmdId = int(self.custom_id)
        if interaction.user.voice is None:
            return await interaction.response.send_message(
                "You must be in a voice channel to use this command!", ephemeral=True
            )
        userChannel = interaction.user.voice.channel
        if cmdId == 4:
            return await ClaimChannel().callback(interaction)

        if userChannel.category_id != joinToCreateParent:
            return await interaction.response.send_message(
                "You must be in a temporary voice channel to use this command!", ephemeral=True
            )

        noChannelOwnerText = "You must be the channel owner to use this command!"
        if not await memberIsChannelOwner(userChannel.id, interaction.user.id):
            return await interaction.response.send_message(noChannelOwnerText, ephemeral=True)

        if cmdId == 0:
            await interaction.response.send_modal(RenameChannel(title="Rename your voice channel"))
        elif cmdId == 1:
            await interaction.response.send_modal(LimitChannel(title="Set Userlimit"))
        elif cmdId == 2:
            await LockChannel().callback(interaction)
        elif cmdId == 3:
            await UnlockChannel().callback(interaction)


class RenameChannel(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Choose a new name for your channel!",
                placeholder="Leave blank to reset",
                required=False,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        if channel is not None:
            try:
                if self.children[0].value:
                    await channel.edit(name=f"🔊・{self.children[0].value}")
                else:
                    await channel.edit(name=f"🔊・{interaction.user.display_name}'s Channel")

                embed: discord.Embed = await default_embed()
                embed.title = "Update successful!"
                embed.description = f"Your channel is now named {channel.name}!"
                embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=oJQSZNne5Rp0&format=png&color=000000")
                await interaction.response.send_message(embeds=[embed], ephemeral=True)
            except discord.HTTPException as e:
                if e.status == 429:
                    await interaction.response.send_message(
                        "You've ran into the Discord rate limit!\nPlease try again in 10 minutes.",
                        ephemeral=True,
                    )
                else:
                    raise e


class LimitChannel(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Choose the new limit for your channel!",
                placeholder="Leave blank to reset the limit",
                required=False,
                max_length=2,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        if not self.children[0].value:
            self.children[0].value = "10"
            await channel.edit(user_limit=10)
        elif self.children[0].value.isnumeric():
            await channel.edit(user_limit=int(self.children[0].value))
        else:
            return await interaction.response.send_message(
                "Please enter a valid number! (1 - 99)", ephemeral=True
            )
        embed: discord.Embed = await default_embed()
        embed.title = "Update successful!"
        embed.description = f"Your channel now has a limit of {channel.user_limit}!"
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=2v99zq45tmel&format=png&color=000000")
        await interaction.response.send_message(embeds=[embed], ephemeral=True)


class ClaimChannel(CooldownSetter):
    async def callback(self, interaction: discord.Interaction):
        if self.i_did_smth_too_fast(interaction.user):
            await interaction.response.send_message("You are doing this too fast!", ephemeral=True)
            return

        userChannel = interaction.user.voice.channel
        if await memberIsChannelOwner(userChannel.id, interaction.user.id):
            return await interaction.response.send_message(
                "You already have a temporary voice channel!", ephemeral=True
            )

        for member in interaction.user.voice.channel.members:
            if member.id == await TempVoiceBackend().get_owner_id(userChannel.id):
                return await interaction.response.send_message(
                    "The channel owner is already in the temporary voice channel!", ephemeral=True
                )

        await TempVoiceBackend().change_channel_owner_id(userChannel.id, interaction.user.id)
        await interaction.user.voice.channel.edit(name=f"🔊・{interaction.user.display_name}'s Channel")

        embed: discord.Embed = await default_embed()
        embed.title = "Temporary voice channel claimed!"
        embed.description = "You have successfully claimed the temporary voice channel!"
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=2HUccuweutbu&format=png&color=000000")
        await interaction.respond(embed=embed, ephemeral=True)


class LockChannel(CooldownSetter):
    async def callback(self, interaction: discord.Interaction):
        if self.i_did_smth_too_fast(interaction.user):
            await interaction.response.send_message("You are doing this too fast!", ephemeral=True)
        else:
            channel = interaction.user.voice.channel
            permissions = {
                interaction.guild.default_role: discord.PermissionOverwrite(connect=False),
                interaction.user: discord.PermissionOverwrite(connect=True),
            }
            await channel.edit(overwrites=permissions)
            embed: discord.Embed = await default_embed()
            embed.title = "Update successful!"
            embed.description = "Your temporary voice channel has been successfully locked!"
            embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=znpDNZWhQe6p&format=png&color=000000")
            await interaction.response.send_message(embed=embed, ephemeral=True)


class UnlockChannel(CooldownSetter):
    async def callback(self, interaction: discord.Interaction):
        if self.i_did_smth_too_fast(interaction.user):
            await interaction.response.send_message("You are doing this too fast!", ephemeral=True)
        else:
            channel = interaction.user.voice.channel
            permissions = {interaction.guild.default_role: discord.PermissionOverwrite(connect=True)}
            await channel.edit(overwrites=permissions)
            embed: discord.Embed = await default_embed()
            embed.title = "Update successful!"
            embed.description = "Your temporary voice channel has been successfully unlocked!"
            embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=bmqc7DrIxfXZ&format=png&color=000000")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def memberIsChannelOwner(channel_id, member_id):
    return await TempVoiceBackend().get_owner_id(channel_id=channel_id) == member_id


async def createTempVoice(bot, join_parent_id, member: discord.Member):
    category = bot.get_channel(join_parent_id)
    channel: discord.VoiceChannel = await category.create_voice_channel(
        f"🔊・{member.display_name}'s Channel", user_limit=10
    )
    if member.guild.premium_tier == 3:
        await channel.edit(bitrate=384000)
    elif member.guild.premium_tier == 2:
        await channel.edit(bitrate=256000)
    elif member.guild.premium_tier == 1:
        await channel.edit(bitrate=128000)
    else:
        await channel.edit(bitrate=96000)
    await TempVoiceBackend().create_temp_voice(member.id, channel.id, member.guild.id)
    await member.move_to(channel)
    return channel


async def deleteTempVoice(bot, temp_voice_id):
    channel = bot.get_channel(temp_voice_id)
    if channel:
        await channel.delete()
    await TempVoiceBackend().delete_temp_voice(temp_voice_id)
    return channel


class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="temp-voice-interface")
    @is_owner()
    async def tempVoiceInterface(self, ctx: discord.ApplicationContext):
        view = discord.ui.View(timeout=None)
        embed = discord.Embed(
            title="Temp Voice Interface",
            description="This Interface can be used to configure the temporary voice channels!",
            color=0x1abc9c,
        )
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=aKW2O80wacNj&format=png&color=000000")
        embed.set_footer(text="⚙️ Click on the buttons to use the interface!")

        for cmdId in tempVoiceCmdIds:
            view.add_item(TempVoiceInterface(cmdId))
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        for cmdId in tempVoiceCmdIds:
            view.add_item(TempVoiceInterface(cmdId))
        self.bot.add_view(view)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        parent_id = int(os.getenv("JOINTOCREATEPARENT", 0))
        hub_voice_id = int(os.getenv("JOINTOCREATEVOICE", 0))

        # Member connected to voice
        if before.channel is None:
            if after.channel is not None and after.channel.id == hub_voice_id:
                await createTempVoice(self.bot, parent_id, member)

        # Member disconnected from voice
        elif after.channel is None:
            if before.channel.category_id != parent_id or before.channel.id == hub_voice_id:
                return
            if len(before.channel.members) == 0:
                await deleteTempVoice(self.bot, before.channel.id)

        # Member moved between channels
        elif before.channel and after.channel:
            if before.channel.category_id != parent_id and after.channel.category_id != parent_id:
                return
            if before.channel.category_id != parent_id and after.channel.category_id == parent_id:
                if after.channel.id == hub_voice_id:
                    await createTempVoice(self.bot, parent_id, member)
            elif before.channel.category_id == parent_id and after.channel.category_id != parent_id:
                if before.channel.id != hub_voice_id and len(before.channel.members) == 0:
                    await deleteTempVoice(self.bot, before.channel.id)
            elif before.channel.category_id == parent_id and after.channel.category_id == parent_id:
                if before.channel.id != hub_voice_id and after.channel.id == hub_voice_id:
                    if len(before.channel.members) == 0:
                        await deleteTempVoice(self.bot, before.channel.id)
                    await createTempVoice(self.bot, parent_id, member)
                elif before.channel.id != hub_voice_id and after.channel.id != hub_voice_id:
                    if len(before.channel.members) == 0:
                        await deleteTempVoice(self.bot, before.channel.id)


def setup(bot):
    bot.add_cog(TempVoice(bot))
