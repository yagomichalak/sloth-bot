import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Any
from extra import utils

class AspirantsTable(commands.Cog):
    """ Class for managing the AspirantsTable table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_aspirants_table(self, ctx):
        """(ADM) Creates the AspirantActivity table."""
        
        member: discord.Member = ctx.author
        if await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute(
            'CREATE TABLE AspirantActivity (user_id bigint , time bigint, timestamp bigint default null, messages int)')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_aspirants(self, ctx):
        """(ADM) Drops the AspirantActivity table."""

        member: discord.Member = ctx.author
        if not await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute('DROP TABLE AspirantActivity')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_aspirants(self, ctx):
        """ (ADM) Resets the AspirantActivity table. """

        member: discord.Member = ctx.author
        if not await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM AspirantActivity")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` reset, {member.mention}!**")

    async def check_aspirant_activity_exists(self) -> bool:
        """ Checks whether the AspirantActivity table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'AspirantActivity'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_aspirant(self, user_id: int, old_ts: int) -> None:
        """ Inserts an aspirant to the database.
        :param user_id: The ID of the aspirant to add.
        :param old_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute(
            "INSERT INTO AspirantActivity (user_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)", 
            (user_id, 0, old_ts, 0))
        await db.commit()
        await mycursor.close()

    async def get_all_aspirants(self) -> List[List[int]]:
        """ Gets all aspirants. """

        mycursor, _ = await the_database()
        await mycursor.execute('SELECT user_id FROM AspirantActivity')
        users = await mycursor.fetchall()
        await mycursor.close()
        return list(map(lambda user: user[0], users))

    async def get_aspirant_current_timestamp(self, user_id: int, old_ts: int) -> int:
        """ Gets a specific aspirant's timestamp.
        :param user_id: The ID of the user from whom to get it.
        :param old_ts: The current timestamp. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM AspirantActivity WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchone()
        await mycursor.close()

        if not user:
            await self.insert_aspirant(user_id, old_ts)
            return await self.get_aspirant_current_timestamp(user_id, old_ts)

        if user[2]:
            return user[2]
        else:
            return old_ts

    async def get_aspirant_current_messages(self, user_id: int) -> int:
        """ Gets a specific aspirant's messages counter.
        :param user_id: The ID of the user from whom to get it. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM AspirantActivity WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchone()
        await mycursor.close()

        if not user:
            await self.insert_aspirant_message(user_id)
            return await self.get_aspirant_current_messages(user_id)

        return user[3]

    async def add_aspirant_time(self, user_id: int, addition: int) -> None:
        """ Updates an aspirant's time counter.
        :param user_id: The ID of the aspirant to add.
        :param addition: The addition to increment to their current time counter. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET time = time + %s WHERE user_id = %s", (addition, user_id))
        await db.commit()
        await mycursor.close()
        await self.update_aspirant_time(user_id)

    async def update_aspirant_message(self, user_id: int) -> None:
        """ Updates an aspirant's message counter.
        :param user_id: The user for whom to update it. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET messages = messages + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_aspirant_time(self, user_id: int) -> None:
        """ Updates an aspirant's timestamp.
        :param user_id: The ID of the aspirant from whom to update it. """

        mycursor, db = await the_database()
        current_ts = await utils.get_timestamp()
        await mycursor.execute("UPDATE AspirantActivity SET timestamp = %s WHERE user_id = %s", (int(current_ts), user_id))
        await db.commit()
        await mycursor.close()

    async def reset_users_activity(self, user_id: int) -> None:
        """ Resets an aspirant's statuses.
        :param user_id: The ID of the user to reset. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET messages = 0, time = 0 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()