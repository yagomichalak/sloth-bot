import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio
from PIL import Image, ImageFont, ImageDraw
import os
from cogs.slothcurrency import SlothCurrency
from mysqldb import *
from typing import List, Union, Callable, Any
from extra.menu import ConfirmSkill


class CreateSmartRoom(commands.Cog):
	""" A cog related to the creation of a custom voice channel. """

	def __init__(self, client):
		""" Class initializing method. """

		self.client = client
		self.vc_id = int(os.getenv('CREATE_SMART_ROOM_VC_ID'))
		self.cat_id = int(os.getenv('CREATE_SMART_ROOM_CAT_ID'))

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

		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()

		# Looks for rooms that are soon going to be deleted (Danger zone)
		danger_rooms = await self.get_all_galaxy_rooms_in_danger_zone(the_time)
		for droom in danger_rooms:
			member = self.client.get_user(droom[0])
			embed = discord.Embed(
				title="__Galaxy Rooms in Danger Zone__",
				description=(
					"Your Galaxy rooms will be deleted within two days, in case you wanna keep them,"
					" consider renewing them for `1500łł` (2 channels) or for `2000łł` (3 channels) by using the **z!pay_rent** command in any of your rooms!"
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
			epoch = datetime.utcfromtimestamp(0)
			the_time = (datetime.utcnow() - epoch).total_seconds()
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
				return await member.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

			if user_currency[0][1] < 5:
				return await member.send("**You don't have enough money to buy this service!**")

			# Gets the CreateSmartRoom category, creates the VC and tries to move the user to there
			the_category_test = discord.utils.get(member.guild.categories, id=self.cat_id)

			if not (creation := await self.try_to_create(kind='voice', category=the_category_test, name=name, user_limit=limit)):
				return await member.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

			await SlothCurrency.update_user_money(member, member.id, -5)
			await member.send(f"**You've been charged `5łł`!**")

			await member.send(file=discord.File('./images/smart_vc/created.png'))
			try:
				await member.move_to(creation)
			except discord.errors.HTTPException:
				await member.send("**You cannot be moved because you are not in a Voice-Channel!**")
				await creation.delete()
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
				return await member.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

			if user_currency[0][1] < 100:
				return await member.send("**You don't have enough money to buy this service!**")

			# Gets the CreateSmartRoom category, creates the VC and text channel and tries to move the user to there

			creations = []
			failed = False

			the_category_test = discord.utils.get(member.guild.categories, id=self.cat_id)

			if vc_channel := await self.try_to_create(kind='voice', category=the_category_test, name=name, user_limit=limit):
				creations.append(vc_channel)
			else:
				failed = True

			if txt_channel := await self.try_to_create(kind='text', category=the_category_test, name=name):
				creations.append(txt_channel)
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
			finally:
				try:
					os.remove(f'./images/smart_vc/user_previews/{member.id}.png')
				except Exception:
					pass

		else:
			return

	async def try_to_create(self, kind: str, category: discord.CategoryChannel = None, guild: discord.Guild = None, **kwargs: Any) -> Union[bool, Any]:
		""" Try to create something.
		:param thing: The thing to try to create.
		:param kind: Kind of creation. (txt, vc, cat)
		:param category: The category in which it will be created. (Optional)
		:param guild: The guild in which it will be created in. (Required for categories)
		:param kwargs: The arguments to inform the creations. """

		try:
			if kind == 'text':
				the_thing = await category.create_text_channel(**kwargs)
			elif kind == 'voice':
				the_thing = await category.create_voice_channel(**kwargs)
			elif kind == 'category':
				the_thing = await guild.create_category(**kwargs)
		except:
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

			# Checks if the user has money (1500łł)
			user_currency = await SlothCurrency.get_user_currency(member, member.id)
			if not user_currency:
				return await member.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

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
			epoch = datetime.utcfromtimestamp(0)
			the_time = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_galaxy_vc(member.id, the_cat.id, vc_channel.id, txt_channel1.id, the_time)
			await member.send(file=discord.File('./images/smart_vc/created.png'))
			try:
				await member.move_to(vc_channel)
			except discord.errors.HTTPException:
				await member.send("**You cannot be moved because you are not in a Voice-Channel, but your channels and category will remain alive nonetheless! 👍**")
			finally:
				try:
					os.remove(f'./images/smart_vc/user_previews/{member.id}.png')
				except Exception:
					pass

				await member.send("""**Congrats you created a galaxy room** :tada:
Here are some rules and rights:

1) Your galaxy room costs **1500** :leaves: every **14 days**. You will get a reminder to pay your rent in the galaxy room a few days before it's due. If you don't pay using the **z!renew** command, the galaxy room gets deleted. 

2) You can **allow** or **unallow** any user to see and use your galaxy room by using the command **z!allow @User/ID** and **z!forbid @User/ID**

3) You have to allow a minimum of **10** users. (Bots or admins do not count) 

4) You can add an additional channel for **500** :leaves: by writing **z!agc text (name of the channel)**  or **z!agc voice (user limit) (name of the channel)** for a voice channel. 
You can only add 1 additional channel. Voice **OR** Text.""")

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

	# Database commands

	# Premium related functions
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_premium_vc(self, ctx) -> None:
		""" (ADM) Creates the PremiumVc table. """

		if await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ already exists!**")

		mycursor, db = await the_database()
		await mycursor.execute("CREATE TABLE PremiumVc (user_id BIGINT, user_vc BIGINT, user_txt BIGINT)")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __PremiumVc__ created!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_premium_vc(self, ctx) -> None:
		""" (ADM) Drops the PremiumVc table. """

		if not await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ doesn't exist!**")

		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE PremiumVc")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __PremiumVc__ dropped!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_premium_vc(self, ctx) -> None:
		""" (ADM) Resets the PremiumVc table. """

		if not await self.table_premium_vc_exists():
			return await ctx.send("**Table __PremiumVc__ doesn't exist yet!**")

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM PremiumVc")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __PremiumVc__ reset!**")

	async def table_premium_vc_exists(self) -> bool:
		""" Checks whether the PremiumVc table exists. """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'PremiumVc'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True

	async def insert_premium_vc(self, user_id: int, user_vc: int, user_txt: int) -> None:
		""" Inserts a Premium Room.
		:param user_id: The owner ID.
		:param user_vc: The voice channel ID.
		:param user_txt: The text channel ID. """

		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO PremiumVc (user_id, user_vc, user_txt) VALUES (%s, %s, %s)", (user_id, user_vc, user_txt))
		await db.commit()
		await mycursor.close()

	async def get_premium_vc(self, user_vc: int) -> List[List[int]]:
		""" Gets a Premium Room by voice channel ID.
		:param user_vc: The voice channel ID. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM PremiumVc WHERE user_vc = %s", (user_vc,))
		premium_vc = await mycursor.fetchall()
		await mycursor.close()
		return premium_vc

	async def delete_premium_vc(self, user_id: int, user_vc: int) -> None:
		""" Deletes a Premium Room by voice channel ID.
		:param user_id: The owner ID.
		:param user_vc: The voice channel ID. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM PremiumVc WHERE user_id = %s and user_vc = %s", (user_id, user_vc))
		await db.commit()
		await mycursor.close()

	# Galaxy related functions
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Creates the GalaxyVc table. """

		if await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ already exists!**")

		mycursor, db = await the_database()
		await mycursor.execute("""
			CREATE TABLE GalaxyVc (
			user_id BIGINT, user_cat BIGINT, user_vc BIGINT, 
			user_txt1 BIGINT, user_txt2 BIGINT, user_vc2 BIGINT,
			user_ts BIGINT, user_notified VARCHAR(3) default 'no')""")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __GalaxyVc__ created!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Drops the GalaxyVc table. """

		if not await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ doesn't exist!**")

		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE GalaxyVc")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __GalaxyVc__ dropped!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_galaxy_vc(self, ctx) -> None:
		""" (ADM) Resets the GalaxyVc table. """

		if not await self.table_galaxy_vc_exists():
			return await ctx.send("**Table __GalaxyVc__ doesn't exist yet!**")

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM GalaxyVc")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __GalaxyVc__ reset!**")

	async def table_galaxy_vc_exists(self) -> bool:
		""" Checks whether the GalaxyVc table exists. """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'GalaxyVc'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True

	async def insert_galaxy_vc(self, user_id: int, user_cat: int, user_vc: int, user_txt1: int, user_ts: int) -> None:
		""" Inserts a Galaxy Room.
		:param user_id: The owner ID.
		:param user_cat: The category ID.
		:param user_vc: The Galaxy Room's main voice channel ID.
		:param user_txt1: The ID of the first text channel.
		:param user_txt2: The ID of the second text channel.
		:param user_ts: The current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute(
			"""
			INSERT INTO GalaxyVc (user_id, user_cat, user_vc, user_txt1, user_ts)
			VALUES (%s, %s, %s, %s, %s)""", (user_id, user_cat, user_vc, user_txt1, user_ts)
			)
		await db.commit()
		await mycursor.close()

	async def get_galaxy_txt(self, user_id: int, user_cat: int) -> List[List[int]]:
		""" Gets the Galaxy Room's channels by category ID.
		:param user_id: The ID of the owner of the channels.
		:param user_cat: The ID of the category. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM GalaxyVc WHERE user_id = %s and user_cat = %s", (user_id, user_cat))
		galaxy_vc = await mycursor.fetchall()
		await mycursor.close()
		return galaxy_vc

	async def get_galaxy_by_cat_id(self, cat_id: int) -> List[int]:
		""" Gets a Galaxy Room by category ID.
		:param cat_id: The category ID. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM GalaxyVc WHERE user_cat = %s", (cat_id,))
		galaxy_vc = await mycursor.fetchone()
		await mycursor.close()
		return galaxy_vc

	async def get_all_galaxy_rooms(self, the_time: int):
		""" Get all expired Galaxy Rooms.
		:param the_time The current time. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM GalaxyVc WHERE %s - user_ts >= 1209600", (the_time,))
		rooms = await mycursor.fetchall()
		await mycursor.close()
		return rooms

	async def delete_galaxy_vc(self, user_id: int, user_vc: int) -> None:
		""" Deletes a a Galaxy Room by voice channel ID.
		:param user_id: The user ID.
		:param user_vc: The voice channel ID. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM GalaxyVc WHERE user_id = %s and user_vc = %s", (user_id, user_vc))
		await db.commit()
		await mycursor.close()

	async def delete_galaxy_by_cat_id(self, cat_id: int) -> None:
		""" Deletes a a Galaxy Room by category ID.
		:param cat_id: The category ID. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM GalaxyVc WHERE user_cat = %s", (cat_id,))
		await db.commit()
		await mycursor.close()

	@commands.command(aliases=['permit'])
	async def allow(self, ctx) -> None:
		""" Allows one or more members to join your channels.
		:param members: The members to allow. """

		members = await CreateSmartRoom.get_mentions(message=ctx.message)
		member = ctx.author

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**Inform one or more members to allow, {member.mention}!**")

		user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot allow someone in it, {member.mention}!**")

		channels = [
			discord.utils.get(ctx.guild.categories, id=user_galaxy[0][1]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][2]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][3]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][4]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][5])
		]
		allowed = []

		for m in members:
			try:
				for c in channels:
					await c.set_permissions(
						m, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)

			except:
				pass
			else:
				allowed.append(m.mention)

		if not allowed:
			return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

		allowed = ', '.join(allowed)
		await ctx.send(f"**{allowed} {'have' if len(allowed) > 1 else 'has'} been allowed, {member.mention}!**")

	@staticmethod
	async def get_mentions(message: discord.Message) -> List[discord.Member]:
		""" Get mentions from a specific message.
		:param message: The message to get the mentions from. """

		guild = message.guild

		members = [
			m for word in message.content.split()
			if word.isdigit() and (m := discord.utils.get(guild.members, id=int(word)))
			or (m := discord.utils.get(guild.members, name=str(word)))
			or (m := discord.utils.get(guild.members, nick=str(word)))
			or (m := discord.utils.get(guild.members, display_name=str(word)))
		]
		members.extend(message.mentions)
		members = list(set(members))

		return members

	@staticmethod
	async def get_voice_channel_mentions(message: discord.Message) -> List[discord.VoiceChannel]:
		""" Get voice channel mentions from a specific message.
		:param message: The message to get the mentions from. """

		guild = message.guild

		channel_mentions = [
			m for word in message.content.split()
			if word.isdigit() and (m := discord.utils.get(guild.voice_channels, id=int(word)))
			or (m := discord.utils.get(guild.voice_channels, name=str(word)))
		]

		channel_mentions.extend(list(map(lambda c: isinstance(c, discord.VoiceChannel), message.channel_mentions)))
		channel_mentions = list(set(channel_mentions))

		return channel_mentions

	@commands.command(aliases=['prohibit'])
	async def forbid(self, ctx) -> None:
		""" Forbids one or more members from joining your channels.
		:param members: The members to forbid. """

		members = await CreateSmartRoom.get_mentions(message=ctx.message)
		member = ctx.author

		if member in members:
			members.remove(member)

		if not members:
			return await ctx.send(f"**Inform one or more members to forbid, {member.mention}!**")

		user_galaxy = await self.get_galaxy_txt(ctx.author.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send(f"**This is not your room, so you cannot forbid someone from it, {member.mention}!**")

		channels = [
			discord.utils.get(ctx.guild.categories, id=user_galaxy[0][1]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][2]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][3]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][4]),
			discord.utils.get(ctx.guild.channels, id=user_galaxy[0][5])
		]
		forbid = []

		for m in members:
			try:
				for c in channels:
					await c.set_permissions(
						m, read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)
			except:
				pass
			else:
				forbid.append(m.mention)

		if not forbid:
			return await ctx.send(f"**For some reason, I couldn't forbid any of those members, {member.mention}!**")

		forbid = ', '.join(forbid)

		await ctx.send(f"**{forbid} {'have' if len(forbid) > 1 else 'has'} been forbidden, {member.mention}!**")

	async def get_user_vc_timestamp(self, user_id: int, the_time: int) -> int:
		""" Gets the user voice channel timestamp, and insert them into the database
		in case they are not there yet.
		:param user_id: The ID of the user.
		:param the_time: The current time. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserVCstamp WHERE user_id = %s", (user_id,))
		user = await mycursor.fetchall()
		await mycursor.close()

		if not user:
			await self.insert_user_vc(user_id, the_time)
			return await self.get_user_vc_timestamp(user_id, the_time)

		return user[0][1]

	async def insert_user_vc(self, user_id: int, the_time: int) -> None:
		""" Inserts a user into the UserVCstamp table.
		:param user_id: The ID of the user.
		:param the_time: The current time. """

		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO UserVCstamp (user_id, user_vc_ts) VALUES (%s, %s)", (user_id, the_time - 61))
		await db.commit()
		await mycursor.close()

	async def update_user_vc_ts(self, user_id: int, new_ts: int) -> None:
		""" Updates the user's voice channel timestamp.
		:param user_id: The ID of the user.
		:param new_ts: The new/current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserVCstamp SET user_vc_ts = %s WHERE user_id = %s", (new_ts, user_id))
		await db.commit()
		await mycursor.close()

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def create_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Creates the UserVcstamp table. """

		await ctx.message.delete()
		if await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ already exists!**")
		mycursor, db = await the_database()
		await mycursor.execute("CREATE TABLE UserVCstamp (user_id bigint, user_vc_ts bigint)")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserVCstamp__ created!**", delete_after=5)

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def drop_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Drops the UserVcstamp table. """

		await ctx.message.delete()
		if not await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ doesn't exist!**")
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserVCstamp")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserVCstamp__ dropped!**", delete_after=5)

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def reset_table_user_vc_ts(self, ctx) -> None:
		""" (ADM) Resets the UserVcstamp table. """

		await ctx.message.delete()
		if not await self.table_user_vc_ts_exists():
			return await ctx.send("**Table __UserVCstamp__ doesn't exist yet!**")
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserVCstamp")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserVCstamp__ reset!**", delete_after=5)

	async def table_user_vc_ts_exists(self) -> bool:
		""" Checks whether the UserVCstamp table exists. """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'UserVCstamp'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True

	# Other useful commands
	@commands.command(aliases=['creation', 'expiration'])
	async def galaxy_info(self, ctx) -> None:
		""" Shows the creation and expiration time of the user's Galaxy Rooms. """

		user_galaxy = await self.get_galaxy_txt(ctx.author.id, ctx.channel.category.id)
		if not user_galaxy:
			return await ctx.send("**You cannot run this command outside your rooms, in case you have them!**")

		user_ts = user_galaxy[0][6]
		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()
		deadline = user_ts + 1209600

		embed = discord.Embed(
			title=f"__{ctx.author.name}'s Rooms' Info__",
			description=f'''**Created at:** {datetime.utcfromtimestamp(user_ts)}
			**Expected expiration:** {datetime.utcfromtimestamp(deadline)}\n''',
			color=ctx.author.color,
			timestamp=ctx.message.created_at)

		embed.set_thumbnail(url=ctx.author.avatar_url)
		embed.set_footer(text="Requested")

		seconds_left = deadline - the_time
		if seconds_left >= 86400:
			embed.description += f"**Time left:** {round(seconds_left/3600/24)} days left"
		elif seconds_left >= 3600:
			embed.description += f"**Time left:** {round(seconds_left/3600)} hours left"
		elif seconds_left >= 60:
			embed.description += f"**Time left:** {round(seconds_left/60)} minutes left"
		else:
			embed.description += f"**Time left:** {round(seconds_left)} seconds left"

		await ctx.send(embed=embed)

	@commands.command(aliases=['rent', 'renew'])
	async def pay_rent(self, ctx) -> None:
		""" Delays the user's Galaxy Rooms deletion by 14 days for 350łł (2 channels) or for 500łł (3 channels). """

		if not ctx.guild:
			return await ctx.send("**Don't use it here!**")

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")
		
		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only run this command in your Galaxy Room, {member.mention}!**")

		user_ts = user_rooms[0]
		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()
		seconds_left = (user_ts + 1209600) - the_time

		# Checks rooms deletion time
		if seconds_left > 172800:
			return await ctx.send(f"**You can only renew your rooms at least 2 days before their deletion time, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)
		money = 1500

		if len(vcs + txts) >= 3:
			money = 2000

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

	@commands.command(aliases=['cgr', 'close_galaxy', 'closegalaxy', 'delete_galaxy', 'deletegalaxy'])
	async def close_galaxy_room(self, ctx) -> None:
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
			discord.utils.get(channel.guild.channels, id=galaxy_room[5]),
			discord.utils.get(channel.guild.channels, id=galaxy_room[4]),
			discord.utils.get(channel.guild.channels, id=galaxy_room[3]),
			discord.utils.get(channel.guild.channels, id=galaxy_room[2]),
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

		vcs = [vc for vc in [user_rooms[4], user_rooms[5]] if vc is not None]
		txts = [txt for txt in [user_rooms[2], user_rooms[3]] if txt is not None]

		return vcs, txts


	@commands.group(aliases=['agc'])
	async def add_galaxy_channel(self, ctx) -> None:
		""" Adds either a Text or a Voice Channel to
		the user's Galaxy Room. """

		if ctx.invoked_subcommand:
			return

		cmd = self.client.get_command('add_galaxy_channel')
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

	@add_galaxy_channel.command(name='text', aliases=['txt', 'text_channel'])
	# @commands.cooldown(1, 60, commands.BucketType.user)
	async def add_text(self, ctx, *, name: str = None) -> None:
		""" Adds a Text Channel.
		:param name: The name of the Text Channel. """

		member = ctx.author

		if not name:
			return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

		if len(name) > 20:
			return await ctx.send("**Please inform a name having 1-20 characters!**")

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)

		if len(vcs) + len(txts) >= 3:
			return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Rooms, {member.mention}!**")

		if len(txts) >= 2:
			return await ctx.send(f"**You cannot add more text channels, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Do you want to add an extra `Text Channel` for `500łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `2000łł` in your next fortnight rents||"
			).prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")


		SlothCurrency = self.client.get_cog('SlothCurrency')
		if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
			return await ctx.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

		if user_currency[0][1] < 500:
			return await ctx.send("**You don't have enough money to buy this service!**")


		cat = discord.utils.get(ctx.guild.categories, id=user_rooms[1])
			
		if not (txt := await self.try_to_create(kind='text', category=cat, name=name)):
			return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

		await self.update_txt_2(member.id, txt.id)
		await SlothCurrency.update_user_money(member.id, -500)
		await ctx.send(f"**Text Channel created, {member.mention}!** ({txt.mention})")


	@add_galaxy_channel.command(name='voice', aliases=['vc', 'voice_channel'])
	# @commands.cooldown(1, 60, commands.BucketType.user)
	async def add_voice(self, ctx, limit: int = None, *, name: str = None) -> None:
		""" Adds a Voice Channel.
		:param: The user limit of the Voice Cchannel.
		:param name: The name of the Voice Channel. """

		member = ctx.author

		if limit is None:
			return await ctx.send(f"**Please, inform a user limit for your vc, {member.mention}!** `(0 for limitless)`")

		if not name:
			return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

		if len(name) > 20:
			return await ctx.send("**Please inform a name having 1-20 characters!**")

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, txts = await self.order_rooms(user_rooms)

		if len(vcs) + len(txts) >= 3:
			return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Rooms, {member.mention}!**")

		if len(vcs) >= 2:
			return await ctx.send(f"**You cannot add more voice channels, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Do you want to add an extra `Voice Channel` for `500łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `2000łł` in your next fortnight rents||"
			).prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")


		SlothCurrency = self.client.get_cog('SlothCurrency')
		if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
			return await ctx.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

		if user_currency[0][1] < 500:
			return await ctx.send("**You don't have enough money to buy this service!**")


		cat = discord.utils.get(ctx.guild.categories, id=user_rooms[1])
			
		if not (vc := await self.try_to_create(kind='voice', category=cat, name=name, limit=limit)):
			return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

		await self.update_vc_2(member.id, vc.id)
		await SlothCurrency.update_user_money(member.id, -500)
		await ctx.send(f"**Voice Channel created, {member.mention}!** ({vc.mention})")



	@commands.group(aliases=['dgc', 'remove_galaxy_channel', 'rgc'])
	async def delete_galaxy_channel(self, ctx) -> None:
		""" Deletes either a Text or a Voice Channel from
		the user's Galaxy Room. """

		if ctx.invoked_subcommand:
			return

		cmd = self.client.get_command('delete_galaxy_channel')
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

	@delete_galaxy_channel.command(name='text', aliases=['txt', 'text_channel'])
	# @commands.cooldown(1, 60, commands.BucketType.user)
	async def delete_text(self, ctx) -> None:
		""" Deletes the user's second Text Channel from their Galaxy Room. """

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")


		_, txts = await self.order_rooms(user_rooms)

		if len(txts) != 2:
			return await ctx.send(f"**You don't have a second Text Channel to delete, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Are you sure you want to delete <#{txts[1]}>, {member.mention}?**\n\n||From now on, you're gonna be charged `1500łł` in your next fortnight rents||"
			).prompt(ctx)

		if not confirm:
			return await ctx.send(f"**Not doing it then, {member.mention}!**")

		try:
			await self.update_txt_2(member.id)
		except:
			await ctx.send(f"**For some reason I couldn't delete it, try again, {member.mention}!**")
		else:
			if txt := discord.utils.get(ctx.guild.channels, id=txts[1]):
				await self.delete_things([txt])

			await ctx.send(f"**Text Channel deleted, {member.mention}!**")
		


	@delete_galaxy_channel.command(name='voice', aliases=['vc', 'voice_channel'])
	# @commands.cooldown(1, 60, commands.BucketType.user)
	async def delete_voice(self, ctx) -> None:
		""" Deletes the user's second Voice Channel from their Galaxy Room. """

		member = ctx.author

		if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
			return await ctx.send(f"**You don't have any Galaxy Rooms!**")

		if ctx.channel.id not in user_rooms:
			return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

		vcs, _ = await self.order_rooms(user_rooms)

		if len(vcs) != 2:
			return await ctx.send(f"**You don't have a second Voice Channel to delete, {member.mention}!**")

		confirm = await ConfirmSkill(
			f"**Are you sure you want to delete <#{vcs[1]}>, {member.mention}?**\n\n||From now on, you're gonna be charged `1500łł` in your next fortnight rents||"
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

	async def increment_galaxy_ts(self, user_id: int, addition: int) -> None:
		""" Increments a Galaxy Room's timestamp so it lasts longer.
		:param user_id: The ID of the owner of the Galaxy Room.
		:param addition: The amount of time to increment, in seconds. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE GalaxyVc SET user_ts = user_ts + %s WHERE user_id = %s", (addition, user_id))
		await db.commit()
		await mycursor.close()

	async def get_all_galaxy_rooms_in_danger_zone(self, the_time) -> None:
		""" Gets all Galaxy Rooms in the danger zone; at least 2 days from being deleted.
		:param the_time: The current time. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM GalaxyVc WHERE (user_ts + 1209600) - %s <= 172800 and user_notified = 'no'", (the_time,))
		danger_rooms = await mycursor.fetchall()
		await mycursor.close()
		return danger_rooms

	async def get_user_all_galaxy_rooms(self, user_id: int) -> List[int]:
		""" Checks whether a user has a Galaxy Room.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT user_ts, user_cat, user_txt1, user_txt2, user_vc, user_vc2 FROM GalaxyVc WHERE user_id = %s", (user_id,))
		user_rooms = await mycursor.fetchone()
		await mycursor.close()
		return user_rooms


	async def update_txt_2(self, user_id: int, txt2: int = None) -> None:
		""" Updates the user's second text channel value in the database.
		:param user_id: The user ID.
		:param txt2: The value for the second txt. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE GalaxyVc SET user_txt2 = %s WHERE user_id = %s", (txt2, user_id))
		await db.commit()
		await mycursor.close()

	async def update_vc_2(self, user_id: int, vc2: int = None) -> None:
		""" Updates the user's second voice channel value in the database.
		:param user_id: The user ID.
		:param vc2: The value for the second vc. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE GalaxyVc SET user_vc2 = %s WHERE user_id = %s", (vc2, user_id))
		await db.commit()
		await mycursor.close()


	async def user_notified_yes(self, user_id: int) -> None:
		""" Updates the the user notified status to 'yes'.
		:param user_id: The ID of the user. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE GalaxyVc SET user_notified = 'yes' WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	async def user_notified_no(self, user_id: int) -> None:
		""" Updates the the user notified status to 'no'.
		:param user_id: The ID of the user. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE GalaxyVc SET user_notified = 'no' WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	async def has_galaxy_rooms(self, user_id: int) -> bool:
		""" Checks whether a user has a Galaxy Room.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM GalaxyVc WHERE user_id = %s", (user_id,))
		user_rooms = await mycursor.fetchall()
		await mycursor.close()

		if user_rooms:
			return True
		else:
			return False


def setup(client):
	""" Cog's setup function. """

	client.add_cog(CreateSmartRoom(client))
