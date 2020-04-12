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
        await ctx.channel.purge(limit=amount + 1)

    # Warns a member
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        await ctx.message.delete()
        if not member:
            await ctx.send("Please, specify a member!", delete_after=3)
        else:
            # General embed
            general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_gold())
            general_embed.set_author(name=f'{member} has been warned', icon_url=member.avatar_url)
            await ctx.send(embed=general_embed)
            # Moderation log embed
            moderation_log = ctx.utils.get(ctx.guild.channels, id=mod_log_id)
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
    async def mute(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role not in member.roles:
            await member.add_roles(role)
            await ctx.send("**Member muted!**")
        else:
            await ctx.send('**The member is already muted!**')

    # Unmutes a member
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send("**Member unmuted!**")
        else:
            await ctx.send("**The member is not even muted!**", delete_after=3)

    # Mutes a member temporarily
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, minutes: int = 5):
        await ctx.message.delete()
        if minutes == 0:
            return await ctx.send('**Inform a valid parameter!**', delete_after=3)

        role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
        seconds = minutes * 60
        if not member:
            return await ctx.send("**Please, specify a member!**", delete_after=3)
        if role not in member.roles:
            await member.add_roles(role)
            await ctx.send(f"**{member} was tempmuted for {minutes} minutes!**")
            await asyncio.sleep(seconds)
            await member.remove_roles(role)
            await ctx.send(f'**{member} was unmuted!**')
        else:
            await ctx.send('**The member is already muted!**', delete_after=3)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
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
                moderation_log = ctx.utils.get(ctx.guild.channels, id=mod_log_id)
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
                moderation_log = ctx.utils.get(ctx.guild.channels, id=mod_log_id)
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
                moderation_log = ctx.utils.get(ctx.guild.channels, id=mod_log_id)
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


def setup(client):
    client.add_cog(Moderation(client))
