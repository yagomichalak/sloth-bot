import discord
from discord.ext import commands, menus

from extra.prompt.menu import Confirm, prompt_number, prompt_emoji_guild, prompt_message_guild, get_role_response

from extra.roleselection.db_commands import RoleSelectionDatabaseCommands
from extra.roleselection.menu import RoleButton, ManageRoleSelectionMenu
from extra.prompt.menu import ConfirmButton
from extra.roleselection.utils import callback as button_callback

from functools import partial

from mysqldb import the_database
from typing import List, Dict, Union, Any


class RoleSelection(RoleSelectionDatabaseCommands):
	""" Category for creating, managing and interacting with
	role selection menus. """

	def __init__(self, client) -> None:
		self.client = client
		self.db = super()


	@commands.Cog.listener()
	async def on_ready(self) -> None:

		selection_menus = await self.get_selection_menus()
		messages = {}
		for button in selection_menus:
			try:
				if not messages.get(button[0]):
					messages[button[0]] = [button[3:]]
				else:
					messages[button[0]].append(button[3:])
			except Exception as e:
				print('error in roleseleciton', e)
		for message_id, buttons in messages.items():
			try:
				view = discord.ui.View(timeout=None)
				for button in buttons:
					view.add_item(RoleButton(style=button[0], label=button[1], emoji=button[2], custom_id=button[3]))

				# for child in view.children:
				#     child.callback = partial(button_callback, child)

				self.client.add_view(view=view, message_id=message_id)
			except Exception as e:
				print('ERROR IN RoleSelection', e)
			else:
				continue
			
		print('RoleSelection cog is online!')

	@commands.command(aliases=['create_menu', 'createmenu', 'make_menu', 'makemenu', 'startmenu'])
	@commands.has_permissions(administrator=True)
	async def start_menu(self, ctx, message_id: int = None) -> None:
		""" Creates a Button Role-Selection Menu.
		:param message_id: The ID of the message which is gonna be the menu. """

		await ctx.message.delete()
		member = ctx.author

		if not message_id:
			return await ctx.send(f"**Please, inform a `message ID`, {member.mention}!**", delete_after=5)
		
		msg = await ctx.channel.fetch_message(message_id)
		if not msg:
			return await ctx.send(f"**Message not found, {member.mention}!**", delete_after=5)

		view = discord.ui.View(timeout=None)
		while True:

			button_configs = await self.ask_button_questions(ctx, msg)
			if not button_configs:
				break
			
			view.add_item(RoleButton(**button_configs))

			try:
				await self.db.insert_menu_button(msg.id, msg.channel.id, msg.guild.id, *button_configs.values())
			except Exception as e:
				print(e)
				await ctx.send(f"**I couldn't add your button to the database, {member.mention}!**", delete_after=5)
			else:
				await msg.edit(view=view)

			await msg.edit(view=view)

			confirm_view = ConfirmButton(member)
			embed = discord.Embed(description=f"**Wanna add more buttons into your menu, {member.mention}?**", color=member.color)
			confirm_msg = await ctx.channel.send(embed=embed, view=confirm_view)
			
			
			await confirm_view.wait()
			await confirm_msg.delete()
			if confirm_view.value is None or not confirm_view.value:
				break


		self.client.add_view(view=view, message_id=msg.id)
		await ctx.send(f"**Menu successfully completed, {member.mention}!**", delete_after=5)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	async def edit_menu(self, ctx, message_id: int = None) -> None:
		""" Edits a Role Selection menu.
		:param message_id: The message ID of the selection menu. """

		member = ctx.author
		guild = ctx.guild

		await ctx.message.delete()

		if not message_id:
			return await ctx.send(f"**Please, inform a message ID, {member.mention}!**")

		selection_menu = await self.get_selection_menu(message_id, guild.id)
		if not selection_menu:
			return await ctx.send(f"**No menus with that ID were found, {member.mention}!**", delete_after=3)

		if not (channel := discord.utils.get(guild.text_channels, id=selection_menu[1])):
			await self.db.delete_selection_menu_by_channel_id(selection_menu[1], guild.id)
			return await ctx.send(f"**Channel and message of the Menu don't exist anymore, {member.mention}!**", delete_after=3)

		if not (message := await channel.fetch_message(selection_menu[0])):
			await self.db.delete_selection_menu_by_message_id(selection_menu[0], guild.id)
			return await ctx.send(f"**Message of the Menu doesn't exist anymore, {member.mention}!**", delete_after=3)
		
		embed = discord.Embed(
			title=f"__Editing Menu__ ({message_id})",
			color=member.color,
			timestamp=ctx.message.created_at
		)

		embed.set_author(name=guild.name, url=guild.icon.url, icon_url=guild.icon.url)
		embed.set_footer(text=f"Being edited by {member}", icon_url=member.avatar.url)

		view = ManageRoleSelectionMenu(self.client, message)

		msg = await ctx.send(embed=embed, view=view)
		try:
			await view.wait()
			await msg.delete()
		except:
			pass

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	async def see_menus(self, ctx) -> None:
		""" Displays all Role Selection menus from the server. """

		member = ctx.author
		guild = ctx.guild

		selection_menus = await self.get_selection_menus()
		messages = {}
		for button in selection_menus:
			if not messages.get(button[0]):
				messages[button[0]] = [1, button[1]]
			else:
				messages[button[0]][0] += 1

		message_text = [f"**`{menu[0]}`** buttons **-** <#{menu[1]}> (`{msg_id}`)" for msg_id, menu in messages.items()]

		embed = discord.Embed(
			title="__Menus Available__",
			description='\n'.join(message_text),
			color=member.color,
			timestamp=ctx.message.created_at
		)
		embed.set_author(name=guild.name, icon_url=guild.icon.url, url=guild.icon.url)
		embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar.url)

		await ctx.send(embed=embed)



	async def ask_button_questions(self, ctx: commands.Context, message: discord.Message) -> Dict[str, str]:

		member = ctx.author
		channel = ctx.channel

		# BTN Questions: style, label, emoji, role
		
		btn_configs: Dict[str, str] = {}

		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)

		# Question 1 - Style:
		embed.description = """
			**__Styles Available:__**
			
			**Primary**	1	blurple
			**Secondary**	2	grey
			**Success**	3	green
			**Danger**	4	red

			Type the number of the button stlye of your choice (1-4)
		"""

		initial_message = await ctx.send(embed=embed)
		
		style = await prompt_number(
			self.client, channel=channel,
			member=member, limit=4)

		if not style: 
			return False
		btn_configs['style'] = style

		# Question 2 - Label:
		embed.description = "**What is the label of your button?**"
		await initial_message.edit(embed=embed)
		label = await prompt_message_guild(self.client, member=member, channel=channel, limit=80)
		if not label: return False
		btn_configs['label'] = label

		# Question 3 - Emoji:
		embed.description = "**Type an emoji to attach to the button**"
		await initial_message.edit(embed=embed)
		emoji = await prompt_emoji_guild(self.client, member=member, channel=channel, limit=100)
		# emoji = await prompt_message_guild(self.client, member=member, channel=channel, limit=100)
		if not emoji: return False
		btn_configs['emoji'] = emoji

		# Question 4 - Role:
		embed.description = "**Type a role! (@role /role id/role name)**"
		await initial_message.edit(embed=embed)
		while True:
			role = await get_role_response(self.client, ctx, msg=initial_message, member=member, embed=embed, channel=channel)
			if not role: return False
			btn_configs['custom_id'] = str(role.id)

			if await self.db.get_button_by_id(str(role.id), message.id, message.guild.id):
				await ctx.send("**There is already a button with this role in this menu, type another role!**", delete_after=3)
			else:
				break

		await initial_message.delete()

		return btn_configs

		


def setup(client) -> None:
	client.add_cog(RoleSelection(client))