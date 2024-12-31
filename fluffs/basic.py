import discord
from discord.ext import commands
import os
from sqlalchemy import select, update, delete

from database.fluffs_db import Database, FluffUserTable, MasterFluffTable
import logging

class FluffBasic(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot
    logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.db = Database()
        self.bot.loop.create_task(self.db.init_db())

    fluffBasic = discord.SlashCommandGroup(name="fluffs-basic", description="Basic Fluffs Commands") # create a group of slash commands
    @fluffBasic.command(name="intro", description="Introduction to the Fluffs Feature and select your starter Fluff")
    async def intro(self, ctx):
        await ctx.defer()

        # Send introduction message
        embed = discord.Embed(
            title="Welcome to Fluffs!",
            description="Fluffs is a feature that allows you to collect, train, and battle with cute and powerful creatures called Fluffs!"
        )
        embed.add_field(name="Collect 'em all!", value=f"There are many different Fluffs to collect, each with their own unique abilities and stats.\nYou can find them in the wild, or trade with other players to complete your collection!", inline=False)
        embed.add_field(name="Go on an adventure!", value=f"Take your Fluffs on an adventure to explore the world and battle other trainers.\nEarn rewards and level up your Fluffs by winning battles!", inline=False),
        embed.add_field(name="Train your Fluffs!", value=f"Train your Fluffs to increase their stats and learn new moves.\nYou can also evolve your Fluffs into more powerful forms!", inline=False),
        embed.add_field(name="Battle other trainers!", value=f"Challenge other trainers to battles and test your skills.\nBattle other trainers in real-time or compete in tournaments to win prizes!", inline=False),
        embed.add_field(name="Visit the regions!", value=f"Travel to different regions to discover new Fluffs and meet other trainers.\nEach region has its own unique Fluffs and challenges to explore! There are also special regions like the CCH :eyes:", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1234978354650808330/1323415501203832995/Fluff_1.png?ex=67746e3b&is=67731cbb&hm=925098fe7e436265965b9aefb591424ff77617643479709b11c9b49a32b4dcfb&")

        if await self.db.get_fluffs_by_user(ctx.author.id, ctx.guild.id):
            return await ctx.respond(embed=embed)
        
        view = discord.ui.View(timeout=180)
        view.add_item(GetStarterFluffButton())
        embed.set_footer(text="Click the button below to get your starter Fluff!")
        await ctx.respond(embed=embed, view=view)

    @fluffBasic.command(name="fluffs", description="View all the Fluffs you own")
    async def fluffs(self, ctx):
        await ctx.defer()

        fluffs = await self.db.get_fluffs_by_user(ctx.author.id, ctx.guild.id)
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Fluffs",
            description="Here are all the Fluffs you own:"
        )
        if not fluffs:
            embed.add_field(name="No Fluffs", value="You don't own any Fluffs yet. Go catch some in the wild!")
            embed.set_footer(text="Use the /fluffs-basic intro command to get started!")
        else:
            for fluff in fluffs:
                embed.add_field(name=f"{fluff.name}", value=f"Level: {fluff.level}\nHP: {fluff.hp}\nID: {fluff.fluff_user_id}")
        await ctx.respond(embed=embed)
class GetStarterFluffButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Get Starter Fluff", custom_id="getStarterFluff")
        self.db = Database()

    async def callback(self, interaction: discord.Interaction):
        starter1 = await self.db.get_master_fluff_by_id(1)
        starter2 = await self.db.get_master_fluff_by_id(4)
        starter3 = await self.db.get_master_fluff_by_id(7)

        embed = discord.Embed(
            title="Select your Starter Fluff!",
            description="Choose your starter Fluff from the options below:"
        )
        embed.add_field(
            name=f"{starter1.name}",
            value=(
                f"HP: {starter1.hp}\n"
                f"Type: {starter1.type1}" + (f", {starter1.type2}" if starter1.type2 else "") + "\n"
                f"Attack: {starter1.attack}\n"
                f"Defense: {starter1.defense}\n"
                f"Speed: {starter1.speed}\n"
                f"Description:\n{starter1.description}\n"
                
            )
        )
        embed.add_field(
            name=f"{starter2.name}",
            value=(
                f"HP: {starter2.hp}\n"
                f"Type: {starter2.type1}" + (f", {starter2.type2}" if starter2.type2 else "") + "\n"
                f"Attack: {starter2.attack}\n"
                f"Defense: {starter2.defense}\n"
                f"Speed: {starter2.speed}\n"
                f"Description:\n{starter2.description}\n"
            )
        )
        embed.add_field(
            name=f"{starter3.name}",
            value=(
                f"HP: {starter3.hp}\n"
                f"Type: {starter3.type1}" + (f", {starter3.type2}" if starter3.type2 else "") + "\n"
                f"Attack: {starter3.attack}\n"
                f"Defense: {starter3.defense}\n"
                f"Speed: {starter3.speed}\n"
                f"Description:\n{starter3.description}\n"
            )
        )
        embed.set_footer(text="Choose wisely! You can only pick one starter Fluff.")
        view = discord.ui.View(timeout=180)
        view.add_item(SelectStarterFluffButton(1, starter1.name))
        view.add_item(SelectStarterFluffButton(4, starter2.name))
        view.add_item(SelectStarterFluffButton(7, starter3.name))

        await interaction.response.send_message(embed=embed, view=view)

class SelectStarterFluffButton(discord.ui.Button):
    def __init__(self, custom_id : int, name : str):
        super().__init__(style=discord.ButtonStyle.secondary, label=name, custom_id=str(custom_id))
        self.db = Database()

    async def callback(self, interaction: discord.Interaction):
        if await self.db.get_fluffs_by_user(interaction.user.id, interaction.guild.id):
            await interaction.response.send_message("You already have a Fluff! You can't get another starter Fluff.", ephemeral=True)
            return await interaction.message.delete()
        
        await self.db.create_fluff_from_master(interaction.user.id, interaction.guild.id, int(self.custom_id))
        await interaction.response.send_message(f"Congratulations! You have received {self.label} as your starter Fluff.")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(FluffBasic(bot)) # add the cog to the bot