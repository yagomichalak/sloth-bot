import discord
from discord.ext import commands

general_voice_chat_id = 562019539135627276
announcement_channel_id = 562019353583681536


class Communication(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Communication cog is ready!')

    # Says something by using the bot
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def say(self, ctx):
        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split('!say', 1)
        await ctx.send(msg[1])

    # Spies a channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spy(self, ctx, cid):
        await ctx.message.delete()
        if len(ctx.message.content.split()) < 3:
            return await ctx.send('You must inform all parameters!')

        spychannel = self.client.get_channel(int(cid))
        msg = ctx.message.content.split(cid)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await spychannel.send(embed=embed)

    # Welcomes an user by telling them to assign a role
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if not member:
            return await ctx.send('Inform a member!')

        general_channel = discord.utils.get(ctx.guild.channels, id=general_voice_chat_id)
        await general_channel.send(
            f'''{member.mention}, remember to Assign your Native language in  <#679333977705676830>, click in the flag that best represents your native language!
    This way you will have full access to the server and its voice channels!
    Enjoy!!''')

    # Pretends that a role has been given to an user by the bot
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def auto(self, ctx, member: discord.Member = None, text: str = None):
        await ctx.message.delete()
        if not text:
            return await ctx.send('Inform the parameters!')

        elif not member:
            return await ctx.send('Inform a member!')

        general_channel = discord.utils.get(ctx.guild.channels, id=general_voice_chat_id)
        await general_channel.send(
            f'''{member.mention} - Hey! since you didn't assign your native language I went ahead and assigned it for you automatically based on my best guess of what is your native language, I came to the conclusion that it is {text.title()}.  If I'm incorrect please let me know!''')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        announce_channel = discord.utils.get(ctx.guild.channels, id=announcement_channel_id)
        msg = ctx.message.content.split('!announce', 1)
        await announce_channel.send(msg[1])


def setup(client):
    client.add_cog(Communication(client))
