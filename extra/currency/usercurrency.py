# import.standard
from typing import List, Tuple

# import.thirdparty
import discord
from discord.ext import commands

class UserCurrencyTable:
    """ Class for the UserCurrency table in the database. """

    TABLE_NAME = "UserCurrency"

    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_currency(self, ctx) -> None:
        """ (ADM) Creates the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if await self.db.table_exists(self.TABLE_NAME):
            return await ctx.send(f"**The `{self.TABLE_NAME}` table already exists, {member.mention}!**")

        await self.db.execute_query("""
            CREATE TABLE UserCurrency (
                user_id BIGINT NOT NULL, 
                user_money BIGINT DEFAULT 0, 
                last_purchase_ts BIGINT DEFAULT NULL,
                user_classes BIGINT DEFAULT 0, 
                user_class_reward BIGINT DEFAULT 0, 
                user_hosted BIGINT DEFAULT 0,
                user_lotto BIGINT DEFAULT NULL,
                user_premium_money BIGINT DEFAULT 0
                PRIMARY KEY (user_id))
            """)
        return await ctx.send(f"**Table `{self.TABLE_NAME}` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_currency(self, ctx) -> None:
        """ (ADM) Drops the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.db.table_exists(self.TABLE_NAME):
            return await ctx.send(f"**The `{self.TABLE_NAME}` table doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE UserCurrency")
        return await ctx.send(f"**Table `{self.TABLE_NAME}` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_currency(self, ctx) -> None:
        """ (ADM) Resets the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.db.table_exists(self.TABLE_NAME):
            return await ctx.send(f"**The `{self.TABLE_NAME}` table doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM UserCurrency")

        return await ctx.send(f"**Table `{self.TABLE_NAME}` reset, {member.mention}!**")

    # ===== SELECT =====

    async def get_user_currency(self, user_id: int) -> List[List[int]]:
        """ Gets the user's currency info.
        :param user_id: The ID of the user to get. """

        return await self.db.execute_query("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,), fetch="all")

    async def get_top_ten_leaves_users(self) -> List[List[int]]:
        """ Gets the top ten users with the most leaves. """

        return await self.db.execute_query("SELECT * FROM UserCurrency ORDER BY user_money DESC LIMIT 10", fetch="all")

    async def get_top_ten_time_users(self) -> List[List[int]]:
        """ Gets the top ten users with the most time. """

        return await self.db.execute_query("SELECT * FROM UserServerActivity ORDER BY user_time DESC LIMIT 10", fetch="all")

    async def get_all_leaves_users(self) -> List[List[int]]:
        """ Gets all users with the most leaves. """

        return await self.db.execute_query("SELECT * FROM UserCurrency ORDER BY user_money DESC", fetch="all")

    async def get_all_specific_leaves_users(self, user_ids: List[int]) -> List[List[int]]:
        """ Gets specific users with the most leaves.
        :param user_ids: The list of the user IDs. """

        return await self.db.execute_query("SELECT * FROM UserCurrency WHERE user_id IN {} ORDER BY user_money DESC".format(tuple(user_ids)), fetch="all")

    async def get_all_time_users(self) -> List[List[int]]:
        """ Gets all users with the most time. """

        return await self.db.execute_query("SELECT * FROM UserServerActivity ORDER BY user_time DESC", fetch="all")

    # ===== INSERT =====

    async def insert_user_currency(self, user_id: int, the_time: int) -> None:
        """ Inserts a user into the currency system.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        await self.db.execute_query("INSERT INTO UserCurrency (user_id, user_money, last_purchase_ts) VALUES (%s, %s, %s)", (user_id, 0, the_time))

    # ===== UPDATE =====
    async def update_user_money(self, user_id: int, money: int) -> None:
        """ Updates the user money.
        :param user_id: The user's ID.
        :param money: The money addition. (It can be negative)"""

        await self.db.execute_query("UPDATE UserCurrency SET user_money = user_money + %s WHERE user_id = %s", (money, user_id))

    async def update_user_premium_money(self, user_id: int, money: int) -> None:
        """ Updates the user money.
        :param user_id: The user's ID.
        :param premium_money: The money addition. (It can be negative)"""

        await self.db.execute_query("UPDATE UserCurrency SET user_premium_money = user_premium_money + %s WHERE user_id = %s", (money, user_id))

    async def update_user_many_money(self, users: List[Tuple[int, int]]) -> None:
        """ Updates many the money of many users.
        :param users: The users to update the money. """

        await self.db.execute_query("UPDATE UserCurrency SET user_money = user_money + %s WHERE user_id = %s", users, execute_many=True)

    async def update_user_purchase_ts(self, user_id: int, the_time: int) -> None:
        """ Updates the user purchase timestamp.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        await self.db.execute_query("UPDATE UserCurrency SET last_purchase_ts = %s WHERE user_id = %s", (the_time, user_id))

    async def update_user_lotto_ts(self, user_id: int, the_time: int) -> None:
        """ Updates the user lotto timestamp.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        await self.db.execute_query("UPDATE UserCurrency SET user_lotto = %s WHERE user_id = %s", (the_time, user_id))

    async def update_user_hosted(self, user_id: int) -> None:
        """ Updates the user hosted classes counter.
        :param user_id: The user's ID. """

        await self.db.execute_query("UPDATE UserCurrency SET user_hosted = user_hosted + 1 WHERE user_id = %s", (user_id,))

    async def update_user_classes(self, user_id: int) -> None:
        """ Updates the user classes counter.
        :param user_id: The user's ID. """

        await self.db.execute_query("UPDATE UserCurrency SET user_classes = user_classes + 1 WHERE user_id = %s", (user_id,))

    async def update_user_class_reward(self, user_id: int) -> None:
        """ Updates the user reward classes counter.
        :param user_id: The user's ID. """

        await self.db.execute_query("UPDATE UserCurrency SET user_class_reward = user_class_reward + 1 WHERE user_id = %s", (user_id,))
