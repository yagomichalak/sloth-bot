import discord
from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Tuple


class UserMutedGalaxiesTable(commands.Cog):
    """ Class for managing the UserMutedGalaxies table and its methods. """
    
    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_muted_galaxies(self, ctx) -> None:
        """ (ADM) Creates the UserMutedGalaxies table. """

        member: discord.Member = ctx.author

        if await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ already exists!, {member.mention}!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE UserMutedGalaxies (
            user_id BIGINT NOT NULL,
            cat_id BIGINT NOT NULL,
            PRIMARY KEY (user_id, cat_id)
        )""")

        return await ctx.send(f"**Table __UserMutedGalaxies__ created!, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_muted_galaxies(self, ctx) -> None:
        """ (ADM) Creates the UserMutedGalaxies table """

        member: discord.Member = ctx.author

        if not await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ doesn't exist!, {member.mention}!**")

        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE UserMutedGalaxies")

        return await ctx.send(f"**Table __UserMutedGalaxies__ dropped!, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_muted_galaxies(self, ctx):
        """ (ADM) Resets the UserMutedGalaxies table. """

        member: discord.Member = ctx.author

        if not await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ doesn't exist yet, {member.mention}!**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM UserMutedGalaxies")

        return await ctx.send(f"**Table __UserMutedGalaxies__ reset!, {member.mention}!**")

    async def check_table_user_muted_galaxies_exists(self) -> bool:
        """ Checks whether the UserMutedGalaxies table exists """

        return await self.db.table_exists("UserMutedGalaxies")

    async def insert_user_muted_galaxies(self, muted_galaxies: List[Tuple[int, int]]) -> None:
        """ Inserts rows for a user in the UserMutedGalaxies table.
        :param muted_galaxies: The galaxies in which the user got muted. """

        await self.db.execute_querymany("INSERT INTO UserMutedGalaxies (user_id, cat_id) VALUES (%s, %s)", muted_galaxies)

    async def get_user_muted_galaxies(self, user_id: int) -> List[Tuple[int, int]]:
        """ Gets all Muted Galaxies of a user.
        :param user_id: The ID of the user. """

        return await self.db.execute_query("SELECT * FROM UserMutedGalaxies WHERE user_id = %s", (user_id,), fetch="all")

    async def delete_user_muted_galaxies(self, user_id: int) -> None:
        """ Removes all muted galaxies rows from a user.
        :param user_id: The ID of the user. """

        await self.db.execute_query("DELETE FROM UserMutedGalaxies WHERE user_id = %s", (user_id,))
