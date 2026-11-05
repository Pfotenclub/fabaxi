import asyncio
import logging
import os
from pathlib import Path
import random

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from ext.cache import load_random_status
from ext.system import send_system_message
from ext.api import ApiServer
from db import Database
import db.tables  # noqa: F401 - Ensure all ORM models are registered on Base.metadata

from app.core.config import ENVIRONMENT, LOG_LEVEL, TOKEN, CURRENT_GUILD_ID, UPTIME_KUMA_PUSH_URL


load_dotenv()
##########################################################################
# Python 3.14 removed the implicit event loop creation in
# asyncio.get_event_loop(); py-cord's Client.__init__ still relies on it
# when no loop is passed explicitly, so we set one up ourselves here.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
##########################################################################
intents = discord.Intents().default()
intents.message_content = True
intents.guild_messages = True
intents.messages = True
intents.guilds = True
intents.members = True
##########################################################################
if ENVIRONMENT == 'PROD':
    bot = commands.Bot(command_prefix='!', intents=intents)
else:
    bot = commands.Bot(command_prefix='!', debug_guilds=[CURRENT_GUILD_ID], intents=intents)

_api_server = ApiServer(bot)
##########################################################################
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()],
)
##########################################################################

@bot.event
async def on_ready():
    logging.info("--------------------------------------")
    logging.info(f"Bot is ready! Logged in as {bot.user.name} ({bot.user.id})")
    logging.info("--------------------------------------")
    try:
        await Database().init_db()
        logging.info("Database schema initialized and verified!")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
    await _api_server.start()
    await send_system_message(bot=bot, content="Bot is ready and online!")
    if not change_status.is_running():
        change_status.start()
    if not uptime_heartbeat.is_running():
        uptime_heartbeat.start()

@bot.event
async def on_close():
    await _api_server.stop()

@tasks.loop(seconds=30)
async def uptime_heartbeat():
    if not bot.is_ready():
        uptime_heartbeat.stop()
        return
    url = UPTIME_KUMA_PUSH_URL
    if not url:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url):
                pass
    except Exception as e:
        logging.warning(f"Uptime Kuma heartbeat failed: {e}")

@tasks.loop(hours=12)
async def change_status():
    new_status = random.choice(load_random_status())
    logging.info(f"Current Status: {new_status}")
    await send_system_message(bot, f"Set new Status:\n**{new_status}**")
    await bot.change_presence(activity=discord.CustomActivity(name=new_status))

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Start the HTTP health/API server early so Kubernetes liveness/startup probes succeed during boot
    loop.run_until_complete(_api_server.start())

    # Load Cogs dynamically from app/cogs
    cogs_dir = Path("app/cogs")
    if cogs_dir.is_dir():
        for cog_file in sorted(cogs_dir.glob("*.py")):
            if cog_file.name.startswith("__"):
                continue
            module_name = f"app.cogs.{cog_file.stem}"
            try:
                bot.load_extension(module_name)
            except Exception as error:
                logging.error(f"{cog_file.name} could not be loaded: [{error}]")
            else:
                logging.info(f"{cog_file.name} was loaded correctly")

    bot.run(TOKEN)
