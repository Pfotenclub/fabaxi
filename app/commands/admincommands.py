import discord
from discord.ext import commands
import os
import json

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
data_path = None
if environment == "DEV": data_path = ".\data"
elif environment == "PROD": data_path = "/db"

class AdminCommands(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.command(name="role-colors") # this is a command that can be used by users
    @commands.is_owner()
    async def roleColors(self, ctx): # the first argument of a command is always the context

        roleJson = None
        with open(os.path.join(data_path, "rolecolors.json"), "r", encoding='utf-8') as file: roleJson = json.load(file)
        roleMsgId = roleJson["roleMsgId"]
        rolecolors = roleJson["rolecolors"]
        embedText = ""
        for role in rolecolors:
            if int(role) == 0: continue
            embedText += f"{rolecolors[role]} - <@&{int(role)}>\n"
        embed = discord.Embed(title="Role colors", description=embedText)
        embed.color = 0x1abc9c
        embed.set_footer(text=f"To remove your color, react with ❌")
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=Qw82NJLhJoqc&format=png&color=000000")
        msg = await ctx.send(content="React to change your role color!", embed=embed)
        for role in rolecolors:
            await msg.add_reaction(rolecolors[role])
        
        with open(os.path.join(data_path, "rolecolors.json"), "r+", encoding='utf-8') as file:
            data = json.load(file)
            data["roleMsgId"] = msg.id
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
    

    @discord.Cog.listener("on_raw_reaction_add")
    async def chooseRoleColor(self, payload):
        if payload.member.bot: return

        roleJson = None
        with open(os.path.join(data_path, "rolecolors.json"), "r", encoding='utf-8') as file: roleJson = json.load(file)
        roleMsgId = roleJson["roleMsgId"]
        if payload.message_id != roleMsgId: return # the message id of the role color message in #chat-color
        rolecolors = roleJson["rolecolors"]
        if str(payload.emoji) == "❌":
            for role in rolecolors:
                if payload.member.guild.get_role(int(role)) in payload.member.roles:
                    await payload.member.remove_roles(payload.member.guild.get_role(int(role)))
            msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            await payload.member.send("Removed your role color")
            return

        for role in rolecolors:
            if payload.member.guild.get_role(int(role)) in payload.member.roles:
                await payload.member.remove_roles(payload.member.guild.get_role(int(role)))
        await payload.member.add_roles(payload.member.guild.get_role(int(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))])), reason="Role color")
        msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await payload.member.send(f"Changed your role color to {payload.member.guild.get_role(int(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))])).name}")        

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(AdminCommands(bot)) # add the cog to the bot