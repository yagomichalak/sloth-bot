from datetime import time
import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Optional, Tuple

class UserMutedGalaxiesTable(commands.Cog):
    """ Class for managing the UserMutedGalaxies table and its methods. """
    
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_muted_galaxies(self, ctx) -> None:
        """ (ADM) Creates the UserMutedGalaxies table. """

        member: discord.Member = ctx.author

        if await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ already exists!, {member.mention}!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE UserMutedGalaxies (
            user_id BIGINT NOT NULL,
            cat_id BIGINT NOT NULL,
            PRIMARY KEY (user_id, cat_id)
        )""")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table __UserMutedGalaxies__ created!, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_muted_galaxies(self, ctx) -> None:
        """ (ADM) Creates the UserMutedGalaxies table """

        member: discord.Member = ctx.author

        if not await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ doesn't exist!, {member.mention}!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserMutedGalaxies")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table __UserMutedGalaxies__ dropped!, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_muted_galaxies(self, ctx):
        """ (ADM) Resets the UserMutedGalaxies table. """

        member: discord.Member = ctx.author

        if not await self.check_table_user_muted_galaxies_exists():
            return await ctx.send(f"**Table __UserMutedGalaxies__ doesn't exist yet, {member.mention}!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserMutedGalaxies")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table __UserMutedGalaxies__ reset!, {member.mention}!**")

    async def check_table_user_muted_galaxies_exists(self) -> bool:
        """ Checks whether the UserMutedGalaxies table exists """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserMutedGalaxies'")
        exists = await mycursor.fetchone()
        await mycursor.close()

        if exists:
            return True
        else:
            return False

    async def insert_user_muted_galaxies(self, muted_galaxies: List[Tuple[int, int]]) -> None:
        """ Inserts rows for a user in the UserMutedGalaxies table.
        :param muted_galaxies: The galaxies in which the user got muted. """

        mycursor, db = await the_database()
        await mycursor.executemany("INSERT INTO UserMutedGalaxies (user_id, role_id) VALUES (%s, %s)", muted_galaxies)
        await db.commit()
        await mycursor.close()

    async def get_user_muted_galaxies(self, user_id: int) -> List[Tuple[int, int]]:
        """ Gets all Muted Galaxies of a user.
        :param user_id: The ID of the user. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserMutedGalaxies WHERE user_id = %s", (user_id,))
        muted_galaxies = await mycursor.fetchall()
        await mycursor.close()
        return muted_galaxies

    async def delete_user_muted_galaxies(self, user_id: int) -> None:
        """ Removes all muted galaxies rows from a user.
        :param user_id: The ID of the user. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserMutedGalaxies WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()