import discord
from discord.ext import commands
import os
from datetime import datetime

from db.economy import EconomyBackend
from db.garden import GardenBackend

from ext.system import default_embed

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
slots = ["slot1", "slot2", "slot3", "slot4", "slot5"]

class GardenCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    garden = discord.SlashCommandGroup("garden", "Commands related to the garden system.")


    @garden.command(name="seeds", description="View all the seeds you have and can plant.")
    async def seeds(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        plants = await GardenBackend().get_plant_summary_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Your Garden Plants"
        embed.description = "Here are all the plants you have in your garden:"
        embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
        embed.set_footer(text="Use /garden greenhouse plant to plant your seeds in your greenhouse.")
        for plant in plants:
            plant_name = await GardenBackend().get_plant_name(plant_id=plant)
            embed.description += f"\n**{plant_name}**: {plants[plant]} seed{'s' if plants[plant] > 1 else ''}"
        await ctx.respond(embed=embed)
        
    @garden.command(name="shop", description="View the garden shop to buy seeds.")
    @discord.option(name="plant", description="The plant you want to buy seeds for. (Has to be the exact name)", type=discord.SlashCommandOptionType.string, required=False)
    async def shop(self, ctx: discord.ApplicationContext, plant: str = None):
        await ctx.defer()
        # Showing the shop if no plant is specified
        greenhouse = await GardenBackend().get_greenhouse_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        if not plant:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Garden Shop"
            embed.description = "Here are the available seeds you can buy:"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
            embed.set_footer(text="To buy seeds, use the /garden shop command with your desired plant.")
            plants = await GardenBackend().get_all_plants()
            if not greenhouse:
                embed.description += "\n**Greenhouse** - 500 coins (You need a greenhouse to plant seeds!)"
            for plant in plants:
                plant_name = plant.name
                plant_price = plant.cost
                embed.description += f"\n**{plant_name}** - {plant_price} coins"
            await ctx.respond("*Insert \"[Gaiety in the Golden Age](https://www.youtube.com/watch?v=u5BNQDzXEu8)\" shopping soundtrack*", embed=embed)
        else:
            all_plants = await GardenBackend().get_all_plants()
            selected_plant = None
            if plant.lower() == "greenhouse":
                if greenhouse:
                    embed: discord.Embed = await default_embed(ctx.author, fact=False)
                    embed.title = "Garden Shop"
                    embed.description = "You already own a greenhouse! You don't need to buy another one."
                    embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
                    embed.set_footer(text="Use /garden greenhouse to manage your greenhouse.")
                    return await ctx.respond(embed=embed)
                user_balance = await EconomyBackend().get_economy_record(user_id=ctx.author.id, guild_id=ctx.guild.id)
                if not user_balance or user_balance.balance < 500:
                    embed: discord.Embed = await default_embed(ctx.author, fact=False)
                    embed.title = "Garden Shop"
                    embed.description = f"You do not have enough coins to buy a greenhouse."
                    embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
                    embed.set_footer(text="Get money or something, and stop being poor. Tried just havin money?")
                    return await ctx.respond(embed=embed)
                await GardenBackend().create_greenhouse(user_id=ctx.author.id, guild_id=ctx.guild.id)
                await EconomyBackend().remove_balance(user_id=ctx.author.id, guild_id=ctx.guild.id, amount=500)
                embed: discord.Embed = await default_embed(ctx.author, fact=False)
                embed.title = "Garden Shop"
                embed.description = f"*Beep* Greenhouse purchased successfully!"
                embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
                embed.set_footer(text="Use /garden greenhouse to manage your greenhouse.")
                return await ctx.respond(embed=embed)
            for p in all_plants:
                if p.name.lower() == plant.lower():
                    selected_plant = p
                    break
            if not selected_plant:
                embed: discord.Embed = await default_embed(ctx.author, fact=False)
                embed.title = "Garden Shop"
                embed.description = f"The plant '{plant}' was not found in the garden shop. Please check the name and try again."
                embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
                embed.set_footer(text="Use /garden shop to view all available plants, or stop being dumb.")
                return await ctx.respond(embed=embed)
            user_balance = await EconomyBackend().get_economy_record(user_id=ctx.author.id, guild_id=ctx.guild.id)
            if not user_balance or user_balance.balance < selected_plant.cost:
                embed: discord.Embed = await default_embed(ctx.author, fact=False)
                embed.title = "Garden Shop"
                embed.description = f"You do not have enough coins to buy a seed of {selected_plant.name}."
                embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
                embed.set_footer(text="Get money or something, and stop being poor. Tried just havin money?")
                return await ctx.respond(embed=embed)
            
            await GardenBackend().buy_plant(user_id=ctx.author.id, guild_id=ctx.guild.id, plant_id=selected_plant.plant_id)
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Garden Shop"
            embed.description = f"*Beep* {selected_plant.name} seed purchased successfully!"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
            embed.set_footer(text="Use /garden seeds to view your purchased seeds.")
            await ctx.respond(embed=embed)

    greenhouse = garden.create_subgroup("greenhouse", "Commands related to your greenhouse.")
    @greenhouse.command(name="view", description="View the plants in your greenhouse.")
    async def view_greenhouse(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        greenhouse = await GardenBackend().get_greenhouse_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Your Greenhouse"
        embed.description = "Here are the plants in your greenhouse:"

        if not greenhouse:
            embed.description = "**You don't have a greenhouse yet. Use /garden greenhouse create to get started!**"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            embed.set_footer(text="Visit the /garden shop to buy a greenhouse.")
            return await ctx.respond(embed=embed)
        slot_count = 0
        for plant in greenhouse:
            for slot in slots:
                slot_count += 1
                plant_id = getattr(plant, slot)
                if plant_id == -1: break
                await ctx.respond("Test")
        
        await ctx.respond(embed=embed)

    @greenhouse.command(name="plant", description="Plant a seed in your greenhouse.")
    @discord.option(name="plant", description="The plant you want to plant. (Has to be the exact name)", type=discord.SlashCommandOptionType.string, required=True)
    async def plant_seed(self, ctx: discord.ApplicationContext, plant: str):
        await ctx.defer()
        user_plants = await GardenBackend().get_plant_summary_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        if not user_plants:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Your Greenhouse"
            embed.description = "You have no seeds to plant. Visit the /garden shop to buy some!"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            return await ctx.respond(embed=embed)
        
        selected_plant = None
        for p in user_plants:
            plant_name = await GardenBackend().get_plant_name(plant_id=p)
            if plant_name.lower() == plant.lower():
                selected_plant = p
                break
        if not selected_plant:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Your Greenhouse"
            embed.description = f"You do not have any seeds of '{plant}' to plant. Check your /garden seeds."
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            return await ctx.respond(embed=embed)
        greenhouse = await GardenBackend().get_greenhouse_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        empty_slot = None
        if not greenhouse:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Your Greenhouse"
            embed.description = "You have no greenhouse yet. Buy one from the /garden shop first!"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            return await ctx.respond(embed=embed)
        

        


def setup(bot):
    bot.add_cog(GardenCommands(bot))