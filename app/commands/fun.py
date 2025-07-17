import discord
from discord.ext import commands
import os
import random
from ext.system import default_embed
from openai import OpenAI

class Fun(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    @discord.slash_command(name="8ball", description="Let 8ball foresee your future! Ask him yes or no questions.", contexts={discord.InteractionContextType.guild})
    async def eightBall(self, ctx, question: str):
        responses = [
            "Yes",
            "Yes",
            "Awoo (Yes)",
            "Awoo (Yes)",
            "No",
            "No",
            "Awoo (No)",
            "I don't know, ask me later",
            "Maybe",
            "Maybe",
        ]

        funnyResponses = [
            "No, you're a loser",
            "Yes, you're a winner",
            "HELL NAH",
            "HELL YEAH",
            "Ehm, what the hell are you asking me?",
            "What the hell is wrong with you?",
            "If you ask me that question one more time, I'm going to slap you (You won't like it :eyes:)",
            "I'm not going to answer that question",
            "Penis",
            "For legally reasons I am not allowed to answer that question",
            "It's my day off. Fuck you.",
            "Ask again later, I'm busy",
            "I'm just a silly fluffy dragon, not a fortune teller >:(",
            "Why do you care?",
            "I'm not sure, try flipping a coin",
            "You don't want to know",
            "42",
            "69",
            "That's a secret",
            "I can't predict now",
            "Ask someone else",
            "I'm too tired to answer that",
            "Why are you asking me?",
            "I have no idea",
            "Absolutely not",
            "Absolutely yes",
            "You wish",
            "In your dreams",
            "Not in a million years",
            "Sure, why not",
            "Definitely",
            "No way",
            "Ask your mom",
            "Ask your dad",
            "Ask your dog",
            "Ask your cat",
            "Ask your imaginary friend",
            "I'm not sure, try again",
            "I can't tell you that",
            "That's classified",
            "I'd do it, but I am not exactly sane",
            "Yeah. Probably illegal, but yeah",
            "Ask me again when you're sober",
            "I'm not sure, but I think you're a loser",
            "Theoretically, yes. Practically, no",
            "Bro, I'm not a magic 8ball",
            "Ask someone who cares",
            "Ask someone else, I'm not you're therapist",
            "Let's just say... depends on how desperate you are",
            "Nope, but go ahead and try, I could use a laugh",
            "I mean... technically yes. Ethically? no",
            "Yup. Might ruin your life, but go ahead",
            "Absolutely. Just sign this totally not suspicious contract first",
            "It's a strong maybe. Which means no, but I'm too polite to say it",
            "Hard to say... and I don't care enough to find out",
            "No, but watching you struggle will be entertaining",
            "You want some furry pizza?"
        ]
        if random.randint(1, 100) <= 10:
            response = random.choice(funnyResponses)
        else:
            response = random.choice(responses)
        embed: discord.Embed = await default_embed(ctx.author)
        embed.title = "Magic 8ball"
        embed.set_thumbnail(url="https://cdn.pixabay.com/photo/2015/09/05/07/17/pool-ball-923833_960_720.png")
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="hug", description="Hug someone!", contexts={discord.InteractionContextType.guild})
    @discord.option("user", description="User you want to hug", type=discord.SlashCommandOptionType.user, required=True)
    async def hug(self, ctx: discord.ApplicationContext, user: discord.User):
        if ctx.author.id == user.id: return await ctx.respond(f"{ctx.author.mention} hugs themselves. Aww, don't worry, you're not alone! :people_hugging:")
        if random.randint(1, 100) <= 10: return await ctx.respond(f"{ctx.author.mention} tried to hug {user.mention}, but they got rejected! Ouch! :cry:")
        elif random.randint(1, 100) <= 10: return await ctx.respond(f"{ctx.author.mention} hugged {user.mention} to death! :skull:")
        else: return await ctx.respond(f"{ctx.author.mention} hugs {user.mention}! :hugging:")
    
    @discord.slash_command(name="pat", description="Pat someone!", contexts={discord.InteractionContextType.guild})
    @discord.option("user", description="User you want to pat", type=discord.SlashCommandOptionType.user, required=True)
    async def pat(self, ctx: discord.ApplicationContext, user: discord.User):
        if ctx.author.id == user.id: return await ctx.respond(f"{ctx.author.mention} pats themselves. Aww, don't worry, you're not alone! :people_hugging:")
        if random.randint(1, 100) <= 10: return await ctx.respond(f"{ctx.author.mention} tried to pat {user.mention}, but they got rejected! Ouch! :cry:")
        elif random.randint(1, 100) <= 10: return await ctx.respond(f"{ctx.author.mention} patted {user.mention} to death! :skull:")
        else: return await ctx.respond(f"{ctx.author.mention} pats {user.mention}!")

    @discord.Cog.listener('on_message')
    async def fabaxi_alexa(self, message: discord.Message):
        if message.author.bot: return

        content = message.content.lower()
        if not content.startswith("fabaxi,"): return

        query = content[7:].strip().rstrip('?!.,')
        if not query: return

        async with message.channel.typing():
            try:
                aiclient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                system_prompt = """You are Fabaxi, a sarcastic and funny dragon who loves to joke around. You are not a serious AI, so don't take anything too seriously.
                You are here to entertain and make people laugh. You can answer questions, but you will always do it in a funny and sarcastic way.
                You are not a therapist, so don't give serious advice. Answer in maximum 2 sentences."""

                user_prompt = f"User: {message.author.name}, Question: {query}"

                
                
                response = aiclient.responses.create(
                    model="gpt-3.5-turbo",
                    instructions=system_prompt,
                    input=user_prompt
                )

                await message.reply(response.output_text)

            except Exception as e:
                fallback_responses = [
                "I don't know, I'm just a dragon",
                "Error 404: Fabaxi not found",
                "I'm not sure, but I think you're a loser",
                "I don't have an answer for that, but I can tell you a joke",
                ]

                await message.reply(random.choice(fallback_responses) + f" (Error: {str(e)})")


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Fun(bot)) # add the cog to the bot
