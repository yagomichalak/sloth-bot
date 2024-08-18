from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union, Optional


class PremiumVcTable(commands.Cog):
	""" Class for database commands and methods related to the PremiumVc. """

	def __init__(self, client) -> None:
		self.client = client
		self.db = DatabaseCore()

	# Premium related functions
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_premium_vc(self, ctx) -> None:
		""" (ADM) Creates the PremiumVc table. """

		if await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ already exists!**")

		await self.db.execute_query("CREATE TABLE PremiumVc (user_id BIGINT, user_vc BIGINT, user_txt BIGINT)")
		return await ctx.send("**Table __PremiumVc__ created!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_premium_vc(self, ctx) -> None:
		""" (ADM) Drops the PremiumVc table. """

		if not await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ doesn't exist!**")

		await self.db.execute_query("DROP TABLE PremiumVc")
		return await ctx.send("**Table __PremiumVc__ dropped!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_premium_vc(self, ctx) -> None:
		""" (ADM) Resets the PremiumVc table. """

		if not await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ doesn't exist yet!**")

		await self.db.execute_query("DELETE FROM PremiumVc")
		return await ctx.send("**Table __PremiumVc__ reset!**")

	async def table_premium_vc_exists(self) -> bool:
		""" Checks whether the PremiumVc table exists. """

		return await self.db.table_exists("PremiumVc")

	async def insert_premium_vc(self, user_id: int, user_vc: int, user_txt: int) -> None:
		""" Inserts a Premium Room.
		:param user_id: The owner ID.
		:param user_vc: The voice channel ID.
		:param user_txt: The text channel ID. """

		await self.db.execute_query("INSERT INTO PremiumVc (user_id, user_vc, user_txt) VALUES (%s, %s, %s)", (user_id, user_vc, user_txt))

	async def get_premium_vc(self, user_vc: int) -> List[List[int]]:
		""" Gets a Premium Room by voice channel ID.
		:param user_vc: The voice channel ID. """

		return await self.db.execute_query("SELECT * FROM PremiumVc WHERE user_vc = %s", (user_vc,), fetch="all")

	async def get_premium_txt(self, user_txt: int) -> List[List[int]]:
		""" Gets a Premium Room by text channel ID.
		:param user_txt: The text channel ID. """

		return await self.db.execute_query("SELECT * FROM PremiumVc WHERE user_txt = %s", (user_txt,), fetch="all")

	async def delete_premium_vc(self, user_id: int, user_vc: int) -> None:
		""" Deletes a Premium Room by voice channel ID.
		:param user_id: The owner ID.
		:param user_vc: The voice channel ID. """

		await self.db.execute_query("DELETE FROM PremiumVc WHERE user_id = %s and user_vc = %s", (user_id, user_vc))

	async def delete_premium_txt(self, user_id: int, user_txt: int) -> None:
		""" Deletes a Premium Room by text channel ID.
		:param user_id: The owner ID.
		:param user_txt: The text channel ID. """

		await self.db.execute_query("DELETE FROM PremiumVc WHERE user_id = %s and user_txt = %s", (user_id, user_txt))

class GalaxyVcTable(commands.Cog):
	""" Class for database commands and methods related to the GalaxyVc. """

	def __init__(self, client) -> None:
		self.client = client
		self.db = DatabaseCore()

	# Galaxy related functions
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Creates the GalaxyVc table. """

		if await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ already exists!**")

		await self.db.execute_query("""
			CREATE TABLE GalaxyVc (
			user_id BIGINT NOT NULL,
			user_cat BIGINT NOT NULL,
			user_vc BIGINT NOT NULL,
			user_txt1 BIGINT NOT NULL,
			user_txt2 BIGINT DEFAULT NULL,
			user_vc2 BIGINT DEFAULT NULL,
			user_ts BIGINT NOT NULL,
			user_notified VARCHAR(3) DEFAULT 'no',
			user_txt3 BIGINT DEFAULT NULL,
			user_txt4 BIGINT DEFAULT NULL,
			user_txt5 BIGINT DEFAULT NULL,
			auto_pay TINYINT(1) DEFAULT 0,
			PRIMARY KEY (user_id)
		)""")

		return await ctx.send("**Table __GalaxyVc__ created!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Drops the GalaxyVc table. """

		if not await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ doesn't exist!**")

		await self.db.execute_query("DROP TABLE GalaxyVc")
		return await ctx.send("**Table __GalaxyVc__ dropped!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Resets the GalaxyVc table. """

		if not await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ doesn't exist yet!**")

		await self.db.execute_query("DELETE FROM GalaxyVc")
		return await ctx.send("**Table __GalaxyVc__ reset!**")

	async def table_galaxy_vc_exists(self) -> bool:
		""" Checks whether the GalaxyVc table exists. """

		return await self.db.table_exists("GalaxyVc")

	async def insert_galaxy_vc(self, user_id: int, user_cat: int, user_vc: int, user_txt1: int, user_ts: int) -> None:
		""" Inserts a Galaxy Room.
		:param user_id: The owner ID.
		:param user_cat: The category ID.
		:param user_vc: The Galaxy Room's main voice channel ID.
		:param user_txt1: The ID of the first text channel.
		:param user_txt2: The ID of the second text channel.
		:param user_ts: The current timestamp. """

		await self.db.execute_query(
			"""
			INSERT INTO GalaxyVc (user_id, user_cat, user_vc, user_txt1, user_ts)
			VALUES (%s, %s, %s, %s, %s)""", (user_id, user_cat, user_vc, user_txt1, user_ts)
			)

	async def get_galaxy_txt(self, user_id: int, user_cat: int) -> List[int]:
		""" Gets the Galaxy Room's channels by category ID.
		:param user_id: The ID of the owner of the channels.
		:param user_cat: The ID of the category. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE user_id = %s and user_cat = %s", (user_id, user_cat), fetch="one")

	async def get_galaxy_by_cat_id(self, cat_id: int) -> List[int]:
		""" Gets a Galaxy Room by category ID.
		:param cat_id: The category ID. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE user_cat = %s", (cat_id,), fetch="one")

	async def get_galaxy_by_user_id(self, user_id: int) -> List[Union[int, str]]:
		""" Gets a Galaxy Room by user ID.
		:param user_id: The user ID. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE user_id = %s", (user_id,), fetch="one")

	async def get_all_galaxy_rooms(self, the_time: int):
		""" Get all expired Galaxy Rooms.
		:param the_time The current time. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE %s - user_ts >= 1209600", (the_time,), fetch="all")

	async def get_galaxy_rooms_by_expiration_time(self) -> List[List[Union[str, int]]]:
		""" Get all Galaxy Rooms. """

		return await self.db.execute_query("SELECT user_id, user_ts FROM GalaxyVc ORDER BY user_ts ASC", fetch="all")

	async def get_galaxy_rooms(self) -> List[List[Union[str, int]]]:
		""" Get all Galaxy Rooms. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc", fetch="all")

	async def get_all_galaxy_rooms_in_danger_zone(self, the_time) -> None:
		""" Gets all Galaxy Rooms in the danger zone; at least 2 days from being deleted.
		:param the_time: The current time. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE (user_ts + 1209600) - %s <= 172800 and user_notified = 'no'", (the_time,), fetch="all")

	async def get_user_all_galaxy_rooms(self, user_id: int) -> List[int]:
		""" Checks whether a user has a Galaxy Room.
		:param user_id: The ID of the user to check it. """

		return await self.db.execute_query("SELECT user_ts, user_cat, user_txt1, user_txt2, user_txt3, user_txt4, user_txt5, user_vc, user_vc2, auto_pay FROM GalaxyVc WHERE user_id = %s", (user_id,), fetch="one")

	async def has_galaxy_rooms(self, user_id: int) -> bool:
		""" Checks whether a user has a Galaxy Room.
		:param user_id: The ID of the user to check it. """

		return await self.db.execute_query("SELECT * FROM GalaxyVc WHERE user_id = %s", (user_id,), fetch="one")

	async def update_txt(self, user_id: int, position: int, channel_id: Optional[int] = None) -> None:
		""" Updates a channel value in the database.
		:param user_id: The ID of the owner of the Galaxy Room.
		:param position: The position of the channel to update.
		:param channel_id: The ID of the channel. [Optional] """

		column_name = f"user_txt{position}"
		sql = "UPDATE GalaxyVc SET " + column_name + " = %s WHERE user_id = %s "

		await self.db.execute_query(sql, (channel_id, user_id))

	async def update_galaxy_user(self, old_owner_id: int, new_owner_id: int) -> None:
		""" Updates the Galaxy Room's owner ID.
		:param old_owner_id: The old owner's ID.
		:param new_owner_id: The new owner's ID. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_id = %s WHERE user_id = %s", (new_owner_id, old_owner_id))

	async def update_txt_2(self, user_id: int, txt2: int = None) -> None:
		""" Updates the user's second text channel value in the database.
		:param user_id: The user ID.
		:param txt2: The value for the second txt. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_txt2 = %s WHERE user_id = %s", (txt2, user_id))

	async def update_vc_2(self, user_id: int, vc2: int = None) -> None:
		""" Updates the user's second voice channel value in the database.
		:param user_id: The user ID.
		:param vc2: The value for the second vc. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_vc2 = %s WHERE user_id = %s", (vc2, user_id))

	async def user_notified_yes(self, user_id: int) -> None:
		""" Updates the the user notified status to 'yes'.
		:param user_id: The ID of the user. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_notified = 'yes' WHERE user_id = %s", (user_id,))

	async def user_notified_no(self, user_id: int) -> None:
		""" Updates the the user notified status to 'no'.
		:param user_id: The ID of the user. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_notified = 'no' WHERE user_id = %s", (user_id,))

	async def increment_galaxy_ts(self, user_id: int, addition: int) -> None:
		""" Increments a Galaxy Room's timestamp so it lasts longer.
		:param user_id: The ID of the owner of the Galaxy Room.
		:param addition: The amount of time to increment, in seconds. """

		await self.db.execute_query("UPDATE GalaxyVc SET user_ts = user_ts + %s WHERE user_id = %s", (addition, user_id))

	async def update_galaxy_auto_pay(self, user_id: int, auto_pay: bool = True) -> None:
		""" Updates the the Galaxy Room's auto pay mode.
		:param user_id: The ID of the user who's the owner of the Galaxy Room.
		:param auto_pay: Whether to put it into auto pay mode or not. [Default = True] """

		auto_pay = 1 if auto_pay else 0
		await self.db.execute_query("UPDATE GalaxyVc SET auto_pay = %s WHERE user_id = %s", (auto_pay, user_id))

	async def delete_galaxy_vc(self, user_id: int, user_vc: int) -> None:
		""" Deletes a a Galaxy Room by voice channel ID.
		:param user_id: The user ID.
		:param user_vc: The voice channel ID. """

		await self.db.execute_query("DELETE FROM GalaxyVc WHERE user_id = %s and user_vc = %s", (user_id, user_vc))

	async def delete_galaxy_by_cat_id(self, cat_id: int) -> None:
		""" Deletes a a Galaxy Room by category ID.
		:param cat_id: The category ID. """

		await self.db.execute_query("DELETE FROM GalaxyVc WHERE user_cat = %s", (cat_id,))

class UserVcStampTable(commands.Cog):
	""" Class for database commands and methods related to the SmartRooms. """

	def __init__(self, client) -> None:
		self.client = client
		self.db = DatabaseCore()

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def create_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Creates the UserVcstamp table. """

		if await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ already exists!**")
			
		await self.db.execute_query("CREATE TABLE UserVCstamp (user_id bigint, user_vc_ts bigint)")

		return await ctx.send("**Table __UserVCstamp__ created!**", delete_after=5)

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def drop_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Drops the UserVcstamp table. """

		if not await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ doesn't exist!**")

		await self.db.execute_query("DROP TABLE UserVCstamp")

		return await ctx.send("**Table __UserVCstamp__ dropped!**", delete_after=5)

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def reset_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Resets the UserVcstamp table. """

		if not await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ doesn't exist yet!**")

		await self.db.execute_query("DELETE FROM UserVCstamp")

		return await ctx.send("**Table __UserVCstamp__ reset!**", delete_after=5)

	async def table_user_vc_ts_exists(self) -> bool:
		""" Checks whether the UserVCstamp table exists. """

		return await self.db.table_exists("UserVCstamp")

	async def insert_user_vc(self, user_id: int, the_time: int) -> None:
		""" Inserts a user into the UserVCstamp table.
		:param user_id: The ID of the user.
		:param the_time: The current time. """

		await self.db.execute_query("INSERT INTO UserVCstamp (user_id, user_vc_ts) VALUES (%s, %s)", (user_id, the_time - 61))

	async def get_user_vc_timestamp(self, user_id: int, the_time: int) -> int:
		""" Gets the user voice channel timestamp, and insert them into the database
		in case they are not there yet.
		:param user_id: The ID of the user.
		:param the_time: The current time. """

		user = await self.db.execute_query("SELECT * FROM UserVCstamp WHERE user_id = %s", (user_id,), fetch="one")

		if not user:
			await self.insert_user_vc(user_id, the_time)
			return await self.get_user_vc_timestamp(user_id, the_time)

		return user[1]

	async def update_user_vc_ts(self, user_id: int, new_ts: int) -> None:
		""" Updates the user's voice channel timestamp.
		:param user_id: The ID of the user.
		:param new_ts: The new/current timestamp. """

		await self.db.execute_query("UPDATE UserVCstamp SET user_vc_ts = %s WHERE user_id = %s", (new_ts, user_id))
