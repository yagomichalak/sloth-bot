import discord
from discord.ext import commands, tasks
from mysqldb import *
import asyncio
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime

def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


# Reading the bot's token
token = read_token()

# Making the client variable
client = commands.Bot(command_prefix='!')

rules = ["Do not post or talk about NSFW content in text or voice chat. This server is a safe for work, that is except in #💩sloth-shitposting💩.",
"Be respectful of all members, especially Staff.",
"Avoid topics such as: Politics,Religion,Self-Harm or anything considered controversial.",
"Do not share others' personal information without their consent.",
"Do not advertise your server or other communities without express consent from an Owner of this server.",
"Do not flood or spam the text chat. Do not tag native roles repeatedly without need.",
"No ear rape or mic spam. If you have a loud background, go on push-to-talk or mute.",
"Check a user’s DM status before direct messaging them and respect their wishes.",
"Try to resolve disputes personally. You may mute or block a user. If you cannot resolve the issue, contact 👮‍♂️Moderators ",
"Abide by Discord’s Terms of Service and Community Guidelines."]

# Tells when the bot is online
@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready!')


# Handles the errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do that!")

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please, inform all parameters!')


# Teachers status update
@tasks.loop(seconds=10)
async def change_status():
    len_teachers = len(show_teachers())
    if len_teachers == 1:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len_teachers} teacher.'))
    else:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len_teachers} teachers.'))


# Joins VC log
@client.event
async def on_voice_state_update(member, before, after):
    mod_role = discord.utils.get(member.guild.roles, name='👮‍♂️Moderators')
    if mod_role not in member.roles:
        return

    if not before.self_mute == after.self_mute or not before.self_deaf == after.self_deaf:
        return

    mod_log = client.get_channel(675745413760024595)
    if after.channel is not None:
        # Switched between voice channels
        if before.channel is not None:
            embed = discord.Embed(description=f'**{member}** switched between voice channels: {before.channel.name} - {after.channel.name}', colour=discord.Colour.dark_green(), timestamp=datetime.utcnow())
            embed.add_field(name='Channels', value=f'{before.channel.name} - {after.channel.name}', inline=False)
            embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nPrevious Channel = {before.channel.id}\nCurrent Channel = {after.channel.id}```')
            embed.set_footer(text=f"Guild name: {member.guild.name}")
            embed.set_author(name=member, icon_url=member.avatar_url)
            await mod_log.send(embed=embed)
        # Entered a voice channel
        else:
            embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}', colour=discord.Colour.green(), timestamp=datetime.utcnow())
            embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
            embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
            embed.set_footer(text=f"Guild name: {member.guild.name}")
            embed.set_author(name=member, icon_url=member.avatar_url)
            await mod_log.send(embed=embed)
    # Left voice channel
    elif after.channel is None:
        embed = discord.Embed(description=f'**{member}** left voice channel: {before.channel.name}', colour=discord.Colour.red(), timestamp=datetime.utcnow())
        embed.add_field(name='Channel', value=f'{before.channel.name}', inline=False)
        embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {before.channel.id}```')
        embed.set_footer(text=f"Guild name: {member.guild.name}")
        embed.set_author(name=member, icon_url=member.avatar_url)
        await mod_log.send(embed=embed)


# Available teachers
@client.command()
async def teachers(ctx):
    teachers = show_teachers()
    if len(teachers) == 0:
        await ctx.send('There is no scheduled teachers!')
    elif len(teachers) == 1:
        await ctx.send('There is 1 scheduled teacher!')
    else:
        await ctx.send(f'There are {len(teachers)} scheduled teachers!')


# Shows the specific rule
@client.command()
async def rule(ctx, numb: int = None):
    await ctx.message.delete()
    if not numb:
        return await ctx.send('**Invalid parameter!**')
    if numb > 10 or numb <= 0:
        return await ctx.send('**Paremeter out of range!**')
    
    embed = discord.Embed(title=f'Rule - {numb}#', description=f"{rules[numb-1]}", colour=discord.Colour.dark_green())
    embed.set_footer(text=ctx.author.guild.name)
    await ctx.send(embed=embed)

# Teachers' schedules
@client.command()
async def classes(ctx):
    classes = show_teachers()
    embed = discord.Embed(title='Classes', description='All available classes and their schedules (UTC+1)', colour=discord.Colour.dark_green())
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    if len(classes) != 0:
        for c in classes:
            embed.add_field(name=f'{c[0]} - {c[1]}', value=f'Teacher: {c[2]} | Day: {c[3]} | Time: {c[4]} | Type: {c[5]} | For: {c[6]}', inline=False)
        await ctx.send(content=None, embed=embed)
    else:
        embed.add_field(name='None', value='No classes available')
        await ctx.send(content=None, embed=embed)


# Add classes
@client.command()
@commands.has_permissions(administrator=True)
async def add_class(ctx, language: str, teacher: str, day: str, time: str, type: str, forr: str = None):
    if not forr:
        forr = 'General people'
    add_teacher_class(len(show_teachers())+1, language.title(), teacher.title(), day.title(), time.upper(), type.title(), forr.title())
    await ctx.send(f"{teacher.title()}'s class successfully added!")


# Remove classes
@client.command()
@commands.has_permissions(administrator=True)
async def remove_class(ctx, id: str = None):
    if not id:
        return await ctx.send('Inform the id!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            remove_teacher_class(id)
            return await ctx.send(f"{teacher[2]}'s class successfully removed!")
    else:
        await ctx.send('Teacher not found!')


# Updates classes
@client.command()
@commands.has_permissions(administrator=True)
async def update_class(ctx, id: str = None, language: str = None):
    if id is None or language is None:
        return await ctx.send('Inform all parameters!')    
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_language(id, language.title())
            return await ctx.send(f"Teacher's **class** updated!")
    else:
        await ctx.send('Teacher not found')
    

# Updates classes
@client.command()
@commands.has_permissions(administrator=True)
async def update_name(ctx, id: str = None, name: str = None):
    if id is None or name is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_name(id, name.title())
            return await ctx.send(f"Teacher's **name** updated!")
    else:
        await ctx.send('Teacher not found')
    

# Updates classes
@client.command()
@commands.has_permissions(administrator=True)
async def update_day(ctx, id: str = None, day: str = None):
    if id is None or day is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_day(id, day.title())
            return await ctx.send(f"Teacher's **day** updated!")
    else:
        await ctx.send('Teacher not found')
    

# Updates classes
@client.command()
@commands.has_permissions(administrator=True)
async def update_time(ctx, id: str = None, time: str = None):
    if id is None or time is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')
    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_time(id, time.upper())
            return await ctx.send(f"Teacher's **time** updated!")
    else:
        await ctx.send('Teacher not found')
    

# Updates classes
@client.command()
@commands.has_permissions(administrator=True)
async def update_type(ctx, id: str = None, type: str = None):
    if id is None or type is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_type(id, type.title())
            return await ctx.send(f"Teacher's **type** updated!")
    else:
        await ctx.send('Teacher not found')


# Updates the aiming public
@client.command()
@commands.has_permissions(administrator=True)
async def update_public(ctx, id: str = None, forr: str = None):
    if id is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')
    elif not forr:
        forr = 'General people'

    teachers = show_teachers()
    for teacher in teachers:
        if id == str(teacher[0]):
            edit_teacher_class_forr(id, forr.title())
            return await ctx.send(f"Teacher's **public** updated!")
    else:
        await ctx.send('Teacher not found')

# Wrong command 1
@client.command()
async def lessons(ctx):
    await ctx.send("The command is **!classes**, and not **!lessons**")


# Wrong command 2
@client.command()
async def calendar(ctx):
    await ctx.send("The command is **!classes**, and not **!calendar**")


# Spy command
@client.command()
@commands.has_permissions(administrator=True)
async def spy(ctx, cid, *messages):
    await ctx.message.delete()
    if len(ctx.message.content.split()) < 3:
        return await ctx.send('You must inform all parameters!')

    spychannel = client.get_channel(int(cid))
    msg = ctx.message.content.split(cid)
    embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_blue())
    await spychannel.send(embed=embed)
    

# Fast classes
@client.command()
async def fclasses(ctx):
    classes = show_teachers()
    embed = discord.Embed(title='(f) Classes', description='All available classes and their schedules (UTC+1)', colour=discord.Colour.dark_green())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    the_class = await ctx.send(embed=embed)
    if len(classes) != 0:
        await asyncio.sleep(3)
        for i, c in enumerate(classes):
            embed = discord.Embed(title=f'(f) Classes ({i+1}/{len(classes)})', description=f'**Class:** {c[1]}\n**Teacher:** {c[2]}\n**Day:** {c[3]}\n**Time:** {c[4]}\n**Type:** {c[5]}\n**For:** {c[6]}', colour=discord.Colour.dark_green())
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
            await the_class.edit(embed=embed)
            await asyncio.sleep(5)

        embed = discord.Embed(title=f'Reviewed {len(classes)} classes!', description='Thank you for using me! 🦥', colour=discord.Colour.dark_green())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
        await the_class.edit(embed=embed)

    else:
        embed.add_field(name='None', value='No classes available')
        await the_class.edit(embed=embed)


@commands.has_permissions(administrator=True)
@client.command()
async def update(ctx):
    await ctx.message.delete()
    copy_channel = client.get_channel(673592568268980244)
    configs = show_config()
    if len(configs) > 0:
        channel = discord.utils.get(ctx.author.guild.channels, id=configs[0][0])
        msg = await channel.fetch_message(configs[0][1])
    img = Image.open("calendar_template.png") #Replace name.png with your background image.
    draw = ImageDraw.Draw(img)
    small = ImageFont.truetype("built titling sb.ttf", 45) #Make sure you insert a valid font from your folder.
    teachers = show_teachers()
    events = show_events()
    #    (x,y)::↓ ↓ ↓ (text)::↓ ↓     (r,g,b)::↓ ↓ ↓
    for teacher in teachers:
        x = check_x(teacher)
        y = check_y(teacher)
        clr = check_clr(teacher)

        if x != 0 and y != 0:
            draw.text((x, y), f"{teacher[1]}", clr, font=small)

    for event in events:
        x = check_x(event)
        y = check_y(event)
        clr = check_clr(event)

        if x != 0 and y != 0:
            draw.text((x, y), f"{event[1]}", clr, font=small)

    img.save('calendar_template2.png') #Change name2.png if needed.
    e = discord.Embed(colour=discord.Colour.dark_green())
    new_message = await copy_channel.send(file=discord.File('calendar_template2.png'))

    for u in new_message.attachments:
        e.set_image(url=u.url)
        if len(configs) > 0:
            return await msg.edit(embed=e)
        else:
            return await ctx.send(embed=e)


# Show specific class
@client.command()
async def show(ctx, id: str = None):
    await ctx.message.delete()
    if not id:
        return await ctx.send('**Inform the class id!**')
    elif not id.isnumeric():
        return await ctx.send('**Inform a numeric value!**')

    teachers = show_teachers()
    for teacher in teachers:
        if teacher[0] == int(id):
            embed = discord.Embed(title=f'Class - {id}#', description=f'**Class:** {teacher[1]}\n**Teacher:** {teacher[2]}\n**Day:** {teacher[3]}\n**Time:** {teacher[4]}\n**Type:** {teacher[5]}\n**For:** {teacher[6]}', colour=discord.Colour.dark_green())
            return await ctx.send(embed=embed)
    else:
        return await ctx.send('**Class not found!**')


@commands.has_permissions(administrator=True)
@client.command()
async def exception(ctx):
    await ctx.message.delete()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = ['1AM', '3AM', '12PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM']
    teachers = show_teachers()
    events = show_events()
    embed = discord.Embed(title='Excepted Classes & Events', description='All classes and events that cannot be inserted into the calendar.', colour=discord.Colour.dark_green())
    for teacher in teachers:
        if teacher[3] not in days or teacher[4] not in hours:
            embed.add_field(name=f'{teacher[0]} - {teacher[1]}', value=f"{teacher[2]} | {teacher[3]} | {teacher[4]} | {teacher[5]} | {teacher[6]}", inline=False)

    for event in events:
        if event[2] not in days or event[3] not in hours:
            embed.add_field(name=f'{event[0]} - {event[1]}', value=f"{event[2]} | {event[3]}", inline=False)

    if len(embed.fields) == 0:
        embed.add_field(name='None', value='No exceptions.', inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=embed)
            

@commands.has_permissions(administrator=True)
@client.command()
async def repeated(ctx):
    await ctx.message.delete()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = ['1AM', '3AM', '12PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM']
    teachers1 = teachers2 = show_teachers()
    events = show_events()
    dupes = []
    embed = discord.Embed(title="Repeated values", description="All classes and events that have values equal to others'", colour=discord.Colour.dark_green())
    for teacher1 in teachers1:
        for teacher2 in teachers2:
            if teacher1[0] != teacher2[0] and teacher1[3] == teacher2[3] and teacher1[4] == teacher2[4] and teacher1[3] in days and teacher1[4] in hours:
                dupes.append(teacher1)

    for teacher1 in teachers1:
        for event in events:
            if teacher1[3] == event[2] and teacher1[4] == event[3] and teacher1[3] in days and teacher1[4] in hours:
                dupes.append(teacher1)
                dupes.append(event)

    if len(dupes) > 0:
        for d in dupes:
            if len(d) == 7:
                embed.add_field(name=f'{d[0]} - {d[1]} (Class)', value=f"{d[2]} | **{d[3]}** | **{d[4]}** | {d[5]} | {d[6]}", inline=False)
            elif len(d) == 4:
                embed.add_field(name=f'{d[0]} - {d[1]} (Event)', value=f"**{d[2]}** | **{d[3]}**", inline=False)

        await ctx.send(embed=embed)

    else:
        embed.add_field(name=f'None', value='Neither classes nor events are repeated!', inline=False)
        await ctx.send(embed=embed)


@commands.has_permissions(administrator=True)
@client.command()
async def addconfigs(ctx, channel_id: str = None, message_id: str = None):
    if not channel_id or not message_id :
        return await ctx.send('**Inform all parameters!**')
    elif not channel_id.isnumeric() or not message_id.isnumeric():
        return await ctx.send('**Inform a numeric values!**')

    add_cid_id(int(channel_id), int(message_id))
    await ctx.send('**Calendar ids have been configured!**')


@commands.has_permissions(administrator=True)
@client.command()
async def delconfigs(ctx):
    if len(show_config()) != 0:
        remove_cid_id()
        await ctx.send('**Calendar ids deleted!**')
    else:
        await ctx.send(("**No configurations were set yet!**"))


@commands.has_permissions(administrator=True)
@client.command()
async def showconfigs(ctx):
    if len(show_config()) > 0:
        return await ctx.send(f"Calendar configuration:\n**CID: {show_config()[0][0]}\nMID: {show_config()[0][1]}**")
    else:
        return await ctx.send("**There aren't configurations**")


# Teachers' schedules
@client.command()
async def events(ctx):
    events = show_events()
    embed = discord.Embed(title='Events', description='All available events and their schedules (UTC+1)', colour=discord.Colour.dark_green())
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    if len(events) != 0:
        for e in events:
            embed.add_field(name=f'{e[0]} - {e[1]}', value=f'Day: {e[2]} | Time: {e[3]}', inline=False)
        await ctx.send(content=None, embed=embed)
    else:
        embed.add_field(name='None', value='No events available')
        await ctx.send(content=None, embed=embed)


# Add events
@client.command()
@commands.has_permissions(administrator=True)
async def add_event(ctx, event: str, day: str, time: str):
    add_the_event(len(show_events())+1, event.title(), day.title(), time.upper())
    await ctx.send(f"{event.title()} event successfully added!")


# Remove classes
@client.command()
@commands.has_permissions(administrator=True)
async def remove_event(ctx, id: str = None):
    if not id:
        return await ctx.send('Inform the id!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    events = show_events()
    for event in events:
        if id == str(event[0]):
            remove_the_event(id)
            return await ctx.send(f"{event[1]} event successfully removed!")
    else:
        await ctx.send('Event not found!')


# Updates events
@commands.has_permissions(administrator=True)
@client.command()
async def update_event_name(ctx, id: str = None, name: str = None):
    if id is None or name is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    events = show_events()
    for event in events:
        if id == str(event[0]):
            edit_event_name(id, name.title())
            return await ctx.send(f"Event's **name** updated!")
    else:
        await ctx.send('Event not found')

@commands.has_permissions(administrator=True)
@client.command()
async def update_event_time(ctx, id: str = None, time: str = None):
    if id is None or time is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    events = show_events()
    for event in events:
        if id == str(event[0]):
            edit_event_time(id, time.upper())
            return await ctx.send(f"Event's **name** updated!")
    else:
        await ctx.send('Event not found')
# Updates events


@commands.has_permissions(administrator=True)
@client.command()
async def update_event_day(ctx, id: str = None, day: str = None):
    if id is None or day is None:
        return await ctx.send('Inform all parameters!')
    elif not id.isnumeric():
        return await ctx.send('Inform a valid id!')

    events = show_events()
    for event in events:
        if id == str(event[0]):
            edit_event_day(id, day.title())
            return await ctx.send(f"Event's **day** updated!")
    else:
        await ctx.send('Event not found')


# Calendar commands
@client.command()
async def cmds(ctx):
    embed = discord.Embed(title="Calendar's command list", description="Some useful commands", colour=discord.Colour.dark_green())
    embed.add_field(name='(Admin+) !update_calendar', value='Updates the calendar by organizing each of the available classes in their respective positions.', inline=False)
    embed.add_field(name="(Admin+) !showconfigs", value="Shows the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !addconfigs [channel_id] [message_id]", value="Adds the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !delconfigs", value="Deletes the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !exception", value="Shows the excepted classes and events.", inline=False)
    embed.add_field(name="(Admin+) !repeated", value="Shows the repeated values.", inline=False)
    embed.add_field(name="(Admin+) !spy [channel_id] [message]", value="The bot sends a message to the given channel.", inline=False)
    embed.add_field(name="!cmds", value="Shows this.", inline=False)
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    await ctx.send(embed=embed)


# Calendar commands
@client.command()
async def class_cmds(ctx):
    embed = discord.Embed(title="Calendar's class command list", description="Some useful class commands", colour=discord.Colour.dark_green())
    embed.add_field(name='(Admin+) !add_class [language] [teacher] [day] [time] [type]', value='Adds a new class.', inline=False)
    embed.add_field(name='(Admin+) !remove_class [id]', value='Removes an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_language [id] [new_language]', value='Updates the language of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_name [id] [new_name]', value='Updates the name of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_day [id] [new_day]', value='Updates the day of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_time [id] [new_time]', value='Updates the time of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_type [id] [new_type]', value='Updates the type of an existent class.', inline=False)
    embed.add_field(name='!teachers', value='Tells the amount of scheduled teachers.', inline=False)
    embed.add_field(name='!show [id]', value='Shows a specific class.', inline=False)
    embed.add_field(name='!classes', value='Shows all the available classes.', inline=False)
    embed.add_field(name='!fclasses', value='Shows all available classes one at a time.', inline=False)
    embed.add_field(name="!class_cmds", value="Shows this.", inline=False)
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    await ctx.send(embed=embed)

@client.command()
async def event_cmds(ctx):
    embed = discord.Embed(title="Calendar's event command list", description="Some useful event commands", colour=discord.Colour.dark_green())
    embed.add_field(name='(Admin+) !add_event [event] [day] [time]', value='Adds a new event.', inline=False)
    embed.add_field(name='(Admin+) !remove_event [id]', value='Removes an existent event.', inline=False)
    embed.add_field(name='(Admin+) !update_event_name [id] [new_name]', value='Updates the name of an existent event.', inline=False)
    embed.add_field(name='(Admin+) !update_event_day [id] [new_day]', value='Updates the day of an existent event.', inline=False)
    embed.add_field(name='(Admin+) !update_event_time [id] [new_time]', value='Updates the time of an existent event.', inline=False)
    embed.add_field(name="!event_cmds", value="Shows this.", inline=False)
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
    await ctx.send(embed=embed)


client.run(token)