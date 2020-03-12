import discord
from discord.ext import commands, tasks
from mysqldb import *
import asyncio
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime
import os

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


@client.event
async def on_message(message):
    if not message.author.bot:
        report_channel = 685832739517366340
        if 'Direct Message' not in str(message.channel):
            if message.channel.id == report_channel:
                await message.delete()
                member = discord.utils.get(message.author.guild.members, id=message.author.id)
                gid = 459195345419763713 # Guild id
                cid = 683693966016774168 # Report log's channel id         
                guild = client.get_guild(gid)
                moderators = discord.utils.get(guild.roles, id=497522510212890655)
                cosmos = discord.utils.get(guild.members, id=423829836537135108)
                the_channel = discord.utils.get(guild.channels, id=cid)
                report = message.content

                # Report embed
                embed_report = discord.Embed(description=report, colour=discord.Colour.green(), timestamp=message.created_at)
                embed_report.set_author(name=f'{message.author} | ID: {message.author.id}', icon_url=message.author.avatar_url)

                await the_channel.send(f'{moderators.mention}, {cosmos.mention}')
                await the_channel.send(embed=embed_report)
            
    await client.process_commands(message)


@client.event
async def on_raw_reaction_add(overload):
    guild = client.get_guild(overload.guild_id)
    user = discord.utils.get(guild.members, id=overload.user_id)
    message = 686821958708363281
    pvm = '''You can create your own room by joining any room with a plus on it.
    
**Public Commands:**

Here are the commands you can use:

`vc/lock` - Locks the room so no one can join.
`vc/unlock` - Unlocks the room allowing people to join.
`vc/kick @username` - Kicks and locks the room for an user 
Above commands are only usable by the owner of the room.
Ownership is automatically transferred to another member in the room when the original owner leaves.
For transfering ownership without leaving the room use:
`vc/transfer @user`
The role will disappear after 1 minute.'''

    if overload.message_id == message:
        if str(overload.emoji) == '⌛':
            embed = discord.Embed(description=pvm, colour=discord.Colour.dark_green())
            await user.send(embed=embed)
    
    native_germanic = 687653940602339349
    native_uralic = 687653990791774218
    native_celtic = 687654028905021584
    native_romance = 687654128905748743
    native_baltic = 687654156852264978
    native_slavic = 687654179707027495
    native_semitic = 687654243653779478
    native_turkic = 687654272284098560
    native_iranian = 687654283684085771
    native_asian = 687654312465137679
    native_indian = 687654329921830933

    elif overload.message_id == native_germanic:
        if str(overload.emoji) == '🇬🇧':
            embed = discord.Embed(title='English', description=read_native('native', 'english'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇩🇪':
            embed = discord.Embed(title='German', description=read_native('native', 'german'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇩🇰':
            embed = discord.Embed(title='Danish', description=read_native('native', 'danish'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇳🇱':
            embed = discord.Embed(title='Dutch', description=read_native('native', 'dutch'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇳🇴':
            embed = discord.Embed(title='Norwegian', description=read_native('native', 'norwegian'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇸🇪':
            embed = discord.Embed(title='Swedish', description=read_native('native', 'swedish'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇮🇸':
            embed = discord.Embed(title='Icelandic', description=read_native('native', 'icelandic'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇿🇦':
            embed = discord.Embed(title='Afrikaans', description=read_native('native', 'afrikaans'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇫🇴':
            embed = discord.Embed(title='Faroese', description=read_native('native', 'faroese'), colour=discord.Colour.dark_green())
        elif str(overload.emoji) == '🇱🇺':
            embed = discord.Embed(title='Luxembourgish', description=read_native('native', 'luxembourgish'), colour=discord.Colour.dark_green())

        embed.set_footer(text=f"Guild name: {guild.name}")
        embed.set_author(name=user, icon_url=user.avatar_url)
        return await user.send(embed=embed)
        
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
    teacher_role = discord.utils.get(member.guild.roles, name='👨‍🏫Teachers')
    if mod_role not in member.roles and teacher_role not in member.roles:
        return

    if not before.self_mute == after.self_mute or not before.self_deaf == after.self_deaf:
        return

    mod_log = client.get_channel(675745413760024595)
    lesson_log = client.get_channel(679043911225966608)
    lesson_cat = 562019326295670806
    if after.channel is not None:
        # Switched between voice channels
        if before.channel is not None:
            # Switched between channels in the lessons category. (Switched)
            if teacher_role in member.roles and after.channel.category_id == lesson_cat and before.channel.category_id == lesson_cat:
                embed = discord.Embed(description=f'**{member}** switched between voice channels: {before.channel.name} - {after.channel.name}', colour=discord.Colour.dark_green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channels', value=f'{before.channel.name} - {after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nPrevious Channel = {before.channel.id}\nCurrent Channel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await lesson_log.send(embed=embed)

            # Switched between channels, considering that the former is not in the lesson category and the latter is. (Joined)
            elif teacher_role in member.roles and after.channel.category_id == lesson_cat and before.channel.category_id != lesson_cat:
                embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}', colour=discord.Colour.green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await lesson_log.send(embed=embed)

            # Switched between channels, considering that the former is in the lesson category and the latter is not. (Left)
            elif teacher_role in member.roles and after.channel.category_id != lesson_cat and before.channel.category_id == lesson_cat:
                embed = discord.Embed(description=f'**{member}** left voice channel: {before.channel.name}', colour=discord.Colour.red(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{before.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {before.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await lesson_log.send(embed=embed)


            if mod_role in member.roles:
                embed = discord.Embed(description=f'**{member}** switched between voice channels: {before.channel.name} - {after.channel.name}', colour=discord.Colour.dark_green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channels', value=f'{before.channel.name} - {after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nPrevious Channel = {before.channel.id}\nCurrent Channel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await mod_log.send(embed=embed)
        # Entered a voice channel
        else:
            if teacher_role in member.roles and after.channel.category_id == lesson_cat:
                embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}', colour=discord.Colour.green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await lesson_log.send(embed=embed)

            if mod_role in member.roles:
                embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}', colour=discord.Colour.green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await mod_log.send(embed=embed)

    # Left voice channel
    elif after.channel is None:
        if teacher_role in member.roles and before.channel.category_id == lesson_cat:
            embed = discord.Embed(description=f'**{member}** left voice channel: {before.channel.name}', colour=discord.Colour.red(), timestamp=datetime.utcnow())
            embed.add_field(name='Channel', value=f'{before.channel.name}', inline=False)
            embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {before.channel.id}```')
            embed.set_footer(text=f"Guild name: {member.guild.name}")
            embed.set_author(name=member, icon_url=member.avatar_url)
            await lesson_log.send(embed=embed)

        if mod_role in member.roles:
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


# Spy command
@client.command()
@commands.has_permissions(administrator=True)
async def rspy(ctx, cid, *messages):
    await ctx.message.delete()
    if len(ctx.message.content.split()) < 3:
        return await ctx.send('You must inform all parameters!')

    spychannel = client.get_channel(int(cid))
    msg = ctx.message.content.split(cid)
    embed = discord.Embed(description=msg[1], colour=discord.Colour.red())
    await spychannel.send(embed=embed)
    

# Embed command    
@client.command()
@commands.has_permissions(administrator=True)
async def embed(ctx):
    await ctx.message.delete()
    if len(ctx.message.content.split()) < 2:
        return await ctx.send('You must inform all parameters!')

    msg = ctx.message.content.split('embed', 1)
    embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
    await ctx.send(embed=embed)


# Member counting command
@client.command()
async def members(ctx):
    all_users = ctx.guild.members
    await ctx.send(f'{len(all_users)} members!')
    
    
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


# Countdown command
@client.command()
@commands.has_permissions(administrator=True)
async def count(ctx, amount=0):
    await ctx.message.delete()
    if amount > 0:
        msg = await ctx.send(f'**{amount}**')
        await asyncio.sleep(1)
        for x in range(int(amount)-1, -1, -1):
            await msg.edit(content=f'**{x}**')
            await asyncio.sleep(1)
        await msg.edit(content='**Done!**')
    else:
        await ctx.send('Invalid parameters!')
        
        
@client.command()
@commands.has_permissions(administrator=True)
async def gif(ctx, name: str = None):
    await ctx.message.delete()
    try:
        with open(f'gif/{name}.gif', 'rb') as pic:
            await ctx.send(file=discord.File(pic))
    except FileNotFoundError:
        return await ctx.send("**File not found!**")


@client.command()
@commands.has_permissions(administrator=True)
async def png(ctx, name: str = None):
    await ctx.message.delete()
    try:
        await ctx.send(file=discord.File(f'png/{name}.png'))
    except FileNotFoundError:
        return await ctx.send("**File not found!**")


@client.command()
@commands.has_permissions(administrator=True)
async def files(ctx, type: str = None):
    await ctx.message.delete()
    if not type:
        return await ctx.send('**Please, specify an extension!**')
    elif type.lower() != "png" and type.lower() != "gif":
        return await ctx.send('**Extension not supported!**')
    arr = os.listdir(f'./{type}')
    temp = []
    for a in arr:
        if type.lower() == "png":
            temp.append(a[:-4])
        else:
            temp.append(a[:-4])

    temp = ' \n'.join(temp)
    embed = discord.Embed(title=f'{type.title()} files', description=f"__All available files:__\n**{temp}**", colour=discord.Colour.dark_green())
    embed.set_footer(text=ctx.author.guild.name)
    if len(temp) == 0:
        embed.add_field(name='None', value='No files available')

    await ctx.send(content=None, embed=embed)


def read_native(type, language):
    with open(f'texts/germanic/{type}/{language}.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
        text = ''.join(text)
        return text
        
        
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