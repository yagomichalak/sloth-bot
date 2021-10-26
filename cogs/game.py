import discord
from discord.ext import commands

from extra.minigames.view import MoveObjectGameView, TicTacToeView


class Game(commands.Cog):
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
        


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Game(client))
