import discord
from discord.ext import commands
from mysqldb import the_database
from typing import Optional
from extra import utils

class ModActivityTable(commands.Cog):
    """ Class for managing the ModActivity table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    # Database commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_mod_activity_table(self, ctx) -> None:
        """ (ADM) Creates the ModActivity table. """

        member: discord.Member = ctx.author
        if await self.check_mod_activity_table_exists():
            return await ctx.send(f"**The `ModActivity` table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE ModActivity (
                mod_id BIGINT NOT NULL, 
                time BIGINT DEFAULT 0, 
                timestamp BIGINT DEFAULT NULL, 
                messages INT DEFAULT 0,
                PRIMARY KEY (mod_id)
            )""")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `ModActivity` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_mod_activity_table(self, ctx) -> None:
        """ (ADM) Drops the ModActivity table. """

        member: discord.Member = ctx.author
        if not await self.check_mod_activity_table_exists():
            return await ctx.send(f"**The `ModActivity` table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute('DROP TABLE ModActivity')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `ModActivity` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_mod_activity_table(self, ctx) -> None:
        """ (ADM) Resets the ModActivity table. """

        member: discord.Member = ctx.author
        if not await self.check_mod_activity_table_exists():
            return await ctx.send(f"**The `ModActivity` table doesn't exist yett, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ModActivity")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `ModActivity` reset, {member.mention}!**")

    async def check_mod_activity_table_exists(self) -> bool:
        """ Checks whether the ModActivity table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'ModActivity'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False
    
    async def insert_moderator(self, mod_id: int, old_ts: Optional[int] = None, messages: Optional[int] = 0) -> None:
        """ Inserts a moderator.
        :param mod_id: The ID of the moderator to insert.
        :param old_ts: The current timestamp. [Optional]
        :param messages: The initial amount of messages for the moderator to start with. [Optional][Default = 0] """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO ModActivity (mod_id, timestamp, messages) VALUES (%s, %s, %s)
            """, (mod_id, old_ts, messages))
        await db.commit()
        await mycursor.close()

    async def get_moderator_current_timestamp(self, mod_id: int, old_ts: Optional[int] = None) -> int:
        """ Gets the moderator's current timestamp.
        :param mod_id: The moderator ID.
        :param old_ts: The current global timestmap. [Optional]"""

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM ModActivity WHERE mod_id = %s", (mod_id,))
        mod = await mycursor.fetchone()
        await mycursor.close()

        if not mod:
            await self.insert_moderator(mod_id, old_ts)
            return await self.get_moderator_current_timestamp(mod_id)

        return mod[2] if mod[2] else old_ts

    async def get_moderator_current_messages(self, mod_id: int) -> int:
        """ Gets the moderator's current amount of messages.
        :param mod_id: The moderator ID. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM ModActivity WHERE mod_id = %s", (mod_id,))
        mod = await mycursor.fetchone()
        await mycursor.close()

        if not mod:
            await self.insert_moderator(mod_id, messages=1)
            return await self.get_moderator_current_messages(mod_id)

        return mod[3]

    async def update_moderator_message(self, mod_id: int) -> None:
        """ Updates the moderator's message counter.
        :param mod_id: The moderator's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ModActivity SET messages = messages + 1 WHERE mod_id = %s", (mod_id,))
        await db.commit()
        await mycursor.close()

    async def update_moderator(self, mod_id: int) -> None:
        """ Updates the moderator's timestamp.
        :param mod_id: The moderator ID. """

        mycursor, db = await the_database()
        current_ts = await utils.get_timestamp()
        await mycursor.execute("UPDATE ModActivity SET timestamp = %s WHERE mod_id = %s", (current_ts, mod_id))
        await db.commit()
        await mycursor.close()

    async def add_time_moderator(self, mod_id: int, addition: int) -> None:
        """ Increments the moderator's time counter.
        :param mod_id: The moderator ID.
        :param addition: The addition value. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ModActivity SET time = time + %s WHERE mod_id = %s", (addition, mod_id))
        await db.commit()
        await mycursor.close()
        await self.update_moderator(mod_id)

