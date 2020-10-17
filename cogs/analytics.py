import discord
from discord.ext import commands, tasks
from mysqldb2 import *
from datetime import datetime
from pytz import timezone
from PIL import Image, ImageFont, ImageDraw
from typing import List

bots_and_commands_channel_id = 562019654017744904
select_your_language_channel_id = 695491104417513552


class Analytics(commands.Cog):
    '''
    A cog related to the analytics of the server.
    '''

    def __init__(self, client) -> None:
        self.client = client
        self.dnk_id: int = 647452832852869120

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Analytics cog is online!")
        self.check_midnight.start()

    @tasks.loop(minutes=1)
    async def check_midnight(self) -> None:
        time_now = datetime.now()
        tzone = timezone("CET")
        date_and_time = time_now.astimezone(tzone)
        # hour = date_and_time.strftime('%H:%M')
        day = date_and_time.strftime('%d')
        if await self.check_relatory_time(day):
            await self.update_day(day)
            # channel = await self.client.fetch_channel(bots_and_commands_channel_id)
            channel = self.client.get_channel(bots_and_commands_channel_id)
            members = channel.guild.members
            info = await self.get_info()
            online_members = [om for om in members if str(om.status) == "online"]
            small = ImageFont.truetype("built titling sb.ttf", 45)
            analytics = Image.open("analytics2.png").resize((500, 600))
            draw = ImageDraw.Draw(analytics)
            draw.text((140, 270), f"{info[0][0]}", (255, 255, 255), font=small)
            draw.text((140, 335), f"{info[0][1]}", (255, 255, 255), font=small)
            draw.text((140, 395), f"{info[0][2]}", (255, 255, 255), font=small)
            draw.text((140, 460), f"{len(members)}", (255, 255, 255), font=small)
            draw.text((140, 520), f"{len(online_members)}", (255, 255, 255), font=small)
            analytics.save('analytics_result.png', 'png', quality=90)
            await channel.send(file=discord.File('analytics_result.png'))

            await self.reset_table_sloth_analytics()
            complete_date = date_and_time.strftime('%d/%m/%Y')
            await self.bump_data(info[0][0], info[0][1], info[0][1], len(members), len(online_members), str(complete_date))

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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET m_joined = m_joined + 1")
        await db.commit()
        await mycursor.close()

    async def update_left(self) -> None:
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET m_left = m_left + 1")
        await db.commit()
        await mycursor.close()

    async def update_messages(self) -> None:
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET messages_sent = messages_sent + 1")
        await db.commit()
        await mycursor.close()

    async def update_day(self, day: str) -> None:
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE SlothAnalytics SET day_now = '{day}'")
        await db.commit()
        await mycursor.close()

    async def check_relatory_time(self, time_now: str) -> bool:
        mycursor, db = await the_data_base3()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
        if str(info[0][3]) != str(time_now):
            return True
        else:
            return False

    async def get_info(self) -> List[int]:
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
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
        mycursor, db = await the_data_base3()
        await mycursor.execute("DELETE FROM DataBumps")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `DataBumps` reset!**")

    async def table_data_bumps_exists(self) -> bool:
        """ Checks whether the DataBumps table exists. """

        mycursor, db = await the_data_base3()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'DataBumps'")
        exists = await mycursor.fetchall()
        await mycursor.close()
        if len(exists) == 0:
            return False
        else:
            return True


def setup(client):
    client.add_cog(Analytics(client))
