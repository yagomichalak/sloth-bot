import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class ModerationWatchlistTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table. """

        if await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE Watchlist (
            user_id BIGINT NOT NULL,
            message_id BIGINT NOT NULL,
            PRIMARY KEY (user_id)
            )""")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Watchlist")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_watchlist(self, ctx):
        """ (ADM) Resets the Watchlist table. """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Watchlist")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ reset!**", delete_after=3)

    async def check_table_watchlist_exists(self) -> bool:
        """ Checks if the Watchlist table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Watchlist'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True


    async def get_user_watchlist(self, user_id: int) -> List[int]:
        """ Gets a user from the watchlist.
        :param user_id: The ID of the user to get.. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Watchlist WHERE user_id = %s", (user_id,))
        watchlist = await mycursor.fetchone()
        await mycursor.close()
        return watchlist

    
    async def insert_user_watchlist(self, user_id: int, message_id: int) -> None:
        """ Inserts a user into the watchlist.
        :param user_id: The ID of the user to insert.
        :param message_id: The ID of the message in the watchlist channel. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Watchlist (user_id, message_id) VALUES (%s, %s)", (user_id, message_id))
        await db.commit()
        await mycursor.close()

    async def delete_user_watchlist(self, user_id: int) -> None:
        """ Deletes a user from the watchlist.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Watchlist WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()