import discord
from discord.ext import commands
from mysqldb import *


class EventManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('EventManagement cog is ready!')

    # Teachers' schedules
    @commands.command()
    async def events(self, ctx):
        events = await show_events()
        embed = discord.Embed(title='Events', description='All available events and their schedules (UTC+1)',
                              colour=discord.Colour.dark_green())
        embed.set_author(name='DNK',
                         icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
        embed.set_footer(text=ctx.author.guild.name)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
        if len(events) != 0:
            for e in events:
                embed.add_field(name=f'{e[0]} - {e[1]}', value=f'Day: {e[2]} | Time: {e[3]}', inline=False)
            await ctx.send(content=None, embed=embed)
        else:
            embed.add_field(name='None', value='No events available')
            await ctx.send(content=None, embed=embed)

    # Add events
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_event(self, ctx, event: str, day: str, time: str):
        events = await show_events()
        await add_the_event(len(events) + 1, event.title(), day.title(), time.upper())
        await ctx.send(f"{event.title()} event successfully added!")

    # Remove events
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_event(self, ctx, id: str = None):
        if not id:
            return await ctx.send('Inform the id!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        events = await show_events()
        for event in events:
            if id == str(event[0]):
                await remove_the_event(id)
                return await ctx.send(f"{event[1]} event successfully removed!")
        else:
            await ctx.send('Event not found!')

    # Updates event's name
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_event_name(self, ctx, id: str = None, name: str = None):
        if id is None or name is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        events = await show_events()
        for event in events:
            if id == str(event[0]):
                await edit_event_name(id, name.title())
                return await ctx.send(f"Event's **name** updated!")
        else:
            await ctx.send('Event not found')

    # Updates event's time
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_event_time(self, ctx, id: str = None, time: str = None):
        if id is None or time is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        events = await show_events()
        for event in events:
            if id == str(event[0]):
                await edit_event_time(id, time.upper())
                return await ctx.send(f"Event's **name** updated!")
        else:
            await ctx.send('Event not found')

    # Updates event's day
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_event_day(self, ctx, id: str = None, day: str = None):
        if id is None or day is None:
            return await ctx.send('Inform all parameters!')
        elif not id.isnumeric():
            return await ctx.send('Inform a valid id!')

        events = await show_events()
        for event in events:
            if id == str(event[0]):
                await edit_event_day(id, day.title())
                return await ctx.send(f"Event's **day** updated!")
        else:
            await ctx.send('Event not found')


def setup(client):
    client.add_cog(EventManagement(client))
