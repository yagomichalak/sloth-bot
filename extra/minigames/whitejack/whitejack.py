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
import string
import random

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
    async def start_whitejack_game(self, ctx, bet = None, games: int = 1) -> None:
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
        
        try:
            games = int(games)
        except ValueError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform an integer value!**")

        if games <= 0:
            return await ctx.send(f"**You must have at least 1 game!**")

        if games > 5:
            return await ctx.send(f"**You can only have a maximum of 5 games at a time!**")

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
        if game_sessions := self.whitejack_games[guild.id].get(player.id):
            if len(game_sessions) >= 5:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("**You reached the limit of 5 games at a time!**")
        if bet < minimum_bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")
        if player_bal < bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You don't have `{bet}`!**")
        if bet < minimum_bet:
            return await ctx.reply(f"**The minimum bet is `{minimum_bet}łł`!**")

        for _ in range(games):
            await self.white_jack_callback_before(bet, player, guild, player_bal, ctx=ctx)
    
    async def white_jack_callback_before(self, 
        bet: int, player: discord.Member, guild: discord.Guild, player_bal: int,
        ctx: commands.Context = None, interaction: discord.Interaction = None
    ) -> None:

        session_id: int = self.generate_session_id()
        game = WhiteJackGame(self.client, bet, player, guild, player_bal, session_id)
        game_sessions = self.whitejack_games[guild.id]
        if game_sessions.get(player.id):
            game_sessions[player.id][session_id] = game
        else:
            game_sessions[player.id] = {session_id: game}

        if game.status == 'finished':
            del self.whitejack_games[guild.id][player.id][game.session_id]
            
        embed = await game.create_whitejack_embed()
        whitejack_view: discord.ui.View = WhiteJackActionView(self.client, player, game)

        if game.status == 'finished':
            await utils.disable_buttons(whitejack_view)
            return await whitejack_view.end_game(ctx)

        if ctx:
            msg = await ctx.send(embed=embed, view=whitejack_view)
            whitejack_view.msg = msg
        else:
            msg = await interaction.followup.edit_message(interaction.message.id, embed=embed, view=whitejack_view)
            whitejack_view.msg = msg

    async def white_jack_callback_after(self, view: discord.ui.View, game: Any, guild: discord.Guild, msg: discord.Message) -> None:

        SlothCurrency = self.client.get_cog('SlothCurrency')
        bet = game.bet
        player = game.player
        player_bal = game.current_money

        # msg = await interaction.followup.edit_message(interaction.message.id, view=view)

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

        game.current_money = player_bal
        new_footer = f"Whitejack: {player_bal}łł"
        embed = await game.create_whitejack_embed()
        embed.set_footer(text=new_footer)
        msg = await msg.edit(embed=embed)
        view.msg = msg

        
    def generate_session_id(self, length: Optional[int] = 18) -> str:
        """ Generates a session ID.
        :param length: The length of the session ID. [Default = 18] """

        # Defines data
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        num = string.digits
        symbols = string.punctuation

        # Combines the data
        all_chars = lower + upper + num + symbols

        # Uses random 
        temp = random.sample(all_chars, length)

        # Create the session ID 
        session_id = "".join(temp)
        return session_id