from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List


class CoinflipMemberTable(commands.Cog):
    """ Class for managing the CoinflipMember table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_coinflip_member(self, ctx: commands.Context) -> None:
        """ Creates the CoinflipMember table. """

        member = ctx.author

        if await self.check_coinflip_member_table_exists():
            return await ctx.send(f"**Table `CoinflipMember` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
            CREATE TABLE CoinflipMember (
                user_id BIGINT NOT NULL,
                wins INT DEFAULT 0,
                losses INT DEFAULT 0,
                last_played_ts BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")

        await ctx.send(f"**Table `CoinflipMember` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_coinflip_member(self, ctx: commands.Context) -> None:
        """ Drops the CoinflipMember table. """

        member = ctx.author
        
        if not await self.check_coinflip_member_table_exists():
            return await ctx.send(f"**Table `CoinflipMember` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE CoinflipMember")

        await ctx.send(f"**Table `CoinflipMember` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_coinflip_member(self, ctx: commands.Context) -> None:
        """ Resets the CoinflipMember table. """

        member = ctx.author
        
        if not await self.check_coinflip_member_table_exists():
            return await ctx.send(f"**Table `CoinflipMember` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM CoinflipMember")

        await ctx.send(f"**Table `CoinflipMember` reset, {member.mention}!**")

    async def check_coinflip_member_table_exists(self) -> bool:
        """ Checks whether the CoinflipMember table exists. """

        return await self.db.table_exists("CoinflipMember")

    async def insert_coinflip_member(self, user_id: int, current_ts: int, wins: int = 0, losses: int = 0) -> None:
        """ Inserts a member into the MemoryTable.
        :param user_id: The user ID.
        :param current_ts: The current timestamp. 
        :param wins: The amount of wins they have.
        :param losses: The amount of losses they have. """

        await self.db.execute_query("""
            INSERT INTO CoinflipMember (
                user_id, wins, losses, last_played_ts
            ) VALUES (%s, %s, %s, %s)""", (user_id, wins, losses, current_ts))

    async def get_coinflip_member(self, user_id: int) -> List[int]:
        """ Gets a memory member.
        :param user_id: The ID of the member to get. """

        return await self.db.execute_query("SELECT * FROM CoinflipMember WHERE user_id = %s", (user_id,), fetch="one")

    async def update_coinflip_member(self, user_id: int, current_ts: int, wins: int = 0, losses: int = 0) -> None:
        """ Updates a memory member.
        :param user_id: The ID of the member to update.
        :param current_ts: The current timestamp. 
        :param wins: The increment value in the wins counter. [Default = 0]
        :param losses: The increment value in the losses counter. [Default = 0] """

        await self.db.execute_query("""
            UPDATE CoinflipMember SET wins = wins + %s, losses = losses + %s, last_played_ts = %s
            WHERE user_id = %s""", (wins, losses, current_ts, user_id))

    async def get_top_ten_coinflip_members_by_wins(self) -> List[List[int]]:
        """ Gets the top ten users with the most wins in the coinflip game. """

        return await self.db.execute_query("SELECT * FROM CoinflipMember ORDER BY wins DESC LIMIT 10", fetch="all")

    async def get_all_coinflip_members_by_wins(self) -> List[List[int]]:
        """ Gets the top ten users with the most wins in the coinflips game. """

        return await self.db.execute_query("SELECT * FROM CoinflipMember ORDER BY wins DESC", fetch="all")
