import discord
from discord.ext import commands, tasks
from mysqldb2 import *
from datetime import datetime
from pytz import timezone
from PIL import Image, ImageFont, ImageDraw

bots_and_commands_channel_id = 562019654017744904
select_your_language_channel_id = 695491104417513552

class Analytics(commands.Cog):
    '''
    A cog related to the analytics of the server.
    '''

    def __init__(self, client):
        self.client = client
        self.check_midnight.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Analytics cog is online!")


    @tasks.loop(minutes=1)
    async def check_midnight(self):
        time_now = datetime.now()
        tzone = timezone("CET")
        date_and_time = time_now.astimezone(tzone)
        hour = date_and_time.strftime('%H:%M')
        day = date_and_time.strftime('%d')
        if await self.check_relatory_time(day):
            await self.update_day(day)
            channel = self.client.get_channel(bots_and_commands_channel_id)
            members = channel.guild.members
            info = await self.get_info()
            online_members = [om for om in members if str(om.status) == "online"]
            small = ImageFont.truetype("built titling sb.ttf", 45)
            analytics = Image.open("analytics2.png")
            draw = ImageDraw.Draw(analytics)
            draw.text((140, 270), f"{info[0][0]}", (255, 255, 255), font=small)
            draw.text((140, 335), f"{info[0][1]}", (255, 255, 255), font=small)
            draw.text((140, 395), f"{info[0][2]}", (255, 255, 255), font=small)
            draw.text((140, 460), f"{len(members)}", (255, 255, 255), font=small)
            draw.text((140, 520), f"{len(online_members)}", (255, 255, 255), font=small)
            analytics.save('analytics_result.png', 'png', quality=90)
            await channel.send(file=discord.File('analytics_result.png'))
            return await self.reset_table_sloth_analytics()


    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, id=select_your_language_channel_id)
        await channel.send(f'''Hello {member.mention} ! Scroll up and choose your Native Language by clicking in the flag that best represents it!
<:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449> <:zarrowup:688222444292669449>''', delete_after=120)
        await self.update_joined()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        return await self.update_left()

    @commands.Cog.listener()
    async def on_message(self, message):
        return await self.update_messages()


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def stop_task(self, ctx):
        await ctx.message.delete()
        self.check_midnight.stop()
        return await ctx.send("**Analytics task has been stopped!**", delete_after=3)
        
    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_analytics(self, ctx):
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
    async def drop_table_sloth_analytics(self, ctx):
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
    async def reset_table_sloth_analytics(self, ctx = None):
        '''
        (ADM) Resets the SlothAnalytics table.
        '''
        if ctx:
            await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute("DROP TABLE SlothAnalytics")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE SlothAnalytics (m_joined int default 0, m_left int default 0, messages_sent int default 0, day_now VARCHAR(2))")
        await db.commit()
        time_now = datetime.now()
        tzone = timezone("CET")
        date_and_time = time_now.astimezone(tzone)
        day = date_and_time.strftime('%d')
        await mycursor.execute("INSERT INTO SlothAnalytics (day_now) VALUES (%s)", (day))
        await db.commit()
        await mycursor.close()
        if ctx:
            return await ctx.send("**Table *SlothAnalytics* reseted!**", delete_after=3)

    async def update_joined(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET m_joined = m_joined + 1")
        await db.commit()
        await mycursor.close()

    async def update_left(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET m_left = m_left + 1")
        await db.commit()
        await mycursor.close()

    async def update_messages(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute("UPDATE SlothAnalytics SET messages_sent = messages_sent + 1")
        await db.commit()
        await mycursor.close()

    async def update_day(self, day: str):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE SlothAnalytics SET day_now = '{day}'")
        await db.commit()
        await mycursor.close()

    async def check_relatory_time(self, time_now: str):
        mycursor, db = await the_data_base3()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
        if str(info[0][3]) != str(time_now):
            return True
        else:
            return False

    async def get_info(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute("SELECT * from SlothAnalytics")
        info = await mycursor.fetchall()
        await mycursor.close()
        return info


def setup(client):
    client.add_cog(Analytics(client))
