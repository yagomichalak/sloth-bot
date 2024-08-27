# import.standard
from typing import List

# import.thirdparty
from discord.ext import commands

class OpenChannels(commands.Cog):
    """ Cog for managing user open channels. """

    async def member_has_open_channel(self, member_id: int) -> List[int]:
        """ Checks whether the member has an open channel.
        :param member_id: The ID of the member to check. """

        return await self.db.execute_query("SELECT * FROM OpenChannels WHERE user_id = %s", (member_id,), fetch="one")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_case_counter(self, ctx):
        """ (ADM) Creates the CaseCounter table. """

        if await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ already exists!**")

        await self.db.execute_query("CREATE TABLE CaseCounter (case_number bigint default 0)")
        await self.db.execute_query("INSERT INTO CaseCounter (case_number) VALUES (0)")

        await ctx.send("**Table __CaseCounter__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_case_counter(self, ctx):
        """ (ADM) Drops the CaseCounter table. """

        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist!**")

        await self.db.execute_query("DROP TABLE CaseCounter")

        return await ctx.send("**Table __CaseCounter__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_case_counter(self, ctx):
        """ (ADM) Resets the CaseCounter table. """

        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM CaseCounter")
        await self.db.execute_query("INSERT INTO CaseCounter (case_number) VALUES (0)")

        return await ctx.send("**Table __CaseCounter__ reset!**")

    async def table_case_counter_exists(self) -> bool:
        """ Checks whether the CaseCounter table exists. """

        return await self.db.table_exists("CaseCounter")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_open_channels(self, ctx):
        """ (ADM) Creates the OpenChannels table. """

        if await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ already exists!**")

        await self.db.execute_query("""
            CREATE TABLE OpenChannels (
                user_id BIGINT,
                channel_id BIGINT,
                created_at BIGINT,
                last_message_at BIGINT
            )
        """)

        await ctx.send("**Table __OpenChannels__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_open_channels(self, ctx):
        """ (ADM) Drops the OpenChannels table. """

        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist!**")

        await self.db.execute_query("DROP TABLE OpenChannels")

        return await ctx.send("**Table __OpenChannels__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_open_channels(self, ctx):
        """ (ADM) Resets the OpenChannels table. """

        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM OpenChannels")

        return await ctx.send("**Table __OpenChannels__ reset!**")

    async def table_open_channels_exists(self) -> bool:
        """ Checks whether the OpenChannels table exists. """

        return await self.db.table_exists("OpenChannels")

    async def get_case_number(self) -> List[int]:
        """ Gets the current case counting number. """

        return await self.db.execute_query("SELECT * FROM CaseCounter", fetch="all")

    async def increase_case_number(self) -> None:
        """ Increases the current case counting number. """

        await self.db.execute_query("UPDATE CaseCounter SET case_number = case_number + 1")

    async def insert_user_open_channel(self, member_id: int, channel_id: int, current_ts: int) -> None:
        """ Inserts an open channel for a user.
        :param member_id: The ID of the user who opened the channel.
        :param channel_id: The ID of the channel they opened. """

        await self.db.execute_query("""
            INSERT INTO OpenChannels (
                user_id, channel_id, created_at, last_message_at
            ) VALUES (%s, %s, %s, %s)""", (member_id, channel_id, current_ts, current_ts))

    async def remove_user_open_channel(self, member_id: int) -> None:
        """ Removes an open channel.
        :param member_id: The ID of the member whose channel are gonna be deleted. """

        await self.db.execute_query("DELETE FROM OpenChannels WHERE user_id = %s", (member_id,))

    async def get_case_channel(self, channel_id: int) -> List[List[int]]:
        """ Gets an open case channel.
        :param channel_id: The ID of the channel to get.
        
        * Refactor this later so it returns just a list. """

        return await self.db.execute_query("SELECT * FROM OpenChannels WHERE channel_id = %s", (channel_id,), fetch="all")

    async def update_case_timestamp(self, channel_id: int, current_ts: int) -> None:
        """ Updates the case last message timestamp.
        :param channel_id: The channel ID.
        :param current_ts: The current timestamp. """

        await self.db.execute_query("""
            UPDATE OpenChannels SET last_message_at = %s WHERE channel_id = %s
        """, (current_ts, channel_id))

    async def get_inactive_cases(self, current_ts: int) -> List[List[int]]:
        """ Gets all case rooms that are inactive for 24h or more.
        :param current_ts: The current timestamp. """

        return await self.db.execute_query("""
            SELECT * FROM OpenChannels
            WHERE %s - last_message_at >= 86400
        """, (current_ts,), fetch="all")
