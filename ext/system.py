import os
import requests

import aiohttp
import discord
from discord import Webhook


async def send_system_message(picture_url, username: str, content: str):
    embed = discord.Embed(title="⚙️System Message⚙️", description=content, color=discord.Color.blue())
    embed.set_footer(text="This is a system message.")
    embed.timestamp = discord.utils.utcnow()
    embed.set_thumbnail(url=picture_url)

    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(os.getenv('WEBHOOK_URL'), session=session)
        await webhook.send(embed=embed, username=username)

async def default_embed(user: discord.User):
    embed = discord.Embed()
    if user.color != discord.Color.default(): embed.color = user.color
    else: embed.color = 0x1abc9c
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en")
    fact = response.json().get("text", "No fact found.")
    embed.set_footer(text=fact)
    return embed