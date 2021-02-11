import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime

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

		if not await self.get_user_currency(target.id):
			return await ctx.send(f"**You cannot steal from someone who doesn't have an account, {attacker.mention}!**")

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
	@Player.skill_two_on_cooldown()
	@Player.user_is_class('prawler')
	@Player.skill_mark()
	@Player.not_ready()
	async def sharpen(self, ctx) -> None:
		""" Sharpen one's blade so when stealing from someone, 
		it has a 35% chance of doubling the stolen money and stealing it from them as a bonus (if they have the money). 
		The blade can be sharpened up to 5 times. """

		pass



	async def check_steals(self) -> None:
		""" Check on-going steals and their expiration time. """
		
		steals = await self.get_expired_steals()
		for steal in steals:
			try:
				channel = self.bots_txt
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