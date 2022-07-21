import discord
from discord.ext import commands
from discord import slash_command, Option
import os
import aiohttp
import json
from random import choice
from typing import List
from extra import utils

guild_ids: List[int] = [int(os.getenv("SERVER_ID", 123))]

class Pictures(commands.Cog):
    """ Category for getting random pictures from the internet. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print("Pictures cog is online!")


    @commands.command(aliases=['tak'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cow(self, ctx) -> None:
        """ Gets a random Cow image. """

        author: discord.Member = ctx.author
        cow_token: str = os.getenv('COW_API_TOKEN')
        
        req: str = f'https://api.unsplash.com/search/photos?client_id={cow_token}&?&query=cow&?format=json'


        async with self.session.get(req) as response:
            if response.status != 200:
                return await ctx.send(f"**Something went wrong with your request, {author.mention}!**")

            data = json.loads(await response.read())
            pics = data['results']
            embed: discord.Embed = discord.Embed(
                title="__Cow__",
                description=f"Showing 1 random Cow picture out of {len(pics)} results.",
                color=author.color,
                timestamp=ctx.message.created_at
            )

            embed.set_image(url=choice(pics)['urls']['full'])
            embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
            await ctx.send(embed=embed)


    @commands.command(aliases=['httpcat', 'hc', 'http'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def http_cat(self, ctx, code: int = None) -> None:
        """ Gets an HTTP cat image. 
        :param code: The HTTP code to search the image. """

        if not code:
            return await ctx.send("**Please, inform an HTTP code!**")

        code_list = [
            100, 101, 102, 200, 201, 202, 204, 206, 207, 300, 301, 302, 303, 304, 305, 307,
            400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416,
            417, 418, 420, 421, 422, 423, 424, 425, 426, 429, 431, 444, 450, 451, 499, 500,
            501, 502, 503, 504, 506, 507, 508, 509, 510, 511, 599]

        if not code in code_list:
            return await ctx.send(
                content="**Invalid code, please type one of these!**", 
                embed=discord.Embed(description=f"```py\n{', '.join(map(lambda e: str(e), code_list))}```"))

        req = f'https://http.cat/{code}'

        try:
            embed = discord.Embed(
            title="__HTTP Cat__",
            url=req)
            embed.set_image(url=req)
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            return await ctx.send("**Something went wrong with it!**")


    @slash_command(name="change_server")
    @commands.has_permissions(administrator=True)
    @utils.is_allowed_members([228296480643874826], throw_exc=True) # Wynnie's ID
    async def _change_server(self, ctx,
        icon: Option(discord.Attachment, name="icon", description="The new server icon.", required=False),
        banner: Option(discord.Attachment, name="banner", description="The new server banner.", required=False)
    ) -> None:
        """ Changes the server's icon and/or banner. """

        await ctx.defer()
        member: discord.Member = ctx.author
        if not icon and not banner:
            return await ctx.respond(f"**Please, inform at least a banner or an icon, {member.mention}!**")

        try:
            if icon and banner:
                await ctx.guild.edit(icon=await icon.read(), banner=await banner.read())
            elif icon:
                await ctx.guild.edit(icon=await icon.read())
            elif banner:
                await ctx.guild.edit(banner=await banner.read())

        except Exception as e:
            print("Error at changing server pics: ", e)
            await ctx.respond(f"**Something went wrong with it, {member.mention}!**")

        else:
            await ctx.respond(f"**Successfully changed the server's pictures, {member.mention}!**")
    
def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(Pictures(client))