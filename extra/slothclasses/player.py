import discord
from discord.ext import commands

from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown

from mysqldb import the_database
from typing import Union, List
from datetime import datetime
import os

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Player(commands.Cog):

	def __init__(self, client) -> None:
		print('oi')
		self.client = client


	@commands.Cog.listener()
	async def on_ready(self) -> None:
		print('ok')
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

	def skill_on_cooldown():
		""" Checks whether the user's action skill is on cooldown. """

		async def get_user_action_skill_ts(user_id: int) -> Union[str, bool]:
			""" Gets the user's last action skill timestamp from the database.
			:param user_id: The ID of the user to get the action skill timestamp. """

			mycursor, db = await the_database()
			await mycursor.execute("SELECT last_skill_ts FROM UserCurrency WHERE user_id = %s", (user_id,))
			last_skill_ts = await mycursor.fetchone()
			await mycursor.close()
			if last_skill_ts:
				return last_skill_ts[0]
			else:
				return None

		async def real_check(ctx):
			""" Perfoms the real check. """

			last_skill_ts = await get_user_action_skill_ts(ctx.author.id)
			current_time = ctx.message.created_at
			cooldown_in_seconds = (current_time - datetime.utcfromtimestamp(last_skill_ts)).total_seconds()
			if cooldown_in_seconds >= 86400:
				return True
			raise ActionSkillOnCooldown(try_after=cooldown_in_seconds, error_message="Action skill on cooldown!")

		return commands.check(real_check)

	# Is user EFFECT


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

	async def is_user_knocked_out(self, user_id: int) -> bool:
		""" Checks whether user is knocked out.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT knocked_out FROM UserCurrency WHERE user_id = %s", (user_id,))
		user_knocked_out = await mycursor.fetchone()
		await mycursor.close()
		return user_knocked_out is not None and user_knocked_out[0]




	async def insert_skill_action(self, user_id: int, skill_type: str, skill_timestamp: int, target_id: int = None, message_id: int = None, channel_id: int = None, emoji: str = None, price: int = 0) -> None:
		""" Inserts a skill action into the database, if needed.
		:param user_id: The ID of the perpetrator of the skill action.
		:param skill_type: The type of the skill action.
		:param skill_timestamp: The timestamp of the skill action.
		:param target_id: The ID of the target member of the skill action. 
		:param message_id: The ID of the message related to the action, if there's any. 
		:param price: The price of the item or something, if it is for sale. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO SlothSkills (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price))
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

	async def get_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by target ID and skill type.
		:param target_id: The target ID with which to get the skill action. 
		:param skill_type: The skill type of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE target_id = %s and skill_type = %s", (target_id, skill_type))
		skill_action = await mycursor.fetchone()
		await mycursor.close()
		return skill_action

	async def get_skill_action_by_reaction_context(self, message_id: int, target_id: int) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by reaction context.
		:param message_id: The ID of the message of the skill action.
		:param target_id: The ID of the target member of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s AND target_id = %s", (message_id, target_id))
		skill_action = await mycursor.fetchone()
		await mycursor.close()
		return skill_action

	async def get_skill_action_by_user_id(self, user_id: int) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by reaction context.
		:param user_id: The ID of the user of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE user_id = %s AND skill_type = 'potion'", (user_id,))
		skill_action = await mycursor.fetchone()
		await mycursor.close()
		return skill_action

	async def get_timestamp(self) -> int:
		""" Gets the current timestamp. """

		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()
		return the_time

	async def get_expired_steals(self) -> List[List[Union[str, int]]]:
		""" Gets expired steal skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'steal' AND (%s - skill_timestamp) >= 2400
			""", (the_time,))
		steals = await mycursor.fetchall()
		await mycursor.close()
		return steals

	async def get_expired_protections(self) -> None:
		""" Gets expired divine protection skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'divine_protection' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		divine_protections = await mycursor.fetchall()
		await mycursor.close()
		return divine_protections

	async def get_expired_transmutations(self) -> None:
		""" Gets expired transmutation skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'transmutation' AND (%s - skill_timestamp) >= 3600
			""", (the_time,))
		transmutations = await mycursor.fetchall()
		await mycursor.close()
		return transmutations

	async def get_expired_open_shop_items(self) -> None:
		""" Gets expired transmutation skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'potion' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		transmutations = await mycursor.fetchall()
		await mycursor.close()
		return transmutations

	async def get_expired_hacks(self) -> None:
		""" Gets expired hack skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'hack' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		hacks = await mycursor.fetchall()
		await mycursor.close()
		return hacks

	async def get_expired_knock_outs(self) -> None:
		""" Gets expired knock-out skill actions. """

		the_time = await self.get_timestamp()
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

	async def reset_user_action_skill_cooldown(self, user_id: int) -> None:
		""" Resets the user's action skill cooldown. 
		:param user_id: The ID of the user to reet the cooldown. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET last_skill_ts = 0 WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()






