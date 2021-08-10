import discord
from discord import member
from discord.ext import commands
from .player import Player
from .view import HugView, KissView, SlapView, HoneymoonView
from extra import utils

class SlothClassGeneralCommands(commands.Cog):

    def __init__(self, client) -> None:
        self.client  = client


    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def hug(self, ctx, *, member: discord.Member = None) -> None:
        """ Hugs someone.
        :param member: The member to hug.
        
        * Cooldown: 2 minutes """
        
        author = ctx.author
        if author.id == member.id:
            self.client.get_command('hug').reset_cooldown(ctx)
            return await ctx.send(f"**You can't hug yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Hug Prompt__",
            description=f"Do you really wanna hug {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = HugView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
    
    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def kiss(self, ctx, *, member: discord.Member = None) -> None:
        """ Kisses someone.
        :param member: The member to kiss.
        
        * Cooldown: 2 minutes """

        author = ctx.author
        if author.id == member.id:
            self.client.get_command('kiss').reset_cooldown(ctx)
            return await ctx.send(f"**You can't kiss yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Kiss Prompt__",
            description=f"Select the kind of kiss you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = KissView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def slap(self, ctx, *, member: discord.Member = None) -> None:
        """ Slaps someone.
        :param member: The member to slap.
        
        * Cooldown: 2 minutes """

        author = ctx.author
        if author.id == member.id:
            self.client.get_command('slap').reset_cooldown(ctx)
            return await ctx.send(f"**You can't slap yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Slap Prompt__",
            description=f"Select the kind of slap you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = SlapView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    # @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.not_ready()
    async def honeymoon(self, ctx) -> None:
        """ Celebrates a honey moon with your partner. """

        member = ctx.author
        partner = ctx.author

        embed = discord.Embed(
            title="__Honeymoon Setup__",
            description=f"{member.mention}, select where in the world you wanna have your honeymoon with {partner.mention}.",
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at,
            url="https://travel.usnews.com/rankings/best-honeymoon-destinations/"
        )
        embed.set_thumbnail(url='https://i.pinimg.com/originals/87/35/53/873553eeb255e47b1b4b440e4302e17f.gif')

        embed.set_author(name=member, icon_url=member.avatar.url, url=member.avatar.url)
        embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar.url)

        view = HoneymoonView(member=member, target=member, timeout=120)
        await ctx.send(content=f"{member.mention}, {partner.mention}", embed=embed, view=view)

        await view.wait()

        if view.value is None:
            await utils.disable_buttons(view)