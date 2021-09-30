import discord
from discord.ext import commands
from extra import utils

from PIL import Image, ImageDraw, ImageFont
from typing import Union, List, Any, Optional
import os
from io import BytesIO

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
        :param member: The member to show. [Optional][Default = You]. """

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
        :param member: The member to show. [Optional][Default = You]. """

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

    @commands.command(aliases=["invert"])
    @utils.not_ready()
    async def flip(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Flips an image.
        :param member: The member to flip the profile picture. [Optional][Default = Cached Image] """

        pass

    @commands.command()
    @utils.not_ready()
    async def rain(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Rains on an image, making its colors look different.
        :param member: The member to rain on the profile picture. [Optional][Default = Cached Image] """

        pass

    @commands.command()
    @utils.not_ready()
    async def explode(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Explodes an image.
        :param member: The member to explode the profile picture. [Optional][Default = Cached Image] """

        pass

    @commands.command()
    @utils.not_ready()
    async def implode(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Implodes an image.
        :param member: The member to implode the profile picture. [Optional][Default = Cached Image] """

        pass

    @commands.command()
    @utils.not_ready()
    async def rotates(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Rotates an image.
        :param member: The member to rotate the profile picture from. [Optional][Default = Cached Image] """

        pass

    @commands.command(aliases=['light', 'brighten', 'bright'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lighten(self, ctx, member: Optional[discord.Member] = None, percentage: int = 55) -> None:
        """ Lightens an image.
        :param member: The member of whom to lighten the picture. [Optional][Default = Cached Image] """

        file: Any = None

        if member:
            file = member.display_avatar
        else:
            if self.cached_image:
                file = self.cached_image
            else:
                file = ctx.author.display_avatar
        image: Image.Image = await self.change_image_brightness(file=file, action='lighten', percentage=percentage)
        self.cached_image = image
        embed = discord.Embed(
            color=int('36393F', 16)
        )

        embed.set_image(url='attachment://lightened_image.png')
        bytes_image = await self.image_to_byte_array(image)
        await ctx.reply(embed=embed, file=discord.File(BytesIO(bytes_image), 'lightened_image.png'))

    @commands.command(aliases=['dark', 'dim'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def darken(self, ctx, member: Optional[discord.Member] = None, percentage: int = 55) -> None:
        """ Darkens an image.
        :param member: The member of whom to darken the profile picture. [Optional][Default = Cached Image] """

        file: Any = None

        if member:
            file = member.display_avatar
        else:
            if self.cached_image:
                file = self.cached_image
            else:
                file = ctx.author.display_avatar
        image: Image.Image = await self.change_image_brightness(file=file, action='darken', percentage=percentage)
        self.cached_image = image
        embed = discord.Embed(
            color=int('36393F', 16)
        )

        embed.set_image(url='attachment://darkened_image.png')
        bytes_image = await self.image_to_byte_array(image)
        await ctx.reply(embed=embed, file=discord.File(BytesIO(bytes_image), 'darkened_image.png'))

    async def image_to_byte_array(self, image: Image.Image) -> bytes:
        """ Converts an image to bytes.
        :param image: The image to convert to bytes. """

        imgByteArr = BytesIO()
        image.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    async def change_image_brightness(self, file: Any, action: str, percentage: int,
        r: bool = True, g: bool = True, b: bool = True) -> None:
        """ Changes the brightness level of each pixel of the image.
        :param file: The file to execute the task on.
        :param action: Whether to lighten or darken the image.
        :param percentage: The percentage to ligthen or darken the image. """

        if not isinstance(file, Image.Image):
            original_image = Image.open(BytesIO(await file.read()))
        else:
            original_image = file
        pixels = original_image.getdata()

        #initialise the new image
        new_image = Image.new('RGB', original_image.size)
        new_image_list = []

        brightness_multiplier = 1.0

        if action == 'lighten':
            brightness_multiplier += (percentage/100)
        else:
            brightness_multiplier -= (percentage/100)

        #for each pixel, append the brightened or darkened version to the new image list
        for pixel in pixels:
            new_pixel = (
                int(pixel[0] * brightness_multiplier) if r else int(pixel[0]),
                int(pixel[1] * brightness_multiplier) if g else int(pixel[1]),
                int(pixel[2] * brightness_multiplier) if b else int(pixel[2])
            )

            #check the new pixel values are within rgb range
            for pixel in new_pixel:
                if pixel > 255:
                    pixel = 255
                elif pixel < 0:
                    pixel = 0

            new_image_list.append(new_pixel)

        #save the new image
        new_image.putdata(new_image_list)
        return new_image


    

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def red(self, ctx, member: Optional[discord.Member] = None, percentage: int = 55) -> None:
        """ Makes an image redder.
        :param member: The member of whom to increase the red values of the profile picture. [Optional][Default = Cached Image] """

        file: Any = None

        if member:
            file = member.display_avatar
        else:
            if self.cached_image:
                file = self.cached_image
            else:
                file = ctx.author.display_avatar
        image: Image.Image = await self.change_image_brightness(file=file, action='lighten', percentage=percentage, r=False)
        self.cached_image = image
        embed = discord.Embed(
            color=int('36393F', 16)
        )

        embed.set_image(url='attachment://red_image.png')
        bytes_image = await self.image_to_byte_array(image)
        await ctx.reply(embed=embed, file=discord.File(BytesIO(bytes_image), 'red_image.png'))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blue(self, ctx, member: Optional[discord.Member] = None, percentage: int = 55) -> None:
        """ Makes an image bluer.
        :param member: The member of whom to increase the bluer values of the profile picture. [Optional][Default = Cached Image] """

        file: Any = None

        if member:
            file = member.display_avatar
        else:
            if self.cached_image:
                file = self.cached_image
            else:
                file = ctx.author.display_avatar
        image: Image.Image = await self.change_image_brightness(file=file, action='lighten', percentage=percentage, g=False)
        self.cached_image = image
        embed = discord.Embed(
            color=int('36393F', 16)
        )

        embed.set_image(url='attachment://blue_image.png')
        bytes_image = await self.image_to_byte_array(image)
        await ctx.reply(embed=embed, file=discord.File(BytesIO(bytes_image), 'blue_image.png'))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def yellow(self, ctx, member: Optional[discord.Member] = None, percentage: int = 55) -> None:
        """ Makes an image yellower.
        :param member: The member of whom to increase the yellow values of the profile picture. [Optional][Default = Cached Image] """

        file: Any = None

        if member:
            file = member.display_avatar
        else:
            if self.cached_image:
                file = self.cached_image
            else:
                file = ctx.author.display_avatar
        image: Image.Image = await self.change_image_brightness(file=file, action='lighten', percentage=percentage, b=False)
        self.cached_image = image
        embed = discord.Embed(
            color=int('36393F', 16)
        )

        embed.set_image(url='attachment://yellow_image.png')
        bytes_image = await self.image_to_byte_array(image)
        await ctx.reply(embed=embed, file=discord.File(BytesIO(bytes_image), 'yellow_image.png'))

def setup(client: commands.Cog) -> None:
    """ Cog's setup function. """

    client.add_cog(ImageManipulation(client))