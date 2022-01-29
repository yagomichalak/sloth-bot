import asyncio
import discord
from discord.ext import commands
from mysqldb import *

import copy
import random


class BlackJackDB(commands.Cog):
    """ Class for the BlackJack game. """


    ### Database commands for aspirants activity
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_blackjack_table(self, ctx):
        """(ADM) Creates the Blackjack table."""
        
        member: discord.Member = ctx.author
        if await self.check_blackjack_exists():
            return await ctx.send(f"**The Blackjack table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute(
            'CREATE TABLE Blackjack (user_id bigint, wins int, losses int, draws int, surrenders int, games int)')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `Blackjack` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_blackjack(self, ctx):
        """(ADM) Drops the Blackjack table."""

        member: discord.Member = ctx.author
        if not await self.check_blackjack_exists():
            return await ctx.send(f"**The Blackjack table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute('DROP TABLE Blackjack')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `Blackjack` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_blackjack(self, ctx):
        """ (ADM) Resets the Blackjack table. """

        member: discord.Member = ctx.author
        if not await self.check_blackjack_exists():
            return await ctx.send(f"**The Blackjack table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Blackjack")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `Blackjack` reset, {member.mention}!**")

    async def check_blackjack_exists(self) -> bool:
        """ Checks whether the Blackjack table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Blackjack'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_user_database(self, user_id) -> None:
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Blackjack (user_id, wins, losses, draws, surrenders, games) VALUES (%s, %s, %s, %s, %s, %s) )", (user_id, 0, 0, 0, 0, 0))
        await db.commit()
        await mycursor.close()

    async def check_user_database(self, user_id) -> bool:
        """ Checks whether the Blackjack table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM Blackjack WHERE user_id = %s", (user_id,))
        exist = await mycursor.fetchone()
        await mycursor.close()
        if exist:
            return True
        else:
            return False

    async def insert_user_data(self, type: str, user_id: int) -> None:
        """ Checks whether the Blackjack table exists. """

        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Blackjack SET {type} = {type} + 1 WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def get_user_data(self, user_id) -> None:
        """ Checks whether the Blackjack table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Blackjack WHERE user_id = %s", (user_id,))
        user_data = await mycursor.fetchone()
        await mycursor.close()
        return user_data
