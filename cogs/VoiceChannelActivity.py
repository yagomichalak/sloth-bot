import discord
from discord.ext import commands, tasks
from mysqldb import the_database
from typing import List, Tuple, Union, Any
from datetime import datetime
from pytz import timezone
import os

allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('MOD_ROLE_ID'))]

class VoiceChannelActivity(commands.Cog):
	""" Category for the users' voice channel activities. """

	def __init__(self, client) -> None:
		""" Cog's initializing method. """

		self.client = client
		self.server_id = 777886754761605140


	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to use. """

		self.calculate.start()
		self.check_old_record_deletion_time.start()

		print('VoiceChannelActivity cog is online!')

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		""" Registers a member whenever they join a channel. """
		

		# === Checks whether the user just changed their state being in the same VC. ===
		if before.self_mute != after.self_mute: return
		if before.self_deaf != after.self_deaf: return
		if before.self_stream != after.self_stream: return
		if before.self_deaf != after.self_deaf: return
		if before.mute != after.mute: return
		if before.deaf != after.deaf: return
		if channel := after.channel:

			tzone = timezone('Etc/GMT-1')
			date_and_time = datetime.now().astimezone(tzone)
			the_time = date_and_time.strftime('%H:%M')

			await self.insert_row(the_time, channel.id, channel.name, member.id, member.name)


	@tasks.loop(seconds=60)
	async def calculate(self) -> None:
		""" Calculates all members that are in a voice channel. """

		tzone = timezone('Etc/GMT-1')
		date_and_time = datetime.now().astimezone(tzone)
		the_time = date_and_time.strftime('%H:%M')

		guild = self.client.get_guild(self.server_id)
		channels = [c for c in guild.voice_channels]

		all_channel_members = []

		for channel in channels:
			if channel.members:
				channel_members = [(the_time, channel.id, channel.name, m.id, m.name) for m in channel.members]
				all_channel_members.append(channel_members)

		if all_channel_members:
			await self.insert_first_row(channel_members)


	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_voice_channel_activity(self, ctx):
		""" Creates the VoiceChannelActivity table. """

		if await self.table_voice_channel_activity_exists():
			return await ctx.send("**The __VoiceChannelActivity__ already exists!**")

		mycursor, db = await the_database()
		await mycursor.execute("""
			CREATE TABLE VoiceChannelActivity (
				the_time TIME NOT NULL, channel_id BIGINT NOT NULL,
				channel_name VARCHAR(50) NOT NULL, member_id BIGINT NOT NULL,
				member_name VARCHAR(50) NOT NULL) DEFAULT CHARSET utf8mb4
		""")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Table __VoiceChannelActivity__ created!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_voice_channel_activity(self, ctx):
		""" Drops the VoiceChannelActivity table. """

		if not await self.table_voice_channel_activity_exists():
			return await ctx.send("**The __VoiceChannelActivity__ doesn't exist!**")

		mycursor, db = await the_database()		
		await mycursor.execute("DROP TABLE VoiceChannelActivity")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Table __VoiceChannelActivity__ dropped!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_voice_channel_activity(self, ctx):
		""" Resets the VoiceChannelActivity table. """

		if not await self.table_voice_channel_activity_exists():
			return await ctx.send("**The __VoiceChannelActivity__ doesn't exist yet!**")

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM VoiceChannelActivity")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Table __VoiceChannelActivity__ reset!**")


	async def insert_first_row(self, channel_members: List[Tuple[Union[int, str]]]) -> None:
		""" Inserts the first row of the minute with the info of all users who are in voice channels. 
		:param channel_members: A list of tuples containing the individual members and their info. """

		mycursor, db = await the_database()
		await mycursor.executemany("""
			INSERT INTO VoiceChannelActivity (the_time, channel_id, channel_name, member_id, member_name)
			VALUES (%s, %s, %s, %s, %s)""", channel_members)
		await db.commit()
		await mycursor.close()

	async def insert_row(self, the_time: datetime, channel_id: int, channel_name: str, member_id: int, member_name: str) -> None:
		""" Inserts a row containing info of member and the voice channel that they're currently in. 
		:param the_time: The current time.
		:param: channel_id: The ID channel that the member is in.
		:param channel_name: The name of the channel that the member is in.
		:param member_id: The ID of the member.
		:param member_name: The name of the member. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO VoiceChannelActivity (the_time, channel_id, channel_name, member_id, member_name)
			VALUES (%s, %s, %s, %s, %s)""", (the_time, channel_id, channel_name, member_id, member_name))
		await db.commit()
		await mycursor.close()

	@tasks.loop(seconds=60)
	async def check_old_record_deletion_time(self, limit_hours: int = 3) -> None:
		""" Checks whether it's time to delete old records.
		:param limit_hours: The limit of hours that the DB needs to store,
		PS: If the number of registered hours in the DB is exceeded, the oldest records will be deleted,
		so the limit is satisfied again. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT DISTINCT HOUR(the_time) FROM VoiceChannelActivity")
		hours = [h[0] for h in await mycursor.fetchall()]

		if limit_hours < len(hours):
			await mycursor.execute("DELETE FROM VoiceChannelActivity WHERE HOUR(the_time) = %s", (hours.pop(0),))
			await db.commit()

	async def get_hour_record_by_channel(self, channel_id: int, time: str) -> List[List[Union[datetime, str, int]]]:
		""" Gets all user records at a given hour and channel.
		:param channel_id: The ID of the channel to which you are filtering.
		:param time: The time to which you are filtering the search. """

		mycursor, db = await the_database()
		if len(time) < 3:
			await mycursor.execute("SELECT DISTINCT HOUR(the_time), member_name, member_id FROM VoiceChannelActivity WHERE channel_id = %s and HOUR(the_time) = %s", (channel_id, time))
		else:
			await mycursor.execute("SELECT DISTINCT the_time, member_name, member_id FROM VoiceChannelActivity WHERE channel_id = %s and the_time = %s", (channel_id, time))

		records = await mycursor.fetchall()
		await mycursor.close()
		return records

	async def get_user_record_by_time(self, member_id: int, time: str) -> List[Union[int, str]]:
		""" Gets user records by the given hour. 
		:param member_id: The ID of the member from whom you want to fetch information.
		:param time: The time at around the user that you are looking for has to have information. """

		mycursor, db = await the_database()
		if len(time) < 3:
			await mycursor.execute("SELECT DISTINCT HOUR(the_time), channel_id, channel_name,  member_id from VoiceChannelActivity WHERE HOUR(the_time) = %s and member_id = %s", (time, member_id))
		else:
			await mycursor.execute("SELECT DISTINCT the_time, channel_id, channel_name, member_id from VoiceChannelActivity WHERE the_time = %s and member_id = %s", (time, member_id))

		records = await mycursor.fetchall()
		await mycursor.close()
		return records

	@commands.command(aliases=['whowas', 'ww', 'whoWas', 'whowere', 'who_were', 'whoWere'])
	@commands.has_any_role(*allowed_roles)
	async def who_was(self, ctx, channel: discord.VoiceChannel = None, time: str = None) -> None:
		""" Shows in which members were in the given voice channel at the given time:
		:param channel: The channel you want to check.
		:param time: The time. """

		if not channel:
			return await ctx.send("**Hey, inform a channel to fetch users from!**")

		if not time:
			return await ctx.send("**Yo, inform a time!**")

		records = await self.get_hour_record_by_channel(channel.id, time)
		if not records:
			return await ctx.send("**Nothing found for the given time!**")


		users = [m.mention if (m := discord.utils.get(ctx.guild.members, id=member[2])) else member[1] for member in records]

		embed = discord.Embed(
			title=f"Users at around `{records[0][0]}` in the `{channel}` VC:",
			description=f"{', '.join(users)}"
			)

		await ctx.send(embed=embed)

	@commands.command(aliases=['waswhere', 'was'])
	@commands.has_any_role(*allowed_roles)
	async def was_where(self, ctx, member: discord.Member = None, time: str = None) -> None:
		""" Shows in which voice channel a specific user was at a given time:
		:param member: The member you want to check.
		:param time: The time. """

		if not member:
			return await ctx.send("**Hey, inform a channel to fetch users from!**")

		if time is None:
			return await ctx.send("**Yo, inform a time!**")

		records = await self.get_user_record_by_time(member.id, time)
		if not records:
			return await ctx.send("**Nothing found for the given time and/or member!**")

		channels = [c.mention if (c := discord.utils.get(ctx.guild.channels, id=channel[1])) else channel[2] for channel in records]
		embed = discord.Embed(
			title=f"`{member}` at around `{time}` was in:",
			description=f"{', '.join(channels)}"
			)

		await ctx.send(embed=embed)


def setup(client) -> None:
	client.add_cog(VoiceChannelActivity(client))