import discord
from discord.app import Option, OptionChoice
from discord.utils import escape_mentions
from pytz import timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks, flags

from extra import utils, useful_variables
from typing import Dict, Optional
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

server_id = int(os.getenv('SERVER_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
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

    elif isinstance(error, flags._parser.ArgumentParsingError):
        await ctx.send("**Unrecognized arguments!**")

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
            commands = [f"{client.command_prefix}{c.name}" for c in cog.get_commands() if not c.hidden]
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
                for c in cog.get_commands():
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

@client.slash_command(name="embed", default_permission=False, guild_ids=guild_ids)
@commands.has_permissions(administrator=True)
async def _embed(ctx,
    description: Option(str, name="description", description="Description.", required=False),
    title: Option(str, name="title", description="Title.", required=False),
    timestamp: Option(bool, name="timestamp", description="If timestamp is gonna be shown.", required=False),
    url: Option(str, name="url", description="URL for the title.", required=False),
    thumbnail: Option(str, name="thumbnail", description="Thumbnail for the embed.", required=False),
    image: Option(str, name="image", description="Display image.", required=False),
    color: Option(str, name="color", description="The color for the embed.", required=False,
        choices=[
            OptionChoice(name="Blue", value="0011ff"), OptionChoice(name="Red", value="ff0000"),
            OptionChoice(name="Green", value="00ff67"), OptionChoice(name="Yellow", value="fcff00"),
            OptionChoice(name="Black", value="000000"), OptionChoice(name="White", value="ffffff"),
            OptionChoice(name="Orange", value="ff7100"), OptionChoice(name="Brown", value="522400"),
            OptionChoice(name="Purple", value="380058")])) -> None:
    """ (ADM) Makes an improved embedded message """

    # Checks if there's a timestamp and sorts time
    embed = discord.Embed()

    # Adds optional parameters, if informed
    if title: embed.title = title
    if timestamp: embed.timestamp = await utils.parse_time()
    if description: embed.description = description.replace(r'\n', '\n')
    if color: embed.color = int(color, 16)
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    if url: embed.url = url
    if image: embed.set_image(url=image)

    if not description and not image and not thumbnail:
        return await ctx.send(
            f"**{ctx.author.mention}, you must inform at least one of the following options: `description`, `image`, `thumbnail`**")

    await ctx.respond(embed=embed)




@client.slash_command(name="timestamp", guild_ids=guild_ids)
async def _timestamp(ctx, 
        hour: Option(int, name="hour", description="Hour of time in 24 hour format.", required=False),
        minute: Option(int, name="minute", description="Minute of time.", required=False),
        day: Option(int, name="day", description="Day of date.", required=False),
        month: Option(int, name="month", description="Month of date.", required=False),
        year: Option(int, name="year", description="Year of date.", required=False)) -> None:
    """ Gets a timestamp for a specific date and time. - Output will format according to your timezone. """

    current_date = await utils.get_time_now()

    if hour: current_date = current_date.replace(hour=hour)
    if minute: current_date = current_date.replace(minute=minute)
    if day: current_date = current_date.replace(day=day)
    if month: current_date = current_date.replace(month=month)
    if year: current_date = current_date.replace(year=year)

    embed = discord.Embed(
        title="__Timestamp Created__",
        description=f"Requested date: `{current_date.strftime('%m/%d/%Y %H:%M')}` (**GMT**)",
        color=ctx.author.color
    )
    timestamp = int(current_date.timestamp())
    embed.add_field(name="Output", value=f"<t:{timestamp}>")
    embed.add_field(name="Copyable", value=f"\<t:{timestamp}>")

    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(name="dnk", guild_ids=guild_ids)
async def _dnk(ctx) -> None:
    """ Tells you something about DNK. """
    await ctx.respond(f"**DNK est toujours là pour les vrais !**")

@client.slash_command(name="twiks", guild_ids=guild_ids)
async def _twiks(ctx) -> None:
    """ Tells you something about Twiks. """

    await ctx.respond(f"**Twiks est mon frérot !**")


@client.slash_command(name="mention", guild_ids=guild_ids)
@utils.is_allowed([moderator_role_id, admin_role_id])
async def _mention(ctx, 
    member: Option(str, name="member", description="The Staff member to mention/ping.", required=True,
		choices=[
			OptionChoice(name="Cosmos", value=os.getenv('COSMOS_ID')), OptionChoice(name="Alex", value=os.getenv('ALEX_ID')),
			OptionChoice(name="DNK", value=os.getenv('DNK_ID')), OptionChoice(name="Muffin", value=os.getenv('MUFFIN_ID')),
			OptionChoice(name="Prisca", value=os.getenv('PRISCA_ID')), OptionChoice(name="GuiBot", value=os.getenv('GUIBOT_ID'))
		]
	)) -> None:
    """ (ADMIN) Used to mention staff members. """

    if staff_member := discord.utils.get(ctx.guild.members, id=int(member)):
        await ctx.respond(staff_member.mention)
    else:
        await ctx.respond("**For some reason I couldn't ping them =\ **")



_cnp = client.command_group(name="cnp", description="For copy and pasting stuff.", guild_ids=guild_ids)

@_cnp.command(name="specific")
@utils.is_allowed([moderator_role_id, admin_role_id])
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
@utils.is_allowed([moderator_role_id, admin_role_id])
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

@client.slash_command(name="rules", guild_ids=guild_ids)
@utils.is_allowed([moderator_role_id, admin_role_id])
async def _rules_slash(ctx, 
    rule_number: Option(int, name="rule_number", description="The number of the rule you wanna show.", choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], required=False), 
    reply_message: Option(bool, name="reply_message", description="Weather the slash command should reply to your original message.", required=False, default=True)) -> None:
    """ (MOD) Sends an embedded message containing all rules in it, or a specific rule. """

    cog = client.get_cog('Show')
    if rule_number:
        await cog._rule(ctx, rule_number, reply_message)
    else:
        await cog._rules(ctx, reply_message)



@client.user_command(name="Click", guild_ids=guild_ids)
async def _click(ctx, user: discord.Member) -> None:
    await ctx.respond(f"**{ctx.author.mention} clicked on {user.mention}!**")

@client.user_command(name="Help", guild_ids=guild_ids)
async def _help(ctx, user: discord.Member) -> None:
    await ctx.respond(f"**{ctx.author.mention} needs your help, {user.mention}!**")

@client.slash_command(name="info", guild_ids=guild_ids)
@commands.cooldown(1, 5, commands.BucketType.user)
async def _info_slash(ctx, 
    member: Option(discord.Member, description="The member to show the info; [Default=Yours]", required=False)) -> None:
    """ Shows the user's level and experience points. """

    await ctx.defer()
    await client.get_cog('SlothReputation')._info(ctx, member)

@client.slash_command(name="profile", guild_ids=guild_ids)
@commands.cooldown(1, 5, commands.BucketType.user)
async def _profile_slash(ctx, member: Option(discord.Member, description="The member to show the info; [Default=Yours]", required=False)) -> None:
    """ Shows the member's profile with their custom sloth. """

    await ctx.defer()
    await client.get_cog('SlothCurrency')._profile(ctx, member)


@client.slash_command(name="youtube_together", guild_ids=guild_ids)
@utils.is_allowed([booster_role_id, *useful_variables.patreon_roles.keys(), moderator_role_id, admin_role_id, teacher_role_id], throw_exc=True)
async def youtube_together(ctx,
    voice_channel: Option(discord.abc.GuildChannel, description="The voice channel in which to create the party.")
) -> None:
    """ Creates a YouTube Together session in a VC. """

    member = ctx.author

    if not isinstance(voice_channel, discord.VoiceChannel):
        return await ctx.respond(f"**Please, select a `Voice Channel`, {member.mention}!**")

    link: str = ''
    try:
        link = await voice_channel.create_activity_invite(event='youtube', max_age=600)
    except Exception as e:
        print("Invite creation error: ", e)
        await ctx.respond(f"**For some reason I couldn't create it, {member.mention}!**")
    current_time = await utils.get_time_now()

    view = discord.ui.View()
    view.add_item(discord.ui.Button(url=str(link), label="Start/Join the Party!", emoji="🔴"))
    embed = discord.Embed(
        title="__Youtube Together__",
        color=discord.Color.red(),
        timestamp=current_time,
        url=link
    )
    embed.set_author(name=member, url=member.display_avatar, icon_url=member.display_avatar)
    embed.set_footer(text=f"(Expires in 5 minutes)", icon_url=ctx.guild.icon.url)
    await ctx.respond("\u200b", embed=embed, view=view)

@client.slash_command(name="poll", guild_ids=guild_ids)
@utils.is_allowed([moderator_role_id, admin_role_id], throw_exc=True)
async def _poll(ctx, 
    description: Option(str, description="The description of the poll."),
    title: Option(str, description="The title of the poll.", required=False, default="Poll"), 
    role: Option(discord.Role, description="The role to tag in the poll.", required=False)) -> None:
    """ Makes a poll.
    :param title: The title of the poll.
    :param description: The description of the poll. """

    await ctx.defer()

    member = ctx.author
    current_time = await utils.get_time_now()

    embed = discord.Embed(
        title=f"__{title}__",
        description=description,
        color=member.color,
        timestamp=current_time
    )

    if role:
        msg = await ctx.respond(content=role.mention, embed=embed)
    else:
        msg = await ctx.respond(embed=embed)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')


@client.message_command(name="Translate", guild_ids=guild_ids)
async def _tr_slash(ctx, message: discord.Message) -> None:
    """ Translates a message into another language. """

    await ctx.defer(ephemeral=True)
    language: str = 'en'    
    await client.get_cog('Tools')._tr_callback(ctx, language, message.content)

# End of slash commands

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('TOKEN'))
