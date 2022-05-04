import discord
from discord.ext import commands

from random import randint, sample, shuffle, choice
import os
import json
from typing import List, Dict, Optional, Any, Union
import asyncio

from extra import utils
from extra.slothclasses.player import Player
from extra.minigames.connect_four import ConnectFour
from extra.minigames.blackjack.blackjack import BlackJack
from extra.minigames.view import MoveObjectGameView, TicTacToeView, FlagsGameView

minigames_cogs: List[commands.Cog] = [
    ConnectFour, BlackJack
]

class Games(*minigames_cogs):
    """ A category for a minigames. """

    def __init__(self, client) -> None:
        """ Class init method. """

        # Initiates all inherited cogs
        for minigame_cog in minigames_cogs:
            minigame_cog.__init__(self, client)
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the Games cog is ready to go. """

        print("Game cog is online!")

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def destiny(self, ctx) -> None:
        """ Plays the Destiny game. """

        member = ctx.author


        embed = discord.Embed(
            title="__Destiny__",
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

    @commands.command(aliases=["ttt", "jogo_da_idosa", "jdi", "jogo_da_velha", "#"])
    @Player.poisoned()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def tic_tac_toe(self, ctx, *, member: discord.Member = None) -> None:
        """ Plays Tic Tac Toe.
        :param member: The opponent. """

        author: discord.Member = ctx.author
        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member to play against, {author.mention}!**")

        if author.id == member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot play with yourself, {author.mention}! <:sheesh:872621063987679243>**")

        if member.bot:
            ctx.command.reset_cooldown(ctx)
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

        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        await asyncio.sleep(0.3)

        if view.state is False:
            embed.color = discord.Color.brand_red()
            embed.set_field_at(1, name="__Timeout__", value="The game has timeouted!")
            await msg.edit(embed=embed)
        

    @commands.command(aliases=['flag', 'flag_game', 'flags'])
    @Player.poisoned()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def flag_quiz(self, ctx) -> None:
        """ Plays Country Flags Quiz"""

        json_flags = json.load(open("extra/random/json/flag_game.json"))

        # Selects twenty unique flags
        flags = [json_flags[number] for number in sample(range(0, len(json_flags)), 20)]

        await self.generate_flag_game(ctx=ctx, points=0, round=0, flags=flags)


    async def generate_flag_game(self, ctx: commands.Context, message: Optional[discord.Message] = None, points: int = 0, round: int = 0, flags: List[Any] = None, timeout_count: int = 0):
        # Open JSON file
        json_flags = json.load(open("extra/random/json/flag_game.json", encoding='utf-8'))

        # Creates the name options
        countries_options = []

        # Gets three random countries name
        while len(countries_options) != 3:
            name = json_flags[randint(0, len(json_flags) - 1)]['name']
            if name + '0' not in countries_options and name != flags[round]['name']:
                countries_options.append(name + '0')
        
        countries_options.append(flags[round]['name'] + '1')
        shuffle(countries_options)

        # Game embed
        embed = discord.Embed(
            title='__Guess the flag__',
            description= f"\u200b\n**🪙 Points: {points}**",
            colour=1,
        )
        embed.set_image(url=f"https://flagcdn.com/224x168/{flags[round]['code']}.png")
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        embed.set_footer(text=f"Round {round + 1} of 20")

        # Creates the buttons
        view = FlagsGameView(ctx=ctx, client=self.client, countries_names=countries_options, flags=flags, points=points, round=round, timeout_count=timeout_count)
    
        if message:
            await message.edit('\u200b', embed=embed, view=view)  
        else:
            message = await ctx.send('\u200b', embed=embed, view=view) 

        await view.wait()

        # Timeout
        if not view.used:
            view.stop()

            # Shows the correct button
            correct_button = [button for button in view.children if button.label == flags[round]['name']]
            correct_button[0].style = discord.ButtonStyle.primary

            embed.description = f"\n** 🪙 Points: {points}**\n\n**🔺 Timeout!**"
            
            await message.edit('\u200b', embed=embed, view=view)    

            await asyncio.sleep(1)

            if view.timeout_count == 3:
                return await self.end_flag_game(ctx=ctx, message=message, member=ctx.message.author, points=points)

            else:
                view.timeout_count += 1

            if round >= 19:
                return await self.end_flag_game(ctx=ctx, message=message, member=ctx.message.author, points=points)
    
            await self.generate_flag_game(ctx=ctx, message=message, points=points, round=round + 1, flags=flags, timeout_count=view.timeout_count)

        else:
            view.timeout_count = 0

    async def end_flag_game(self, ctx: commands.Context, message: discord.Message, member: discord.Member, points: int):
        # Generates the end game embed
        embed = discord.Embed(
            title='__Guess the flag__',
            description= f"✅ Correct Answers: {points}/20.",
        )
        embed.set_author(name=member, icon_url=member.display_avatar)
        await message.edit('\u200b', embed=embed, view=None)

        if points == 20:
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(member.id, 4)


    #=== Flag games settings ===#
    @commands.command(hidden=True)
    @commands.is_owner()
    async def check_flags(self, ctx) -> None:
        """ Shows all flags and their names. This command is used to check the link of the images. """

        json_flags = json.load(open("extra/random/json/flag_game.json", encoding='utf-8'))
        for flag in json_flags:
            embed = discord.Embed()
            embed.set_image(url=flag['link'] + '.png')
            await ctx.send(flag['name'], embed=embed)

    
    @commands.command(aliases=['lotto'])
    @Player.poisoned()
    async def lottery(self, ctx, g1 = None, g2 = None, g3 = None):
        """ Enter the lottery and see if you win!
        :param g1: Guess 1.
        :param g2: Guess 2.
        :param g3: Guess 3.
        
        * Cost: 1łł.
        * Prize: 500łł """

        author = ctx.author

        await ctx.message.delete()
        if not g1:
            return await ctx.send("**You informed 0 guesses, 3 guesses are needed!**", delete_after=3)
        elif not g2:
            return await ctx.send("**You informed 1 guess, 3 guesses are needed!**", delete_after=3)
        elif not g3:
            return await ctx.send("**You informed 2 guesses, 3 guesses are needed!**", delete_after=3)

        try:
            g1 = int(g1)
            g2 = int(g2)
            g3 = int(g3)
        except ValueError:
            return await ctx.send("**All guesses must be integers!**", delete_after=3)

        for n in [g1, g2, g3]:
            if n <= 0 or n > 5:
                return await ctx.send(f"**Each number must be between 1-5!**", delete_after=3)

        SlothCurrency = self.client.get_cog('SlothCurrency')

        # Check if user is not on cooldown
        user_secs = await SlothCurrency.get_user_currency(author.id)
        current_ts = await utils.get_timestamp()
        if not user_secs:
            await SlothCurrency.insert_user_currency(author.id, current_ts - 61)
            user_secs = await SlothCurrency.get_user_currency(author.id)

        if user_secs[0][1] >= 1:
            await SlothCurrency.update_user_money(author.id, -1)
        else:
            return await ctx.send(f"**You need 1łł to play the lottery, {author.mention}!**")

        if user_secs[0][6]:
            sub_time = current_ts - user_secs[0][6]
            if sub_time >= 1200:
                await SlothCurrency.update_user_lotto_ts(author.id, current_ts)
            else:
                m, s = divmod(1200 - int(sub_time), 60)
                h, m = divmod(m, 60)
                if h > 0:
                    return await ctx.send(f"**You're on cooldown, try again in {h:d} hours, {m:02d} minutes and {s:02d} seconds.**", delete_after=5)
                elif m > 0:
                    return await ctx.send(
                        f"**You're on cooldown, try again in {m:02d} minutes and {s:02d} seconds.**",
                        delete_after=5)
                else:
                    return await ctx.send(
                        f"**You're on cooldown, try again in {s:02d} seconds.**",
                        delete_after=5)
        else:
            await SlothCurrency.update_user_lotto_ts(author.id, current_ts)

        author = author
        numbers = []
        for x in range(3):
            numbers.append(randint(1, 5))

        string_numbers = [str(i) for i in numbers]
        if g1 == numbers[0] and g2 == numbers[1] and g3 == numbers[2]:
            await ctx.send(f'**{author.mention} You won! Congratulations on winning the lottery with the numbers ({g1}, {g2}, {g3})!🍃+500łł!**')
            if not await SlothCurrency.get_user_currency(author.id):

                await SlothCurrency.insert_user_currency(author.id, current_ts - 61)
            await SlothCurrency.update_user_money(author.id, 500)

        else:
            await ctx.send(
                f"**{author.mention}, better luck next time... You guessed {g1}, {g2}, {g3}...\nThe numbers were:** `{', '.join(string_numbers)}`")

    
    @commands.command(aliases=['dice'])
    @Player.poisoned()
    async def roll(self, ctx, sides = None):
        """ Roll a dice with the number of faces given.
        :param sides: The number of faces to roll. """
        
        await ctx.message.delete()

        if not sides:
            sides = 6

        try:
            sides = int(sides)
        except ValueError:
            sides = 6

        if sides > 1000000000000 or sides < 0:
            return await ctx.send("**Enter a valid integer value**", delete_after=3)
        
        embed = discord.Embed(color=ctx.author.color, title=f":game_die: **YOU GOT:** **{randint(1, sides)}** :game_die: `(1 - {sides})`",
            timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Rolled by {ctx.author}", icon_url=ctx.author.display_avatar)
        await ctx.send(embed=embed)


    @commands.command(aliases=['flip_coin', 'flipcoin', 'coinflip', 'cf', 'fc'])
    @Player.poisoned()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coin_flip(self, ctx, bet: int = None, side: str = None) -> None:
        """ Command for flipping a coin.
        :param bet: The amount of money you want to bet.
        :param side: The side you wanna bet on. (Heads/Tail)
        
        * Minimum bet: 50łł """

        member: discord.Member = ctx.author

        if bet is None or bet < 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform how much you wanna bet!**")

        minimum_bet: int = 50
        bet_limit: int = 5000
        if bet > bet_limit:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You cannot bet more than {bet_limit}łł at a time, {member.mention}!**")

        if not side:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform the side you wanna bet on!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency: List[int] = await SlothCurrency.get_user_currency(member.id)
        if not user_currency:
            return await ctx.reply("**You don't even have a Profile!**")

        if user_currency[0][1] < bet:
            return await ctx.reply(f"**You don't have `{bet} leaves` to bet!**")

        if bet != 0 and bet < minimum_bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")

        side_options: Dict[str, List[str]] = {
            'Tail': {'aliases': ['t', 'tail', 'tails'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/2021_Native_American_%241_Coin_Reverse.png/220px-2021_Native_American_%241_Coin_Reverse.png'},
            'Heads': {'aliases': ['h', 'head', 'heads'], 'image': 'https://upload.wikimedia.org/wikipedia/en/f/fe/Sacagawea_dollar_obverse.png'}
        }

        if side.lower() not in side_options['Tail']['aliases'] + side_options['Heads']['aliases']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("**Please, inform a valid side!**")

        side = 'Tail' if side.lower() in side_options['Tail']['aliases'] else 'Heads'

        coin_var: str = choice(['Tail', 'Heads'])
        win_var: str = 'won' if side.lower() == coin_var.lower() else 'lost'
        # Makes the embed
        embed: discord.Embed = discord.Embed(
            description = f"It's **{coin_var}**",
        )
        if bet != 0: embed.add_field(name=f"Amount {win_var}", value=f"{bet} leaves 🍃")
        
        if win_var == 'won':
            embed.color=discord.Color.green()
            if bet != 0:
                embed.add_field(name="New balance", value=f"{user_currency[0][1]+bet} leaves 🍃")
                await SlothCurrency.update_user_money(member.id, bet)
        else:
            embed.color=discord.Color.dark_red()
            if bet != 0:
                embed.add_field(name="New balance", value=f"{user_currency[0][1]-bet} leaves 🍃")
                await SlothCurrency.update_user_money(member.id, -bet)

        embed.set_author(name=f"You've {win_var}!", icon_url=member.display_avatar)
        embed.set_thumbnail(url=side_options[coin_var]['image'])
        embed.set_footer(text=f"Gambled by {member}")
        await ctx.reply(embed=embed)

        if win_var == 'won' and bet == 50:
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(member.id, 3)



    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def slots(self, ctx, bet: int = None) -> None:
        """ Command for playing Slots.
        :param bet: The amount you wanna bet.
        
        * Minimum bet: 50łł """

        author: discord.Member = ctx.author

        if not bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**Please inform how much you wanna bet, {author.mention}**")

        minimum_bet: int = 50
        bet_limit: int = 5000
        if bet > bet_limit:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You cannot bet more than {bet_limit}łł at a time, {author.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(author.id)
        if not user_currency:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
            return await ctx.reply( 
                embed=discord.Embed(description=f"**{author.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)

        try:
            bet = int(bet)
        except ValueError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**Please, inform a valid bet value, {author.mention}!**")

        if bet > user_currency[0][1]:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You don't have {bet} to bet, {author.mention}!**")

        if bet < minimum_bet:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**The minimum bet is `{minimum_bet} leaves`!**")

        if bet < 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"**You must inform a positive amount to bet, {author.mention}**")

        # slots = ['bus', 'train', 'horse', 'heart', 'monkey', 'cow', 'parrot', 'leaves', 'money_mouth']
        slots: List[Dict[str, Union[str, int, float]]] = [
            {"emoji": ':bus:', "multiplier": 2}, 
            {"emoji": ':train:', "multiplier": 2}, 
            {"emoji": ':heart:', "multiplier": 4}, 
            {"emoji": ':monkey:', "multiplier": 2}, 
            {"emoji": ':cow:', "multiplier": 2}, 
            {"emoji": ':money_mouth:', "multiplier": 3},
        ]

        slot1 = slots[randint(0, 5)]
        slot2 = slots[randint(0, 5)]
        slot3 = slots[randint(0, 5)]

        slotOutput = '| {} | {} | {} |\n'.format(slot1["emoji"], slot2["emoji"], slot3["emoji"])

        ok = discord.Embed(title="__Slots Machine__", color=discord.Color(0xFFEC))
        ok.set_footer(text=f"Bet from {author}", icon_url=author.display_avatar)


        rolling_emoji: str = '<a:slots_emoji:903335419725373490>'
        ok.add_field(name='Rolling...', value='| {} | {} | {} |\n'.format(rolling_emoji, rolling_emoji, rolling_emoji))
        msg = await ctx.send(embed=ok)
        await asyncio.sleep(0.8)

        ok.set_field_at(0, name='Rolling...', value='| {} | {} | {} |\n'.format(slot1["emoji"], rolling_emoji, rolling_emoji))
        await msg.edit(embed=ok)
        await asyncio.sleep(0.8)

        ok.set_field_at(0, name='Rolling...', value='| {} | {} | {} |\n'.format(slot1["emoji"], slot2["emoji"], rolling_emoji))
        await msg.edit(embed=ok)
        await asyncio.sleep(0.8)

        money_won: int = bet * slot1['multiplier']

        # User won with 3
        won = discord.Embed(title = "Slots Machine", color = discord.Color(0xFFEC))
        won.add_field(name="{}\nWon".format(slotOutput), value=f'You won {money_won} leaves')
        won.set_footer(text=f"Bet from {author}", icon_url=author.display_avatar)

        # User broke even with 2
        be = discord.Embed(title = "Slots Machine", color = discord.Color(0xFFEC))
        be.add_field(name="{}\nBroke even".format(slotOutput), value=f'You broke even, so you keep your {bet} leaves')
        be.set_footer(text=f"Bet from {author}", icon_url=author.display_avatar)

        # User lost
        lost = discord.Embed(title = "Slots Machine", color = discord.Color(0xFFEC))
        lost.add_field(name="{}\nLost".format(slotOutput), value=f'You lost {bet} leaves')
        lost.set_footer(text=f"Bet from {author}", icon_url=author.display_avatar)


        if slot1["emoji"] == slot2["emoji"] == slot3["emoji"]:
            await SlothCurrency.update_user_money(ctx.author.id, money_won)
            return await msg.edit(embed=won)
        elif slot1["emoji"] == slot2["emoji"] or slot2["emoji"] == slot3["emoji"]:
            return await msg.edit(embed=be)
        else:
            await SlothCurrency.update_user_money(ctx.author.id, -bet)
            return await msg.edit(embed=lost)


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Games(client))
