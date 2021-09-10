import discord
from discord import utils
from discord.ext import commands, tasks
from mysqldb import the_database

from datetime import datetime, timedelta
from extra import utils

from PIL import Image, ImageFont, ImageDraw
from typing import List
import os
import io

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
select_your_language_channel_id = int(os.getenv('SELECT_YOUR_LANGUAGE_CHANNEL_ID'))


class Analytics(commands.Cog):
    """ A cog related to the analytics of the server. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client
        self.dnk_id: int = int(os.getenv('DNK_ID'))

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog's ready to be used. """

        print("Analytics cog is online!")
        self.check_midnight.start()

    @tasks.loop(minutes=1)
    async def check_midnight(self) -> None:
        """ Checks whether it's midnight. """

        time_now = await utils.get_time_now()
        day = time_now.day
        if await self.check_relatory_time(day):
            await self.update_day(day)
            channel = self.client.get_channel(bots_and_commands_channel_id)
            members = channel.guild.members
            info = await self.get_info()
            online_members = [om for om in members if str(om.status) == "online"]
            small = ImageFont.truetype("built titling sb.ttf", 45)
            analytics = Image.open("./png/analytics.png").resize((500, 600))
            draw = ImageDraw.Draw(analytics)
            draw.text((140, 270), f"{info[0]}", (255, 255, 255), font=small)
            draw.text((140, 335), f"{info[1]}", (255, 255, 255), font=small)
            draw.text((140, 395), f"{info[2]}", (255, 255, 255), font=small)
            draw.text((140, 460), f"{len(members)}", (255, 255, 255), font=small)
            draw.text((140, 520), f"{len(online_members)}", (255, 255, 255), font=small)

            with io.BytesIO() as fp:
                analytics.save(fp, 'png', quality=90)
                fp.seek(0)
                fp = discord.File(fp, filename="analytics_result.png")
                await channel.send(file=fp)

            try:
                await self.reset_table_sloth_analytics_callback()
                complete_date = time_now.strftime('%d/%m/%Y')
                await self.bump_data(info[0], info[1], info[2], len(members), len(online_members), str(complete_date))
            except Exception as e:
                print('SlothAnalytics error', e)
                print('aah')

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        """ Tells the newcomer to assign themselves a native language role, and updates the joined members counter. """

        channel = discord.utils.get(member.guild.channels, id=select_your_language_channel_id)
        await channel.send(
            f"""Hello {member.mention} ! Scroll up and choose your Native Language by clicking in the flag that best represents it!
<:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449>""",
            delete_after=120)
        await self.update_joined()

    @commands.Cog.listener()
    async def on_member_remove(self, member) -> None:
        """ Updates the let members counter. """

        await self.update_left()

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """ Updates the messages counter. """

        if not message.guild:
            return

        await self.update_messages()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def stop_task(self, ctx) -> None:
        """ Stops the midnight-checker task. """

        await ctx.message.delete()
        self.check_midnight.stop()
        return await ctx.send("**Analytics task has been stopped!**", delete_after=3)

    async def bump_data(self, joined: int, left: int, messages: int, members: int, online: int,
                        complete_date: str) -> None:
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

    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_analytics(self, ctx) -> None:
        """ (ADM) Creates the SlothAnalytics table. """

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute(
            "CREATE TABLE SlothAnalytics (m_joined int default 0, m_left int default 0, messages_sent int default 0, day_now VARCHAR(2))")
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
        """ (ADM) Resets the SlothAnalytics table. (Callback)"""


        await ctx.message.delete()
        await self.reset_table_sloth_analytics_callback()
        return await ctx.send("**Table *SlothAnalytics* reset!**", delete_after=3)

    async def reset_table_sloth_analytics_callback(self) -> None:
        """ (ADM) Resets the SlothAnalytics table. (Callback)"""

        mycursor, db = await the_database()
        time_now = await utils.get_time_now()
        await mycursor.execute("""
            UPDATE SlothAnalytics SET day_now = %s, m_joined = 0, m_left = 0,
            messages_sent = 0
        """, (time_now.day,))
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

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
        await mycursor.close()
        if str(info[0][3]) != str(time_now):
            return True
        else:
            return False

    async def get_info(self) -> List[int]:
        """ Gets the analytics info. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchone()
        await mycursor.close()
        return info

    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_data_bumps(self, ctx) -> None:
        """ (DNK) Creates the DataBumps table. """

        if ctx.author.id != self.dnk_id:
            return await ctx.send("**You're not DNK!**")

        if await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE DataBumps (
            m_joined BIGINT, m_left BIGINT, messages BIGINT, members BIGINT, online BIGINT, complete_date VARCHAR(11)
            )""")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `DataBumps` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_data_bumps(self, ctx) -> None:
        """ (DNK) Drops the DataBumps table. """
        if ctx.author.id != self.dnk_id:
            return await ctx.send("**You're not DNK!**")

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE DataBumps")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `DataBumps` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_data_bumps(self, ctx) -> None:
        """ (DNK) Resets the DataBumps table. """

        if ctx.author.id != self.dnk_id:
            return await ctx.send("**You're not DNK!**")

        if not await self.table_data_bumps_exists():
            return await ctx.send("**The table `DataBumps` doesn't exist yet!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM DataBumps")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `DataBumps` reset!**")

    async def table_data_bumps_exists(self) -> bool:
        """ Checks whether the DataBumps table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'DataBumps'")
        exists = await mycursor.fetchall()
        await mycursor.close()
        if len(exists) == 0:
            return False
        else:
            return True

    # ==========================================#

    async def get_monthly_total(self) -> List[int]:
        """ Gets all monthly total of members. """

        mycursor, db = await the_database()

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
        # pprint(months)
        return months

    async def get_daily_total(self) -> List[int]:
        """ Gets all daily total of members. """

        mycursor, db = await the_database()

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
        # pprint(months)
        return months

    async def growth_percentage(self, present: int, past: int) -> float:
        """ Gets the growth percentage of a value compared to another one.
        :param present: The current value.
        :param past: The old value to which you wanna compare. """

        # PR = Percent Rate
        pr = ((present - past) / past) * 100
        return pr

    async def calculate_monthly(self) -> List[float]:
        """ Calculates, shows and returns the growth percentage rate of all months. """

        pr_list: List[float] = []
        total_month_members = await self.get_monthly_total()
        # print('='*45)
        for i, month in enumerate(total_month_members):
            first_line = f"Month: {i+1} | Total Members: {month}"
            # print(f"{first_line:^45}")
            if i != 0 and (i-1) % 2 == 0 and (i-1) < len(total_month_members):
                pr = await self.growth_percentage(total_month_members[i], total_month_members[i-1])
                pr_list.append(pr)
                # print(f'\tGrowth increase: {pr:.2f}% ({total_month_members[i-1]} → {total_month_members[i]})')
                # print('='*45)

        return pr_list

    async def calculate_daily(self) -> List[float]:
        """ Calculates, shows and returns the growth percentage rate of all days. """

        pr_list: List[float] = []
        total_day_members = await self.get_daily_total()
        # print('='*45)
        for i, day in enumerate(total_day_members):
            first_line = f"Day: {i+1} | Total Members: {day}"
            # print(f"{first_line:^45}")
            if i != 0 and (i-1) % 2 == 0 and (i-1) < len(total_day_members):
                pr = await self.growth_percentage(total_day_members[i], total_day_members[i-1])
                pr_list.append(pr)
                # print(f'\tGrowth increase: {pr:.2f}% ({total_day_members[i-1]} → {total_day_members[i]})')
                # print('='*45)

        return pr_list

    async def get_current_day_and_future_day(self, days: int, hours: int) -> str:
        """ Gets the current day and the future day, by incrementing X days to the current day.
        :param days: The amount of days to be incremented.
        :param hours: The amount of hours to be incremented. """

        time_now = await utils.get_time_now()
        future_date_and_time = time_now + timedelta(days=days, hours=hours)

        last_day = time_now.strftime('%d/%m/%Y at %H')
        future_day = future_date_and_time.strftime('%d/%m/%Y at %H')
        return last_day, future_day

    async def predict_total_members(self, present: int, future: int, pr: float) -> int:
        """ Predicts the total of members in days.
        :param present: The current value.
        :param future: The goal value.
        :param the percentage growth rate. """

        count = 0
        hours = 0
        current_compound = temp_value = present
        # print('-'*20)
        time_now = await utils.get_time_now()

        while True:

            # PR (Percentage Rate)
            pr_compound = (current_compound * pr) / 100

            # Sum of PR and current compound
            sum_both = current_compound + pr_compound

            # Sees whether the sum of PR and current value are >= the future value
            if sum_both >= future:
                pr_divided = pr_compound / 24
                remaining_hours = 24
                if time_now.hour != 0 and count == 0:
                    remaining_hours = 24 - time_now.hour

                # Divides the remaining PR by 24 hours
                remaining_pr = pr_compound / 24

                # Loops through each remaining hour of that day, so the data is hour-precise
                for _ in range(remaining_hours):
                    sum_remaining = current_compound + remaining_pr
                    current_compound = sum_remaining
                    hours += 1

                    # If the current compound is >= the future value, break the loop
                    if sum_remaining >= future:
                        break

                break

            # If none of the conditions are satisfied, starts another iteration of another looping
            current_compound = sum_both
            count += 1

        last_day, future_day = await self.get_current_day_and_future_day(count, hours)
        line1 = f"{'Present:':<8} {present} members. Date: ({last_day})"
        line2 = f"|↓ in {count} day(s) and {hours} hours ↓|"
        line3 = f"{'Future:':<8} {future} members. Date: ({future_day})"
        return f"{line1}\n{line2:^48}\n{line3}"

    async def get_last_members_record(self) -> int:
        """ Gets the last record of total members. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT members FROM DataBumps ORDER BY members DESC LIMIT 1")
        last_record = await mycursor.fetchone()
        await mycursor.close()
        return last_record[0]

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def when(self, ctx, future: int = None) -> None:
        """ Estimates and predicts when the server will hit the given amount of members.
        :param future: The goal value. """

        if not future:
            return await ctx.send("**Please, inform a future value (goal value)!**")

        if len(str(future)) > 6:
            return await ctx.send("**Don't try to troll!**")

        # await calculate_monthly()
        pr_list = await self.calculate_daily()
        pr_average = sum(pr_list) / len(pr_list)
        if pr_average <= 0:
            return await ctx.send(f"**I'm afraid I can't calculate it, because you have a negative PR of `{round(pr_average, 2)}%`**")
        # last_record = await self.get_last_members_record()
        last_record = len(ctx.guild.members)

        if last_record >= future:
            return await ctx.send("**It looks like the server already reached that number!**")
        prediction = await self.predict_total_members(
            present=last_record, future=future, pr=pr_average
        )

        embed = discord.Embed(
            title="Future Value Estimation",
            description=f"Considering an average Growth Percentage Rate of `{round(pr_average, 2)}%`",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )

        embed.add_field(
            name="="*59,
            value=f"```apache\n{prediction}```**{'='*59}**"
        )

        await ctx.send(embed=embed)


def setup(client):
    """ Cog's setup function. """

    client.add_cog(Analytics(client))
