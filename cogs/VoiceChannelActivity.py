import discord
from discord.ext import commands, tasks
from mysqldb import DatabaseCore

from datetime import datetime
from pytz import timezone
import os

from typing import List, Tuple, Union, Optional, Dict, Any
from extra import utils
from extra.menu import PaginatorView
from extra.tool.voice_channel_history import VoiceChannelHistoryTable, VoiceChannelHistorySystem

allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123))]
allowed_roles_and_analysts = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123)), int(os.getenv('ANALYST_DEBUGGER_ROLE_ID', 123))]

tool_cogs: List[commands.Cog] = [
    VoiceChannelHistoryTable, VoiceChannelHistorySystem
]

class VoiceChannelActivity(*tool_cogs):
    """ Category for the users' voice channel activities. """

    def __init__(self, client) -> None:
        """ Cog's initializing method. """

        self.client = client
        self.server_id = int(os.getenv('SERVER_ID', 123))
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to use. """

        self.calculate.start()
        self.check_old_record_deletion_time.start()
        self.check_exceeding_voice_channels_from_history.start()

        print('VoiceChannelActivity cog is online!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ Registers a member whenever they join a channel. """

        # === Checks whether the user just changed their state being in the same VC. ===
        if before.self_mute != after.self_mute:
            return
        if before.self_deaf != after.self_deaf:
            return
        if before.self_stream != after.self_stream:
            return
        if before.self_video != after.self_video:
            return

        if before.mute != after.mute:
            return
        if before.deaf != after.deaf:
            return

        if channel := after.channel:

            tzone = timezone('Europe/Berlin')
            date_and_time = datetime.now().astimezone(tzone)
            the_time = date_and_time.strftime('%H:%M')

            await self.insert_row(the_time, channel.id, channel.name, member.id, member.name)

    @tasks.loop(seconds=60)
    async def calculate(self) -> None:
        """ Calculates all members that are in a voice channel. """
        tzone = timezone('Europe/Berlin')
        date_and_time = datetime.now().astimezone(tzone)
        the_time = date_and_time.strftime('%H:%M')

        print(f'Calculate VC at {the_time}')
        guild = self.client.get_guild(self.server_id)
        channels = [c for c in guild.voice_channels]

        all_channel_members = []

        for channel in channels:
            if channel.members:
                channel_members = [(the_time, channel.id, channel.name, m.id, m.name) for m in channel.members]
                all_channel_members.append(channel_members)

        all_channel_members = [m for c in all_channel_members for m in c]
        if all_channel_members:
            await self.insert_first_row(all_channel_members)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_voice_channel_activity(self, ctx):
        """ Creates the VoiceChannelActivity table. """

        if await self.table_voice_channel_activity_exists():
            return await ctx.send("**The __VoiceChannelActivity__ already exists!**")

        await self.db.execute_query("""
            CREATE TABLE VoiceChannelActivity (
                the_time TIME NOT NULL, channel_id BIGINT NOT NULL,
                channel_name VARCHAR(50) NOT NULL, member_id BIGINT NOT NULL,
                member_name VARCHAR(50) NOT NULL) DEFAULT CHARSET utf8mb4
        """)
        await ctx.send("**Table __VoiceChannelActivity__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_voice_channel_activity(self, ctx):
        """ Drops the VoiceChannelActivity table. """

        if not await self.table_voice_channel_activity_exists():
            return await ctx.send("**The __VoiceChannelActivity__ doesn't exist!**")

        await self.db.execute_query("DROP TABLE VoiceChannelActivity")
        await ctx.send("**Table __VoiceChannelActivity__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_voice_channel_activity(self, ctx):
        """ Resets the VoiceChannelActivity table. """

        if not await self.table_voice_channel_activity_exists():
            return await ctx.send("**The __VoiceChannelActivity__ doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM VoiceChannelActivity")
        await ctx.send("**Table __VoiceChannelActivity__ reset!**")

    async def insert_first_row(self, channel_members: List[Tuple[Union[int, str]]]) -> None:
        """ Inserts the first row of the minute with the info of all users who are in voice channels.
        :param channel_members: A list of tuples containing the individual members and their info. """

        await self.db.execute_query("""
            INSERT INTO VoiceChannelActivity (the_time, channel_id, channel_name, member_id, member_name)
            VALUES (%s, %s, %s, %s, %s)""", channel_members, execute_many=True)

    async def insert_row(self, the_time: datetime, channel_id: int, channel_name: str, member_id: int, member_name: str) -> None:
        """ Inserts a row containing info of member and the voice channel that they're currently in.
        :param the_time: The current time.
        :param: channel_id: The ID channel that the member is in.
        :param channel_name: The name of the channel that the member is in.
        :param member_id: The ID of the member.
        :param member_name: The name of the member. """

        await self.db.execute_query("""
            INSERT INTO VoiceChannelActivity (the_time, channel_id, channel_name, member_id, member_name)
            VALUES (%s, %s, %s, %s, %s)""", (the_time, channel_id, channel_name, member_id, member_name))

    @tasks.loop(seconds=60)
    async def check_old_record_deletion_time(self, limit_hours: int = 6) -> None:
        """ Checks whether it's time to delete old records.
        :param limit_hours: The limit of hours that the DB needs to store,
        PS: If the number of registered hours in the DB is exceeded, the oldest records will be deleted,
        so the limit is satisfied again. """

        hours = await self.db.execute_query("SELECT DISTINCT HOUR(the_time) FROM VoiceChannelActivity", fetch="all")
        hours = [h[0] for h in hours]

        if limit_hours < len(hours):
            await self.db.execute_query("DELETE FROM VoiceChannelActivity WHERE HOUR(the_time) = %s", (hours.pop(0),))

    async def get_hour_record_by_channel(self, channel: discord.TextChannel, time: str, time2: str = None) -> List[List[Union[datetime, str, int]]]:
        """ Gets all user records at a given hour and channel.
        :param channel_id: The ID of the channel to which you are filtering.
        :param time: The time to which you are filtering the search. """

        records = []
        text = ""

        if len(time) < 3:
            time = datetime.strptime(time, '%H')

            # Checks whether user provided two values
            if time2:
                time2 = datetime.strptime(time2, '%H')
                records = await self.db.execute_query("""
                    SELECT DISTINCT HOUR(the_time), member_name, member_id
                    FROM VoiceChannelActivity WHERE channel_id = %s AND HOUR(the_time) BETWEEN %s AND %s""",
                    (channel.id, time.hour, time2.hour), fetch="all")

                text = f"Users who joined `{channel}` between `{time.hour}:00` and `{time2.hour}:59`:"
            else:
                records = await self.db.execute_query("""
                    SELECT DISTINCT HOUR(the_time), member_name, member_id
                    FROM VoiceChannelActivity WHERE channel_id = %s AND HOUR(the_time) = %s""",
                    (channel.id, time.hour), fetch="all")

                text = f"Users who joined `{channel}` between `{time.hour}:00` and `{time.hour}:59`:"

        else:
            time = datetime.strptime(time, '%H:%M')

            # Checks whether two values were passed
            if time2:
                time2 = datetime.strptime(time2, '%H:%M')
                the_time1 = f"{time.hour}:{time.minute}"
                the_time2 = f"{time2.hour}:{time2.minute}"

                text = f"Users who joined `{channel}` between `{the_time1}` and `{the_time2}`:"

                records = await self.db.execute_query("""
                    SELECT DISTINCT the_time, member_name, member_id
                    FROM VoiceChannelActivity WHERE channel_id = %s AND the_time BETWEEN %s AND %s""",
                    (channel.id, the_time1, the_time2), fetch="all")

            # If not, assumes the second value
            else:
                if time.minute >= 0 and time.minute <= 29:
                    the_time1 = f"{time.hour}:00"
                    the_time2 = f"{time.hour}:29"
                else:
                    the_time1 = f"{time.hour}:30"
                    the_time2 = f"{time.hour}:59"

                text = f"Users who joined `{channel}` between `{the_time1}` and `{the_time2}`:"
                records = await self.db.execute_query("""
                    SELECT DISTINCT the_time, member_name, member_id
                    FROM VoiceChannelActivity WHERE channel_id = %s AND the_time BETWEEN %s AND %s""",
                    (channel.id, the_time1, the_time2), fetch="all")

        return records, time, text

    async def get_user_record_by_time(self, member: discord.Member, time: str, time2: str = None) -> List[Union[int, str]]:
        """ Gets user records by the given hour.
        :param member: The member from whom you want to fetch information.
        :param time: The time at around the user that you are looking for has to have information. """

        records = []
        text = ""

        # If in format (HOUR)
        if len(time) < 3:
            time = datetime.strptime(time, '%H')
            # Checks whether user provided two values
            if time2:
                time2 = datetime.strptime(time2, '%H')
                records = await self.db.execute_query("""
                    SELECT DISTINCT HOUR(the_time), channel_id, channel_name,  member_id
                    FROM VoiceChannelActivity WHERE HOUR(the_time) BETWEEN %s AND %s AND member_id = %s""",
                    (time.hour, time2.hour, member.id), fetch="all")

                text = f"User between `{time.hour}` and `{time2.hour}` was in:"

            # If not, gets all values from that hour.
            else:
                records = await self.db.execute_query("""
                    SELECT DISTINCT HOUR(the_time), channel_id, channel_name,  member_id
                    FROM VoiceChannelActivity WHERE HOUR(the_time) = %s AND member_id = %s""",
                    (time.hour, member.id), fetch="all")

                text = f"User between `{time.hour}` and `{time.hour}` was in:"

        else:
            # If in format (HOUR:MINUTE)
            time = datetime.strptime(time, '%H:%M')

            # Checks whether user provided two values
            if time2:
                time2 = datetime.strptime(time2, '%H:%M')
                the_time1 = f"{time.hour}:{time.minute}"
                the_time2 = f"{time2.hour}:{time2.minute}"

                records = await self.db.execute_query("""
                    SELECT DISTINCT the_time, channel_id, channel_name, member_id
                    FROM VoiceChannelActivity
                    WHERE the_time BETWEEN %s AND %s AND member_id = %s""",
                    (the_time1, the_time2, member.id), fetch="all")

                text = f"{member} between `{the_time1}` and `{the_time2}` was in:"

            # If not, gets values from either (HOUR:00 - HOUR:29) or (HOUR:30 - HOUR:59)
            else:
                # If it's between HOUR:00 and HOUR:29
                if time.minute >= 0 and time.minute <= 29:
                    the_time1 = f"{time.hour}:00"
                    the_time2 = f"{time.hour}:29"
                    text = f"{member} between `{the_time1}` and `{the_time2}` was in:"

                # If it's between HOUR:30 and HOUR:30
                else:
                    the_time1 = f"{time.hour}:30"
                    the_time2 = f"{time.hour}:59"
                    text = f"{member} between `{the_time1}` and `{the_time2}` was in:"

                records = await self.db.execute_query("""
                    SELECT DISTINCT the_time, channel_id, channel_name, member_id
                    FROM VoiceChannelActivity
                    WHERE the_time BETWEEN %s AND %s AND member_id = %s""",
                    (the_time1, the_time2, member.id), fetch="all")

        return records, time, text

    async def format_time(self, time: str) -> str:
        """ Formats the time if needed.
        :param time: The time you want to format. """

        formated_time = time
        if len(time) == 3 and time[2] == ':':
            formated_time = time.replace(':', '')

        return formated_time

    @commands.command(aliases=['whj', 'wj1', 'whojoined', 'whoj', 'who', 'quem'])
    @commands.has_any_role(*allowed_roles)
    async def who_joined(self, ctx, channel: discord.VoiceChannel = None, time: str = None, time2: str = None) -> None:
        """ Shows which members were in the given voice channel at the given time:
        :param channel: The channel you want to check.
        :param time: The time. """

        if not channel:
            return await ctx.send("**Hey, inform a channel to fetch users from!**")

        if not time:
            return await ctx.send("**Yo, inform a time!**")

        time = await self.format_time(time)
        time2 = await self.format_time(time2) if time2 else None

        records, ftime, text = await self.get_hour_record_by_channel(channel, time, time2)
        if not records:
            return await ctx.send("**Nothing found for the given channel and/or time!**")

        users = set([m.mention if (m := discord.utils.get(ctx.guild.members, id=member[2])) else member[1] for member in records])

        embed = discord.Embed(
            title=text,
            description=f"{', '.join(users)}"
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=['wherejoined', 'joined_where', 'wj2', 'where', 'onde'])
    @commands.has_any_role(*allowed_roles)
    async def where_joined(self, ctx, member: discord.Member = None, time: str = None, time2: str = None) -> None:
        """ Shows in which voice channel a specific user was at a given time:
        :param member: The member you want to check.
        :param time: The time. """

        if not member:
            return await ctx.send("**Hey, inform a channel to fetch users from!**")

        if time is None:
            return await ctx.send("**Yo, inform a time!**")

        time = await self.format_time(time)
        time2 = await self.format_time(time2) if time2 else None

        records, ftime, text = await self.get_user_record_by_time(member, time, time2)

        if not records:
            return await ctx.send("**Nothing found for the given time and/or member!**")

        channels = set([c.mention if (c := discord.utils.get(ctx.guild.channels, id=channel[1])) else channel[2] for channel in records])

        embed = discord.Embed(
            title=text,
            description=f"{', '.join(channels)}"
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=['vh'])
    @utils.is_allowed(allowed_roles_and_analysts, throw_exc=True)
    async def voice_history(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Shows the Voice Channel history of a member.
        :param member: The member from whom to see the history. [Optional][Default = You] """

        author: discord.Member = ctx.author

        if not member:
            member = ctx.author

        channels_in_history = await self.get_voice_channel_history(member.id)
        if not channels_in_history:
            if author == member:
                return await ctx.send(f"**You don't have any Voice Channels in the history, {member.mention}!**")
            else:
                return await ctx.send(f"**This user doesn't have any Voice Channels in the history, {member.mention}!**")

        if not channels_in_history:
            if author == member:
                return await ctx.send(f"**You don't have any Voice Channels in your history, {author.mention}!**")
            else:
                return await ctx.send(f"**{member.mention} doesn't have any Voice Channels in their history, {author.mention}!**")

        # Additional data:
        additional = {
            'client': self.client,
            'change_embed': self.make_voice_history_embed,
            'target': member
        }
        view = PaginatorView(channels_in_history, increment=6, **additional)
        embed = await view.make_embed(member)
        await ctx.send(embed=embed, view=view)
        return embed

    async def make_voice_history_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any, 
        offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None, **kwargs: Dict[str, Any]) -> discord.Embed:
        """ Makes an embed for .
        :param req: The request URL link.
        :param member: The member who triggered the command.
        :param search: The search that was performed.
        :param example: The current search example.
        :param offset: The current page of the total entries.
        :param lentries: The length of entries for the given search. """

        current_time = await utils.get_time_now()
        target = kwargs.get("target")
        if not target:
            target = member

        # Makes the embed's header
        embed = discord.Embed(
            title=f"__Voice Channel History__ ({offset}/{lentries})",
            color=target.color,
            timestamp=current_time
        )

        description_list = []

        for i in range(0, 6, 1):
            if offset - 1 + i < lentries:
                entry = entries[offset-1 + i]
                if entry[1] == 'switch':
                    description_list.append(f"(**{entry[1]}**) <#{entry[3]}> **->** <#{entry[4]}>  <t:{entry[2]}>")
                else:
                    description_list.append(f"(**{entry[1]}**) <#{entry[3]}> <t:{entry[2]}>")
            else:
                break

        embed.description = '\n'.join(description_list)

        # Sets the author of the search
        embed.set_author(name=target, icon_url=target.display_avatar)
        # Makes a footer with the a current page and total page counter
        embed.set_footer(text=f"Requested by {target}", icon_url=target.display_avatar)

        return embed        


def setup(client) -> None:
    client.add_cog(VoiceChannelActivity(client))
