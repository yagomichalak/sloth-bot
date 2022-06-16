import discord
import enum
from typing import Callable
from .quests_callbacks import *

class QuestEnum(enum.Enum):
    """ Class for the Quests enum. """

    one: Callable = quest_one_callback
    two: Callable = quest_two_callback
    three: Callable = quest_three_callback
    four: Callable = quest_four_callback
    five: Callable = quest_five_callback
    six: Callable = quest_six_callback
    seven: Callable = quest_seven_callback
    ten: Callable = quest_ten_callback