import discord
from discord.ext import commands
import praw
from random import randint
import aiohttp
import os

reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),  # client id
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),  # my client secret
                     user_agent=os.getenv('USER_AGENT'),  # my user agent. It can be anything
                     username='',  # Not needed
                     password='')  # Not needed


class Social(commands.Cog):
    '''
    Social related commands.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')

    @commands.command(aliases=['si', 'server'])
    async def serverinfo(self, ctx):
        '''
        Shows some information about the server.
        '''
        await ctx.message.delete()
        guild = ctx.guild
        guild_age = (ctx.message.created_at - guild.created_at).days
        created_at = f"Server created on {guild.created_at.strftime('%b %d %Y at %H:%M')}. That\'s over {guild_age} days ago!"
        color = discord.Color.green()

        em = discord.Embed(description=created_at, color=color)
        em.add_field(name='Online Members',
                     value=len({m.id for m in guild.members if m.status is not discord.Status.offline}))
        em.add_field(name='Total Members', value=len(guild.members))
        em.add_field(name='Text Channels', value=len(guild.text_channels))
        em.add_field(name='Voice Channels', value=len(guild.voice_channels))
        em.add_field(name='Roles', value=len(guild.roles))
        em.add_field(name='Owner', value=guild.owner)

        em.set_thumbnail(url=None or guild.icon_url)
        em.set_author(name=guild.name, icon_url=None or guild.icon_url)
        await ctx.send(embed=em)

    # Shows all the info about a user
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        '''
        Shows all the information about a member.
        :param member: The member to show the info.
        :return: An embedded message with the user's information
        '''
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
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def meme(self, ctx):
        '''
        Gets a random meme from Reddit.
        (cooldown = 5 secs)
        '''
        memes_submissions = reddit.subreddit('memes').hot()
        post_to_pick = randint(1, 50)
        for i in range(0, post_to_pick):
            submissions = next(x for x in memes_submissions if not x.stickied)


        meme_embed = discord.Embed(title="__**Meme**__", colour=ctx.author.colour, timestamp=ctx.message.created_at)
        meme_embed.set_image(url=submissions.url)
        meme_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=meme_embed)


    @commands.command(aliases=['xkcd', 'comic'])
    async def randomcomic(self, ctx):
        '''Get a comic from xkcd.'''
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/info.0.json') as resp:
                data = await resp.json()
                currentcomic = data['num']
        rand = randint(0, currentcomic)  # max = current comic
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/{rand}/info.0.json') as resp:
                data = await resp.json()
        em = discord.Embed(color=discord.Color.green())
        em.title = f"XKCD Number {data['num']}- \"{data['title']}\""
        em.set_footer(text=f"Published on {data['month']}/{data['day']}/{data['year']}")
        em.set_image(url=data['img'])
        await ctx.send(embed=em)

        
def setup(client):
    client.add_cog(Social(client))
