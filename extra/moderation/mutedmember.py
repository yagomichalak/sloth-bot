from datetime import time
import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Optional, Tuple

class ModerationMutedMemberTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_mutedmember(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table. """

        if await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE mutedmember (
            user_id BIGINT NOT NULL, 
            role_id BIGINT NOT NULL, 
            mute_ts BIGINT DEFAULT NULL, 
            muted_for_seconds BIGINT DEFAULT NULL,
            PRIMARY KEY (user_id, role_id)
            )""")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MutedMember__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_mutedmember(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """
        if not await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE mutedmember")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MutedMember__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_mutedmember(self, ctx):
        '''
        (ADM) Resets the MutedMember table.
        '''
        if not await self.check_table_mutedmember_exists():
            return await ctx.send("**Table __MutedMember__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM mutedmember")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __mutedmember__ reset!**", delete_after=3)

    async def check_table_mutedmember_exists(self) -> bool:
        '''
        Checks if the MutedMember table exists
        '''
        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'mutedmember'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    async def get_expired_tempmutes(self, current_ts: int) -> List[int]:
        """ Gets expired tempmutes.
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT DISTINCT(user_id) FROM mutedmember WHERE (%s -  mute_ts) >= muted_for_seconds", (current_ts,))
        tempmutes = list(map(lambda m: m[0], await mycursor.fetchall()))
        await mycursor.close()
        return tempmutes

    async def get_muted_members(self, current_ts: int, days_ago: Optional[int] = 0) -> List[int]:
        """ Gets muted members from the past X days.
        :param current_ts: The current timestamp.
        :param days_ago: The amount of days ago to get muted members from. [Optional] """

        seconds_ago = 86400 * days_ago
        mycursor, db = await the_database()
        await mycursor.execute("SELECT DISTINCT(user_id) FROM mutedmember WHERE (%s -  mute_ts) >= %s", (current_ts, seconds_ago))
        muted_members = list(map(lambda m: m[0], await mycursor.fetchall()))
        await mycursor.close()
        return muted_members


    async def insert_in_muted(self, user_role_ids: List[Tuple[int]]):
        mycursor, db = await the_database()
        await mycursor.executemany(
            """
            INSERT INTO mutedmember (
            user_id, role_id, mute_ts, muted_for_seconds) VALUES (%s, %s, %s, %s)""", user_role_ids
            )
        await db.commit()
        await mycursor.close()

    async def get_muted_roles(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM mutedmember WHERE user_id = %s", (user_id,))
        user_roles = await mycursor.fetchall()
        await mycursor.close()
        return user_roles

    async def remove_role_from_system(self, user_role_ids: int):
        mycursor, db = await the_database()
        await mycursor.executemany("DELETE FROM mutedmember WHERE user_id = %s AND role_id = %s", user_role_ids)
        await db.commit()
        await mycursor.close()

    async def remove_all_roles_from_system(self, user_id: int):
        """ Removes all muted-roles linked to a user from the system.
        :param user_id: The ID of the user. """

        mycursor, db = await the_database()
        await mycursor.executemany("DELETE FROM mutedmember WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_mute_time(self, user_id: int, current_time: int, time: int):
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE mutedmember SET mute_ts = %s, muted_for_seconds = %s WHERE user_id = %s", (current_time, time, user_id))
        await db.commit()
        await mycursor.close()

    async def get_mute_time(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.executemany("SELECT mute_ts, muted_for_seconds FROM mutedmember WHERE user_id = %s", (user_id,))
        times = await mycursor.fetchone()
        await mycursor.close()
        return times
    
    async def get_not_unmuted_members(self):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT user_id, mute_ts FROM mutedmember WHERE muted_for_seconds IS NULL")
        muted_members = await mycursor.fetchall()
        await mycursor.close()
        return set(muted_members)
