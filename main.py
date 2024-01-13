import discord
from discord.utils import escape_mentions
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks

from extra import utils
from extra.menu import PaginatorView
from typing import List
import os
from datetime import datetime
from itertools import cycle
from typing import Dict, Union, Any

from extra.useful_variables import patreon_roles

from extra.customerrors import (
    MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, 
    SkillsUsedRequirement, ActionSkillsLocked, KidnappedCommandError,
    StillInRehabError
)

load_dotenv()

# IDs
user_cosmos_id = int(os.getenv('COSMOS_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
moderator_role_id = int(os.getenv('MOD_ROLE_ID', 123))
booster_role_id = int(os.getenv('BOOSTER_ROLE_ID', 123))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID', 123))
giveaway_manager_role_id: int = int(os.getenv('GIVEAWAY_MANAGER_ROLE_ID', 123))

server_id = int(os.getenv('SERVER_ID', 123))

moderation_log_channel_id = int(os.getenv('MOD_LOG_CHANNEL_ID', 123))
lesson_category_id = int(os.getenv('LESSON_CAT_ID', 123))
clock_voice_channel_id = int(os.getenv('CLOCK_VC_ID', 123))
admin_commands_channel_id = int(os.getenv('ADMIN_COMMANDS_CHANNEL_ID', 123))
patreon_role_id = int(os.getenv('SLOTH_EXPLORER_ROLE_ID', 123))
support_us_channel_id = int(os.getenv('SUPPORT_US_CHANNEL_ID', 123))
error_log_channel_id = int(os.getenv('ERROR_LOG_CHANNEL_ID', 123))
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
client = commands.Bot(command_prefix='z!', intents=discord.Intents.all(), help_command=None, case_insensitive=True)

# Tells when the bot is online
@client.event
async def on_ready() -> None:
    change_status.start()
    change_color.start()
    print('Bot is ready!')


@tasks.loop(seconds=65)
async def change_color() -> None:
    guild = client.get_guild(server_id)
    patreon = discord.utils.get(guild.roles, id=patreon_role_id)
    r, g, b = next(shades_of_pink)
    await patreon.edit(colour=discord.Colour.from_rgb(r, g, b))

@client.event
async def on_member_update(before, after) -> None:
    """ Sends a messages to new patreons, as soon as they get their patreon roles. """

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
                support_us_channel = discord.utils.get(before.guild.channels, id=support_us_channel_id)
                await support_us_channel.send(patreon_roles[pr][0].format(member=after))
                return await after.send(patreon_roles[pr][1])


@client.event
async def on_member_remove(member) -> None:
    roles = [role for role in member.roles]
    channel = discord.utils.get(member.guild.channels, id=admin_commands_channel_id)
    embed = discord.Embed(title=member.name, description=f"User has left the server.", colour=discord.Colour.dark_red())
    embed.set_thumbnail(url=member.display_avatar)
    embed.set_author(name=f"User Info: {member}")
    embed.add_field(name="ID:", value=member.id, inline=False)
    embed.add_field(name="Guild name:", value=member.display_name, inline=False)
    embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name="Left at:", value=datetime.utcnow().strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
    embed.add_field(name=f"Roles: {len(roles)}", value=" ".join([role.mention for role in roles]), inline=False)
    embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)
    embed.add_field(name="Bot?", value=member.bot)
    await channel.send(embed=embed)

@client.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**You can't do that!**")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please, inform all parameters!**')

    elif isinstance(error, commands.NotOwner):
        await ctx.send("**You're not the bot's owner!**")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)

    elif isinstance(error, commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.send(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, commands.errors.RoleNotFound):
        await ctx.send(f"**Role not found**")

    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("**Channel not found!**")

    elif isinstance(error, MissingRequiredSlothClass):
        await ctx.send(f"**{error.error_message}: `{error.required_class.title()}`**")

    elif isinstance(error, ActionSkillsLocked):
        pass

    elif isinstance(error, KidnappedCommandError):
        await ctx.send(f"**You cannot interact with tribes until any member of your tribe pays your kidnap rescue value**")

    elif isinstance(error, CommandNotReady):
        await ctx.send("**This command is either under construction or on maintenance!**")

    elif isinstance(error, SkillsUsedRequirement):
        await ctx.send(f"**{error.error_message}**")

    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.send("**You can't do that!**")

    elif isinstance(error, commands.CheckAnyFailure):
        if isinstance(error.errors[0], ActionSkillOnCooldown):
            the_error = error.errors[0]
            cooldown = the_error.skill_ts + the_error.cooldown
            await ctx.send(f"**You can use your skill again <t:{int(cooldown)}:R>!**")

        if isinstance(error.errors[0], StillInRehabError):
            the_error = error.errors[0]
            cooldown = the_error.rehab_ts + the_error.cooldown
            await ctx.send(f"**You will leave rehab <t:{int(cooldown)}:R>!** <:nervous_sloth:974087109176598579>")

    elif isinstance(error, ActionSkillOnCooldown):
        cooldown = error.skill_ts + error.cooldown
        await ctx.send(f"**You can use your skill again <t:{int(cooldown)}:R>!**")

    elif isinstance(error, StillInRehabError):
        cooldown = error.rehab_ts + error.cooldown
        await ctx.send(f"**You will leave rehab <t:{int(cooldown)}:R>!** <:nervous_sloth:974087109176598579>")

    elif isinstance(error, ActionSkillsLocked):
        await ctx.send(f"**{error.error_message}**")

    print('='*10)
    print(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
    print('='*10)
    error_log = client.get_channel(error_log_channel_id)
    if error_log:
        await error_log.send('='*10)
        await error_log.send(f"ERROR: {escape_mentions(str(error))} | Class: {error.__class__} | Cause: {error.__cause__}")
        await error_log.send('='*10)

@client.event
async def on_application_command_error(ctx, error) -> None:

    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond('**Please, inform all parameters!**')

    elif isinstance(error, commands.NotOwner):
        await ctx.respond("**You're not the bot's owner!**")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)

    elif isinstance(error, ActionSkillsLocked):
        pass

    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.respond(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, commands.errors.RoleNotFound):
        await ctx.respond(f"**Role not found**")

    elif isinstance(error, commands.ChannelNotFound):
        await ctx.respond("**Channel not found!**")


    print('='*10)
    print(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
    print('='*10)
    error_log = client.get_channel(error_log_channel_id)
    if error_log:
        await error_log.send('='*10)
        await error_log.send(f"ERROR: {escape_mentions(str(error))} | Class: {error.__class__} | Cause: {error.__cause__}")
        await error_log.send('='*10)

# @client.event
# async def on_typing(channel, user, when) -> None:
#     await channel.send("**I smell you... 👀**")
    

# Members status update
@tasks.loop(seconds=10)
async def change_status() -> None:
    guild = client.get_guild(server_id)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(guild.members)} members.'))


@tasks.loop(seconds=60)
async def update_timezones() -> None:
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
async def on_voice_state_update(member, before, after) -> None:
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
                embed.set_author(name=member, icon_url=member.display_avatar)
                await mod_log.send(embed=embed)
        # Entered a voice channel
        else:

            if mod_role in member.roles:
                embed = discord.Embed(description=f'**{member}** joined voice channel: {after.channel.name}',
                                      colour=discord.Colour.green(), timestamp=datetime.utcnow())
                embed.add_field(name='Channel', value=f'{after.channel.name}', inline=False)
                embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {after.channel.id}```')
                embed.set_footer(text=f"Guild name: {member.guild.name}")
                embed.set_author(name=member, icon_url=member.display_avatar)
                await mod_log.send(embed=embed)

    # Left voice channel
    elif after.channel is None:

        if mod_role in member.roles:
            embed = discord.Embed(description=f'**{member}** left voice channel: {before.channel.name}',
                                  colour=discord.Colour.red(), timestamp=datetime.utcnow())
            embed.add_field(name='Channel', value=f'{before.channel.name}', inline=False)
            embed.add_field(name='ID', value=f'```py\nUser = {member.id}\nChannel = {before.channel.id}```')
            embed.set_footer(text=f"Guild name: {member.guild.name}")
            embed.set_author(name=member, icon_url=member.display_avatar)
            await mod_log.send(embed=embed)

start_time = datetime.now(timezone('Etc/GMT'))


@client.command()
async def uptime(ctx: commands.Context) -> None:
    """ Shows for how much time the bot is online. """

    now = await utils.get_time_now()  # Timestamp of when uptime function is run
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


async def make_help_embed(req: str, member: Union[discord.Member, discord.User], search: str, example: Any, 
    offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None, **kwargs: Dict[str, Any]) -> discord.Embed:
    """ Makes an embed for .
    :param req: The request URL link.
    :param member: The member who triggered the command.
    :param search: The search that was performed.
    :param example: The current search example.
    :param offset: The current page of the total entries.
    :param lentries: The length of entries for the given search. """

    embed: discord.Embed = None
    target = kwargs.get("target")
    if not target:
        target = member

    per_page = kwargs.get("per_page")
    current_embed = kwargs.get("current_embed")
    embed = current_embed
    embed.clear_fields()

    for i in range(0, per_page, 1):
        if offset - 1 + i < lentries:
            entry = entries[offset-1 + i]
            embed.add_field(**entry)
        else:
            break

    # Sets the author of the search
    embed.set_author(name=target, icon_url=target.display_avatar)
    # Makes a footer with the a current page and total page counter
    embed.set_footer(text=f"Requested by {target}", icon_url=target.display_avatar)

    return embed


@client.command()
async def help(ctx, *, cmd: str =  None) -> None:
    """ Shows some information about commands and categories. 
    :param cmd: The command/category. """

    if not cmd:
        fields = []
        current_embed = discord.Embed(
            title=f"All commands and categories",
            description=f"```ini\nUse {client.command_prefix}help command or {client.command_prefix}help category to know more about a specific command or category\n\n[Examples]\n[1] Category: {client.command_prefix}help SlothCurrency\n[2] Command : {client.command_prefix}help rep```",
            timestamp=ctx.message.created_at,
            color=ctx.author.color
        )

        for cog in client.cogs:
            cog = client.get_cog(cog)
            cog_commands = [c for c in cog.__cog_commands__ if hasattr(c, 'parent') and c.parent is None]
            commands = [f"{client.command_prefix}{c.name}" for c in cog_commands if hasattr(c, 'hidden') and not c.hidden]
            if commands:
                fields.append({
                    "name": f"__{cog.qualified_name}__",
                    "value": f"`Commands:` {', '.join(commands)}",
                    "inline": False}
                )

        cmds = []
        for y in client.walk_commands():
            if not y.cog_name and not y.hidden:
                cmds.append(f"{client.command_prefix}{y.name}")

        fields.append({
            "name": '__Uncategorized Commands__',
            "value": f"`Commands:` {', '.join(cmds)}",
            "inline": False}
        )
        
        additional = {
            "client": client,
            "change_embed": make_help_embed,
            "target": ctx.author,
            "per_page": 25,
            "current_embed": current_embed
        }
        view = PaginatorView(fields, increment=25, **additional)
        embed = await view.make_embed(ctx.author)
        await ctx.send(embed=embed, view=view)

    else:  
        cmd = escape_mentions(cmd)
        if command := client.get_command(cmd.lower()):
            command_embed = discord.Embed(title=f"__Command:__ {client.command_prefix}{command.qualified_name}", description=f"__**Description:**__\n```{command.help}```", color=ctx.author.color, timestamp=ctx.message.created_at)
            return await ctx.send(embed=command_embed)
        
        fields = []

        # Checks if it's a cog
        for cog in client.cogs:
            if str(cog).lower() == str(cmd).lower():
                cog = client.get_cog(cog)
                current_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
                cog_commands = [c for c in cog.__cog_commands__ if hasattr(c, 'hidden') and hasattr(c, 'parent') and c.parent is None]
                for c in cog_commands:
                    if not c.hidden:
                        fields.append({"name": c.qualified_name, "value": c.help, "inline": False})
            
                additional = {
                    "client": client,
                    "change_embed": make_help_embed,
                    "target": ctx.author,
                    "per_page": 25,
                    "current_embed": current_embed
                }
                view = PaginatorView(fields, increment=25, **additional)
                embed = await view.make_embed(ctx.author)
                return await ctx.send(embed=embed, view=view)
        # Otherwise, it's an invalid parameter (Not found)
        else:
            await ctx.send(f"**Invalid parameter! It is neither a command nor a cog!**")


@client.command(aliases=['al', 'alias'])
async def aliases(ctx, *, cmd: str =  None) -> None:
    """ Shows some information about commands and categories. 
    :param cmd: The command. """

    if not cmd:
        return await ctx.send("**Please, informe one command!**")

    cmd = escape_mentions(cmd)
    if command := client.get_command(cmd.lower()):
        embed = discord.Embed(title=f"Command: {command}", color=ctx.author.color, timestamp=ctx.message.created_at)
        aliases = [alias for alias in command.aliases]

        if not aliases:
            return await ctx.send("**This command doesn't have any aliases!**")
        embed.description = '**Aliases: **' + ', '.join(aliases)
        return await ctx.send(embed=embed)
    else:
        await ctx.send(f"**Invalid parameter! It is neither a command nor a cog!**")

@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def load(ctx, extension: str = None) -> None:
    """ Loads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} loaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def unload(ctx, extension: str = None) -> None:
    """ Unloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} unloaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def reload(ctx, extension: str = None) -> None:
    """ Reloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} reloaded!**", delete_after=3)

forbidden_files: List[str] = [
    # 'createdynamicroom.py'
]

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename not in forbidden_files:
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('TOKEN'))
