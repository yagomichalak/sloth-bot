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


    
def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(Pictures(client))