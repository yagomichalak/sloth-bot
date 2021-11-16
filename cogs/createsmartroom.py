import discord
from discord.ext import commands

from extra.smartrooms.rooms import BasicRoom, PremiumRoom, GalaxyRoom, SmartRoom
from extra.smartrooms.discord_commands import GalaxyRoomCommands
from extra.smartrooms.database_commands import SmartRoomDatabase
from extra.view import SmartRoomView
from extra import utils

import os
from typing import List, Dict

smartroom_cogs: List[commands.Cog] = [
	SmartRoomDatabase, GalaxyRoomCommands
]

class CreateSmartRoom(*smartroom_cogs):

	def __init__(self, client: commands.Cog) -> None:
		self.client = client
		self.vc_id = int(os.getenv('CREATE_SMART_ROOM_VC_ID'))
		self.cat_id = int(os.getenv('CREATE_SMART_ROOM_CAT_ID'))

		self.user_cooldowns: Dict[int, int] = {}


	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after) -> None:
		""" Handler for voice channel activity, that's eventually gonna be used
		for creating a SmartRoom. """

		# Checks if the user is leaving the vc and whether there still are people in there
		if before.channel and before.channel.category and before.channel.category.id == self.cat_id:
			user_voice_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
			len_users = len(user_voice_channel.members)
			if len_users == 0 and user_voice_channel.id != self.vc_id:
				try:
					smart_room = await self.get_smartroom(vc_id=user_voice_channel.id)

					if isinstance(smart_room, BasicRoom):
						await self.delete_smartroom(room_type=smart_room.room_type, vc_id=smart_room.vc.id)
						
					elif isinstance(smart_room, PremiumRoom):
						# the_txt = discord.utils.get(member.guild.channels, id=smart_room.txt.id)
						await self.delete_smartroom(room_type=smart_room.room_type, vc_id=smart_room.vc.id)
						await smart_room.txt.delete()

				except Exception as e:
					print('dsahudhsau e', e)
					pass
				await user_voice_channel.delete()

		# Checks if the user is joining the create a room VC
		if not after.channel:
			return

		if after.channel.id == self.vc_id:
			the_time = await utils.get_timestamp()
			
			old_time = self.user_cooldowns.get(member.id)
			if old_time:
				if the_time - old_time < 60:
					return await member.send(f"**You're on a cooldown, try again in {round(60 - (the_time - old_time))} seconds!**")

				if the_time - old_time >= 60:
					self.user_cooldowns[member.id] = the_time
			else:
				self.user_cooldowns[member.id] = the_time

			embed = discord.Embed(color=member.color)
			embed.set_image(url="attachment://create_galaxy_room.png")

			category: discord.CategoryChannel = discord.utils.get(member.guild.categories, id=self.cat_id)
			view: discord.ui.View = SmartRoomView(self.client, member=member, cog=self, category=category)
			create_room_msg = await member.send(embed=embed, file=discord.File('./images/smart_vc/selection_menu.png', filename='create_galaxy_room.png'), view=view)


			await view.wait()
			await utils.disable_buttons(view)
			await create_room_msg.edit(view=view)

	


def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(CreateSmartRoom(client))