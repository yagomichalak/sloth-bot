import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Seraph(Player):

	def __init__(self, client) -> None:
		self.client = client
		# self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)


	@commands.command(aliases=['dp', 'divine', 'protection'])
	@Player.skill_on_cooldown()
	@Player.user_is_class('seraph')
	@Player.skill_mark()
	async def divine_protection(self, ctx, target: discord.Member = None) -> None:
		""" A command for Seraphs. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(ctx.author.id):
			return await ctx.send(f"**{ctx.author.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			target = ctx.author

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{target.mention} is already protected, {ctx.author.mention}!**")

		confirmed = await ConfirmSkill(f"**{ctx.author.mention}, are you sure you want to use your skill, to protect {target.mention}?**").prompt(ctx)
		if confirmed:
			current_timestamp = await self.get_timestamp()
			await self.insert_skill_action(
				user_id=ctx.author.id, skill_type="divine_protection", skill_timestamp=current_timestamp, 
				target_id=target.id, channel_id=ctx.channel.id
			)
			await self.update_user_protected(target.id, 1)
			await self.update_user_action_skill_ts(ctx.author.id, current_timestamp)
			divine_protection_embed = await self.get_divine_protection_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			await ctx.send(embed=divine_protection_embed)
		else:
			await ctx.send("**Not protecting anyone, then!**")


	@commands.command()
	@Player.skill_two_on_cooldown()
	@Player.user_is_class('seraph')
	@Player.not_ready()
	async def reinforce(self, ctx) -> None:
		""" Gets a 20% chance of reinforcing all of their protected people's Divine Protection shield, 
		by making it last for one more day and a 10% chance of getting a protection for themselves too 
		(in case they don't have one already). """

		pass

	async def check_protections(self) -> None:
		""" Check on-going protections and their expiration time. """
		
		divine_protections = await self.get_expired_protections()
		for dp in divine_protections:
			await self.update_user_protected(dp[3], 0)
			await self.delete_skill_action_by_target_id_and_skill_type(dp[3], 'divine_protection')

			channel = self.bots_txt
			

			await channel.send(
				content=f"<@{dp[0]}>, <@{dp[3]}>", 
				embed=discord.Embed(
					description=f"**<@{dp[3]}>'s `Divine Protection` from <@{dp[0]}> just expired!**",
					color=discord.Color.red()))


	async def update_user_protected(self, user_id: int, protected: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param protected: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET protected = %s WHERE user_id = %s", (protected, user_id))
		await db.commit()
		await mycursor.close()


	async def get_divine_protection_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a divine protection action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the divine protection.
		:param target_id: The ID of the target member that is gonna be protected. """

		timestamp = await self.get_timestamp()

		divine_embed = discord.Embed(
			title="A Divine Protection has been executed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		divine_embed.description=f"🛡️ <@{perpetrator_id}> protected <@{target_id}> from attacks for 24 hours! 🛡️"
		divine_embed.color=discord.Color.green()

		divine_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
		divine_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return divine_embed