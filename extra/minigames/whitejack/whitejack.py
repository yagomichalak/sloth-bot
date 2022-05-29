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
    # @utils.not_ready()
    async def start_whitejack_game(self, ctx, bet = None) -> None:
        """ Starts the Whitejack game.
        :param bet: The amount of money you wanna bet.
        
        * Minimum bet = 50 leaves.
        * Maximum bet = 2500 leaves. """

        player: discord.Member = ctx.author
        max_bet: int = 2500
        guild = ctx.guild

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

        # Check if player's blackjack game is active
        if player.id in self.blackjack_games[guild.id]:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("**You are already in a game!**")
        if bet < minimum_bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")
        if player_bal < bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You don't have `{bet}`!**")
        if bet < minimum_bet:
            return await ctx.reply(f"**The minimum bet is `{minimum_bet}łł`!**")

        game = WhiteJackGame(self.client, bet, player, guild, player_bal)
        self.blackjack_games[guild.id][player.id] = game
        if game.status == 'finished':
            del self.blackjack_games[guild.id][player.id]

        embed = await game.create_whitejack_embed()
        whitejack_view: discord.ui.View = WhiteJackActionView(self.client, player, game)

        if game.status == 'finished':
            await utils.disable_buttons(whitejack_view)

        msg = await ctx.send(embed=embed, view=whitejack_view)
        await whitejack_view.wait()

        if game.state == 'win':
            await self.insert_user_data(type="wins", user_id=player.id)

            addition = bet
            if game.doubled:
                addition *= 2
            if game.blackjack:
                addition = int(bet * 1.5)

            player_bal += addition
            await SlothCurrency.update_user_money(player.id, addition)

        elif game.state == 'lose':
            await self.insert_user_data(type="losses", user_id=player.id)

            subtraction = bet
            if game.doubled:
                subtraction *= 2
            if game.blackjack:
                subtraction = int (bet * 0.75)

            player_bal -= subtraction
            await SlothCurrency.update_user_money(player.id, -subtraction)

        elif game.state == 'surrender':
            await self.insert_user_data('surrenders', player.id)
            
            subtraction = int(bet * 0.35)

            player_bal -= subtraction
            await SlothCurrency.update_user_money(player.id, -subtraction)
        
        elif game.state == 'draw':
            await self.insert_user_data('draws', player.id)

        print(f"Your current balance: {player_bal}")
        new_footer = f"Whitejack: {player_bal}łł"
        embed = msg.embeds[0]
        if embed.footer.text != new_footer:
            embed.set_footer(text=new_footer)
            await msg.edit(embed=embed)

        