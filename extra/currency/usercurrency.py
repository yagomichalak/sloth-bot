import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class UserCurrencyTable(commands.Cog):
    """ Class for the UserCurrency table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_currency(self, ctx) -> None:
        """ (ADM) Creates the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if await self.check_user_currency_table_exists():
            return await ctx.send(f"**The `UserCurrency` table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE UserCurrency (
                user_id BIGINT NOT NULL, 
                user_money BIGINT DEFAULT 0, 
                last_purchase_ts BIGINT DEFAULT NULL,
                user_classes BIGINT DEFAULT 0, 
                user_class_reward BIGINT DEFAULT 0, 
                user_hosted BIGINT DEFAULT 0,
                user_lotto BIGINT DEFAULT NULL, 
                PRIMARY KEY (user_id))
            """)
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserCurrency` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_currency(self, ctx) -> None:
        """ (ADM) Drops the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_user_currency_table_exists():
            return await ctx.send(f"**The `UserCurrency` table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserCurrency")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserCurrency` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_currency(self, ctx) -> None:
        """ (ADM) Resets the UserCurrency table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_user_currency_table_exists():
            return await ctx.send(f"**The `UserCurrency` table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserCurrency")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserCurrency` reset, {member.mention}!**")

    # ===== SHOW =====
    async def check_user_currency_table_exists(self) -> bool:
        """ Checks whether the UserCurrency table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW STATUS LIKE 'UserCurrency'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== SELECT =====

    async def get_user_currency(self, user_id: int) -> List[List[int]]:
        """ Gets the user's currency info.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        return user_currency

    # ===== INSERT =====

    async def insert_user_currency(self, user_id: int, the_time: int) -> None:
        """ Inserts a user into the currency system.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO UserCurrency (user_id, user_money, last_purchase_ts) VALUES (%s, %s, %s)",
                               (user_id, 0, the_time))
        await db.commit()
        await mycursor.close()

    # ===== UPDATE =====
    async def update_user_money(self, user_id: int, money: int) -> None:
        """ Updates the user money.
        :param user_id: The user's ID.
        :param money: The money addition. (It can be negative)"""

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET user_money = user_money + %s WHERE user_id = %s", (money, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_many_money(self, users: List[int]) -> None:
        """ Updates many the money of many users.
        :param users: The users to update the money. """

        mycursor, db = await the_database()
        await mycursor.executemany("UPDATE UserCurrency SET user_money = user_money + %s WHERE user_id = %s", users)
        await db.commit()
        await mycursor.close()

    async def update_user_purchase_ts(self, user_id: int, the_time: int) -> None:
        """ Updates the user purchase timestamp.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET last_purchase_ts = %s WHERE user_id = %s", (the_time, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_lotto_ts(self, user_id: int, the_time: int) -> None:
        """ Updates the user lotto timestamp.
        :param user_id: The user's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET user_lotto = %s WHERE user_id = %s", (the_time, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_hosted(self, user_id: int) -> None:
        """ Updates the user hosted classes counter.
        :param user_id: The user's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET user_hosted = user_hosted + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_user_classes(self, user_id: int) -> None:
        """ Updates the user classes counter.
        :param user_id: The user's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET user_classes = user_classes + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_user_class_reward(self, user_id: int) -> None:
        """ Updates the user reward classes counter.
        :param user_id: The user's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET user_class_reward = user_class_reward + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()