import discord
from discord.ext import commands
from pprint import pprint
from typing import List, Any, Union, Tuple, Dict
import asyncio
from random import randint
from extra.minigames.view import MoveObjectGameView


class Game(commands.Cog):
    """ A category for a simple embedded message game. """

    def __init__(self, client) -> None:
        """"""

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Game cog is online!")

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def start(self, ctx) -> None:
        """ Starts the game. """

        member = ctx.author


        embed = discord.Embed(
            title="__`GRA`__",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )


        view: discord.ui.View = MoveObjectGameView(ctx, member)

        square = await view.make_game_square(update=True)
        square = '\n'.join(map(lambda r: ''.join(r), square))
        embed.description = square
        msg = await ctx.send(embed=embed, view=view)

        await view.wait()

        if view.status == 'Timeout':
            embed.title += ' (Timeout)'
            embed.color = discord.Color.red()
            ctx.command.reset_cooldown(ctx)
            await msg.edit(embed=embed)


            

        


def setup(client) -> None:
    client.add_cog(Game(client))
