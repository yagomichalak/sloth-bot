import discord
from discord.ext import commands, tasks
from mysqldb import *
from datetime import datetime
import os
import pytz
from pytz import timezone

# IDs
user_cosmos_id = 423829836537135108
server_id = 459195345419763713
moderator_role_id = 497522510212890655
teacher_role_id = 507298235766013981
moderation_log_channel_id = 675745413760024595
lesson_log_channel_id = 679043911225966608
lesson_category_id = 562019326295670806
clock_voice_channel_id = 687783432222277695
announcement_channel_id = 689918515129352213
report_channel_id = 685832739517366340
report_log_channel_id = 683693966016774168
admin_commands_channel_id = 562019472257318943


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


# Reading the bot's token
token = read_token()

# Making the client variable
client = commands.Bot(command_prefix='z!')


# Tells when the bot is online
@client.event
async def on_ready():
    change_status.start()
    update_timezones.start()
    print('Bot is ready!')


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
    cosmos = discord.utils.get(member.guild.members, id=user_cosmos_id)
    await channel.send(content=f"{cosmos.mention}", embed=embed)


@client.event
async def on_message(message):
    if not message.author.bot:

        if 'Direct Message' not in str(message.channel):
            if message.channel.id == report_channel_id:
                await message.delete()
                cid = report_log_channel_id  # Report log's channel id
                moderators = discord.utils.get(message.author.guild.roles, id=moderator_role_id)
                cosmos = discord.utils.get(message.author.guild.members, id=user_cosmos_id)
                the_channel = discord.utils.get(message.author.guild.channels, id=cid)
                report = message.content

                # Report embed
                embed_report = discord.Embed(description=f"**Report sent by:** {message.author.mention}\n{report}", colour=discord.Colour.green(),
                                             timestamp=message.created_at)
                #embed_report.set_author(name=message.author,icon_url=message.author.avatar_url)
                embed_report.set_thumbnail(url=message.author.avatar_url)
                #embed_report.set_footer(icon_url=message.author.avatar_url)

                await the_channel.send(f'{moderators.mention}, {cosmos.mention}')
                await the_channel.send(embed=embed_report)

    await client.process_commands(message)


# Delete messages log
@client.event
async def on_raw_message_delete(payload):
    if payload.channel_id == announcement_channel_id:
        announcements = await show_class_announcements()
        for ann in announcements:
            if payload.message_id == ann[1]:
                return await remove_announcement(payload.message_id)


def read_native(branch, type, language):
    with open(f'texts/{branch}/{type}/{language}.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
        text = ''.join(text)
        return text


@client.event
async def on_raw_reaction_add(overload):
    guild = client.get_guild(overload.guild_id)
    user = discord.utils.get(guild.members, id=overload.user_id)

    if user.bot:
        return

    # User reaction info
    user_emoji = overload.emoji
    rid = overload.message_id

    # Create room message id
    info = []

    # Language rooms
    x = 695491104417513552
    y = 683987207065042944
    z = 688037387561205824

    languages = {
        'germanic': [{'native': 695616470234824845, 'fluent': 688070989757808653, 'studying': 688532522052878349},
                     {'🇬🇧': 'english', '🇩🇪': 'german', '🇩🇰': 'danish', '🇳🇱': 'dutch', '🇳🇴': 'norwegian',
                      '🇸🇪': 'swedish', '🇮🇸': 'icelandic', '🇿🇦': 'afrikaans', '🇫🇴': 'faroese',
                      '🇱🇺': 'luxembourgish'}],
        'uralic': [{'native': 695616528472866828, 'fluent': 688071024356360372, 'studying': 688532812797706255},
                   {'🇫🇮': 'finnish', '🇭🇺': 'hungarian', '🇪🇪': 'estonian',
                    '<:flag_smi:490116718241513472> ': 'sámi'}],
        'celtic': [{'native': 695616551692402699, 'studying': 688532738810183692}, {'🇮🇪': 'celtic'}],
        'romance': [{'native': 695616564480966706, 'fluent': 688071741448519708, 'studying': 688532923401371649},
                    {'🇫🇷': 'french', '🇪🇸': 'spanish', '🇵🇹': 'portuguese_pt', '🇧🇷': 'portuguese_br',
                     '🇮🇹': 'italian', '🇷🇴': 'romanian',
                     '<:flag_cat:635441691419082773>': 'catalan', '<:flag_gal:490116682417963008> ': 'galician',
                     '<:flag_rm:490116699190722570>': 'latin'}],
        'baltic': [{'native': 695616630998302742, 'fluent': 688072044243714095, 'studying': 688532873312993340},
                   {'🇱🇹': 'lithuanian', '🇱🇻': 'latvian'}],
        'slavic': [{'native': 695616645036507217, 'fluent': 688072145687019524, 'studying': 688532945245307068},
                   {'🇷🇺': 'russian', '🇺🇦': 'ukrainian', '🇵🇱': 'polish', '🇧🇾': 'belarusian', '🇨🇿': 'czech',
                    '🇸🇰': 'slovak', '🇧🇦': 'bosnian', '🇷🇸': 'serbian', '🇸🇮': 'slovenian', '🇭🇷': 'croatian',
                    '🇲🇰': 'macedonian', '🇧🇬': 'bulgarian'}],
        'semitic': [{'native': 695616659255459880, 'fluent': 688072184811618432, 'studying': 688533046894395424},
                    {'🇸🇦': 'arabic', '🇮🇱': 'hebrew', '🇪🇹': 'amharic'}],
        'turkic': [{'native': 695616682768465962, 'fluent': 688072219053785093, 'studying': 688533085306093754},
                   {'🇹🇷': 'turkish', '🇰🇿': 'kazakh', '🇦🇿': 'azerbaijani'}],
        'iranian': [{'native': 695616726397616140, 'fluent': 688073486459207745, 'studying': 123456789},
                    {'🇦🇫': 'pashto', '<:flag_kd:490181096873525258>': 'kurdish', '🇮🇷': 'persian'}],
        'asian': [{'native': 695616743879475200, 'fluent': 688073546835951700, 'studying': 688533171112902663},
                  {'🇯🇵': 'japanese', '🇨🇳': 'chinese', '🇰🇷': 'korean', '🇻🇳': 'vietnamese', '🇹🇭': 'thai',
                   '🇱🇰': 'sinhalese', '🇵🇭': 'tagalog', '🇮🇩': 'indonesian', '🇲🇾': 'malay', '🇲🇳': 'mongolian',
                   '🇭🇰': 'cantonese'}],
        'indian': [{'native': 695616775286554681, 'fluent': 688073575298629788, 'studying': 688533187315499127},
                   {'🇮🇳': 'hindustani'}],
        'unafiliated': [{'native': 695616885080981564, 'fluent': 688073619515113485, 'studying': 688533247986106373},
                        {'🇬🇷': 'greek', '<:flag_bas:490116649467379712>': 'basque', '🇦🇲': 'armenian',
                         '🇦🇱': 'albanian'}],
        'constructed': [{'studying': 688533271021486091},
                        {'<:flag1:490116752567697410>': 'esperanto', '🤖': 'programming'}]
    }

    # Class announcement
    if overload.channel_id == announcement_channel_id:
        announcements = await show_class_announcements()
        for announcement in announcements:
            if overload.message_id == announcement[1]:
                if str(overload.emoji) == '✅':
                    channel = discord.utils.get(guild.channels, id=announcement_channel_id)
                    teacher = discord.utils.get(guild.members, id=announcement[0])
                    msg = await channel.fetch_message(announcement[1])
                    reactions = msg.reactions
                    participants = []
                    for react in reactions:
                        if react.emoji == '✅':
                            async for userr in react.users():
                                if not userr.bot:
                                    participants.append(f'{userr}')
                    attendees = ', '.join(participants)
                    await msg.edit(content=f"```-> {attendees}```")
                    await teacher.send(f'**{user}** is coming to your class!')
        return

    if overload.channel_id == x or overload.channel_id == y or overload.channel_id == z:
        for branch in languages:
            # Get the language equivalent to the reacted emoji
            language_emojis = languages[branch][1]
            for le in language_emojis:
                if str(user_emoji) == str(le):
                    info.append(branch)
                    info.append(language_emojis[le])
                    break
            if len(info) == 2:
                break

        # Get the type of the language
        language_types = languages[info[0]][0]
        for lt in language_types:
            if rid == int(language_types[lt]):
                info.append(lt)
                break

        if info[2] == 'native':
            text = read_native(info[0], info[2], info[1])
            embed = discord.Embed(title='', description=text, colour=discord.Colour.dark_green())
            embed.set_footer(text=f"Guild name: {guild.name}")
            embed.set_author(name=user, icon_url=user.avatar_url)
            return await user.send(embed=embed)


@client.event
async def on_raw_reaction_remove(overload):
    guild = client.get_guild(overload.guild_id)
    user = discord.utils.get(guild.members, id=overload.user_id)

    # User reaction info
    user_emoji = overload.emoji
    rid = overload.message_id
    info = []

    # Language rooms
    x = 695491104417513552
    y = 683987207065042944
    z = 688037387561205824

    languages = {
        'germanic': [{'native': 695616470234824845, 'fluent': 688070989757808653, 'studying': 688532522052878349},
                     {'🇬🇧': 'english', '🇩🇪': 'german', '🇩🇰': 'danish', '🇳🇱': 'dutch', '🇳🇴': 'norwegian',
                      '🇸🇪': 'swedish', '🇮🇸': 'icelandic', '🇿🇦': 'afrikaans', '🇫🇴': 'faroese',
                      '🇱🇺': 'luxembourgish'}],
        'uralic': [{'native': 695616528472866828, 'fluent': 688071024356360372, 'studying': 688532812797706255},
                   {'🇫🇮': 'finnish', '🇭🇺': 'hungarian', '🇪🇪': 'estonian',
                    '<:flag_smi:490116718241513472> ': 'sámi'}],
        'celtic': [{'native': 695616551692402699, 'studying': 688532738810183692}, {'🇮🇪': 'celtic'}],
        'romance': [{'native': 695616564480966706, 'fluent': 688071741448519708, 'studying': 688532923401371649},
                    {'🇫🇷': 'french', '🇪🇸': 'spanish', '🇵🇹': 'portuguese_pt', '🇧🇷': 'portuguese_br',
                     '🇮🇹': 'italian', '🇷🇴': 'romanian',
                     '<:flag_cat:635441691419082773>': 'catalan', '<:flag_gal:490116682417963008> ': 'galician',
                     '<:flag_rm:490116699190722570>': 'latin'}],
        'baltic': [{'native': 695616630998302742, 'fluent': 688072044243714095, 'studying': 688532873312993340},
                   {'🇱🇹': 'lithuanian', '🇱🇻': 'latvian'}],
        'slavic': [{'native': 695616645036507217, 'fluent': 688072145687019524, 'studying': 688532945245307068},
                   {'🇷🇺': 'russian', '🇺🇦': 'ukrainian', '🇵🇱': 'polish', '🇧🇾': 'belarusian', '🇨🇿': 'czech',
                    '🇸🇰': 'slovak', '🇧🇦': 'bosnian', '🇷🇸': 'serbian', '🇸🇮': 'slovenian', '🇭🇷': 'croatian',
                    '🇲🇰': 'macedonian', '🇧🇬': 'bulgarian'}],
        'semitic': [{'native': 695616659255459880, 'fluent': 688072184811618432, 'studying': 688533046894395424},
                    {'🇸🇦': 'arabic', '🇮🇱': 'hebrew', '🇪🇹': 'amharic'}],
        'turkic': [{'native': 695616682768465962, 'fluent': 688072219053785093, 'studying': 688533085306093754},
                   {'🇹🇷': 'turkish', '🇰🇿': 'kazakh', '🇦🇿': 'azerbaijani'}],
        'iranian': [{'native': 695616726397616140, 'fluent': 688073486459207745, 'studying': 123456789},
                    {'🇦🇫': 'pashto', '<:flag_kd:490181096873525258>': 'kurdish', '🇮🇷': 'persian'}],
        'asian': [{'native': 695616743879475200, 'fluent': 688073546835951700, 'studying': 688533171112902663},
                  {'🇯🇵': 'japanese', '🇨🇳': 'chinese', '🇰🇷': 'korean', '🇻🇳': 'vietnamese', '🇹🇭': 'thai',
                   '🇱🇰': 'sinhalese', '🇵🇭': 'tagalog', '🇮🇩': 'indonesian', '🇲🇾': 'malay', '🇲🇳': 'mongolian',
                   '🇭🇰': 'cantonese'}],
        'indian': [{'native': 695616775286554681, 'fluent': 688073575298629788, 'studying': 688533187315499127},
                   {'🇮🇳': 'hindustani'}],
        'unafiliated': [{'native': 695616885080981564, 'fluent': 688073619515113485, 'studying': 688533247986106373},
                        {'🇬🇷': 'greek', '<:flag_bas:490116649467379712>': 'basque', '🇦🇲': 'armenian',
                         '🇦🇱': 'albanian'}],
        'constructed': [{'studying': 688533271021486091},
                        {'<:flag1:490116752567697410>': 'esperanto', '🤖': 'programming'}]
    }

    if overload.channel_id == announcement_channel_id:
        announcements = await show_class_announcements()
        for announcement in announcements:
            if overload.message_id == announcement[1]:
                if str(overload.emoji) == '✅':
                    channel = discord.utils.get(guild.channels, id=announcement_channel_id)
                    teacher = discord.utils.get(guild.members, id=announcement[0])
                    msg = await channel.fetch_message(announcement[1])
                    reactions = msg.reactions
                    participants = []
                    for react in reactions:
                        if react.emoji == '✅':
                            async for userr in react.users():
                                if not userr.bot:
                                    participants.append(f'{userr}')

                    attendees = ', '.join(participants)
                    await msg.edit(content=f"```-> {attendees}```")
                    await teacher.send(f'**{user}** is not coming to your class anymore!')
        return

    if overload.channel_id == x or overload.channel_id == y or overload.channel_id == z:
        for branch in languages:

            # Get the language equivalent to the reacted emoji
            language_emojis = languages[branch][1]
            for le in language_emojis:
                if str(user_emoji) == str(le):
                    info.append(branch)
                    info.append(language_emojis[le])
                    break
            if len(info) == 2:
                break

        # Get the type of the language
        language_types = languages[info[0]][0]
        for lt in language_types:
            if rid == language_types[lt]:
                info.append(lt)
                break


# Handles the errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do that!")

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please, inform all parameters!')

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(error)


# Members status update
@tasks.loop(seconds=10)
async def change_status():
    guild = client.get_guild(server_id)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(guild.members)} members.'))

@tasks.loop(seconds=60)
async def update_timezones():
    gid = server_id  # Guild id
    guild = client.get_guild(gid)
    time_now = datetime.now()
    timezones = {'Etc/GMT-2': [clock_voice_channel_id, 'CET']}

    for tz in timezones:
        tzone = timezone(tz)
        date_and_time = time_now.astimezone(tzone)
        date_and_time_in_text = date_and_time.strftime('%H:%M')
        the_vc = discord.utils.get(guild.channels, id=timezones[tz][0])
        await the_vc.edit(name=f'{timezones[tz][1]} - {date_and_time_in_text}')


# Joins VC log
@client.event
async def on_voice_state_update(member, before, after):
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


@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} loaded!**", delete_after=3)


@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} unloaded!**", delete_after=3)


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} reloaded!**", delete_after=3)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)
