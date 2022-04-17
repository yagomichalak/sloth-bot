import discord
import enum
from typing import Callable
from .quests_callbacks import *

class QuestEnum(enum.Enum):
    """ Class for the Quests enum. """

    one: Callable = lambda args: args
    twice: Callable = lambda args: args
    three: Callable = lambda args: args
    four: Callable = lambda args: args
    five: Callable = lambda args: args
    six: Callable = quest_six_callback