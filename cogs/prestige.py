# import.standard
import os
from random import choice, randrange

# import.thirdparty
from discord import slash_command
from discord.ext import commands

# variables.id
guild_ids = [int(os.getenv('SERVER_ID', 123))]

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))

class Prestige(commands.Cog, command_attrs=dict(hidden=True)):
    """ Category for prestige commands. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @slash_command(name="dnk", guild_ids=guild_ids)
    async def _dnk(self, ctx) -> None:
        """ Tells you something about DNK. """

        await ctx.respond(f"**`Sapristi ! C'est qui ? Oui, c'est lui le plus grave et inouï keum qu'on n'a jamais ouï-dire, tandis qu'on était si abasourdi et épris de lui d'être ici affranchi lorsqu'il a pris son joli gui qui ne nie ni être suivi par une souris sur son nid ni être mis ici un beau lundi !`**")

    @slash_command(name="gabriel", guild_ids=guild_ids)
    async def _gabriel_slash(self, ctx) -> None:
        """ Tells you something about Gabriel. """

        await ctx.respond(f"**<@366628959657394186>? Il est frais et il est chaud, et quand il rap c'est que du feu**")

    @commands.command(name="gabriel", aliases=["gab", "gabi", "gbrl", "gaburierudesu", "camisa9", "atacante", "rapper"])
    async def _gabriel_command(self, ctx) -> None:
        """ Tells you something about Gabriel. """

        await ctx.send(f"**<@366628959657394186>, desculpa por interromper o seu andamento, é que eu te vi passando, você é artista?**")

        await ctx.message.delete()
    @commands.command(aliases=["lexi", "lèqçi", "lexis"])
    async def alexis(self, ctx) -> None:
        """ A command for telling something about Alexis. """

        await ctx.message.delete()

        sentences = [
            "**I have a really nice voice**",
            "**Best sister-in-law ever**",
            "**z!bj 50**",
            "**z!bj 5000**",
            "**I see where you're coming from**",
        ]

        await ctx.send(choice(sentences))

    @commands.command()
    async def freak(self, ctx) -> None:
        """ A command for telling something about Marceline. """

        await ctx.message.delete()
        await ctx.send("You mean missy aka Marceline")

    @commands.command()
    async def hiba(self, ctx) -> None:
        """ A command for telling something about Hiba. """

        await ctx.message.delete()
        
        sentences = [
            "<@760178072904531988> Give me attention",
            "<@760178072904531988>\nAll of these girl on some uppercase shi\nThat means they all cap\nBeing the best at whatever i do\nThat’s sounding on brand",
            "<@760178072904531988> Morning 🤨",
            "<@760178072904531988> Kant hear you",
            "<@760178072904531988> Can you move me?",
            "<@760178072904531988>\nYou wouldnt put it\nSo no point ~",
            "<@760178072904531988>\nGab\nI have a problem",
            "<@760178072904531988> mysqli_query($cnx,$req1)",
            "<@760178072904531988> Caught you there ✨",
            "<@760178072904531988> I’m restarted",
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["not_lime", "lemonade", "citric", "yellow_fruit"])
    async def lemon(self, ctx) -> None:
        """ A command for telling something about Wyncham. """
        await ctx.message.delete()

        sentences = [
            "**Easy peasy, lemon squeezy** �",
            "**When life gives you a lemon, make it an admin!** <:lemonsloth:785872087414996992>",
            "**My greatest fear is a limenade...**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["felipe"])
    async def sousa(self, ctx) -> None:
        """ A command for telling something about Sousa. """

        await ctx.message.delete()

        sentences = [
            "If you give <@372100977060347906> a cup of coffee, he might tell you a secret...",
            "**<@372100977060347906> He's Simple, He's Dumb, He's The Pilot.**",
            "Gohan, vê se você me escuta... Não é pecado lutar pela justiça, ao contrário, é uma boa ação, pense... Existem inimigos que não são convencidos com palavras, você só tem que soltar a fúria que está dentro do seu espírito, eu sei como você se sente... Não precisa mais suportar isso Gohan... Gohan, proteja os seres vivos e as plantas desse mundo que eu tanto amei, conto com você. <@372100977060347906>"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["maksiu", "maks1u", "c4tchme"])
    async def choose_right(self, ctx) -> None:
        await ctx.message.delete()

        idkWhichOne = [
            "Oh, <@312940056115544064>. 🧠 He's found... never mind",
            "<@312940056115544064> If this were a game of 'spot the right one,' I'd say we're still playing 😈",
            "👌 ||Almost there||, but this one is playing hard to get! <@312940056115544064>",
            "u got me! 💐 from <@312940056115544064>",
            "with love to <@439110609745870870> 🇮🇹 from <@312940056115544064>"
        ]

        await ctx.send(choice(idkWhichOne))

    @commands.command(aliases=["birds"])
    async def keybirds(self, ctx) -> None:
        """ A command for telling something about Keybirds. """

        await ctx.message.delete()

        sentences = [
            "<@584699027421921280> Well, sounds like a good idea",
            "<@584699027421921280> Stina wants to go outside",
            "<@584699027421921280> I closed it and now it's closed"
            ]

        await ctx.send(choice(sentences))

    @commands.command()
    async def loral(self, ctx) -> None:
        """ A command for telling something about Loral. """

        await ctx.message.delete()
        await ctx.send("<@759049454819999776> Mans annoying")

    @commands.command()
    async def leonor(self, ctx) -> None:
        """ A command for telling something about Leonor. """

        await ctx.message.delete()
        await ctx.send("<@754678627265675325> Human brain smells like cat piss when it dries out")

    @commands.command()
    async def anis(self, ctx) -> None:
        """ A command for telling something about anis. """

        await ctx.message.delete()
        await ctx.send("<@515991382217981952> niso")

    @commands.command(aliases=["hodjapie", "onekebappls"])
    async def hodja(self, ctx) -> None:
        """ A command for telling something about the kebap guy, Hodja. """

        await ctx.message.delete()

        sentences = [
            "**I THOUGHT YOU WERE A GIRL** <@201086628167417857>",
            "*One kebap, please!* <@201086628167417857>"
        ]

        if randrange(67) == 33:
            await ctx.send("**SUPER RARE DOUBLE LAVASH KEBAP PULL!!!** <@201086628167417857>")
        else:
            await ctx.send(choice(sentences))
            
    @commands.command(aliases=["jelly", "jellyfish", "jellytimet", "jogurt", "doctor"])
    async def _jelly(self, ctx) -> None:
        """ A command for telling something about Jelly. """

        await ctx.message.delete()

        sentences = [
            "love you all from <@781007535267119138>",
            "<@781007535267119138> don't call me if you are sick, i'm busy jellying :p",
            "<@781007535267119138> I'm a doctor, not a magician",
            "be nice not mean, spread love not hate 💞",
            "<@781007535267119138> at your service, how may I help?",
            "An apple a day keeps a doctor away",
        ]

        await ctx.send(choice(sentences))


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Prestige(client))
