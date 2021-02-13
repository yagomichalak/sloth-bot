import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime
from typing import List, Union
import random
import asyncio

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Prawler(Player):

	def __init__(self, client) -> None:
		self.client = client
		# bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload) -> None:
		""" Checks reactions related to skill actions. """

		# Checks if it wasn't a bot's reaction
		if not payload.guild_id:
			return

		# Checks whether it's a valid member and not a bot
		if not payload.member or payload.member.bot:
			return

		skill_action = await self.get_skill_action_by_reaction_context(payload.message_id, payload.user_id)
		if skill_action is not None:
			emoji = str(payload.emoji)

			# Checks whether it's a steal
			if skill_action[6] == '🛡️' and emoji == '🛡️':

				await self.delete_skill_action_by_message_id(payload.message_id)
				channel = self.client.get_channel(skill_action[5])
				if not channel:
					channel = self.bots_txt
				else:
					message = await channel.fetch_message(skill_action[4])
					if message:
						message_embed = message.embeds[0]
						message_embed.color = discord.Color.green()
						message_embed.description=f"**Good job, <@{skill_action[3]}>! You saved yourself against <@{skill_action[0]}>'s stealing!**"
						await message.edit(embed=message_embed)
						await message.remove_reaction('🛡️', self.client.user)
						await message.remove_reaction('🛡️', payload.member)

				return await channel.send(
					embed=discord.Embed(
						description=f"**{payload.member.mention} defended themselves against <@{skill_action[0]}>'s stealing, good luck next time!**",
						color=discord.Color.green()))


	@commands.command(aliases=['stl', 'rob'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('prawler')
	@Player.skill_mark()
	async def steal(self, ctx, target: discord.Member = None) -> None:
		""" A command for Prawlers. 
		:param target: The member from whom you want to steal. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		attacker = ctx.author

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			return await ctx.send(f"**Inform a member to steal, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send("**You cannot steal from yourself!**")

		target_currency = await self.get_user_currency(target.id)
		if not target_currency:
			return await ctx.send(f"**You cannot steal from someone who doesn't have an account, {attacker.mention}!**")

		if target_currency[7] == 'default':
			return await ctx.send(f"**You cannot steal from someone who has a `default` Sloth class, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, you cannot steal from {target.mention}, because they are protected against attacks!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to steal from {target.mention}?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not stealing from anyone, then!**")

		await self.check_cooldown(user_id=attacker.id, skill_number=1)

		current_timestamp = await self.get_timestamp()

		embed = discord.Embed(
			description=f"**{target.mention}, you are being robbed by {attacker.mention}! Defend yourself by reacting with 🛡️!**",
			color=discord.Color.orange())
		embed.set_footer(text="You have 40 minutes to defend yourself!")

		try:
			steal = await ctx.send(embed=embed)
			await self.insert_skill_action(
				user_id=attacker.id, skill_type="steal", skill_timestamp=current_timestamp, 
				target_id=target.id, message_id=steal.id, channel_id=steal.channel.id, emoji="🛡️"
			)
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
		except Exception as e:
			print(e)
			await steal.delete()
			return await ctx.send(f"**Your skill failed miserably for some reason, {attacker.mention}!**")

		else:
			await steal.add_reaction('🛡️')
			await steal.edit(content=f"<@{target.id}>")




	@commands.command()
	@Player.skill_on_cooldown(skill_number=2, seconds=2592000)
	@Player.user_is_class('prawler')
	@Player.skill_mark()
	@Player.not_ready()
	async def sharpen(self, ctx) -> None:
		""" Sharpen one's blade so when stealing from someone, 
		it has a 35% chance of doubling the stolen money and stealing it from them as a bonus (if they have the money). 
		The blade can be sharpened up to 5 times. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		perpetrator = ctx.author

		if await self.is_user_knocked_out(perpetrator.id):
			return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

		user = await self.get_user_currency(perpetrator.id)
		stack = user[16]

		if stack == 5:
			return await ctx.send(f"**{perpetrator.mention}, your knife sharpness is already stacked to its maximum; `{stack}`!**")

		if not user[1] >= 1000:
			return await ctx.send(f"**You don't have `1000łł` to use this skill, {perpetrator.mention}!**")


		confirmed = await ConfirmSkill(
			f"**{perpetrator.mention}, are you sure you want to sharpen your knife sharpness stack `{stack}` to `{stack+1}` for `1000łł`?**"
			).prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not stealing from anyone, then!**")

		await self.check_cooldown(user_id=perpetrator.id, skill_number=2, seconds=2592000)

		await self.update_user_money(perpetrator.id, -1000)

		try:
			# Update user's second skill cooldown timestamp
			current_ts = await self.get_timestamp()
			await self.update_user_action_skill_two_ts(user_id=perpetrator.id, current_ts=current_ts)
			await self.increments_user_sharpness_stack(user_id=perpetrator.id, increment=1)

		except Exception as e:
			print(e)
			await ctx.send(f"**For some reason I couldn't sharpen your knife, {perpetrator.mention}!**")
		else:
			sharpen_embed = await self.get_sharpen_embed(
				channel=ctx.channel, perpetrator_id=perpetrator.id, stack=stack+1)
			await ctx.send(embed=sharpen_embed)


	async def check_steals(self) -> None:
		""" Check on-going steals and their expiration time. """
		
		steals = await self.get_expired_steals()
		for steal in steals:
			channel = self.bots_txt
			try:
				message = await channel.fetch_message(steal[4])
				if message:
					message_embed = message.embeds[0]
					message_embed.color = discord.Color.red()
					message_embed.description=f"**Too late, <@{steal[3]}>! You were robbed by <@{steal[0]}>!**"
					await message.edit(embed=message_embed)
					await message.remove_reaction('🛡️', self.client.user)
				# Removes skill action from the database
				await self.delete_skill_action_by_message_id(steal[4])
				# Gives money to the attacker
				user_currency = await self.get_user_currency(steal[3])
				if user_currency and user_currency[1] >= 5:
					await self.update_user_money(steal[0], 5)
					await self.update_user_money(steal[3], -5)
					steal_embed = await self.get_steal_embed(
						channel=channel, attacker_id=steal[0], target_id=steal[3], attack_succeeded=True)
					await channel.send(content=f"<@{steal[0]}>", embed=steal_embed)
				else:
					steal_embed = await self.get_steal_embed(
						channel=channel, attacker_id=steal[0], target_id=steal[3])
					await channel.send(content=f"<@{steal[0]}>", embed=steal_embed)

			except Exception as e:
				print(e)
				pass
			finally:
				user = await self.get_user_currency(steal[0])
				stack = user[16]
				if stack:
					return await self.double_steal(channel=channel, attacker_id=steal[0], target_id=steal[3], stack=stack)


	async def double_steal(self, channel: discord.TextChannel, attacker_id: int, target_id: int, stack: int, loop: int = 1, init_rob_money: int = 5) -> None:
		""" Tries to double the steal based on the attacker's knife sharpness stack.
		:param attacker_id: The ID of the attacker.
		:param stack: The attacker's knife sharpness stack.
		:money loop: The loop that the recursion is in. 
		:param init_rob_money: The initial rob money that will be doubled. """

		rob_money = init_rob_money * 2


		# Calculates a 35% chance of doubling the previous steal amount
		if random.random() <= 0.35:
			try:
				target_currency = await self.get_user_currency(target_id)
				# Checks whether target still has money to be robbed from
				if target_currency and target_currency[1] >= rob_money:
					await self.update_user_money(attacker_id, rob_money)
					await self.update_user_money(target_id, -rob_money)
				else:
					return await channel.send(f"**<@{target_id}> doesn't have more `{rob_money}łł`, otherwise you would steal it, <@{attacker_id}>!**")
			except Exception as e:
				print(e)
				await channel.send(f"**For some reason I couldn't double your stealing, <@{attacker_id}>!**")

			else:
				rob_doubled_embed = await self.get_rob_doubled_embed(channel=channel, attacker_id=attacker_id, double_amount=rob_money, rob_stack=loop)
				await channel.send(embed=rob_doubled_embed)
				# Checks whether user achieved its maximum rob stack recursion
				if loop < stack:
					await asyncio.sleep(3)
					return await self.double_steal(channel=channel, attacker_id=attacker_id, target_id=target_id, stack=stack, loop=loop+1, init_rob_money=rob_money)

		else:
			await channel.send(
				f"**<@{attacker_id}>, you had a `35%` chance of doubling the previous amount and getting more `{rob_money}łł`, but you missed it!**")



	async def increments_user_sharpness_stack(self, user_id: int, increment: int) -> None:
		""" Increments the user knife sharpness stack.
		:param user_id: The ID of the user.
		:param increment: The value to be incremented (negative numbers to decrement). """


		mycursor, db = await the_database()
		await mycursor.execute("""
			UPDATE UserCurrency 
			SET knife_sharpness_stack = knife_sharpness_stack + %s
			WHERE user_id = %s""", (increment, user_id))
		await db.commit()
		await mycursor.close()


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

	async def get_steal_embed(self, channel, attacker_id: int, target_id: int, attack_succeeded: bool = False) -> discord.Embed:
		""" Makes an embedded message for a steal action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the stealing.
		:param target_id: The ID of the target member who is beeing stolen from. 
		:param attack_succeed: Whether the attack succeeded or not. """

		timestamp = await self.get_timestamp()

		steal_embed = discord.Embed(
			title="A steal just happend!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		if attack_succeeded:
			steal_embed.description=f"🍃 <@{attacker_id}> stole 5łł from <@{target_id}>! 🍃"
			steal_embed.color=discord.Color.red()
		else:
			steal_embed.description=f"🍃 <@{attacker_id}> tried to steal 5łł from <@{target_id}>, but they didn't have it! 🍃"
			steal_embed.color=discord.Color.green()

		steal_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Prawler.png")
		steal_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return steal_embed


	async def get_sharpen_embed(self, channel, perpetrator_id: int, stack: int) -> discord.Embed:
		""" Makes an embedded message for a knife sharpen action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the stealing.
		:param stack: The stack number that the knife was sharpened to. """

		timestamp = await self.get_timestamp()

		sharpen_embed = discord.Embed(
			title="A Knife has been Sharpened!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		sharpen_embed.description=f"<@{perpetrator_id}> has just sharpened his knife to stack `{stack}` 🔪"
		sharpen_embed.color=discord.Color.green()

		sharpen_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Prawler.png")
		sharpen_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return sharpen_embed

	async def get_rob_doubled_embed(self, channel, attacker_id: int, double_amount: int, rob_stack: int) -> discord.Embed:
		""" Makes an embedded message for a rob being doubled.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the stealing.
		:param double_amount: The amount of leaves that it was doubled to. 
		:param rob_stack: The stack related to the current rob. """

		timestamp = await self.get_timestamp()
		rob_doubled_embed = discord.Embed(
			title="Rob has been Doubled!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)

		rob_doubled_embed.description=f"<@{attacker_id}> managed to double their stealing, and got more `{double_amount}łł` 🔪🍃"
		rob_doubled_embed.color=discord.Color.green()

		rob_doubled_embed.set_author(name=f"Rob stack {rob_stack} (35% chance)", icon_url=self.client.user.avatar_url)
		rob_doubled_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Prawler.png")
		rob_doubled_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return rob_doubled_embed