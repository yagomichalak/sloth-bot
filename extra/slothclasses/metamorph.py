import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Metamorph(Player):

	def __init__(self, client) -> None:
		self.client = client
		# self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)



	@commands.command(aliases=['transmutate', 'trans'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('metamorph')
	@Player.skill_mark()
	async def transmutation(self, ctx) -> None:
		""" Transmutates into a different thing temporarily. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		member = ctx.author

		if await self.is_user_knocked_out(member.id):
			return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

		if await self.is_transmutated(member.id):
			return await ctx.send(f"**You are already transmutated, {member.mention}!**")

		confirmed = await ConfirmSkill(f"**{member.mention}, are you sure you want to transmutate yourself into a diffrent form for 1 hour?**").prompt(ctx)
		if not confirmed:
			return await ctx.send(f"**{member.mention}, not transmutating, then!**")

		timestamp = await self.get_timestamp()
		await self.insert_skill_action(
			user_id=member.id, skill_type="transmutation",
			skill_timestamp=timestamp, target_id=member.id,
			channel_id=ctx.channel.id
		)
		await self.update_user_action_skill_ts(member.id, timestamp)
		# Updates user's skills used counter
		await self.update_user_skills_used(user_id=attacker.id)

		transmutation_embed = await self.get_transmutation_embed(channel=ctx.channel, perpetrator_id=ctx.author.id)
		await ctx.send(embed=transmutation_embed)

	async def check_transmutations(self) -> None:

		""" Check on-going transmutations and their expiration time. """

		transmutations = await self.get_expired_transmutations()
		for tm in transmutations:
			print(tm)
			await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'transmutation')

			channel = self.bots_txt
			

			await channel.send(
				content=f"<@{tm[0]}>", 
				embed=discord.Embed(
					description=f"**<@{tm[3]}>'s `Transmutation` has just expired! 🐩→💥→🦥**",
					color=discord.Color.red()))


	async def check_frogifies(self) -> None:

		""" Check on-going frogifies and their expiration time. """

		frogifies = await self.get_expired_frogifies()
		for ff in frogifies:
			await self.delete_skill_action_by_target_id_and_skill_type(ff[3], 'frogify')
			await self.update_user_frogified(ff[3], 0)

			channel = self.bots_txt

			await channel.send(
				content=f"<@{ff[0]}>", 
				embed=discord.Embed(
					description=f"**<@{ff[3]}>'s `Frogify` has just expired! 🐸→💥→🦥**",
					color=discord.Color.red()))


	@commands.command(aliases=['dnk'])
	@Player.skill_on_cooldown(skill_number=2)
	@Player.user_is_class('metamorph')
	@Player.skill_mark()
	# @Player.not_ready()
	async def frogify(self, ctx, target: discord.Member = None) -> None:
		""" Makes someone a frog temporarily. 
		:param target: The person who you want to frogify. """


		# # Updates user's skills used counter
		# await self.update_user_skills_used(user_id=attacker.id)
		
		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		attacker = ctx.author

		if not target:
			return await ctx.send(f"**Please, inform a target to frogify, {attacker.mention}!**")

		if target.id == attacker.id:
			return await ctx.send(f"**You cannot frogify yourself, {attacker.mention}!**")

		attacker_effects = await self.get_user_effects(user_id=attacker.id)

		if 'knocked_out' in attacker_effects:
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if 'transmutated' in attacker_effects:
			return await ctx.send(f"**You are already transmutated, {attacker.mention}!**")


		target_effects = await self.get_user_effects(user_id=target.id)

		if 'frogified' in target_effects:
			return await ctx.send(f"**{target.mention} is already frogified, {attacker.mention}!**")

		if 'protected' in target_effects:
			return await ctx.send(f"**{target.mention} is protected against threats, {attacker.mention}!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to frogify {target.mention}?**").prompt(ctx)
		if not confirmed:
			return await ctx.send(f"**{attacker.mention}, not frogifying them, then!**")

		timestamp = await self.get_timestamp()
		await self.insert_skill_action(
			user_id=attacker.id, skill_type="frogify",
			skill_timestamp=timestamp, target_id=target.id,
			channel_id=ctx.channel.id
		)
		try:
			await self.update_user_action_skill_two_ts(attacker.id, timestamp)
			# Updates user's skills used counter
			await self.update_user_skills_used(user_id=attacker.id)

			await self.update_user_frogified(target.id, 1)
		except Exception as e:
			print(e)
			await ctx.send(f"**Something went wrong with it, {attacker.mention}!**")
		else:
			frogify_embed = await self.get_frogify_embed(channel=ctx.channel, attacker_id=attacker.id, target_id=target.id)
			await ctx.send(embed=frogify_embed)


	async def get_transmutation_embed(self, channel, perpetrator_id: int) -> discord.Embed:
		""" Makes an embedded message for a transmutation action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the transmutation. """

		timestamp = await self.get_timestamp()

		transmutation_embed = discord.Embed(
			title="A Transmutation just happened in front of everyone's eyes!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		transmutation_embed.description=f"**<@{perpetrator_id}> transmutated themselves into something else! 🦥→💥→🐩**"
		transmutation_embed.color=discord.Color.green()

		transmutation_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Metamorph.png")
		transmutation_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return transmutation_embed


	async def get_frogify_embed(self, channel, attacker_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a frogify action. 
		:param channel: The context channel.
		:param attacker_id: The ID of the attacker.
		:param target_id: The ID of the target. """

		timestamp = await self.get_timestamp()

		transmutation_embed = discord.Embed(
			title="A Prince(ss) rolled back Time!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		transmutation_embed.description=f"**<@{attacker_id}> frogified <@{target_id}>!  🦥→💥→🐸**"
		transmutation_embed.color=discord.Color.green()

		transmutation_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Metamorph.png")
		transmutation_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return transmutation_embed


	async def update_user_frogified(self, user_id: int, frogified: int) -> None:
		""" Updates the user's frogify state.
		:param user_id: The ID of the member to update. 
		:param frogify: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET frogified = %s WHERE user_id = %s", (frogified, user_id))
		await db.commit()
		await mycursor.close()