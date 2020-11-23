import discord
from discord.ext import commands
import os
from cogs.slothcurrency import SlothCurrency

class RoleTexts(commands.Cog):
	""" A class focused on giving members a text
	when they get a new role. """

	def __init__(self, client) -> None:
		""" Class initializing method. """

		self.client = client

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to use. """

		print('RoleTexts cog is online!')
		# await SlothCurrency.text_download_update(self.client)


	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		""" When the member is assigned to a new role,
		it gives them a respective text to that role,
		if there is any. """

		if not after.guild:
			return

		# Checks whether the member was assigned to a new role
		roles = before.roles
		roles2 = after.roles
		if len(roles2) <= len(roles):
			return

		# Gets the role that was assigned to the member
		new_role = None
		for r2 in roles2:
			if r2 not in roles:
				new_role = r2.name
				break
		else:
			return

		path = f"./texts/languages/{new_role.replace(' ', '_').lower()}.txt"
		if os.path.exists(path):
			# Reads text
			role_text = await self.read_text(path)
			# Makes the embed
			embed = discord.Embed(
				title=new_role,
				description=role_text,
				color=after.color
			)
			# Sends to user
			try:
				await after.send(embed=embed)
			except:
				pass

	async def read_text(self, path) -> str:
		""" Reads a text file. 
		:param path: The path of the file to read. """

		with open(path, 'r') as f:
			lines = f.read()
			return lines

def setup(client) -> None:
	""" Cog's setup function. """

	client.add_cog(RoleTexts(client))