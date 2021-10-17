import discord
from discord.app.commands import Option, slash_command
from discord.ext import commands
from random import randint
import aiohttp
import os
from typing import List, Union

from extra import utils, useful_variables
from extra.view import QuickButtons
from mysqldb import the_database
from external_cons import the_reddit

from extra.moderation.userinfractions import ModerationUserInfractionsTable
from extra.moderation.fakeaccounts import ModerationFakeAccountsTable

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
watchlist_channel_id = int(os.getenv('WATCHLIST_CHANNEL_ID'))
slothboard_channel_id = int(os.getenv('SLOTHBOARD_CHANNEL_ID'))
booster_role_id = int(os.getenv('BOOSTER_ROLE_ID'))
guild_ids = [int(os.getenv('SERVER_ID'))]

class Social(commands.Cog):
    """ Social related commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        """ Sends messages to the Slothboard channel. """
        
        emoji = str(payload.emoji)
        star = '<:zzSloth:686237376510689327>'

        # Checkes whether it's the right emoji
        if emoji != star:
            return

        if payload.channel_id == slothboard_channel_id:
            return

        # Gets message
        guild = self.client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message is None:
            return

        # Checks whether the message has enough reactions
        for reaction in message.reactions:
            if str(reaction) != emoji:
                continue

            if reaction.count < 10:
                continue

            # Check whether message is already in the Slothboard
            if not await self.get_slothboard_message(message.id, channel.id):

                # Checks whether message content contains an embedded image
                current_date = await utils.get_time_now()

                embed = discord.Embed(
                    title="__Slothboard__",
                    color=discord.Color.gold(),
                    timestamp=current_date
                )

                # Gets all Discord link attachments
                attachment_root = 'https://cdn.discordapp.com/attachments/'
                content = message.content.split()
                discord_attachments = [att for att in content if att.startswith(attachment_root)]
                for datt in discord_attachments:
                    try:
                        if not embed.image:
                            embed.set_image(url=datt)

                        content.remove(datt)
                    except:
                        pass

                message.content = ' '.join(content).strip() if content else None
                embed.description=f"[**Original Message**]({message.jump_url})\n\n**Content:** {message.content}"

                # Gets all embedded attachments
                if all_attachments := message.attachments:
                    attachments = [att for att in all_attachments if att.content_type.startswith('image')]

                    if attachments:
                        embed.set_image(url=attachments[0])
                    else:
                        return

                embed.set_author(name=message.author, url=message.author.display_avatar, icon_url=message.author.display_avatar)
                # Post in #slothboard
                await self.insert_slothboard_message(message.id, channel.id)
                slothboard_channel = guild.get_channel(slothboard_channel_id)
                return await slothboard_channel.send(content=f"**From:** {channel.mention}", embed=embed)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_slothboard(self, ctx) -> None:
        """ (ADM) Creates the Slothboard table. """

        if await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE Slothboard (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                PRIMARY KEY (message_id, channel_id)
            )""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `Slothboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_slothboard(self, ctx) -> None:
        """ (ADM) Drops the Slothboard table. """

        if not await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Slothboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `Slothboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_slothboard(self, ctx) -> None:
        """ (ADM) Resets the Slothboard table. """

        if not await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Slothboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `Slothboard` table!**")

    async def table_slothboard_exists(self) -> bool:
        """ Checks whether the Slothboard table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Slothboard'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    async def get_slothboard_message(self, message_id: int, channel_id: int) -> List[int]:
        """ Gets a Slothboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Slothboard WHERE message_id = %s AND channel_id = %s", (message_id, channel_id))
        Slothboard_message = await mycursor.fetchone()
        await mycursor.close()
        return Slothboard_message

    async def insert_slothboard_message(self, message_id: int, channel_id: int) -> None:
        """ Inserts a Slothboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel.  """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Slothboard (message_id, channel_id) VALUES (%s, %s)", (
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
    async def userinfo(self, ctx, *, message : str = None):
        """ Shows all the information about a member.
        :param member: The member to show the info.
        :return: An embedded message with the user's information """

        if not await utils.is_allowed([mod_role_id, admin_role_id]).predicate(ctx):
            if len(message.split()) > 1:
                message = message.split()[0]

        members, _ = await utils.greedy_member_reason(ctx, message)

        members = [ctx.author] if not members else members

        for member in members:
            embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at, description=f"\n<@{member.id}>")

            embed.set_author(name=f"User Info: {member}")
            embed.set_thumbnail(url=member.display_avatar)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)

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

            view = QuickButtons(client=self.client, ctx=ctx, target_member=member)
            if not await utils.is_allowed([mod_role_id, admin_role_id]).predicate(ctx):
                view.children.remove(view.children[4])
                view.children.remove(view.infractions_button)
                view.children.remove(view.fake_accounts_button)
            else:
                view.children.remove(view.info_button)
                view.children.remove(view.profile_button)

                if not await ModerationUserInfractionsTable.get_user_infractions(ctx, member.id):
                    view.children[0].disabled = True

                if not await ModerationFakeAccountsTable.get_fake_accounts(ctx, member.id):
                    view.children[1].disabled = True
                
                watchlist = await self.client.get_cog('Moderation').get_user_watchlist(member.id)
                
                if watchlist:
                    message_url = f"https://discord.com/channels/{ctx.guild.id}/{watchlist_channel_id}/{watchlist[1]}"
                    view.children[2].url = message_url
                else:
                    view.children[2].disabled = True

            await ctx.send("\u200b", embed=embed, view=view)


    # Sends a random post from the meme subreddit
    # @commands.command()
    # @commands.cooldown(1, 5, type=commands.BucketType.user)
    # async def meme(self, ctx):
    #     """ Gets a random meme from Reddit.

    #     * Cooldown = 5 secs """

    #     reddit = await the_reddit()
    #     memes_submissions = reddit.subreddit('memes').hot()
    #     post_to_pick = randint(1, 50)
    #     for i in range(0, post_to_pick):
    #         submissions = next(x for x in memes_submissions if not x.stickied)

    #     meme_embed = discord.Embed(title="__**Meme**__", colour=ctx.author.colour, timestamp=ctx.message.created_at)
    #     meme_embed.set_image(url=submissions.url)
    #     meme_embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
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

    @slash_command(name="youtube_together", guild_ids=guild_ids)
    @utils.is_allowed([booster_role_id, *useful_variables.patreon_roles.keys(), mod_role_id, admin_role_id, teacher_role_id], throw_exc=True)
    async def youtube_together(self, ctx,
        voice_channel: Option(discord.abc.GuildChannel, description="The voice channel in which to create the party.")
    ) -> None:
        """ Creates a YouTube Together session in a VC. """

        member = ctx.author

        if not isinstance(voice_channel, discord.VoiceChannel):
            return await ctx.respond(f"**Please, select a `Voice Channel`, {member.mention}!**")

        link: str = ''
        try:
            link = await voice_channel.create_activity_invite(event='youtube', max_age=600)
        except Exception as e:
            print("Invite creation error: ", e)
            await ctx.respond(f"**For some reason I couldn't create it, {member.mention}!**")
        current_time = await utils.get_time_now()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(url=str(link), label="Start/Join the Party!", emoji="🔴"))
        embed = discord.Embed(
            title="__Youtube Together__",
            color=discord.Color.red(),
            timestamp=current_time,
            url=link
        )
        embed.set_author(name=member, url=member.display_avatar, icon_url=member.display_avatar)
        embed.set_footer(text=f"(Expires in 5 minutes)", icon_url=ctx.guild.icon.url)
        await ctx.respond("\u200b", embed=embed, view=view)


def setup(client):
    client.add_cog(Social(client))
