import asyncio
from datetime import datetime
import errno
import json
import logging
import os
import shutil

import discord
from discord.ext import commands
from dotenv import load_dotenv

from app.core.config import BAN_REPORT_CHANNEL_ID, DATA_DIR, OWNER_IDS, RULES_IMAGE_PATH, MEDIA_EXTENSIONS
from ext.system import default_embed, is_owner

logger = logging.getLogger(__name__)


def get_clean_filepath(target_dir: str, msg_id: int, att_id: int, filename: str) -> str:
    """Generates a safe and unique filepath for an attachment."""
    base = os.path.basename(filename)
    name, ext = os.path.splitext(base)
    ext = ext.lower()
    clean_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip()
    if not clean_name:
        clean_name = f"attachment_{att_id}"
    clean_filename = f"{msg_id}_{att_id}_{clean_name}{ext}"
    return os.path.join(target_dir, clean_filename)


async def save_attachment_with_retry(att: discord.Attachment, filepath: str, max_retries: int = 3) -> bool:
    """Saves a discord attachment atomically with retries on rate limits (429) or transient HTTP/network errors."""
    target_dir = os.path.dirname(filepath)
    # Check disk space (require at least 100MB free)
    try:
        if shutil.disk_usage(target_dir).free < 100 * 1024 * 1024:
            raise OSError(errno.ENOSPC, "Less than 100MB disk space remaining")
    except OSError as e:
        if e.errno == errno.ENOSPC:
            raise

    temp_filepath = f"{filepath}.{os.getpid()}.tmp"

    for attempt in range(1, max_retries + 1):
        try:
            await att.save(temp_filepath)
            os.replace(temp_filepath, filepath)
            return True
        except discord.NotFound:
            # File was deleted on Discord CDN; try proxy_url cache as fallback
            try:
                await att.save(temp_filepath, use_cached=True)
                os.replace(temp_filepath, filepath)
                return True
            except Exception:
                logger.warning(f"Attachment {att.id} ({att.filename}) was deleted on Discord.")
                return False
        except discord.HTTPException as http_err:
            if http_err.status == 429:
                wait_time = attempt * 2
                logger.warning(f"Rate limited (429) downloading {att.filename}. Retrying in {wait_time}s (attempt {attempt}/{max_retries})...")
                await asyncio.sleep(wait_time)
            elif attempt < max_retries:
                await asyncio.sleep(1)
            else:
                logger.error(f"HTTP error {http_err.status} saving {att.filename}: {http_err}")
                return False
        except (asyncio.TimeoutError, ConnectionError, OSError) as conn_err:
            if isinstance(conn_err, OSError) and conn_err.errno == errno.ENOSPC:
                raise conn_err
            if attempt < max_retries:
                await asyncio.sleep(attempt)
            else:
                logger.error(f"Network error saving {att.filename}: {conn_err}")
                return False
        except Exception as err:
            logger.error(f"Unexpected error saving {att.filename}: {err}")
            return False
        finally:
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass
    return False


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(
        name="archive-media",
        description="Archives all media in this channel",
        default_member_permissions=discord.Permissions(administrator=True),
    )
    @discord.option(
        name="limit",
        description="Max messages to scan (leave empty for all messages)",
        input_type=int,
        required=False,
        default=None,
    )
    @discord.option(
        name="include_threads",
        description="Also archive media from threads in this channel",
        input_type=bool,
        required=False,
        default=False,
    )
    async def archiveMedia(
        self,
        ctx: discord.ApplicationContext,
        limit: int = None,
        include_threads: bool = False,
    ):
        channel = ctx.channel
        is_forum = isinstance(channel, discord.ForumChannel)

        if not is_forum and not hasattr(channel, "history"):
            await ctx.respond("This channel does not support message history.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        if limit is not None and limit <= 0:
            limit = None

        target_dir = os.path.join(DATA_DIR, "media_archive", str(channel.id))
        os.makedirs(target_dir, exist_ok=True)

        channels_to_scan = []
        if not is_forum and hasattr(channel, "history"):
            channels_to_scan.append((channel, "main channel"))

        if include_threads or is_forum:
            # Active cached threads
            if hasattr(channel, "threads"):
                for th in channel.threads:
                    channels_to_scan.append((th, f"thread '{th.name}'"))
            # Archived threads
            if hasattr(channel, "archived_threads"):
                try:
                    async for th in channel.archived_threads(limit=None):
                        channels_to_scan.append((th, f"archived thread '{th.name}'"))
                except discord.Forbidden:
                    logger.warning(f"No permission to read archived threads in channel {channel.id}")
                except Exception as err:
                    logger.warning(f"Error fetching archived threads in channel {channel.id}: {err}")

        count = 0
        skipped = 0
        errors = 0
        last_progress_time = asyncio.get_event_loop().time()

        try:
            for target, target_desc in channels_to_scan:
                try:
                    async for msg in target.history(limit=limit):
                        for att in msg.attachments:
                            if att.filename.lower().endswith(MEDIA_EXTENSIONS):
                                filepath = get_clean_filepath(target_dir, msg.id, att.id, att.filename)

                                if not os.path.exists(filepath):
                                    success = await save_attachment_with_retry(att, filepath)
                                    if success:
                                        count += 1
                                    else:
                                        errors += 1
                                else:
                                    skipped += 1

                                now = asyncio.get_event_loop().time()
                                if now - last_progress_time >= 5:
                                    try:
                                        await ctx.interaction.edit_original_response(
                                            content=f"⏳ Archiving in progress ({target_desc})...\n"
                                                    f"• **{count}** downloaded\n"
                                                    f"• **{skipped}** skipped (already archived)\n"
                                                    f"• **{errors}** failed"
                                        )
                                        last_progress_time = now
                                    except Exception:
                                        pass
                except discord.Forbidden:
                    logger.warning(f"Missing permissions to read history in {target_desc} ({target.id})")
                    errors += 1

            summary = (
                f"✅ **Archive completed!**\n"
                f"• **{count}** new attachments downloaded\n"
                f"• **{skipped}** existing attachments skipped\n"
                f"• Target directory: `{target_dir}`"
            )
            if errors > 0:
                summary += f"\n⚠️ **{errors}** attachments or threads could not be accessed."

            try:
                await ctx.interaction.edit_original_response(content=summary)
            except discord.NotFound:
                logger.warning("Interaction token expired. Sending DM to user.")
                try:
                    await ctx.author.send(f"✅ Media archive for <#{channel.id}> finished:\n{summary}")
                except Exception as dm_err:
                    logger.error(f"Failed to send completion DM: {dm_err}")
        except OSError as os_err:
            if os_err.errno == errno.ENOSPC:
                err_msg = f"❌ **Archive aborted: Disk space is full!**\nSaved **{count}** files before running out of space."
                logger.critical(f"Disk full during archive in channel {channel.id}!")
                try:
                    await ctx.interaction.edit_original_response(content=err_msg)
                except Exception:
                    try:
                        await ctx.author.send(err_msg)
                    except Exception:
                        pass
            else:
                logger.error(f"OS error during archiving: {os_err}")
                try:
                    await ctx.followup.send(f"❌ OS Error: {os_err}", ephemeral=True)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error during media archiving in channel {channel.id}: {e}")
            try:
                await ctx.followup.send(f"❌ An error occurred during archiving: {e}", ephemeral=True)
            except Exception:
                pass

    @commands.slash_command(name="ban", description="Ban a member (Only Burgeramt!)")
    @discord.option(
        name="member",
        description="Member you want to ban",
        contexts={discord.SlashCommandOptionType.user},
        required=True,
    )
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member):
        if not ctx.user.guild_permissions.ban_members:
            await ctx.respond(
                "You don't have the permission to ban others! Please reach out to the Burgeramt.",
                ephemeral=True,
            )
            return
        await ctx.response.send_modal(BanModal(member))

    @commands.command(name="role-colors")
    @is_owner()
    async def roleColors(self, ctx: commands.Context):
        role_file = os.path.join(DATA_DIR, "rolecolors.json")
        if not os.path.exists(role_file):
            return await ctx.send(f"Error: `{role_file}` does not exist.")

        with open(role_file, "r", encoding="utf-8") as file:
            roleJson = json.load(file)

        rolecolors = roleJson["rolecolors"]
        embedText = ""
        for role in rolecolors:
            if int(role) == 0:
                continue
            embedText += f"{rolecolors[role]} - <@&{int(role)}>\n"
        embed = discord.Embed(title="Role colors", description=embedText)
        embed.color = 0x1abc9c
        embed.set_footer(text="To remove your color, react with ❌")
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=Qw82NJLhJoqc&format=png&color=000000")
        msg = await ctx.send(content="React to change your role color!", embed=embed)
        for role in rolecolors:
            await msg.add_reaction(rolecolors[role])

        with open(role_file, "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["roleMsgId"] = msg.id
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()

        await ctx.message.delete()

    @commands.command(name="rules")
    @is_owner()
    async def rules(self, ctx: commands.Context):
        picture_embed = discord.Embed()
        file = discord.File(fp=str(RULES_IMAGE_PATH), filename="rules.png")
        picture_embed.set_image(url="attachment://rules.png")
        picture_embed.color = 0x1abc9c

        rules_embed = discord.Embed(
            title="Official Pfotenclub rules",
            description="Under the loving dictatorship of Muffin and Wolfiii",
        )
        rules_embed.color = 0x1abc9c
        rules_embed.add_field(
            name="1. Respect",
            value="Respect other members... or at least pretend to. We want to keep drama to a minimum, so please make an effort to be polite and considerate.",
            inline=False,
        )
        rules_embed.add_field(
            name="2. Spamming",
            value="Spamming is strictly forbidden... unless you have really good memes. In that case, please forward them to the server management for quality control.",
            inline=False,
        )
        rules_embed.add_field(
            name="3. NSFW",
            value="NSFW content is strictly limited to the Pfoten Nightclub category. If you want access, request approval in <#1310668407871508530>. No approval, no entry – keep it clean everywhere else!",
            inline=False,
        )
        rules_embed.add_field(
            name="4. Bots",
            value="Don’t be a bot. We’re not against automation, but if you don’t have a soul, you’re in the wrong place. (This also applies to Muffin.)",
            inline=False,
        )
        rules_embed.add_field(
            name="5. Recognizement of Poland",
            value="We tried being bad neighbors once – didn’t end well. So here’s the deal: We recognize the Polish Border and the sovereignty of it's state, and we’re not opening that chapter again.",
            inline=False,
        )
        rules_embed.add_field(
            name="6. Furry Pride",
            value="This Server consists of Furrys (NO WAY! WAHT!?), so expect a lot of fur here :3 If you have smth against furrys, then why the heck are you even here?",
            inline=False,
        )
        rules_embed.add_field(
            name="7. Criticism of the Admins",
            value="Criticism of Muffin and Wolfiii is welcome – and will be promptly discarded. Complaint hotline: 0800-WE-DONT-CARE.",
            inline=False,
        )
        rules_embed.add_field(
            name="8. Activity",
            value="We are a 'bit too big friend group', so please try to be active and engage with the community. Everything on here works on a baseline of trust.",
            inline=False,
        )
        rules_embed.add_field(
            name="9. Farewells",
            value="Anyone leaving the server must deliver an emotional farewell speech. Tears are optional, but we expect at least a PowerPoint presentation of your best moments. (licence not sponsored)",
            inline=False,
        )
        rules_embed.add_field(
            name="10. Birth",
            value="PLEASE DO NOT give birth. No, seriously. The burgeramt is already overworked, and adding “midwife” to their duties isn’t on the table.",
            inline=False,
        )
        rules_embed.add_field(
            name="11. Kissing",
            value="Under all circumstances, DO NOT KISS BOYS AS A BOY.\n350€ penatly that goes into the boykisser coffers.",
            inline=False,
        )
        rules_embed.add_field(
            name="12. Have fun!",
            value="This is the most important rule. If you’re not having fun, you’re doing it wrong.",
            inline=False,
        )

        await ctx.send(
            "Hey and Welcome to Pfotenclub! Your new cult from now on :3\n\nBefore you can start socializing (eek-, whats that >->?), here are the rules of this server.\n"
            "Please read them carefully and follow them, so we can all have a good time together! If you have any questions, feel free to ask the admins or moderators. Enjoy your stay! :3"
            "\n\n**P.S.** If you want to get access to the NSFW channels, please request approval in <#1310668407871508530> and wait for an admin to approve you. Thanks!"
            "\n**P.P.S.** If you want to change your role color, react to the message in <#1341782920972603453> with the color you want! If you want to remove your role color, react with ❌"
            "\n**P.P.P.S.** Even though the rules are written in a humorous way, we take them seriously. Please follow them to ensure a fun and respectful environment for everyone. Thanks for being part of the Pfotenclub community! ^w^"
        )
        await ctx.send(file=file, embed=picture_embed)
        await ctx.send(embed=rules_embed)
        await ctx.message.delete()

    @discord.Cog.listener("on_raw_reaction_add")
    async def chooseRoleColor(self, payload):
        if payload.member.bot:
            return

        role_file = os.path.join(DATA_DIR, "rolecolors.json")
        if not os.path.exists(role_file):
            return

        with open(role_file, "r", encoding="utf-8") as file:
            roleJson = json.load(file)
        roleMsgId = roleJson.get("roleMsgId")
        if payload.message_id != roleMsgId:
            return
        rolecolors = roleJson.get("rolecolors", {})
        if str(payload.emoji) == "❌":
            for role in rolecolors:
                role_obj = payload.member.guild.get_role(int(role))
                if role_obj and role_obj in payload.member.roles:
                    await payload.member.remove_roles(role_obj)
            channel = self.bot.get_channel(payload.channel_id)
            if channel:
                msg = channel.get_partial_message(payload.message_id)
                await msg.remove_reaction(payload.emoji, payload.member)
            await payload.member.send("Removed your role color")
            return

        for role in rolecolors:
            role_obj = payload.member.guild.get_role(int(role))
            if role_obj and role_obj in payload.member.roles:
                await payload.member.remove_roles(role_obj)

        if str(payload.emoji) in rolecolors.values():
            role_id = int(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))])
            target_role = payload.member.guild.get_role(role_id)
            if target_role:
                await payload.member.add_roles(target_role, reason="Role color")
                await payload.member.send(f"Changed your role color to {target_role.name}")
        channel = self.bot.get_channel(payload.channel_id)
        if channel:
            msg = channel.get_partial_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)


class BanModal(discord.ui.Modal):
    def __init__(self, member: discord.Member, *args, **kwargs):
        super().__init__(title="Ban Member", *args, **kwargs)
        self.member = member
        self.add_item(
            discord.ui.InputText(
                label="Reason",
                placeholder="Please provide a reason for the ban.",
                style=discord.InputTextStyle.paragraph,
                max_length=4000,
                required=True,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        reason = self.children[0].value
        await self.member.ban(
            reason=f"Banned by {interaction.user.name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {reason}"
        )
        await interaction.response.send_message(
            f"You have successfully banned {self.member.mention} for the following reason: {reason}",
            ephemeral=True,
        )

        embed = await default_embed(fact=False)
        embed.title = "Member Banned"
        embed.description = f"{self.member.name} has been banned by {interaction.user.name}."
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Ban executed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        target_channel = self.member.guild.get_channel(BAN_REPORT_CHANNEL_ID)
        if target_channel:
            owner_mentions = " ".join(f"<@{uid}>" for uid in OWNER_IDS)
            await target_channel.send(
                content=f"{owner_mentions} Please review the ban details and fill out the form: https://cloud.pfotenclub.eu/f/4131",
                embed=embed,
            )


def setup(bot):
    bot.add_cog(Admin(bot))
