import discord
from discord.ext import commands

rules = [
    "Do not post or talk about NSFW content in text or voice chat. This server is a safe for work.",
    "Be respectful of all members, especially Staff.",
    "Avoid topics such as: Politics,Religion,Self-Harm or anything considered controversial anywhere in the server except in the **Debate Club**.",
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


def setup(client):
    client.add_cog(Show(client))
