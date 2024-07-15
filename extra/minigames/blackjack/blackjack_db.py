import discord
from discord.ext import commands
from typing import List


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

        await self.db.execute_query("""
            CREATE TABLE Blackjack (
                user_id BIGINT NOT NULL, 
                wins INT NOT DEFAULT 0,
                losses INT DEFAULT 0,
                draws INT DEFAULT 0,
                surrenders INT DEFAULT 0,
                games INT DEFAULT 0,
                PRIMARY KEY (user_id)
        )""")
        await ctx.send(f"**Table `Blackjack` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_blackjack(self, ctx):
        """(ADM) Drops the Blackjack table."""

        member: discord.Member = ctx.author
        if not await self.check_blackjack_exists():
            return await ctx.send(f"**The Blackjack table doesn't exist, {member.mention}!**")

        await self.db.execute_query('DROP TABLE Blackjack')
        await ctx.send(f"**Table `Blackjack` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_blackjack(self, ctx):
        """ (ADM) Resets the Blackjack table. """

        member: discord.Member = ctx.author
        if not await self.check_blackjack_exists():
            return await ctx.send(f"**The Blackjack table doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM Blackjack")
        await ctx.send(f"**Table `Blackjack` reset, {member.mention}!**")

    async def check_blackjack_exists(self) -> bool:
        """ Checks whether the Blackjack table exists. """

        return await self.db.table_exists("SHOW TABLE STATUS LIKE 'Blackjack'")

    async def insert_user_database(self, user_id) -> None:
        await self.db.execute_query("""
            INSERT INTO Blackjack (user_id, wins, losses, draws, surrenders, games) 
            VALUES (%s, %s, %s, %s, %s, %s)""", (user_id, 0, 0, 0, 0, 0))

    async def check_user_database(self, user_id) -> bool:
        """ Checks whether the Blackjack table exists. """

        return await self.db.execute_query("SELECT * FROM Blackjack WHERE user_id = %s", (user_id,), fetch="one")

    async def insert_user_data(self, data_type: str, user_id: int) -> None:
        """ Checks whether the Blackjack table exists. """

        await self.db.execute_query(
            "UPDATE Blackjack SET {0} = {0} + 1 WHERE user_id = {1}".format(data_type, user_id)
        )

    async def get_user_data(self, user_id) -> None:
        """ Checks whether the Blackjack table exists. """

        return await self.db.execute_query("SELECT * FROM Blackjack WHERE user_id = %s", (user_id,), fetch="one")

    async def get_top_ten_blackjack_members_by_wins(self) -> List[List[int]]:
        """ Gets the top ten users with the most wins in the coinflip game. """

        return await self.db.execute_query("SELECT * FROM Blackjack ORDER BY wins DESC LIMIT 10", fetch="all")

    async def get_all_blackjack_members_by_wins(self) -> List[List[int]]:
        """ Gets the top ten users with the most wins in the coinflips game. """

        return await self.db.execute_query("SELECT * FROM Blackjack ORDER BY wins DESC", fetch="all")
