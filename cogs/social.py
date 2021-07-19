import discord
from discord.ext import commands
import praw
from random import randint
import aiohttp
import os
from typing import List
from extra import utils

reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),  # client id
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),  # my client secret
                     user_agent=os.getenv('USER_AGENT'),  # my user agent. It can be anything
                     username='',  # Not needed
                     password='')  # Not needed

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))


class Social(commands.Cog):
    '''
    Social related commands.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')


    @commands.Cog.listener()
    async def on_interaction_update(self, message, member, button, response) -> None:
        """ Handles button clicks in the quick button menu in the z!userinfo command. """

        custom_id = button.custom_id
        for c_id in ["user_infractions", "user_profile", "user_info"]:
            if custom_id.startswith(c_id):
                break
        else:
            return

        button.ping(response)


        ctx = await self.client.get_context(message)
        target_member = discord.utils.get(message.guild.members, id=int(button.custom_id.split(':', 1)[1]))
        
        if custom_id.startswith('user_infractions'):
            if await Social.is_allowed(ctx, [mod_role_id, admin_role_id]):
                return await self.client.get_cog("Moderation").infractions(ctx=ctx, member=target_member)
            
        elif custom_id.startswith("user_profile"):
            await self.client.get_cog("SlothCurrency").profile(ctx=ctx, member=target_member)

        elif custom_id.startswith("user_info"):
            await self.client.get_cog("SlothReputation").info(ctx=ctx, member=target_member)

    @commands.command(aliases=['si', 'server'])
    async def serverinfo(self, ctx) -> None:
        """ Shows information about the server. """

        guild = ctx.guild

        em = discord.Embed(description=guild.description, color=ctx.author.color)
        online = len({m.id for m in guild.members if m.status is not discord.Status.offline})
        em.add_field(name="Server ID", value=guild.id, inline=True)
        em.add_field(name="Owner", value=guild.owner.mention, inline=False)

        admins_role = discord.utils.get(guild.roles, id=admin_role_id)
        admins = len([m.mention for m in guild.members if admins_role in m.roles])
        em.add_field(name="👑 Admins", value=admins, inline=True)

        mods_role = discord.utils.get(guild.roles, id=mod_role_id)
        mods = len([m.mention for m in guild.members if mods_role in m.roles])
        em.add_field(name="<:zslothmod:737325517077872697> Mods", value=mods, inline=True)

        teachers_role = discord.utils.get(guild.roles, id=teacher_role_id)
        teachers = len([m.mention for m in guild.members if teachers_role in m.roles])
        em.add_field(name="🧑‍🏫 Teachers", value=teachers, inline=True)

        em.add_field(name="Members", value=f"🟢 {online} members ⚫ {len(guild.members)} members", inline=True)
        em.add_field(name="Channels",
            value=f"⌨️ {len(guild.text_channels)} | 🔈 {len(guild.voice_channels)} | 📻 {len(guild.stage_channels)} | 📁 {len(guild.categories)} | **=** {len(guild.channels)}",
            inline=False)
        em.add_field(name="Roles", value=len(guild.roles), inline=True)
        em.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        em.add_field(name="🌐 Region", value=str(guild.region).title() if guild.region else None, inline=True)
        em.add_field(name="<:ban:593407893248802817> Bans", value=len(await guild.bans()), inline=True)
        em.add_field(name="🌟 Boosts", value=f"{guild.premium_subscription_count} (Level {guild.premium_tier})", inline=True)
        features = ', '.join(list(map(lambda f: f.replace('_', ' ').capitalize(), guild.features)))
        em.add_field(name="Server Features", value=features if features else None, inline=False)

        em.set_thumbnail(url=guild.icon.url)
        em.set_image(url=guild.banner_url)
        em.set_author(name=guild.name, icon_url=guild.icon.url)
        created_at = await utils.sort_time(guild.created_at)
        em.set_footer(text=f"Created: {guild.created_at.strftime('%d/%m/%y')} ({created_at})")
        await ctx.send(embed=em)

    # Shows all the info about a user
    @commands.command(aliases=['user', 'whois', 'who_is'])
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
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(name="Guild name:", value=member.display_name, inline=False)

        sorted_time_create = f"<t:{int(member.created_at.timestamp())}:R>"
        sorted_time_join = f"<t:{int(member.joined_at.timestamp())}:R>"

        embed.add_field(name="Created at:", value=f"{member.created_at.strftime('%d/%m/%y')} ({sorted_time_create}) **GMT**",
						inline=False)
        embed.add_field(name="Joined at:", value=f"{member.joined_at.strftime('%d/%m/%y')} ({sorted_time_join}) **GMT**", inline=False)

        embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)

        embed.add_field(name="Bot?", value=member.bot)


        component = discord.Component()
        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(ctx):
            component.add_button(label="See Infractions", style=4, emoji="❗", custom_id=f"user_infractions:{member.id}")
        
        component.add_button(label="See Profile", style=1, emoji="👤", custom_id=f"user_profile:{member.id}")
        component.add_button(label="See Info", style=2, emoji="ℹ️", custom_id=f"user_info:{member.id}")

        await ctx.send(embed=embed, components=[component])


    @staticmethod
    async def is_allowed(ctx: commands.Context, roles: List[int]) -> bool:
        """ Checks whether the member has adm perms or has an allowed role. """

        perms = ctx.channel.permissions_for(ctx.author)

        if perms.administrator:
            return True

        for rid in roles:
            if rid in [role.id for role in ctx.author.roles]:
                return True

        else:
            return False

        
        

        


    # Sends a random post from the meme subreddit
    # @commands.command()
    # @commands.cooldown(1, 5, type=commands.BucketType.user)
    # async def meme(self, ctx):
    #     '''
    #     Gets a random meme from Reddit.
    #     (cooldown = 5 secs)
    #     '''
    #     memes_submissions = reddit.subreddit('memes').hot()
    #     post_to_pick = randint(1, 50)
    #     for i in range(0, post_to_pick):
    #         submissions = next(x for x in memes_submissions if not x.stickied)

    #     meme_embed = discord.Embed(title="__**Meme**__", colour=ctx.author.colour, timestamp=ctx.message.created_at)
    #     meme_embed.set_image(url=submissions.url)
    #     meme_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
    #     await ctx.send(embed=meme_embed)

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
