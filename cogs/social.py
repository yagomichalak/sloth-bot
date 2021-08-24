import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions
from discord.utils import maybe_coroutine
import praw
from random import randint
import aiohttp
import os
from typing import List, Union
from extra import utils
from extra.view import QuickButtons
from mysqldb import the_database


reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),  # client id
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),  # my client secret
                     user_agent=os.getenv('USER_AGENT'),  # my user agent. It can be anything
                     username='',  # Not needed
                     password='')  # Not needed

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
watchlist_channel_id = int(os.getenv('WATCHLIST_CHANNEL_ID'))
starboard_channel_id = int(os.getenv('STARBOARD_CHANNEL_ID'))

class Social(commands.Cog):
    """ Social related commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        """ Sends messages to the starboard channel. """
        
        emoji = str(payload.emoji)
        star = '<:zzSloth:686237376510689327>'

        # Checkes whether it's the right emoji
        if emoji != star:
            return

        if payload.channel_id == starboard_channel_id:
            return

        # Gets message
        guild = self.client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if not message:
            return

        # Checks whether the message has enough reactions
        for reaction in message.reactions:
            if str(reaction) != emoji:
                continue

            if reaction.count < 10:
                continue

            if not await self.get_starboard_message(message.id, channel.id):
                # Post in #starboard
                current_date = await utils.get_time_now()
                embed = discord.Embed(
                    title="__Starboard__",
                    description=message.content,
                    color=discord.Color.gold(),
                    timestamp=current_date
                )

                if all_attachments := message.attachments:
                    attachments = [att for att in all_attachments if att.content_type.startswith('image')]
                    if attachments:
                        embed.set_image(url=attachments[0])
                    else:
                        return

                embed.set_author(name=message.author, url=message.author.avatar.url, icon_url=message.author.avatar.url)

                await self.insert_starboard_message(message.id, channel.id)
                starboard_channel = guild.get_channel(starboard_channel_id)
                return await starboard_channel.send(content=f"**From:** {channel.mention}", embed=embed)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_starboard(self, ctx) -> None:
        """ (ADM) Creates the Starboard table. """

        if await self.table_starboard_exists():
            return await ctx.send("**The `Starboard` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE Starboard (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                PRIMARY KEY (message_id, channel_id)
            )""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `Starboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_starboard(self, ctx) -> None:
        """ (ADM) Drops the Starboard table. """

        if not await self.table_starboard_exists():
            return await ctx.send("**The `Starboard` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Starboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `Starboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_starboard(self, ctx) -> None:
        """ (ADM) Resets the Starboard table. """

        if not await self.table_starboard_exists():
            return await ctx.send("**The `Starboard` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Starboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `Starboard` table!**")

    async def table_starboard_exists(self) -> bool:
        """ Checks whether the Starboard table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Starboard'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    async def get_starboard_message(self, message_id: int, channel_id: int) -> List[int]:
        """ Gets a starboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Starboard WHERE message_id = %s AND channel_id = %s", (message_id, channel_id))
        starboard_message = await mycursor.fetchone()
        await mycursor.close()
        return starboard_message

    async def insert_starboard_message(self, message_id: int, channel_id: int) -> None:
        """ Inserts a starboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel.  """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Starboard (message_id, channel_id) VALUES (%s, %s)", (
            message_id, channel_id))
        await db.commit()
        await mycursor.close()


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
        if guild.banner:
            em.set_image(url=guild.banner.url)
        em.set_author(name=guild.name, icon_url=guild.icon.url)
        created_at = await utils.sort_time(guild.created_at)
        em.set_footer(text=f"Created: {guild.created_at.strftime('%d/%m/%y')} ({created_at})")
        await ctx.send(embed=em)

    # Shows all the info about a user
    @commands.command(aliases=['user', 'whois', 'who_is'])
    async def userinfo(self, ctx, member: Union[discord.Member, discord.User] = None):
        '''
        Shows all the information about a member.
        :param member: The member to show the info.
        :return: An embedded message with the user's information
        '''
        member = ctx.author if not member else member

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_author(name=f"User Info: {member}")
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        embed.add_field(name="ID:", value=member.id, inline=False)

        if hasattr(member, 'guild'):
            embed.add_field(name="Guild name:", value=member.display_name, inline=False)
            sorted_time_create = f"<t:{int(member.created_at.timestamp())}:R>"
            sorted_time_join = f"<t:{int(member.joined_at.timestamp())}:R>"

            embed.add_field(name="Created at:", value=f"{member.created_at.strftime('%d/%m/%y')} ({sorted_time_create}) **GMT**",
                            inline=False)
            embed.add_field(name="Joined at:", value=f"{member.joined_at.strftime('%d/%m/%y')} ({sorted_time_join}) **GMT**", inline=False)

            embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)

        embed.add_field(name="Bot?", value=member.bot)

        
        view = QuickButtons(self.client, ctx, member)
        if not await utils.is_allowed([mod_role_id, admin_role_id]).predicate(ctx):
            view.children.remove(view.infractions_button)
            view.children.remove(view.fake_accounts_button)
            view.children.remove(view.children[4])
        else:
            watchlist = await self.client.get_cog('Moderation').get_user_watchlist(member.id)
            if watchlist:
                message_url = f"https://discord.com/channels/{ctx.guild.id}/{watchlist_channel_id}/{watchlist[1]}"
                view.children[4].url = message_url
            else:
                view.children[4].disabled = True

        await ctx.send(embed=embed, view=view)


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
        """ Get a comic from xkcd. """

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
