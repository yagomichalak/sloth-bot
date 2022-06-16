from __future__ import annotations
import discord
from discord.ext import commands

from extra import utils
import os
from typing import Dict, Union
from datetime import datetime

bots_and_commands_channel_id: int = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))
server_id: int = int(os.getenv('SERVER_ID', 123))

async def quest_one_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest one.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    await money_callback(client, user_id, 'One', 230, quest)

async def quest_two_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest two.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    money = 100

    # Checks whether the int content reached its expected mark, else increments it
    if quest[9] < 2:
         await cog.update_sloth_skill_int_content(member.id, quest[9]+1, current_time.timestamp(), 'quest')
         if quest[9] + 1 < 2:
             return

    await update_tribe_members_money(client, member, 'Two', money, current_time, quest)

async def quest_three_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest_three.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    await money_callback(client, user_id, 'Three', 250, quest)

async def quest_four_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest four.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    await money_callback(client, user_id, 'Four', 100, quest)

async def quest_five_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest five.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    money = 100

    # Checks whether the int content reached its expected mark, else increments it
    quest = await cog.get_skill_action_by_user_id_and_skill_type(user_id=user_id, skill_type="quest")
    if not quest:
        return

    required_time: int = 3600 * 4
    increment: int = kwargs["increment"]
    seconds = quest[9]

    current_seconds: int = int(seconds + increment)
    if current_seconds + increment < required_time:
        return await cog.update_sloth_skill_int_content(member.id, current_seconds, current_time.timestamp(), 'quest')

    await update_tribe_members_money(client, member, 'Five', money, current_time, quest)

async def quest_six_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest six.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    await money_callback(client, user_id, 'Six', 100, quest)

async def quest_seven_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest six.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    staff_id: int = kwargs.get("staff_id")
    money = 150

    # Checks whether the int content reached its expected mark, else increments it
    if old_staff_id := quest[9]:
        if old_staff_id == staff_id:
            return
    else:
        return await cog.update_sloth_skill_int_content(member.id, staff_id, current_time.timestamp(), 'quest')

    await money_callback(client, user_id, 'Seven', money, quest)

async def quest_ten_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest ten.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    teacher_id: int = kwargs.get("teacher_id")
    money = 150

    # Checks whether the int content reached its expected mark, else increments it
    if old_teacher_id := quest[9]:
        if old_teacher_id == teacher_id:
            return
    else:
        return await cog.update_sloth_skill_int_content(member.id, teacher_id, current_time.timestamp(), 'quest')

    await money_callback(client, user_id, 'Ten', money, quest)

async def quest_twelve_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest four.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    await money_callback(client, user_id, 'Twelve', 50, quest)

async def quest_thirteen_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest thirteen.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    money = 100

    # Checks whether the int content reached its expected mark, else increments it
    if quest[9] < 3:
         await cog.update_sloth_skill_int_content(member.id, quest[9]+1, current_time.timestamp(), 'quest')

    if quest[9] + 1 < 3:
        return

    await update_tribe_members_money(client, member, 'Thirteen', money, current_time, quest)

async def quest_fourteen_callback(client: commands.Bot, user_id: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Callback for the quest fourteen.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest: The quest information and data.
    :param kwargs: Additional data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)
    cog = client.get_cog('SlothClass')
    command_name = kwargs.get("command_name")
    money = 75

    # Checks whether the int content reached its expected mark, else increments it
    if not quest[8]:
         await cog.update_sloth_skill_content(member.id, command_name, current_time.timestamp(), 'quest')

    if quest[8] == command_name:
        return

    await update_tribe_members_money(client, member, 'Fourteen', money, current_time, quest)

# Default callbacks
async def money_callback(client: commands.Cog, user_id: int, quest_name: str, money: int, quest: Dict[str, Union[str, int]], **kwargs) -> None:
    """ Default callback for Quests which the reward is just money for the entire tribe.
    :param client: The bot client.
    :param user_id: The user ID.
    :param quest_name: The quest name. E.g: Six
    :param money: The amount of money to give.
    :param quest: The quest information and data. """

    # Gets general info
    current_time = await utils.get_time_now()
    guild = client.get_guild(server_id)
    member = guild.get_member(user_id)

    await update_tribe_members_money(client, member, quest_name, money, current_time, quest)

async def update_tribe_members_money(
    client: commands.Cog, member: discord.Member, quest_name: str, 
    money: int, current_time: datetime, quest: Dict[str, Union[str, int]]
) -> None:
    """ Second step of callbacks that reward tribe members with money.
    :param client: The bot client.
    :param member: The member.
    :param quest_name: The quest name. E.g: Six
    :param money: The amount of money to give.
    :param current_time: The current time.
    :param quest: The quest information and data. """

    cog = client.get_cog('SlothClass')
    # Gets user profile
    sloth_profile = await cog.get_sloth_profile(member.id)
    if not sloth_profile:
        return

    # Gets user tribe
    tribe = await cog.get_tribe_info_by_name(sloth_profile[3])
    if not tribe:
        return
    
    tribe_members = await cog.get_tribe_members(tribe_name=tribe['name'])
    all_users = list(map(lambda mid: (money, mid[0]), tribe_members))

    await client.get_cog('SlothCurrency').update_user_many_money(all_users)
    bots_and_commands_channel = member.guild.get_channel(bots_and_commands_channel_id)

    # Makes embed
    embed = discord.Embed(
        title=f"__Quest {quest_name} Complete__",
        description=f"{member.mention} and all members of his tribe named `{tribe['name']}` got `{money}`łł" \
            f" for completing the `Quest {quest_name}`! 🍃🍃",
        color=discord.Color.green(),
        timestamp=current_time
    )
    embed.add_field(name="__Quest Description:__", value=f"```{quest[8]}```")
    embed.set_author(name=f"Tribe: {tribe['name']}", url=tribe["link"])
    if tribe_tn := tribe.get('thumbnail'):
        embed.set_thumbnail(url=tribe_tn)
    embed.set_footer(text=f"Completed by: {member}", icon_url=member.display_avatar)

    await bots_and_commands_channel.send(content=member.mention, embed=embed)

    # Deletes Quest
    await cog.delete_skill_action_by_user_id_and_skill_type(user_id=member.id, skill_type='quest')

    locked_users = [(tm[0], 'lock') for tm in tribe_members]
    await cog.delete_skill_actions_by_target_id_and_skill_type(locked_users)