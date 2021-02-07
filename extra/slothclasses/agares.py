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
			# Sends embedded message into the channel
			magic_pull_embed = await self.get_magic_pull_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id,
				t_before_vc=target_vc, t_after_vc=attacker_vc)
			await ctx.send(content=target.mention, embed=magic_pull_embed)


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