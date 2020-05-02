import discord
from discord.ext import commands
import asyncio

mod_log_id = 562195805272932372
muted_role_id = 537763763982434304


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog is ready!')

    # Purge command
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=0):
        '''
        Purges messages.
        :param amount: The amount of messages to purge.
        '''
        await ctx.channel.purge(limit=amount + 1)

    # Warns a member
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        '''
        Warns a member.
        :param member: The @ or ID of the user to warn.
        :param reason: The reason for warning the user. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            await ctx.send("Please, specify a member!", delete_after=3)
        else:
            # General embed
            general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_gold())
            general_embed.set_author(name=f'{member} has been warned', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
            # Moderation log embed
            moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
            embed = discord.Embed(title='__**Warning**__', colour=discord.Colour.dark_gold(),
                                  timestamp=ctx.message.created_at)
            embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                            inline=False)
            embed.add_field(name='Reason:', value=f'```{reason}```')
            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.avatar_url)
            await moderation_log.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, reason = None):
        '''
        Mutes a member.
        :param member: The @ or the ID of the user to mute.
        '''
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role not in member.roles:
            await member.add_roles(role)
            # General embed
            general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_grey(), timestamp=ctx.message.created_at)
            general_embed.set_author(name=f'{member} has been muted', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
            # Moderation log embed
            moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
            embed = discord.Embed(title='__**Mute**__', colour=discord.Colour.dark_grey(),
                                  timestamp=ctx.message.created_at)
            embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                            inline=False)
            embed.add_field(name='Reason:', value=f'```{reason}```')

            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.avatar_url)
            await moderation_log.send(embed=embed)
        
        else:
            await ctx.send(f'**{member} is already muted!**', delete_after=5)

    # Unmutes a member
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        '''
        Unmutes a member.
        :param member: The @ or the ID of the user to unmute.
        '''
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role in member.roles:
            await member.remove_roles(role)
            # General embed
            general_embed = discord.Embed(colour=discord.Colour.light_grey(),
                                          timestamp=ctx.message.created_at)
            general_embed.set_author(name=f'{member} has been unmuted', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
            # Moderation log embed
            moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
            embed = discord.Embed(title='__**Unmute**__', colour=discord.Colour.light_grey(),
                                  timestamp=ctx.message.created_at)
            embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                            inline=False)
            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.avatar_url)
            await moderation_log.send(embed=embed)

        else:
            await ctx.send(f'**{member} is not even muted!**', delete_after=5)

    # Mutes a member temporarily
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, minutes: int = 5, *, reason =  None):
        '''
        Mutes a member for a determined amount of time.
        :param member: The @ or the ID of the user to tempmute.
        :param minutes: The amount of minutes that the user will be muted.
        '''
        await ctx.message.delete()
        if minutes == 0:
            return await ctx.send('**Inform a valid parameter!**', delete_after=3)

        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        seconds = minutes * 60
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role not in member.roles:
            await member.add_roles(role)
            # General embed
            general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.lighter_grey(),
                                          timestamp=ctx.message.created_at)
            general_embed.set_author(name=f'{member} has been tempmuted', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
            # Moderation log embed
            moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
            embed = discord.Embed(title='__**Tempmute**__', colour=discord.Colour.lighter_grey(),
                                  timestamp=ctx.message.created_at)
            embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                            inline=False)
            embed.add_field(name='Reason:', value=f'```{reason}```')
            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Tempmuted by {ctx.author}", icon_url=ctx.author.avatar_url)
            await moderation_log.send(embed=embed)
            # After a while
            await asyncio.sleep(seconds)
            await member.remove_roles(role)
            general_embed = discord.Embed(colour=discord.Colour.lighter_grey(),
                                          timestamp=ctx.message.created_at)
            general_embed.set_author(name=f'{member} is no longer tempmuted', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
        else:
            await ctx.send(f'**{member} is not even muted!**', delete_after=5)
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        '''
        Kicks a member from the server.
        :param member: The @ or ID of the user to kick.
        :param reason: The reason for kicking the user. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            await ctx.send('**Please, specify a member!**', delete_after=3)
        else:
            try:
                await member.kick(reason=reason)
            except Exception:
                await ctx.send('**You cannot do that!**', delete_after=3)
            else:
                # General embed
                general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.magenta())
                general_embed.set_author(name=f'{member} has been kicked', icon_url=member.avatar_url)
                await ctx.send(embed=general_embed)
                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(title='__**Kick**__', colour=discord.Colour.magenta(),
                                      timestamp=ctx.message.created_at)
                embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                                inline=False)
                embed.add_field(name='Reason:', value=f'```{reason}```')
                embed.set_author(name=member)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.avatar_url)
                await moderation_log.send(embed=embed)

    # Bans a member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        '''
        Bans a member from the server.
        :param member: The @ or ID of the user to ban.
        :param reason: The reason for banning the user. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            await ctx.send('**Please, specify a member!**', delete_after=3)
        else:
            try:
                await member.ban(delete_message_days=7, reason=reason)
            except Exception:
                await ctx.send('**You cannot do that!**', delete_after=3)
            else:
                # General embed
                general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_red())
                general_embed.set_author(name=f'{member} has been banned', icon_url=member.avatar_url)
                await ctx.send(embed=general_embed)
                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(title='__**Banishment**__', colour=discord.Colour.dark_red(),
                                      timestamp=ctx.message.created_at)
                embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                                inline=False)
                embed.add_field(name='Reason:', value=f'```{reason}```')
                embed.set_author(name=member)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=f"Banned by {ctx.author}", icon_url=ctx.author.avatar_url)
                await moderation_log.send(embed=embed)

    # Unbans a member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member=None):
        '''
        Unbans a member from the server.
        :param member: The full nickname and # of the user to unban.
        '''
        await ctx.message.delete()
        if not member:
            return await ctx.send('**Please, inform a member!**', delete_after=3)

        banned_users = await ctx.guild.bans()
        try:
            member_name, member_discriminator = str(member).split('#')
        except ValueError:
            return await ctx.send('**Wrong parameter!**', delete_after=3)

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                # General embed
                general_embed = discord.Embed(colour=discord.Colour.red())
                general_embed.set_author(name=f'{user} has been unbanned', icon_url=user.avatar_url)
                await ctx.send(embed=general_embed)
                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(title='__**Unbanishment**__', colour=discord.Colour.red(),
                                      timestamp=ctx.message.created_at)
                embed.add_field(name='User info:', value=f'```Name: {user.display_name}\nId: {user.id}```',
                                inline=False)
                embed.set_author(name=user)
                embed.set_thumbnail(url=user.avatar_url)
                embed.set_footer(text=f"Unbanned by {ctx.author}", icon_url=ctx.author.avatar_url)
                await moderation_log.send(embed=embed)
                return
        else:
            await ctx.send('**Member not found!**', delete_after=3)

    # Bans a member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def softban(self, ctx, member: discord.Member = None, *, reason=None):
        '''
        Bans and unbans a member from the server; deleting their messages from the last 7 seven days.
        :param member: The @ or ID of the user to softban.
        :param reason: The reason for softbanning the user. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            await ctx.send('**Please, specify a member!**', delete_after=3)
        else:
            try:
                await member.ban(delete_message_days=7, reason=reason)
                await member.unban(reason=reason)
            except Exception:
                await ctx.send('**You cannot do that!**', delete_after=3)
            else:
                # General embed
                general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_purple())
                general_embed.set_author(name=f'{member} has been softbanned', icon_url=member.avatar_url)
                await ctx.send(embed=general_embed)
                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(title='__**SoftBanishment**__', colour=discord.Colour.dark_purple(),
                                      timestamp=ctx.message.created_at)
                embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
                                inline=False)
                embed.add_field(name='Reason:', value=f'```{reason}```')
                embed.set_author(name=member)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=f"SoftBanned by {ctx.author}", icon_url=ctx.author.avatar_url)
                await moderation_log.send(embed=embed)


def setup(client):
    client.add_cog(Moderation(client))
