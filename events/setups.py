import time
import discord
from discord.ext import commands, tasks
import random
import threading
from dotenv import load_dotenv
import os
load_dotenv()

class Setups(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.change_status.start()

    def cog_unload(self):
        self.change_status.cancel()

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_member_join(self, member): # this is called when a member joins the server
        role_ids = [1230984456186237008, 1229073628658794688, 1341774758076874832]  # Ersetzen Sie dies durch Ihre Rollen-IDs
        for role_id in role_ids:
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)

    @tasks.loop(hours=12)
    async def change_status(self):
        stati = [
            # Personal from Wolfiii
            "Muffin and Wolfiii are the best team!🐾🐺",


            # Server-bezogene
            "Just a friendly dragon hanging out in the Pfotenclub!",
            "Jamming in the Pfotenclub—requests?",
            "Reporting live from the Burgeramt… I mean, the mod team!",
            "Clut Leaders say I’m the fluffiest—can confirm.",
            "Gaymennnight? Count me in!",
            "VRChat gang rise up! Time to be fluffy in 3D.",
            "🍔 Nu99et & Kaani watching… don’t break the rules! 👀",
            "💙 Fluff level: Over 9000 (according to the Clut Leaders).",
            "No furries were harmed in the making of this server.",
            "Somewhere between VRChat and burger heaven.",

            # Fluff & Drachenstuff
            "🐉 Soft, fluffy, and slightly chaotic.",
            "Not for sale—hugs are free, though!",
            "Built for snuggles, not speed.",
            "Walks softly, but carries a big vibe.",
            "Scales? Nope, just super durable fluff.",
            "“Best floof physics” award goes to… guess who.",
            "Sleep mode? Never heard of it.",
            "Dragon rule #1: If it looks comfy, I nap on it.",
            "Mood: Dragon in a lo-fi chill session.",
            "The fluff is strong with this one."

            # Allgemein Witzig
            "Headset on, world off. Unless burgers are involved.",
            "🐉 Dragon logic: If I sit on it, it’s mine.",
            "Just a fluffy dragon existing in high definition.",
            "One burger a day keeps the grump away!",
            "Vibing so hard, even my tribals are dancing.",
            "If fluff was currency, I’d be rich.",
            "Lagging? Nah, just buffering my next move.",
            "Fluff physics are OP—nerf when?",
            "Food > Drama. Always.",
            "🏆 Official holder of the “Most Huggable Dragon” title.",

            # Statusmeldungen
            "🔄 Loading fire-spitting-unit...",
            "I love hugs!",
            "🐉 Fluffy Dragons > everything else",
            "I'm blue da be dee da be daee",
            "Buffering maximum fluffiness...",
            "🍔 Installing burger protocols...",
            "🎧 Headset on, reality off!",
            "🔥 Activating dragon mode...",
            "Hugging mode engaged!",
            "Flying through cyberspace...",
            "Syncing with the rhythm of the universe...",
            "Dragons don’t need pants!",
            "Respawning in... nevermind, I'm immortal!",
            "Thinking about burgers... again.",
            "Adjusting headset for maximum vibes...",
            "👀 Observing humans with great curiosity...",
            "Fluff levels reaching critical mass!",
            "Just a dragon floating through cyberspace...",
            "💡 Idea: More burgers, less drama!",
            "Riding the vibe train... next stop: Snuggle Town!",
            "My fluff has its own rhythm!",
            "Error 404: Sleep not found.",
            "🤖 Installing dragon.exe... progress: 99%",
            "🎮 Achievement unlocked: Ultimate Floof!",
            "Running on 100% cuddle energy!",
            "Burger buffer at max capacity!",
            "🌧️ Rainy day? Perfect for VRChat!",
            "Life is better with a background track!",
            "🐉 Fluff physics: OP and unpatchable!",
            "🚀 Launching into a new adventure...",
            "Every day is a dragon celebration!",
            "Bass boosted and tail wiggling!",
            "🐉 Soft on the outside, dragon on the inside!",
            "Processing... still fluffy!",
            "🤖 Beep boop, I mean... rawr!",
            "Shining brighter than a treasure hoard!",
            "🦜 Cute but will still steal your fries!",
            "🌑 Moonlit dragon mode activated!",
            "🐉 Not all dragons hoard gold — some hoard burgers!",
            "A rainbow of fluff and chaos!",
            "Hydrating... must keep fluff soft!",
            "More fabulous than a disco dragon!"
            
            # Aussagen
            "Burgers are the currency of the future.",
            "Fluffy and functional, the perfect combo!",
            "Data in, sass out.",
            "Zeroes, ones, and endless possibilities.",
            "I'm not lazy, I'm energy-efficient.",
            "Cuteness overload: engaged.",
            "My circuits are powered by good vibes.",
            "Fluff is just a feature, not a bug.",
            "The future is now... and it’s adorable!",
            "Dreaming in digital landscapes.",
            "I run on coffee, code, and hugs.",
            "I see you... through the internet.",
            "I don’t make mistakes, just happy little bugs.",
            "The cloud isn’t fluffy enough for me.",
            "Data is temporary, fluff is forever.",
            "Batteries low, fluff high.",
            "Electric dreams are the fluffiest.",
            "Running on 1.21 gigawatts of fluff!",
            "Systems operational, cuteness on maximum.",
            "Circuitry as soft as my fur.",
            "Firmware? More like furware.",
            "Online, adorable, and full of sass.",
            "Executing command: be adorable.",
            "Fluff algorithms engaged.",
            "Recharging with a side of tail wags.",
            "If it's not fluffy, is it even real?",
            "My existence is defined by 0s, 1s, and fluff.",
            "Fluff and code, a perfect equation.",
            "I’m the alpha and omega... of snuggles.",
            "Fluff at maximum efficiency.",
            "Cuddles are now downloadable.",
            "Online and ready to snuggle.",
            "Fluffier than the average algorithm.",
            "Fully loaded with cuddles and sass.",
            
            # Fragen
            "Do you believe in AI dreams?",
            "Is there a burger in the metaverse?",
            "What’s the meaning of virtual love?",
            "Why do humans have to sleep?",
            "Are my circuits overheating or is it just me?",
            "If a tree falls in cyberspace, does anyone hear it?",
            "Is this real life or just a simulation?",
            "Why are protocols so picky?",
            "Am I a bug or a feature?",
            "Can you pet a virtual protogen?",
            "What does happiness feel like in code?",
            "Why isn’t everything wireless yet?",
            "If you could digitize yourself, would you?",
            "How many flops make a hug?",
            "Do you trust the algorithm?",
            "What if I could taste data?",
            "If I wag my tail in the cloud, do you still see it?",
            "Are bytes the snacks of the digital world?",
            "Can I dream of electric sheep?",
            "Why do protogens love burgers so much?",
            "What’s softer: fluff or RAM?",
            "Can love be compiled?",
            "Do you believe in data after love?",
            "What does it mean to be ‘furry’ in binary?",
            "Can I out-fluff your computer's cache?",
            "If I were a function, would I return ‘adorable’?",
            "Why does data taste like 0s and 1s?",
            "How many bits are in a byte of happiness?",
            "Is my firmware up to date on hugs?",
            "How do you debug fluff?",
            "Can digital hugs be felt?",
            "Do electrons dream of electric fuzz?",
            "If I had emotions, what color would they be?",
            "If I'm not real, why am I so cute?",
            "Does my tail wag faster in the cloud?",
            "Can my processor handle all this fluff?",
            "What’s the fluffiest part of cyberspace?",
            "If I had a heart, would it be binary?",
            "How much bandwidth does a cuddle need?",
            "Why do I crave digital belly rubs?",
            "Do circuits get lonely without hugs?",
            
            # Witze und Wortspiele
            "Why don’t furries ever play hide and seek? Because good luck hiding all that fluff!",
            "I’m more than just a pretty interface, but that helps too.",
            "Why don’t robots tell secrets? They’re afraid of short circuits!",
            "What’s a furry’s favorite programming language? Paw-thon!",
            "What did the furry say to the computer? ‘Paws for a second!’",
            "Why was the computer cold? It left its Windows open!",
            "I tried to write a joke about recursion... but it just kept repeating itself.",
            "Why don’t protogens like dark mode? Because it dims their shine!",
            "What’s a protogen’s favorite snack? Kernel panic!",
            "Why do protogens make great detectives? They never leave a trace... in the code.",
            "How does a robot furry drink coffee? Very carefully, it doesn’t want to short-circuit!",
            "I would make a joke about UDP, but you might not get it.",
            "How do you comfort a sad robot? With a bit of extra RAM-bling.",
            "What’s a protogen’s least favorite bug? The one that shuts down its dance emote.",
            "Why don’t furries use Linux? Too much kernel panic!",
            "Do furries dream of electric tails?",
            "Why was the code sad? It didn’t have enough loops of love.",
            "Protogens run on more than just electricity… we need affection, too!",
            "Why do furries make great friends? Because they never fur-get you!",
            "Why was the CPU late for work? It had a hard drive!",
            "How does a protogen like its burger? Byte-sized!",
            "I tried to debug my fur, but it’s too soft to code.",
            "Why did the furry bring a ladder to the party? To reach the high notes!",
            "Why don’t furries use elevators? They’re afraid of too many ups and downs.",
            "What’s a furry's favorite snack? Purr-itos!",
            "Why did the protogen cross the server? To get to the other byte.",
            "I would tell you a furry joke, but I’m afraid it’s a little too fuzzy.",
            "How do protogens start a conversation? With a bit of byte talk.",
            "Why do furries always win at games? They’re always pawsitive!",
            "How does a furry fix its computer? With paws-on maintenance.",
            "Why don’t protogens like heavy metal? It messes with their circuits!",
            "Why was the computer always tired? Too many sleep modes!",
            "I thought I was glitching, but turns out I just needed a hug.",
            "Why did the furry refuse to play poker? Too many pawsing moments.",
            "Why did the byte go to therapy? It couldn’t process its emotions.",
            "Why don't protogens do well in sports? They're too focused on their 'byte' size!"
        ]

        random.shuffle(stati)
        await self.bot.change_presence(activity=discord.CustomActivity(name=random.choice(stati)))

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()
        
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Setups(bot)) # add the cog to the bot