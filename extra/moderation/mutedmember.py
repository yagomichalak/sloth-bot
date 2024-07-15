from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Optional, Tuple


class ModerationMutedMemberTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_mutedmember(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table. """

        if await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE mutedmember (
            user_id BIGINT NOT NULL, 
            role_id BIGINT NOT NULL, 
            mute_ts BIGINT DEFAULT NULL, 
            muted_for_seconds BIGINT DEFAULT NULL,
            PRIMARY KEY (user_id, role_id)
            )""")

        return await ctx.send("**Table __MutedMember__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_mutedmember(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """
        if not await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE mutedmember")

        return await ctx.send("**Table __MutedMember__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_mutedmember(self, ctx):
        """ (ADM) Resets the MutedMember table. """

        if not await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM mutedmember")

        return await ctx.send("**Table __mutedmember__ reset!**", delete_after=3)

    async def check_table_mutedmember_exists(self) -> bool:
        """ Checks if the MutedMember table exists """

        return await self.db.table_exists("mutedmember")

    async def get_expired_tempmutes(self, current_ts: int) -> List[int]:
        """ Gets expired tempmutes.
        :param current_ts: The current timestamp. """

        tempmutes = await self.db.execute_query(
            "SELECT DISTINCT(user_id) FROM mutedmember WHERE (%s -  mute_ts) >= muted_for_seconds", (current_ts,), fetch="all")
        return list(map(lambda m: m[0], tempmutes))

    async def get_muted_members(self, current_ts: int, days_ago: Optional[int] = 0) -> List[int]:
        """ Gets muted members from the past X days.
        :param current_ts: The current timestamp.
        :param days_ago: The amount of days ago to get muted members from. [Optional] """

        seconds_ago = 86400 * days_ago
        muted_members = await self.db.execute_query(
            "SELECT DISTINCT(user_id) FROM mutedmember WHERE (%s -  mute_ts) >= %s", (current_ts, seconds_ago), fetch="all")
        return list(map(lambda m: m[0], muted_members))

    async def insert_in_muted(self, user_role_ids: List[Tuple[int]]):
        await self.db.execute_query(
            """
            INSERT INTO mutedmember (
            user_id, role_id, mute_ts, muted_for_seconds) VALUES (%s, %s, %s, %s)""", user_role_ids, execute_many=True
            )

    async def get_muted_roles(self, user_id: int):
        return await self.db.execute_query("SELECT * FROM mutedmember WHERE user_id = %s", (user_id,), fetch="all")

    async def remove_role_from_system(self, user_role_ids: int):
        await self.db.execute_query("DELETE FROM mutedmember WHERE user_id = %s AND role_id = %s", user_role_ids, execute_many=True)

    async def remove_all_roles_from_system(self, user_id: int):
        """ Removes all muted-roles linked to a user from the system.
        :param user_id: The ID of the user. """

        await self.db.execute_query("DELETE FROM mutedmember WHERE user_id = %s", (user_id,), execute_many=True)

    async def update_mute_time(self, user_id: int, current_time: int, time: int):
        await self.db.execute_query("UPDATE mutedmember SET mute_ts = %s, muted_for_seconds = %s WHERE user_id = %s", (current_time, time, user_id))

    async def get_mute_time(self, user_id: int):
        return await self.db.execute_query(
            "SELECT mute_ts, muted_for_seconds FROM mutedmember WHERE user_id = %s", (user_id,), execute_many=True, fetch="one")

    async def get_not_unmuted_members(self):
        muted_members = await self.db.execute_query("SELECT user_id, mute_ts FROM mutedmember WHERE muted_for_seconds IS NULL", fetch="all")
        return set(muted_members)
