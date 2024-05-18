import discord
from discord.ext import commands
import random
from flask import Flask, request
import threading
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

@app.route('/chatgpaint-ping', methods=['POST'])
def ping():
    return "OK", 200

def run():
    print("Starting Flask server")
    app.run(host='0.0.0.0', port=os.getenv("STATUS_UPDATE_PORT"))

class Setups(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_member_join(self, member): # this is called when a member joins the server
        role_ids = [1230984456186237008, 1229073628658794688]  # Ersetzen Sie dies durch Ihre Rollen-IDs
        for role_id in role_ids:
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)
    @commands.Cog.listener()
    async def on_ready(self):
        threading.Thread(target=run).start()
        stati = [
            "Toasting..."
        ]
        await self.bot.change_presence(activity=discord.Game(name="Toasting..."))
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Setups(bot)) # add the cog to the bot