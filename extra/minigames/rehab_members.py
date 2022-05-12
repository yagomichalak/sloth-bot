import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Tuple
from extra.customerrors import StillInRehabError
from extra import utils

class RehabMembersTable(commands.Cog):
    """ Class for managing the RehabMembers table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    def in_rehab(seconds: int = 86400):
        """ Checks whether the user's action skill is on cooldown. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            rehab_member = await RehabMembersTable.get_rehab_member(RehabMembersTable, user_id=ctx.author.id)

            if not rehab_member:
                return True

            rehab_ts = rehab_member[1]

            current_time = await utils.get_timestamp()
            cooldown_in_seconds = current_time - rehab_ts
            if cooldown_in_seconds >= seconds:
                return True

            raise StillInRehabError(
                try_after=cooldown_in_seconds, error_message="You're still in rehab!", rehab_ts=rehab_ts, cooldown=seconds)

        return commands.check(real_check)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_rehab_members(self, ctx: commands.Context) -> None:
        """ Creates the RehabMembers table. """

        member = ctx.author

        if await self.check_rehab_members_exists():
            return await ctx.send(f"**Table `RehabMembers` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE RehabMembers (
                user_id BIGINT NOT NULL,
                rehab_ts BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `RehabMembers` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_rehab_members(self, ctx: commands.Context) -> None:
        """ Creates the RehabMembers table. """

        member = ctx.author
        
        if not await self.check_rehab_members_exists():
            return await ctx.send(f"**Table `RehabMembers` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE RehabMembers")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `RehabMembers` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_rehab_members(self, ctx: commands.Context) -> None:
        """ Creates the RehabMembers table. """

        member = ctx.author
        
        if not await self.check_rehab_members_exists():
            return await ctx.send(f"**Table `RehabMembers` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM RehabMembers")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `RehabMembers` reset, {member.mention}!**")

    async def check_rehab_members_exists(self) -> bool:
        """ Checks whether the RehabMembers table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'RehabMembers'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_rehab_member(self, user_id: int, rehab_ts: int) -> None:
        """ Inserts a member into the rehab.
        :param user_id: The ID of the user.
        :param rehab_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO RehabMembers (user_id, rehab_ts) VALUES (%s, %s)", (user_id, rehab_ts))
        await db.commit()
        await mycursor.close()

    async def get_rehab_member(self, user_id: int) -> Tuple[int, int]:
        """ Gets a rehab member.
        :param user_id: The user ID to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM RehabMembers WHERE user_id = %s", (user_id,))
        rehab_member = await mycursor.fetchone()
        await mycursor.close()
        return rehab_member

    async def update_rehab_member(self, user_id: int, current_ts: int) -> None:
        """ Updates a rehab member's rehab timestamp.
        :param user_id: The ID of the member to update.
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE RehabMembers SET rehab_ts = %s WHERE user_id = %s", (current_ts, user_id))
        await db.commit()
        await mycursor.close()