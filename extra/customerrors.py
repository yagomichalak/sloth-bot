import discord
from discord.ext import commands

class NotInWhitelist(commands.CheckFailure): pass

class MissingRequiredSlothClass(commands.CheckFailure): 

	def __init__(self, required_class: str, error_message: str) -> None:
		self.required_class = required_class
		self.error_message = error_message

class ActionSkillOnCooldown(commands.CheckFailure): 

	def __init__(self, try_after: int, error_message: str) -> None:
		self.try_after = try_after
		self.error_message = error_message


class CommandNotReady(commands.CheckFailure): pass