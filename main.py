import pytz
import discord
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks

# Slash
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import CogBaseCommandObject

import os
from datetime import datetime
from itertools import cycle

from extra.useful_variables import patreon_roles

from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, SkillsUsedRequirement

load_dotenv()

# IDs
user_cosmos_id = int(os.getenv('COSMOS_ID'))
moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
server_id = int(os.getenv('SERVER_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
moderation_log_channel_id = int(os.getenv('MOD_LOG_CHANNEL_ID'))
lesson_category_id = int(os.getenv('LESSON_CAT_ID'))
clock_voice_channel_id = int(os.getenv('CLOCK_VC_ID'))
admin_commands_channel_id = int(os.getenv('ADMIN_COMMANDS_CHANNEL_ID'))
patreon_role_id = int(os.getenv('SLOTH_EXPLORER_ROLE_ID'))
announ_announ_channel_id = int(os.getenv('ANNOUNCEMENT_CHANNEL_ID'))
error_log_channel_id = int(os.getenv('ERROR_LOG_CHANNEL_ID'))
guild_ids = [server_id]

# colors = cycle([(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (143, 0, 255)])
shades_of_pink = cycle([(252, 15, 192), (255, 0, 255), (248, 24, 148),
              (224, 17, 95), (246, 74, 138), (236, 85, 120),
              (255, 11, 255), (227, 49, 99), (253, 185, 200),
              (222, 111, 161), (255, 166, 201), (251, 163, 183),
              (255, 0, 144), (251, 96, 127), (255, 102, 204),
              (241, 156, 187), (251, 174, 210), (249, 135, 197),
              (255, 105, 180), (254, 91, 172), (245, 195, 194),
              (223, 82, 134), (254, 127, 156), (253, 171, 159)
              ])

# Making the client variable
intents = discord.Intents.all()
client = commands.Bot(command_prefix='z!', intents=intents, help_command=None)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

token = os.getenv('TOKEN')


# Tells when the bot is online
@client.event
async def on_ready():
    change_status.start()
    change_color.start()
    # update_timezones.start()
    print('Bot is ready!')


@tasks.loop(seconds=65)
async def change_color():
    guild = client.get_guild(server_id)
    patreon = discord.utils.get(guild.roles, id=patreon_role_id)
    r, g, b = next(shades_of_pink)
    await patreon.edit(colour=discord.Colour.from_rgb(r, g, b))


@client.event
async def on_member_update(before, after):
    if not after.guild:
        return

    roles = before.roles
    roles2 = after.roles
    if len(roles2) < len(roles):
        return

    new_role = None

    for r2 in roles2:
        if r2 not in roles:
            new_role = r2
            break

    

    if new_role:
        for pr in patreon_roles.keys():
            if new_role.id == pr:
                announ = discord.utils.get(before.guild.channels, id=announ_announ_channel_id)
                await announ.send(patreon_roles[pr][0].format(member=after))
                return await after.send(patreon_roles[pr][1])


@client.event
async def on_member_remove(member):
    roles = [role for role in member.roles]
    channel = discord.utils.get(member.guild.channels, id=admin_commands_channel_id)
    embed = discord.Embed(title=member.name, description=f"User has left the server.", colour=discord.Colour.dark_red())
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=f"User Info: {member}")
    embed.add_field(name="ID:", value=member.id, inline=False)
    embed.add_field(name="Guild name:", value=member.display_name, inline=False)
    embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name="Left at:", value=datetime.utcnow().strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name=f"Roles: {len(roles)}", value=" ".join([role.mention for role in roles]), inline=False)
    embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)
    embed.add_field(name="Bot?", value=member.bot)
    # cosmos = discord.utils.get(member.guild.members, id=user_cosmos_id)
    await channel.send(embed=embed)


# Handles the errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do that!")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please, inform all parameters!')

    elif isinstance(error, commands.NotOwner):
        await ctx.send("You're not the bot's owner!")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)

    elif isinstance(error, commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.send(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, commands.errors.RoleNotFound):
        await ctx.send(f"**{error}**")

    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("**Channel not found!**")

    elif isinstance(error, MissingRequiredSlothClass):
        await ctx.send(f"**{error.error_message}: `{error.required_class.title()}`**")

    elif isinstance(error, CommandNotReady):
        await ctx.send("**This command is either under construction or on maintenance!**")

    elif isinstance(error, SkillsUsedRequirement):
        await ctx.send(f"**{error.error_message}**")

    elif isinstance(error, ActionSkillOnCooldown):
        m, s = divmod(error.cooldown - int(error.try_after), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d > 0:
            await ctx.send(f"**You can use your skill again in {d:d} days, {h:d} hours, {m:02d} minutes and {s:02d} seconds!**")
        elif h > 0:
            await ctx.send(f"**You can use your skill again in {h:d} hours, {m:02d} minutes and {s:02d} seconds!**")
        elif m > 0:
            await ctx.send(f"**You can use your skill again in {m:02d} minutes and {s:02d} seconds!**")
        elif s > 0:
            await ctx.send(f"**You can use your skill again in {s:02d} seconds!**")

    print('='*10)
    print(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
    print('='*10)
    error_log = client.get_channel(error_log_channel_id)
    if error_log:
        await error_log.send('='*10)
        await error_log.send(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
        await error_log.send('='*10)


# Members status update
@tasks.loop(seconds=10)
async def change_status():
    guild = client.get_guild(server_id)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(guild.members)} members.'))


@tasks.loop(seconds=60)
async def update_timezones():
    time_now = datetime.now()
    timezones = {'Etc/GMT-1': [clock_voice_channel_id, 'CET']}

    for tz in timezones:
        the_vc = client.get_channel(timezones[tz][0])
        tzone = timezone(tz)
        date_and_time = time_now.astimezone(tzone)
        date_and_time_in_text = date_and_time.strftime('%H:%M')
        print(the_vc)
        await the_vc.edit(name=f'{timezones[tz][1]} - {date_and_time_in_text}')


# Joins VC log #########
@client.event
async def on_voice_state_update(member, before, after):
    # No longer being used

    return
    if not member.guild:
        return
    mod_role = discord.utils.get(member.guild.roles, id=moderator_role_id)
    teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
    if mod_role not in member.roles and teacher_role not in member.roles:
        return

    if not before.self_mute == after.self_mute or not before.self_deaf == after.self_deaf:
        return

    mod_log = client.get_channel(moderation_log_channel_id)
    if after.channel is not None:
        # Switched between voice channels
        if before.channel is not None:
            if mod_role in member.roles:
                embed = discord.Embed(
                    description=f'**{member}** switched between voice channels: {before.channel.name} - {after.channel.name}',
                    colour=discord.Colour.dark_green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channels', value=f'{before.channel.name} - {after.channel.name}', inline=False)
                embed.add_field(name='ID',
                                value=f'```py\nUser = {member.id}\nPrevious Channel = {before.channel.id}\nCurrent Channel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await mod_log.send(embed=embed)
        # Entered a voice channel
        else:

            if mod_role in member.roles:
                embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}',
                                      colour=discord.Colour.green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.avatar_url)
                await mod_log.send(embed=embed)

    # Left voice channel
    elif after.channel is None:

        if mod_role in member.roles:
            embed = discord.Embed(description=f'**{member}** left voice channel: {before.channel.name}',
                                  colour=discord.Colour.red(), timestamp=datetime.utcnow())
            embed.add_field(name='Channel', value=f'{before.channel.name}', inline=False)
            embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {before.channel.id}```')
            embed.set_footer(text=f"Guild name: {member.guild.name}")
            embed.set_author(name=member, icon_url=member.avatar_url)
            await mod_log.send(embed=embed)

start_time = datetime.utcnow()


@client.command()
async def uptime(ctx: commands.Context):
    """ Shows for how much time the bot is online. """

    now = datetime.utcnow()  # Timestamp of when uptime function is run
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
    elif hours:
        time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."
    elif minutes:
        time_format = "**{m}** minutes, and **{s}** seconds."
    else:
        time_format = "**{s}** seconds."
    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
    await ctx.send(f"I've been online for {uptime_stamp}")


@client.command()
async def help(ctx, *, cmd: str = None):
    """ Shows some information about commands and categories. 
    :param cmd: The command/category. """

    if not cmd:
        embed = discord.Embed(
            title="All commands and categories",
            description=f"```ini\nUse {client.command_prefix}help command or {client.command_prefix}help category to know more about a specific command or category\n\n[Examples]\n[1] Category: {client.command_prefix}help SlothCurrency\n[2] Command : {client.command_prefix}help rep```",
            timestamp=ctx.message.created_at,
            color=ctx.author.color
            )

        for cog in client.cogs:
            cog = client.get_cog(cog)

            commands = [f"{client.command_prefix}{c.name}" for c in cog.get_commands() if not c.hidden]
            slash_commands = [f"/{sc}" for sc, sco in cog.client.slash.commands.items() if sco.cog == cog]
            commands.extend(slash_commands)

            if commands:
                embed.add_field(
                    name=f"__{cog.qualified_name}__",
                    value=f"`Commands:` {', '.join(commands)}",
                    inline=False
                    )

        cmds = []
        slash_cmds = [f"/{sc}" for sc, sco in client.slash.commands.items() if not sco.cog]
        for y in client.walk_commands():
            if not y.cog_name and not y.hidden:
                cmds.append(f"{client.command_prefix}{y.name}")

        cmds.extend(slash_cmds)
                
        embed.add_field(
            name='__Uncategorized Commands__',
            value=f"`Commands:` {', '.join(cmds)}",
            inline=False)
        await ctx.send(embed=embed)

    else:
        # Checks if it's a command
        if cmd.startswith('/') and (command := client.slash.commands.get(cmd[1:])):
            command_embed = discord.Embed(title=f"__Command:__ /{command.name}", description=f"__**Description:**__\n```{command.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
            return await ctx.send(embed=command_embed)
            
        if command := client.get_command(cmd.lower()):
            command_embed = discord.Embed(title=f"__Command:__ {client.command_prefix}{command.qualified_name}", description=f"__**Description:**__\n```{command.help}```", color=ctx.author.color, timestamp=ctx.message.created_at)
            return await ctx.send(embed=command_embed)

        # Checks if it's a cog
        for cog in client.cogs:
            if str(cog).lower() == str(cmd).lower():
                cog = client.get_cog(cog)
                cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
                for c in cog.get_commands():
                    if not c.hidden:
                        cog_embed.add_field(name=c.qualified_name, value=c.help, inline=False)

                return await ctx.send(embed=cog_embed)

        # Otherwise, it's an invalid parameter (Not found)
        else:
            await ctx.send(f"**Invalid parameter! `{cmd}` is neither a command nor a cog!**")


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def load(ctx, extension: str = None):
    '''
    Loads a cog.
    :param extension: The cog.
    '''
    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} loaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def unload(ctx, extension: str = None):
    '''
    Unloads a cog.
    :param extension: The cog.
    '''
    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} unloaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def reload(ctx, extension: str = None):
    '''
    Reloads a cog.
    :param extension: The cog.
    '''
    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} reloaded!**", delete_after=3)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)
