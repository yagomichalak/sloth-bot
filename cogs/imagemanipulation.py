import discord
from discord.ext import commands
from extra import utils

from PIL import Image, ImageDraw, ImageFont
from typing import Union, List, Any, Optional
import os


class ImageManipulation(commands.Cog):
    """ Categories for image manipulations and visualization. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class' init method. """

        self.client = client
        self.cached_image: Union[
            discord.Member.display_avatar, discord.User.display_avatar,
            discord.Guild.banner] = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print('ImageManipulation cog is ready!')

    @commands.command()
    async def avatar(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Shows the user avatar picture.
        :param member: The member to show. [Optional] [Default = You]. """

        if not member:
            member = ctx.author

        avatar = member.avatar if member.avatar else member.display_avatar
        display = member.display_avatar

        embed = discord.Embed(
            description=f"[Default]({avatar}) - [Server]({display})",
            color=int('36393F', 16)
        )

        embed.set_image(url=display)
        self.cached_image = display
        await ctx.reply(embed=embed)

    @commands.command()
    async def banner(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Shows the user banner picture if they have one
        :param member: The member to show. [Optional] [Default = You]. """

        if not member:
            member = ctx.author

        user = await self.client.fetch_user(member.id)

        banner = user.banner
        if not (banner := user.banner):
            if member == ctx.author:
                return await ctx.reply(f"**You don't have a banner!**")
            else:
                return await ctx.reply(f"**{member.mention} doesn't have a banner!**")

        embed = discord.Embed(
            description=f"[Banner]({banner})",
            color=int('36393F', 16)
        )

        embed.set_image(url=banner)
        self.cached_image = banner
        await ctx.send(embed=embed)

    @commands.command(aliases=["cache", "cached_image", "ci"])
    async def cached(self, ctx) -> None:
        """ Shows the cached image. """

        if not self.cached_image:
            return await ctx.reply(f"**There isn't a cached image, {ctx.author.mention}!**")

        embed = discord.Embed(
            description=f"[Cached Image]({self.cached_image})",
            color=int('36393F', 16)
        )

        embed.set_image(url=self.cached_image)
        await ctx.reply(embed=embed)

def setup(client: commands.Cog) -> None:
    """ Cog's setup function. """

    client.add_cog(ImageManipulation(client))