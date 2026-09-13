import discord
from discord.ext import commands

from app.core.config import WELCOME_ROLE_IDS


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        for role_id in WELCOME_ROLE_IDS:
            role = discord.utils.get(member.guild.roles, id=role_id)
            if role:
                await member.add_roles(role)


def setup(bot):
    bot.add_cog(Welcome(bot))
