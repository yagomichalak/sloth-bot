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
		""" A command for Metamorphs. """

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


	@commands.command(aliases=['clone'])
	@Player.skill_two_on_cooldown()
	@Player.user_is_class('metamorph')
	@Player.skill_mark()
	@Player.not_ready()
	async def impersonate(self, ctx, target: discord.Member = None) -> None:
		""" Becomes someone else; gets someone else's items and clothes temporarily. 
		:param target: The person who you want to impersonate. """


		pass


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