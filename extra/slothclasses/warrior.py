import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Warrior(Player):


	def __init__(self, client) -> None:
		self.client = client
		# super().__init__(self)
		# self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)

	@commands.command(aliases=['ko', 'knock-out', 'knock_out', 'knock'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('warrior')
	@Player.skill_mark()
	async def hit(self, ctx, target: discord.Member = None) -> None:
		""" A command for Warriors. """

		attacker = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**{attacker.mention}, you cannot knock yourself out!**")

		if target.bot:
			return await ctx.send(f"**{attacker.mention}, you cannot knock out a bot!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't knock them out!**")

		if await self.is_user_knocked_out(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is already knocked out!**")


		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to knock {target.mention} out?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not knocking them out, then!**")

		try:
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			await self.update_user_is_knocked_out(target.id, 1)
			await self.insert_skill_action(
				user_id=attacker.id, skill_type="hit", skill_timestamp=current_timestamp,
				target_id=target.id, channel_id=ctx.channel.id
			)
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			hit_embed = await self.get_hit_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
			msg = await ctx.send(embed=hit_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Hit` skill failed, {attacker.mention}!**")

	async def check_knock_outs(self) -> None:

		""" Check on-going knock-outs and their expiration time. """

		knock_outs = await self.get_expired_knock_outs()
		for ko in knock_outs:
			await self.delete_skill_action_by_target_id_and_skill_type(ko[3], 'hit')
			await self.update_user_is_knocked_out(ko[3], 0)

			channel = self.bots_txt
		
			await channel.send(
				content=f"<@{ko[0]}>",
				embed=discord.Embed(
					description=f"**<@{ko[3]}> got better from <@{ko[0]}>'s knock-out! 🤕**",
					color=discord.Color.red()))



	async def update_user_is_knocked_out(self, user_id: int, is_it: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param is_it: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET knocked_out = %s WHERE user_id = %s", (is_it, user_id))
		await db.commit()
		await mycursor.close()


	async def get_hit_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a knock-out action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the knock-out.
		:param target_id: The ID of the target of the knock-out. """

		timestamp = await self.get_timestamp()

		hit_embed = discord.Embed(
			title="Someone was Knocked Out!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		hit_embed.description=f"**<@{perpetrator_id}> knocked <@{target_id}> out!** 😵"
		hit_embed.color=discord.Color.green()

		hit_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
		hit_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return hit_embed