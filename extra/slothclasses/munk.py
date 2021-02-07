import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Munk(Player):

	def __init__(self, client) -> None:
		self.client = client


	@commands.command()
	@Player.skill_on_cooldown()
	@Player.user_is_class('munk')
	async def munk(self, ctx, target: discord.Member = None) -> None:
		""" Converts a user into a real Munk. 
		:param target: The person you want to convert to a Munk. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		attacker = ctx.author

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			return await ctx.send(f"**Please, choose a member to use the `Munk` skill, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**You cannot convert yourself, since you are already a `Munk`, {attacker.mention}!**")

		if target.display_name.strip().title().endswith('Munk'):
			return await ctx.send(f"**{target.mention} is already a `Munk`, {attacker.mention}!**")

		if not await self.get_user_currency(target.id):
			return await ctx.send(f"**You cannot convert someone who doesn't have an account, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, you cannot convert {target.mention} into a `Munk`, because they are protected against attacks!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to convert {target.mention} into a `Munk`?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not converting them, then!**")

		try:
			await target.edit(nick=f"{target.display_name} Munk")
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			# await self.insert_skill_action(
			# 	user_id=attacker.id, skill_type="munk", skill_timestamp=current_timestamp, 
			# 	target_id=target.id, channel_id=ctx.channel.id
			# )
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			munk_embed = await self.get_munk_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			msg = await ctx.send(embed=munk_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

		else:
			await msg.edit(content=f"<@{target.id}>")


	async def get_munk_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a munk action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the munk skill.
		:param target_id: The ID of the target member that is gonna be protected. """

		timestamp = await self.get_timestamp()

		munk_embed = discord.Embed(
			title="A Munk Convertion has been delightfully performed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		munk_embed.description=f"🐿️ <@{perpetrator_id}> converted <@{target_id}> into a `Munk`! 🐿️"
		munk_embed.color=discord.Color.green()

		munk_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Munk.png")
		munk_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return munk_embed