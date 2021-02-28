import discord
from discord.ext import commands
import os
from .player import Player
from extra.menu import ConfirmSkill
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Agares(Player):

	def __init__(self, client) -> None:
		self.client = client
		# self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)

		self.safe_categories = [
			int(os.getenv('LESSON_CAT_ID')),
			int(os.getenv('CASE_CAT_ID')),
			int(os.getenv('EVENTS_CAT_ID')),
			int(os.getenv('DEBATE_CAT_ID')),
			int(os.getenv('CULTURE_CAT_ID')),
			int(os.getenv('APPLICATION_CAT_ID'))
		]


	@commands.command(aliases=['ma'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('agares')
	@Player.skill_mark()
	async def magic_pull(self, ctx, target: discord.Member = None) -> None:
		""" A command for Agares. """

		attacker = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		attacker_state = attacker.voice
		if not attacker_state or not (attacker_vc := attacker_state.channel):
			return await ctx.send(f"**{attacker.mention}, you first need to be in a voice channel to magic pull someone!**")

		if not target:
			return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull yourself!**")

		if target.bot:
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull a bot!**")

		target_currency = await self.get_user_currency(target.id)
		if not target_currency:
			return await ctx.send(f"**You cannot magic pull someone who doesn't have an account, {attacker.mention}!**")

		if target_currency[7] == 'default':
			return await ctx.send(f"**You cannot magic pull someone who has a `default` Sloth class, {attacker.mention}!**")

		target_state = target.voice

		if not target_state or not (target_vc := target_state.channel):
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull {target.mention}, because they are not in a voice channel!!**")

		if target_vc.category and target_vc.category.id in self.safe_categories:
			return await ctx.send(
				f"**{attacker.mention}, you can't magic pull {target.mention} from `{target_vc}`, because it's a safe channel.**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't magic pull them!**")

		try:
			await target.move_to(attacker_vc)
		except Exception as e:
			print(e)
			await ctx.send(
				f"**{attacker.mention}, for some reason I couldn't magic pull {target.mention} from `{target_vc}` to `{attacker_vc}`**")
		else:
			# Puts the attacker's skill on cooldown
			current_ts = await self.get_timestamp()
			await self.update_user_action_skill_ts(attacker.id, current_ts)
			# Updates user's skills used counter
			await self.update_user_skills_used(user_id=attacker.id)
			# Sends embedded message into the channel
			magic_pull_embed = await self.get_magic_pull_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id,
				t_before_vc=target_vc, t_after_vc=attacker_vc)
			await ctx.send(content=target.mention, embed=magic_pull_embed)

	@commands.command()
	@Player.skills_used(requirement=5)
	@Player.skill_on_cooldown(skill_number=2)
	@Player.user_is_class('agares')
	@Player.skill_mark()
	# @Player.not_ready()
	async def recharge(self, ctx, target: discord.Member = None) -> None:
		""" Recharges someone's first skill by removing its cooldown.
		:param target: The target person who you want to recharge the skill for. """

		perpetrator = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if not target:
			return await ctx.send(f"**Please, inform a target, {perpetrator.mention}**")

		if target.bot:
			return await ctx.send(f"**{perpetrator.mention}, you cannot use this on a bot!**")

		if await self.is_user_knocked_out(perpetrator.id):
			return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

		target_currency = await self.get_user_currency(target.id)
		if not target_currency:
			return await ctx.send(f"**You cannot recharge the skill of someone who doesn't have an account, {perpetrator.mention}!**")

		if target_currency[7] == 'default':
			return await ctx.send(f"**You cannot recharge the skill of someone who has a `default` Sloth class, {perpetrator.mention}!**")


		confirm = await ConfirmSkill(f"**Are you sure you to reset {target.mention}'s first skill cooldown, {perpetrator.mention}?**").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not resetting it, then!**")

		await self.check_cooldown(user_id=perpetrator.id, skill_number=2)

		try:
			await self.reset_user_action_skill_cooldown(target.id)
		except Exception as e:
			print(e)
			await ctx.send(f"**For some reason I couldn't reset {target.menion}'s cooldown, {perpetrator.mention}!**")
		else:
			# Puts the perpetrator's skill on cooldown
			current_ts = await self.get_timestamp()
			await self.update_user_action_skill_two_ts(perpetrator.id, current_ts)
			# Updates user's skills used counter
			await self.update_user_skills_used(user_id=perpetrator.id)
			# Sends embedded message into the channel
			recharge_embed = await self.get_recharge_embed(
				channel=ctx.channel, perpetrator_id=perpetrator.id, target_id=target.id)

			await ctx.send(embed=recharge_embed)


	async def get_magic_pull_embed(self, channel, perpetrator_id: int, target_id: int, t_before_vc: discord.VoiceChannel, t_after_vc: discord.VoiceChannel) -> discord.Embed:
		""" Makes an embedded message for a magic pull action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the magic pulling. 
		:param target_id: The ID of the target of the magic pulling. """

		timestamp = await self.get_timestamp()

		magic_pull_embed = discord.Embed(
			title="A Magic Pull has been Successfully Pulled Off!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		magic_pull_embed.description=f"**<@{perpetrator_id}> magic pulled <@{target_id}> from `{t_before_vc}` to `{t_after_vc}`!** 🧲"
		magic_pull_embed.color=discord.Color.green()

		magic_pull_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Agares.png")
		magic_pull_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return magic_pull_embed


	async def get_recharge_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a recharge action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the magic pulling. 
		:param target_id: The ID of the target of the magic pulling. """

		timestamp = await self.get_timestamp()

		recharge_embed = discord.Embed(
			title="A Cooldown Recharge just Happend!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		recharge_embed.description=f"**<@{perpetrator_id}> reset <@{target_id}>'s first skill cooldown!** 🔁"
		recharge_embed.color=discord.Color.green()

		recharge_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Agares.png")
		recharge_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)
		recharge_embed.set_image(url='https://media1.tenor.com/images/623500b09831e08eb963bdc7d75797c4/tenor.gif?itemid=20299439')

		return recharge_embed