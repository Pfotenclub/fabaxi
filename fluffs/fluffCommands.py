import discord
from discord.ext import commands
import os
from sqlalchemy import select, update, delete
import random

from database.fluffs_db import Database, FluffUserTable, MasterFluffTable
import logging
import asyncio

class FluffBasic(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot
    logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot # save the bot instance
        self.db = Database() # create an instance of the database class from fluffs_db.py
        self.bot.loop.create_task(self.db.init_db()) # create a task to initialize the database

    fluffCommandGroup = discord.SlashCommandGroup(name="fluffs", description="Fluff Commands") # create a group of slash commands
    @fluffCommandGroup.command(name="intro", description="Introduction to the Fluffs Feature and select your starter Fluff")
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

        # Check if user already has a Fluff. If not, show button to get starter Fluff
        if await self.db.get_fluffs_by_user(ctx.author.id, ctx.guild.id):
            return await ctx.respond(embed=embed)
        
        view = discord.ui.View(timeout=180)
        view.add_item(GetStarterFluffButton())
        embed.set_footer(text="Click the button below to get your starter Fluff!")
        await ctx.respond(embed=embed, view=view)

    @fluffCommandGroup.command(name="my-fluffs", description="View all the Fluffs you own")
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
    
    @fluffCommandGroup.command(name="battle", description="Challenge another player to a Fluff battle")
    async def battle(self, ctx, user: discord.Member):
        # Check if user has any Fluffs
        challenger_fluffs = await self.db.get_fluffs_by_user(ctx.author.id, ctx.guild.id)
        if not challenger_fluffs: return await ctx.respond("You can't battle without any Fluffs! Use the /fluffs-basic intro command to get started.", ephemeral=True)
        # If user is a bot, return error message
        if user.bot: return await ctx.respond("You can't battle a bot!", ephemeral=True)
        # Check if user has any Fluffs
        oponent_fluffs = await self.db.get_fluffs_by_user(user.id, ctx.guild.id)
        if not oponent_fluffs: return await ctx.respond("You can't battle someone who doesn't have any fluffs!", ephemeral=True)

        # Get main Fluffs for both users
        challenger_main = None
        for fluff in challenger_fluffs:
            if fluff.main:
                challenger_main = fluff
                break
        opponent_main = None
        for fluff in oponent_fluffs:
            if fluff.main:
                opponent_main = fluff
                break

        # Send battle challenge message with accept and decline buttons for the opponent
        embed = discord.Embed(
            title=f"{ctx.author.display_name} has challenged you to a fluff battle!",
            description=f"{user.mention}, do you accept the challenge?",
        )
        embed.add_field(
            name=f"{ctx.author.display_name}'s Fluff",
            value=(
                f"{challenger_main.name}\n"
                f"Level: {challenger_main.level}\nHP: {challenger_main.hp}\n"
            )
        )
        embed.add_field(
            name=f"{user.display_name}'s Fluff",
            value=(
                f"{opponent_main.name}\n"
                f"Level: {opponent_main.level}\nHP: {opponent_main.hp}\n"
            )
        )
        embed.set_footer(text="Accept the challenge with ✅ or decline with ❌")
        view = discord.ui.View(timeout=300)
        view.add_item(BattleAcceptButton(discord.ButtonStyle.success, "Accept", 1, challenger=ctx.author, opponent=user))
        view.add_item(BattleAcceptButton(discord.ButtonStyle.danger, "Decline", 2, challenger=ctx.author, opponent=user))

        await ctx.respond(f"{user.mention}", embed=embed, view=view)

        

        
# Gives the user the option to get a starter Fluff if they don't already have one
class GetStarterFluffButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Get Starter Fluff", custom_id="getStarterFluff") # create a button with the label "Get Starter Fluff" and the custom_id "getStarterFluff"
        self.db = Database() # create an instance of the database class from fluffs_db.py

    async def callback(self, interaction: discord.Interaction):
        # Gets the predefined starter Fluffs from the database
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

# Gives the user his selected starter Fluff
class SelectStarterFluffButton(discord.ui.Button):
    def __init__(self, custom_id : int, name : str):
        super().__init__(style=discord.ButtonStyle.secondary, label=name, custom_id=str(custom_id))
        self.db = Database()

    async def callback(self, interaction: discord.Interaction):
        if await self.db.get_fluffs_by_user(interaction.user.id, interaction.guild.id):
            await interaction.response.send_message("You already have a Fluff! You can't get another starter Fluff.", ephemeral=True)
            return await interaction.message.delete()
        
        await self.db.create_fluff_from_master(interaction.user.id, interaction.guild.id, int(self.custom_id), main=True)
        await interaction.response.send_message(f"Congratulations! You have received {self.label} as your starter Fluff.")

# Gives the opponent the option to accept or decline the battle challenge
class BattleAcceptButton(discord.ui.Button):
            def __init__(self, style, label, custom_id : int, challenger : discord.User, opponent : discord.User):
                super().__init__(style=style, label=label, custom_id=str(custom_id))
                self.challenger = challenger
                self.opponent = opponent
                self.db = Database()

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != self.opponent.id: return await interaction.respond("You can't accept or decline a challenge that wasn't sent to you!", ephemeral=True)
                if self.custom_id == "2": 
                    await interaction.respond(f"{interaction.user.display_name} has declined the challenge!")
                    return await interaction.message.delete()

                challenger_fluffs = await self.db.get_fluffs_by_user(self.challenger.id, interaction.guild.id)
                opponent_fluffs = await self.db.get_fluffs_by_user(self.opponent.id, interaction.guild.id)
                challenger_main = None
                opponent_main = None
                for fluff in challenger_fluffs:
                    if fluff.main:
                        challenger_main = fluff
                        break
                for fluff in opponent_fluffs:
                    if fluff.main:
                        opponent_main = fluff
                        break
                challenger_hp = challenger_main.hp
                opponent_hp = opponent_main.hp

                if challenger_hp == 0: return await interaction.respond(f"{self.challenger.display_name} doesn't have any HP left and can't battle!")
                if opponent_hp == 0: return await interaction.respond(f"{self.opponent.display_name} doesn't have any HP left and can't battle!")

                embed = discord.Embed(
                    title="Fluff Battle!",
                    description=f"{self.challenger.display_name} vs {self.opponent.display_name}",
                )
                embed.add_field(
                    name=f"{self.challenger.display_name}'s Fluff",
                    value=(
                        f"{challenger_main.name}\n"
                        f"Level: {challenger_main.level}\nHP: {challenger_hp}\n"
                    )
                )
                embed.add_field(
                    name=f"{self.opponent.display_name}'s Fluff",
                    value=(
                        f"{opponent_main.name}\n"
                        f"Level: {opponent_main.level}\nHP: {opponent_hp}\n"
                    )
                )
                embed.set_footer(text="The Battle will begin shortly!")
                await interaction.message.delete()
                await interaction.respond(embed=embed)
                embed.set_footer(text="The Battle has begun!")
                
                await asyncio.sleep(5)

                attacker = 1
                if opponent_main.speed > challenger_main.speed: attacker = 2

                while challenger_hp > 0 and opponent_hp > 0:
                    if attacker == 1: 
                        opponent_hp = await executeAttack(self=self, attacker=challenger_main, opponent=opponent_main, oppponent_hp=opponent_hp)
                        attacker = 2
                    updateBattleEmbed(self, embed, challenger_main, opponent_main, challenger_hp, opponent_hp)
                    await interaction.edit_original_response(embed=embed)
                    await asyncio.sleep(3)

                    if opponent_hp == 0: break

                    if attacker == 2:
                        challenger_hp = await executeAttack(self=self, attacker=opponent_main, opponent=challenger_main, oppponent_hp=challenger_hp)
                        attacker = 1

                    updateBattleEmbed(self, embed, challenger_main, opponent_main, challenger_hp, opponent_hp)
                    await interaction.edit_original_response(embed=embed)
                    await asyncio.sleep(3)
                await self.db.set_fluff_hp(challenger_main.fluff_user_id, challenger_hp)
                await self.db.set_fluff_hp(opponent_main.fluff_user_id, opponent_hp)

                if challenger_hp == 0: await interaction.edit_original_response(content=f"{self.opponent.display_name} has won the battle!", embed=None)
                if opponent_hp == 0: await interaction.edit_original_response(content=f"{self.challenger.display_name} has won the battle!", embed=None)


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(FluffBasic(bot)) # add the cog to the bot

async def executeAttack(self, attacker, opponent, oppponent_hp):
    base_damage = attacker.attack - opponent.defense / 2
    # Checking for type effectiveness
    if await self.db.is_effective(attacker.type1, opponent.type1) == "+": base_damage *= 2
    elif await self.db.is_effective(attacker.type1, opponent.type1) == "-": base_damage /= 2
    elif await self.db.is_effective(attacker.type1, opponent.type1) == "0": base_damage *= 0

    if attacker.type2:
        if await self.db.is_effective(attacker.type2, opponent.type1) == "+": base_damage *= 2
        elif await self.db.is_effective(attacker.type2, opponent.type1) == "-": base_damage /= 2
        elif await self.db.is_effective(attacker.type2, opponent.type1) == "0": base_damage *= 0

    if opponent.type2:
        if await self.db.is_effective(attacker.type1, opponent.type2) == "+": base_damage *= 2
        elif await self.db.is_effective(attacker.type1, opponent.type2) == "-": base_damage /= 2
        elif await self.db.is_effective(attacker.type1, opponent.type2) == "0": base_damage *= 0

        if attacker.type2:
            if await self.db.is_effective(attacker.type2, opponent.type2) == "+": base_damage *= 2
            elif await self.db.is_effective(attacker.type2, opponent.type2) == "-": base_damage /= 2
            elif await self.db.is_effective(attacker.type2, opponent.type2) == "0": base_damage *= 0

        
    

    if base_damage < 1: base_damage = 1
    if random.randint(1, 100) <= 5: base_damage *= 2 # Critical Hit
    elif random.randint(1, 100) <= 3: base_damage = 0 # Miss
    base_damage = int(base_damage)
    oppponent_hp -= base_damage
    if oppponent_hp < 0: oppponent_hp = 0
    return oppponent_hp

def updateBattleEmbed(self, embed, challenger_main, opponent_main, challenger_hp, opponent_hp):
    embed.clear_fields()
    embed.add_field(
        name=f"{self.challenger.display_name}'s Fluff",
        value=(
            f"{challenger_main.name}\n"
            f"Level: {challenger_main.level}\nHP: {challenger_hp}\n"
        )
    )
    embed.add_field(
        name=f"{self.opponent.display_name}'s Fluff",
        value=(
            f"{opponent_main.name}\n"
            f"Level: {opponent_main.level}\nHP: {opponent_hp}\n"
        )
    )
    embed.add_field(
        name="Battle Log",
        value="",
        inline=False
    )