import discord
from discord.ext import commands
from mysqldb import the_database
import os
import aiohttp
from extra import utils
import json
import asyncio
from random import choice

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


    @commands.command()
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

    
def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(Pictures(client))