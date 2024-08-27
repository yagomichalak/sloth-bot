# import.standard
import asyncio
import os
from typing import List, Optional

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.minigames.rehab_members import RehabMembersTable
from extra.minigames.view import BlackJackActionView
from extra.slothclasses.player import Player
from mysqldb import * 
from .blackjack_db import BlackJackDB
from .blackjack_game import BlackJackGame
from .create_cards_pack import cards_pack

# variables.id
server_id: int = int(os.getenv('SERVER_ID', 123))

blackjack_db: List[commands.Cog] = [
	BlackJackDB
]

class BlackJack(*blackjack_db):
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
    @utils.is_subscriber()
    @Player.poisoned()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @RehabMembersTable.in_rehab()
    async def start_blackjack_game(self, ctx, bet = None) -> None:
        """ Starts the BlackJack game.
        :param bet: The amount of money you wanna bet.
        
        * Minimum bet = 50 leaves.
        * Maximum bet = 2500 leaves. """

        player: discord.Member = ctx.author
        guild_id = ctx.guild.id
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
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://languagesloth.com/profile/update"))
            return await ctx.send( 
                embed=discord.Embed(description=f"**{player.mention}, you don't have an account yet. Click [here](https://languagesloth.com/profile/update) to create one, or in the button below!**"),
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
            current_game = BlackJackGame(self.client, bet, player, [], [], self.cards_pack, guild_id, player_bal-bet)
            self.blackjack_games[guild_id][player.id] = current_game
            if current_game.status == 'finished':
                del self.blackjack_games[guild_id][player.id]

            view: discord.ui.View = BlackJackActionView(self.client, player)
            if current_game.status == 'finished':
                await utils.disable_buttons(view)

            await SlothCurrency.update_user_money(player.id, -bet)
            msg = await ctx.send(embed=current_game.embed(), view=view)

            # Checks if the user is in the blackjack table
            if not await self.check_user_database(ctx.author.id):
                await self.insert_user_database(ctx.author.id)

            # Inserts game in user blackjack status
            await self.insert_user_data(data_type="games", user_id=ctx.author.id)

            await view.wait()
            user_currency = await SlothCurrency.get_user_currency(player.id)
            current_game.current_money = user_currency[0][1]
            await asyncio.sleep(0.3)
            await utils.disable_buttons(view)
            await msg.edit(embed=current_game.embed(), view=view)

    @commands.command(aliases=[
        "fix_bj", "fbj", "fixbj", "reset_bj", "rbj", "resetbj",
        "fix_wj", "fwj", "fixwj", "reset_wj", "rwj", "resetwj",
        "fix_j", "fj", "fixj", "reset_j", "rj", "resetj"
    ])
    @utils.is_subscriber()
    async def fix_jack(self, ctx, member: discord.Member = None) -> None:
        """ Fixes the Jack games for a specific user.
        :param member: The member for whom fix the game. """

        author: discord.Member = ctx.author

        if member:
            perms = ctx.channel.permissions_for(author)
            if not perms.administrator:
                return await ctx.send("**You can't do that**")

        if not member:
            member: discord.Member = ctx.message.author

        # Checks if the user is in the blackjack table
        if not await self.check_user_database(author.id):
            return await ctx.send(f"**No games of blackjack were found for {member}**")

        fixed_games: bool = False

        if self.blackjack_games[ctx.guild.id].get(member.id):
            try:
                del self.blackjack_games[ctx.guild.id][member.id]
            except:
                pass
            else:
                fixed_games = True
                await ctx.send(f"**Fixed BJ game for `{member}`!**")
                
        if self.whitejack_games[ctx.guild.id].get(member.id):
            try:
                del self.whitejack_games[ctx.guild.id][member.id]
            except:
                pass
            else:
                fixed_games = True
                await ctx.send(f"**Fixed WJ game for `{member}`!**")
        if not fixed_games:
            if author.id == member.id:
                return await ctx.send(f"**You're not even broken, you can't be fixed, {member.mention}!**")
            else:
                return await ctx.send(f"**You're not even broken, you can't be fixed, {member.mention}!**")

    @commands.command(aliases=["bjs", "wjs", "whjs", "blackjack_status", "whitejack_status"])
    @commands.has_permissions()
    async def jack_status(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Shows your blackjack/whitejack game status; wins, losses, draws, surrenders and total of games.
        :param member: The member to show it for. [Optional][Default = You] """
    
        if not member:
            member: discord.Member = ctx.message.author
        
        _, wins, losses, draws, surrenders, _ = await self.get_user_data(member.id)

        games = sum([wins, losses, draws, surrenders])
        embed = discord.Embed(title=f"Jack Status {member}", timestamp=ctx.message.created_at, color=ctx.author.color)
        embed.description=(f"```{wins} wins ✅| {losses} losses ❌| {draws} draws 🔶| {surrenders} srr 🏳️| {games} games 🏅```")
        await ctx.send(embed=embed)
