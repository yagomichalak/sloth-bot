import discord
from discord.ext import commands, menus
from typing import Union, List
import asyncio

class ConfirmSkill(menus.Menu):
	""" Class related to confirmation skill actions. """

	def __init__(self, msg, content: str = None):
		""" Class initializing method that inherits the parent's initializer. """

		super().__init__(timeout=60, delete_message_after=False, clear_reactions_after=True)

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
		""" Confirms skill action."""

		embed = self.sent_msg.embeds[0]
		embed.color = discord.Color.green()
		embed.title="Confirmed!"
		await self.sent_msg.edit(embed=embed)
		self.result = True
		self.stop()

	@menus.button('\N{CROSS MARK}')
	async def do_deny(self, payload):
		""" Denies skill action."""

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



class InventoryLoop(menus.ListPageSource):
	""" A class for iterating through inventory items. """

	def __init__(self, data):
		super().__init__(data, per_page=6)

	async def format_page(self, menu, entries) -> discord.Embed:
		""" Formats the inventory for each page. """

		offset = menu.current_page * self.per_page

		embed = discord.Embed(
			title="__Inventory Items__",
			description="All your items gathered in one place.",
			color=menu.ctx.author.color,
			timestamp=menu.ctx.message.created_at
		)
		embed.set_thumbnail(url=menu.ctx.author.avatar_url)

		for i, v in enumerate(entries, start=offset):
			embed.add_field(name=f"{i+1}. {v[1]}", value=f"**State:** `{v[2]}`\n**Kind:** `{v[3]}`", inline=True)
			embed.set_footer(text=f"({i+1}-{i+1+6} of {len(self.entries)})")

		return embed

class OpenShopLoop(menus.ListPageSource):
	""" A class for iterating through inventory items. """

	def __init__(self, data):
		super().__init__(data, per_page=6)

	async def format_page(self, menu, entries) -> discord.Embed:
		""" Formats the inventory for each page. """

		offset = menu.current_page * self.per_page

		embed = discord.Embed(
			title="__Sloth Class Shop Items__",
			description="All available shop items.\n**To buy a potion, use: `z!buy_potion @member`**",
			color=menu.ctx.author.color,
			timestamp=menu.ctx.message.created_at
		)
		embed.set_author(name=menu.ctx.author, icon_url=menu.ctx.author.avatar_url)

		for i, v in enumerate(entries, start=offset):
			embed.add_field(name=f"{i+1}.", value=f"**Merchant:** <@{v[0]}>\n**Item Price:** `{v[7]}`", inline=True)
			embed.set_footer(text=f"({i+1}-{i+6} of {len(self.entries)})")

		return embed


async def prompt_message(client, member: discord.Member, channel: discord.TextChannel, limit: int = 100) -> str:
	def msg_check(message):
		if message.author == member and not message.guild:
			if len(message.content) <= limit:
				return True
			else:
				client.loop.create_task(channel.send(f"**Your answer must be within {limit} characters**"))
		else:
			return False
	try:
		message = await client.wait_for('message', timeout=240, 
		check=msg_check)
	except asyncio.TimeoutError:
		await channel.send("**Timeout! Try again.**")
		return None
	else:
		content = message.content
		return content


async def prompt_number(client, ctx: commands.Context, the_msg: discord.Message, member: discord.Member, limit: int = 1000) -> Union[int, None]:
	""" Prompts the user for a number.
	:param ctx: The context.
	:param member: The member that is gonna be prompted. """


	def check(m) -> bool:
		if m.author.id == member.id and msg.channel.id == m.channel.id:
			if len(m.content.strip()) <= len(str(limit)):
				if m.content.strip().isdigit():
					if int(m.content.strip()) > 0 and int(m.content.strip()) <= limit:
						return True
					else:
						client.loop.create_task(ctx.send(f"**The number has to be between 1-{limit}, {member.mention}!**"))	
						return False
				else:
					client.loop.create_task(ctx.send(f"**The number `MUST` be an integer value, {member.mention}!**"))	
					return False
			else:
				client.loop.create_task(ctx.send(f"**The number has a maximum lenght of 2, {member.mention}!**"))
				return False

		else:
			return False


	msg = await ctx.send(embed=discord.Embed(
		description=the_msg, 
		color=member.color, 
		timestamp=ctx.message.created_at))

	try:
		m = await client.wait_for('message', timeout=60, check=check)
		content = m.content
	except asyncio.TimeoutError:
		await msg.edit(content="**Timeout!**")
		return None
	else:
		return int(content)


class InroleLooping(menus.ListPageSource):
	def __init__(self, members, **kwargs):
		super().__init__(members, per_page=15)
		self.role = kwargs.get('role')

	async def format_page(self, menu, entries):
		start = menu.current_page * self.per_page
		embed = discord.Embed(
			title=f"__{self.role}__ ({self.role.id})",
			description=f'\n'.join(f"`{i+1}` - **{v}**" for i, v in enumerate(entries, start=start)),
			color=self.role.color,
			timestamp=menu.ctx.message.created_at
			)
		for i, v in enumerate(entries, start=start):
			embed.set_footer(text=f"({i+1}-{i+6} of {len(self.entries)})")


		return embed