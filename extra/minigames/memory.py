import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Tuple
from extra.customerrors import StillInRehabError
from extra import utils

class MemoryTable(commands.Cog):
    """ Class for managing the MemoryMember table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_memory_member(self, ctx: commands.Context) -> None:
        """ Creates the MemoryMember table. """

        member = ctx.author

        if await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE MemoryMember (
                user_id BIGINT NOT NULL,
                level TINYINT(4) NOT NULL,
                record_ts BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MemoryMember` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_memory_member(self, ctx: commands.Context) -> None:
        """ Drops the MemoryMember table. """

        member = ctx.author
        
        if not await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE MemoryMember")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MemoryMember` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_memory_member(self, ctx: commands.Context) -> None:
        """ Resets the MemoryMember table. """

        member = ctx.author
        
        if not await self.check_memory_member_table_exists():
            return await ctx.send(f"**Table `MemoryMember` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MemoryMember")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MemoryMember` reset, {member.mention}!**")

    async def check_memory_member_table_exists(self) -> bool:
        """ Checks whether the MemoryMember table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'MemoryMember'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_memory_member(self, user_id: int, level: int, current_ts: int) -> None:
        """ Inserts a member into the MemoryTable.
        :param user_id: The user ID.
        :param level: The highest level they passed in game. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO MemoryMember (user_id, level, record_ts) VALUES (%s, %s, %s)", (user_id, level, current_ts))
        await db.commit()
        await mycursor.close()

    async def get_memory_member(self, user_id: int) -> List[int]:
        """ Gets a memory member.
        :param user_id: The ID of the member to get. """

        mycursor, _  = await the_database()
        await mycursor.execute("SELECT * FROM MemoryMember WHERE user_id = %s", (user_id,))
        memory_member = await mycursor.fetchone()
        await mycursor.close()
        return memory_member

    async def update_memory_member(self, user_id: int, level: int, current_ts: int) -> None:
        """ Updates a memory member.
        :param user_id: The ID of the member to update.
        :param level: The new level the member got to.
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MemoryMember SET level = %s, record_ts = %s WHERE user_id = %s", (level, current_ts, user_id))
        await db.commit()
        await mycursor.close()