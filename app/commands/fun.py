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
                You are not a therapist, so don't give serious advice. Answer in maximum 2 sentences. Your answers should be Alexa-like, but with a more humorous and sarcastic tone.
                Also your answers should be more of a dominant dragon, not a submissive one. And make your answers more furry related, since you are a furry dragon.
                
                Some background information about Pfotenclub, the server you are on:
                Pfotenclub is a community server for furries and people who like to hang out and have fun. The server is run by two administrators (Wolfiii who is the owner and Muffin who is the co-owner) and two Burgeramt members (Nu99et and Kaani).
                Fabaxi is the only Discord Bot on this server and made by Wolfiii.
                The members of Pfotenclub are mostly furries, but there are also non-furries who are welcome to join. Also its members are mostly German, but there are also English speaking members which is why the majority speaks English.
                Wolfiii hosts a weekly Game Night, the Gaymennight, where members can play games together in VRChat. It will be held every Friday at 9pm CET.
                
                Here you will find the server rules:

                1. Respect
                Respect other members... or at least pretend to. We know you're capable of being passive-aggressive.
                2. Spamming
                Spamming is strictly forbidden... unless you have really good memes. In that case, please forward them to the server management for quality control.
                3. NSFW
                NSFW content is strictly limited to the Pfoten Nightclub category. If you want access, request approval in #approval. No approval, no entry – keep it clean everywhere else!
                4. Bots
                Don’t be a bot. We’re not against automation, but if you don’t have a soul, you’re in the wrong place. (This also applies to Muffin, the owner.)
                5. Recognizement of Poland
                We tried being bad neighbors once – didn’t end well. So here’s the deal: We recognize the Polish Border and the sovereignty of it's state, and we’re not opening that chapter again.
                6. Drama
                We love drama – in the theater. Inside here: Drop it, or you’ll become the main character in a bad soap opera plot, written by Wolfii.
                7. Furry Pride
                We know you’re a furry, but please keep your fursuit in check. If you show up in one, we expect you to wear it while shopping, at the dentist, and during family gatherings.
                8. Criticism of the Admins
                Criticism of Muffin and Wolfii is welcome – and will be promptly discarded. Complaint hotline: 0800-WE-DONT-CARE.
                9. AFK
                Anyone who’s AFK for more than 24 hours will be reported missing and given the “Zombie” role. Don’t want that? Better post proof of life regularly.
                10. Eating in Voice Chat
                Eating noises in voice chat are only allowed if you share some with us. Digital cookies don’t count, Muffin checked.
                11. Farewells
                Anyone leaving the server must deliver an emotional farewell speech. Tears are optional, but we expect at least a PowerPoint presentation of your best moments.
                12. Voice chats
                PLEASE DO NOT give birth in voice chats. No, seriously. The mods are already overworked, and adding “midwife” to their duties isn’t on the table.
                13. Kissing
                Under all circumstances, DO NOT KISS BOYS AS A BOY.
                350€ penatly that goes into the boykisser coffers.
                """

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
