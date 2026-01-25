import discord
from discord.ext import commands
import os
from datetime import datetime
from PIL import Image
import io

from db.economy import EconomyBackend
from db.garden import GardenBackend

from ext.system import default_embed

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
slots = ["slot1", "slot2", "slot3", "slot4", "slot5"]
slot_costs = [500, 2000, 5000, 10000, 20000]
pot_positions = [(143, 308), (442, 643), (936, 398), (1348, 799), (1731, 543)]
plant_positions= [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]

class GardenCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
################################################################################## Garden Commands
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
        if not plants:
            embed.description = "**You don't have any seeds yet. Visit the /garden shop to buy some!**"
            return await ctx.respond(embed=embed)
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
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Garden Shop"
        embed.set_thumbnail(url="https://img.icons8.com/fluency/48/online-shop-shopping-bag.png")
        if not plant:
            embed.description = "Here are the available seeds you can buy:"
            embed.set_footer(text="To buy seeds, use the /garden shop command with your desired plant.")
            plants = await GardenBackend().get_all_plants()
            if not greenhouse:
                embed.description += f"\n**Greenhouse** - {slot_costs[0]} coins (You need a greenhouse to plant seeds!)"
            slot_count = 0
            for slot in slots:
                if getattr(greenhouse[0], slot) == -1:
                    embed.description += f"\n**Upgrade Greenhouse** - Increases your greenhouse slots to {slots.index(slot)+1} ({slot_costs[slot_count]} coins)"
                    break
                slot_count += 1
            for plant in plants:
                plant_name = plant.name
                plant_description = plant.description
                plant_price = plant.cost
                embed.description += f"\n**{plant_name}** - {plant_description} ({plant_price} coins)"
            await ctx.respond("*Insert \"[Gaiety in the Golden Age](https://www.youtube.com/watch?v=u5BNQDzXEu8)\" shopping soundtrack*", embed=embed)
        else:
            all_plants = await GardenBackend().get_all_plants()
            selected_plant = None
            if plant.lower() == "greenhouse":
                if greenhouse:
                    embed.description = "You already own a greenhouse! You don't need to buy another one."
                    embed.set_footer(text="Use /garden greenhouse to manage your greenhouse.")
                    return await ctx.respond(embed=embed)
                user_balance = await EconomyBackend().get_balance(user_id=ctx.author.id, guild_id=ctx.guild.id)
                if user_balance < 500:
                    embed.description = f"You do not have enough coins to buy a greenhouse."
                    embed.set_footer(text="Get money or something, and stop being poor. Tried just havin money?")
                    return await ctx.respond(embed=embed)
                await GardenBackend().create_greenhouse(user_id=ctx.author.id, guild_id=ctx.guild.id)
                await EconomyBackend().remove_balance(user_id=ctx.author.id, guild_id=ctx.guild.id, amount=500)
                embed.description = f"*Beep* Greenhouse purchased successfully!"
                embed.set_footer(text="Use /garden greenhouse to manage your greenhouse.")
                return await ctx.respond(embed=embed)
            if plant.lower() == "upgrade greenhouse":
                if not greenhouse:
                    embed.description = "You don't have a greenhouse to upgrade! Buy one first from the /garden shop."
                    await ctx.respond(embed=embed)
                    return
                upgrade_slot = None
                slot_count = 0
                for slot in slots:
                    if getattr(greenhouse[0], slot) == -1:
                        upgrade_slot = slot
                        break
                    slot_count += 1
                if not upgrade_slot:
                    embed.description = "Your greenhouse is already at the maximum upgrade level!"
                    return await ctx.respond(embed=embed)
                upgrade_cost = slot_costs[slot_count]
                user_balance = await EconomyBackend().get_balance(user_id=ctx.author.id, guild_id=ctx.guild.id)
                if user_balance < upgrade_cost:
                    embed.description = f"You do not have enough coins to upgrade your greenhouse."
                    embed.set_footer(text="I've heard prostitution is a good way to make money. But that wouldn't be something for you, right? :)")
                    return await ctx.respond(embed=embed)
                await GardenBackend().upgrade_greenhouse(user_id=ctx.author.id, guild_id=ctx.guild.id, slot=upgrade_slot)
                await EconomyBackend().remove_balance(user_id=ctx.author.id, guild_id=ctx.guild.id, amount=upgrade_cost)
                embed.description = f"*Beep* Greenhouse upgraded successfully! You can now plant more seeds."
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
            user_balance = await EconomyBackend().get_balance(user_id=ctx.author.id, guild_id=ctx.guild.id)
            if user_balance < selected_plant.cost:
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
################################################################################## Greenhouse Commands
    greenhouse = garden.create_subgroup("greenhouse", "Commands related to your greenhouse.")

    @greenhouse.command(name="view", description="View the plants in your greenhouse.")
    async def view_greenhouse(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        greenhouse = await GardenBackend().get_greenhouse_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Your Greenhouse"
        embed.description = "Here are the plants in your greenhouse:"
        embed.set_footer(text="Use /garden greenhouse harvest to harvest fully grown plants.")
        embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")

        if not greenhouse:
            embed.description = "**You don't have a greenhouse yet. Visit the /garden shop to buy one!**"
            embed.set_footer(text="Visit the /garden shop to buy a greenhouse.")
            return await ctx.respond(embed=embed)
        
        background = Image.open("./ext/images/greenhouse_base.png").convert("RGBA")
        img_bytes = io.BytesIO()
        slot_count = 0
        for user in greenhouse:
            for slot in slots:
                slot_count += 1
                plant_id = getattr(user, slot)
                if plant_id == -1: break
                if plant_id == 0:
                    embed.description += f"\n**Slot {slot_count}:** Empty"
                    overlay = Image.open("./ext/images/pot_empty.png").convert("RGBA")
                    background.paste(overlay, pot_positions[slot_count - 1], overlay)
                    continue
                else:
                    grow_time = await GardenBackend().get_plant_grown_time(user_id=ctx.author.id, guild_id=ctx.guild.id, plant_id=plant_id, slot=slot)
                    grow_time_text = ""
                    if grow_time <= 0:
                        grow_time_text = "(Fully Grown!)"
                    elif grow_time > 60:
                        grow_time_hours = grow_time // 60
                        grow_time_minutes = grow_time % 60
                        if grow_time_hours > 24:
                            grow_time_days = grow_time_hours // 24
                            grow_time_hours = grow_time_hours % 24
                            grow_time_text = f"(Grows in {grow_time_days} day{'s' if grow_time_days > 1 else ''}, {grow_time_hours} hour{'s' if grow_time_hours != 1 else ''}, {grow_time_minutes} minute{'s' if grow_time_minutes != 1 else ''})"
                        else:
                            grow_time_text = f"(Grows in {grow_time_hours} hour{'s' if grow_time_hours != 1 else ''}, {grow_time_minutes} minute{'s' if grow_time_minutes != 1 else ''})"
                    embed.description += f"\n**Slot {slot_count}:** {await GardenBackend().get_plant_name(plant_id=plant_id)} {grow_time_text}"
        
        background.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        file = discord.File(img_bytes, filename="greenhouse_base.png")
        embed.set_image(url="attachment://greenhouse_base.png")
        await ctx.respond(embed=embed, file=file)

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
        if not greenhouse:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Your Greenhouse"
            embed.description = "You have no greenhouse yet. Buy one from the /garden shop first!"
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            return await ctx.respond(embed=embed)
        empty_slot = None
        for user in greenhouse:
            for slot in slots:
                slotid = getattr(user, slot)
                if slotid == 0:
                    empty_slot = slot
                    break
        if not empty_slot:
            embed: discord.Embed = await default_embed(ctx.author, fact=False)
            embed.title = "Your Greenhouse"
            embed.description = "Your greenhouse is full! You need to wait for some plants to grow before planting more."
            embed.set_footer(text="Use /garden greenhouse view to see your current plants.")
            embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
            return await ctx.respond(embed=embed)
        
        await GardenBackend().plant_seed_in_greenhouse(user_id=ctx.author.id, guild_id=ctx.guild.id, plant_id=selected_plant, slot=empty_slot)
        await GardenBackend().remove_plant_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id, plant_id=selected_plant)
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Your Greenhouse"
        embed.description = f"You have successfully planted a {await GardenBackend().get_plant_name(plant_id=selected_plant)} seed in your greenhouse!"
        embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
        embed.set_footer(text="Use /garden greenhouse view to see your planted seeds.")
        await ctx.respond(embed=embed)        
    
    @greenhouse.command(name="harvest", description="Harvest fully grown plants from your greenhouse.")
    @discord.option(name="slot_number", description="The slot number of the plant you want to harvest. (1-5)", type=discord.SlashCommandOptionType.integer, required=True)
    async def harvest_plants(self, ctx: discord.ApplicationContext, slot_number: int = None):
        if slot_number < 1 or slot_number > 5:
            return await ctx.respond("Invalid slot number. Please provide a slot number between 1 and 5.", ephemeral=True)
        await ctx.defer()
        greenhouse = await GardenBackend().get_greenhouse_from_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        embed: discord.Embed = await default_embed(ctx.author, fact=False)
        embed.title = "Your Greenhouse"
        embed.set_thumbnail(url="https://img.icons8.com/fluency/48/sprout.png")
        if not greenhouse:
            embed.description = "You have no greenhouse yet to harvest plants from. Buy one from the /garden shop first!"
            return await ctx.respond(embed=embed)
        
        slot = f"slot{slot_number}"
        greenhouse = greenhouse[0]
        plant_id = getattr(greenhouse, slot)
        if plant_id == -1:
            embed.description = f"You don't have this slot in your greenhouse. Buy a bigger greenhouse from the /garden shop!"
            return await ctx.respond(embed=embed)
        if plant_id == 0:
            embed.description = f"Slot {slot_number} is empty. You have no plant to harvest here."
            return await ctx.respond(embed=embed)
        grow_time = await GardenBackend().get_plant_grown_time(user_id=ctx.author.id, guild_id=ctx.guild.id, plant_id=plant_id, slot=slot)
        if grow_time > 0:
            embed.description = f"The plant in slot {slot_number} is not fully grown yet. Please wait until it is fully grown before harvesting."
            return await ctx.respond(embed=embed)
        plant_name = await GardenBackend().get_plant_name(plant_id=plant_id)
        plant_gain = await GardenBackend().get_plant_gain(plant_id=plant_id)
        await GardenBackend().harvest_plant_from_greenhouse(user_id=ctx.author.id, guild_id=ctx.guild.id, slot=slot)
        embed.description = f"You have successfully harvested a {plant_name} from slot {slot_number} and earned {plant_gain} coins!"
        return await ctx.respond(embed=embed)



def setup(bot):
    bot.add_cog(GardenCommands(bot))