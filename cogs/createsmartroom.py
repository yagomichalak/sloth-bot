import discord
from extra import utils
from discord.ext import commands, tasks
from datetime import datetime
import asyncio
from PIL import Image, ImageFont, ImageDraw
import os
from cogs.slothcurrency import SlothCurrency
from mysqldb import *
from typing import List, Union, Any, Optional

from extra.menu import ConfirmSkill
from extra.smartroom.smartroom import PremiumVcTable, GalaxyVcTable, UserVcStampTable

smart_room_cogs: List[commands.Cog] = [
	PremiumVcTable, GalaxyVcTable, UserVcStampTable
]

class CreateSmartRoom(*smart_room_cogs):
	""" A cog related to the creation of a custom voice channel. """

	def __init__(self, client):
		""" Class initializing method. """

		self.client = client
		self.vc_id = int(os.getenv('CREATE_SMART_ROOM_VC_ID', 123))
		self.cat_id = int(os.getenv('CREATE_SMART_ROOM_CAT_ID', 123))

	@commands.Cog.listener()
	async def on_ready(self):
		""" Tells when the cog is ready to be used. """

		print("CreateSmartRoom cog is online")
		self.check_galaxy_expiration.start()

	@tasks.loop(hours=3)
	async def check_galaxy_expiration(self):
		""" Task that checks Galaxy Rooms expirations. """

		if not await self.table_galaxy_vc_exists():
			return

		the_time = await utils.get_timestamp()

		# Looks for rooms that are soon going to be deleted (Danger zone)
		SlothCurrency = self.client.get_cog("SlothCurrency")
		danger_rooms = await self.get_all_galaxy_rooms_in_danger_zone(the_time)
		for droom in danger_rooms:
			member = self.client.get_user(droom[0])
			if not member:
				continue

			# Checks for auto_pay mode
			if droom[11]:
				# Checks to see if the user has enough money to autopay the GR
				user_currency = await SlothCurrency.get_user_currency(member.id)
				vcs, txts = await self.order_rooms_default(droom)
				required_money: int = await self.get_rent_price(len(txts), len(vcs))
				if user_currency and user_currency[0][1] >= required_money:
					await SlothCurrency.update_user_money(member.id, -required_money)
					await self.increment_galaxy_ts(member.id, 1209600)
					await self.user_notified_no(member.id)
					# Tries notifying the user of the renewal through DM's
					try:
						await member.send(f"**Your Galaxy Room was auto renewed! `(-{required_money}łł)`**")
					except Exception:
						pass
					continue

			# Embed for the Galaxy Room in Danger Zone notification
			embed = discord.Embed(
				title="__Galaxy Rooms in Danger Zone__",
				description=(
					"Your Galaxy rooms will be deleted within two days, in case you wanna keep them,"
					" consider renewing them for `1500łł` (2 channels) or for `2000łł` (3 channels) by using the **z!galaxy pay_rent** command in any of your rooms!"
				),
				color=discord.Color.red())
			try:
				await member.send(embed=embed)
				await self.user_notified_yes(member.id)
			except Exception:
				pass

		# Looks for expired rooms to delete
		all_rooms = await self.get_all_galaxy_rooms(the_time)
		for room in all_rooms:
			for i in range(2, 6):
				# id, cat, vc, txt1, txt2, txt3, ts
				channel = self.client.get_channel(room[i])
				try:
					await channel.delete()
				except Exception:
					pass

			member = self.client.get_user(room[0])
			try:
				category = self.client.get_channel(room[1])
				await category.delete()
			except Exception as e:
				print(e)
				pass
			else:
				await member.send(f"**Hey! Your rooms expired so they got deleted!**")
			finally:
				await self.delete_galaxy_vc(room[0], room[2])

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after) -> None:
		""" Handler for voice channel activity, that's eventually gonna be used
		for creating a SmartRoom. """

		# Checks if the user is leaving the vc and whether there still are people in there
		if before.channel:
			if before.channel.category:
				if before.channel.category.id == self.cat_id:
					user_voice_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
					len_users = len(user_voice_channel.members)
					if len_users == 0 and user_voice_channel.id != self.vc_id:
						try:
							premium_channels = await self.get_premium_vc(user_voice_channel.id)
							if premium_channels:
								the_txt = discord.utils.get(member.guild.channels, id=premium_channels[0][2])
								await self.delete_premium_vc(premium_channels[0][0], premium_channels[0][1])
								await the_txt.delete()
						except Exception:
							pass
						await user_voice_channel.delete()

		# Checks if the user is joining the create a room VC
		if not after.channel:
			return

		if after.channel.id == self.vc_id:
			the_time = await utils.get_timestamp()
			old_time = await self.get_user_vc_timestamp(member.id, the_time)
			if not the_time - old_time >= 60:
				await member.send(
					f"**You're on a cooldown, try again in {round(60 - (the_time - old_time))} seconds!**",)
				# return await member.move_to(None)
				return
			if the_time - old_time >= 60:
				await self.update_user_vc_ts(member.id, the_time)

			df_msg = await member.send(file=discord.File('./images/smart_vc/selection_menu.png'))
			await df_msg.add_reaction('1️⃣')
			await df_msg.add_reaction('2️⃣')
			await df_msg.add_reaction('3️⃣')

			def check(reaction, user):
				return user == member and str(reaction.emoji) in '1️⃣2️⃣3️⃣'

			# Gets the room type
			reaction, user = await self.get_reaction_response(member, check)
			if reaction is None:
				return

			# Redirects the member to their equivalent room type choice
			if str(reaction.emoji) == '1️⃣':
				await self.basic_room(member)
			elif str(reaction.emoji) == '2️⃣':
				await self.premium_room(member)
			else:
				await self.galaxy_room(member)

	# Room type 1
	async def basic_room(self, member: discord.Member) -> None:
		""" Prompts questions to the member in order to create a Basic Room.
		:param member: The member to prompt. """

		# Checks
		def check_size(m):
			value = m.content
			author = m.author
			if value.isnumeric() and author == member and m.channel == bot_msg.channel:
				value = int(value)
				if value >= 0 and value <= 10 and value != 1:
					return True
				else:
					self.client.loop.create_task(member.send(file=discord.File('./images/smart_vc/basic/1 incorrect.png')))
			elif not value.isnumeric() and author == member and m.channel == bot_msg.channel:
				self.client.loop.create_task(member.send('**Inform a valid value!**'))

		def check_name(m):
			value = m.content
			author = m.author
			if author == member and m.channel == bot_msg.channel:
				if 0 < len(m.content) <= 20:
					return True
				else:
					self.client.loop.create_task(member.send('**Please inform a name having between 1-20 characters!**'))

		def check_confirm(reaction, user):
			return user == member and str(reaction.emoji) in '✅❌'

		# Setting room configs

		# Get the size of the room
		bot_msg = ''
		msg1 = await member.send(file=discord.File('./images/smart_vc/basic/1 select size.png'))
		bot_msg = msg1
		limit = await self.get_response(member, check_size)

		if limit is None:
			return

		# Get the name of the room
		msg2 = await member.send(file=discord.File('./images/smart_vc/basic/1 select name.png'))
		bot_msg = msg2
		name = await self.get_response(member, check_name)

		if name is None:
			return

		# Gets the configuration confirmation
		await self.make_preview_basic(member.id, name, limit)
		msg3 = await member.send(file=discord.File(f'./images/smart_vc/user_previews/{member.id}.png'))
		await msg3.add_reaction('✅')
		await msg3.add_reaction('❌')
		bot_msg = msg3
		reaction, user = await self.get_reaction_response(member, check_confirm)
		if reaction is None:
			return

		# Confirm configurations
		if str(reaction.emoji) == '✅':

			# Checks if the user has money for it (5łł)
			user_currency = await SlothCurrency.get_user_currency(member, member.id)
			if not user_currency:
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
				return await member.send( 
					embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
					view=view)

			if user_currency[0][1] < 5:
				return await member.send("**You don't have enough money to buy this service!**")

			# Gets the CreateSmartRoom category, creates the VC and tries to move the user to there
			the_category_test = discord.utils.get(member.guild.categories, id=self.cat_id)

			if not (creation := await self.try_to_create(kind='voice', category=the_category_test, name=name, user_limit=limit)):
				return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

			await creation.edit(sync_permissions=True)
			await creation.set_permissions(member, move_members=True)
			await SlothCurrency.update_user_money(member, member.id, -5)
			await member.send(f"**You've been charged `5łł`!**")

			await member.send(file=discord.File('./images/smart_vc/created.png'))
			try:
				await member.move_to(creation)
			except discord.errors.HTTPException:
				await member.send("**You cannot be moved because you are not in a Voice-Channel!**")
				await creation.delete()
			else:
				await self.log_smartroom_creation(member, 'basic', vc=creation)
			finally:
				try:
					os.remove(f'./images/smart_vc/user_previews/{member.id}.png')
				except Exception:
					pass
		else:
			return

	# Room type 2
	async def premium_room(self, member: discord.Member) -> None:
		""" Prompts questions to the member in order to create a Premium Room.
		:param member: The member to prompt. """

		# Checks
		def check_size(m):
			value = m.content
			author = m.author
			if value.isnumeric() and author == member and m.channel == bot_msg.channel:
				value = int(value)
				if value >= 0 and value <= 25 and value != 1:
					return True
				else:
					self.client.loop.create_task(member.send(file=discord.File('./images/smart_vc/premium/incorrect.png')))
			elif not value.isnumeric() and author == member and m.channel == bot_msg.channel:
				self.client.loop.create_task(member.send('**Inform a valid value!**'))

		def check_name(m):
			value = m.content
			author = m.author
			if author == member and m.channel == bot_msg.channel:
				if 0 < len(m.content) <= 20:
					return True
				else:
					self.client.loop.create_task(member.send('**Please inform a name having between 1-20 characters!**'))

		def check_confirm(reaction, user):
			return user == member and str(reaction.emoji) in '✅❌'

		# Setting room configs

		# Get the size of the room
		bot_msg = ''
		msg1 = await member.send(file=discord.File('./images/smart_vc/premium/2 select size.png'))
		bot_msg = msg1
		limit = await self.get_response(member, check_size)

		if limit is None:
			return

		# Get the name of the room
		msg2 = await member.send(file=discord.File('./images/smart_vc/premium/2 select name.png'))
		bot_msg = msg2
		name = await self.get_response(member, check_name)

		if name is None:
			return

		# Gets the configuration confirmation
		await self.make_preview_premium(member.id, name, name, limit)
		msg3 = await member.send(file=discord.File(f'./images/smart_vc/user_previews/{member.id}.png'))
		await msg3.add_reaction('✅')
		await msg3.add_reaction('❌')
		bot_msg = msg3
		reaction, user = await self.get_reaction_response(member, check_confirm)
		if reaction is None:
			return

		# Confirm configurations
		if str(reaction.emoji) == '✅':
			# Checks if the user has money for it (100łł)
			user_currency = await SlothCurrency.get_user_currency(member, member.id)
			if not user_currency:
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
				return await member.send( 
					embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
					view=view)

			if user_currency[0][1] < 100:
				return await member.send("**You don't have enough money to buy this service!**")

			# Gets the CreateSmartRoom category, creates the VC and text channel and tries to move the user to there

			creations = []
			failed = False

			the_category_test = discord.utils.get(member.guild.categories, id=self.cat_id)

			if vc_channel := await self.try_to_create(kind='voice', category=the_category_test, name=name, user_limit=limit):
				creations.append(vc_channel)
				await vc_channel.edit(sync_permissions=True)
			else:
				failed = True

			if txt_channel := await self.try_to_create(kind='text', category=the_category_test, name=name):
				creations.append(txt_channel)
				await txt_channel.edit(sync_permissions=True)
			else:
				failed = True

			# Checks whether there are failed creations, if so, delete the channels
			if failed:
				await self.delete_things(creations)
				return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

			await SlothCurrency.update_user_money(member, member.id, -100)
			await member.send(f"**You've been charged `100łł`!**")

			# Puts the channels ids in the database
			await self.insert_premium_vc(member.id, vc_channel.id, txt_channel.id)
			await member.send(file=discord.File('./images/smart_vc/created.png'))
			try:
				await member.move_to(vc_channel)
			except discord.errors.HTTPException:
				await member.send("**You cannot be moved because you are not in a Voice-Channel! You have one minute to join the room before it gets deleted together with the text channel.**")
				await asyncio.sleep(60)
				if len(vc_channel.members) == 0:
					await vc_channel.delete()
					await txt_channel.delete()
			else:
				await self.log_smartroom_creation(member, 'premium', vc=vc_channel, txt=txt_channel)
			finally:
				try:
					os.remove(f'./images/smart_vc/user_previews/{member.id}.png')
				except Exception:
					pass

		else:
			return

	async def try_to_create(
		self, 
		kind: str, category: discord.CategoryChannel = None, 
		channel: discord.TextChannel = None, guild: Optional[discord.Guild] = None, owner: Optional[discord.Member] = None, **kwargs: Any
		) -> Union[bool, discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.Thread]:
		""" Try to create something.
		:param thing: The thing to try to create.
		:param kind: Kind of creation. (txt, vc, cat, thread)
		:param category: The category in which it will be created. (Optional)
		:param channel: The channel in which the thread be created in. (Optional)(Required for threads)
		:param guild: The guild in which it will be created in. (Optional)(Required for categories)
		:param owner: The owner of the Galaxy Rooms. (Optional)
		:param kwargs: The arguments to inform the creations. """

		try:
			if kind == 'text':
				the_thing = await category.create_text_channel(**kwargs)
			elif kind == 'voice':
				the_thing = await category.create_voice_channel(**kwargs)
			elif kind == 'category':
				the_thing = await guild.create_category(**kwargs)
			elif kind == 'thread':
				start_message = await channel.send(kwargs['name'])
				await start_message.pin(reason="Galaxy Room's Thread Creation")
				the_thing = await start_message.create_thread(**kwargs)
				if owner:
					await the_thing.add_user(owner)
		except Exception as e:
			print(e)
			return False
		else:
			return the_thing

	async def delete_things(self, things: List[Any]) -> None:
		""" Deletes a list of things.
		:param things: The things to delete. """

		for thing in things:
			try:
				await thing.delete()
			except:
				pass

	# Room type 3
	async def galaxy_room(self, member: discord.Member) -> None:
		""" Prompts questions to the member in order to create a Galaxy Room.
		:param member: The member to prompt. """

		def check_size(m):
			value = m.content
			author = m.author
			if value.isnumeric() and author == member and m.channel == bot_msg.channel:
				value = int(value)
				if value >= 0 and value <= 25 and value != 1:
					return True
				else:
					self.client.loop.create_task(member.send('**Please, a number between 0 and 25 and different than 1!**'))
			elif not value.isnumeric() and author == member and m.channel == bot_msg.channel:
				self.client.loop.create_task(member.send('**Inform a valid value!**'))

		def check_name(m):
			value = m.content
			author = m.author
			if author == member and m.channel == bot_msg.channel:
				if 0 < len(m.content) <= 20:
					return True
				else:
					self.client.loop.create_task(member.send(file=discord.File('./images/smart_vc/galaxy/3 incorrect vc name.png')))

		def check_cat_or_txt_name(m):
			value = m.content
			author = m.author
			if author == member and m.channel == bot_msg.channel:
				if 0 < len(m.content) <= 10:
					return True
				else:
					self.client.loop.create_task(member.send(file=discord.File('./images/smart_vc/galaxy/3 incorrect text chat name or category.png')))

		def check_confirm(reaction, user):
			return user == member and str(reaction.emoji) in '✅❌'

		# Setting room configs

		# Gets the name of the category
		bot_msg = ''
		msg = await member.send(file=discord.File('./images/smart_vc/galaxy/3 category.png'))
		bot_msg = msg
		category_name = await self.get_response(member, check_cat_or_txt_name)

		if category_name is None:
			return

		# Gets the size of the room
		msg2 = await member.send(file=discord.File('./images/smart_vc/galaxy/3 select size vc.png'))
		bot_msg = msg2
		limit = await self.get_response(member, check_size)

		if limit is None:
			return

		# Gets the name of the room
		msg3 = await member.send(file=discord.File('./images/smart_vc/galaxy/3 select name vc.png'))
		bot_msg = msg3
		vc_name = await self.get_response(member, check_name)

		if vc_name is None:
			return

		# Gets the name of the text channel 1
		msg4 = await member.send(file=discord.File('./images/smart_vc/galaxy/3 select text chat 1.png'))
		bot_msg = msg4
		txt1_name = await self.get_response(member, check_cat_or_txt_name)

		if txt1_name is None:
			return

		# Makes the preview image
		# member_id, cat_name, txt1, txt2, txt3, vc, size
		await self.make_preview_galaxy(member.id, category_name, txt1_name, vc_name, limit)
		# Gets the configuration confirmation
		msg5 = await member.send(file=discord.File(f'./images/smart_vc/user_previews/{member.id}.png'))
		await msg5.add_reaction('✅')
		await msg5.add_reaction('❌')
		bot_msg = msg5
		reaction, user = await self.get_reaction_response(member, check_confirm)
		if reaction is None:
			return

		# Confirm configurations
		if str(reaction.emoji) == '✅':

			# Checks if user already has galaxy rooms
			has_galaxy = await self.has_galaxy_rooms(member.id)
			if has_galaxy:
				return await member.send("**You already have a Galaxy category, you can't create more than one!**")

			# Checks whether the server reached the limit of 15 galaxy rooms created at a time 
			if len(await self.get_galaxy_rooms()) >= 15:
				return await member.send(f"**You cannot created a Galaxy Room, because the server reached the limit of Galaxy rooms that can be created at a time; 15!**")

			# Checks if the user has money (1500łł)
			user_currency = await SlothCurrency.get_user_currency(member, member.id)
			if not user_currency:
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
				return await member.send( 
					embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
					view=view)

			if user_currency[0][1] < 1500:
				return await member.send("**You don't have enough money to buy this service!**")

			creations = []
			failed = False

			# Gets the CreateSmartRoom category, creates the VC and text channel and tries to move the user to there
			overwrites = {
			member.guild.default_role: discord.PermissionOverwrite(
				read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False),
			member: discord.PermissionOverwrite(
				read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
			}

			if the_cat := await self.try_to_create(kind='category', guild=member.guild, name=category_name, overwrites=overwrites):
				creations.append(the_cat)
			else:
				return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

			if vc_channel := await self.try_to_create(kind='voice', category=the_cat, name=vc_name, user_limit=limit):
				creations.append(vc_channel)
			else:
				failed = True

			if txt_channel1 := await self.try_to_create(kind='text', category=the_cat, name=txt1_name):
				creations.append(txt_channel1)
			else:
				failed = True

			if failed:
				await self.delete_things(creations)
				return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

			await SlothCurrency.update_user_money(member, member.id, -1500)
			await member.send(f"**You've been charged `1500łł`!**")

			# Inserts the channels in the database
			the_time = await utils.get_timestamp()
			await self.insert_galaxy_vc(member.id, the_cat.id, vc_channel.id, txt_channel1.id, the_time)
			await member.send(file=discord.File('./images/smart_vc/created.png'))
			try:
				await member.move_to(vc_channel)
			except discord.errors.HTTPException:
				await member.send("**You cannot be moved because you are not in a Voice-Channel, but your channels and category will remain alive nonetheless! 👍**")
			else:
				await self.log_smartroom_creation(member, 'galaxy', vc=vc_channel, txt=txt_channel1, cat=the_cat)
			finally:
				try:
					os.remove(f'./images/smart_vc/user_previews/{member.id}.png')
				except Exception:
					pass

				await member.send(embed=discord.Embed(description="""**Congrats you created a galaxy room** :tada:
Here are some rules and rights:

1) Your galaxy room costs **1500** :leaves: every **14 days**. You will get a reminder to pay your rent in the galaxy room a few days before it's due. If you don't pay using the **z!renew** command, the galaxy room gets deleted. 

2) You can **allow** or **unallow** any user to see and use your galaxy room by using the command **z!galaxy allow @User/ID** and **z!galaxy forbid @User/ID**

3) You have to allow a minimum of **10** users. (Bots or admins do not count) 

4) You can check all Galaxy Room related commands using the **z!galaxy** command in the channel

5) You can add up to 4 **threads** each for **250 :leaves: **by writing **z!agc thread `name of the channel` ** **or** for **500** :leaves:  1 additional voice channel by writing **z!agc voice `user limit (0-25)` `name of the channel`** 
You can only add either **threads** **OR** one **voice channel**"""))

		else:
			return

	async def get_response(self, member, check) -> str:
		""" Gets a message response from the member.
		:param member: The member.
		:param check: The check that is gonna be used. """

		try:
			response = await self.client.wait_for('message', timeout=60.0, check=check)
			response = response.content
		except asyncio.TimeoutError:
			await member.send(file=discord.File('./images/smart_vc/timeout.png'))
			return None
		else:
			return response

	async def get_reaction_response(self, member, check) -> List[Union[discord.Reaction, discord.User]]:
		""" Gets a reaction response from the member.
		:param member: The member.
		:param check: The check that is gonna be used. """

		try:
			reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
		except asyncio.TimeoutError:
			timeout = discord.Embed(title='Timeout',
									description='You took too long to answer the questions, try again later.',
									colour=discord.Colour.dark_red())
			await member.send(file=discord.File('./images/smart_vc/timeout.png'))
			return None, None
		else:
			return reaction, user

	async def overwrite_image(self, member_id, text, coords, color, image) -> None:
		""" Writes a text on a Smartroom's image preview, and overwrites the original one.
		:param member_id: The ID of the user who's creating it.
		:param text: The text that's gonna be written.
		:param coords: The coordinates for the text.
		:param color: The color of the text.
		:param image: The image to write on. """

		small = ImageFont.truetype("./images/smart_vc/uni-sans-regular.ttf", 40)
		base = Image.open(image)
		draw = ImageDraw.Draw(base)
		draw.text(coords, text, color, font=small)
		base.save(f'./images/smart_vc/user_previews/{member_id}.png')

	async def overwrite_image_with_image(self, member_id, coords, size) -> None:
		""" Pastes a voice channel image on top of a SmartRoom's image preview
		and overwrites the original one.
		:param member_id: The ID of the user who's creating it.
		:param coords: The coordinates for the image that's gonna be pasted on top of it.
		:param size: The size of the voice channel. """

		path = f'./images/smart_vc/user_previews/{member_id}.png'
		user_preview = Image.open(path)
		size_image = Image.open(size).resize((78, 44), Image.LANCZOS)
		user_preview.paste(size_image, coords, size_image)
		user_preview.save(path)

	async def make_preview_basic(self, member_id, vc, size) -> None:
		""" Makes a creation preview for a Basic Room.
		:param member_id: The ID of the user who's creating it.
		:param vc: The voice channel name.
		:param size: The voice channel size; user limit. """

		preview_template = './images/smart_vc/basic/1 preview2.png'
		color = (132, 142, 142)
		await self.overwrite_image(member_id, vc, (585, 870), color, preview_template)
		if int(size) != 0:
			await self.overwrite_image_with_image(member_id, (405, 870), f'./images/smart_vc/sizes/voice channel ({size}).png')

	async def make_preview_premium(self, member_id, txt, vc, size) -> None:
		""" Makes a creation preview for a Premium Room.
		:param member_id: The ID of the user who's creating it.
		:param txt: The name o the first text channel.
		:param vc: The voice channel name.
		:param size: The voice channel size; user limit. """

		preview_template = './images/smart_vc/premium/2 preview2.png'
		color = (132, 142, 142)
		await self.overwrite_image(member_id, txt.lower(), (585, 760), color, preview_template)
		await self.overwrite_image(member_id, vc, (585, 955), color, f'./images/smart_vc/user_previews/{member_id}.png')
		if int(size) != 0:
			await self.overwrite_image_with_image(member_id, (405, 955), f'./images/smart_vc/sizes/voice channel ({size}).png')

	async def make_preview_galaxy(self, member_id: int, cat_name: str, txt1: str, vc: str, size: int) -> None:
		""" Makes a creation preview for a Galaxy Room.
		:param member_id: The ID of the user who's creating it.
		:param cat_name: The category name.
		:param txt1: The name o the first text channel.
		:param txt2: The name o the second text channel.
		:param txt3: The name o the third text channel. (Deprecated)
		:param vc: The main voice channel name.
		:param size: The voice channel size; user limit. """

		preview_template = './images/smart_vc/galaxy/3 preview2.png'
		color = (132, 142, 142)
		await self.overwrite_image(member_id, cat_name, (505, 730), color, preview_template)
		await self.overwrite_image(member_id, txt1.lower(), (585, 840), color, f'./images/smart_vc/user_previews/{member_id}.png')
		await self.overwrite_image(member_id, vc, (585, 970), color, f'./images/smart_vc/user_previews/{member_id}.png')
		if int(size) != 0:
			await self.overwrite_image_with_image(member_id, (375, 965), f'./images/smart_vc/sizes/voice channel ({size}).png')

	async def handle_permissions(self, members: List[discord.Member], galaxy_room: List[Union[int, str]], guild: discord.Guild, allow: bool = True) -> List[str]:
		""" Handles permissions for a member in one's Galaxy Room.
		:param members: The list of members to handle permissions for.
		:param galaxy_room: The Galaxy Room info.
		:param guild: The guild of the Galaxy Room.
		:param allow: Whether to allow or disallow the member and their permissions from the Galaxy Room. [Default=True]"""

		channels: List[Union[discord.abc.GuildChannel, discord.Thread]] = [
			discord.utils.get(guild.categories, id=galaxy_room[1]),
			discord.utils.get(guild.voice_channels, id=galaxy_room[2]),
			discord.utils.get(guild.text_channels, id=galaxy_room[3]),
			discord.utils.get(guild.threads, id=galaxy_room[4]),
			discord.utils.get(guild.voice_channels, id=galaxy_room[5]),
			discord.utils.get(guild.threads, id=galaxy_room[8]),
			discord.utils.get(guild.threads, id=galaxy_room[9]),
			discord.utils.get(guild.threads, id=galaxy_room[10])
		]

		actioned: List[str] = []

		for m in members:
			try:
				for c in channels:
					if not isinstance(c, discord.Thread):
						if c:
							if allow:
								await c.set_permissions(
									m, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
							else:
								await c.set_permissions(m, overwrite=None)
					else:
						if allow:
							await c.add_user(m)
						else:
							await c.remove_user(m)

			except Exception as e:
				print(e)
				pass
			else:
				actioned.append(m.mention)

		return actioned


	@commands.group(aliases=['gr', 'galaxy_room', 'galaxyroom'])
	async def galaxy(self, ctx) -> None:
		""" Command for managing Galaxy Rooms. """

		if ctx.invoked_subcommand:
			return

		cmd = ctx.command
		prefix = self.client.command_prefix
		subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands]

		subcommands = '\n'.join(subcommands)
		embed = discord.Embed(
		  title="Subcommads",
		  description=f"```apache\n{subcommands}```",
		  color=ctx.author.color,
		  timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)

	@galaxy.command(name="count", aliases=["number", "current", "cnt", "co"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _galaxy_count(self, ctx) -> None:
		""" Counts how many Galaxy Rooms there are currently. """

		galaxy_rooms = await self.get_galaxy_rooms()
		await ctx.reply(f"**We currently have `{len(galaxy_rooms)}` Galaxy Rooms!**")

	@galaxy.command(name="allow", aliases=['permit'])
	async def _galaxy_allow(self, ctx) -> None:
		""" Allows one or more members to join your channels.
		:param members: The members to allow. """

		members = await utils.get_mentions(message=ctx.message)
		member = ctx.author

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**Inform one or more members to allow, {member.mention}!**")

		user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot allow someone in it, {member.mention}!**")

		allowed = await self.handle_permissions(members, user_galaxy, ctx.guild)
	
		if not allowed:
			return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

		allowed_members = ', '.join(allowed)
		await ctx.send(f"**{allowed_members} {'have' if len(allowed) > 1 else 'has'} been allowed, {member.mention}!**")

	@galaxy.command(name="forbid", aliases=['prohibit'])
	async def _galaxy_forbid(self, ctx) -> None:
		""" Forbids one or more members from joining your channels.
		:param members: The members to forbid. """

		members = await utils.get_mentions(message=ctx.message)
		member = ctx.author

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**Inform one or more members to forbid, {member.mention}!**")

		user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot forbid someone from it, {member.mention}!**")

		forbid = await self.handle_permissions(members, user_galaxy, ctx.guild, allow=False)

		if not forbid:
			return await ctx.send(f"**For some reason, I couldn't forbid any of those members, {member.mention}!**")

		forbidden_members = ', '.join(forbid)

		await ctx.send(f"**{forbidden_members} {'have' if len(forbid) > 1 else 'has'} been forbidden, {member.mention}!**")

	# Other useful commands
	@galaxy.command(name="info", aliases=['creation', 'expiration'])
	async def _galaxy_info(self, ctx) -> None:
		""" Shows the creation and expiration time of the user's Galaxy Rooms. """

		author: discord.Member = ctx.author
		is_admin = ctx.channel.permissions_for(author).administrator

		user_galaxy = await self.get_galaxy_by_cat_id(ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send("**This is not a Galaxy Room!**")

		if user_galaxy[0] != author.id and not is_admin:
			return await ctx.send(f"**You cannot run this command outside your Galaxy Room, in case you have one, {author.mention}!**")

		member: discord.Member = discord.utils.get(ctx.guild.members, id=user_galaxy[0])
		if not member:
			return await ctx.send(f"**It looks like the owner of this Galaxy Room is not in the server anymore, {author.mention}!")

		user_ts = user_galaxy[6]
		auto_pay = True if user_galaxy[11] else False
		the_time = await utils.get_timestamp()
		deadline = user_ts + 1209600

		embed = discord.Embed(
			title=f"__{member.name}'s Rooms' Info__",
			description=f"""**Created at:** `{datetime.fromtimestamp(user_ts)}`
			**Expected expiration:** `{datetime.fromtimestamp(deadline)}`\n**Auto Pay:** `{auto_pay}`\n""",
			color=member.color,
			timestamp=ctx.message.created_at)

		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text="Requested")

		seconds_left = deadline - the_time
		if seconds_left >= 86400:
			embed.description += f"**Time left:** `{round(seconds_left/3600/24)} days left`"
		elif seconds_left >= 3600:
			embed.description += f"**Time left:** `{round(seconds_left/3600)} hours left`"
		elif seconds_left >= 60:
			embed.description += f"**Time left:** `{round(seconds_left/60)} minutes left`"
		else:
			embed.description += f"**Time left:** `{round(seconds_left)} seconds left`"

		await ctx.send(embed=embed)

	@galaxy.command(name="pay_rent", aliases=['pr', 'payrent', 'rent', 'renew'])
	async def _galaxy_pay_rent(self, ctx) -> None:
		""" Delays the user's Galaxy Rooms deletion by 14 days.
		
		* Price:
		- +250 for each Thread
		- +500 for the additional Voice Channel, if there is one.
		
		Max Rent Possible: 2500łł
		
		PS: You can either have an extra Voice Channel or up to 4 Threads. """

		if not ctx.guild:
			return await ctx.send("**Don't use it here!**")

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")
		
		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only run this command in your Galaxy Room, {member.mention}!**")

		user_ts = user_rooms[0]
		the_time = await utils.get_timestamp()
		seconds_left = (user_ts + 1209600) - the_time

		# Checks rooms deletion time
		if seconds_left > 172800:
			return await ctx.send(f"**You can only renew your rooms at least 2 days before their deletion time, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)
		money: int = await self.get_rent_price(len(txts), len(vcs))


		confirm = await ConfirmSkill(f"Are you sure you want to renew your Galaxy Room for `{money}łł`, {member.mention}?").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		# Checks if the user has money for it (1500-2000łł)
		SlothCurrency = self.client.get_cog('SlothCurrency')
		user_currency = await SlothCurrency.get_user_currency(member.id)
		if user_currency[0][1] >= money:
			await SlothCurrency.update_user_money(member.id, -money)
		else:
			return await ctx.send(f"**You don't have enough money to renew your rooms, {member.mention}!** `({money}łł)`")

		await self.increment_galaxy_ts(member.id, 1209600)
		await self.user_notified_no(member.id)
		await ctx.send(f"**{member.mention}, Galaxy Rooms renewed! `(-{money}łł)`**")

	async def get_rent_price(self, txts: int, vcs: int) -> int:
		""" Gets the rent price that the user has to pay, according to the amount of
		channels that they have in their Galaxy Room.
		:param txts: The amount of of text based channels the user has.
		:param vcs: The amount of of voice channels the user has. """

		money = 1500 # Minimum renting price
		money += (txts - 1) * 250
		money += (vcs - 1) * 500
		return money

	@galaxy.command(name="transfer_ownership", aliases=['transfer', 'to', 'transferownership'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_transfer_ownership(self, ctx, member: discord.Member = None) -> None:
		""" Transfer the Galaxy Room's ownership  to someone else.
		:param member: The member to transfer the Galaxy Room to.
		
		PS: Only the owner of the Galaxy Room and admins can use this. """

		if not ctx.guild:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send("**Don't use it here!**")

		author = ctx.author
		channel = ctx.channel

		if not member:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Please, inform a member, {author.mention}!**")

		if not (cat := channel.category):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**This is definitely not a Galaxy Room, {author.mention}!**")

		if not (galaxy_room := await self.get_galaxy_by_cat_id(cat.id)):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**This is not a Galaxy Room, {author.mention}!**")

		perms = channel.permissions_for(author)
		if author.id != galaxy_room[0] and not perms.administrator:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You don't have permission to do this, {author.mention}!**")
		
		if member.id == galaxy_room[0]:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You cannot transfer the Galaxy Room to the same owner, {author.mention}!**")

		if await self.get_galaxy_by_user_id(member.id):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You cannot transfer the Galaxy Room to {member.mention} because they have one already, {author.mention}!**")

		confirm = await ConfirmSkill(
			f"**Are you sure you want to transfer the ownership of this Galaxy Room from <@{galaxy_room[0]}> to {member.mention}, {author.mention}?**"
			).prompt(ctx)
		if not confirm:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Not deleting it then, {author.mention}!**")


		try:
			await self.update_galaxy_user(galaxy_room[0], member.id)
			await self.handle_permissions([member], galaxy_room, ctx.guild)
		except:
			ctx.command.reset_cooldown(ctx)
			await ctx.send(f"**Something went wrong with it, please contact an admin, {author.mention}!**")
		else:
			await ctx.send(f"**Successfully transferred the ownership of this Galaxy Room from <@{galaxy_room[0]}> to {member.mention}!**")

	@galaxy.command(name="close", aliases=['close_room', 'closeroom', 'kill', 'terminate', 'delete', 'del'])
	async def _galaxy_close(self, ctx) -> None:
		""" Deletes a Galaxy Room. """

		if not ctx.guild:
			return await ctx.send("**Don't use it here!**")

		member = ctx.author
		channel = ctx.channel

		if not (cat := channel.category):
			return await ctx.send(f"**This is definitely not a Galaxy Room, {member.mention}!**")

		if not (galaxy_room := await self.get_galaxy_by_cat_id(cat.id)):
			return await ctx.send(f"**This is not a Galaxy Room, {member.mention}!**")

		perms = channel.permissions_for(member)
		if member.id != galaxy_room[0] and not perms.administrator:
			return await ctx.send(f"**You don't have permission to do this, {member.mention}!**")

		confirm = await ConfirmSkill(f"**Are you sure you want to close this Galaxy Room, {member.mention}!**").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not deleting it then, {member.mention}!**")

		member = self.client.get_user(galaxy_room[0])
		rooms = [
			discord.utils.get(channel.guild.voice_channels, id=galaxy_room[2]),
			discord.utils.get(channel.guild.text_channels, id=galaxy_room[3]),
			discord.utils.get(channel.guild.voice_channels, id=galaxy_room[5]),
			discord.utils.get(channel.guild.categories, id=galaxy_room[1])
		]
		try:
			await self.delete_things(rooms)
			await member.send(f"**Hey! Your rooms got deleted!**")
		except Exception:
			pass
		finally:
			await self.delete_galaxy_by_cat_id(galaxy_room[1])

	async def order_rooms(self, user_rooms: List[int]) -> List[List[int]]:
		""" Orders the user's Galaxy Room channels by txt and vc.
		:param user_rooms: The user rooms. """

		vcs = [vc for vc in [user_rooms[7], user_rooms[8]] if vc is not None]
		txts = [txt for txt in [user_rooms[2], user_rooms[3], user_rooms[4], user_rooms[5], user_rooms[6]] if txt is not None]

		return vcs, txts

	async def order_rooms_default(self, user_rooms: List[int]) -> List[List[int]]:
		""" Orders the user's Galaxy Room channels by txt and vc.
		:param user_rooms: The user rooms. """

		vcs = [vc for vc in [user_rooms[2], user_rooms[5]] if vc is not None]
		txts = [txt for txt in [user_rooms[3], user_rooms[4], user_rooms[8], user_rooms[9], user_rooms[10]] if txt is not None]

		return vcs, txts

	@galaxy.group(name="add_channel", aliases=['ac'])
	async def _galaxy_add_channel(self, ctx) -> None:
		""" Adds either a Text or a Voice Channel to
		the user's Galaxy Room. """

		if ctx.invoked_subcommand:
			return

		cmd = ctx.command
		prefix = self.client.command_prefix
		subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands]

		subcommands = '\n'.join(subcommands)
		embed = discord.Embed(
		  title="Subcommads",
		  description=f"```apache\n{subcommands}```",
		  color=ctx.author.color,
		  timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)

	@_galaxy_add_channel.command(name='thread', aliases=['th', 'thread_channel', 'text', 'txt', 'text_channel'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_add_channel_thread(self, ctx, *, name: str = None) -> None:
		""" Adds a Text Channel.
		:param name: The name of the Text Channel. """

		member = ctx.author

		if not name:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

		if len(name) > 20:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send("**Please inform a name having 1-20 characters!**")

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)

		if len(vcs) == 2:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You cannot add threads because you chose to have a second Voice Channel instead, {member.mention}!**")

		if len(txts) >= 5:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You cannot add more thread channels, {member.mention}!**")

		if len(vcs) + len(txts) >= 6:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Rooms, {member.mention}!**")

		money: int = await self.get_rent_price(len(txts)+1, len(vcs))
		confirm = await ConfirmSkill(
			f"**Do you want to add an extra `Thread` channel for `250łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
			).prompt(ctx)
		if not confirm:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Not doing it then, {member.mention}!**")


		SlothCurrency = self.client.get_cog('SlothCurrency')
		if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
			return await member.send( 
				embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
				view=view)

		if user_currency[0][1] < 250:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send("**You don't have enough money to buy this service!**")

		channel = discord.utils.get(ctx.guild.text_channels, id=user_rooms[2])
			
		if not (thread := await self.try_to_create(kind='thread', channel=channel, owner=member, name=name, auto_archive_duration=10080)):
			return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

		await self.update_txt(user_id=member.id, position=len(txts)+1, channel_id=thread.id)
		# await self.update_txt_2(member.id, thread.id)
		await SlothCurrency.update_user_money(member.id, -250)
		await ctx.send(f"**Thread Channel created, {member.mention}!** ({thread.mention})")
		await self.log_smartroom_creation(member, 'galaxy', created=False, thread=thread)

	@_galaxy_add_channel.command(name='voice', aliases=['vc', 'voice_channel'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_add_channel_voice(self, ctx, limit: int = None, *, name: str = None) -> None:
		""" Adds a Voice Channel.
		:param limit: The user limit of the Voice Cchannel.
		:param name: The name of the Voice Channel. """

		member = ctx.author

		if limit is None:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Please, inform a user limit for your vc, {member.mention}!** `(0 for limitless)`")

		if not name:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

		if len(name) > 20:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send("**Please inform a name having 1-20 characters!**")

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)
		money: int = await self.get_rent_price(len(txts), len(vcs)+1)

		if len(vcs) == 2:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You cannot add more voice channels, {member.mention}!**")
			
		if len(vcs) + len(txts) >= 3:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Room, {member.mention}!**")


		confirm = await ConfirmSkill(
			f"**Do you want to add an extra `Voice Channel` for `500łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
			).prompt(ctx)
		if not confirm:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**Not doing it then, {member.mention}!**")


		SlothCurrency = self.client.get_cog('SlothCurrency')
		if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
			return await member.send( 
				embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
				view=view)

		if user_currency[0][1] < 500:
			ctx.command.reset_cooldown(ctx)
			return await ctx.send("**You don't have enough money to buy this service!**")


		cat = discord.utils.get(ctx.guild.categories, id=user_rooms[1])
			
		if not (vc := await self.try_to_create(kind='voice', category=cat, name=name, user_limit=limit)):
			return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

		await self.update_vc_2(member.id, vc.id)
		await SlothCurrency.update_user_money(member.id, -500)
		await ctx.send(f"**Voice Channel created, {member.mention}!** ({vc.mention})")
		await self.log_smartroom_creation(member, 'galaxy', created=False, vc=vc)

	@galaxy.group(name="delete_channel", aliases=['dc', 'deletechannel', 'remove_channel', 'removechannel', 'rc'])
	async def _galaxy_delete_channel(self, ctx) -> None:
		""" Deletes either a Text or a Voice Channel from
		the user's Galaxy Room. """

		if ctx.invoked_subcommand:
			return

		cmd = ctx.command
		prefix = self.client.command_prefix
		subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands]

		subcommands = '\n'.join(subcommands)
		embed = discord.Embed(
		  title="Subcommads",
		  description=f"```apache\n{subcommands}```",
		  color=ctx.author.color,
		  timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)

	@_galaxy_delete_channel.command(name='thread', aliases=['thread_channel', 'th', 'thr', 'text', 'txt', 'text_channel'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_delete_channel_thread(self, ctx) -> None:
		""" Deletes the user's second Text Channel from their Galaxy Room. """

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")


		vcs, txts = await self.order_rooms(user_rooms)
		money: int = await self.get_rent_price(len(txts)-1, len(vcs))

		if len(txts) <= 1:
			return await ctx.send(f"**You don't have a Thread to delete, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Are you sure you want to delete <#{txts[1]}>, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
			).prompt(ctx)

		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		try:
			await self.update_txt(user_id=member.id, position=len(txts))
		except:
			await ctx.send(f"**For some reason I couldn't delete it, try again, {member.mention}!**")
		else:
			if txt := discord.utils.get(ctx.guild.threads, id=txts[len(txts)-1]):
				await self.delete_things([txt])
			elif txt := discord.utils.get(ctx.guild.text_channels, id=txts[len(txts)-1]):
				await self.delete_things([txt])

			await ctx.send(f"**Text Channel deleted, {member.mention}!**")
		
	@_galaxy_delete_channel.command(name='voice', aliases=['vc', 'voice_channel'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_delete_channel_voice(self, ctx) -> None:
		""" Deletes the user's second Voice Channel from their Galaxy Room. """

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)
		money: int = await self.get_rent_price(len(txts), len(vcs)-1)

		if len(vcs) != 2:
			return await ctx.send(f"**You don't have a second Voice Channel to delete, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Are you sure you want to delete <#{vcs[1]}>, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
			).prompt(ctx)
		
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		try:
			await self.update_vc_2(member.id)
		except:
			await ctx.send(f"**For some reason I couldn't delete it, try again, {member.mention}!**")
		else:
			if vc := discord.utils.get(ctx.guild.channels, id=vcs[1]):
				await self.delete_things([vc])

			await ctx.send(f"**Voice Channel deleted, {member.mention}!**")

	@galaxy.command(name="allow_tribe", aliases=['at', 'permit_tribe', 'add_tribe', 'allowtribe', 'permittribe', 'addtribe'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_allow_tribe(self, ctx) -> None:
		""" Allows your Tribe members into your Galaxy Room.  """

		member = ctx.author

		user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot allow people in it, {member.mention}!**")

		SlothClass = self.client.get_cog('SlothClass')
		user_tribe = await SlothClass.get_tribe_info_by_user_id(member.id)
		if not user_tribe['name']:
			return await ctx.send(f"**You don't even have a tribe, you cannot do this, {member.mention}!**")

		members: List[List[Union[int, str]]] = await SlothClass.get_tribe_members(tribe_name=user_tribe['name'])
		members: List[discord.Member] = [m for m_id in members if (m := discord.utils.get(ctx.guild.members, id=m_id[0]))]

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**You don't have members in your tribe, {member.mention}!**")

		async with ctx.typing():
			allowed = await self.handle_permissions(members, user_galaxy, ctx.guild)

			if not allowed:
				return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

			text: str = "**{lendisa} {subjplural} from {tribe_name} {verbplural} been allowed, {mention}!**".format(
				lendisa=len(allowed),
				subjplural='people' if len(allowed) > 1 else 'person',
				tribe_name=user_tribe['name'],
				verbplural='have' if len(allowed) > 1 else 'has',
				mention=member.mention)

			await ctx.send(text)

	@galaxy.command(name="forbid_tribe", aliases=[
		'dt', 'disallow_tribe', 'delete_tribe', 'removetribe', 'disallowtribe', 'deletetribe', 'deltribe',
		'forbidtribe', 'remove_tribe', 'ft'])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def _galaxy_remove_tribe(self, ctx) -> None:
		""" Removes your Tribe members from your Galaxy Room.. """

		member = ctx.author

		user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot allow people in it, {member.mention}!**")

		SlothClass = self.client.get_cog('SlothClass')
		user_tribe = await SlothClass.get_tribe_info_by_user_id(member.id)
		if not user_tribe['name']:
			return await ctx.send(f"**You don't even have a tribe, you cannot do this, {member.mention}!**")

		members: List[List[Union[int, str]]]  = await SlothClass.get_tribe_members(tribe_name=user_tribe['name'])
		members: List[discord.Member] = [m for m_id in members if (m := discord.utils.get(ctx.guild.members, id=m_id[0]))]

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**You don't have members in your tribe, {member.mention}!**")

		async with ctx.typing():
			disallowed = await self.handle_permissions(members, user_galaxy, ctx.guild, allow=False)
		
			if not disallowed:
				return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

			text: str = "**{lendisa} {subjplural} from {tribe_name} {verbplural} been disallowed, {mention}!**".format(
				lendisa=len(disallowed),
				subjplural='people' if len(disallowed) > 1 else 'person',
				tribe_name=user_tribe['name'],
				verbplural='have' if len(disallowed) > 1 else 'has',
				mention=member.mention)

			await ctx.send(text)

	# Creates a smartroom manually
	@commands.command(aliases=['csr'])
	async def create_smartroom(self, ctx, type: int, limit: int, *, name: str) -> None:
		""":param type: The type of smart room (1-Basic / 2-Premium)
		:param size: The size of the smart room (0-25)
		:param name: The name of the smart room"""

		if not type:
			return await ctx.send("**Please, inform the type of the room (1-Basic 5🍃/ 2-Premium 100🍃)**")

		if not limit:
			return await ctx.send("**Please, inform the limit of the voice channel**")

		if not name:
			return await ctx.send("**Please, inform the name of the room**")

		else:
			if len(name) < 1 or len(name) > 30:
				return await ctx.send("**The name of the room must have between 1 and 30 characters**")

		member = ctx.message.author
		if type == 1:
			price = 5
		elif type == 2:
			price = 100

		# Checks if the user has money for it
		user_currency = await SlothCurrency.get_user_currency(member, member.id)
		if not user_currency:
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://discord.languagesloth.com/profile/update"))
			return await ctx.send( 
				embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://discord.languagesloth.com/profile/update) to create one, or in the button below!**"),
				view=view)

		if user_currency[0][1] < price:
			return await ctx.send("**You don't have enough money to buy this service!**")

		confirm = await ConfirmSkill(f"Would you like to create this smart room for {price} 🍃?`, {member.mention}?").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		# Gets the CreateSmartRoom category, creates the VC and text channel and tries to move the user to there

		creations = []
		failed = False

		the_category_test = discord.utils.get(member.guild.categories, id=self.cat_id)

		if vc_channel := await self.try_to_create(kind='voice', category=the_category_test, name=name, user_limit=limit):
			creations.append(vc_channel)
			await vc_channel.edit(sync_permissions=True)
		else:
			failed = True

		if type == 2:
			if txt_channel := await self.try_to_create(kind='text', category=the_category_test, name=name):
				creations.append(txt_channel)
				await txt_channel.edit(sync_permissions=True)
			else:
				failed = True

		# Checks whether there are failed creations, if so, delete the channels
		if failed:
			await self.delete_things(creations)
			return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")


		# Puts the channels ids in the database
		if type == 2:
			await self.insert_premium_vc(member.id, vc_channel.id, txt_channel.id)

		await SlothCurrency.update_user_money(member, member.id, -price)
		await ctx.send(f"**Your smartroom {vc_channel.mention} has been created**", delete_after=60)

		try:
			await member.move_to(vc_channel)
		except:
			await ctx.send("**You cannot be moved because you are not in a Voice-Channel! You have one minute to join the room before it gets deleted together with the text channel.**", delete_after=60)
			await asyncio.sleep(60)
			if len(vc_channel.members) == 0:
				await vc_channel.delete()
				if type == 2:
					await txt_channel.delete()


	async def log_smartroom_creation(self, member: discord.Member, room_type: str, created: bool = True, **data) -> None:
		""" Logs the creation of a SmartRoom.
		:param ctx: The context of the command.
		:param room_type: The type of room to log.
		:param data: The key-word arguments. """

		current_time = await utils.get_time_now()

		embed = discord.Embed(
			title=f"__SmartRoom {'Created' if created else 'Edited'}__",
			description=f"**Type:** `{room_type}`\n**User ID:** {member.id}",
			color=member.color,
			timestamp=current_time
		)
		vc_emoji = '<:vc:914947524178116649>'
		txt_emoji = '<:txt:975033834166972496>'
		cat_emoji = '📁'
		thr_emoji = '<:thr:975056831271551047>'

		if room_type == 'basic':
			embed.add_field(name=f"{vc_emoji} Voice Channel:", value=f"Name: {data['vc'].name} ({data['vc'].id})")

		elif room_type == 'premium':
			embed.add_field(name=f"{vc_emoji} Voice Channel:", value=f"Name: {data['vc'].name} ({data['vc'].id})")
			embed.add_field(name=f"{txt_emoji} Text Channel:", value=f"Name: {data['txt'].name} ({data['txt'].id})")

		elif room_type == 'galaxy':
			if created:
				embed.add_field(name=f"{cat_emoji} Category:", value=f"Name: {data['cat'].name} ({data['cat'].id})")
				embed.add_field(name=f"{vc_emoji} Voice Channel:", value=f"Name: {data['vc'].name} ({data['vc'].id})")
				embed.add_field(name=f"{txt_emoji} Text Channel:", value=f"Name: {data['txt'].name} ({data['txt'].id})")
			else:
				if thr := data.get("thread"):
					embed.add_field(name=f"{thr_emoji} Thread Channel:", value=f"Name: {thr.name} ({thr.id})")
				elif vc := data.get("vc"):
					embed.add_field(name=f"{vc_emoji} Voice Channel:", value=f"Name: {vc.name} ({vc.id})")


		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text=f"Created by: {member}", icon_url=member.display_avatar)

		log_channel: discord.TextChannel = discord.utils.get(member.guild.text_channels, id=int(os.getenv("SMART_ROOM_CHANNEL_LOG_ID", 123)))
		await log_channel.send(embed=embed)

	@galaxy.command(name="auto_pay", aliases=['ap', 'autopay', 'pay_auto', 'payauto', 'ar', 'auto_renew', 'autorenew'])
	async def _galaxy_auto_pay(self, ctx) -> None:
		""" Puts the Galaxy Room into the auto pay mode. """

		if not ctx.guild:
			return await ctx.send("**Don't use it here!**")

		member = ctx.author

		user_galaxy = await self.get_galaxy_by_cat_id(ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send("**This is not a Galaxy Room!**")

		if user_galaxy[0] != member.id:
			return await ctx.send(f"**You cannot run this command outside your Galaxy Room, in case you have one, {member.mention}!**")

		auto_pay_int = user_galaxy[11]
		auto_pay = 'on' if auto_pay_int else 'off'
		reverse_auto_pay = 'off' if auto_pay_int else 'on'

		confirm = await ConfirmSkill(f"Your Galaxy Room's auto pay mode is currently turned `{auto_pay}`, do you wanna turn it `{reverse_auto_pay}`, {member.mention}?").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		await self.update_galaxy_auto_pay(member.id, not auto_pay_int)
		await self.user_notified_no(member.id)
			
		await ctx.send(f"**Your Galaxy Room's auto pay mode has been turned `{reverse_auto_pay}`, {member.mention}!**")

def setup(client):
	""" Cog's setup function. """

	client.add_cog(CreateSmartRoom(client))
