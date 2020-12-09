import discord
from discord.ext import commands
from mysqldb import the_database

rules = [
    "Do not post or talk about NSFW content in text or voice chat. This server is a safe for work.",
    "Be respectful of all members, especially Staff.",
    "Avoid topics such as: Politics, Religion, Transphobia, Self-Harm or anything considered controversial anywhere in the server except in the **Debate Club**.",
    "Do not advertise your server or other communities without express consent from an Owner of this server.",
    "Do not share others' personal information without their consent.",
    "Do not flood or spam the text chat. Do not staff members repeatedly without a reason.",
    "No ear rape or mic spam. If you have a loud background, go on push-to-talk or mute.",
    "Try to settle disputes personally. You may mute or block a user. If you cannot resolve the issue, contact staff in <#729454413290143774>.",
    "Do not impersonate users or member of the staff.",
    "No asking to be granted roles/moderator roles, you may apply by accessing the link in <#562019353583681536> but begging the staff repeatedly and irritatingly will result in warnings or even ban."]


class Show(commands.Cog):
    '''
    Commands involving showing some information related to the server.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Show cog is ready!')

    # Shows how many members there are in the server
    @commands.command()
    async def members(self, ctx):
        '''
        Shows how many members there are in the server (including bots).
        '''
        await ctx.message.delete()
        all_users = ctx.guild.members
        await ctx.send(f'{len(all_users)} members!')

    # Shows the specific rule
    @commands.command()
    async def rule(self, ctx, numb: int = None):
        '''
        Shows a specific server rule.
        :param numb: The number of the rule to show.
        '''
        await ctx.message.delete()
        if not numb:
            return await ctx.send('**Invalid parameter!**')
        if numb > 10 or numb <= 0:
            return await ctx.send('**Paremeter out of range!**')

        embed = discord.Embed(title=f'Rule - {numb}#', description=f"{rules[numb - 1]}",
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=ctx.author.guild.name)
        await ctx.send(embed=embed)

    @commands.command(aliases=['ss'])
    @commands.has_permissions()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def server_status(self, ctx) -> None:
        """ Shows some server statuses. """

        member = ctx.author

        group_by += 's'.title()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT 
            STR_TO_DATE(complete_date, '%d/%m/%Y') AS Months,
            SUM(m_joined) - SUM(m_left) AS 'Total Joins',
            members AS 'First Member Record of the Month',
            MAX(members) AS 'Last Member Record of the Month'
            FROM DataBumps
            GROUP BY MONTH(Months)
            """)

        months = await mycursor.fetchall()
        await mycursor.close()

        embed = discord.Embed(
            title="__Server's Monthly Statuses__",
            description="**N**: Month counting;\n"\
            +"**Date**: The day of the month that the bot started registering server statuses;\n"\
            +"**Joins**: The total of users who joined the server in the month;\n"\
            +"**FtRec**: First record of total members of the month;\n"\
            +"**LtRec**: Last record of total members of the month.",
            color=member.color,
            timestamp=ctx.message.created_at,
            url="http://thelanguagesloth.com"
        )

        temp_text1 = f"{'N':>2} | {'Date':<4} | {'Joins':^5} | {'FtRec':>5} | {'LtRec':>5}"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text1}```",
            inline=False
        )

        temp_text2 = ''
        # the_months = {1: '',2: '',3: '',4: '',5: '',6: '',7: '',8: '',9: '',10: '',11: '',12: ''}
        for i, month in enumerate(months):
            the_month = month[0].strftime('%b')
            temp_text2 += f"{i+1:>2} | {the_month:<4} | {month[1]:^5} | {month[2]:>5} | {month[3]:>5}\n"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text2}```",
            inline=False
        )

        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Show(client))
