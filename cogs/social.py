import discord
from discord.ext import commands
import praw
import random

reddit = praw.Reddit(client_id='Ph3swv14_OMx7w',  # client id
                     client_secret='tmDpbL1xeJAoIrroDH0yS_lf4sU',  # my client secret
                     user_agent='prawautomate123',  # my user agent. It can be anything
                     username='',  # Not needed
                     password='')  # Not needed


class Social(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')

    # Shows all the info about a user
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        roles = [role for role in member.roles]

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_author(name=f"User Info: {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(name="Guild name:", value=member.display_name, inline=False)

        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %d %B %y, %I %M %p UTC"),
                        inline=False)
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)

        embed.add_field(name=f"Roles: {len(roles)}", value=" ".join([role.mention for role in roles]), inline=False)
        embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)

        embed.add_field(name="Bot?", value=member.bot)

        await ctx.send(embed=embed)

    # Sends a random post from the meme subreddit
    @commands.command()
    async def meme(self, ctx):
        '''
        Gets a random meme from Reddit.
        '''
        memes_submissions = reddit.subreddit('memes').hot()
        post_to_pick = random.randint(1, 50)
        for i in range(0, post_to_pick):
            submissions = next(x for x in memes_submissions if not x.stickied)


        meme_embed = discord.Embed(title="__**Meme**__", colour=ctx.author.colour, timestamp=ctx.message.created_at)
        meme_embed.set_image(url=submissions.url)
        meme_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=meme_embed)


def setup(client):
    client.add_cog(Social(client))
