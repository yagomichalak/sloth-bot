import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class OpenChannels(commands.Cog):
    """ Cog for managing user open channels. """

    async def member_has_open_channel(self, member_id: int) -> List[int]:
        """ Checks whether the member has an open channel.
        :param member_id: The ID of the member to check. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM OpenChannels WHERE user_id = %s", (member_id,))
        user = await mycursor.fetchone()
        await mycursor.close()
        return user

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_case_counter(self, ctx):
        """ (ADM) Creates the CaseCounter table. """

        if await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE CaseCounter (case_number bigint default 0)")
        await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table __CaseCounter__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_case_counter(self, ctx):
        """ (ADM) Drops the CaseCounter table. """

        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE CaseCounter")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __CaseCounter__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_case_counter(self, ctx):
        """ (ADM) Resets the CaseCounter table. """

        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM CaseCounter")
        await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __CaseCounter__ reset!**")

    async def table_case_counter_exists(self) -> bool:
        """ Checks whether the CaseCounter table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'CaseCounter'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_open_channels(self, ctx):
        """ (ADM) Creates the OpenChannels table. """

        if await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE OpenChannels (user_id bigint, channel_id bigint)")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table __OpenChannels__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_open_channels(self, ctx):
        """ (ADM) Drops the OpenChannels table. """

        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE OpenChannels")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __OpenChannels__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_open_channels(self, ctx):
        """ (ADM) Resets the OpenChannels table. """

        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM OpenChannels")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __OpenChannels__ reset!**")

    async def table_open_channels_exists(self) -> bool:
        """ Checks whether the OpenChannels table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'OpenChannels'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False
        else:
            return True

    async def get_case_number(self) -> List[int]:
        """ Gets the current case counting number. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM CaseCounter")
        counter = await mycursor.fetchall()
        await mycursor.close()
        return counter

    async def increase_case_number(self) -> None:
        """ Increases the current case counting number. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE CaseCounter SET case_number = case_number + 1")
        await db.commit()
        await mycursor.close()

    async def insert_user_open_channel(self, member_id: int, channel_id: int) -> None:
        """ Inserts an open channel for a user.
        :param member_id: The ID of the user who opened the channel.
        :param channel_id: The ID of the channel they opened. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO OpenChannels (user_id, channel_id) VALUES (%s, %s)", (member_id, channel_id))
        await db.commit()
        await mycursor.close()

    async def remove_user_open_channel(self, member_id: int) -> None:
        """ Removes an open channel.
        :param member_id: The ID of the member whose channel are gonna be deleted. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM OpenChannels WHERE user_id = %s", (member_id,))
        await db.commit()
        await mycursor.close()

    async def get_case_channel(self, channel_id: int) -> List[List[int]]:
        """ Gets an open case channel.
        :param channel_id: The ID of the channel to get.
        
        * Refactor this later so it returns just a list. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM OpenChannels WHERE channel_id = %s", (channel_id,))
        channel = await mycursor.fetchall()
        await mycursor.close()
        return channel

