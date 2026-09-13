import logging
import discord
from discord.ext import commands

from ext.system import send_system_message

logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You are not authorized to use this command.")
            await send_system_message(
                bot=self.bot,
                content=f"Unauthorized access attempt by {ctx.author} ({ctx.author.id}) for command `{ctx.command}`.",
            )
        else:
            self.counter += 1
            logger.error(f"Command error in {ctx.command}: {error}")
            await send_system_message(
                bot=self.bot,
                content=f"Error report Nr. {self.counter} after reset.\nServer: {ctx.message.guild}\nCommand: {ctx.message.content}\nError: {error}",
                alert=True,
            )

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        logger.error(f"Application command error in {ctx.command}: {error}")
        if str(error).startswith("The check functions"):
            await ctx.respond("You are not authorized to use this command.", ephemeral=True)
        else:
            await ctx.respond("There was an error while executing the command.", ephemeral=True)
            self.counter += 1
            await send_system_message(
                bot=self.bot,
                content=f"Error report Nr. {self.counter} after reset.\nServer: {ctx.guild}\nCommand: {ctx.command.name}\nUser: {ctx.author} ({ctx.author.id})\nError: ```\n{error}```",
                alert=True,
            )


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
