import discord
from discord.ext import commands, tasks
from mysqldb import *
from datetime import datetime, timedelta
from pytz import timezone
from PIL import Image, ImageFont, ImageDraw
from typing import List
import os
import asyncio
from mysqldb import the_database



bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
select_your_language_channel_id = int(os.getenv('SELECT_YOUR_LANGUAGE_CHANNEL_ID'))


class Analytics(commands.Cog):
    '''
    A cog related to the analytics of the server.
    '''

    def __init__(self, client) -> None:
        self.client = client
        self.dnk_id: int = int(os.getenv('DNK_ID'))

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Analytics cog is online!")
        self.check_midnight.start()

    @tasks.loop(minutes=1)
    async def check_midnight(self) -> None:
        time_now = datetime.now()
        tzone = timezone("Etc/GMT-1")
        date_and_time = time_now.astimezone(tzone)
        day = date_and_time.strftime('%d')

        if await self.check_relatory_time(day):
            await self.update_day(day)
            channel = self.client.get_channel(bots_and_commands_channel_id)
            members = channel.guild.members
            info = await self.get_info()
            online_members = [om for om in members if str(om.status) == "online"]
            small = ImageFont.truetype("built titling sb.ttf", 45)
            analytics = Image.open("./png/analytics.png").resize((500, 600))
            draw = ImageDraw.Draw(analytics)
            draw.text((140, 270), f"{info[0][0]}", (255, 255, 255), font=small)
            draw.text((140, 335), f"{info[0][1]}", (255, 255, 255), font=small)
            draw.text((140, 395), f"{info[0][2]}", (255, 255, 255), font=small)
            draw.text((140, 460), f"{len(members)}", (255, 255, 255), font=small)
            draw.text((140, 520), f"{len(online_members)}", (255, 255, 255), font=small)
            analytics.save('./png/analytics_result.png', 'png', quality=90)
            await channel.send(file=discord.File('./png/analytics_result.png'))

            await self.reset_table_sloth_analytics()
            complete_date = date_and_time.strftime('%d/%m/%Y')
            await self.bump_data(info[0][0], info[0][1], info[0][2], len(members), len(online_members), str(complete_date))

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        channel = discord.utils.get(member.guild.channels, id=select_your_language_channel_id)
        await channel.send(
            f'''Hello {member.mention} ! Scroll up and choose your Native Language by clicking in the flag that best represents it!
<:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449>''',
            delete_after=120)
        await self.update_joined()

    @commands.Cog.listener()
    async def on_member_remove(self, member) -> None:
        return await self.update_left()

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if not message.guild:
            return

        return await self.update_messages()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def stop_task(self, ctx) -> None:
        await ctx.message.delete()
        self.check_midnight.stop()
        return await ctx.send("**Analytics task has been stopped!**", delete_after=3)

    async def bump_data(self, joined: int, left: int, messages: int, members: int, online: int,
                        complete_date: str) -> None:
        '''
        Bumps the data from the given day to the database.
        '''
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
        '''
        (ADM) Creates the SlothAnalytics table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute(
            f"CREATE TABLE SlothAnalytics (m_joined int default 0, m_left int default 0, messages_sent int default 0, day_now VARCHAR(2))")
        await db.commit()
        time_now = datetime.now()
        tzone = timezone("CET")
        date_and_time = time_now.astimezone(tzone)
        day = date_and_time.strftime('%d')
        await mycursor.execute("INSERT INTO SlothAnalytics (day_now) VALUES (%s)", (day))
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *SlothAnalytics* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_analytics(self, ctx) -> None:
        '''
        (ADM) Drops the SlothAnalytics table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SlothAnalytics")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *SlothAnalytics* dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_analytics(self, ctx=None) -> None:
        '''
        (ADM) Resets the SlothAnalytics table.
        '''
        if ctx:
            await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothAnalytics")
        await db.commit()  # IDK
        time_now = datetime.now()
        tzone = timezone("CET")
        date_and_time = time_now.astimezone(tzone)
        day = date_and_time.strftime('%d')
        await mycursor.execute("INSERT INTO SlothAnalytics (day_now) VALUES (%s)", (day))
        await db.commit()
        await mycursor.close()
        if ctx:
            return await ctx.send("**Table *SlothAnalytics* reset!**", delete_after=3)

    async def update_joined(self) -> None:
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET m_joined = m_joined + 1")
        await db.commit()
        await mycursor.close()

    async def update_left(self) -> None:
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET m_left = m_left + 1")
        await db.commit()
        await mycursor.close()

    async def update_messages(self) -> None:
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothAnalytics SET messages_sent = messages_sent + 1")
        await db.commit()
        await mycursor.close()

    async def update_day(self, day: str) -> None:
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE SlothAnalytics SET day_now = '{day}'")
        await db.commit()
        await mycursor.close()

    async def check_relatory_time(self, time_now: str) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
        await mycursor.close()
        if str(info[0][3]) != str(time_now):
            return True
        else:
            return False

    async def get_info(self) -> List[int]:
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
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
        await mycursor.execute('''
            CREATE TABLE DataBumps (
            m_joined BIGINT, m_left BIGINT, messages BIGINT, members BIGINT, online BIGINT, complete_date VARCHAR(11)
            )''')
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

    #==========================================#


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


    async def get_current_day_and_future_day(self, date: datetime, days: int) -> str:
        """ Gets the current day and the future day, by incrementing X days to the current day.
        :param days: The amount of days to be incremented. """

        tzone = timezone('Etc/GMT-1')
        # current_date_and_time = datetime.now().astimezone(tzone)
        date = datetime.strptime(date, '%d/%m/%Y')
        future_date_and_time = date + timedelta(days=days)

        last_day = date.strftime('%d/%m/%Y')
        future_day = future_date_and_time.strftime('%d/%m/%Y')
        # print(current_day)
        # print(future_day)
        return last_day, future_day

    async def predict_total_members(self, date: datetime, present: int, future: int, pr: float) -> int:
        """ Predicts the total of members in days. 
        :param present: The current value.
        :param future: The goal value. 
        :param the percentage growth rate. """

        count = 0
        compound = present
        # print('-'*20)
        while True:

            if compound >= future:
                break

            count += 1
            
            # print(f"Present: {round(compound)}")
            compound += (compound * pr)/100
            # print(f"Present+PR: {round(compound)}")
            # print('-'*20)

        last_day, future_day = await self.get_current_day_and_future_day(date=date, days=count)
        # message = await self.make_message(present=present, today=today, future=futre, future_day=future_day, count=int)
        # return f"""{present} ({today})\n↓ in {count} days!\n{future} ({future_day})"""
        line1 = f"{'Present:':<8} {present} members. Date: ({last_day})"
        line2 = f"|↓ in {count} day(s) ↓|"
        line3 = f"{'Future:':<8} {future} members. Date: ({future_day})"
        return f"{line1}\n{line2:^39}\n{line3}"

    async def get_last_members_record(self) -> int:
        """ Gets the last record of total members. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT members, complete_date FROM DataBumps ORDER BY members DESC LIMIT 1")
        last_record = await mycursor.fetchone()
        await mycursor.close()
        return last_record[0], last_record[1]



    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def when(self, ctx, future: int = None) -> None:
        """ Estimates and predicts when the server will hit the given amount of members.
        :param future: The goal value. """

        if not future:
            return await ctx.send("**Please, inform a future value (goal value)!**")

        if len(future) > 6:
            return await ctx.send("**Don't try to troll!**")

        # await calculate_monthly()
        pr_list = await self.calculate_daily()
        pr_average = sum(pr_list)/ len(pr_list)
        last_record, complete_date = await self.get_last_members_record()

        if last_record >= future:
            return await ctx.send("**It looks like the server already reached that number!**")
        prediction = await self.predict_total_members(
            date=complete_date, present=last_record, future=future, pr=pr_average
        )

        embed = discord.Embed(
            title="Future Value Esimation",
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
    client.add_cog(Analytics(client))
