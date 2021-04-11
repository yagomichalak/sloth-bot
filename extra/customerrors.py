import discord
from discord.ext import commands


class NotInWhitelist(commands.CheckFailure): pass


class MissingRequiredSlothClass(commands.CheckFailure):

    def __init__(self, required_class: str, error_message: str) -> None:
        self.required_class = required_class
        self.error_message = error_message


class ActionSkillOnCooldown(commands.CheckFailure):

    def __init__(self, try_after: int, error_message: str, cooldown: int = 86400) -> None:
        self.try_after = try_after
        self.error_message = error_message
        self.cooldown = cooldown


class CommandNotReady(commands.CheckFailure): pass


class SkillsUsedRequirement(commands.CheckFailure):

    def __init__(self, error_message: str) -> None:
        self.error_message = error_message
