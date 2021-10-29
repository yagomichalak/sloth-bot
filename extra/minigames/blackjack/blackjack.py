import discord
from discord.ext import commands
from .blackjack_game import BlackJackGame
from .create_cards_pack import cards_pack

from extra.minigames.view import BlackJackActionView
from extra import utils

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
        self.blackjack_games = {}

    @commands.command(name='blackjack', aliases=['bj'])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def start_blackjack_game(self, ctx, bet = None) -> None:
        """ Starts the BlackJack game.
        :param bet: The amount of money you wanna bet.
        
        PS: Minimum bet = 50 leaves. """

        player: discord.Member = ctx.author
        guild_id = ctx.guild.id

        if not bet:
            return await ctx.reply("**Please, inform an amount to bet!**")

        try:
            bet = int(bet)
        except ValueError:
            return await ctx.reply("**Please, inform an integer value!**")

        if bet > 1000:
            return await ctx.reply("**The betting limit is `1000łł`!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(player.id)
        if not user_currency:
            return await ctx.reply("**You don't have an account yet, use `!text_rank` or `!vc_rank` to create one!**")


        player_bal = user_currency[0][1]
        minimum_bet = 50

        try:
            bet = int(bet)
        except ValueError:
            raise commands.UserInputError

        if user_currency[0][1] < minimum_bet:
            return await ctx.reply("**The minimum bet is `50 leaves`!**")

        if user_currency[0][1] < bet:
            return await ctx.reply(f"**You don't have `{bet}`!**")

        if self.blackjack_games.get(guild_id) is None:
            self.blackjack_games[guild_id] = {}

        # Check if player's blackjack game is active
        if player.id in self.blackjack_games[guild_id]:
            await ctx.send("**You are already in a game!**")
        elif bet < minimum_bet:
            await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")
        elif player_bal < bet:
            await ctx.send("**You have insufficient funds!**")
        else:
            await SlothCurrency.update_user_money(player.id, -bet)

            current_game = BlackJackGame(self.client, bet, player, [], [], self.cards_pack, guild_id)
            self.blackjack_games[guild_id][player.id] = current_game
            if current_game.status == 'finished':
                del self.blackjack_games[guild_id][player.id]

            view: discord.ui.View = BlackJackActionView(self.client, player)
            if current_game.status == 'finished':
                await utils.disable_buttons(view)
            await ctx.send(embed=current_game.embed(), view=view)
