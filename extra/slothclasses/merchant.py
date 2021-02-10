import discord
from discord.ext import commands, menus
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill, prompt_number, OpenShopLoop
import os
from typing import List, Union
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Merchant(Player):

	def __init__(self, client) -> None:
		self.client = client
		# self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)


	@commands.command(aliases=['os', 'open', 'shop'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('merchant')
	@Player.skill_mark()
	async def open_shop(self, ctx) -> None:
		""" A command for Merchants. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		member = ctx.author

		if await self.is_user_knocked_out(member.id):
			return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

		if (shopitem := await self.get_skill_action_by_user_id(member.id)):
			return await ctx.send(f"**{member.mention}, you already have an item in your shop!**")


		item_price = await prompt_number(self.client, ctx, f"**{member.mention}, for how much do you want to sell your changing-Sloth-class potion?**", member)
		if item_price is None:
			return

		confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to spend 50łł to put an item in your shop with the price of `{item_price}`łł ?**").prompt(ctx)
		if confirm:
			user_currency = await self.get_user_currency(member.id)
			if user_currency[1] >= 50:
				await self.update_user_money(member.id, -50)
			else:
				return await ctx.send(f"**{member.mention}, you don't have `50łł`!**")

			try:
				current_timestamp = await self.get_timestamp()
				await self.insert_skill_action(
					user_id=member.id, skill_type="potion", skill_timestamp=current_timestamp, 
					target_id=member.id, channel_id=ctx.channel.id, price=item_price
				)
				await self.update_user_action_skill_ts(member.id, current_timestamp)
				open_shop_embed = await self.get_open_shop_embed(
					channel=ctx.channel, perpetrator_id=member.id, price=item_price)
				await ctx.send(embed=open_shop_embed)
			except Exception as e:
				print(e)
				return await ctx.send(f"**{member.mention}, something went wrong with it, try again later!**")
			else:
				await ctx.send(f"**{member}, your item is now in the shop, check `z!sloth_shop` to see it there!**")
		else:
			return await ctx.send(f"**Not doing it, then, {member.mention}!**")


	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def sloth_shop(self, ctx) -> None:
		""" Shows all class related items in the Sloth shop. """

		embed = discord.Embed(
			title="__Sloth Class Shop__",
			description="All available items related to Sloth classes.",
			color=ctx.author.color,
			timestamp=ctx.message.created_at
			)

		potions = await self.get_open_shop_items()
		if potions:
			the_menu = menus.MenuPages(source=OpenShopLoop(potions), clear_reactions_after=True)
			await the_menu.start(ctx)
		else:
			return await ctx.send(f"**There are no items in the `Sloth class shop` yet, {ctx.author.mention}!**")


	@commands.command(aliases=['bp', 'buy'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def buy_potion(self, ctx, member: discord.Member = None) -> None:
		""" Buys a changing-Sloth-class potion from a Merchant. """

		buyer = ctx.author
		if not member:
			return await ctx.send(f"**Please, inform a `Merchant`, {buyer.mention}!**")


		if not (merchant_item := await self.get_skill_action_by_user_id(member.id)):
			return await ctx.send(
				f"**{member} is either not a `Merchant` or they don't have a potion available for purchase, {buyer.mention}!**")


		user_info = await self.get_user_currency(buyer.id)
		if not user_info:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

		elif user_info[7].lower() == 'default':
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have a Sloth class yet. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))

		elif user_info[11]:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you already have a potion, you can't buy another one!**"))

		elif user_info[1] < merchant_item[7]:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, the potion costs {merchant_item[7]}, but you only have {user_info[1]}łł!**"))

		else:
			confirm = await ConfirmSkill(f"**{buyer.mention}, are you sure you want to buy a `changing-Sloth-class potion` for `{merchant_item[7]}łł`?**").prompt(ctx)
			if not confirm:
				return await ctx.send(f"**Not buying it, then, {buyer.mention}!**")

			try:
				# Updates both buyer and seller's money
				await self.update_user_money(buyer.id, - merchant_item[7])
				await self.update_user_money(member.id, merchant_item[7])
				# Gives the buyer their potion and removes the potion from the store
				await self.update_user_has_potion(buyer.id, 1)
				await self.delete_skill_action_by_target_id_and_skill_type(member.id, 'potion')
			except Exception as e:
				print(e)
				await ctx.send(embed=discord.Embed(
					title="Error!",
					description=f"**Something went wrong with that purchase, {buyer.mention}!**",
					color=discord.Color.red(),
					timestamp=ctx.message.created_at
					))

			else:
				await ctx.send(embed=discord.Embed(
					title="__Successful Acquisition__",
					description=f"{buyer.mention} bought a `changing-Sloth-class potion` from {member.mention}!",
					color=discord.Color.green(),
					timestamp=ctx.message.created_at
					))


	@commands.command()
	@Player.skill_two_on_cooldown()
	@Player.user_is_class('merchant')
	@Player.skill_mark()
	@Player.not_ready()
	async def package(self, ctx) -> None:
		""" Buys a package from Dark Sloth Web and has a 15% chance of getting any equippable item from the Leaf Shop. """
		
		pass

	async def check_open_shop_items(self) -> None:

		""" Check on-going open-shop items and their expiration time. """

		transmutations = await self.get_expired_open_shop_items()
		for tm in transmutations:
			print(tm)
			await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'potion')

			channel = self.bots_txt
		
			await channel.send(
				content=f"<@{tm[0]}>",
				embed=discord.Embed(
					description=f"**<@{tm[3]}>'s `changing-Sloth-class potion` has just expired! Then it's been removed from the `Sloth class shop`! 🍯**",
					color=discord.Color.red()))


	# ========== Update ===========

	async def update_user_has_potion(self, user_id: int, has_it: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param has_it: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET has_potion = %s WHERE user_id = %s", (has_it, user_id))
		await db.commit()
		await mycursor.close()


	# ========== Get ===========


	async def get_open_shop_items(self) -> List[List[Union[str, int]]]:
		""" Gets all open shop items. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = 'potion'")
		potions = await mycursor.fetchall()
		await mycursor.close()
		return potions

	async def get_open_shop_embed(self, channel, perpetrator_id: int, price: int) -> discord.Embed:
		""" Makes an embedded message for a magic pull action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the magic pulling. 
		:param price: The price of the item that Merchant put into the shop. """

		timestamp = await self.get_timestamp()

		open_shop_embed = discord.Embed(
			title="A Merchant item has been put into the `Sloth Class Shop`!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		open_shop_embed.description=f"**<@{perpetrator_id}> put a `changing-Sloth-class potion` into the Sloth class shop, for the price of `{price}łł`!** 🍯"
		open_shop_embed.color=discord.Color.green()

		open_shop_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Merchant.png")
		open_shop_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return open_shop_embed