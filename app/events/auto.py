import json
from datetime import datetime

import discord
from discord.ext import commands
from ext.system import send_system_message


class AutoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You are not authorized to use this command.")
            await send_system_message(
                picture_url=self.bot.user.avatar,
                username=self.bot.user.name,
                content=f"Unauthorized access attempt by {ctx.author} ({ctx.author.id}) ({ctx.guild.id}) for command `{ctx.command}`.",
            )
        else:
            self.counter = + 1
            # channel = self.bot.get_channel(data["error"])
            await send_system_message(
                picture_url=self.bot.user.avatar,
                username=self.bot.user.name,
                content=f"Error report Nr. {self.counter} after reset.\nServer: {ctx.message.guild}\nCommand: {ctx.message.content}\nError: {error}",
                alert=True
            )
            """ Storing this for archive purposes, maybe useful later
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
            """

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        print(error)
        if str(error).startswith("The check functions"):
            await ctx.respond("You are not authorized to use this command.")
        else:
            self.counter = + 1
            await send_system_message(
                picture_url=self.bot.user.avatar,
                username=self.bot.user.name,
                content=f"Error report Nr. {self.counter} after reset.\nServer: {ctx.guild}\nCommand: {ctx.command.name}\nError: {error}",
                alert=True
            )
            """ Storing this for archive purposes, maybe useful later
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
            """

def setup(bot):
    bot.add_cog(AutoCommands(bot))
