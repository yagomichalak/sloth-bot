import discord
from discord.ext import commands

import os
from extra import utils
from random import choice

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))

class Prestige(commands.Cog):
    """ Category for prestige commands. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """
        
        self.client = client

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

    @commands.command(aliases=["winni", "winnie", "wynni", "wynnie"])
    async def lemon(self, ctx) -> None:
        """ A command for telling something about Wyncham. """

        sentences = [
            "**Easy peasy, lemon squeezy** �",
            "**When life gives you a lemon, make it an admin!** <:lemonsloth:785872087414996992>",
            "**My greatest fear is a limenade...**"
        ]

        await ctx.send(choice(sentences))


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Prestige(client))
