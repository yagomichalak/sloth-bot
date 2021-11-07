import discord
import enum
from typing import Callable, Any

class QuestEnum(enum.Enum):

    one: Callable = lambda args: args
    twice: Callable = lambda args: args
    three: Callable = lambda args: args
    four: Callable = lambda args: args
    five: Callable = lambda args: args
    six: Callable = lambda args: args