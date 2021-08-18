import discord
from discord.ext import commands
import os

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
announcement_channel_id = int(os.getenv('ANNOUNCEMENT_CHANNEL_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), mod_role_id]


class Communication(commands.Cog):
    """ A cog related to communication commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Communication cog is ready!')

    # Says something by using the bot
    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def say(self, ctx):
        """ (ADM) Makes the bot say something. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split('!say', 1)
        await ctx.send(msg[1])

    # Spies a channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spy(self, ctx, cid):
        """ (ADM) Makes the bot send a message to a given channel.
        :param cid: The ID of the channel. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 3:
            return await ctx.send('You must inform all parameters!')

        spychannel = self.client.get_channel(int(cid))
        msg = ctx.message.content.split(cid)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await spychannel.send(embed=embed)

    # Welcomes an user by telling them to assign a role
    @commands.command()
    @commands.has_any_role(474774889778380820, 574265899801116673, 699296718705000559)
    async def welcome(self, ctx, member: discord.Member = None):
        """ (WELCOMER) Welcomes a user.
        :param member: The member to welcome. """

        await ctx.message.delete()
        if not member:
            return await ctx.send('Inform a member!')

        bots_and_commands_channel = discord.utils.get(ctx.guild.channels, id=bots_and_commands_channel_id)
        await bots_and_commands_channel.send(
            f'''__**Welcome to the Language Sloth**__! {member.mention}
This is a community of people who are practicing and studying languages from all around the world! While you're here, you will also make tons of new friends! There is a lot to do here in the server but there are some things you should do to start off.

1. Make sure you go check out the <#688967996512665655> and the informations page. These rules are very important and are taken seriously here on the server.
2. After you have finished reading those, you can assign yourself some roles at <#679333977705676830> <#683987207065042944> <#688037387561205824> and <#562019509477703697>! These roles will give you access to different voice and text channels! To choose your role click on the flag that best represents your native language.

If you have any questions feel free to ask! And if you experience any type of problem make sure you let a staff member know right away''')

    # Pretends that a role has been given to an user by the bot
    @commands.command()
    @commands.has_any_role(474774889778380820, 574265899801116673, 699296718705000559)
    async def auto(self, ctx, member: discord.Member = None, language: str = None):
        """ (WELCOMER) Makes the bot send an 'automatic' message to someone.
        :param member: The member:
        :param  language: The language. """

        await ctx.message.delete()
        if not language:
            return await ctx.send('**Inform a language!**', delete_after=3)

        elif not member:
            return await ctx.send('**Inform a member!**', delete_after=3)

        bots_and_commands_channel = discord.utils.get(ctx.guild.channels, id=bots_and_commands_channel_id)
        await bots_and_commands_channel.send(
            f'''{member.mention} - Hey! since you didn't assign your native language I went ahead and assigned it for you automatically based on my best guess of what is your native language, I came to the conclusion that it is {language.title()}.  If I'm incorrect please let me know!''')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        """ (ADM) Announces a message in the announcements channel using the bot. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        announce_channel = discord.utils.get(ctx.guild.channels, id=announcement_channel_id)
        msg = ctx.message.content.split('!announce', 1)
        await announce_channel.send(msg[1])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, member: discord.Member = None, *, message=None):
        """ (ADM) Sends a Direct Message to someone.
        :param member: The member to send the message to.
        :param message: The message to send. """

        await ctx.message.delete()

        if not message:
            return await ctx.send("**Inform a message to send!**", delete_after=3)

        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        check_member = ctx.guild.get_member(member.id)
        if check_member:
            return await member.send(message)
        await ctx.send(f"**Member: {member} not found!", delete_after=3)


def setup(client):
    """ Cog's setup function. """

    client.add_cog(Communication(client))
