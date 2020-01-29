import discord
from discord.ext import commands, tasks
from mysqldb import *
import asyncio


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


# Reading the bot's token
token = read_token()

# Making the client variable
client = commands.Bot(command_prefix='!')


# Tells when the bot is onlin
@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready!')


# Handles the errors
#@client.event
#async def on_command_error(ctx, error):
    #if isinstance(error, commands.MissingPermissions):
        #await ctx.send("You can't do that!")

    #if isinstance(error, commands.MissingRequiredArgument):
     #   await ctx.send('Please, inform all parameters!')


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
    if len(classes) != 0:
        the_class = await ctx.send(embed=embed)
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


# Calendar commands
@client.command()
async def cmds(ctx):
    embed = discord.Embed(title="Calendar's command list", description="Some useful commands", colour=discord.Colour.gold())
    embed.add_field(name="!cmds", value="Shows all of the commands.", inline=False)
    embed.add_field(name='!classes', value='Shows all the available classes.', inline=False)
    embed.add_field(name='(Admin+) !add_class [language] [teacher] [day] [time] [type]', value='Adds a new class.', inline=False)
    embed.add_field(name='(Admin+) !remove_class [id]', value='Removes an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_language [id] [new_language]', value='Updates the language of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_name [id] [new_name]', value='Updates the name of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_day [id] [new_day]', value='Updates the day of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_time [id] [new_time]', value='Updates the time of an existent class.', inline=False)
    embed.add_field(name='(Admin+) !update_type [id] [new_type]', value='Updates the type of an existent class.', inline=False)
    embed.add_field(name='!teachers', value='Tells the amount of scheduled teachers.', inline=False)
    embed.set_author(name='DNK', icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
    embed.set_footer(text=ctx.author.guild.name)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/562019489642709022/658745955343925268/test1.gif')
    await ctx.send(embed=embed)

client.run(token)