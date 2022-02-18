import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Any
from extra import utils

class SlothAnalyticsTable(commands.Cog):
    """ Class for managing the SlothAnalytics table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_analytics(self, ctx) -> None:
        """ (ADM) Creates the SlothAnalytics table. """

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute(
            """CREATE TABLE SlothAnalytics (
                m_joined INT DEFAULT 0,
                m_left INT DEFAULT 0, 
                messages_sent INT DEFAULT 0,
                day_now VARCHAR(2) DEFAULT NULL
            )""")
        await db.commit()
        time_now = await utils.get_time_now()
        await mycursor.execute("INSERT INTO SlothAnalytics (day_now) VALUES (%s)", (time_now.day))
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *SlothAnalytics* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_analytics(self, ctx) -> None:
        """ (ADM) Drops the SlothAnalytics table. """

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SlothAnalytics")
        await db.commit()
        await mycursor.close()
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

        mycursor, db = await the_database()
        time_now = await utils.get_time_now()
        await mycursor.execute("UPDATE SlothAnalytics SET day_now = %s", (time_now.day,))
        await db.commit()
        await mycursor.close()

    async def update_joined(self) -> None:
        """ Updates the joined members counting. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET m_joined = m_joined + 1")
        await db.commit()
        await mycursor.close()

    async def update_left(self) -> None:
        """ Updates the left members counting. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET m_left = m_left + 1")
        await db.commit()
        await mycursor.close()

    async def update_messages(self) -> None:
        """ Updates the message counting. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET messages_sent = messages_sent + 1")
        await db.commit()
        await mycursor.close()

    async def update_day(self, day: str) -> None:
        """ Updates the day.
        :param day: The day it is. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET day_now = %s", (day,))
        await db.commit()
        await mycursor.close()

    async def check_relatory_time(self, time_now: str) -> bool:
        """ Checks the relatory time in the database, so it knows whether it should reset
        the data or not.
        :param time_now: The current time. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchone()
        await mycursor.close()
        if info and str(info[3]) != str(time_now):
            return True
        else:
            return False

    async def get_info(self) -> List[int]:
        """ Gets the analytics info. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchone()
        await mycursor.close()
        return info


class SlothAnalyticsTable(commands.Cog):
    """ Class for managing the SlothAnalytics table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_data_bumps(self, ctx) -> None:
        """ (ADM) Creates the DataBumps table. """

        if await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE DataBumps (
                m_joined BIGINT DEFAULT 0,
                m_left BIGINT DEFAULT 0, 
                messages BIGINT DEFAULT 0,
                members BIGINT DEFAULT 0, 
                online BIGINT DEFAULT 0, 
                complete_date VARCHAR(11) DEFAULT NULL
            )""")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `DataBumps` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_data_bumps(self, ctx) -> None:
        """ (ADM) Drops the DataBumps table. """

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE DataBumps")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `DataBumps` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_data_bumps(self, ctx) -> None:
        """ (ADM) Resets the DataBumps table. """

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM DataBumps")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `DataBumps` reset!**")

    async def table_data_bumps_exists(self) -> bool:
        """ Checks whether the DataBumps table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'DataBumps'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

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

        mycursor, db = await the_database()
        await mycursor.execute('''
            INSERT INTO DataBumps (
            m_joined, m_left, messages, members, online, complete_date)
            VALUES (%s, %s, %s, %s, %s, %s)''', (joined, left, messages, members, online, complete_date))
        await db.commit()
        await mycursor.close()

    async def get_monthly_total(self) -> List[int]:
        """ Gets all monthly total of members. """

        mycursor, _ = await the_database()

        await mycursor.execute("""
            SELECT Month(STR_TO_DATE(complete_date, '%d/%m/%Y')) AS Months,
                (SUM(m_joined) - SUM(m_left)) AS 'Totals Joinings',
                COUNT(*) AS 'Records',
                MAX(members) AS 'Members at the End'
            FROM DataBumps
            GROUP BY Months;
        """)

        months = await mycursor.fetchall()
        months = list(map(lambda e: e[3], months))
        await mycursor.close()
        return months

    async def get_daily_total(self) -> List[int]:
        """ Gets all daily total of members. """

        mycursor, _ = await the_database()

        await mycursor.execute("""
            SELECT STR_TO_DATE(complete_date, '%d/%m/%Y') AS Days,
                (SUM(m_joined) - SUM(m_left)) AS 'Totals Joinings',
                COUNT(*) AS 'Records',
                members AS 'Members at the End'
            FROM DataBumps
            GROUP BY Days;
        """)

        months = await mycursor.fetchall()
        months = list(map(lambda e: e[3], months))
        await mycursor.close()
        return months

    async def get_last_members_record(self) -> int:
        """ Gets the last record of total members. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT members FROM DataBumps ORDER BY members DESC LIMIT 1")
        last_record = await mycursor.fetchone()
        await mycursor.close()
        return 0 if not last_record else last_record[0]