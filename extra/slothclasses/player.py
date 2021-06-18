import discord
from discord.ext import commands

from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, CommandNotReady, SkillsUsedRequirement
from extra import utils

from mysqldb import the_database, the_django_database
from typing import Union, List
from datetime import datetime
import os

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


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
            await mycursor.execute("SELECT sloth_class FROM UserCurrency WHERE user_id = %s", (user_id,))
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

    async def check_cooldown(self, user_id, skill_number: int, seconds: int = 86400) -> bool:
        """ Checks whether user skill is on cooldown (method).
        :param user_id: The ID of the user who to check it"""

        last_skill_ts = await self.get_user_action_skill_ts(user_id=user_id, skill_number=skill_number)

        # current_time = ctx.message.created_at
        current_time = datetime.utcnow()

        cooldown_in_seconds = (current_time - datetime.fromtimestamp(last_skill_ts)).total_seconds()
        if cooldown_in_seconds >= seconds:
            return True
        raise ActionSkillOnCooldown(try_after=cooldown_in_seconds, error_message="Action skill on cooldown!")

    def skill_on_cooldown(skill_number: int = 1, seconds: int = 86400):
        """ Checks whether the user's action skill is on cooldown. """

        async def real_check(ctx):
            """ Perfoms the real check. """

            last_skill_ts = await Player.get_user_action_skill_ts(Player, user_id=ctx.author.id, skill_number=skill_number)
            current_time = await utils.get_timestamp()
            cooldown_in_seconds = current_time - last_skill_ts
            if cooldown_in_seconds >= seconds:
                return True
            raise ActionSkillOnCooldown(
                try_after=cooldown_in_seconds, error_message="Action skill on cooldown!", cooldown=seconds)

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

            user_currency = await Player.get_user_currency(Player, user_id=ctx.author.id)

            if user_currency[15] >= requirement:
                return True

            raise SkillsUsedRequirement(
                error_message=f"You must have `{requirement}` skills used in order to use this skill, {ctx.author.mention}!")

        return commands.check(real_check)

    # Is user EFFECT

    async def get_user_effects(self, user_id: int) -> List[str]:
        """ Gets the effects that the user is under. """

        # effects = []

        effects = {}
        now = await utils.get_timestamp()

        def calculate(now, then):
            # - int(now)
            m, s = divmod((int(then) - int(now)), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)

            d += 1

            msg = ""

            if d > 0:
                msg = f"Ends in `{d:d}d`, `{h:d}h`, `{m:02d}m` & `{s:02d}s`"
            elif h > 0:
                msg = f"Ends in `{h:d}h`, `{m:02d}m` & `{s:02d}s`"
            elif m > 0:
                msg = f"Ends in `{m:02d}m` & `{s:02d}s`"
            elif s > 0:
                msg = f"Ends in `{s:02d}s`"

            return msg

        if await self.is_user_protected(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='divine_protection')
            effects['protected'] = {}
            effects['protected']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['protected']['frames'] = []
            effects['protected']['cords'] = (0, 0)
            effects['protected']['resize'] = None
            effects['protected']['has_gif'] = True

        if await self.is_transmutated(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='transmutation')
            effects['transmutated'] = {}
            effects['transmutated']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['transmutated']['frames'] = []
            effects['transmutated']['cords'] = (0, 0)
            effects['transmutated']['resize'] = None
            effects['transmutated']['has_gif'] = True

        if await self.is_user_hacked(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='hack')
            effects['hacked'] = {}
            effects['hacked']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['hacked']['frames'] = []
            effects['hacked']['cords'] = (0, 0)
            effects['hacked']['resize'] = None

        if await self.is_user_wired(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='wire')
            effects['wired'] = {}
            effects['wired']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['wired']['frames'] = []
            effects['wired']['cords'] = (0, 0)
            effects['wired']['resize'] = None

        if await self.is_user_knocked_out(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='knock_out')
            effects['knocked_out'] = {}
            effects['knocked_out']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['knocked_out']['frames'] = []
            effects['knocked_out']['cords'] = (0, 0)
            effects['knocked_out']['resize'] = None

        if await self.is_user_frogged(user_id=user_id):
            then = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='frog')
            effects['frogged'] = {}
            effects['frogged']['cooldown'] = calculate(now=now, then=then[2]) if then else 'Ends in ??'
            effects['frogged']['frames'] = []
            effects['frogged']['cords'] = (0, 0)
            effects['frogged']['resize'] = None

        return effects

    async def is_user_protected(self, user_id: int) -> bool:
        """ Checks whether user is protected.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT protected FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_protected = await mycursor.fetchone()
        await mycursor.close()
        return user_protected is not None and user_protected[0]

    async def is_transmutated(self, user_id: int) -> bool:
        """ Checks whether user is transmutated.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT COUNT(*) FROM SlothSkills WHERE user_id = %s AND skill_type = 'transmutation'", (user_id,))
        user_transmutated = await mycursor.fetchone()
        await mycursor.close()
        return user_transmutated[0]

    async def is_user_hacked(self, user_id: int) -> bool:
        """ Checks whether user is hacked.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT hacked FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_hacked = await mycursor.fetchone()
        await mycursor.close()
        return user_hacked is not None and user_hacked[0]

    async def is_user_wired(self, user_id: int) -> bool:
        """ Checks whether user is wired.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT wired FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_wired = await mycursor.fetchone()
        await mycursor.close()
        return user_wired is not None and user_wired[0]

    async def is_user_knocked_out(self, user_id: int) -> bool:
        """ Checks whether user is knocked out.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT knocked_out FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_knocked_out = await mycursor.fetchone()
        await mycursor.close()
        return user_knocked_out is not None and user_knocked_out[0]

    async def is_user_frogged(self, user_id: int) -> bool:
        """ Checks whether user is frogged.
        :param user_id: The ID of the user to check it. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT frogged FROM UserCurrency WHERE user_id = %s", (user_id,))
        user_frogged = await mycursor.fetchone()
        await mycursor.close()
        return user_frogged is not None and user_frogged[0]

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

    async def get_skill_action_by_user_id_and_skill_type(self, user_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
        """ Gets a skill action by user ID and skill type.
        :param user_id: The user ID with which to get the skill action.
        :param skill_type: The skill type of the skill action. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE user_id = %s and skill_type = %s", (user_id, skill_type))
        skill_actions = await mycursor.fetchall()
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

    async def get_user_action_skill_ts(self, user_id: int, skill_number: int = 1) -> Union[str, bool]:
        """ Gets the user's last action skill timestamp from the database.
        :param user_id: The ID of the user to get the action skill timestamp.
        :param skill_number: The number of the skill, ex: 1 for skill 1. """

        mycursor, db = await the_database()
        if skill_number == 1:
            await mycursor.execute("SELECT last_skill_ts FROM UserCurrency WHERE user_id = %s", (user_id,))
        elif skill_number == 2:
            await mycursor.execute("SELECT last_skill_two_ts FROM UserCurrency WHERE user_id = %s", (user_id,))

        last_skill_ts = await mycursor.fetchone()
        await mycursor.close()
        if last_skill_ts:
            return last_skill_ts[0]
        else:
            return None

    async def get_timestamp(self) -> int:
        """ Gets the current timestamp. """

        epoch = datetime.fromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        return the_time

    async def get_expired_transmutations(self) -> None:
        """ Gets expired transmutation skill actions. """

        the_time = await utils.get_timestamp()
        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'transmutation' AND (%s - skill_timestamp) >= 3600
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

    async def get_expired_open_shop_items(self) -> None:
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

    async def get_expired_hacks(self) -> None:
        """ Gets expired hacks skill actions. """

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

    async def get_user_currency(self, user_id: int) -> Union[List[Union[str, int]], bool]:
        """ Gets the user currency.
        :param user_id: The ID of the user to get. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,))
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

    async def delete_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> None:
        """ Deletes a skill action by target ID.
        :param target_id: The ID of the target member.
        :param skill_type: The type of the action skill. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothSkills WHERE target_id = %s AND skill_type = %s", (target_id, skill_type))
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

    async def update_user_action_skill_ts(self, user_id: int, current_ts: int) -> None:
        """ Updates the user's last action skill timestamp.
        :param user_id: The ID of the member to update.
        :param current_ts: The timestamp to update to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET last_skill_ts = %s WHERE user_id = %s", (current_ts, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_action_skill_two_ts(self, user_id: int, current_ts: int) -> None:
        """ Updates the user's last action skill two timestamp.
        :param user_id: The ID of the member to update.
        :param current_ts: The timestamp to update to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET last_skill_two_ts = %s WHERE user_id = %s", (current_ts, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_skills_used(self, user_id: int, addition: int = 1) -> None:
        """ Updates the user's skills used counter.
        :param user_id: The ID of the user.
        :param addition: What will be added to the user's current number of skills used. (Can be negative numbers)"""

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET skills_used = skills_used + %s WHERE user_id = %s", (addition, user_id))
        await db.commit()
        await mycursor.close()

    async def reset_user_action_skill_cooldown(self, user_id: int) -> None:
        """ Resets the user's action skill cooldown.
        :param user_id: The ID of the user to reet the cooldown. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET last_skill_ts = 0 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()


    @commands.command(aliases=["fx", "efx", "user_effects", "usereffects", "geteffects", "membereffects", "member_effects"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def effects(self, ctx, member: discord.Member = None) -> None:
        """ Gets all effects from a member.
        :param member: The member to get it from. """

        if not member:
            member = ctx.author

        effects = await self.get_user_effects(member.id)
        formated_effects = [f"__**{effect.title()}**__: {values['cooldown']}" for effect, values in effects.items()]
        
        embed = discord.Embed(
            title=f"__Effects for {member}__",
            description='\n'.join(formated_effects),
            color=member.color,
            timestamp=ctx.message.created_at,
            url=member.avatar_url
        )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)