import discord
from discord.errors import NotFound
from discord.ext import commands, tasks
import os
from extra import utils
from mysqldb import the_database
from typing import List, Union
import json
from random import choice

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
announcement_channel_id = int(os.getenv('ANNOUNCEMENT_CHANNEL_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
senior_mod_role_id = int(os.getenv('SENIOR_MOD_ROLE_ID'))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), mod_role_id]
general_channel_id = int(os.getenv('GENERAL_CHANNEL_ID'))
lesson_manager_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))
real_event_manager_role_id = int(os.getenv('REAL_EVENT_MANAGER_ROLE_ID'))

class Communication(commands.Cog):
    """ A cog related to communication commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        self.advertise_patreon.start()
        print('Communication cog is ready!')

    @tasks.loop(seconds=60)
    async def advertise_patreon(self) -> None:
        """ Checks the time for advertising Patreon. """

        current_ts = await utils.get_timestamp()
        # Checks whether Patreon advertising event exists
        if not await self.get_advertising_event(event_label='patreon_ad'):
            # If not, creates it
            return await self.insert_advertising_event(event_label='patreon_ad', current_ts=current_ts-14400)

        # Checks whether advertising time is due
        if await self.check_advertising_time(
            current_ts=int(current_ts), event_label="patreon_ad", ad_time=14400):
            # Updates time and advertises.
            await self.update_advertising_time(event_label="patreon_ad", current_ts=current_ts)
            general_channel = self.client.get_channel(general_channel_id)

            data = {}
            with open('./extra/random/json/patreon_ads.json', 'r', encoding="utf-8") as f:
                data = json.loads(f.read())
            
            random_message = choice(list(data.values()))
            await general_channel.send(random_message)


    # Says something by using the bot
    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def say(self, ctx):
        """ (MOD) Makes the bot say something. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split('!say', 1)
        await ctx.send(msg[1])


    # Edits a message sent by the bot
    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def edit(self, ctx, message_id : int = None, *, text : str = None):
        """ (Mod) Edits a message sent by the bot.
        :param nessage_id: The message id."""

        await ctx.message.delete()

        if not message_id:
            return await ctx.send("**Please, insert a message id**", delete_after=3)

        if not text:
            return await ctx.send("**Please, insert a message**", delete_after=3)
        
        channel = ctx.message.channel
        
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(text)

        except NotFound:
            return await ctx.send("**Message not found. Send the command in the same channel as the original message.**", delete_after=5)



    # Replies a message by using the bot
    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def reply(self, ctx, message_id : int = None, *, text : str = None):
        """ (Mod) Replies a message with the bot.
        :param message_id: The message id to reply.
        :param message: The message to send"""

        await ctx.message.delete()

        if not message_id:
            return await ctx.send("**Please, insert a message id to reply to it**", delete_after=3)
        
        if not text:
            return await ctx.send("**Please, insert a message**", delete_after=3)

        channel = ctx.message.channel
        
        try:
            message = await channel.fetch_message(message_id)
            await message.reply(text)

        except NotFound:
            return await ctx.send("**Message not found. Send the command in the same channel as the original message.**", delete_after=5)


    # Spies a channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spy(self, ctx, cid):
        """ (ADM) Makes the bot send a message to a given channel.
        :param cid: The ID of the channel. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 3:
            return await ctx.send('You must inform all parameters!')

        spychannel = self.client.get_channel(int(cid))
        msg = ctx.message.content.split(cid)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await spychannel.send(embed=embed)

    # Welcomes an user by telling them to assign a role
    @commands.command()
    @commands.has_any_role(474774889778380820, 574265899801116673, 699296718705000559)
    async def welcome(self, ctx, member: discord.Member = None):
        """ (WELCOMER) Welcomes a user.
        :param member: The member to welcome. """

        await ctx.message.delete()
        if not member:
            return await ctx.send('Inform a member!')

        bots_and_commands_channel = discord.utils.get(ctx.guild.channels, id=bots_and_commands_channel_id)
        await bots_and_commands_channel.send(
            f'''__**Welcome to the Language Sloth**__! {member.mention}
This is a community of people who are practicing and studying languages from all around the world! While you're here, you will also make tons of new friends! There is a lot to do here in the server but there are some things you should do to start off.

1. Make sure you go check out the <#688967996512665655> and the informations page. These rules are very important and are taken seriously here on the server.
2. After you have finished reading those, you can assign yourself some roles at <#679333977705676830> <#683987207065042944> <#688037387561205824> and <#562019509477703697>! These roles will give you access to different voice and text channels! To choose your role click on the flag that best represents your native language.

If you have any questions feel free to ask! And if you experience any type of problem make sure you let a staff member know right away''')

    # Pretends that a role has been given to an user by the bot
    @commands.command()
    @commands.has_any_role(474774889778380820, 574265899801116673, 699296718705000559)
    async def auto(self, ctx, member: discord.Member = None, language: str = None):
        """ (WELCOMER) Makes the bot send an 'automatic' message to someone.
        :param member: The member:
        :param  language: The language. """

        await ctx.message.delete()
        if not language:
            return await ctx.send('**Inform a language!**', delete_after=3)

        elif not member:
            return await ctx.send('**Inform a member!**', delete_after=3)

        bots_and_commands_channel = discord.utils.get(ctx.guild.channels, id=bots_and_commands_channel_id)
        await bots_and_commands_channel.send(
            f'''{member.mention} - Hey! since you didn't assign your native language I went ahead and assigned it for you automatically based on my best guess of what is your native language, I came to the conclusion that it is {language.title()}.  If I'm incorrect please let me know!''')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        """ (ADM) Announces a message in the announcements channel using the bot. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        announce_channel = discord.utils.get(ctx.guild.channels, id=announcement_channel_id)
        msg = ctx.message.content.split('!announce', 1)
        await announce_channel.send(msg[1])

    @commands.command()
    @utils.is_allowed([senior_mod_role_id, lesson_manager_role_id, real_event_manager_role_id], throw_exc=True)
    async def dm(self, ctx, member: discord.Member = None, *, message=None):
        """ (SeniorMod) Sends a Direct Message to someone.
        :param member: The member to send the message to.
        :param message: The message to send. """

        await ctx.message.delete()
        author: discord.Member = ctx.author

        if not message:
            return await ctx.send("**Inform a message to send!**", delete_after=3)

        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        check_member = ctx.guild.get_member(member.id)
        if not check_member:
            return await ctx.send(f"**Member: {member} not found!", delete_after=3)

        try:
            await member.send(message)
        except:
            pass

        # Moderation log
        if demote_log := discord.utils.get(ctx.guild.text_channels, id=int(os.getenv('DM_LOG_CHANNEL_ID'))):
            dm_embed = discord.Embed(
                title="__DM Message__",
                description=f"{author.mention} DM'd {member.mention}.\n**Message:** {message}",
                color=author.color,
                timestamp=ctx.message.created_at
            )
            dm_embed.set_author(name=member, icon_url=member.display_avatar)
            dm_embed.set_footer(text=f"Sent by: {author}", icon_url=author.display_avatar)
            await demote_log.send(embed=dm_embed)



    # Database


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_scheduled_events(self, ctx: commands.Context) -> None:
        """ Creates the ScheduledEvents table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_scheduled_events_exists():
            return await ctx.send(f"**Table `ScheduledEvents` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE ScheduledEvents (
                event_label VARCHAR(100) NOT NULL,
                event_ts BIGINT NOT NULL,
                PRIMARY KEY (event_label)
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `ScheduledEvents` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_scheduled_events(self, ctx: commands.Context) -> None:
        """ Creates the ScheduledEvents table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_scheduled_events_exists():
            return await ctx.send(f"**Table `ScheduledEvents` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE ScheduledEvents")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `ScheduledEvents` dropped, {member.mention}!**")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_scheduled_events(self, ctx: commands.Context) -> None:
        """ Creates the ScheduledEvents table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_scheduled_events_exists():
            return await ctx.send(f"**Table `ScheduledEvents` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ScheduledEvents")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `ScheduledEvents` reset, {member.mention}!**")

    async def check_scheduled_events_exists(self) -> bool:
        """ Checks whether the ScheduledEvents table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'ScheduledEvents'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def check_advertising_time(self, current_ts: int, event_label: str, ad_time: int) -> bool:
        """ Checks whether the advertising time is due.
        :param current_ts: The current timestamp.
        :param event_label: The label of the event
        :param ad_time: Advertising time cooldown. """

        mycursor, _ = await the_database()
        await mycursor.execute("""
            SELECT * from ScheduledEvents
            WHERE event_label = %s AND %s - event_ts >= %s
        """, (event_label, current_ts, ad_time))
        
        due_event = await mycursor.fetchone()
        await mycursor.close()
        if due_event:
            return True
        else:
            return False

    async def get_advertising_event(self, event_label: str) -> List[Union[str, int]]:
        """ Gets an advertising event.
        :param event_label: The label of the advertising event. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM ScheduledEvents WHERE event_label = %s", (event_label,))
        event = await mycursor.fetchone()
        await mycursor.close()
        return event

    async def insert_advertising_event(self, event_label: str, current_ts: int) -> None:
        """ Inserts an advertising event.
        :param event_label: The label of the advertising event.
        :param current_ts: The timestamp in which it was inserted. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO ScheduledEvents (event_label, event_ts) VALUES (%s, %s)", (event_label, current_ts))
        await db.commit()
        await mycursor.close()

    async def update_advertising_time(self, event_label: str, current_ts: int) -> None:
        """ Updates the timestamp of the advertising event.
        :param event_label: The label of the advertising event.
        :param current_ts: The timestamp to update the event to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ScheduledEvents SET event_ts = %s WHERE event_label = %s", (current_ts, event_label))
        await db.commit()
        await mycursor.close()

def setup(client):
    """ Cog's setup function. """

    client.add_cog(Communication(client))
