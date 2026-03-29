import os
import requests

import aiohttp
import discord
from discord import Webhook
from discord.ext import commands

# used to send a system message to a webhook into the channel fabaxi_systems
async def send_system_message(bot: discord.Bot, content: str, alert: bool = False):
    embed = discord.Embed(title="⚙️System Message⚙️", description=content, color=discord.Color.blue())
    embed.set_footer(text="This is a system message.")
    embed.timestamp = discord.utils.utcnow()
    embed.set_thumbnail(url=bot.user.avatar.url)

    async with aiohttp.ClientSession() as session:
        if os.getenv('WEBHOOK_URL'):
            webhook = Webhook.from_url(os.getenv('WEBHOOK_URL'), session=session)
            if alert:
                embed.color = discord.Color.red()
                embed.set_thumbnail(url="https://img.icons8.com/fluency/48/high-priority--v1.png")
                await webhook.send(embed=embed, username=bot.user.name, content="<@!327880195476422656> <@!474947907913515019>")
            else: await webhook.send(embed=embed, username=bot.user.name)
# default embed generator for commands which sets the user's color and adds a random fact to the footer (if fact=True)
async def default_embed(user: discord.User, fact: bool = True):
    embed = discord.Embed()
    if user.color != discord.Color.default():
        embed.color = user.color
    else:
        embed.color = 0x1abc9c
    if fact:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en") as response:
                data = await response.json()
                fact = data.get("text", "No fact found.")
        embed.set_footer(text=fact)
    return embed

OWNER_IDS = [327880195476422656, 474947907913515019]
def is_owner():
    async def predicate(ctx):
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)