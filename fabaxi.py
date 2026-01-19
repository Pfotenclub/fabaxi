import logging
import os
import random

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from ext.cache import load_random_status
from ext.system import send_system_message
from db import Database


load_dotenv()
##########################################################################
intents = discord.Intents().default()
intents.message_content = True
intents.guild_messages = True
intents.messages = True
intents.guilds = True
intents.members = True
##########################################################################
environment = os.getenv('ENVIRONMENT')  # get the environment variable
if environment == 'PROD':
    TOKEN = os.getenv('PROD_TOKEN')
    bot = commands.Bot(command_prefix='!', intents=intents)
else:
    TOKEN = os.getenv('DEV_TOKEN')
    bot = commands.Bot(command_prefix='!', debug_guilds=[os.getenv("DEV_SERVER")], intents=intents)
##########################################################################
logging.basicConfig(level=logging.WARN, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler()])
##########################################################################

@bot.event
async def on_ready():
    print('--------------------------------------')
    print('Bot is ready.')
    print('Eingeloggt als')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------------------------')
    logging.info(f"{bot.user} is ready and online!")
    await Database().init_db()
    logging.info("Database initialized!")
    await send_system_message(bot.user.avatar, "Fabaxi", "Bot is ready and online!")
    await change_status.start()

@tasks.loop(hours=12)
async def change_status():
    new_status = random.choice(load_random_status())
    logging.info(f"Current Status: {new_status}")
    await send_system_message(bot.user.avatar, "Fabaxi", f"Set new Status:\n**{new_status}**")
    await bot.change_presence(activity=discord.CustomActivity(name=new_status))

if __name__ == '__main__':
    # Command Handler
    for i in ["commands", "events", "temp-voice", "minigames", "admin_commands"]:
        if os.path.isdir(f"app/{i}"):
            for j in os.listdir(f"app/{i}"):
                if j.endswith(".py"):
                    try:
                        bot.load_extension(f"app.{i}.{j[:-3]}")
                    except Exception as error:
                        logging.error(f'{j} could not be loaded. [{error}]')
                    else:
                        logging.error(f"{j} was loaded correctly")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    bot.run(TOKEN)