import discord
from discord.ext import commands
from .blackjack_game import BlackJackGame
from .create_cards_pack import cards_pack

from extra.slothclasses.player import Player
from extra.minigames.view import BlackJackActionView
from extra import utils
import asyncio
import os

server_id: int = int(os.getenv('SERVER_ID'))

class BlackJack(commands.Cog):
    """ To start a blackjack game in your channel use the 'blackjack <bet>' command,
    and instead of <bet> put the amount you want to gamble (the value must be an integer).
    After you start a blackjack game use 'hit' command to draw a new card, 'stand' command
    to hold your total and end your turn, 'double' command which is like a 'hit' command,
    but the bet is doubled and you only get one more card, or 'surrender' command to give
    up and lose your bet. """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.cards_pack = cards_pack
        self.blackjack_games = {server_id: {}}

    @commands.command(name='blackjack', aliases=['bj'])
    @Player.poisoned()
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def start_blackjack_game(self, ctx, bet = None) -> None:
        """ Starts the BlackJack game.
        :param bet: The amount of money you wanna bet.
        
        PS: Minimum bet = 50 leaves. """

        player: discord.Member = ctx.author
        guild_id = ctx.guild.id

        if not bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform an amount to bet!**")

        try:
            bet = int(bet)
        except ValueError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform an integer value!**")

        if bet > 1000:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**The betting limit is `1000łł`!**")

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
        if player.id in self.blackjack_games[guild_id]:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("**You are already in a game!**")
        elif bet < minimum_bet:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")
        elif player_bal < bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You don't have `{bet}`!**")
        else:
            await SlothCurrency.update_user_money(player.id, -bet)

            current_game = BlackJackGame(self.client, bet, player, [], [], self.cards_pack, guild_id)
            self.blackjack_games[guild_id][player.id] = current_game
            if current_game.status == 'finished':
                del self.blackjack_games[guild_id][player.id]

            view: discord.ui.View = BlackJackActionView(self.client, player)
            if current_game.status == 'finished':
                await utils.disable_buttons(view)
            msg = await ctx.send(embed=current_game.embed(), view=view)

            await view.wait()
            await asyncio.sleep(0.3)
            await utils.disable_buttons(view)
            await msg.edit(embed=current_game.embed(), view=view)
