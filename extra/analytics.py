from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union
from extra import utils
from datetime import datetime


class SlothAnalyticsTable(commands.Cog):
    """ Class for managing the SlothAnalytics table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_analytics(self, ctx) -> None:
        """ (ADM) Creates the SlothAnalytics table. """

        await ctx.message.delete()
        await self.db.execute_query(
            """CREATE TABLE SlothAnalytics (
                m_joined INT DEFAULT 0,
                m_left INT DEFAULT 0, 
                messages_sent INT DEFAULT 0,
                day_now VARCHAR(2) DEFAULT NULL
            )""")
        time_now = await utils.get_time_now()
        await self.db.execute_query("INSERT INTO SlothAnalytics (day_now) VALUES (%s)", (time_now.day))
        return await ctx.send("**Table *SlothAnalytics* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_analytics(self, ctx) -> None:
        """ (ADM) Drops the SlothAnalytics table. """

        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE SlothAnalytics")
        return await ctx.send("**Table *SlothAnalytics* dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_analytics(self, ctx = None) -> None:
        """ (ADM) Resets the SlothAnalytics table. (Callback) """

        await ctx.message.delete()
        await self.reset_table_sloth_analytics_callback()
        return await ctx.send("**Table *SlothAnalytics* reset!**", delete_after=3)

    async def reset_table_sloth_analytics_callback(self) -> None:
        """ (ADM) Resets the SlothAnalytics table. (Callback) """

        time_now = await utils.get_time_now()
        await self.db.execute_query("UPDATE SlothAnalytics SET day_now = %s, m_joined = 0, m_left = 0, messages_sent = 0", (time_now.day,))

    async def update_joined(self) -> None:
        """ Updates the joined members counting. """

        await self.db.execute_query("UPDATE SlothAnalytics SET m_joined = m_joined + 1")

    async def update_left(self) -> None:
        """ Updates the left members counting. """

        await self.db.execute_query("UPDATE SlothAnalytics SET m_left = m_left + 1")

    async def update_messages(self) -> None:
        """ Updates the message counting. """

        await self.db.execute_query("UPDATE SlothAnalytics SET messages_sent = messages_sent + 1")

    async def update_day(self, day: str) -> None:
        """ Updates the day.
        :param day: The day it is. """

        await self.db.execute_query("UPDATE SlothAnalytics SET day_now = %s", (day,))

    async def check_relatory_time(self, time_now: str) -> bool:
        """ Checks the relatory time in the database, so it knows whether it should reset
        the data or not.
        :param time_now: The current time. """

        info = await self.db.execute_query("SELECT * from SlothAnalytics", fetch="one")
        if info and str(info[3]) != str(time_now):
            return True
        return False

    async def get_info(self) -> List[int]:
        """ Gets the analytics info. """

        return await self.db.execute_query("SELECT * from SlothAnalytics", fetch="one")


class DataBumpsTable(commands.Cog):
    """ Class for managing the DataBumps table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_data_bumps(self, ctx) -> None:
        """ (ADM) Creates the DataBumps table. """

        if await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` already exists!**")

        await self.db.execute_query("""
            CREATE TABLE DataBumps (
                m_joined BIGINT DEFAULT 0,
                m_left BIGINT DEFAULT 0, 
                messages BIGINT DEFAULT 0,
                members BIGINT DEFAULT 0, 
                online BIGINT DEFAULT 0, 
                complete_date VARCHAR(11) DEFAULT NULL
            )""")
        return await ctx.send("**Table `DataBumps` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_data_bumps(self, ctx) -> None:
        """ (ADM) Drops the DataBumps table. """

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist!**")

        await self.db.execute_query("DROP TABLE DataBumps")
        return await ctx.send("**Table `DataBumps` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_data_bumps(self, ctx) -> None:
        """ (ADM) Resets the DataBumps table. """

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM DataBumps")
        await ctx.send("**Table `DataBumps` reset!**")

    async def table_data_bumps_exists(self) -> bool:
        """ Checks whether the DataBumps table exists. """

        return await self.db.table_exists("DataBumps")

    async def bump_data(self, 
        joined: int, left: int, messages: int, 
        members: int, online: int, complete_date: str) -> None:
        """ Bumps the data from the given day to the database.
        :param joined: The joined members counter.
        :param left: The left members counter.
        :param messages: The messages counter.
        :param members: The members counter.
        :param online: The online members counter.
        :param complete_date: The complete date referring to the data. """

        await self.db.execute_query('''
            INSERT INTO DataBumps (
            m_joined, m_left, messages, members, online, complete_date)
            VALUES (%s, %s, %s, %s, %s, %s)''', (joined, left, messages, members, online, complete_date))

    async def get_monthly_total(self) -> List[int]:
        """ Gets all monthly total of members. """


        months = await self.db.execute_query("""
            SELECT Month(STR_TO_DATE(complete_date, '%d/%m/%Y')) AS Months,
                (SUM(m_joined) - SUM(m_left)) AS 'Totals Joinings',
                COUNT(*) AS 'Records',
                MAX(members) AS 'Members at the End'
            FROM DataBumps
            GROUP BY Months;
        """, fetch="all")

        months = list(map(lambda e: e[3], months))
        return months

    async def get_daily_total(self) -> List[int]:
        """ Gets all daily total of members. """


        months = await self.db.execute_query("""
            SELECT STR_TO_DATE(complete_date, '%d/%m/%Y') AS Days,
                (SUM(m_joined) - SUM(m_left)) AS 'Totals Joinings',
                COUNT(*) AS 'Records',
                members AS 'Members at the End'
            FROM DataBumps
            GROUP BY Days;
        """, fetch="all")

        months = list(map(lambda e: e[3], months))
        return months

    async def get_last_members_record(self) -> int:
        """ Gets the last record of total members. """

        last_record = await self.db.execute_query("SELECT members FROM DataBumps ORDER BY members DESC LIMIT 1", fetch="one")
        return 0 if not last_record else last_record[0]

    async def get_month_statuses(self) -> List[Union[datetime, str, int]]:
        """ Gets months statuses. """

        return await self.db.execute_query("""
            SELECT
                STR_TO_DATE(complete_date, '%d/%m/%Y') AS Months,
                SUM(m_joined) - SUM(m_left) AS 'Total Joins',
                members AS 'First Member Record of the Month',
                MAX(members) AS 'Last Member Record of the Month'
            FROM DataBumps
            GROUP BY YEAR(Months), MONTH(Months)
        """, fetch="all")
