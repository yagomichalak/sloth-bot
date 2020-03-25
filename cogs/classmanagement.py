import discord
from discord.ext import commands
from mysqldb import *


class ClassManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ClassManagement cog is ready.')

    # Add classes
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_class(self, ctx, language: str, teacher: str, day: str, time: str, type: str, forr: str = None):
        teachers = await show_teachers()
        if not forr:
            forr = 'General people'
        await add_teacher_class(len(teachers) + 1, language.title(), teacher.title(), day.title(), time.upper(),
                                type.title(), forr.title())
        await ctx.send(f"{teacher.title()}'s class successfully added!")

    # Remove classes
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_class(self, ctx, id: str = None):
        if not id:
            return await ctx.send('Inform the id!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await remove_teacher_class(id)
                return await ctx.send(f"{teacher[2]}'s class successfully removed!")
        else:
            await ctx.send('Teacher not found!')

    # Updates the class' language
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_class(self, ctx, id: str = None, language: str = None):
        if id is None or language is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_language(id, language.title())
                return await ctx.send(f"Teacher's **class** updated!")
        else:
            await ctx.send('Teacher not found')

    # Updates the class' name
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_name(self, ctx, id: str = None, name: str = None):
        if id is None or name is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_name(id, name.title())
                return await ctx.send(f"Teacher's **name** updated!")
        else:
            await ctx.send('Teacher not found')

    # Updates the class' day
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_day(self, ctx, id: str = None, day: str = None):
        if id is None or day is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_day(id, day.title())
                return await ctx.send(f"Teacher's **day** updated!")
        else:
            await ctx.send('Teacher not found')

    # Updates the class' time
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_time(self, ctx, id: str = None, time: str = None):
        if id is None or time is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')
        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_time(id, time.upper())
                return await ctx.send(f"Teacher's **time** updated!")
        else:
            await ctx.send('Teacher not found')

    # Updates the class' type
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_type(self, ctx, id: str = None, type: str = None):
        if id is None or type is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_type(id, type.title())
                return await ctx.send(f"Teacher's **type** updated!")
        else:
            await ctx.send('Teacher not found')

    # Updates the class' aiming public
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_public(self, ctx, id: str = None, forr: str = None):
        if id is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')
        elif not forr:
            forr = 'General people'

        teachers = await show_teachers()
        for teacher in teachers:
            if id == str(teacher[0]):
                await edit_teacher_class_forr(id, forr.title())
                return await ctx.send(f"Teacher's **public** updated!")
        else:
            await ctx.send('Teacher not found')

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def exception(self, ctx):
        await ctx.message.delete()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = ['1AM', '3AM', '12PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM']
        teachers = await show_teachers()
        events = await show_events()
        embed = discord.Embed(title='Excepted Classes & Events',
                              description='All classes and events that cannot be inserted into the calendar.',
                              colour=discord.Colour.dark_green())
        for teacher in teachers:
            if teacher[3] not in days or teacher[4] not in hours:
                embed.add_field(name=f'{teacher[0]} - {teacher[1]}',
                                value=f"{teacher[2]} | {teacher[3]} | {teacher[4]} | {teacher[5]} | {teacher[6]}",
                                inline=False)

        for event in events:
            if event[2] not in days or event[3] not in hours:
                embed.add_field(name=f'{event[0]} - {event[1]}', value=f"{event[2]} | {event[3]}", inline=False)

        if len(embed.fields) == 0:
            embed.add_field(name='None', value='No exceptions.', inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def repeated(self, ctx):
        await ctx.message.delete()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = ['1AM', '3AM', '12PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM']
        teachers1 = teachers2 = await show_teachers()
        events = await show_events()
        dupes = []
        embed = discord.Embed(title="Repeated values",
                              description="All classes and events that have values equal to others'",
                              colour=discord.Colour.dark_green())
        for teacher1 in teachers1:
            for teacher2 in teachers2:
                if teacher1[0] != teacher2[0] and teacher1[3] == teacher2[3] and teacher1[4] == teacher2[4] and \
                        teacher1[
                            3] in days and teacher1[4] in hours:
                    dupes.append(teacher1)

        for teacher1 in teachers1:
            for event in events:
                if teacher1[3] == event[2] and teacher1[4] == event[3] and teacher1[3] in days and teacher1[4] in hours:
                    dupes.append(teacher1)
                    dupes.append(event)

        if len(dupes) > 0:
            for d in dupes:
                if len(d) == 7:
                    embed.add_field(name=f'{d[0]} - {d[1]} (Class)',
                                    value=f"{d[2]} | **{d[3]}** | **{d[4]}** | {d[5]} | {d[6]}", inline=False)
                elif len(d) == 4:
                    embed.add_field(name=f'{d[0]} - {d[1]} (Event)', value=f"**{d[2]}** | **{d[3]}**", inline=False)

            await ctx.send(embed=embed)

        else:
            embed.add_field(name=f'None', value='Neither classes nor events are repeated!', inline=False)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(ClassManagement(client))
