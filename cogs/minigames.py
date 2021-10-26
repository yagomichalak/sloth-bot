import discord
from discord.ext import commands

from extra import utils
import os
from typing import List, Union, Dict, Optional

from extra.minigames.view import TicTacToeView


class MiniGames(commands.Cog):
    """ Category for minigames. """

    def __init__(self, client: commands.Bot) -> None:
        """ Classs init method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print('MiniGames cog is online!')

    @commands.command(aliases=["ttt", "jogo_da_idosa", "jdi", "jogo_da_velha", "#"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def tic_tac_toe(self, ctx, *, member: Optional[discord.Member] = None) -> None:
        """ Plays Tic Tac Toe.
        :param member: The opponent. [Optional][Default = PC] """

        author: discord.Member = ctx.author
        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member to play against, {author.mention}!**")

        if author.id == member.id:
            return await ctx.send(f"**You cannot play with yourself, {author.mention}! <:sheesh:872621063987679243>**")

        if member.bot:
            return await ctx.send(f"**You cannot play against a bot, {author.mention}! 🤖**")

        embed: discord.Embed = discord.Embed(
            title="__Tic Tac Toe__",
            color=member.color,
            timestamp=ctx.message.created_at
        )

        embed.set_author(name=author, icon_url=author.display_avatar)
        embed.set_footer(text=member, icon_url=member.display_avatar)

        view: discord.ui.View = TicTacToeView(self.client, player=author, opponent=member)

        embed.add_field(name="__Players__:", value=f"{author.mention} = ❌ | {member.mention} = ⭕", inline=False)
        embed.add_field(name="__Turn__:", value=f"Now it's {view.turn_member.mention}'s turn!")

        await ctx.send(embed=embed, view=view)

def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(MiniGames(client))