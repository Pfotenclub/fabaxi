from datetime import date, datetime, timedelta, time

import discord
from discord.ext import commands, tasks
from ext.system import default_embed

from db import Database
from db.economy import EconomyBackend
from db.birthdays import BirthdayBackend


class Stuff(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.check_birthdays.start()
        self.remove_birthday_role.start()

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        now = datetime.now()
        target_time = time(3, 0)
        target_datetime = datetime.combine(now.date(), target_time)

        if now > target_datetime:
            target_datetime += timedelta(days=1)

        await discord.utils.sleep_until(target_datetime)

        today = target_datetime.date()
        users_with_birthday = await BirthdayBackend().get_users_with_birthday(today.day, today.month)
        for user in users_with_birthday:
            guild: discord.Guild = self.bot.get_guild(user.guild_id)
            member = guild.get_member(user.user_id)
            if member:
                amaunzment = guild.get_channel_or_thread(1191397658514956308)
                birthday_role = guild.get_role(1342827586648150076)
                try:
                    if user.year == 1900:
                        await amaunzment.send(f"Happy Birthday, <@{member.id}>! :birthday: ")
                        await member.add_roles(birthday_role)
                    else:
                        await amaunzment.send(
                            f"Happy Birthday, <@{member.id}>! :birthday:\nYou're now {today.year - user.year} years old!")
                        await member.add_roles(birthday_role)
                except Exception as e:
                    print(e)

    @tasks.loop(hours=24)
    async def remove_birthday_role(self):
        now = datetime.now()
        target_time = time(0, 0)  # one hour offset because host is in a different timezone
        target_datetime = datetime.combine(now.date(), target_time)

        if now > target_datetime:
            target_datetime += timedelta(days=1)

        await discord.utils.sleep_until(target_datetime)
        bd_role_members = self.bot.get_guild(1056514064081231872).get_role(1342827586648150076).members
        for member in bd_role_members:
            await member.remove_roles(self.bot.get_guild(1056514064081231872).get_role(1342827586648150076))

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

    birthdayCommandGroup = discord.SlashCommandGroup(name="birthday", description="A selection of birthday commands.",
                                                     contexts={discord.InteractionContextType.guild})

    @birthdayCommandGroup.command(name="set", description="Set your birthday.",
                                  contexts={discord.InteractionContextType.guild})
    @discord.option(name="day", description="The day of your birthday as a number. (eg. 14)", type=discord.SlashCommandOptionType.integer,
                    required=True)
    @discord.option(name="month", description="The month of your birthday as a number. (eg. 5 for May)",
                    type=discord.SlashCommandOptionType.integer, required=True)
    @discord.option(name="year", description="The year of your birthday as a number. (eg. 2000)", type=discord.SlashCommandOptionType.integer,
                    required=False)
    async def setBirthday(self, ctx, day: int, month: int, year: int = 1900):
        birthday = None
        try:
            birthday = date(year, month, day)
        except ValueError:
            return await ctx.respond("Invalid date.", ephemeral=True)

        if birthday > date.today():
            return await ctx.respond("You can't set a birthday in the future.", ephemeral=True)
        try:
            if not await BirthdayBackend().get_user_record(ctx.author.id, ctx.guild.id):
                await BirthdayBackend().create_user_record(ctx.author.id, ctx.guild.id, birthday)
                await ctx.respond("Birthday set!")
            else:
                await BirthdayBackend().update_user_record(ctx.author.id, ctx.guild.id, birthday)
                await ctx.respond("Birthday updated!")
        except Exception as e:
            await ctx.respond("An error occurred. Please try again later.", ephemeral=True)
            print(e)

    @birthdayCommandGroup.command(name="delete", description="Delete your birthday.",
                                  contexts={discord.InteractionContextType.guild})
    async def deleteBirthday(self, ctx):
        try:
            await BirthdayBackend().delete_user_record(ctx.author.id, ctx.guild.id)
            await ctx.respond("Birthday deleted!")
        except Exception as e:
            await ctx.respond("An error occurred. Please try again later.", ephemeral=True)
            print(e)

    @birthdayCommandGroup.command(name="view", description="View your birthday.",
                                  contexts={discord.InteractionContextType.guild})
    @discord.option(name="user", description="The user whose birthday you want to view.",
                    type=discord.SlashCommandOptionType.user, required=False)
    async def viewBirthday(self, ctx: discord.InteractionContextType, user: discord.User = None):
        if user is None:
            user = ctx.author
        if user.bot: return await ctx.respond("Bots don't have birthdays.")
        embed: discord.Embed = await default_embed(user=user)
        embed.title = f"{user.display_name}'s Birthday"
        if user.avatar: embed.set_thumbnail(url=user.avatar.url)
        try:
            user_record = await BirthdayBackend().get_user_record(user.id, ctx.guild.id)

            if not user_record:  # Keine Daten gefunden
                embed.description = "No birthday set."
                pass
            elif user_record.year == 1900:
                birthday = date(user_record.year, user_record.month, user_record.day)
                embed.add_field(name=f"{user.display_name}'s Birthday", value=f"{birthday.day}. {birthday.strftime('%B')}")
            else:
                birthday = date(user_record.year, user_record.month, user_record.day)
                embed.add_field(name=f"{user.display_name}'s Birthday",
                                value=f"{birthday.day}. {birthday.strftime('%B')} {birthday.year}")
                age = date.today().year - birthday.year
                if (date.today().month, date.today().day) < (birthday.month, birthday.day): age -= 1
                embed.add_field(name="Age", value=f"{age} years")
        except Exception as e:
            embed.description = "An error occurred. Please try again later."
            print(e)
        if user.color != discord.Color.default(): embed.color = user.color
        else: embed.color = 0x1abc9c
        await ctx.respond(embed=embed)

    @birthdayCommandGroup.command(name="list", description="List all birthdays in the server.",
                                  contexts={discord.InteractionContextType.guild})
    async def listBirthdays(self, ctx):
        embed: discord.Embed = await default_embed(user=ctx.author)
        embed.title = "Birthdays in this server"

        try:
            birthdays = await BirthdayBackend().get_all_birthdays(ctx.guild.id)
            if not birthdays:
                embed.description = "No birthdays set in this server."
            else:
                for birthday in birthdays:
                    user = ctx.guild.get_member(birthday.user_id)
                    if user:
                        birthday_date = date(birthday.year, birthday.month, birthday.day)
                        if birthday.year == 1900:
                            embed.add_field(name=f"{user.display_name}'s Birthday",
                                            value=f"{birthday_date.day}. {birthday_date.strftime('%B')}", inline=False)
                        else:
                            embed.add_field(name=f"{user.display_name}'s Birthday",
                                            value=f"{birthday_date.day}. {birthday_date.strftime('%B')} {birthday_date.year}",
                                            inline=False)
        except Exception as e:
            embed.description = "An error occurred while fetching birthdays. Please try again later."
            print(e)
        await ctx.respond(embed=embed)

def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Stuff(bot))  # add the cog to the bot
