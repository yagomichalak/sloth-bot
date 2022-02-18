import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class CurseTable(commands.Cog):
    """ Class for managing the curse table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_cursed_member(self, ctx) -> None:
        """ (ADM) Creates the CursedMember table. """

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE CursedMember (user_id bigint)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table CursedMember was created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_cursed_member(self, ctx) -> None:
        """ (ADM) Drops the CursedMember table. """

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE CursedMember")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table CursedMember was dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_cursed_member(self, ctx) -> None:
        """ (ADM) Resets the CursedMember table. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM CursedMember")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table CursedMember was reseted!**", delete_after=3)

    async def insert_cursed_member(self, user_id: int) -> None:
        """ Insert the cursed member into the database.
        :param user_id: The ID of the user that's being cursed. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO CursedMember (user_id) VALUES (%s)", (user_id))
        await db.commit()
        await mycursor.close()

    async def get_cursed_member(self, user_id: int) -> List[List[int]]:
        """ Gets the cursed member from the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM CursedMember WHERE user_id = %s", (user_id,))
        cm = await mycursor.fetchone()
        await mycursor.close()
        return cm

    async def delete_cursed_member(self) -> bool:
        """ Deletes the cursed member from the database. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM CursedMember")
        cm = await mycursor.fetchone()
        if cm:
            await mycursor.execute("DELETE FROM CursedMember WHERE user_id = %s", (cm[0],))
            await db.commit()
            await mycursor.close()
            return True
        else:
            await mycursor.close()
            return False
