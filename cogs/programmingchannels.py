import discord
from discord.ext import commands

class ProgrammingChannels(commands.Cog):
    """ Collection of programming channel related commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("ProgrammingChannels cog is online!")

    @commands.command()
    async def justask(self, ctx):
        """ Posts link to "Don't ask to ask, just ask" """
        await ctx.message.delete()
        em = discord.Embed(color=ctx.author.color, title=f"Don't ask to ask, just ask.",
                           timestamp=ctx.message.created_at, url='https://dontasktoask.com/')
        em.set_footer(text=f"With ♥ from {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

def setup(client):
    client.add_cog(ProgrammingChannels(client))
