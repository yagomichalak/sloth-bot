# import.standard
from typing import Tuple

# import.thirdparty
from discord.ext import commands

# import.local
from extra import utils
from extra.customerrors import StillInRehabError
from mysqldb import DatabaseCore

class RehabMembersTable(commands.Cog):
    """ Class for managing the RehabMembers table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    def in_rehab(seconds: int = 86400):
        """ Checks whether the user's action skill is on cooldown. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            rehab_member = await ctx.bot.get_cog("Games").get_rehab_member(user_id=ctx.author.id)

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
        
        await self.db.execute_query("""
            CREATE TABLE RehabMembers (
                user_id BIGINT NOT NULL,
                rehab_ts BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")

        await ctx.send(f"**Table `RehabMembers` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_rehab_members(self, ctx: commands.Context) -> None:
        """ Creates the RehabMembers table. """

        member = ctx.author
        
        if not await self.check_rehab_members_exists():
            return await ctx.send(f"**Table `RehabMembers` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE RehabMembers")

        await ctx.send(f"**Table `RehabMembers` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_rehab_members(self, ctx: commands.Context) -> None:
        """ Creates the RehabMembers table. """

        member = ctx.author
        
        if not await self.check_rehab_members_exists():
            return await ctx.send(f"**Table `RehabMembers` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM RehabMembers")

        await ctx.send(f"**Table `RehabMembers` reset, {member.mention}!**")

    async def check_rehab_members_exists(self) -> bool:
        """ Checks whether the RehabMembers table exists. """

        return await self.db.table_exists("RehabMembers")

    async def insert_rehab_member(self, user_id: int, rehab_ts: int) -> None:
        """ Inserts a member into the rehab.
        :param user_id: The ID of the user.
        :param rehab_ts: The current timestamp. """

        await self.db.execute_query("INSERT INTO RehabMembers (user_id, rehab_ts) VALUES (%s, %s)", (user_id, rehab_ts))

    async def get_rehab_member(self, user_id: int) -> Tuple[int, int]:
        """ Gets a rehab member.
        :param user_id: The user ID to get. """

        return await self.db.execute_query("SELECT * FROM RehabMembers WHERE user_id = %s", (user_id,), fetch="one")

    async def update_rehab_member(self, user_id: int, current_ts: int) -> None:
        """ Updates a rehab member's rehab timestamp.
        :param user_id: The ID of the member to update.
        :param current_ts: The current timestamp. """

        await self.db.execute_query("UPDATE RehabMembers SET rehab_ts = %s WHERE user_id = %s", (current_ts, user_id))

    async def delete_rehab_member(self, user_id: int) -> None:
        """ Deletes a rehab member from rehab.
        :param user_id: The ID of the member to delete. """

        await self.db.execute_query("DELETE FROM RehabMembers WHERE user_id = %s", (user_id,))
