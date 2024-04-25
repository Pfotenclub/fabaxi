from discord.ext import commands
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = commands.Bot(debug_guilds=[1001916230069911703], prefix='irgendwas')

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

"""@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx ):
    await ctx.respond("Hey!")"""

if __name__ == '__main__':
    if os.path.isdir("cogs"):
        os.chdir("cogs")
    else:
        os.chdir("cogs")
    for i in os.listdir():
        if i.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{i[:-3]}")
            except Exception as error:
                print('{} konnte nicht geladen werden. [{}]'.format(i, error))
            else:
                print(f"{i} wurde geladen")

bot.run(os.getenv('TOKEN')) # run the bot with the token

