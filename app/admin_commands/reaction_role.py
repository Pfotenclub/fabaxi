import discord
from discord import SlashCommandGroup
from discord.ext import commands

from ext.valid import check_emoji, check_color


class ReactionRole(commands.Cog):
    reactionrolegroup = SlashCommandGroup("reaction_role")

    def __init__(self, bot):
        self.bot = bot

    @reactionrolegroup.command(name="get_emote_id")
    # @discord.option(name="emote", type=discord.Emoji, description="The emote you want to get the ID for")
    @discord.option(name="emote_str", type=discord.Emoji)
    async def get_emote_id(self, ctx, emote_str):
        try:
            uni_emoji = discord.PartialEmoji.from_str(emote_str).is_unicode_emoji()
            custom_emoji = discord.PartialEmoji.from_str(emote_str).is_custom_emoji()
            if uni_emoji:
                await ctx.respond("This is a unicode emoji, it does not have an ID.")
            if custom_emoji:
                await ctx.respond(f"This is a custom emoji. Emote ID {emote_str.id}.")
        except discord.InvalidArgument:
            return await ctx.respond("Invalid emote format. Please provide a valid emote.")

    @reactionrolegroup.command(name="add", description="Add a role color to the database")
    @discord.option(name="emote_id", type=discord.SlashCommandOptionType.integer,
                    description="The emote id you want to add")
    @discord.option(name="color_hex", type=discord.SlashCommandOptionType.string,
                    description="The color of the role in hex format (e.g. #FF5733)")
    @discord.option(name="role_id", type=discord.SlashCommandOptionType.role,
                    description="The role to add the color to")
    @commands.has_guild_permissions(administrator=True)
    async def add_role_to_database(self, ctx, emote: int, color: str, role: discord.Role):
        emoji_valid = await check_emoji(ctx.guild, emote)
        color_valid = await check_color(color)
        if not emoji_valid:
            return await ctx.respond("Invalid emote ID. Please provide a valid emote ID.", ephemeral=True)
        if not color_valid:
            return await ctx.respond("Invalid color format. Please provide a color in hex format (e.g. #FF5733).",
                                     ephemeral=True)



        await ctx.respond(f"Added role color {color} with emote {emote} for role {role}.")


def setup(bot):
    bot.add_cog(ReactionRole(bot))
