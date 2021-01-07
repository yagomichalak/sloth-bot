import discord
from discord.ext import commands

class NotInWhitelist(commands.CheckFailure): pass

class MissingRequiredSlothClass(commands.CheckFailure): 

	def __init__(self, required_class: str, error_message: str) -> None:
		self.required_class = required_class
		self.error_message = error_message