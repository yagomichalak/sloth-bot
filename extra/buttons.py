# import.thirdparty
import discord
from discord.ext import commands

class ValueButton(discord.ui.Button):
	""" Button class for returning a number value. """

	async def callback(self, interaction: discord.Interaction) -> None:

		self.view.value = self.view.children.index(self)
		self.view.stop()