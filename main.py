import discord
from discord.ext import commands, tasks
from mysqldb import *
import asyncio
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


# Reading the bot's token
token = read_token()

# Making the client variable
client = commands.Bot(command_prefix='!')


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


# Teachers' schedules
@client.command()
async def classes(ctx):
    classes = show_teachers()
    embed = discord.Embed(title='Classes', description='All available classes and their schedules (UTC+1)', colour=discord.Colour.gold())
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/658745955343925268/test1.gif')
    if len(classes) != 0:
        for c in classes:
            embed.add_field(name=f'{c[0]} - {c[1]}', value=f'Teacher: {c[2]} | Day: {c[3]} | Time: {c[4]} | Type: {c[5]}', inline=False)
        await ctx.send(content=None, embed=embed)
    else:
        embed.add_field(name='None', value='No classes available')
        await ctx.send(content=None, embed=embed)


# Add classes
@client.command()
@commands.has_permissions(administrator=True)
async def add_class(ctx, language: str, teacher: str, day: str, time: str, type: str):
    add_teacher_class(len(show_teachers())+1, language.title(), teacher.title(), day.title(), time.upper(), type.title())
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
    embed = discord.Embed(title='(f) Classes', description='All available classes and their schedules (UTC+1)', colour=discord.Colour.gold())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/658745955343925268/test1.gif')
    the_class = await ctx.send(embed=embed)
    if len(classes) != 0:
        await asyncio.sleep(3)
        for i, c in enumerate(classes):
            embed = discord.Embed(title=f'(f) Classes ({i+1}/{len(classes)})', description=f'**Class:** {c[1]}\n**Teacher:** {c[2]}\n**Day:** {c[3]}\n**Time:** {c[4]}\n**Type:** {c[5]}', colour=discord.Colour.gold())
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/658745955343925268/test1.gif')
            await the_class.edit(embed=embed)
            await asyncio.sleep(5)

        embed = discord.Embed(title=f'Reviewed {len(classes)} classes!', description='Thank you for using me! 🦥', colour=discord.Colour.gold())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/658745955343925268/test1.gif')
        await the_class.edit(embed=embed)

    else:
        embed.add_field(name='None', value='No classes available')
        await the_class.edit(embed=embed)


@commands.has_permissions(administrator=True)
@client.command()
async def update(ctx):
    await ctx.message.delete()
    configs = show_config()
    if len(configs) > 0:
        channel = discord.utils.get(ctx.author.guild.channels, id=configs[0][0])
        msg = await channel.fetch_message(configs[0][1])
    img = Image.open("calendar_template.png") #Replace name.png with your background image.
    draw = ImageDraw.Draw(img)
    small = ImageFont.truetype("built titling sb.ttf", 45) #Make sure you insert a valid font from your folder.
    teachers = show_teachers()
    #    (x,y)::↓ ↓ ↓ (text)::↓ ↓     (r,g,b)::↓ ↓ ↓
    for teacher in teachers:
        x = y = 0
        clr = (0, 255, 0)
        if teacher[3] == 'Monday':
            x = 335
        elif teacher[3] == 'Tuesday':
            x = 550
        elif teacher[3] == 'Wednesday':
            x = 760
        elif teacher[3] == 'Thursday':
            x = 970
        elif teacher[3] == 'Friday':
            x = 1180
        elif teacher[3] == 'Saturday':
            x = 1400
        elif teacher[3] == 'Sunday':
            x = 1590

        if teacher[4] == '1AM':
            y = 320
        elif teacher[4] == '3AM':
            y = 390
        elif teacher[4] == '12PM':
            y = 460
        elif teacher[4] == '4PM':
            y = 530
        elif teacher[4] == '5PM':
            y = 595
        elif teacher[4] == '6PM':
            y = 665
        elif teacher[4] == '7PM':
            y = 740
        elif teacher[4] == '8PM':
            y = 810
        elif teacher[4] == '9PM':
            y = 880
        elif teacher[4] == '10PM':
            y = 955

        if teacher[5] == 'Grammar':
            clr = (0, 0, 0)
        elif teacher[5] == 'Pronunciation':
            clr = (0, 153, 153)
        elif teacher[5] == 'Both':
            clr = (255, 0, 0)

        if x != 0 and y != 0:
            draw.text((x, y), f"{teacher[1]}", clr, font=small)

    img.save('calendar_template2.png') #Change name2.png if needed.
    e = discord.Embed()
    new_message = await ctx.send(file=discord.File('calendar_template2.png'))

    for u in new_message.attachments:
        e.set_image(url=u.url)
        if len(configs) > 0:
            await msg.edit(embed=e)
        else:
            await ctx.send(embed=e)
        await asyncio.sleep(1)
    await new_message.delete()


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
            embed = discord.Embed(title=f'Class - {id}#', description=f'**Class:** {teacher[1]}\n**Teacher:** {teacher[2]}\n**Day:** {teacher[3]}\n**Time:** {teacher[4]}\n**Type:** {teacher[5]}', colour=discord.Colour.gold())
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
    embed = discord.Embed(title='Excepted Classes', description='All classes that cannot be inserted into the calendar.', colour=discord.Colour.gold())
    for teacher in teachers:
        if teacher[3] not in days or teacher[4] not in hours:
            embed.add_field(name=f'{teacher[0]} - {teacher[1]}', value=f"{teacher[2]} | {teacher[3]} | {teacher[4]} | {teacher[5]}", inline=False)            
            
    else:
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
    dupes = []
    embed = discord.Embed(title="Repeated values", description="All classes that have values equal to other classes'", colour=discord.Colour.gold())
    for teacher1 in teachers1:
        for teacher2 in teachers2:
            if teacher1[0] != teacher2[0] and teacher1[3] == teacher2[3] and teacher1[4] == teacher2[4] and teacher1[3] in days and teacher1[4] in hours:
                dupes.append(teacher1)

    if len(dupes) > 0:
        for d in dupes:
            embed.add_field(name=f'{d[0]} - {d[1]}', value=f"{d[2]} | **{d[3]}** | **{d[4]}** | {d[5]}", inline=False)
        await ctx.send(embed=embed)

    else:
        embed.add_field(name=f'None', value='No classes are repeated!', inline=False)
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

    
# Calendar commands
@client.command()
async def cmds(ctx):
    embed = discord.Embed(title="Calendar's command list", description="Some useful commands", colour=discord.Colour.dark_red())
    embed.add_field(name='(Admin+) !add_class [language] [teacher] [day] [time] [type]', value='Adds a new class.', inline=False)
    embed.add_field(name='(Admin+) !remove_class [id]', value='Removes an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_language [id] [new_language]', value='Updates the language of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_name [id] [new_name]', value='Updates the name of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_day [id] [new_day]', value='Updates the day of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_time [id] [new_time]', value='Updates the time of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_type [id] [new_type]', value='Updates the type of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_calendar', value='Updates the calendar by organizing each of the available classes in their respective positions.', inline=False)
    embed.add_field(name="(Admin+) !showconfigs", value="Shows the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !addconfigs [channel_id] [message_id]", value="Adds the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !delconfigs", value="Deletes the calendar's configuration ids.", inline=False)
    embed.add_field(name="(Admin+) !exception", value="Shows the excepted classes.", inline=False)
    embed.add_field(name="(Admin+) !repeated", value="Shows the repeated values.", inline=False)
    embed.add_field(name="(Admin+) !spy [channel_id] [message]", value="The bot sends a message to the given channel.", inline=False)
    embed.add_field(name='!teachers', value='Tells the amount of scheduled teachers.', inline=False)
    embed.add_field(name='!show [id]', value='Shows a specific class.', inline=False)
    embed.add_field(name='!classes', value='Shows all the available classes.', inline=False)
    embed.add_field(name='!fclasses', value='Shows all available classes one at a time.', inline=False)
    embed.add_field(name="!cmds", value="Shows all of the commands.", inline=False)
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/652636445982588970/ezgif.com-gif-maker-1.gif')
    await ctx.send(embed=embed)

client.run(token)