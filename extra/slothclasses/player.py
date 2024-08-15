import discord
from discord.ext import commands

from extra.customerrors import (
    MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, 
    SkillsUsedRequirement, ActionSkillsLocked, PoisonedCommandError,
    KidnappedCommandError
    )
from extra import utils

from mysqldb import DatabaseCore
from typing import Union, List, Tuple, Dict, Any
from datetime import datetime
from random import random, choice
import os
from pytz import timezone

from enum import Enum
from .userpets import UserPetsTable
from .userbabies import UserBabiesTable

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))
additional_cogs: List[commands.Cog] = [
    UserPetsTable, UserBabiesTable
]

class Skill(Enum):

    ONE = 'skill_one_ts'
    TWO = 'skill_two_ts'
    THREE = 'skill_three_ts'
    FOUR = 'skill_four_ts'
    FIVE = 'skill_five_ts'


class Player(*additional_cogs):

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

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

            user_sloth_class = await DatabaseCore().execute_query("SELECT sloth_class FROM SlothProfile WHERE user_id = %s", (user_id,), fetch="one")
            return None if not user_sloth_class else user_sloth_class[0]

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

    def skills_locked():
        """ Checks whether the user's set of skills are locked. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            locked = await Player.get_skill_action_by_target_id_and_skill_type(Player, target_id=ctx.author.id, skill_type='lock')
            if not locked:
                return True

            raise ActionSkillsLocked(error_message="Action Skills are locked until completing a Quest!")

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

    def mirrored_skill() -> bool:
        async def real_check(ctx) -> bool:
            mirrored_skill = await Player.get_skill_action_by_user_id_and_skill_type(Player, user_id=ctx.author.id, skill_type='mirror')
            if mirrored_skill:
                return True
            else:
                return False


        return commands.check(real_check)

    def poisoned() -> bool:
        """ Checks whether the user is poisoned and disorients the command. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            poisoned = await Player.get_skill_action_by_target_id_and_skill_type(Player, target_id=ctx.author.id, skill_type='poison')
            if not poisoned:
                return True

            # 65% chance of messing with the user when they're poisoned
            if random() > 0.65:
                return True

            poisoned_messages: List[Dict[str, Any]] = [
                {"name": "Normal", "message": "I can't... 😵‍💫", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "YOU asked for a fun fact? Aight, did you know that if u eat 70 bananas in less than 10 minutes, you'll die of radiation?", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "I guess some **BREAD** is better than what you're trynna do, here, take some 🍞!", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "There is evidence that frogs have roamed the Earth for more than 200 million years, at least as long as the dinosaurs.", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "I'm busy now, I might do it later! 🤨", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "Toads are frogs. The word 'toad' is usually used for frogs that have warty and dry skin, as well as shorter hind legs. 🐸", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "yhbt yhl hand", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "Did you like my new haircut? <a:dance_sloth:737775776228966470>", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "Can you give me some leaves? I'm hungry 😢", "reply": True, "command": None, "kwargs": None},
                {"name": "Normal", "message": "Titanic: * Starts to Sink *\nMe & the crew: <a:sad_pepe_violin:970130876086222848><a:sad_pepe_violin:970130876086222848><a:sad_pepe_violin:970130876086222848><a:sad_pepe_violin:970130876086222848>", "reply": True, "command": None, "kwargs": None},
            ]

            random_poisoned_msg = choice(poisoned_messages)

            # Gets messageable object to send the message
            answer: discord.PartialMessageable = None
            if random_poisoned_msg['reply']:
                if isinstance(ctx, commands.Context):
                    answer = ctx.reply
                else:
                    answer = ctx.respond
            else:
                if isinstance(ctx, commands.Context):
                    answer = ctx.send
                else:
                    answer = ctx.respond

            await answer(content=random_poisoned_msg["message"])


            raise PoisonedCommandError()
            

        return commands.check(real_check)

    def kidnapped() -> bool:
        """ Checks whether the user is poisoned and disorients the command. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            kidnapped = await Player.get_skill_action_by_target_id_and_skill_type(Player, target_id=ctx.author.id, skill_type='kidnap')
            if not kidnapped:
                return True

            raise KidnappedCommandError()

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

        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='sabotage'):
            effects['sabotaged'] = {}
            effects['sabotaged']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['sabotaged']['frames'] = []
            effects['sabotaged']['cords'] = (0, 0)
            effects['sabotaged']['resize'] = None
            effects['sabotaged']['debuff'] = True

        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='lock'):
            effects['locked'] = {}
            effects['locked']['cooldown'] = "Ends when completing a Quest"
            effects['locked']['frames'] = []
            effects['locked']['cords'] = (0, 0)
            effects['locked']['resize'] = None
            effects['locked']['debuff'] = True

        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='poison'):
            effects['poisoned'] = {}
            effects['poisoned']['cooldown'] = f"Ends <t:{int(then[2]) + general_cooldown}:R>" if then else 'Ends in ??'
            effects['poisoned']['frames'] = []
            effects['poisoned']['cords'] = (0, 0)
            effects['poisoned']['resize'] = None
            effects['poisoned']['debuff'] = True

        if then := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='kidnap'):
            effects['kidnapped'] = {}
            effects['kidnapped']['cooldown'] = f"Ends when rescue is paid"
            effects['kidnapped']['frames'] = []
            effects['kidnapped']['cords'] = (0, 0)
            effects['kidnapped']['resize'] = None
            effects['kidnapped']['debuff'] = True

        return effects

    async def get_sloth_class_skills(self, sloth_class: str) -> List[commands.Command]:
        """ Gets all skills for a given Sloth Class.
        :param sloth_class: The name of the Sloth Class. """

        the_class = [cls for cls in Player.__subclasses__() if cls.__name__.lower() == sloth_class.lower()][0]
        class_commands = the_class.__dict__['__cog_commands__']
        cmds = []

        for c in class_commands:
            if c.hidden or c.parent or not c.checks:
                continue

            elif not [check for check in c.checks if check.__qualname__ == 'Player.skill_mark.<locals>.real_check']:
                continue
        
            cmds.append(c)
        return cmds

    async def insert_skill_action(self, user_id: int, skill_type: str, skill_timestamp: int, target_id: int = None, message_id: int = None, channel_id: int = None, emoji: str = None, price: int = 0, content: str = None) -> None:
        """ Inserts a skill action into the database, if needed.
        :param user_id: The ID of the perpetrator of the skill action.
        :param skill_type: The type of the skill action.
        :param skill_timestamp: The timestamp of the skill action.
        :param target_id: The ID of the target member of the skill action.
        :param message_id: The ID of the message related to the action, if there's any.
        :param price: The price of the item or something, if it is for sale.
        :param content: The content of the skill, if any. """

        await self.db.execute_query("""
            INSERT INTO SlothSkills (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price, content))

    # ========== GET ========== #

    async def get_skill_action_by_message_id(self, message_id: int) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by message ID.
        :param message_id: The ID with which to get the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE message_id = %s", (message_id,), fetch="one")

    async def get_skill_action_by_skill_type(self, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by skill type.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE skill_type = %s", (skill_type,), fetch="one")

    async def get_skill_actions_by_skill_type(self, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets skill actions by skill type.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE skill_type = %s", (skill_type,), fetch="all")

    async def get_skill_actions_by_skill_type_and_int_content(self, skill_type: str, int_content) -> Union[List[Union[int, str]], bool]:
        """ Gets skill actions by skill type.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE skill_type = %s AND int_content = %s", (skill_type, int_content), fetch="all")

    async def get_skill_action_by_message_id_and_skill_type(self, message_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by message ID and skill type.
        :param message_id: The ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE message_id = %s AND skill_type = %s", (message_id, skill_type), fetch="one")

    async def get_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by target ID and skill type.
        :param target_id: The target ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE target_id = %s and skill_type = %s", (target_id, skill_type), fetch="one")

    async def get_skill_action_by_user_id_and_skill_type(self, user_id: int, skill_type: str, multiple: bool = False
    ) -> Union[List[List[Union[int, str]]], List[Union[int, str]], bool]:
        """ Gets a skill action by user ID and skill type.
        :param user_id: The user ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        return await self.db.execute_query(
            "SELECT * FROM SlothSkills WHERE user_id = %s and skill_type = %s", (user_id, skill_type),
            fetch="all" if multiple else "one"
            )

    async def get_skill_action_by_user_id_or_target_id_and_skill_type(self, user_id: int, skill_type: str, multiple: bool = False
    ) -> Union[List[List[Union[int, str]]], List[Union[int, str]], bool]:
        """ Gets a skill action by user ID and skill type.
        :param user_id: The user ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        await self.db.execute_query(
            "SELECT * FROM SlothSkills WHERE (user_id = %s OR target_id = %s) and skill_type = %s", (user_id, user_id, skill_type),
            fetch="all" if multiple else "one"
            )

    async def get_skill_action_by_reaction_context(self, message_id: int, target_id: int) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by reaction context.
        :param message_id: The ID of the message of the skill action.
        :param target_id: The ID of the target member of the skill action. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE message_id = %s AND target_id = %s", (message_id, target_id), fetch="one")

    async def get_user_action_skill_ts(self, user_id: int, skill_field: str) -> List[Union[str, bool]]:
        """ Gets the user's last action skill timestamp from the database.
        :param user_id: The ID of the user to get the action skill timestamp.
        :param skill_field: The skill field to check. """

        sql = "SELECT " + skill_field + " FROM SkillsCooldown WHERE user_id = %s"
        skill_ts = await self.db.execute_query(sql, (user_id,), fetch="one")

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
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'transmutation' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_expired_frogs(self) -> None:
        """ Gets expired frog skill actions. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'frog' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_expired_potion_items(self) -> List[List[Union[str, int]]]:
        """ Gets expired Potion items from the shop. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'potion' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_expired_ring_items(self) -> List[List[Union[str, int]]]:
        """ Gets expired Wedding Ring items from the shop. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'ring' AND (%s - skill_timestamp) >= 36000
            """, (the_time,), fetch="all")

    async def get_expired_pet_egg_items(self) -> List[List[Union[str, int]]]:
        """ Gets expired Pet Egg items from the shop. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'pet_egg' AND (%s - skill_timestamp) >= 432000
            """, (the_time,), fetch="all")

    async def get_hacks(self) -> List[List[Union[str, int]]]:
        """ Gets all hack skill actions. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE skill_type = 'hack'", fetch="all")
    
    async def get_user_target_hacks(self, attacker_id: int) -> List[List[Union[str, int]]]:
        """ Gets all hacks that a specific user commited or spreaded.
        :param attacker_id: The ID of the attacker. """

        return await self.db.execute_query("SELECT * FROM SlothSkills WHERE skill_type = 'hack' AND user_id = %s", (attacker_id,), fetch="all")

    async def get_expired_hacks(self) -> List[List[Union[str, int]]]:
        """ Gets expired hack skill actions. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'hack' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_expired_wires(self) -> None:
        """ Gets expired wires skill actions. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'wire' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_expired_knock_outs(self) -> None:
        """ Gets expired knock-out skill actions. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'hit' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

    async def get_user_currency(self, user_id: int) -> List[Union[str, int]]:
        """ Gets the user currency.
        :param user_id: The ID of the user to get. """

        return await self.db.execute_query("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,), fetch="one")

    async def get_users_currency(self, user_ids: List[int]) -> List[List[Union[str, int]]]:
        """ Gets currency of a list of users.
        :param user_ids: The list of IDs of the users to get the currency from. """

        return await self.db.execute_query("SELECT user_money FROM UserCurrency WHERE user_id in %s", (user_ids,), fetch="all")

    async def get_sloth_profile(self, user_id: int) -> List[Union[str, int]]:
        """ Gets the SlothProfile for the user.
        :param user_id: The ID of the user to get. """

        return await self.db.execute_query("SELECT * FROM SlothProfile WHERE user_id = %s", (user_id,), fetch="one")

    async def get_specific_unprotected_users(self, user_ids: int) -> List[Union[str, int]]:
        """ Gets specific SlothProfiles from a list of user IDs.
        :param user_ids: The list of user IDs. """

        return await self.db.execute_query("""
            SELECT UC.user_id, UC.user_money FROM UserCurrency AS UC
            WHERE UC.user_id IN {}
            AND UC.user_id IN (
                SELECT SP.user_id FROM SlothProfile AS SP
                WHERE SP.sloth_class <> 'default') 
            AND UC.user_id NOT IN (
                SELECT SS.target_id FROM SlothSkills AS SS WHERE skill_type = 'divine_protection')
            """.format(tuple(user_ids)), fetch="all")

    # ========== DELETE ========== #
    async def delete_skill_action_by_message_id(self, message_id: int) -> None:
        """ Deletes a skill action by message ID.
        :param message_id: The ID of the skill action. """

        await self.db.execute_query("DELETE FROM SlothSkills WHERE message_id = %s", (message_id,))

    async def delete_skill_action_by_target_id(self, target_id: int) -> None:
        """ Deletes a skill action by target ID.
        :param target_id: The ID of the target member. """

        await self.db.execute_query("DELETE FROM SlothSkills WHERE target_id = %s", (target_id,))

    async def delete_debuff_skill_action_by_target_id(self, target_id: int) -> None:
        """ Deletes debuff skill actions by target ID.
        :param target_id: The ID of the target member. """

        await self.db.execute_query("""
        DELETE FROM SlothSkills WHERE target_id = %s AND skill_type IN ('hack', 'wire', 'frog', 'hit', 'sabotage')
        """, (target_id,))

    async def delete_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str, multiple: bool = False) -> None:
        """ Deletes a skill action by target ID.
        :param target_id: The ID of the target member.
        :param skill_type: The type of the action skill. """

        sql = "DELETE FROM SlothSkills WHERE target_id = %s AND skill_type = %s" + "LIMIT 1" if not multiple else ""
        await self.db.execute_query(sql, (target_id, skill_type))

    async def delete_skill_action_by_user_id_and_skill_type(self, user_id: int, skill_type: str, multiple: bool = False) -> None:
        """ Deletes a skill action by user ID.
        :param user_id: The ID of the user member.
        :param skill_type: The type of the action skill. """

        sql = "DELETE FROM SlothSkills WHERE user_id = %s AND skill_type = %s" + "LIMIT 1" if not multiple else ""
        await self.db.execute_query(sql, (user_id, skill_type))

    async def delete_skill_actions_by_target_id_and_skill_type(self, users: List[Tuple[int, str]]) -> None:
        """ Deletes a skill action by user ID.
        :param user_id: The ID of the user member.
        :param skill_type: The type of the action skill. """

        sql = "DELETE FROM SlothSkills WHERE target_id = %s AND skill_type = %s"
        await self.db.execute_querymany(sql, users)

    async def delete_skill_action_by_user_id_or_target_id_and_skill_type_and_price(self, user_id: int, skill_type: str, price: str, multiple: bool = False) -> None:
        """ Deletes a skill action by user_id or target ID and skill type and price.
        :param user_id: The ID of the user or target member.
        :param skill_type: The type of the action skill.
        :param price: The value for the price field.
        :param multiple: If multiple rows should deleted. """

        sql = "DELETE FROM SlothSkills WHERE (user_id = %s OR target_id = %s) AND skill_type = %s AND price = %s" + "LIMIT 1" if not multiple else ""
        await self.db.execute_query(sql, (user_id, user_id, skill_type, price))

    # ========== UPDATE ========== #
    async def update_user_skills_used(self, user_id: int, addition: int = 1) -> None:
        """ Updates the user's skills used counter.
        :param user_id: The ID of the user.
        :param addition: What will be added to the user's current number of skills used. (Can be negative numbers)"""

        await self.db.execute_query("UPDATE SlothProfile SET skills_used = skills_used + %s WHERE user_id = %s", (addition, user_id))

    async def update_user_rings(self, user_id: int, addition: int = 1) -> None:
        """ Updates the user's rings counter.
        :param user_id: The ID of the user.
        :param addition: What will be added to the user's current number of rings. (Can be negative numbers)"""

        await self.db.execute_query("UPDATE SlothProfile SET rings = rings + %s WHERE user_id = %s", (addition, user_id))


    async def update_user_skill_ts(self, user_id: int, skill: Enum, new_skill_ts: int = None) -> None:
        """ Updates the value of the user's skill.
        :parma user_id: The ID of the user.
        :param skill: The Enum of the skill.
        :param new_skill_ts: The new timestamp value for the skill. Default = None. """

        sql = "UPDATE SkillsCooldown SET " + skill.value + " = %s WHERE user_id = %s"
        await self.db.execute_query(sql, (new_skill_ts, user_id))

    async def update_user_skills_ts(self, user_id: int, new_skill_ts: int = None) -> None:
        """ Updates the values of the user's skills.
        :parma user_id: The ID of the user.
        :param new_skill_ts: The new timestamp value for the skills. Default = None. """

        sql = """
        UPDATE SkillsCooldown SET 
        skill_one_ts = NULL, skill_two_ts = NULL,
        skill_three_ts = NULL, skill_four_ts = NULL,
        skill_five_ts = NULL WHERE user_id = %s
        """
        await self.db.execute_query(sql, (user_id,))

    async def update_user_skills_ts_increment(self, user_id: int, increment: int) -> None:
        """ Updates the timestamps of the user's skills by incrementing them.
        :parma user_id: The ID of the user.
        :param increment: The increment to apply to the cooldowns. (Can be negative) """

        sql = """
        UPDATE SkillsCooldown SET 
        skill_one_ts = skill_one_ts + %s, skill_two_ts = skill_two_ts + %s,
        skill_three_ts = skill_three_ts + %s, skill_four_ts = skill_four_ts + %s,
        skill_five_ts = skill_five_ts + %s WHERE user_id = %s
        """
        await self.db.execute_query(sql, (increment, increment, increment, increment, increment, user_id))

    async def update_change_class_ts(self, user_id: int, new_ts: int) -> None:
        """ Updates the user's changing-Sloth-class cooldown.
        :param user_id: The ID of the user.
        :param new_ts: The new timestamp for the cooldown. """

        await self.db.execute_query("UPDATE SlothProfile SET change_class_ts = %s WHERE user_id = %s", (new_ts, user_id))

    # ========== INSERT ==========

    async def insert_user_skill_cooldown(self, user_id: int, skill: Enum, skill_ts: int) -> None:
        """ Updates the value of the user's skill.
        :parma user_id: The ID of the user.
        :param skill: The Enum of the skill.
        :param skill_ts: The timestamp value for the skill. """

        sql = "INSERT INTO SkillsCooldown (user_id, " + skill.value + ") VALUES (%s, %s)"
        await self.db.execute_query(sql, (user_id, skill_ts))
