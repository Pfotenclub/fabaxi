import discord
from discord.ext import commands
import os
import json
from ext.system import is_owner

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
data_path = None
if environment == "DEV": data_path = "./data"
elif environment == "PROD": data_path = "/db"

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="role-colors")
    @is_owner()
    async def roleColors(self, ctx: commands.context):
        roleJson = None
        with open(os.path.join(data_path, "rolecolors.json"), "r", encoding='utf-8') as file: roleJson = json.load(file)
        roleMsgId = roleJson["roleMsgId"]
        rolecolors = roleJson["rolecolors"]
        embedText = ""
        for role in rolecolors:
            if int(role) == 0: continue
            embedText += f"{rolecolors[role]} - <@&{int(role)}>\n"
        embed = discord.Embed(title="Role colors", description=embedText)
        embed.color = 0x1abc9c
        embed.set_footer(text=f"To remove your color, react with ❌")
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=Qw82NJLhJoqc&format=png&color=000000")
        msg = await ctx.send(content="React to change your role color!", embed=embed)
        for role in rolecolors:
            await msg.add_reaction(rolecolors[role])
        
        with open(os.path.join(data_path, "rolecolors.json"), "r+", encoding='utf-8') as file:
            data = json.load(file)
            data["roleMsgId"] = msg.id
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()

        await ctx.message.delete()
    
    @commands.command(name="rules")
    @is_owner()
    async def rules(self, ctx: commands.context):
        picture_embed = discord.Embed()
        file = discord.File(fp="./ext/images/rules.png", filename="rules.png")
        picture_embed.set_image(url="attachment://rules.png")
        picture_embed.color = 0x1abc9c

        rules_embed = discord.Embed(title="Official Pfotenclub rules", description="Under the loving dictatorship of Muffin and Wolfiii")
        rules_embed.color = 0x1abc9c
        rules_embed.add_field(name="1. Respect", value="Respect other members... or at least pretend to. We know you're capable of being passive-aggressive.", inline=False)
        rules_embed.add_field(name="2. Spamming", value="Spamming is strictly forbidden... unless you have really good memes. In that case, please forward them to the server management for quality control.", inline=False)
        rules_embed.add_field(name="3. NSFW", value="NSFW content is strictly limited to the Pfoten Nightclub category. If you want access, request approval in #approval. No approval, no entry – keep it clean everywhere else!", inline=False)
        rules_embed.add_field(name="4. Bots", value="Don’t be a bot. We’re not against automation, but if you don’t have a soul, you’re in the wrong place. (This also applies to Muffin.)", inline=False)
        rules_embed.add_field(name="5. Recognizement of Poland", value="We tried being bad neighbors once – didn’t end well. So here’s the deal: We recognize the Polish Border and the sovereignty of it's state, and we’re not opening that chapter again.", inline=False)
        rules_embed.add_field(name="6. Have fun!", value="This is the most important rule. If you’re not having fun, you’re doing it wrong. Unless you’re a cat – then just nap.", inline=False)
        rules_embed.add_field(name="7. Furry Pride", value="We know you’re a furry, but please keep your fursuit in check. If you show up in one, we expect you to wear it while shopping, at the dentist, and during family gatherings.", inline=False)
        rules_embed.add_field(name="8. Criticism of the Admins", value="Criticism of Muffin and Wolfiii is welcome – and will be promptly discarded. Complaint hotline: 0800-WE-DONT-CARE.", inline=False)
        rules_embed.add_field(name="9. AFK", value="Anyone who’s AFK for more than 24 hours will be reported missing and given the “Zombie” role. Don’t want that? Better post proof of life regularly.", inline=False)
        rules_embed.add_field(name="10. Eating in Voice Chat", value="Eating noises in voice chat are only allowed if you share some with us. Digital cookies don’t count, Muffin checked.", inline=False)
        rules_embed.add_field(name="11. Farewells", value="Anyone leaving the server must deliver an emotional farewell speech. Tears are optional, but we expect at least a PowerPoint presentation of your best moments.", inline=False)
        rules_embed.add_field(name="12. Birth", value="PLEASE DO NOT give birth. No, seriously. The burgeramt is already overworked, and adding “midwife” to their duties isn’t on the table.", inline=False)
        rules_embed.add_field(name="13. Kissing", value="Under all circumstances, DO NOT KISS BOYS AS A BOY.\n350€ penatly that goes into the boykisser coffers.", inline=False)

        await ctx.send("Hey and Welcome to Pfotenclub! Your new home rom now on :3\n\nBefore you can start socializing (eek-, thats that >->?), here are the rules of this server.")
        await ctx.send(file=file, embed=picture_embed)
        await ctx.send(embed=rules_embed)
        await ctx.message.delete()

    @discord.Cog.listener("on_raw_reaction_add")
    async def chooseRoleColor(self, payload):
        if payload.member.bot: return

        roleJson = None
        with open(os.path.join(data_path, "rolecolors.json"), "r", encoding='utf-8') as file: roleJson = json.load(file)
        roleMsgId = roleJson["roleMsgId"]
        if payload.message_id != roleMsgId: return # the message id of the role color message in #chat-color
        rolecolors = roleJson["rolecolors"]
        if str(payload.emoji) == "❌":
            for role in rolecolors:
                if payload.member.guild.get_role(int(role)) in payload.member.roles:
                    await payload.member.remove_roles(payload.member.guild.get_role(int(role)))
            msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            await payload.member.send("Removed your role color")
            return

        for role in rolecolors:
            if payload.member.guild.get_role(int(role)) in payload.member.roles:
                await payload.member.remove_roles(payload.member.guild.get_role(int(role)))
        await payload.member.add_roles(payload.member.guild.get_role(int(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))])), reason="Role color")
        msg = self.bot.get_channel(payload.channel_id).get_partial_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await payload.member.send(f"Changed your role color to {payload.member.guild.get_role(int(list(rolecolors.keys())[list(rolecolors.values()).index(str(payload.emoji))])).name}")        

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(AdminCommands(bot)) # add the cog to the bot