from discord.ext import commands
from discord import slash_command

import os
from random import choice

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
guild_ids = [int(os.getenv('SERVER_ID', 123))]

class Prestige(commands.Cog):
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

    @slash_command(name="twiks", guild_ids=guild_ids)
    async def _twiks(self, ctx) -> None:
        """ Tells you something about Twiks. """

        await ctx.respond(f"**Twiks est mon frérot !**")

    @commands.command(aliases=["lexi", "lèqçi", "lexis"])
    async def alexis(self, ctx) -> None:
        """ A command for telling something about Alexis. """

        sentences = [
            "**I have a really nice voice**",
            "**Best sister-in-law ever**",
            "**z!bj 50**",
            "**z!bj 2500**",
            "**I see where you're coming from**",
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["eli", "elj", "elijaaah"])
    async def elijah(self, ctx) -> None:
        """ A command for telling something about Elijah. """

        await ctx.send("**Sure, go for it.**")

    @commands.command()
    async def freak(self, ctx) -> None:
        """ A command for telling something about Marceline. """

        await ctx.send("You mean missy aka Marceline")

    @commands.command(aliases=["winni", "winnie", "wynni", "wynnie"])
    async def wyncham(self, ctx) -> None:
        """ A command for telling something about Wyncham. """

        sentences = [
            "**You have a really nice voice**",
            "**Leonarda is my best friend**",
            "**Elijah and DNK are my brothers**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["not_lime", "lemonade", "citric", "yellow_fruit"])
    async def lemon(self, ctx) -> None:
        """ A command for telling something about Wyncham. """

        sentences = [
            "**Easy peasy, lemon squeezy** �",
            "**When life gives you a lemon, make it an admin!** <:lemonsloth:785872087414996992>",
            "**My greatest fear is a limenade...**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["frenzy"])
    async def frenesia(self, ctx) -> None:
        """ A command for telling something about frenesia. """
        
        sentences = [
            "# MIAOOOOOOO <:cat_wave:924495909595779082> <@439110609745870870>",
            "**CIAO SONO FRENESIA 🇮🇹 <@439110609745870870>**",
            "AHAHAAHAHAHA <@439110609745870870>"
        ]

        await ctx.send(choice(sentences))

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Prestige(client))
