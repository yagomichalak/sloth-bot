import discord
from discord.ext import commands

from extra.prompt.menu import ConfirmButton, prompt_number
from extra.roleselection.db_commands import RoleSelectionDatabaseCommands
from extra.roleselection.utils import callback as button_callback
from extra.view import BasicUserCheckView
from extra.buttons import ValueButton

from typing import List
from functools import partial



class ManageRoleSelectionMenu(discord.ui.View):
	""" View for handling the Role Selection menu's editing action buttons """
	
	def __init__(self, client, message: discord.Message) -> None:
		super().__init__(timeout=60)
		self.client = client
		self.message = message
		self.db = RoleSelectionDatabaseCommands

	@discord.ui.button(style=discord.ButtonStyle.success, label="Add Button", custom_id="add_selection_menu_button")
	async def add_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		""" Adds a button to an existing drop-down menu. """

		await interaction.response.defer()
		member = interaction.user
		view_menu = discord.ui.View.from_message(self.message, timeout=None)

		ctx = await self.client.get_context(interaction.message)
		ctx.author = member
		cog = self.client.get_cog('RoleSelection')

		selects = await self.db.get_selection_menus_by_message_id_and_placeholder(self.message.id)
		initial_view = BasicUserCheckView(member, 180)

		# Creates button options for selecting the drop-down in which to add new select options
		for i, select in enumerate(selects):
			initial_view.add_item(ValueButton(
				style=discord.ButtonStyle.blurple, label=f"{i} - {select[6]}", custom_id=f"select_select_{i}_id"))

		# Prompts user the select to use
		initial_msg = await ctx.send("Select a select", view=initial_view)
		await initial_view.wait()
		if initial_view.value is None:
			return
		await initial_msg.delete()

		for child in view_menu.children:
			child.callback = partial(RoleSelect.callback, child)

		placeholder = view_menu.children[initial_view.value].placeholder


		self.stop()
		# Loops creation of select options
		while True:

			select_configs = await cog.ask_select_questions(ctx, self.message)
			if not select_configs:
				break
			
			view_menu.children[initial_view.value].options.append(discord.SelectOption(**select_configs))

			try:
				await self.db.insert_menu_select(self.message.id, self.message.channel.id, self.message.guild.id, *select_configs.values(), placeholder)
			except Exception as e:
				print(e)
				await interaction.channel.send(f"**I couldn't add your button to the database, {member.mention}!**", delete_after=5)
			else:
				await self.message.edit(view=view_menu)
				self.client.add_view(view=view_menu)

			view = ConfirmButton(member)
			embed = discord.Embed(description=f"**Wanna add more options into your select menu, {member.mention}?**", color=member.color)
			msg = await interaction.channel.send(embed=embed, view=view)
			
			
			await view.wait()
			await msg.delete()
			if view.value is None or not view.value:
				break
			
		await self.message.channel.send("**Menu updated!**", delete_after=5)

	@discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Option", custom_id="delete_select_option_menu_button")
	async def delete_select_option(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		""" Deletes a specific item/option from a specific select drop-down. """

		await interaction.response.defer()
		self.stop()

		member = interaction.user
		ctx = await self.client.get_context(interaction.message)
		ctx.author = member

		view_menu = discord.ui.View.from_message(self.message, timeout=None)

		selects = await self.db.get_selection_menus_by_message_id_and_placeholder(self.message.id)
		initial_view = BasicUserCheckView(member, 180)

		# Makes a view with the select options
		for i, select in enumerate(selects):
			initial_view.add_item(ValueButton(
				style=discord.ButtonStyle.blurple, label=f"{i} - {select[6]}", custom_id=f"select_select_{i}_id"))

		initial_msg = await ctx.send("Select a select", view=initial_view)
		await initial_view.wait()
		if initial_view.value is None:
			return
		await initial_msg.delete()

		chosen_select = view_menu.children[initial_view.value]
		options = view_menu.children[initial_view.value].options

		options_text: List[str] = [
			f"`{i+1}`: ({child.emoji}) {child.label} <@&{int(child.value)}>" 
			for i, child in enumerate(options)
		]

		if not options_text:
			return await interaction.channel.send(f"**You have no options in this menu yet, {member.mention}!**", delete_after=3)

		embed = discord.Embed(
			title="__Available Select Options in this Menu__",
			description='\n'.join(options_text),
			color=member.color,
			timestamp=self.message.created_at
		)
		embed.set_footer(text=f"Menu: {self.message.id}")
		
		# Asks user the option to delete
		del_btn_msg = await interaction.channel.send(f"**What select option do you want to delete, {member.mention}?**", embed=embed)
		number = await prompt_number(self.client, interaction.channel, member, limit=len(options))
		if not number:
			return
		
		await del_btn_msg.delete()

		view = ConfirmButton(member)
		chosen_option = options[number-1]
		embed = discord.Embed(
			description=f"""**Are you sure you want to delete the button with label `{chosen_option.label}`,
			with the <@&{chosen_option.value}> role attached to it, {member.mention}?**"""
		)

		msg = await interaction.channel.send(embed=embed, view=view)
		# Wait for the View to stop listening for input...
		await view.wait()
		if view.value is None:
			await interaction.channel.send(f"**Timeout, {member.mention}!**", delete_after=5)

		elif view.value:
			chosen_select.options.remove(chosen_option)
			if not chosen_select.options:
				view_menu.children.pop(initial_view.value)

			for child in view_menu.children:
				child.callback = partial(RoleSelect.callback, child)
			
			try:
				await self.db.delete_menu_select(
					self.message.id, self.message.channel.id, self.message.guild.id, chosen_option.value)
			except Exception as e:
				await interaction.channel.send(f"**I couldn't remove your button from the database, {member.mention}!**", delete_after=5)
			else:
				await self.message.edit(view=view_menu)
				self.client.add_view(view=view_menu, message_id=self.message.id)

			await interaction.channel.send(f"**Menu successfully deleted, {member.mention}!**", delete_after=5)
		else:
			await interaction.channel.send(f"**Not deleting it then, {member.mention}!**", delete_after=5)

		await msg.delete()

	@discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Select", custom_id="delete_select_dropdown_menu")
	async def delete_select_dropdopwn_menu(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		""" Deletes a specific select drop-down from the Role Selection menu. """
		
		await interaction.response.defer()
		member = interaction.user
		ctx = await self.client.get_context(interaction.message)
		ctx.author = member

		view_menu = discord.ui.View.from_message(self.message, timeout=None)
		selects = await self.db.get_selection_menus_by_message_id_and_placeholder(self.message.id)
		initial_view = BasicUserCheckView(member, 180)

		for i, select in enumerate(selects):
			initial_view.add_item(ValueButton(
				style=discord.ButtonStyle.blurple, label=f"{i} - {select[6]}", custom_id=f"select_select_{i}_id"))

		initial_msg = await ctx.send("Which select do you wanna delete?", view=initial_view)
		await initial_view.wait()
		if initial_view.value is None:
			return
		await initial_msg.delete()

		view = ConfirmButton(member)
		self.stop()
		msg = await interaction.channel.send(
			f"**Are you sure you want to delete the `{initial_view.value}#` select, {member.mention}?**", view=view)
		# Wait for the View to stop listening for input...
		await view.wait()
		await msg.delete()
		if view.value is None:
			await interaction.channel.send(f"**Timeout, {member.mention}!**", delete_after=5)
		elif view.value:
			
			try:
				placeholder = view_menu.children[initial_view.value].placeholder
				view_menu.children.pop(initial_view.value)

				for child in view_menu.children:
					child.callback = partial(RoleSelect.callback, child)

				
				await self.db.delete_selection_menu_by_message_id_and_placeholder(self.message.id, self.message.guild.id, placeholder)
				await self.message.edit(view=view_menu)
				self.client.add_view(view=view_menu, message_id=self.message.id)
				await interaction.channel.send(f"**Select `{initial_view.value}#` successfully deleted, {member.mention}!**", delete_after=5)
			except Exception as e:
				print(e)
				await interaction.channel.send(f"**For some reason I couldn't delete this select, {member.mention}!**")

		else:
			await interaction.channel.send(f"**Not deleting it then, {member.mention}!**", delete_after=5)


	@discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Menu", custom_id="delete_whole_selection_menu")
	async def delete_menu(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		""" Deletes the whole Selection Role menu, including the original message. """
		
		await interaction.response.defer()
		member = interaction.user
		view = ConfirmButton(member)
		self.stop()
		msg = await interaction.channel.send(
			f"**Are you sure you want to delete this menu, {member.mention}?**", view=view)
		# Wait for the View to stop listening for input...
		await view.wait()
		if view.value is None:
			await interaction.channel.send(f"**Timeout, {member.mention}!**", delete_after=5)
		elif view.value:
			await self.db.delete_selection_menu_by_message_id(self.message.id, self.message.guild.id)
			await self.message.delete()
			await interaction.channel.send(f"**Menu successfully deleted, {member.mention}!**", delete_after=5)
		else:
			await interaction.channel.send(f"**Not deleting it then, {member.mention}!**", delete_after=5)

		try:
			await msg.delete()
		except:
			pass
		

	@discord.ui.button(style=discord.ButtonStyle.secondary, label="Cancel", custom_id="cancel_selection_menu")
	async def cancel_menu(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		self.stop()



# ===== Button-based =====
class RoleSelect(discord.ui.Select):
	""" Handles clicks in the selection drop-down menus,
	giving users the role attached to the select option. """

	async def callback(self, interaction: discord.Interaction) -> None:

		member = interaction.user
		await interaction.response.defer()
		for value in interaction.data['values']:

			try:
				role = discord.utils.get(member.guild.roles, id=int(value))
			except Exception as e:
				print('error', e)
				pass
			else:
				member_roles_ids = [r.id for r in member.roles]
				if role and role.id not in member_roles_ids:
					native_roles = [r for r in member.roles if r.name.lower().startswith('native')]
					if role.name.lower().startswith('native') and len(native_roles) >= 2:
						await interaction.followup.send(f"**You cannot have more than 2 native roles at a time!**", ephemeral=True)
					else:
						await member.add_roles(role)
						await interaction.followup.send(f"**The `{role}` role was assigned to you!**", ephemeral=True)
					
				else:
					await member.remove_roles(role)
					await interaction.followup.send(f"**The `{role}` role was taken away from you!**", ephemeral=True)

				await interaction.message.edit(view=self.view)
