import discord
from discord.ext import commands
from mysqldb import *
import asyncio

rules = [
    "Do not post or talk about NSFW content in text or voice chat. This server is a safe for work, that is except in",
    "Be respectful of all members, especially Staff.",
    "Avoid topics such as: Politics,Religion,Self-Harm or anything considered controversial anywhere on the server except on the **Debate Club**",
    "Do not advertise your server or other communities without express consent from an Owner of this server.",
    "Do not share others' personal information without their consent.",
    "Do not flood or spam the text chat. Do not tag native roles repeatedly without a reason.",
    "No ear rape or mic spam. If you have a loud background, go on push-to-talk or mute.",
    "Try to settle disputes personally. You may mute or block a user. If you cannot resolve the issue, contact staff in <#685832739517366340>",
    "Do not impersonate users or member of the staff ",
    "No asking to be granted roles/moderator roles, you may apply in <#671788773733826628> but begging the staff repeatedly and irritatingly will result in warnings or even ban."]


class Show(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Show cog is ready!')

    # Shows how many members there are in the server
    @commands.command()
    async def members(self, ctx):
        await ctx.message.delete()
        all_users = ctx.guild.members
        await ctx.send(f'{len(all_users)} members!')

    # Shows the specific rule
    @commands.command()
    async def rule(self, ctx, numb: int = None):
        await ctx.message.delete()
        if not numb:
            return await ctx.send('**Invalid parameter!**')
        if numb > 10 or numb <= 0:
            return await ctx.send('**Paremeter out of range!**')

        embed = discord.Embed(title=f'Rule - {numb}#', description=f"{rules[numb - 1]}",
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=ctx.author.guild.name)
        await ctx.send(embed=embed)

    # Shows a specific class
    @commands.command()
    async def show(self, ctx, id: str = None):
        await ctx.message.delete()
        if not id:
            return await ctx.send('**Inform the class id!**')
        elif not id.isnumeric():
            return await ctx.send('**Inform a numeric value!**')

        teachers = await show_teachers()
        for teacher in teachers:
            if teacher[0] == int(id):
                embed = discord.Embed(title=f'Class - {id}#',
                                      description=f'**Class:** {teacher[1]}\n**Teacher:** {teacher[2]}\n**Day:** {teacher[3]}\n**Time:** {teacher[4]}\n**Type:** {teacher[5]}\n**For:** {teacher[6]}',
                                      colour=discord.Colour.dark_green())
                return await ctx.send(embed=embed)
        else:
            return await ctx.send('**Class not found!**')

    # Shows the classes in a faster way
    @commands.command()
    async def fclasses(self, ctx):
        await ctx.message.delete()
        classes = await show_teachers()
        embed = discord.Embed(title='(f) Classes', description='All available classes and their schedules (UTC+1)',
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
        the_class = await ctx.send(embed=embed)
        if len(classes) != 0:
            await asyncio.sleep(3)
            for i, c in enumerate(classes):
                embed = discord.Embed(title=f'(f) Classes ({i + 1}/{len(classes)})',
                                      description=f'**Class:** {c[1]}\n**Teacher:** {c[2]}\n**Day:** {c[3]}\n**Time:** {c[4]}\n**Type:** {c[5]}\n**For:** {c[6]}',
                                      colour=discord.Colour.dark_green())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
                await the_class.edit(embed=embed)
                await asyncio.sleep(5)

            embed = discord.Embed(title=f'Reviewed {len(classes)} classes!', description='Thank you for using me! 🦥',
                                  colour=discord.Colour.dark_green())
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
            await the_class.edit(embed=embed)

        else:
            embed.add_field(name='None', value='No classes available')
            await the_class.edit(embed=embed)

    # Shows the classes and their schedules
    @commands.command()
    async def classes(self, ctx):
        await ctx.message.delete()
        classes = await show_teachers()
        embed = discord.Embed(title='Classes', description='All available classes and their schedules (UTC+1)',
                              colour=discord.Colour.dark_green())
        embed.set_author(name='DNK',
                         icon_url='https://cdn.discordapp.com/avatars/550057247456100353/e3e2a56379f6457066a630c0eb68d34e.png?size=256')
        embed.set_footer(text=ctx.author.guild.name)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/673592568268980244/673685902312341509/a_0fc103e90b7fcbea53f42dd59d17e920.gif')
        if len(classes) != 0:
            for c in classes:
                embed.add_field(name=f'{c[0]} - {c[1]}',
                                value=f'Teacher: {c[2]} | Day: {c[3]} | Time: {c[4]} | Type: {c[5]} | For: {c[6]}',
                                inline=False)
            await ctx.send(content=None, embed=embed)
        else:
            embed.add_field(name='None', value='No classes available')
            await ctx.send(content=None, embed=embed)

    # Wrong command 1
    @commands.command()
    async def lessons(self, ctx):
        await ctx.message.delete()
        await ctx.send("The command is **!classes**, and not **!lessons**")

    # Wrong command 2
    @commands.command()
    async def calendar(self, ctx):
        await ctx.message.delete()
        await ctx.send("The command is **!classes**, and not **!calendar**")

    # Available teachers
    @commands.command()
    async def teachers(self, ctx):
        await ctx.message.delete()
        teachers = await show_teachers()
        if len(teachers) == 0:
            await ctx.send('There is no scheduled teachers!')
        elif len(teachers) == 1:
            await ctx.send('There is 1 scheduled teacher!')
        else:
            await ctx.send(f'There are {len(teachers)} scheduled teachers!')


def setup(client):
    client.add_cog(Show(client))
