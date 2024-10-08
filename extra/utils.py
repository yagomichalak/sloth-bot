# import.standard
import re
import shlex
from collections import OrderedDict
from datetime import datetime
from io import BytesIO
from typing import Dict, Iterable, List, Optional, Union

# import.thirdparty
import aiohttp
import discord
from discord.enums import EntitlementType
from discord.ext import commands
from PIL import Image, ImageDraw
from pytz import timezone

# import.local
from extra.customerrors import CommandNotReady, NotSubscribed
from extra import utils

session = aiohttp.ClientSession()

async def get_timestamp(tz: str = 'Etc/GMT') -> float:
    """ Gets the current timestamp.
    :param tz: The timezone to get the timstamp from. Default = Etc/GMT """

    tzone = timezone(tz)
    the_time = datetime.now(tzone)
    return the_time.timestamp()

async def get_time_now(tz: str = 'Etc/GMT') -> datetime:
    """ Gets the current timestamp.
    :param tz: The timezone to get the timstamp from. Default = Etc/GMT """

    tzone = timezone(tz)
    the_time = datetime.now(tzone)
    return the_time

async def parse_time(tz: str = 'Etc/GMT') -> str:
    """ Parses time from the current timestamp.
    :param tz: The timezone to get the timestamp from. Default = Etc/GMT """

    tzone = timezone(tz)
    return datetime(*map(int, re.split(r'[^\d]', str(datetime.now(tzone)).replace('+00:00', ''))))


def is_allowed(roles: List[int], check_adm: Optional[bool] = True, throw_exc: Optional[bool] = False) -> bool:
    """ Checks whether the member has adm perms or has an allowed role.
    :param roles: The roles to check if the user has.
    :param check_adm: Whether to check whether the user has adm perms or not. [Optional][Default=True]
    :param throw_exec: Whether to throw an exception if it returns false. [Optional][Default=False] """

    async def real_check(ctx: Optional[commands.Context] = None, channel: Optional[discord.TextChannel] = None, 
        member: Optional[discord.Member] = None) -> bool:

        member = member if not ctx else ctx.author
        channel = channel if not ctx else ctx.channel

        if check_adm:
            perms = channel.permissions_for(member)
            if perms.administrator:
                return True
                
        for rid in roles:
            if rid in [role.id for role in member.roles]:
                return True

        if throw_exc:
            raise commands.MissingAnyRole(roles)

    return commands.check(real_check)

def is_subscriber(check_adm: Optional[bool] = True, throw_exc: Optional[bool] = True) -> bool:
    """ Checks whether the member has adm perms or has an allowed role.
    :param check_adm: Whether to check whether the user has adm perms or not. [Optional][Default=True]
    :param throw_exec: Whether to throw an exception if it returns false. [Optional][Default=False] """

    async def real_check(ctx: Optional[commands.Context] = None, channel: Optional[discord.TextChannel] = None, 
        member: Optional[discord.Member] = None) -> bool:

        member = member if not ctx else ctx.author
        channel = channel if not ctx else ctx.channel

        if check_adm:
            perms = channel.permissions_for(member)
            if perms.administrator:
                return True

        current_date = await utils.get_time_now()
        entitlements = await member.entitlements().flatten()
        for entitlement in entitlements:

            # Checks whether it's a subscription entitlement
            if entitlement.type not in (EntitlementType.application_subscription, EntitlementType.purchase):
                continue
            
            # Checks if it's the Sloth's subscription
            if entitlement.application_id != ctx.bot.application_id:
                continue
            
            # Checks if the subscription is expired
            if entitlement.ends_at and entitlement.ends_at < current_date:
                continue

            return True

        if throw_exc:
            raise NotSubscribed()

    return commands.check(real_check)

def is_allowed_members(members: List[int], check_adm: Optional[bool] = True, throw_exc: Optional[bool] = False) -> bool:
    """ Checks whether the member is allowed to use a command or function.
    :param members: The list of members to check.
    :param check_adm: Whether to check whether the user has adm perms or not. [Optional][Default=True]
    :param throw_exec: Whether to throw an exception if it returns false. [Optional][Default=False] """
    
    async def real_check(ctx: Optional[commands.Context] = None, channel: Optional[discord.TextChannel] = None, 
        member: Optional[discord.Member] = None):

        member = member if not ctx else ctx.author
        channel = channel if not ctx else ctx.channel

        if check_adm:
            perms = channel.permissions_for(member)
            if perms.administrator:
                return True

        if member.id in members:
            return True

        if throw_exc:
            raise commands.MissingPermissions(missing_permissions=['administrator'])

    return commands.check(real_check)


async def get_time_from_text(ctx: commands.Context, time: List[str]) -> Dict[str, int]:
    """ Gets the mute time in seconds.
    :param ctx: The context.
    :param time: The given time. """
    
    keys = ['d', 'h', 'm', 's']
    for k in keys:
        if k in time:
            break
    else:
        await ctx.send(f"**Inform a valid time, {ctx.author.mention}**", delete_after=3)
        return False

    the_time_dict = {
        'days': 0,
        'hours': 0,
        'minutes': 0,
        'seconds': 0,
    }

    seconds = 0

    for t in time.split():

        if (just_time := t[:-1]).isdigit():
            just_time = int(t[:-1])

        if 'd' in t and not the_time_dict.get('days'):

            seconds += just_time * 86400
            the_time_dict['days'] = just_time
            continue
        elif 'h' in t and not the_time_dict.get('hours'):
            seconds += just_time * 3600
            the_time_dict['hours'] = just_time
            continue
        elif 'm' in t and not the_time_dict.get('minutes'):
            seconds += just_time * 60
            the_time_dict['minutes'] = just_time
            continue
        elif 's' in t and not the_time_dict.get('seconds'):
            seconds += just_time
            the_time_dict['seconds'] = just_time
            continue

    if seconds <= 0:
        await ctx.send(f"**Something is wrong with it, {ctx.author.mention}!**", delete_after=3)
        return False, False
    else:
        return the_time_dict, seconds


async def sort_time(at: datetime) -> str:

    timedelta = await get_time_now() - at.astimezone(timezone('Etc/GMT'))

    if type(timedelta) is not float:
        timedelta = timedelta.total_seconds()

    seconds = int(timedelta)

    periods = [
        ('year', 60*60*24*365, 'years'),
        ('months', 60*60*24*30, "months"),
        ('day', 60*60*24, "days"),
        ('hour', 60*60, "hours"),
        ('minute', 60, "minutes"),
        ('second', 1, "seconds")
    ]

    strings = []
    for period_name, period_seconds, plural in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value > 0:
                strings.append(
                    f"{period_value} {plural if period_value > 1 else period_name}"
                )
                
    return ", ".join(strings[:2])


async def get_mentions(message: discord.Message) -> List[discord.Member]:
    """ Get mentions from a specific message.
    :param message: The message to get the mentions from. """

    guild = message.guild

    members = [
        m for word in message.content.split()
        if word.isdigit() and (m := discord.utils.get(guild.members, id=int(word)))
        or (m := discord.utils.get(guild.members, name=str(word)))
        or (m := discord.utils.get(guild.members, nick=str(word)))
        or (m := discord.utils.get(guild.members, display_name=str(word)))
    ]
    members.extend(message.mentions)
    members = list(set(members))

    return members

async def get_roles(message: discord.Message) -> List[discord.Role]:
    """ Get role mentions from a specific message.
    :param message: The message to get the mentions from. """

    guild = message.guild

    roles: List[discord.Role] = [
        m for word in message.content.split()
        if word.isdigit() and (m := discord.utils.get(guild.roles, id=int(word)))
        or (m := discord.utils.get(guild.roles, name=str(word))
        # or (m := await commands.RoleConverter().convert(message, message.content))
        )
    ]
    for role_id in re.findall(r'<@&([0-9]{15,20})>$', message.content):
        if role := discord.utils.get(guild.roles, id=int(role_id)):
            roles.append(role)

    # print('ihi', list(message.role_mentions))
    # roles.extend(message.mentions)
    roles = list(set(roles))

    return roles

async def get_voice_channel_mentions(message: discord.Message) -> List[discord.VoiceChannel]:
    """ Get voice channel mentions from a specific message.
    :param message: The message to get the mentions from. """

    guild = message.guild

    channel_mentions = [
        m for word in message.content.split()
        if word.isdigit() and (m := discord.utils.get(guild.voice_channels, id=int(word)))
        or (m := discord.utils.get(guild.voice_channels, name=str(word)))
    ]

    channel_mentions.extend(list(map(lambda c: isinstance(c, discord.VoiceChannel), message.channel_mentions)))
    channel_mentions = list(set(channel_mentions))

    return channel_mentions

async def disable_buttons(view: discord.ui.View) -> None:
    """ Disables all buttons from a view.
    :param view: The view from which to disable the buttons. """

    for child in view.children:
        child.disabled = True

async def enable_buttons(view: discord.ui.View) -> None:
    """ Enables all buttons from a view.
    :param view: The view from which to enable the buttons. """

    for child in view.children:
        child.disabled = False

async def change_style_buttons(view: discord.ui.View, style: discord.ButtonStyle) -> None:
    """ Changes all button styles from a view.
    :param view: The view from which to change the button styles.
    :param style: The new button style. """

    for child in view.children:
        child.style = style

async def remove_emoji_buttons(view: discord.ui.View) -> None:
    """ Removes all button emojis from a view.
    :param view: The view from which to remove the buttons emojis. """

    for child in view.children:
        child.emoji = None

async def audio(client: commands.Bot, voice_channel: discord.VoiceChannel, member: discord.Member, audio_path: str) -> None:
    """ Plays an audio.
    :param client: The client.
    :param voice_channel: The voice channel in which to play the audio.
    :param member: A member to get guild context from.
    :param audio_path: The path of the audio to play. """

    # Resolves bot's channel state
    bot_state = member.guild.voice_client

    try:
        if bot_state and bot_state.channel and bot_state.channel != voice_channel:
            await bot_state.disconnect()
            await bot_state.move_to(voice_channel)
        elif not bot_state:
            voicechannel = discord.utils.get(member.guild.channels, id=voice_channel.id)
            vc = await voicechannel.connect()

        # await asyncio.sleep(2)
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=member.guild)
        try:
            voice_client.stop()
        except Exception as e:
            pass

        if voice_client and not voice_client.is_playing():
            audio_source = discord.FFmpegPCMAudio(audio_path)
            voice_client.play(audio_source)
        else:
            print('couldnt play it!')

    except Exception as e:
        print(e)
        return


def split_quotes(value):
    lex = shlex.shlex(value)
    lex.quotes = '"'
    lex.whitespace_split = True
    lex.commenters = ''
    return list(lex)

async def greedy_member_reason(ctx, message : str = None):
    """A converter that greedily member or users until it can't.
    The member search ends on the first member not found or when the string does not match a member identifier.
    Everything else is considered a reason."""

    users = []
    reason = None

    if not message:
        return users, reason

    message = split_quotes(message)

    for pos, word in enumerate(message):
        if '"' in word:
            word = word[1:-1]

        # Checks if it is an ID, a mention or name#discriminator
        if (len(word) >= 15 and len(word) <= 20 and word.isdigit()) or re.match(r'<@!?([0-9]{15,20})>$', word) or (len(word) > 5 and word[-5] == '#'):

            # Member search
            try:
                user = await commands.MemberConverter().convert(ctx, word)
                # Ignores member if found by username
                if user.name == word or user.nick == word:
                    del user

            except commands.errors.BadArgument:
                user = None
            # User search (if cannot found a member)
            if not user:
                try:
                    user = await commands.UserConverter().convert(ctx, word)
                    # Ignores member if found by username
                    if user.name == word:
                        del user

                except commands.errors.BadArgument:
                    user = None

            if not user:
                reason = ' '.join(message[pos:])
                return list(OrderedDict.fromkeys(users)), reason

            users.append(user)

        # When does not find a string in the member format
        else:
            reason = ' '.join(message[pos:])
            return list(OrderedDict.fromkeys(users)), reason

    return list(OrderedDict.fromkeys(users)), reason


def not_ready():
    """ Makes a command not be usable. """

    async def real_check(ctx):
        """ Performs the real check. """
        raise CommandNotReady()

    return commands.check(real_check)

async def get_user_pfp(member, thumb_width: int = 59) -> Image:
    """ Gets the user's profile picture.
    :param member: The member from whom to get the profile picture.
    :param thumb_width: The width of the thumbnail. [Default = 59] """

    async with session.get(str(member.display_avatar)) as response:
        image_bytes = await response.content.read()
        with BytesIO(image_bytes) as pfp:
            image = Image.open(pfp)
            im = image.convert('RGBA')

    def crop_center(pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                                (img_height - crop_height) // 2,
                                (img_width + crop_width) // 2,
                                (img_height + crop_height) // 2))

    def crop_max_square(pil_img):
        return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def mask_circle_transparent(pil_img, blur_radius, offset=0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

        result = pil_img.copy()
        result.putalpha(mask)

        return result

    im_square = crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
    im_thumb = mask_circle_transparent(im_square, 4)
    return im_thumb

async def get_member_public_flags(member: discord.Member) -> List[str]:
    """ Gets the member's public flags.
    :param member: The member to get the flags from. """

    public_flags = member.public_flags.all()
    public_flag_names = list(map(lambda pf: pf.name, public_flags))
    return public_flag_names

async def count_members(guild: discord.Guild, roles: Iterable[Union[discord.Role, int]]) -> int:
    """ Counts the members in one or more roles.
    :para"""

    member_ids = set()
    for role in roles:
        if isinstance(role, int):
            role = guild.get_role(role)
        if not role:
            continue
        member_ids.update([m.id for m in role.members])
    return len(member_ids)
