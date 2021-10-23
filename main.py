import discord
from discord.app import Option, option
from discord.utils import escape_mentions
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks

from extra import utils
from typing import Dict, List
import json
import os
from datetime import datetime
from itertools import cycle

from extra.useful_variables import patreon_roles

from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, SkillsUsedRequirement

load_dotenv()

# IDs
user_cosmos_id = int(os.getenv('COSMOS_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
booster_role_id = int(os.getenv('BOOSTER_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
giveaway_manager_role_id: int = int(os.getenv('GIVEAWAY_MANAGER_ROLE_ID'))

server_id = int(os.getenv('SERVER_ID'))

moderation_log_channel_id = int(os.getenv('MOD_LOG_CHANNEL_ID'))
lesson_category_id = int(os.getenv('LESSON_CAT_ID'))
clock_voice_channel_id = int(os.getenv('CLOCK_VC_ID'))
admin_commands_channel_id = int(os.getenv('ADMIN_COMMANDS_CHANNEL_ID'))
patreon_role_id = int(os.getenv('SLOTH_EXPLORER_ROLE_ID'))
support_us_channel_id = int(os.getenv('SUPPORT_US_CHANNEL_ID'))
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
client = commands.Bot(command_prefix='z!', intents=discord.Intents.all(), help_command=None)

# Tells when the bot is online
@client.event
async def on_ready():
    change_status.start()
    change_color.start()
    print('Bot is ready!')


@tasks.loop(seconds=65)
async def change_color():
    guild = client.get_guild(server_id)
    patreon = discord.utils.get(guild.roles, id=patreon_role_id)
    r, g, b = next(shades_of_pink)
    await patreon.edit(colour=discord.Colour.from_rgb(r, g, b))

@client.event
async def on_member_update(before, after):
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
async def on_member_remove(member):
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
async def on_command_error(ctx, error):
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

    elif isinstance(error, ActionSkillOnCooldown):
        cooldown = error.skill_ts + error.cooldown
        await ctx.send(f"**You can use your skill again <t:{int(cooldown)}:R>!**")

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

    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.respond(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, commands.errors.RoleNotFound):
        await ctx.respond(f"**Role not found**")

    elif isinstance(error, commands.ChannelNotFound):
        await ctx.respond("**Channel not found!**")

    elif isinstance(error, discord.app.errors.CheckFailure):
        await ctx.respond("**It looks like you can't run this command!**")


    print('='*10)
    print(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
    print('='*10)
    error_log = client.get_channel(error_log_channel_id)
    if error_log:
        await error_log.send('='*10)
        await error_log.send(f"ERROR: {escape_mentions(str(error))} | Class: {error.__class__} | Cause: {error.__cause__}")
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
async def uptime(ctx: commands.Context):
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


@client.command()
async def help(ctx, *, cmd: str =  None):
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
            cog_commands = [c for c in cog.__cog_commands__ if hasattr(c, 'parent') and c.parent is None]
            commands = [f"{client.command_prefix}{c.name}" for c in cog_commands if not c.hidden]
            if commands:
                embed.add_field(
                    name=f"__{cog.qualified_name}__",
                    value=f"`Commands:` {', '.join(commands)}",
                    inline=False
                    )

        cmds = []
        for y in client.walk_commands():
            if not y.cog_name and not y.hidden:
                cmds.append(f"{client.command_prefix}{y.name}")

        embed.add_field(
            name='__Uncategorized Commands__',
            value=f"`Commands:` {', '.join(cmds)}",
            inline=False)
        await ctx.send(embed=embed)

    else:  
        cmd = escape_mentions(cmd)
        if command := client.get_command(cmd.lower()):
            command_embed = discord.Embed(title=f"__Command:__ {client.command_prefix}{command.qualified_name}", description=f"__**Description:**__\n```{command.help}```", color=ctx.author.color, timestamp=ctx.message.created_at)
            return await ctx.send(embed=command_embed)

        # Checks if it's a cog
        for cog in client.cogs:
            if str(cog).lower() == str(cmd).lower():
                cog = client.get_cog(cog)
                cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
                cog_commands = [c for c in cog.__cog_commands__ if hasattr(c, 'parent') and c.parent is None]
                for c in cog_commands:
                    if not c.hidden:
                        cog_embed.add_field(name=c.qualified_name, value=c.help, inline=False)

                return await ctx.send(embed=cog_embed)
        # Otherwise, it's an invalid parameter (Not found)
        else:
            await ctx.send(f"**Invalid parameter! It is neither a command nor a cog!**")

@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def load(ctx, extension: str = None):
    """ Loads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} loaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def unload(ctx, extension: str = None):
    """ Unloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} unloaded!**", delete_after=3)


@client.command(hidden=True)
@commands.has_permissions(administrator=True)
async def reload(ctx, extension: str = None):
    """ Reloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} reloaded!**", delete_after=3)



# Slash commands


_cnp = client.command_group(name="cnp", description="For copy and pasting stuff.", guild_ids=guild_ids)

@_cnp.command(name="specific")
@utils.is_allowed([moderator_role_id, admin_role_id], throw_exc=True)
async def _specific(ctx, 
    text: Option(str, name="text", description="Pastes a text for specific purposes", required=True,
        choices=['Muted/Purge', 'Nickname', 'Classes', 'Interview', 'Resources', 'Global', 'Searching Teachers'])):
    """ Posts a specific test of your choice """
    
    
    member = ctx.author

    available_texts: Dict[str, str] = {}
    with open(f"./extra/random/json/special_texts.json", 'r', encoding="utf-8") as file:
        available_texts = json.loads(file.read())

    if not (selected_text := available_texts.get(text.lower())):
        return await ctx.respond(f"**Please, inform a supported language, {member.mention}!**\n{', '.join(available_texts)}")

    if selected_text['embed']:
        embed = discord.Embed(
            title=f"__{text.title()}__",
            description=selected_text['text'],
            color=member.color
        )
        if selected_text["image"]:
            embed.set_image(url=selected_text["image"])
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(selected_text['text'])


@_cnp.command(name="speak")
@utils.is_allowed([moderator_role_id, admin_role_id], throw_exc=True)
async def _speak(ctx, language: Option(str, name="language", description="The language they should speak.", required=True)) -> None:
    """ Pastes a 'speak in X language' text in different languages. """

    member = ctx.author

    available_languages: Dict[str, str] = {}
    with open(f"./extra/random/json/speak_in.json", 'r', encoding="utf-8") as file:
        available_languages = json.loads(file.read())

    if not (language_text := available_languages.get(language.lower())):
        return await ctx.respond(f"**Please, inform a supported language, {member.mention}!**\n{', '.join(available_languages)}")

    embed = discord.Embed(
        title=f"__{language.title()}__",
        description=language_text,
        color=member.color
    )
    await ctx.respond(embed=embed)

_giveaway = client.command_group(name="giveaway", description="For copy and pasting stuff.", guild_ids=guild_ids)


@utils.is_allowed([giveaway_manager_role_id, moderator_role_id, admin_role_id], throw_exc=True)
@_giveaway.command(name="start", guild_ids=guild_ids)
@option(type=str, name="prize", description="The prize of the giveaway.", required=True)
@option(type=str, name="title", description="The title for the giveaway.", required=False, default="Giveaway")
@option(type=str, name="description", description="The description of the giveaway.", required=False)
@option(type=int, name="winners", description="The amount of winners.", required=False, default=1)
@option(type=int, name="days", description="The days for the giveaway.", required=False)
@option(type=int, name="hours", description="The hours for the giveaway.", required=False)
@option(type=int, name="minutes", description="The minutes for the giveaway.", required=False)
@option(type=discord.Role, name="role", description="The role for role-only giveaways.", required=False)
@option(type=discord.Member, name="host", description="The person hosting the giveaway.", required=False)
async def _giveaway_start_slash(
    ctx, prize: str, title: str, description: str, winners: int,
     days: int, hours: int, minutes: int, role: discord.Role, host: discord.Member) -> None:
    """ Starts a giveaway. """

    winners = 1 if not winners else winners
    minutes = 0 if minutes is None else minutes
    hours = 0 if hours is None else hours
    days = 0 if days is None else days
    host = host if host else ctx.author

    await client.get_cog('Giveaways')._giveaway_start_callback(ctx=ctx,
        host=host, prize=prize, title=title, description=description, 
        winners=winners, days=days, hours=hours, minutes=minutes, role=role
    )

@utils.is_allowed([giveaway_manager_role_id, moderator_role_id, admin_role_id], throw_exc=True)
@_giveaway.command(name="reroll", guild_ids=guild_ids)
@option("message_id", str, description="The message ID of the giveaway to reroll.")
async def _giveaway_reroll_slash(ctx, message_id: str) -> None:
    """ Rerolls a giveaway. """

    try:
        message_id: int = int(message_id)
    except ValueError:
        await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
    else:
        await client.get_cog('Giveaways')._giveaway_reroll_callback(ctx=ctx, message_id=message_id)

@utils.is_allowed([giveaway_manager_role_id, moderator_role_id, admin_role_id], throw_exc=True)
@_giveaway.command(name="delete", guild_ids=guild_ids)
@option("message_id", str, description="The message ID of the giveaway to delete.")
async def _giveaway_delete_slash(ctx, message_id: str) -> None:
    """ Deletes a giveaway. """

    try:
        message_id: int = int(message_id)
    except ValueError:
        await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
    else:
        await client.get_cog('Giveaways')._giveaway_delete_callback(ctx=ctx, message_id=message_id)

@utils.is_allowed([giveaway_manager_role_id, moderator_role_id, admin_role_id], throw_exc=True)
@_giveaway.command(name="end", guild_ids=guild_ids)
@option("message_id", str, description="The message ID of the giveaway to end.")
async def _giveaway_end_slash(ctx, message_id: str) -> None:
    """ Ends a giveaway. """

    try:
        message_id: int = int(message_id)
    except ValueError:
        await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
    else:
        await client.get_cog('Giveaways')._giveaway_end_callback(ctx=ctx, message_id=message_id)

@utils.is_allowed([giveaway_manager_role_id, moderator_role_id, admin_role_id], throw_exc=True)
@_giveaway.command(name="list", guild_ids=guild_ids)
async def _giveaway_list_slash(ctx) -> None:
    """ Lists all giveaways. """

    await client.get_cog('Giveaways')._giveaway_list_callback(ctx=ctx)

# End of slash commands

forbidden_files: List[str] = [
    # 'createdynamicroom.py'
]

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename not in forbidden_files:
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('TOKEN'))
