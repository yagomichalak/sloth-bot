import discord
from discord.ext import commands

from extra.prompt.menu import ConfirmButton, prompt_number, Confirm
from extra.roleselection.db_commands import RoleSelectionDatabaseCommands
from extra.roleselection.utils import callback as button_callback

from functools import partial



class ManageRoleSelectionMenu(discord.ui.View):
	
	def __init__(self, client, message: discord.Message) -> None:
		super().__init__(timeout=60)
		self.client = client
		self.message = message
		self.db = RoleSelectionDatabaseCommands

	@discord.ui.button(style=discord.ButtonStyle.success, label="Add Button", custom_id="add_selection_menu_button")
	async def add_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

		await interaction.response.defer()
		member = interaction.user
		view_menu = discord.ui.View.from_message(self.message, timeout=None)

		ctx = await self.client.get_context(interaction.message)
		ctx.author = member
		cog = self.client.get_cog('RoleSelection')
		# print('\n'.join([f"button: {btn.label} custom id {btn.custom_id}" for btn in view.children]))



		self.stop()
		while True:

			button_configs = await cog.ask_button_questions(ctx, self.message)
			if not button_configs:
				break

			view_menu.add_item(RoleButton(**button_configs))
			for child in view_menu.children:
				child.callback = partial(button_callback, child)

			try:
				await self.db.insert_menu_button(self.message.id, self.message.channel.id, self.message.guild.id, *button_configs.values())
			except Exception as e:
				print(e)
				await interaction.channel.send(f"**I couldn't add your button to the database, {member.mention}!**", delete_after=5)
			else:
				await self.message.edit(view=view_menu)
				self.client.add_view(view=view_menu) # Maybe delete this line later

			view = ConfirmButton(member)
			embed = discord.Embed(description=f"**Wanna add more buttons into your menu, {member.mention}?**", color=member.color)
			msg = await interaction.channel.send(embed=embed, view=view)
			
			
			await view.wait()
			await msg.delete()
			if view.value is None or not view.value:
				break
			
		await self.message.channel.send("**Menu updated!**", delete_after=5)

	@discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Button", custom_id="delete_selection_menu_button")
	async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

		await interaction.response.defer()
		self.stop()

		member = interaction.user
		view_menu = discord.ui.View.from_message(self.message, timeout=60)		

		buttons_text = [f"`{i+1}`: ({child.emoji}) {child.label} <@&{child.custom_id}>" for i, child in enumerate(view_menu.children)]

		if not buttons_text:
			return await interaction.channel.send(f"**You have no buttons in this menu yet, {member.mention}!**", delete_after=3)

		embed = discord.Embed(
			title="__Available Buttons in this Menu__",
			description='\n'.join(buttons_text),
			color=member.color,
			timestamp=self.message.created_at
		)
		embed.set_footer(text=f"Menu: {self.message.id}")
		
		await interaction.channel.send(f"**What button you want to delete, {member.mention}?**", embed=embed)
		number = await prompt_number(self.client, interaction.channel, member, limit=len(view_menu.children))
		if not number:
			return

		view = ConfirmButton(member)
		chosen_button = view_menu.children[number-1]
		embed = discord.Embed(
			description=f"""**Are you sure you want to delete the button with label `{chosen_button.label}`,
			with the <@&{chosen_button.custom_id}> role attached to it, {member.mention}?**"""
		)

		msg = await interaction.channel.send(embed=embed, view=view)
		# Wait for the View to stop listening for input...
		await view.wait()
		if view.value is None:
			await interaction.channel.send(f"**Timeout, {member.mention}!**", delete_after=5)
		elif view.value:
			view_menu.children = [
				child for child in view_menu.children 
				if child != chosen_button
			]

			for child in view_menu.children:
				child.callback = partial(button_callback, child)
			
			try:
				await self.db.delete_menu_button(
					self.message.id, self.message.channel.id, self.message.guild.id, chosen_button.custom_id)
			except Exception as e:
				await interaction.channel.send(f"**I couldn't remove your button from the database, {member.mention}!**", delete_after=5)
			else:
				await self.message.edit(view=view_menu)
				await self.client.add_view(view=view_menu, message_id=self.message.id)

			await interaction.channel.send(f"**Menu successfully deleted, {member.mention}!**", delete_after=5)
		else:
			await interaction.channel.send(f"**Not deleting it then, {member.mention}!**", delete_after=5)

		await msg.delete()

	@discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Menu", custom_id="delete_whole_selection_menu")
	async def delete_menu(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
		
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
class RoleButton(discord.ui.Button):

	# def __init__(self, **kwargs) -> None:
	# 	super().__init__(kwargs)


	async def callback(self, interaction: discord.Interaction) -> None:

		member = interaction.user

		try:
			role = discord.utils.get(member.guild.roles, id=int(self.custom_id))
		except Exception as e:
			print(e)
			pass
		else:
			member_roles_ids = [r.id for r in member.roles]
			if role and role.id not in member_roles_ids:
				await member.add_roles(role)
				await interaction.response.send_message(f"**The `{role}` role was assigned to you!**", ephemeral=True)
			else:
				await member.remove_roles(role)
				await interaction.response.send_message(f"**The `{role}` role was taken away from you!**", ephemeral=True)
