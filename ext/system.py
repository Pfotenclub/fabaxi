import os
import aiohttp
import discord
from discord import Webhook
from discord.ext import commands

from app.core.config import OWNER_IDS

# used to send a system message to a webhook into the channel fabaxi_systems
async def send_system_message(bot: discord.Bot, content: str, alert: bool = False):
    embed = discord.Embed(title="⚙️System Message⚙️", description=content, color=discord.Color.blue())
    embed.set_footer(text="This is a system message.")
    embed.timestamp = discord.utils.utcnow()
    if bot and getattr(bot, "user", None) and getattr(bot.user, "avatar", None):
        embed.set_thumbnail(url=bot.user.avatar.url)

    async with aiohttp.ClientSession() as session:
        webhook_url = os.getenv('WEBHOOK_URL')
        if webhook_url:
            webhook = Webhook.from_url(webhook_url, session=session)
            bot_name = bot.user.name if bot and getattr(bot, "user", None) else "Fabaxi"
            if alert:
                embed.color = discord.Color.red()
                embed.set_thumbnail(url="https://img.icons8.com/fluency/48/high-priority--v1.png")
                owner_mentions = " ".join(f"<@!{uid}>" for uid in OWNER_IDS)
                await webhook.send(embed=embed, username=bot_name, content=owner_mentions)
            else:
                await webhook.send(embed=embed, username=bot_name)


# default embed generator for commands which sets the user's color and adds a random fact to the footer (if fact=True)
async def default_embed(fact: bool = True):
    embed = discord.Embed()
    embed.color = 0x1abc9c
    if fact:
        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en") as response:
                    if response.status == 200:
                        data = await response.json()
                        fact_text = data.get("text", "No fact found.")
                    else:
                        fact_text = None
            if fact_text:
                embed.set_footer(text=fact_text)
        except Exception:
            pass
    return embed

def is_owner():
    async def predicate(ctx):
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)