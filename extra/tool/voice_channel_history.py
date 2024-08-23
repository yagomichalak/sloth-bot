# import.standard
from typing import List, Optional, Union

# import.thirdparty
from discord.ext import commands, tasks

# import.local
from extra import utils
from mysqldb import DatabaseCore

class VoiceChannelHistoryTable(commands.Cog):
    """ Class for managing the VoiceChannelHistory table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author

        if await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
            CREATE TABLE VoiceChannelHistory (
                user_id BIGINT NOT NULL,
                action_label VARCHAR(6) NOT NULL,
                action_ts BIGINT NOT NULL,
                vc_id BIGINT NOT NULL,
                vc2_id BIGINT DEFAULT NULL
            )""")

        await ctx.send(f"**Table `VoiceChannelHistory` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author
        
        if not await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE VoiceChannelHistory")

        await ctx.send(f"**Table `VoiceChannelHistory` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author
        
        if not await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM VoiceChannelHistory")

        await ctx.send(f"**Table `VoiceChannelHistory` reset, {member.mention}!**")

    async def check_voice_channel_history_exists(self) -> bool:
        """ Checks whether the VoiceChannelHistory table exists. """

        return await self.db.table_exists("VoiceChannelHistory")

    async def insert_voice_channel_history(self, user_id: int, action_label: str, action_ts: int, vc_id: int, vc2_id: Optional[int] = None) -> None:
        """ Inserts a channel into the user's Voice Channel history.
        :param user_id: The user ID.
        :param action_label: The action label.
        :param action_ts: The timestamp of the action.
        :param vc_id: The Voice Channel ID.
        :param vc2_id: The second Voice Channel ID, if any. [Optional] """

        return await self.db.execute_query("""
            INSERT INTO VoiceChannelHistory (
                user_id, action_label, action_ts, vc_id, vc2_id
            ) VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action_label, action_ts, vc_id, vc2_id))

    async def get_voice_channel_history(self, user_id: int) -> List[List[Union[int, str]]]:
        """ Gets the user's Voice Channel history.
        :param user_id: The user's ID. """

        return await self.db.execute_query("SELECT * FROM VoiceChannelHistory WHERE user_id = %s ORDER BY action_ts DESC", (user_id,), fetch="all")

    async def get_users_exceeding_records(self, limit: int = 10) -> List[List[int]]:
        """ Gets all IDs of the users that have an amount of Voice Channel records
        that exceeds the limit.
        :param limit: The limit of records one can have. """

        return await self.db.execute_query("""
            SELECT * FROM (
                SELECT COUNT(*) AS records_count, user_id 
                FROM VoiceChannelHistory GROUP BY user_id
            ) AS result WHERE records_count >= %s;
        """, (limit,), fetch="all")

    async def delete_voice_channel_history(self, users: List[int]) -> None:
        """ Deletes Voice Channels from the users' Voice Channel histories.
        :param users: A list of users from whom to delete records from their history. """

        await self.db.execute_query("DELETE FROM VoiceChannelHistory WHERE user_id = %s LIMIT %s", users, execute_many=True)


class VoiceChannelHistorySystem(commands.Cog):
    """ Class for the VoiceChannelHistory system. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @tasks.loop(minutes=1)
    async def check_exceeding_voice_channels_from_history(self) -> None:
        """ Checks for channels that are exceeding the amount of Voice Channel records
        in people's histories. """

        records_limit: int = 55
        delete_records_limit: int = 5
        if raw_users := await self.get_users_exceeding_records(limit=records_limit):
            users = list(map(lambda result: [result[1], delete_records_limit], raw_users))
            await self.delete_voice_channel_history(users)


    @commands.Cog.listener(name="on_voice_state_update")
    async def on_voice_state_update_voice_channel_history(self, member, before, after):
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

        bc, ac = before.channel, after.channel

        current_ts = await utils.get_timestamp()

        if not bc and ac: # Join
            await self.insert_voice_channel_history(member.id, "join", current_ts, ac.id)
        elif bc and ac: # Switch
            await self.insert_voice_channel_history(member.id, "switch", current_ts, bc.id, ac.id)
        else: # Leave
            await self.insert_voice_channel_history(member.id, "leave", current_ts, bc.id)
