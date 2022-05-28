import discord
from discord.ext import commands
from .whitejack_game import WhiteJackGame
from mysqldb import *
from .whitejack_db import WhiteJackDB
from typing import List, Union, Optional, Dict, Any

from extra.slothclasses.player import Player
from extra.minigames.view import WhiteJackActionView
from extra.minigames.rehab_members import RehabMembersTable
from extra import utils
import asyncio
import os

server_id: int = int(os.getenv('SERVER_ID', 123))

whitejack_db: List[commands.Cog] = [
	WhiteJackDB
]
class WhiteJack(*whitejack_db):
    """ To start a Whitejack game in your channel use the 'whitejack <bet>' command,
    and instead of <bet> put the amount you want to gamble (the value must be an integer).
    After you start a Whitejack game use 'hit' command to draw a new card, 'stand' command
    to hold your total and end your turn, 'double' command which is like a 'hit' command,
    but the bet is doubled and you only get one more card, or 'surrender' command to give
    up and lose your bet. """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.whitejack_games: Dict[int, Dict[str, Any]] = {
            server_id: {}
        }

    @commands.command(name='whitejack', aliases=['whj'])
    @Player.poisoned()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @RehabMembersTable.in_rehab()
    async def start_whitejack_game(self, ctx, bet = None) -> None:
        """ Starts the Whitejack game.
        :param bet: The amount of money you wanna bet.
        
        * Minimum bet = 50 leaves.
        * Maximum bet = 2500 leaves. """

        player: discord.Member = ctx.author
        max_bet: int = 2500

        if not bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform an amount to bet!**")

        try:
            bet = int(bet)
        except ValueError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform an integer value!**")

        if bet > max_bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**The betting limit is `{max_bet}łł`!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(player.id)
        if not user_currency:
            ctx.command.reset_cooldown(ctx)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
            return await ctx.send( 
                embed=discord.Embed(description=f"**{player.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)


        player_bal = user_currency[0][1]
        minimum_bet = 50

        if bet < minimum_bet:
            return await ctx.reply(f"**The minimum bet is `{minimum_bet}łł`!**")

        
        game = WhiteJackGame(self.client, bet, player, ctx.guild, player_bal-bet)
        embed = await game.create_whitejack_embed()

        whitejack_view: discord.ui.View = WhiteJackActionView(self.client, player, game)

        await ctx.send(embed=embed, view=whitejack_view)