import discord
from discord.ext import commands, menus
from mysqldb import *
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
#import requests
import shutil
import asyncio
import aiohttp
from io import BytesIO
import glob
from itertools import cycle

from extra.menu import InventoryLoop
from typing import List, Dict, Tuple, Union, Any

from extra.useful_variables import level_badges, flag_badges
from extra.gif_manager import GIF

shop_channels = [
int(os.getenv('BACKGROUND_ITEMS_CHANNEL_ID')), int(os.getenv('HAND_ITEMS_CHANNEL_ID')),
int(os.getenv('CLOTHES_ITEMS_CHANNEL_ID')), int(os.getenv('LIMITED_EDITION_ITEMS_CHANNEL_ID')),
int(os.getenv('HEAD_ITEMS_CHANNEL_ID')), int(os.getenv('LEG_ITEMS_CHANNEL_ID')),
int(os.getenv('PATREONS_CHANNEL_ID'))
]
afk_channel_id = int(os.getenv('AFK_CHANNEL_ID'))
booster_role_id = int(os.getenv('BOOSTER_ROLE_ID'))


gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
	# This is what solved the issues:
	gauth.GetFlow()
	gauth.flow.params.update({'access_type': 'offline'})
	gauth.flow.params.update({'approval_prompt': 'force'})

	# Authenticate if they're not there
	gauth.LocalWebserverAuth()
elif gauth.access_token_expired:

	# Refresh them if expired
	gauth.Refresh()
else:

	# Initialize the saved creds
	gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)


class SlothCurrency(commands.Cog):
	'''
	Sloth Currency commands.
	'''

	def __init__(self, client):
		self.client = client
		self.session = aiohttp.ClientSession()

	@commands.Cog.listener()
	async def on_ready(self):
		print("SlothCurrency cog is online!")
		# await self.download_update()
		#await self.text_download_update()

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.guild:
			return

		if message.author.bot:
			return
		if not await self.check_table_exist():
			return

		user_info = await self.get_user_activity_info(message.author.id)
		if not user_info:
			return await self.insert_user_server_activity(message.author.id, 1)

		await self.update_user_server_messages(message.author.id, 1)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if member.bot:
			return
		if not await self.check_table_exist():
			return

		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()

		user_info = await self.get_user_activity_info(member.id)
		if not user_info:
			return await self.insert_user_server_activity(member.id, 0, the_time)

		if not before.channel:
			return await self.update_user_server_timestamp(member.id, the_time)

		if not after.channel and not before.channel.id == afk_channel_id:
			old_time = user_info[0][3]
			addition = the_time - old_time
			await self.update_user_server_time(member.id, addition)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not payload.guild_id:
			return

		# Checks if it wasn't a bot's reaction
		if payload.member.bot:
			return
		
		# Takes off the reaction in the shop channel
		if payload.channel_id in shop_channels:
			guild = self.client.get_guild(payload.guild_id)
			channel = discord.utils.get(guild.channels, id=payload.channel_id)
		
			msg = await channel.fetch_message(payload.message_id)
			await msg.remove_reaction(payload.emoji.name, payload.member)

		# Checks if it was a reaction within the shop's channel
		if not payload.channel_id in shop_channels:
			return

		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()
		user = await self.get_user_currency(payload.user_id)
		if not user:
			return await payload.member.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))
			# await self.insert_user_currency(payload.user_id, the_time - 61)

		old_time = await self.get_user_currency(payload.member.id)
		if not the_time - old_time[0][2] >= 60:
			return await payload.member.send(
				f"**You're on a cooldown, try again in {round(60 - (the_time - old_time[0][2]))} seconds!**",
				delete_after=10)

		registered_items = await self.get_registered_items()
		for ri in registered_items:
			if ri[4] == payload.message_id:
				if str(payload.emoji) == ri[5]:
					user_have_item = await self.check_user_have_item(payload.user_id, ri[2])
					if user_have_item:
						return await payload.member.send(
							f"**You already have the item: __{ri[2]}__ in your inventory!**")
					else:
						return await self.try_to_buy_item(payload.user_id, ri[1], ri[2], ri[3], payload.guild_id,
														  the_time)

	# @commands.Cog.listener()
	# async def on_raw_reaction_remove(self, payload):
	#     if not payload.guild_id:
	#         return
	#     member = discord.utils.get(self.client.get_guild(payload.guild_id).members, id=payload.user_id)
	#     if member.bot:
	#         return

	# In-game commands
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def react(self, ctx, mid: discord.Message = None, reaction=None):
		'''
		(ADM) Makes the bot react onto a message.
		:param mid: The message ID.
		:param reaction: The reaction to add.
		'''
		await ctx.message.delete()
		if not reaction:
			return await ctx.send("**Inform a reaction!**", delete_after=3)
		if not mid:
			return await ctx.send("**Inform a message id!**", delete_after=3)
		await mid.add_reaction(reaction)

	@commands.command()
	async def inventory(self, ctx, member: discord.Member = None):
		'''
		Shows the member's item inventory.
		:param member: The member to show.
		'''
		await ctx.message.delete()
		if not member:
			member = discord.utils.get(ctx.guild.members, id=ctx.author.id)

		user_items = await self.get_user_items(member.id)

		if not user_items:
			return await ctx.send(f"**You don't have items to show, {ctx.author.mention}!**")

		the_menu = menus.MenuPages(source=InventoryLoop(user_items), clear_reactions_after=True)
		await the_menu.start(ctx)


	@commands.command()
	async def equip(self, ctx, *, item_name: str = None):
		'''
		Equips an item.
		:param item_name: The item to equip.
		'''
		await ctx.message.delete()
		if not item_name:
			return await ctx.send("**Inform an item to equip!**", delete_after=3)

		user_items = await self.get_user_items(ctx.author.id)
		for item in user_items:
			if str(item[1]) == item_name.title():
				if await self.check_user_can_equip(ctx.author.id, item_name.title()):
					await self.update_user_item_info(ctx.author.id, item_name, 'equipped')
					return await ctx.send(f"**{ctx.author.mention} equipped __{item_name.title()}__!**", delete_after=3)
				else:
					return await ctx.send(f"**You already have a __{item[3]}__ item equipped!**", delete_after=3)
		else:
			return await ctx.send(f"**You don't have an item named __{item_name.title()}__!**", delete_after=3)

	@commands.command()
	async def unequip(self, ctx, *, item_name: str = None):
		'''
		Unequips an item.
		:param item_name: The item to unequip
		'''
		await ctx.message.delete()
		if not item_name:
			return await ctx.send("**Inform an item to unequip!**", delete_after=3)

		user_items = await self.get_user_items(ctx.author.id)
		for item in user_items:
			if item[1] == item_name.title():
				if await self.check_user_can_unequip(ctx.author.id, item_name.lower()):
					await self.update_user_item_info(ctx.author.id, item_name.title(), 'unequipped')
					return await ctx.send(f"**{ctx.author.mention} unequipped __{item_name.title()}__!**",
										  delete_after=3)
				else:
					return await ctx.send(f"**The item __{item_name}__ is already unequipped!**", delete_after=3)
		else:
			return await ctx.send(f"**You don't have an item named __{item_name.title()}__!**", delete_after=3)

	# Database commands
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_user_items(self, ctx):
		'''
		(ADM) Creates the UserItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute(
			"CREATE TABLE UserItems (user_id bigint, item_name VARCHAR(30), enable VARCHAR(10), item_type VARCHAR(10))")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserItems* created!**", delete_after=3)

	@commands.has_permissions(administrator=True)
	@commands.command(hidden=True)
	async def drop_table_user_items(self, ctx):
		'''
		(ADM) Drops the UserItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserItems")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserItems* dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_user_items(self, ctx):
		'''
		(ADM) Resets the UserItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserItems")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserItems* reseted!**", delete_after=3)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def add_member(self, ctx, member: discord.Member = None, *, item_name: str = None):
		'''
		(ADM) Gives a member an item.
		:param member: The member to give the item.
		:param item_name: The name of the item.
		'''
		if not member:
			return await ctx.send("**Inform a member!**", delete_after=3)

		if not item_name:
			return await ctx.send("**Inform an item to add!**", delete_after=3)

		spec_item = await self.get_specific_register_item(item_name)
		if len(spec_item) == 0:
			return await ctx.send(f"**The item: __{item_name.title()}__ doesn't exist!**", delete_after=3)

		user_have_item = await self.get_user_specific_item(member.id, item_name)
		if len(user_have_item) == 0:
			await self.insert_user_item(member.id, item_name, 'unequipped', spec_item[0][1].lower())
			return await ctx.send(f"**{item_name.title()} given to {member.name}!**", delete_after=3)
		else:
			return await ctx.send(f"**{member.name} already have that item!**", delete_after=3)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def remove_member_item(self, ctx, member: discord.Member = None, *, item_name: str = None):
		'''
		(ADM) Removes an item from the member.
		:param member: The member to remove the item.
		:param item_name: The name of the item.
		'''
		if not member:
			return await ctx.send("**Inform a member!**", delete_after=3)

		if not item_name:
			return await ctx.send("**Inform an item to remove!**", delete_after=3)

		user_have_item = await self.get_user_specific_item(member.id, item_name)
		if len(user_have_item) != 0:
			await self.remove_user_item(member.id, item_name)
			return await ctx.send(f"**{item_name.title()} taken from {member.name}!**", delete_after=3)
		else:
			return await ctx.send(f"**{member.name} doesn't have that item!**", delete_after=3)

	async def insert_user_item(self, user_id: int, item_name: str, enable: str, item_type: str):
		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO UserItems (user_id, item_name, enable, item_type) VALUES (%s, %s, %s, %s)",
							   (user_id, item_name.title(), enable, item_type.lower()))
		await db.commit()
		await mycursor.close()


	async def remove_user_item(self, user_id: int, item_name: str):
		mycursor, db = await the_database()
		await mycursor.execute(f"DELETE FROM UserItems WHERE item_name = '{item_name}' and user_id = {user_id}")
		await db.commit()
		await mycursor.close()

	async def update_user_item_info(self, user_id: int, item_name: str, enable: str):
		mycursor, db = await the_database()
		await mycursor.execute(
			f"UPDATE UserItems SET enable = '{enable}' WHERE user_id = {user_id} and item_name = '{item_name}'")
		await db.commit()
		await mycursor.close()


	async def get_user_items(self, user_id: int):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserItems WHERE user_id = {user_id} ORDER BY user_id")
		item_system = await mycursor.fetchall()
		await mycursor.close()
		return item_system

	async def get_user_specific_type_item(self, user_id, item_type):
		mycursor, db = await the_database()
		await mycursor.execute(
			f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_type = '{item_type}' and enable = 'equipped'")
		spec_type_items = await mycursor.fetchall()
		await mycursor.close()

		if len(spec_type_items) != 0:
			registered_item = await self.get_specific_register_item(spec_type_items[0][1])
			return f'./sloth_custom_images/{item_type}/{registered_item[0][0]}'
		else:
			default_item = f'./sloth_custom_images/{item_type}/base_{item_type}.png'
			return default_item

	async def check_user_can_equip(self, user_id, item_name: str) -> bool:
		mycursor, db = await the_database()
		item_type = await self.get_specific_register_item(item_name)
		await mycursor.execute(
			f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_type = '{item_type[0][1]}' and enable = 'equipped'")
		equipped_item = await mycursor.fetchall()
		await mycursor.close()

		if len(equipped_item) != 0 and len(item_type) != 0:
			return False
		else:
			return True

	async def check_user_can_unequip(self, user_id, item_name: str) -> bool:
		mycursor, db = await the_database()
		await mycursor.execute(
			f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_name = '{item_name.lower()}' and enable = 'unequipped'")
		unequipped_item = await mycursor.fetchall()
		await mycursor.close()

		if len(unequipped_item) != 0:
			return False
		else:
			return True

	async def get_user_specific_item(self, user_id: int, item_name: str):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_name = '{item_name}'")
		item_system = await mycursor.fetchall()
		await mycursor.close()
		return item_system

	# Register Items
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_register_items(self, ctx):
		'''
		(ADM) Creates the RegisteredItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute(
			"CREATE TABLE RegisteredItems (image_name VARCHAR(50),item_type VARCHAR(10), item_name VARCHAR(30), item_price int, message_ref bigint default null, reaction_ref VARCHAR(50) default null) DEFAULT CHARSET utf8mb4")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *RegisteredItems* created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_register_items(self, ctx):
		'''
		(ADM) Drops the RegisteredItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute(f"DROP TABLE RegisteredItems")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *RegisteredItems* dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_register_items(self, ctx):
		'''
		(ADM) Resets the RegisteredItems table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM RegisteredItems")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *RegisteredItems* reseted!**", delete_after=3)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def show_registered(self, ctx):
		'''
		(ADM) Shows all the registered items in the shop.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM RegisteredItems")
		registered_items = await mycursor.fetchall()
		await mycursor.close()

		embed = discord.Embed(title="Registered Items", description="All registered items and their info",
							  colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
		for ri in registered_items:
			embed.add_field(name=f"{ri[2]}",
							value=f"**File:** {ri[0]} | **Type:** {ri[1]} | **Price:** {ri[3]}łł | **Reaction:** {ri[5]} |**Message ID:** {ri[4]}",
							inline=False)
		return await ctx.send(embed=embed)

	async def get_registered_items(self):
		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM RegisteredItems")
		registered_items = await mycursor.fetchall()
		await mycursor.close()
		return registered_items

	async def get_specific_register_item(self, item_name: str):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM RegisteredItems WHERE item_name = '{item_name}'")
		item = await mycursor.fetchall()
		await mycursor.close()
		return item

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def remove_registered_item(self, ctx, *, item_name: str = None):
		'''
		(ADM) Removes a registered item from the shop system.
		:param item_name: The name of the item to remove.
		'''
		await ctx.message.delete()
		if not item_name:
			return await ctx.send("**Inform an item name!**", delete_after=3)

		have_spec_item = await self.get_specific_register_item(item_name.title())
		if len(have_spec_item) != 0:
			await self.delete_registered_item(item_name.title())
			return await ctx.send(f"**{item_name.title()} deleted from the system!**", delete_after=3)
		else:
			return await ctx.send("**Item not found in the system!**", delete_after=3)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def register_item(self, ctx, mid: discord.Message = None, reactf=None, image_name: str = None, item_type: str = None, item_price: int = None, *, item_name: str = None):
		'''
		(ADM) Registers an item to the sloth shop.
		:param mid: The message ID of the image from which people will buy the item.
		:param reactf: The reaction that will trigger the buying process of that item.
		:param image_name: The name of the image item that will be shown in the user's inventory.
		:param item_type: The type of item; head, hand, body, bg...
		:param item_price: The price of the item
		:param item_name: The origin name of the image item that is in the system.
		'''

		# print(reactf)
		if not mid:
			return await ctx.send("**Specify the message id!**", delete_after=3)
		elif not reactf:
			if not len(reactf) <= 50:
				return await ctx.send("**Specify a shorter reaction!** (max=50)", delete_after=3)
			else:
				return await ctx.send("**Specify the reaction!**", delete_after=3)
		elif not image_name:
			if not len(item_name) <= 50:
				return await ctx.send("**Specify a shorter item name! (max=50)**", delete_after=3)
			else:
				return await ctx.send("**Specify the image name!**", delete_after=3)
		elif not item_type:
			if not len(item_type) <= 10:
				return await ctx.send("**Specify a shorter item type name!**", delete_after=3)
			else:
				return await ctx.send("**Specify the item type!**", delete_after=3)

		elif not item_price:
			return await ctx.send("**Specify the item price!**", delete_after=3)
		elif not item_name:
			if not len(item_name) <= 30:
				return await ctx.send("**Specify a shorter item name! (max=30)**", delete_after=3)
			else:
				return await ctx.send("**Specify the item name!**", delete_after=3)

		await self.insert_registered_item(mid.id, reactf, image_name, item_type, item_price, item_name)
		await mid.add_reaction(reactf)
		return await ctx.send(f"**Item __{item_name.title()}__ successfully registered!**", delete_after=3)

	async def insert_registered_item(self, mid: int, reactf, image_name: str, item_type: str, item_price: int,
									 item_name: str):
		mycursor, db = await the_database()
		await mycursor.execute(
			"INSERT INTO RegisteredItems (image_name, item_type, item_name, item_price, message_ref, reaction_ref) VALUES (%s, %s, %s, %s, %s, %s)",
			(image_name, item_type.lower(), item_name.title(), item_price, mid, reactf))
		await db.commit()
		await mycursor.close()

	async def delete_registered_item(self, item_name: str):
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM RegisteredItems WHERE item_name = %s", (item_name,))
		await db.commit()
		await mycursor.close()

	async def check_user_have_item(self, user_id: int, item_name: str):

		user_items = await self.get_user_specific_item(user_id, item_name)
		# print(user_items)
		if user_items:
			return True
		else:
			return False

	# Table UserCurrency
	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_user_currency(self, ctx):
		'''
		(ADM) Creates the UserCurrency table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("""
			CREATE TABLE UserCurrency (
			user_id bigint, user_money bigint, last_purchase_ts bigint,
			user_classes bigint default 0, user_class_reward bigint default 0, user_hosted bigint default 0,
			user_lotto bigint default null, sloth_class varchar(30) default 'default', change_class_ts bigint default 0,
			last_skill_ts bigint default 0, protected tinyint(1) default 0, has_potion tinyint(1) default 0,
			hacked tinyint(1) default 0, knocked_out tinyint(1) default 0), last_skill_two_ts bigint default 0,
			skills_used int default 0, wired tinyint(1) default 0, tribe varchar(50) default null,
			frogged tinyint(1) default 0
			""")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserCurrency* created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_user_currency(self, ctx):
		'''
		(ADM) Drops the UserCurrency table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserCurrency")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserCurrency* dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_user_currency(self, ctx):
		'''
		(ADM) Resets the UserCurrency table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserCurrency")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserCurrency* reseted!**", delete_after=3)


	async def send_hacked_image(self, ctx: commands.Context, member: discord.Member) -> None:
		""" Makes and sends a hacked image.
		:param ctx: The context.
		:param member: The member who was hacked. """

		SlothClass = self.client.get_cog('SlothClass')

		try:
			# Gets original skill action and the attacker
			skill_action = await SlothClass.get_skill_action_by_target_id_and_skill_type(member.id, 'hack')
			skill_action = skill_action[0] if skill_action else '??'
			hacker = self.client.get_user(skill_action)
			# Makes the Hacked image and saves it
			big = ImageFont.truetype("built titling sb.ttf", 80)
			background = Image.open('sloth_custom_images/background/hacked.png').convert('RGBA')
			draw = ImageDraw.Draw(background)
			draw.text((350, 300), f"Hacked by {hacker}", font=big, fill=(0, 0, 0))
			file_path = f'media/temporary/hacked_{member.id}.png'
			background.save(file_path, 'png', quality=90)
		except Exception as e:
			print(e)
			return await ctx.send(f"**{ctx.author.mention}, something went wrong with it!**")
		else:
			await ctx.send(file=discord.File(file_path))
			# await asyncio.sleep(0.5)
			return os.remove(file_path)


	async def send_frogged_image(self, ctx: commands.Context, member: discord.Member, knocked_out: bool = False) -> None:
		""" Makes and sends a frogged image.
		:param ctx: The context.
		:param member: The member who was frogged.
		:param knocked_out: Whether the user is knocked out"""
		
		SlothClass = self.client.get_cog('SlothClass')
		try:
			# Gets original skill action and the attacker
			skill_action = await SlothClass.get_skill_action_by_target_id_and_skill_type(member.id, 'frog')
			skill_action = skill_action[0] if skill_action else '??'
			metamorph = self.client.get_user(skill_action)
			# Makes the Hacked image and saves it
			big = ImageFont.truetype("built titling sb.ttf", 80)
			background = None

			if knocked_out:
				background = Image.open('sloth_custom_images/background/frogged_ko.png').convert('RGBA')
			else:
				background = Image.open('sloth_custom_images/background/frogged.png').convert('RGBA')

			draw = ImageDraw.Draw(background)
			draw.text((170, 170), f"{metamorph}", font=big, fill=(39, 126, 205))
			file_path = f'media/temporary/frogged_{member.id}.png'
			background.save(file_path, 'png', quality=90)
		except Exception as e:
			print(e)
			return await ctx.send(f"**{ctx.author.mention}, something went wrong with it!**")
		else:
			await ctx.send(file=discord.File(file_path))
			# await asyncio.sleep(0.5)
			return os.remove(file_path)

	async def get_member_public_flags(self, member: discord.Member) -> List[str]:
		""" Gets the member's public flags.
		:param member: The member to get the flags from. """

		public_flags = member.public_flags.all()
		public_flag_names = list(map(lambda pf: pf.name, public_flags))
		return public_flag_names

		

	@commands.command()
	async def profile(self, ctx, member: discord.Member = None):
		""" Shows the member's profile with their custom sloth.
		:param member: The member to see the profile. (Optional) """

		if not member:
			member = ctx.author

		user_info = await self.get_user_currency(member.id)

		if not user_info:
			if ctx.author.id == member.id:
				return await ctx.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))
			else:
				return await ctx.send(f"**{member} doesn't have an account yet!**", delete_after=3)

		if user_info[0][7].lower() == 'default':
			if ctx.author.id == member.id:
				return await ctx.send(embed=discord.Embed(description=f"**{member.mention}, you have a default Sloth class. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))
			else:
				return await ctx.send(f"**{member} has a default Sloth class, I cannot show their profile!**")

		SlothClass = self.client.get_cog('SlothClass')
		effects = await SlothClass.get_user_effects(user_id=member.id)

		def has_effect(effect: str):
			if effect in effects:
				return effects[effect]

			return False

		# Checks whether user is hacked
		if has_effect('hacked'):
			return await self.send_hacked_image(ctx, member)
		# Checks whether user is frogged
		if has_effect('frogged'):
			return await self.send_frogged_image(ctx, member, user_info[0][13])

		small = ImageFont.truetype("built titling sb.ttf", 45)
		background = Image.open(await self.get_user_specific_type_item(member.id, 'background'))

		# Checks whether user is transmutated
		sloth = None
		if has_effect('transmutated'):
			sloth = Image.open(f"./sloth_custom_images/sloth/transmutated_sloth.png")
		else:
			sloth = Image.open(f"./sloth_custom_images/sloth/{user_info[0][7].title()}.png")

		# print('czxcxzcxzcxzczcxaaaaaaaaadasdsadsadsa')
		# sloth = Image.open(f"./sloth_custom_images/sloth/{user_info[0][7].title()}.png")
		body = Image.open(await self.get_user_specific_type_item(member.id, 'body'))
		hand = Image.open(await self.get_user_specific_type_item(member.id, 'hand'))
		foot = Image.open(await self.get_user_specific_type_item(member.id, 'foot'))
		head = Image.open(await self.get_user_specific_type_item(member.id, 'head'))
		hud = Image.open(await self.get_user_specific_type_item(member.id, 'hud'))
		#badge = Image.open(await self.get_user_specific_type_item(member.id, 'badge'))
		pfp = await self.get_user_pfp(member)
		background.paste(sloth, (0, 0), sloth)
		background.paste(body, (0, 0), body)
		background.paste(head, (0, 0), head)
		background.paste(foot, (0, 0), foot)
		background.paste(hand, (0, 0), hand)
		background.paste(hud, (0, 0), hud)

		# Checks if user is a booster
		booster_role = discord.utils.get(ctx.guild.roles, id=booster_role_id)
		if booster_role in member.roles:
			if flag_badge := flag_badges.get('discord_server_booster'):
				file_path = f"./sloth_custom_images/badge/{flag_badge[0]}"
				if os.path.isfile(file_path):
					booster_badge = Image.open(file_path).resize((50, 50)).convert('RGBA')
					background.paste(booster_badge, flag_badge[1], booster_badge)

		# Pastes all flag badges that the user has
		flags = await self.get_member_public_flags(member)
		for flag in flags:
			if flag_badge := flag_badges.get(flag):
				file_path = f"./sloth_custom_images/badge/{flag_badge[0]}"
				if os.path.isfile(file_path):
					flag_image = Image.open(file_path).resize((50, 50)).convert('RGBA')
					background.paste(flag_image, flag_badge[1], flag_image)

		# Checks whether user has level badges
		user_level = await self.get_specific_user(member.id)
		for key, value in reversed(list(level_badges.items())):
			if user_level[0][2] >= key:
				file_path = f"sloth_custom_images/badge/{value[0]}.png"
				if os.path.isfile(file_path):
					level_badge = Image.open(file_path)
					background.paste(level_badge, value[1], level_badge)
					break

		# Tries to print the user's profile picture
		try:
			background.paste(pfp, (201, 2), pfp)
		except Exception:
			pass

		draw = ImageDraw.Draw(background)
		draw.text((310, 5), f"{str(member)[:10]}", (255, 255, 255), font=small)
		draw.text((80, 525), f"{user_info[0][1]}", (255, 255, 255), font=small)
		file_path = f'media/temporary/profile_{member.id}.png'
		background.save(file_path, 'png', quality=90)

		all_effects = {key:value for (key, value) in effects.items() if value.get('has_gif')}
		async with ctx.typing():
			if all_effects:
				try:
					gif_file_path = await self.make_gif_image(member_id=member.id, file_path=file_path, all_effects=all_effects)
					# print('sending')
					await ctx.send(file=discord.File(gif_file_path))
					# print('sent')
				except Exception as e:
					print(e)
					pass
				finally:
					# pass
					# await asyncio.sleep(2)
					os.remove(file_path)
					os.remove(gif_file_path)
			else:
				try:
					await ctx.send(file=discord.File(file_path))
				except:
					pass
				finally:
					os.remove(file_path)


	async def make_gif_image(self, member_id: int, file_path: str, all_effects: Dict[str, Dict[str, Union[List[str], Tuple[int]]]]) -> None:
		""" Makes a gif image out a profile image.
		:param file_path:
		:param effects: """

		gif_file_path = f'media/temporary/profile_{member_id}.gif'

		try:

			profile = Image.open(f'media/temporary/profile_{member_id}.png').convert('RGBA')
			gif = GIF(image=profile, frame_duration=40)
			path = 'media/effects'

			# Gets all frames of each effect and resize them properly, respectively.
			for effect in all_effects:
				full_path = f"{path}/{effect}"
				# Checks whether the effect folder exists
				if os.path.isdir(full_path):
					# Gets all frame images from the folder
					for i in range(len(glob.glob(f"{full_path}/*.png"))):
						frame = Image.open(f"{full_path}/{effect}_{i+1}.png")#.convert('RGBA') # remove this convert later
						# Checs whether frame has to be resized
						if all_effects[effect]['resize']:
							frame = frame.resize(all_effects[effect]['resize']).convert('RGBA')
						# Appends to its respective frame list
						all_effects[effect]['frames'].append(frame)

			# Loops through the frames based on the amount of frames of the longest effect.
			longest_gif = max([len(frames['frames']) for frames in all_effects.values()])
			
			for efx in all_effects.keys():
				all_effects[efx]['frames'] = cycle(all_effects[efx]['frames'])

			for i in range(longest_gif):
				# print(i+1)
				# Gets a frame of each effect in each iteration of the loop
				base = gif.new_frame()
				await asyncio.sleep(0)
				for efx, value in all_effects.items():
					# print(all_effects[efx]['cords'])
					cords = all_effects[efx]['cords']
					frame = next(all_effects[efx]['frames'])
					# print(efx, frame)
					base.paste(frame, cords, frame)
					gif.add_frame(base)
				# print()

				if i >= 400:
					# print('nah')
					break

			else:
				# print('saving...')
				gif.export(gif_file_path)
				# print('Finished!')
				
		except Exception as e:
			# print('gaaa')
			print(e)
			pass
		finally:
			# print('returning...')
			return gif_file_path




	@commands.command()
	@commands.has_permissions(administrator=True)
	async def add_money(self, ctx, member: discord.Member = None, money: int = None):
		'''
		(ADM) Adds money to a member.
		:param member: The member to add money to.
		:param money: The amount of money to add.
		'''
		if not member:
			return await ctx.send("**Inform a member!**", delete_after=3)
		elif not money:
			return await ctx.send("**Inform an amount of money!**", delete_after=3)

		await self.update_user_money(member.id, money)
		return await ctx.send(f"**{money} added to {member.name}'s bank account!**", delete_after=5)

	async def get_user_currency(self, user_id: int):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
		user_currency = await mycursor.fetchall()
		await mycursor.close()
		return user_currency

	async def try_to_buy_item(self, user_id: int, item_type: str, item_name: str, to_pay: int, guild_id: int,
							  the_time: int):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
		user_info = await mycursor.fetchall()
		await mycursor.close()

		member = discord.utils.get(self.client.get_guild(guild_id).members, id=user_id)
		if user_info[0][1] >= to_pay:
			await self.insert_user_item(user_id, item_name, 'unequipped', item_type)
			await self.update_user_money(user_id, - to_pay)
			await self.update_user_purchase_ts(member.id, the_time)
			shop_embed = discord.Embed(title="Shop Communication",
									   description=f"**You just bought a __{item_name}__!**",
									   colour=discord.Color.green(), timestamp=datetime.utcnow())
			await member.send(embed=shop_embed)
		else:
			shop_embed = discord.Embed(title="Shop Communication",
									   description=f"**You don't have money for that! You need more `{to_pay - user_info[0][1]}łł` in order to buy it!**",
									   colour=discord.Color.green(), timestamp=datetime.utcnow())
			return await member.send(embed=shop_embed)

	async def insert_user_currency(self, user_id: int, the_time: int) -> None:
		""" Inserts a user into the currency system.
		:param user_id: The user's ID.
		:param the_time: The current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO UserCurrency (user_id, user_money, last_purchase_ts) VALUES (%s, %s, %s)",
							   (user_id, 0, the_time))
		await db.commit()
		await mycursor.close()

	async def update_user_money(self, user_id: int, money: int) -> None:
		""" Updates the user money.
		:param user_id: The user's ID.
		:param money: The money addition. (It can be negative)"""

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET user_money = user_money + %s WHERE user_id = %s", (money, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_purchase_ts(self, user_id: int, the_time: int) -> None:
		""" Updates the user purchase timestamp.
		:param user_id: The user's ID.
		:param the_time: The current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET last_purchase_ts = %s WHERE user_id = %s", (the_time, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_lotto_ts(self, user_id: int, the_time: int) -> None:
		""" Updates the user lotto timestamp.
		:param user_id: The user's ID.
		:param the_time: The current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET user_lotto = %s WHERE user_id = %s", (the_time, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_hosted(self, user_id: int) -> None:
		""" Updates the user hosted classes counter.
		:param user_id: The user's ID. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET user_hosted = user_hosted + 1 WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	# Google Drive commands
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def download_update(self, ctx=None, rall: str = 'no'):
		"""
		(ADM) Downloads all shop images from the Google Drive.
		"""
		if ctx:
			await ctx.message.delete()


		if rall.lower() == 'yes':
			try:
				# os.removedirs('./sloth_custom_images')
				shutil.rmtree('./sloth_custom_images')
			except Exception:
				pass
				
		all_folders = {"background": "1V8l391o3-vsF9H2Jv24lDmy8e2erlHyI",
					   "sloth": "16DB_lNrnrmvxu2E7RGu01rQGQk7z-zRy",
					   "body": "1jYvG3vhL32-A0qDYn6lEG6fk_GKYDXD7",
					   "hand": "1ggW3SDVzTSY5b8ybPimCsRWGSCaOBM8d",
					   "hud": "1-U6oOphdMNMPhPAjRJxJ2E6KIzIbewEh",
					   "badge": "1k8NRfwwLzIY5ALK5bUObAcrKr_eUlfjd",
					   "foot": "1Frfra1tQ49dKM6Dg4DIbrfYbtXadv9zj",
					   "head": "1Y9kSOayw4NDehbqfmvPXKZLrXnIjeblP"
					   }

		categories = ['background', 'sloth', 'body', 'hand', 'hud', 'badge', 'foot', 'head']
		for category in categories:
			try:
				os.makedirs(f'./sloth_custom_images/{category}')
				print(f"{category} folder made!")
			except FileExistsError:
				pass

		for folder, folder_id in all_folders.items():
			files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
			download_path = f'./sloth_custom_images/{folder}'
			for file in files:
				isFile = os.path.isfile(f"{download_path}/{file['title']}")
				# print(isFile)
				if not isFile:
					# print(f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
					try:
						output_file = os.path.join(download_path, file['title'])
						temp_file = drive.CreateFile({'id': file['id']})
						temp_file.GetContentFile(output_file)
					except:
						pass
					# print(f"File '{file['title']}' downloaded!")

		if ctx:
			return await ctx.send("**Download update is done!**", delete_after=5)

	# Google Drive commands
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def text_download_update(self, ctx=None, rall: str = 'no'):
		'''
		(ADM) Downloads all texts from the GoogleDrive and stores in the bot's folder
		'''
		if rall.lower() == 'yes':
			try:
				shutil.rmtree('./texts')
			except Exception as e:
				pass

		all_text_folders = {"languages": "1_gBiliWPrCj5cLpChQfg9QRnj8skQVHM"}

		text_categories = ["languages"]
		
		for t_category in text_categories:
			try:
				os.makedirs(f'./texts/{t_category}')
				print(f"{t_category} folder made!")
			except FileExistsError:
				pass

		for folder, folder_id in all_text_folders.items():
			files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
			download_path = f'./texts/{folder}'
			for file in files:
				isFile = os.path.isfile(f"{download_path}/{file['title']}")
				if not isFile:
					try:
						output_file = os.path.join(download_path, file['title'])
						temp_file = drive.CreateFile({'id': file['id']})
						temp_file.GetContentFile(output_file)
					except:
						pass
		if ctx:
			return await ctx.send("**Download update is done!**")

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def list_folder(self, ctx, image_suffix: str = None, item_name: str = None):
		'''
		(ADM) Lists a shop image folder from Google Drive.
		:param image_suffix: The image/folder category.

		'''
		await ctx.message.delete()
		all_folders = {"background": "1V8l391o3-vsF9H2Jv24lDmy8e2erlHyI",
					   "sloth": "16DB_lNrnrmvxu2E7RGu01rQGQk7z-zRy",
					   "body": "1jYvG3vhL32-A0qDYn6lEG6fk_GKYDXD7",
					   "hand": "1ggW3SDVzTSY5b8ybPimCsRWGSCaOBM8d",
					   "hud": "1-U6oOphdMNMPhPAjRJxJ2E6KIzIbewEh",
					   "badge": "1k8NRfwwLzIY5ALK5bUObAcrKr_eUlfjd",
					   "foot": "1Frfra1tQ49dKM6Dg4DIbrfYbtXadv9zj",
					   "head": "1Y9kSOayw4NDehbqfmvPXKZLrXnIjeblP"}

		if not image_suffix:
			for folder, folder_id in all_folders.items():
				files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
				print(f"\033[35mCategory:\033[m {folder}")
				for file in files:
					print(
						f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
		else:

			for key, item in all_folders.items():
				if image_suffix == key:
					embed = discord.Embed(title=f"Category: {image_suffix}", colour=discord.Colour.dark_green(),
										  timestamp=ctx.message.created_at)
					files = drive.ListFile({'q': "'%s' in parents and trashed=false" % item}).GetList()
					print(f"\033[35mCategory:\033[m {image_suffix}")
					for file in files:
						embed.add_field(name=f"Name: {file['title']}", value=f"ID: {file['id']}", inline=False)
						print(
							f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
					return await ctx.send(embed=embed)
			else:
				return await ctx.send("**Category not found!**", delete_after=3)

	# UserServerActivity

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_server_activity(self, ctx):
		'''
		(ADM) Creates the UserServerActivity table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute(
			"CREATE TABLE UserServerActivity (user_id bigint, user_messages bigint, user_time bigint, user_timestamp bigint DEFAULT NULL)")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserServerActivity* created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_server_activity(self, ctx):
		'''
		(ADM) Drops the UserServerActivity table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserServerActivity")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table *UserServerActivity* dropped!**", delete_after=3)

	async def insert_user_server_activity(self, user_id: int, add_msg: int, new_ts: int = None):
		mycursor, db = await the_database()
		await mycursor.execute(
			"INSERT INTO UserServerActivity (user_id, user_messages, user_time, user_timestamp) VALUES (%s, %s, %s, %s)",
			(user_id, add_msg, 0, new_ts))
		await db.commit()
		await mycursor.close()

	async def get_user_activity_info(self, user_id: int):
		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserServerActivity WHERE user_id = {user_id}")
		user_info = await mycursor.fetchall()
		await mycursor.close()
		return user_info

	async def update_user_server_messages(self, user_id: int, add_msg: int):
		mycursor, db = await the_database()
		await mycursor.execute(
			f"UPDATE UserServerActivity SET user_messages = user_messages + {add_msg} WHERE user_id = {user_id}")
		await db.commit()
		await mycursor.close()

	async def update_user_server_time(self, user_id: int, add_time: int):
		mycursor, db = await the_database()
		await mycursor.execute(
			f"UPDATE UserServerActivity SET user_time = user_time + {add_time} WHERE user_id = {user_id}")
		await db.commit()
		await mycursor.close()

	async def update_user_server_timestamp(self, user_id: int, new_ts: int):
		mycursor, db = await the_database()
		await mycursor.execute(f"UPDATE UserServerActivity SET user_timestamp = {new_ts} WHERE user_id = {user_id}")
		await db.commit()
		await mycursor.close()


	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_server_activity(self, ctx):
		'''
		(ADM) Resets the UserServerActivity table.
		'''
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserServerActivity")
		await db.commit()
		await mycursor.close()
		return await ctx.send("**Table *UserServerActivity* reseted!**", delete_after=3)

	async def check_table_exist(self) -> bool:
		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'UserServerActivity'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True

	async def exchange(self, ctx):

		""" Exchange your status into leaves (łł) """

		user_info = await self.get_user_activity_info(ctx.author.id)
		if not user_info:
			return await ctx.send("**You have nothing to exchange!**")
			
		user_found = await self.get_user_currency(ctx.author.id)
		if not user_found:
			epoch = datetime.utcfromtimestamp(0)
			the_time = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_currency(ctx.author.id, the_time - 61)

		user_message = user_info[0][1]
		user_time = user_info[0][2]
		member_id = ctx.author.id
		async with ctx.typing():
			cmsg, message_times = await self.convert_messages(member_id, user_message)
			ctime, time_times = await self.convert_time(member_id, user_time)



		embed = discord.Embed(title="Exchange", colour=ctx.author.color, timestamp=ctx.message.created_at)
		embed.set_author(name=ctx.author, url=ctx.author.avatar_url)
		if not cmsg == ctime == 0:
			if cmsg > 0:
				embed.add_field(name="__**Messages:**__",
								value=f"Exchanged `{message_times * 50}` messages for `{cmsg}`łł;", inline=False)
			if ctime > 0:
				embed.add_field(name="__**Time:**__",
								value=f"Exchanged `{(time_times * 1800) / 60}` minutes for `{ctime}`łł;", inline=False)
			return await ctx.send(embed=embed)
		else:
			return await ctx.send("**You have nothing to exchange!**")

	async def convert_messages(self, member_id, user_message: int):
		messages_left = user_message
		exchanged_money = times = 0

		while True:
			if messages_left >= 50:
				times += 1
				messages_left -= 50
				exchanged_money += 3
				await asyncio.sleep(0)
				continue
				#return await self.convert_messages(member_id, messages_left, exchanged_money, times)
			else:
				await self.update_user_server_messages(member_id, -times * 50)
				await self.update_user_money(member_id, exchanged_money)
				return exchanged_money, times

	async def convert_time(self, member_id, user_time: int):
		time_left = user_time
		exchanged_money = times = 0

		while True:
			if time_left >= 1800:
				times += 1
				time_left -= 1800
				exchanged_money += 3
				await asyncio.sleep(0)
				continue
				#return await self.convert_time(member_id, time_left, exchanged_money, times)
			else:
				await self.update_user_server_time(member_id, -times * 1800)
				await self.update_user_money(member_id, exchanged_money)
				return exchanged_money, times

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def add_message(self, ctx, member: discord.Member = None, add_message: int= None):
		'''
		(ADM) Adds messages to the member's status.
		:param member: The member to add the messages to.
		:param add_message: The amount of messages to add.
		'''
		if not add_message:
			return await ctx.send(f"**Inform an amount of messages to add!**", delete_after=3)
		if not member:
			member = ctx.author
		await self.update_user_server_messages(member.id, add_message)
		return await ctx.send(f"Added {add_message} messages to {member}")

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def add_time(self, ctx, member: discord.Member = None, add_time: int = None):
		'''
		(ADM) Adds time to the member's status.
		:param member: The member to add time to.
		:param add_time: The amount of time to add. (in secs)
		'''
		if not add_time:
			return await ctx.send(f"**Inform an amount of seconds to add!**", delete_after=3)
		if not member:
			member = ctx.author
		await self.update_user_server_time(member.id, add_time)
		return await ctx.send(f"Added {add_time} seconds to {member}")

	@commands.command()
	async def transfer(self, ctx, member: discord.Member = None, money: int = None):
		'''
		Transfers money from one member to another member.
		:param member: The member to transfer the money to.
		:param money: The amount of money to transfer.
		'''
		if not member:
			return await ctx.send('**Inform the member!**', delete_after=3)
		elif member.id == ctx.author.id:
			return await ctx.send("**You can't transfer money to yourself!**", delete_after=3)
		elif not money:
			return await ctx.send('**Inform the amount of money to transfer!**', delete_after=3)
		elif not int(money) > 0:
			return await ctx.send('**Inform value bigger than 0!**', delete_after=3)

		the_user = await self.get_user_currency(ctx.author.id)
		target_user = await self.get_user_currency(member.id)
		if not the_user:
			return await ctx.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))
		elif not target_user:
			return await ctx.send(f"**{member} does not have a bank account yet!**", delete_after=5)


		if the_user[0][1] >= int(money):
			SlothClass = self.client.get_cog('SlothClass')
			if wired_user := await SlothClass.get_skill_action_by_target_id_and_skill_type(
				target_id=ctx.author.id, skill_type='wire'):

				siphon_percentage = 35
				cybersloth_money = round((money*siphon_percentage)/100)
				target_money = money - cybersloth_money
				await self.update_user_money(member.id, target_money)
				await self.update_user_money(ctx.author.id, -money)
				await self.update_user_money(wired_user[0], cybersloth_money)
				await ctx.send(
					content=f"{ctx.author.mention}, {member.mention}, <@{wired_user[0]}>",
					embed=discord.Embed(
						title="__Intercepted Transfer__",
						description=
						f"{ctx.author.mention} tried to transfer `{money}łł` to {member.mention}, " +
						f"but <@{wired_user[0]}> siphoned off `{siphon_percentage}%` of it; `{cybersloth_money}łł`! " +
						f"So {member.mention} actually got `{target_money}łł`!",
						color=ctx.author.color,
						timestamp=ctx.message.created_at)
				)

			else:
				await self.update_user_money(member.id, money)
				await self.update_user_money(ctx.author.id, -money)
				await ctx.send(f"**{ctx.author.mention} transferred {money}łł to {member.mention}!**")
		else:
			await ctx.send(f"You don't have {money}łł!")

	async def get_user_pfp(self, member):
		#im = Image.open(requests.get(member.avatar_url, stream=True).raw)
		async with self.session.get(str(member.avatar_url)) as response:
			image_bytes = await response.content.read()
			with BytesIO(image_bytes) as pfp:
				image = Image.open(pfp)
				im = image.convert('RGBA')

		thumb_width = 59

		def crop_center(pil_img, crop_width, crop_height):
			img_width, img_height = pil_img.size
			return pil_img.crop(((img_width - crop_width) // 2,
								 (img_height - crop_height) // 2,
								 (img_width + crop_width) // 2,
								 (img_height + crop_height) // 2))

		def crop_max_square(pil_img):
			return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

		def mask_circle_transparent(pil_img, blur_radius, offset=0):
			offset = blur_radius * 2 + offset
			mask = Image.new("L", pil_img.size, 0)
			draw = ImageDraw.Draw(mask)
			draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

			result = pil_img.copy()
			result.putalpha(mask)

			return result

		im_square = crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
		im_thumb = mask_circle_transparent(im_square, 4)
		#im_thumb.save('png/user_pfp.png', 'png', quality=90)
		return im_thumb
	
	async def get_specific_user(self, user_id: int):
		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM MembersScore WHERE user_id = %s", (user_id,))
		member = await mycursor.fetchall()
		await mycursor.close()
		return member

def setup(client):
	client.add_cog(SlothCurrency(client))
