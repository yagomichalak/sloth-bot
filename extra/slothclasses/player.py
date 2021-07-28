import discord
from discord.ext import commands
from discord.ext.commands.core import cooldown

from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, SkillsUsedRequirement
from extra import utils

from mysqldb import the_database, the_django_database
from typing import Union, List, Dict, Any
from datetime import datetime
import os
from pytz import timezone

from enum import Enum

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Skill(Enum):

    ONE = 'skill_one_ts'
    TWO = 'skill_two_ts'
    THREE = 'skill_three_ts'
    FOUR = 'skill_four_ts'
    FIVE = 'skill_five_ts'


class Player(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)

    # Check user class
    def user_is_class(command_class):
        """ Checks whether the user has the required Sloth Class to run the command.
        :param command_class: The Sloth Class required to run that command. """

        async def get_user_sloth_class(user_id: int) -> Union[str, bool]:
            """ Gets the user Sloth Class from the database.
            :param user_id: The ID of the user to get the Sloth Class. """

            mycursor, db = await the_database()
            await mycursor.execute("SELECT sloth_class FROM SlothProfile WHERE user_id = %s", (user_id,))
            user_sloth_class = await mycursor.fetchone()
            await mycursor.close()
            if user_sloth_class:
                return user_sloth_class[0]
            else:
                return None

        async def real_check(ctx):
            """ Perfoms the real check. """

            user_sloth_class = await get_user_sloth_class(ctx.author.id)
            if user_sloth_class and user_sloth_class.lower() == command_class:
                return True
            raise MissingRequiredSlothClass(
                required_class=command_class, error_message="You don't have the required Sloth Class to run this command!")
        return commands.check(real_check)

    def skill_on_cooldown(skill: Enum = Skill.ONE, seconds: int = 86400):
        """ Checks whether the user's action skill is on cooldown. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            skill_ts, exists = await Player.get_user_action_skill_ts(Player, user_id=ctx.author.id, skill_field=skill.value)
            if not skill_ts:
                return True, exists

            current_time = await utils.get_timestamp()
            cooldown_in_seconds = current_time - skill_ts
            if cooldown_in_seconds >= seconds:
                return True, exists

            raise ActionSkillOnCooldown(
                try_after=cooldown_in_seconds, error_message="Action skill on cooldown!", skill_ts=skill_ts, cooldown=seconds)

        return commands.check(real_check)

    def skill_mark():
        """ Makes a command be considered a skill command. """

        async def real_check(ctx):
            """ Performs the real check. """
            return True
        return commands.check(real_check)

    def not_ready():
        """ Makes a command not be usable. """

        async def real_check(ctx):
            """ Performs the real check. """
            raise CommandNotReady()

        return commands.check(real_check)

    def skills_used(requirement: int):
        """ Checks whether the user's action skill is on cooldown. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            sloth_profile = await Player.get_sloth_profile(Player, user_id=ctx.author.id)

            if sloth_profile[2] >= requirement:
                return True

            raise SkillsUsedRequirement(
                error_message=f"You must have `{requirement}` skills used in order to use this skill, {ctx.author.mention}!", skills_required=requirement)

        return commands.check(real_check)

    async def has_effect(self, effects: Dict[str, Dict[str, Any]], effect: str) -> Union[str, bool]:
        if effect in effects:
            return effects[effect]['cooldown']

        return False

    # Is user EFFECT

    async def get_user_effects(self, member: Union[discord.User, discord.Member]) -> List[str]:
        """ Gets the effects that the user is under. """

        # effects = []

        effects = {}
        general_cooldown = 86400 # Worth a day in seconds
        


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='divine_protection'):
            effects['protected'] = {}
    
            effects['protected']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['protected']['frames'] = []
            effects['protected']['cords'] = (0, 0)
            effects['protected']['resize'] = None
            effects['protected']['has_gif'] = True
            effects['protected']['debuff'] = False


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='transmutation'):
            effects['transmutated'] = {}
            effects['transmutated']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['transmutated']['frames'] = []
            effects['transmutated']['cords'] = (0, 0)
            effects['transmutated']['resize'] = None
            effects['transmutated']['has_gif'] = True
            effects['transmutated']['debuff'] = False


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='hack'):
            effects['hacked'] = {}
            effects['hacked']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['hacked']['frames'] = []
            effects['hacked']['cords'] = (0, 0)
            effects['hacked']['resize'] = None
            effects['hacked']['debuff'] = True


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='wire'):
            effects['wired'] = {}
            effects['wired']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['wired']['frames'] = []
            effects['wired']['cords'] = (0, 0)
            effects['wired']['resize'] = None
            effects['wired']['debuff'] = True


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='hit'):
            effects['knocked_out'] = {}
            effects['knocked_out']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['knocked_out']['frames'] = []
            effects['knocked_out']['cords'] = (0, 0)
            effects['knocked_out']['resize'] = None
            effects['knocked_out']['debuff'] = True


        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='frog'):
            effects['frogged'] = {}
            effects['frogged']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['frogged']['frames'] = []
            effects['frogged']['cords'] = (0, 0)
            effects['frogged']['resize'] = None
            effects['frogged']['debuff'] = True

        if 'Munk' in member.display_name:
            effects['munk'] = {}
            effects['munk']['cooldown'] = "Endless"
            effects['munk']['frames'] = []
            effects['munk']['cords'] = (0, 0)
            effects['munk']['resize'] = None
            effects['munk']['debuff'] = True

        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='reflect'):
            effects['reflect'] = {}
            effects['reflect']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['reflect']['frames'] = []
            effects['reflect']['cords'] = (0, 0)
            effects['reflect']['resize'] = None
            effects['reflect']['debuff'] = False

        return effects

    async def insert_skill_action(self, user_id: int, skill_type: str, skill_timestamp: int, target_id: int = None, message_id: int = None, channel_id: int = None, emoji: str = None, price: int = 0, content: str = None) -> None:
        """ Inserts a skill action into the database, if needed.
        :param user_id: The ID of the perpetrator of the skill action.
        :param skill_type: The type of the skill action.
        :param skill_timestamp: The timestamp of the skill action.
        :param target_id: The ID of the target member of the skill action.
        :param message_id: The ID of the message related to the action, if there's any.
        :param price: The price of the item or something, if it is for sale.
        :param content: The content of the skill, if any. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO SlothSkills (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price, content))
        await db.commit()
        await mycursor.close()

    # ========== GET ========== #

    async def get_skill_action_by_message_id(self, message_id: int) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by message ID.
        :param message_id: The ID with which to get the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s", (message_id,))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_skill_action_by_skill_type(self, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by skill type.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = %s", (skill_type,))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_skill_actions_by_skill_type(self, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets skill actions by skill type.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = %s", (skill_type,))
        skill_action = await mycursor.fetchall()
        await mycursor.close()
        return skill_action

    async def get_skill_action_by_message_id_and_skill_type(self, message_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by message ID and skill type.
        :param message_id: The ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s AND skill_type = %s", (message_id, skill_type))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by target ID and skill type.
        :param target_id: The target ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE target_id = %s and skill_type = %s", (target_id, skill_type))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_skill_action_by_user_id_and_skill_type(self, user_id: int, skill_type: str, multiple: bool = False
    ) -> Union[List[List[Union[int, str]]], List[Union[int, str]], bool]:
        """ Gets a skill action by user ID and skill type.
        :param user_id: The user ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE user_id = %s and skill_type = %s", (user_id, skill_type))
        if multiple:
            skill_actions = await mycursor.fetchall()
        else:
            skill_actions = await mycursor.fetchone()
        await mycursor.close()
        return skill_actions

    async def get_skill_action_by_reaction_context(self, message_id: int, target_id: int) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by reaction context.
        :param message_id: The ID of the message of the skill action.
        :param target_id: The ID of the target member of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s AND target_id = %s", (message_id, target_id))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_user_action_skill_ts(self, user_id: int, skill_field: str) -> List[Union[str, bool]]:
        """ Gets the user's last action skill timestamp from the database.
        :param user_id: The ID of the user to get the action skill timestamp.
        :param skill_field: The skill field to check. """

        mycursor, db = await the_database()
        sql = "SELECT " + skill_field + " FROM SkillsCooldown WHERE user_id = %s"
        await mycursor.execute(sql, (user_id,))

        skill_ts = await mycursor.fetchone()
        await mycursor.close()
        if skill_ts:
            return skill_ts[0], True
        else:
            return None, False

    async def get_timestamp(self) -> int:
        """ Gets the current timestamp. """

        tzone = timezone('Etc/GMT')
        the_time = datetime.now(tzone).timestamp()
        return the_time

    async def get_expired_transmutations(self) -> None:
        """ Gets expired transmutation skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'transmutation' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        transmutations = await mycursor.fetchall()
        await mycursor.close()
        return transmutations

    async def get_expired_frogs(self) -> None:
        """ Gets expired frog skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'frog' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        frogs = await mycursor.fetchall()
        await mycursor.close()
        return frogs

    async def get_expired_potion_items(self) -> List[List[Union[str, int]]]:
        """ Gets expired transmutation skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'potion' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        transmutations = await mycursor.fetchall()
        await mycursor.close()
        return transmutations

    async def get_expired_ring_items(self) -> List[List[Union[str, int]]]:
        """ Gets expired transmutation skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'ring' AND (%s - skill_timestamp) >= 36000
            """, (the_time,))
        transmutations = await mycursor.fetchall()
        await mycursor.close()
        return transmutations

    async def get_hacks(self) -> List[List[Union[str, int]]]:
        """ Gets all hack skill actions. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = 'hack'")
        hacks = await mycursor.fetchall()
        await mycursor.close()
        return hacks
    
    async def get_user_target_hacks(self, attacker_id: int) -> List[List[Union[str, int]]]:
        """ Gets all hacks that a specific user commited or spreaded.
        :param attacker_id: The ID of the attacker. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = 'hack' AND user_id = %s", (attacker_id,))
        hacks = await mycursor.fetchall()
        await mycursor.close()
        return hacks

    async def get_expired_hacks(self) -> List[List[Union[str, int]]]:
        """ Gets expired hack skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'hack' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        hacks = await mycursor.fetchall()
        await mycursor.close()
        return hacks

    async def get_expired_wires(self) -> None:
        """ Gets expired wires skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'wire' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        wires = await mycursor.fetchall()
        await mycursor.close()
        return wires

    async def get_expired_knock_outs(self) -> None:
        """ Gets expired knock-out skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'hit' AND (%s - skill_timestamp) >= 86400
            """, (the_time,))
        knock_outs = await mycursor.fetchall()
        await mycursor.close()
        return knock_outs

    async def get_user_currency(self, user_id: int) -> List[Union[str, int]]:
        """ Gets the user currency.
        :param user_id: The ID of the user to get. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchone()
        await mycursor.close()
        return user

    async def get_sloth_profile(self, user_id: int) -> List[Union[str, int]]:
        """ Gets the SlothProfile for the user.
        :param user_id: The ID of the user to get. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothProfile WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchone()
        await mycursor.close()
        return user

    # ========== DELETE ========== #
    async def delete_skill_action_by_message_id(self, message_id: int) -> None:
        """ Deletes a skill action by message ID.
        :param message_id: The ID of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothSkills WHERE message_id = %s", (message_id,))
        await db.commit()
        await mycursor.close()

    async def delete_skill_action_by_target_id(self, target_id: int) -> None:
        """ Deletes a skill action by target ID.
        :param target_id: The ID of the target member. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothSkills WHERE target_id = %s", (target_id,))
        await db.commit()
        await mycursor.close()

    async def delete_debuff_skill_action_by_target_id(self, target_id: int) -> None:
        """ Deletes debuff skill actions by target ID.
        :param target_id: The ID of the target member. """

        mycursor, db = await the_database()
        await mycursor.execute("""
        DELETE FROM SlothSkills WHERE target_id = %s
        WHERE skill_type IN ('hack', 'wire', 'frog', 'hit')
        """, (target_id,))
        await db.commit()
        await mycursor.close()

    async def delete_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str, multiple: bool = False) -> None:
        """ Deletes a skill action by target ID.
        :param target_id: The ID of the target member.
        :param skill_type: The type of the action skill. """

        mycursor, db = await the_database()
        sql = "DELETE FROM SlothSkills WHERE target_id = %s AND skill_type = %s" + 'LIMIT 1' if not multiple else ''
        await mycursor.execute(sql, (target_id, skill_type))
        await db.commit()
        await mycursor.close()

    async def delete_skill_action_by_user_id_and_skill_type(self, user_id: int, skill_type: str, multiple: bool = False) -> None:
        """ Deletes a skill action by user ID.
        :param user_id: The ID of the user member.
        :param skill_type: The type of the action skill. """

        mycursor, db = await the_database()
        sql = "DELETE FROM SlothSkills WHERE user_id = %s AND skill_type = %s" + 'LIMIT 1' if not multiple else ''
        await mycursor.execute(sql, (user_id, skill_type))
        await db.commit()
        await mycursor.close()

    # ========== UPDATE ========== #

    async def update_user_money(self, user_id: int, money: int):
        """ Updates the user's money.
        :param user_id: The ID of the user to update the money.
        :param money: The money to be incremented (it works with negative numbers). """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE UserCurrency SET user_money = user_money + %s
            WHERE user_id = %s""", (money, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_skills_used(self, user_id: int, addition: int = 1) -> None:
        """ Updates the user's skills used counter.
        :param user_id: The ID of the user.
        :param addition: What will be added to the user's current number of skills used. (Can be negative numbers)"""

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothProfile SET skills_used = skills_used + %s WHERE user_id = %s", (addition, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_rings(self, user_id: int, addition: int = 1) -> None:
        """ Updates the user's rings counter.
        :param user_id: The ID of the user.
        :param addition: What will be added to the user's current number of rings. (Can be negative numbers)"""

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothProfile SET rings = rings + %s WHERE user_id = %s", (addition, user_id))
        await db.commit()
        await mycursor.close()


    async def update_user_skill_ts(self, user_id: int, skill: Enum, new_skill_ts: int = None) -> None:
        """ Updates the value of the user's skill.
        :parma user_id: The ID of the user.
        :param skill: The Enum of the skill.
        :param new_skill_ts: The new timestamp value for the skill. Default = None. """

        mycursor, db = await the_database()
        sql = "UPDATE SkillsCooldown SET " + skill.value + " = %s WHERE user_id = %s"
        await mycursor.execute(sql, (new_skill_ts, user_id))
        await db.commit()
        await mycursor.close()

    # ========== INSERT ==========

    async def insert_user_skill_cooldown(self, user_id: int, skill: Enum, skill_ts: int) -> None:
        """ Updates the value of the user's skill.
        :parma user_id: The ID of the user.
        :param skill: The Enum of the skill.
        :param skill_ts: The timestamp value for the skill. """

        mycursor, db = await the_database()
        sql = "INSERT INTO SkillsCooldown (user_id, " + skill.value + ") VALUES (%s, %s)"
        await mycursor.execute(sql, (user_id, skill_ts))
        await db.commit()
        await mycursor.close()