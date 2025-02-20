import discord
from discord.ext import commands
import os

class Utils(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    
    @discord.Cog.listener("on_raw_reaction_add")
    async def chooseRoleColor(self, payload):
        if payload.member.bot: return
        if payload.message_id != 1341876396611604581: return
        rolecolors = {
                1341767688384675861: "🍏",
                1341767941586423930: "🍎",
                1341767941586423930: "🍐",
                1341768071030898688: "🍊",
                1341768035932835861: "🍋",
                1341766810286161940: "🍋‍🟩",
                1341768096419025068: "🍌",
                1341767290328453212: "🍉",
                1341766887981318164: "🍇",
                1341767441658941470: "🍓",
                1341766994432622653: "🫐",
                1341768250564022384: "🍈",
                1341768940640272488: "🍒",
                0: "❌"
        }

        if str(payload.emoji) == "❌":
            for role in rolecolors:
                if payload.member.guild.get_role(role) in payload.member.roles:
                    await payload.member.remove_roles(payload.member.guild.get_role(role))
            msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            await payload.member.send("Removed your role color")
            return

        for role in rolecolors:
            if payload.member.guild.get_role(role) in payload.member.roles:
                await payload.member.remove_roles(payload.member.guild.get_role(role))
        await payload.member.add_roles(payload.member.guild.get_role(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))]), reason="Role color")
        msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await payload.member.send(f"Changed your role color to {payload.member.guild.get_role(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))]).name}")
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utils(bot)) # add the cog to the bot