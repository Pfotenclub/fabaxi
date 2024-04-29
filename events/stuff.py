from discord.ext import commands, tasks
import requests

class StatusPageUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_status.start()

    def cog_unload(self):
        self.update_status.cancel()

    @tasks.loop(seconds=299.0)
    async def update_status(self):
        requests.get('https://klara.wolfiii.gay/api/push/FfkEDcIxAt?status=up&msg=OK&ping=')

def setup(bot):
    bot.add_cog(StatusPageUpdate(bot))