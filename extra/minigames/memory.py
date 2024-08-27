# import.standard
from typing import List

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class MemoryTable(commands.Cog):
    """ Class for managing the MemoryMember table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_memory_member(self, ctx: commands.Context) -> None:
        """ Creates the MemoryMember table. """

        member = ctx.author

        if await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
            CREATE TABLE MemoryMember (
                user_id BIGINT NOT NULL,
                level TINYINT(4) NOT NULL,
                record_ts BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")

        await ctx.send(f"**Table `MemoryMember` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_memory_member(self, ctx: commands.Context) -> None:
        """ Drops the MemoryMember table. """

        member = ctx.author
        
        if not await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE MemoryMember")

        await ctx.send(f"**Table `MemoryMember` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_memory_member(self, ctx: commands.Context) -> None:
        """ Resets the MemoryMember table. """

        member = ctx.author
        
        if not await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM MemoryMember")

        await ctx.send(f"**Table `MemoryMember` reset, {member.mention}!**")

    async def check_memory_member_table_exists(self) -> bool:
        """ Checks whether the MemoryMember table exists. """

        return await self.db.table_exists("MemoryMember")

    async def insert_memory_member(self, user_id: int, level: int, current_ts: int) -> None:
        """ Inserts a member into the MemoryTable.
        :param user_id: The user ID.
        :param level: The highest level they passed in game. """

        await self.db.execute_query("INSERT INTO MemoryMember (user_id, level, record_ts) VALUES (%s, %s, %s)", (user_id, level, current_ts))

    async def get_memory_member(self, user_id: int) -> List[int]:
        """ Gets a memory member.
        :param user_id: The ID of the member to get. """

        return await self.db.execute_query("SELECT * FROM MemoryMember WHERE user_id = %s", (user_id,), fetch="one")

    async def update_memory_member(self, user_id: int, level: int, current_ts: int) -> None:
        """ Updates a memory member.
        :param user_id: The ID of the member to update.
        :param level: The new level the member got to.
        :param current_ts: The current timestamp. """

        await self.db.execute_query("UPDATE MemoryMember SET level = %s, record_ts = %s WHERE user_id = %s", (level, current_ts, user_id))

    async def get_top_ten_memory_users(self) -> List[List[int]]:
        """ Gets the top ten users with the highest level in the Memory game. """

        return await self.db.execute_query("SELECT * FROM MemoryMember ORDER BY level DESC LIMIT 10", fetch="all")

    async def get_all_memory_users_by_level(self) -> List[List[int]]:
        """ Gets all users from the MemoryMember table ordered by level. """

        return await self.db.execute_query("SELECT * FROM MemoryMember ORDER BY level DESC", fetch="all")
