import discord
from discord.ext import commands, menus
import asyncio
from typing import Union, List, Any

import re
from emoji.core import emojize, demojize

class ConfirmButton(discord.ui.View):
	def __init__(self, member: Union[discord.User, discord.Member], timeout: int = 180):
		super().__init__(timeout=timeout)
		self.member = member
		self.value = None
		self.interaction = None

	# When the confirm button is pressed, set the inner value to `True` and
	# stop the View from listening to more input.
	# We also send the user an ephemeral message that we're confirming their choice.
	@discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
	async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.response.defer()
		self.value = True
		self.interaction = interaction
		self.stop()

	# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
	async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.response.defer()
		self.value = False
		self.interaction = interaction
		self.stop()

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		return self.member.id == interaction.user.id

# ===== Message-based =====

async def get_role_response(client, ctx, msg: discord.Message, member: discord.Member, embed: discord.Embed, channel: discord.TextChannel) -> Union[discord.Role, None]:
	""" Gets a role response from the user.
	:param ctx:
	:param msg:
	:param member:
	:param embed:
	:param channel: """

	while True:
		try:
			m = await client.wait_for(
				'message', timeout=60, check=lambda m: m.author.id == member.id and m.channel.id == channel.id
			)
		except asyncio.TimeoutError:
			embed.description = "**Timeout!**"
			embed.color = discord.Color.red()
			await msg.edit(embed=embed)
			return None

		else:
			try:
				content = m.content.strip().title()
				converter = commands.RoleConverter()
				role = await converter.convert(ctx, content)
			except discord.ext.commands.errors.RoleNotFound:
				await channel.send(f'**Invalid role, {member.mention}!**', delete_after=3)
				await m.delete()
				continue
			except Exception as e:
				print('===')
				print(e)
				print('===')
				continue
			else:
				await m.delete()
				return role

async def prompt_emoji_guild(client, member: discord.Member, channel: discord.TextChannel, limit: int = 100) -> str:
	""" Prompts an emoji to the user. """

	def msg_check(message):

		if message.author == member and message.guild:
			text_de = demojize(message.content)
			all_emojis = re.findall(r'[<]?[a]?:[!_\-\w]+:[0-9]{0,18}[>]?', text_de)
			all_emojis = list(set(all_emojis))

			client.loop.create_task(message.delete())
			
			if not all_emojis:
				client.loop.create_task(channel.send(f"**Please, inform at least 1 emoji in your message!**", delete_after=3))
				return False

			emoji = all_emojis[0]

			if len(emoji) <= limit:
				return True
			else:
				client.loop.create_task(channel.send(f"**Your emoji must be within {limit} characters!**", delete_after=3))
		else:
			return False
	try:
		message = await client.wait_for('message', timeout=240,
		check=msg_check)
	except asyncio.TimeoutError:
		await channel.send("**Timeout! Try again.**", delete_after=3)
		return None
	else:
		text_de = demojize(message.content)
		all_emojis = re.findall(r'[<]?[a]?:[!_\-\w]+:[0-9]{0,18}[>]?', text_de)
		all_emojis = list(set(all_emojis))
		emoji = all_emojis[0]
		return emojize(emoji)



async def prompt_message_guild(client, member: discord.Member, channel: discord.TextChannel, limit: int = 100) -> str:
	def msg_check(message):
		if message.author == member and message.guild:
			client.loop.create_task(message.delete())
			if len(message.content) <= limit:
				return True
			else:
				client.loop.create_task(channel.send(f"**Your answer must be within {limit} characters**", delete_after=3))
		else:
			return False
	try:
		message = await client.wait_for('message', timeout=240,
		check=msg_check)
	except asyncio.TimeoutError:
		await channel.send("**Timeout! Try again.**", delete_after=3)
		return None
	else:
		content = message.content
		return content


# ===== Reaction-based =====

async def prompt_number(client, channel: discord.TextChannel, member: discord.Member, limit: int = 1000) -> Union[int, None]:
	""" Prompts the user for a number.
	:param channel: The channel.
	:param member: The member that is gonna be prompted. """

	def check(m) -> bool:
		if m.author.id == member.id and channel.id == m.channel.id:
			client.loop.create_task(m.delete())
			if len(m.content.strip()) <= len(str(limit)):
				if m.content.strip().isdigit():
					if int(m.content.strip()) > 0 and int(m.content.strip()) <= limit:
						return True
					else:
						client.loop.create_task(channel.send(f"**The number has to be between 1-{limit}, {member.mention}!**", delete_after=3))
						return False
				else:
					client.loop.create_task(channel.send(f"**The number `MUST` be an integer value, {member.mention}!**", delete_after=3))
					return False
			else:
				client.loop.create_task(channel.send(f"**The number has a maximum length of 2, {member.mention}!**", delete_after=3))
				return False

		else:
			return False

	try:
		m = await client.wait_for('message', timeout=60, check=check)
		content = m.content
	except asyncio.TimeoutError:
		await channel.send("**Timeout!**", delete_after=3)
		return None
	else:
		return int(content)


class Confirm(menus.Menu):
	""" Reaction-role menu for confirming an action. """

	def __init__(self, msg, content: str = None):
		""" Class initializing method that inherits the parent's initializer. """

		super().__init__(timeout=60, delete_message_after=True, clear_reactions_after=True)

		self.content = content
		self.msg = msg
		self.result = None

	async def send_initial_message(self, ctx, channel) -> discord.Message:
		""" Sends the initial message. """

		self.sent_msg = await channel.send(content=self.content, embed=discord.Embed(description=self.msg, color=discord.Color.orange()))
		return self.sent_msg

	async def finalize(self, timed_out) -> None:
		""" Runs when it finalizes.
		:param timed_out: Whether it timed-out or not. """
		
		if timed_out:
			await self.sent_msg.edit(embed=discord.Embed(description="**Timeout!**", color=discord.Color.red()))

	def reaction_check(self, payload):
		"""The function that is used to check whether the payload should be processed.
		This is passed to :meth:`discord.ext.commands.Bot.wait_for <Bot.wait_for>`.
		There should be no reason to override this function for most users (But I'm not like most users).
		Parameters
		------------
		payload: :class:`discord.RawReactionActionEvent`
			The payload to check.
		Returns
		---------
		:class:`bool`
			Whether the payload should be processed.
		"""
		if payload.message_id != self.message.id:
			return False
		if payload.user_id != self._author_id:
			return False

		return payload.emoji in self.buttons

	@menus.button('\N{WHITE HEAVY CHECK MARK}')
	async def do_confirm(self, payload):
		""" Confirms action."""

		embed = self.sent_msg.embeds[0]
		embed.color = discord.Color.green()
		embed.title="Confirmed!"
		await self.sent_msg.edit(embed=embed)
		self.result = True
		self.stop()

	@menus.button('\N{CROSS MARK}')
	async def do_deny(self, payload):
		""" Denies action."""

		embed = self.sent_msg.embeds[0]
		embed.color = discord.Color.red()
		embed.title="Denied!"
		await self.sent_msg.edit(embed=embed)
		self.result = False
		self.stop()

	async def prompt(self, ctx):
		""" Prompts the question. """

		await self.start(ctx, wait=True)
		return self.result