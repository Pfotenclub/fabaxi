import re

import discord


async def check_emoji(guild, emoji_id) -> bool:
    try:
        await guild.fetch_emoji(emoji_id)
    except discord.NotFound:
        return False
    else:
        return True


async def check_color(color: str) -> bool:
    if not isinstance(color, str):
        return False
    if not re.match(r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$', color):
        return False
    return True
