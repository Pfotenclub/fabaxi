import discord
from discord.ext import commands
import os

class AdminCommands(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    @discord.Cog.listener("on_message")
    async def commands(self, message):
        if not message.content.startswith("!"): return
        if message.author.id != 327880195476422656: return

        if message.content == "!stuff":
            for member in message.guild.members:
                if member.bot:
                    continue
                await member.add_roles(message.guild.get_role(1341774758076874832))
                print(f"Gave role to {member.name}")
            await message.channel.send("Done")
        
        elif message.content == "!role-colors":
            rolecolors = {
                1234037731987034183: "🍏",
                1137680433614696469: "🍎",
                1233662864590635042: "🍐",
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
            embedText = ""
            for role in rolecolors:
                if role == 0: continue
                embedText += f"{rolecolors[role]} - <@&{role}>\n"
            embed = discord.Embed(title="Role colors", description=embedText)
            embed.color = discord.Color.blue()
            embed.set_footer(text=f"To remove your color, react with ❌")
            msg = await message.channel.send(content="React to change your role color!", embed=embed)
            for role in rolecolors:
                await msg.add_reaction(rolecolors[role])
            

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(AdminCommands(bot)) # add the cog to the bot