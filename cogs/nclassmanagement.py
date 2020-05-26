import discord
from discord.ext import commands, tasks
from mysqldb import *
from mysqldb2 import the_data_base5
from datetime import datetime

announce_channel = 689918515129352213
server_id = 459195345419763713

class NClassManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('NClassManagement cog is ready!')
        self.check_new_announcements.start()


    @tasks.loop(seconds=60)
    async def check_new_announcements(self):
        if not await self.check_table_app_teachers_exists():
            return

        new_announcements = await self.get_new_announcements()
        if new_announcements:
            for na in new_announcements:
                guild = self.client.get_guild(server_id)
                member = discord.utils.get(guild.members, id=na[0])
                await self.nclass(ctx=None, teacher=member, language=na[1], day=na[2], time=na[3], type=na[4])
                await self.delete_new_announcement(teacher_id=na[0], language=na[1], day=na[2], time=na[3], type=na[4])


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_app_teachers(self, ctx):
        await ctx.message.delete()
        if await self.check_table_app_teachers_exists():
            return await ctx.send(f"**The table AppTeachers already exists!**", delete_after=3)
        mycursor, db = await the_data_base5()
        await mycursor.execute(
            "CREATE TABLE AppTeachers (teacher_id bigint, t_language varchar(22), t_day varchar(26), t_time varchar(15), t_type varchar(13))")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table AppTeachers created!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_app_teachers(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_app_teachers_exists():
            return await ctx.send(f"\t# - The table AppTeachers does not exist!")
        mycursor, db = await the_data_base5()
        await mycursor.execute("DROP TABLE AppTeachers")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table AppTeachers dropped!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_app_teachers(self, ctx=None):
        if ctx:
            await ctx.message.delete()
        if not await self.check_table_app_teachers_exists():
            return await ctx.send("**Table AppTeachers doesn't exist yet!**", delete_after=3)
        mycursor, db = await the_data_base5()
        await mycursor.execute("DELETE FROM AppTeachers")
        await db.commit()
        await mycursor.close()
        if ctx:
            await ctx.send("**Table AppTeachers reset!**", delete_after=3)

    async def delete_new_announcement(self, teacher_id: int, language: str, day: str, time: str, type: str):
        mycursor, db = await the_data_base5()
        await mycursor.execute(f"DELETE FROM AppTeachers WHERE teacher_id = {teacher_id} and t_language = '{language}' and t_day = '{day}' and t_time = '{time}' and t_type = '{type}'")
        await db.commit()
        await mycursor.close()

    async def get_new_announcements(self):
        mycursor, db = await the_data_base5()
        await mycursor.execute("SELECT * FROM AppTeachers")
        new_announcements = await mycursor.fetchall()
        await mycursor.close()
        return new_announcements
    

    async def check_table_app_teachers_exists(self):
        mycursor, db = await the_data_base5()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'AppTeachers'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True    

    # Add classes
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def nclass(self, ctx = None, teacher: discord.Member = None, language: str = None, day: str = None, time: str = None, type: str = None):
        if ctx:
            await ctx.message.delete()
            if not teacher:
                return await ctx.send("**Inform the teacher @ or ID!", delete_after=3)
            elif not language:
                return await ctx.send("**Inform a language!**", delete_after=3)
            elif not day:
                return await ctx.send("**Inform a day!**", delete_after=3)
            elif not time:
                return await ctx.send("**Inform the time!**", delete_after=3)

        guild = self.client.get_guild(server_id)
        embed = discord.Embed(title='Upcoming Class',
                              description=f":bust_in_silhouette: **Teacher:** {teacher.mention}\n:tongue: **Language:** {language.title()}\n:high_brightness: **Day:** {day.title()}\n:timer: **Time:** {time.upper()}\n:scroll: **Class Description:** {type.title()} class for {language.title()} learners.\n`RSVP with ✅`",
                              colour=discord.Colour.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=teacher.avatar_url)
        the_channel = discord.utils.get(guild.channels, id=announce_channel)
        role = discord.utils.get(guild.roles, name=f"Studying {language.title()}")
        if role:
            the_class = await the_channel.send(content=f"{teacher.mention}, {role.mention}", embed=embed)
        else:
            the_class = await the_channel.send(content=f"{teacher.mention}", embed=embed)
        await the_class.edit(content=":busts_in_silhouette: **Attendees:**```->```", embed=embed)
        await the_class.add_reaction('✅')
        await add_class_announcement(teacher.id, the_class.id)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def show_announ(self, ctx):
        await ctx.message.delete()
        announcements = await show_class_announcements()
        if len(announcements) > 0:
            embed = discord.Embed(title="Class Announcements:", description="__Available class announcements__",
                                  colour=discord.Colour.green(), timestamp=ctx.message.created_at)
            for ann in announcements:
                embed.add_field(name=f"Teacher id: {ann[0]}", value=f"Class id: {ann[1]}", inline=False)
        else:
            embed = discord.Embed(title="Class Announcements:", description="__No classes available!__",
                                  colour=discord.Colour.green(), timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def del_announ(self, ctx, class_id: int = None):
        await ctx.message.delete()
        if not class_id:
            return await ctx.send("**Inform the class id!**")

        announcements = await show_class_announcements()
        for announ in announcements:
            if announ[1] == class_id:
                await remove_announcement(announ[1])
                return await ctx.send(f"**Class announcement: `{class_id}` removed!**")
        else:
            await ctx.send("**Class announcement not found!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delall_announs(self, ctx):
        await ctx.message.delete()
        await remove_all_class_announcements()
        return await ctx.send("**All class announcements deleted!**")


def setup(client):
    client.add_cog(NClassManagement(client))
