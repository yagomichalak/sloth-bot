from datetime import datetime
import re
from pytz import timezone
from discord.ext import commands
from typing import List, Dict
import discord

async def get_timestamp(tz: str = 'Etc/GMT') -> int:
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
    :param tz: The timezone to get the timstamp from. Default = Etc/GMT """

    tzone = timezone(tz)
    return datetime(*map(int, re.split(r'[^\d]', str(datetime.now(tzone)).replace('+00:00', ''))))


def is_allowed(roles: List[int]) -> bool:
    """ Checks whether the member has adm perms or has an allowed role. """

    async def real_check(ctx: commands.Context):
        perms = ctx.channel.permissions_for(ctx.author)
        if perms.administrator:
            return True

        for rid in roles:
            if rid in [role.id for role in ctx.author.roles]:
                return True

        else:
            return False
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

async def disable_buttons(view: discord.ui.View) -> None:
    """ Disables all buttons from a view.
    :param view: The view from which to disable the buttons. """

    for child in view.children:
        child.disabled = True
