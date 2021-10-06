import discord
from discord.ext import commands

from extra.smartrooms.rooms import BasicRoom, PremiumRoom, GalaxyRoom, SmartRoom
from extra.smartrooms.database_commands import SmartRoomDatabase
from extra.view import GalaxyRoomView
from extra import utils

import os

class CreateSmartRoom(SmartRoomDatabase):

	def __init__(self, client: commands.Cog) -> None:
		self.client = client
		self.vc_id = int(os.getenv('CREATE_SMART_ROOM_VC_ID'))
		self.cat_id = int(os.getenv('CREATE_SMART_ROOM_CAT_ID'))


	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after) -> None:
		""" Handler for voice channel activity, that's eventually gonna be used
		for creating a SmartRoom. """

		# Checks if the user is leaving the vc and whether there still are people in there
		if before.channel and before.channel.category and before.channel.category.id == self.cat_id:
			user_voice_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
			len_users = len(user_voice_channel.members)
			print('dsadsa')
			if len_users == 0 and user_voice_channel.id != self.vc_id:
				try:
					print('brooooooo')
					premium_channel = await self.get_smartroom(user_voice_channel.id)
					if premium_channel:
						the_txt = discord.utils.get(member.guild.channels, id=premium_channel[4])
						await self.delete_room(premium_channel[1], vc_id=premium_channel[2])
						await the_txt.delete()
				except Exception:
					pass
				await user_voice_channel.delete()

		print('kek')
		# Checks if the user is joining the create a room VC
		if not after.channel:
			return

		if after.channel.id == self.vc_id:
			# the_time = await utils.get_timestamp()
			# old_time = await self.get_user_vc_timestamp(member.id, the_time)
			# if not the_time - old_time >= 60:
			# 	await member.send(
			# 		f"**You're on a cooldown, try again in {round(60 - (the_time - old_time))} seconds!**",)
			# 	# return await member.move_to(None)
			# 	return
			# if the_time - old_time >= 60:
			# 	await self.update_user_vc_ts(member.id, the_time)

			embed = discord.Embed(color=member.color)
			embed.set_image(url="attachment://create_galaxy_room.png")
			view: discord.ui.View = GalaxyRoomView()
			df_msg = await member.send(content="\u200b",
				embed=embed, file=discord.File('./images/smart_vc/selection_menu.png', filename='create_galaxy_room.png'), view=view)


			await view.wait()
			print('Pampa')


	@commands.command()
	async def create_room(self, ctx) -> None:
		""" Test command for creating rooms. """

		author: discord.Member = ctx.author
		guild: discord.Guild = ctx.guild

		cat: discord.CategoryChannel = discord.utils.get(guild.categories, id=777886764056051737)
		vc: discord.VoiceChannel = await guild.create_voice_channel(name=str(ctx.author), category=cat)

		current_ts: int = await utils.get_timestamp()

		try:
			await self.insert_smartroom(author.id, 'basic', vc.id, current_ts)
		except Exception as e:
			print(e)
			await ctx.reply("**An error occurred!**")
		else:
			await ctx.reply(f"Created VC {vc.mention}")


	@commands.command()
	async def get_room(self, ctx, room_id: int = None) -> None:
		""" Test command for getting rooms. """

		author: discord.Member = ctx.author

		if not room_id: return
		
		smart_room: SmartRoom = await self.get_smartroom(vc_id=room_id)

		print('dsauhdsahu', type(smart_room))
		print(smart_room.creation_ts)
		print(smart_room.edited_ts)

	@commands.command()
	async def room(self, ctx, room_id: int = None) -> None:
		""" Test command for deleting rooms. """

		author: discord.Member = ctx.author

		if not room_id: return
		
		smart_room: SmartRoom = await self.get_smartroom(vc_id=room_id)

		print('dsauhdsahu', type(smart_room))
		print(smart_room.creation_ts)
		print(smart_room.edited_ts)


def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(CreateSmartRoom(client))