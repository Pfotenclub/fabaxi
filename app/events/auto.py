import json
from datetime import datetime

import discord
from discord.ext import commands


class AutoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            if ctx.message.content == "n!help":
                await ctx.send("Bitte beachte, dass wir nun / Commands benutzen.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You are not authorized to use this command.")
        else:
            self.counter = + 1
            # channel = self.bot.get_channel(data["error"])
            embed = discord.Embed(title="Ops, there is an error!",
                                  description="Error report Nr. {} after reset.".format(self.counter),
                                  color=ctx.author.color)
            embed.add_field(name='Server:', value='{}'.format(ctx.message.guild), inline=True)
            embed.add_field(name='Command:', value='{}'.format(ctx.message.content), inline=False)
            embed.add_field(name='Error:', value="```python\n{}```".format(error), inline=False)
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_footer(text='Error Message', icon_url=ctx.message.author.avatar)
            embed.timestamp = datetime.utcnow()
            await ctx.channel.send(embed=embed)
            # await channel.send(embed=embed)
            print(error)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        print(error)
        if str(error).startswith("The check functions"):
            await ctx.respond("Es scheint als seist du nicht registriert")
        else:
            # channel = self.bot.get_channel(data["error"])
            embed = discord.Embed(title="Ops, there is an error!",
                                  color=ctx.author.color)
            embed.add_field(name='Server:', value='{}'.format(ctx.guild), inline=True)
            embed.add_field(name='Command:', value='{}'.format(ctx.command.name), inline=False)
            embed.add_field(name='Error:', value="```python\n{}```".format(error), inline=False)
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_footer(text='Error Message', icon_url=ctx.author.avatar)
            embed.timestamp = datetime.utcnow()
            await ctx.respond(embed=embed)
            # await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(AutoCommands(bot))
