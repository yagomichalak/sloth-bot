# import.standard
import os
from typing import Dict

# import.local
from mysqldb import DatabaseCore
from . import (
    agares, cybersloth, merchant, metamorph,
    munk, prawler, seraph, warrior,
)

# variables.textchannel
bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))


classes: Dict[str, object] = {
    'agares': agares.Agares, 'cybersloth': cybersloth.Cybersloth,
    'merchant': merchant.Merchant, 'metamorph': metamorph.Metamorph,
    'munk': munk.Munk, 'prawler': prawler.Prawler,
    'seraph': seraph.Seraph, 'warrior': warrior.Warrior,
}


class Mastersloth(*classes.values()):

    emoji = '<:Mastersloth:1334707029159448628>'

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

        self.safe_categories = [
            int(os.getenv('LESSON_CAT_ID', 123)),
            int(os.getenv('CASE_CAT_ID', 123)),
            int(os.getenv('EVENTS_CAT_ID', 123)),
            int(os.getenv('DEBATE_CAT_ID', 123))
        ]
