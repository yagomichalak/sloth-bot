import discord
from discord.ext import commands

from extra.minigames.view import MoveObjectGameView, TicTacToeView, FlagsGameView
from random import randint, sample, shuffle
from extra import utils
import os
import json

from typing import List, Union, Dict, Optional
import asyncio
from extra.minigames.view import TicTacToeView, FlagsGameView
from random import randint, sample, shuffle

class Games(commands.Cog):
    """ A category for a minigames. """

    def __init__(self, client) -> None:
        """ Class init method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Game cog is online!")

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
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

        await ctx.send(embed=embed, view=view)
        

    @commands.command(aliases=['flag', 'flag_game', 'flags'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def flag_quiz(self, ctx) -> None:
        """ Plays Country Flags Quiz"""
        
        json_flags = json.load(open("extra/random/json/flag_game.json"))
        
        # Select twenty unique flags
        flags = [json_flags[number] for number in sample(range(0, len(json_flags)), 20)]

        await self.generate_flag_game(ctx=ctx, points=0, round=0, flags=flags)


    async def generate_flag_game(self, ctx: commands.Context, message: Optional[discord.Message] = None, points: int = 0, round: int = 0, flags: List = None):
        # Open JSON file
        json_flags = json.load(open("extra/random/json/flag_game.json"))

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
        embed.set_image(url=flags[round]['link'] + ".png")
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        embed.set_footer(text=f"Round {round + 1} of 20")

        # Creates the buttons
        view = FlagsGameView(ctx=ctx, client=self.client, countries_names=countries_options, flags=flags, points=points, round=round)
    
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

            if round >= 19:
                return await self.end_flag_game(ctx=ctx, message=message, member=ctx.message.author, points=points)
    
            await self.generate_flag_game(ctx=ctx, message=message, points=points, round=round + 1, flags=flags)


    async def end_flag_game(self, ctx: commands.Context, message: discord.Message, member: discord.Member, points: int):
        # Generates the end game embed
        embed = discord.Embed(
            title='__Guess the flag__',
            description= f"✅ Correct Answers: {points}/20.",
        )
        embed.set_author(name=member, icon_url=member.display_avatar)

        await message.edit('\u200b', embed=embed, view=None)


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

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Games(client))
