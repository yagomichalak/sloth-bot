class Card:
    # Create a card object
    def __init__(self, card_type_arg: str, number_arg: str, points_arg: int, symbol_arg: str):
        self.card_type = card_type_arg
        self.points = points_arg
        self.number = number_arg
        self.symbol = symbol_arg
        self.original_symbol = symbol_arg

class Card2:
    # Create a card object
    def __init__(self, card_type_arg: str, number_arg: str, points_arg: int, symbol_arg: str):
        self.card_type = card_type_arg
        self.points = points_arg
        self.number = number_arg
        self.symbol = symbol_arg
        self.original_symbol = symbol_arg

card_types = ['♣'] * 13 + ['♦'] * 13 + ['♥'] * 13 + ['♠'] * 13
numbers = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
pointss = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

cards_pack = []
# Create a standard 52-card deck
for card_type, number, points in zip(card_types, numbers, pointss):
    symbol = '`' + number + card_type + '`'
    cards_pack.append(Card(card_type, number, points, symbol))

cards = {
    "A": {
        "points": 11,
        "symbols": {
            "heart": {"symbol": "<:Aheart:980639174497554472>", "original_symbol": "<:Aheart:980639174497554472>"},
            "diamond": {"symbol": "<:Adiamond:980639174346543104>", "original_symbol": "<:Adiamond:980639174346543104>"},
            "spades": {"symbol": "<:Aspades:980639174132650035>", "original_symbol": "<:Aspades:980639174132650035>"},
            "club": {"symbol": "<:Aclub:980639174333980683>", "original_symbol": "<:Aclub:980639174333980683>"},
        }
    },
    "2": {
        "points": 2,
        "symbols": {
            "heart": {"symbol": "<:2heart:980639174153605161>", "original_symbol": "<:2heart:980639174153605161>"},
            "diamond": {"symbol": "<:2diamond:980639174111686746>", "original_symbol": "<:2diamond:980639174111686746>"},
            "spades": {"symbol": "<:2spades:980639174212321300>", "original_symbol": "<:2spades:980639174212321300>"},
            "club": {"symbol": "<:2club:980639174149414912>", "original_symbol": "<:2club:980639174149414912>"},
        }
    },
    "3": {
        "points": 3,
        "symbols": {
            "heart": {"symbol": "<:3heart:980639174308802620>", "original_symbol": "<:3heart:980639174308802620>"},
            "diamond": {"symbol": "<:3diamond:980639174241697862>", "original_symbol": "<:3diamond:980639174241697862>"},
            "spades": {"symbol": "<:3spades:980639174187167744>", "original_symbol": "<:3spades:980639174187167744>"},
            "club": {"symbol": "<:3club:980639174233317427>", "original_symbol": "<:3club:980639174233317427>"},
        }
    },
    "4": {
        "points": 4,
        "symbols": {
            "heart": {"symbol": "<:4heart:980639174275260466>", "original_symbol": "<:4heart:980639174275260466>"},
            "diamond": {"symbol": "<:4diamond:980639174019407963>", "original_symbol": "<:4diamond:980639174019407963>"},
            "spades": {"symbol": "<:4spades:980639174195560499>", "original_symbol": "<:4spades:980639174195560499>"},
            "club": {"symbol": "<:4club:980639174103298049>", "original_symbol": "<:4club:980639174103298049>"},
        }
    },
    "5": {
        "points": 5,
        "symbols": {
            "heart": {"symbol": "<:5heart:980639174304595979>", "original_symbol": "<:5heart:980639174304595979>"},
            "diamond": {"symbol": "<:5diamond:980639173897773110>", "original_symbol": "<:5diamond:980639173897773110>"},
            "spades": {"symbol": "<:5spades:980639174254268446>", "original_symbol": "<:5spades:980639174254268446>"},
            "club": {"symbol": "<:5club:980639174266875904>", "original_symbol": "<:5club:980639174266875904>"},
        }
    },
    "6": {
        "points": 6,
        "symbols": {
            "heart": {"symbol": "<:6heart:980639174258475049>", "original_symbol": "<:6heart:980639174258475049>"},
            "diamond": {"symbol": "<:6diamond:980639174287839262>", "original_symbol": "<:6diamond:980639174287839262>"},
            "spades": {"symbol": "<:6spades:980639174480769074>", "original_symbol": "<:6spades:980639174480769074>"},
            "club": {"symbol": "<:6club:980639174413656145>", "original_symbol": "<:6club:980639174413656145>"},
        }
    },
    "7": {
        "points": 7,
        "symbols": {
            "heart": {"symbol": "<:7heart:980639174333956116>", "original_symbol": "<:7heart:980639174333956116>"},
            "diamond": {"symbol": "<:7diamond:980639174262665226>", "original_symbol": "<:7diamond:980639174262665226>"},
            "spades": {"symbol": "<:7spades:980639174329790466>", "original_symbol": "<:7spades:980639174329790466>"},
            "club": {"symbol": "<:7club:980639174271041546>", "original_symbol": "<:7club:980639174271041546>"},
        }
    },
    "8": {
        "points": 8,
        "symbols": {
            "heart": {"symbol": "<:8heart:980639174317195365>", "original_symbol": "<:8heart:980639174317195365>"},
            "diamond": {"symbol": "<:8diamond:980639174279438396>", "original_symbol": "<:8diamond:980639174279438396>"},
            "spades": {"symbol": "<:8spades:980639174338179072>", "original_symbol": "<:8spades:980639174338179072>"},
            "club": {"symbol": "<:8club:980642846229016626>", "original_symbol": "<:8club:980642846229016626>"},
        }
    },
    "9": {
        "points": 9,
        "symbols": {
            "heart": {"symbol": "<:9heart:980639174346563674>", "original_symbol": "<:9heart:980639174346563674>"},
            "diamond": {"symbol": "<:9diamond:980639174455599134>", "original_symbol": "<:9diamond:980639174455599134>"},
            "spades": {"symbol": "<:9spades:980639174468182016>", "original_symbol": "<:9spades:980639174468182016>"},
            "club": {"symbol": "<:9club:980639174044561479>", "original_symbol": "<:9club:980639174044561479>"},
        }
    },
    "10": {
        "points": 10,
        "symbols": {
            "heart": {"symbol": "<:10heart:980639174484963358>", "original_symbol": "<:10heart:980639174484963358>"},
            "diamond": {"symbol": "<:10diamond:980639174321393704>", "original_symbol": "<:10diamond:980639174321393704>"},
            "spades": {"symbol": "<:10spades:980639174589816842>", "original_symbol": "<:10spades:980639174589816842>"},
            "club": {"symbol": "<:10club:980639174380105798>", "original_symbol": "<:10club:980639174380105798>"},
        }
    },
    "J": {
        "points": 10,
        "symbols": {
            "heart": {"symbol": "<:Jheart:980639174422069338>", "original_symbol": "<:Jheart:980639174422069338>"},
            "diamond": {"symbol": "<:Jdiamond:980639174354935848>", "original_symbol": "<:Jdiamond:980639174354935848>"},
            "spades": {"symbol": "<:Jspades:980639174367526952>", "original_symbol": "<:Jspades:980639174367526952>"},
            "club": {"symbol": "<:Jclub:980639174623391824>", "original_symbol": "<:Jclub:980639174623391824>"},
        }
    },
    "Q": {
        "points": 10,
        "symbols": {
            "heart": {"symbol": "<:Qheart:980639174652743720>", "original_symbol": "<:Qheart:980639174652743720>"},
            "diamond": {"symbol": "<:Qdiamond:980639174317187132>", "original_symbol": "<:Qdiamond:980639174317187132>"},
            "spades": {"symbol": "<:Qspades:980639174438830130>", "original_symbol": "<:Qspades:980639174438830130>"},
            "club": {"symbol": "<:Qclub:980642815363121182>", "original_symbol": "<:Qclub:980642815363121182>"},
        }
    },
    "K": {
        "points": 10,
        "symbols": {
            "heart": {"symbol": "<:Kheart:980639174317199370>", "original_symbol": "<:Kheart:980639174317199370>"},
            "diamond": {"symbol": "<:Kdiamond:980639174354935818>", "original_symbol": "<:Kdiamond:980639174354935818>"},
            "spades": {"symbol": "<:Kspades:980639174350741554>", "original_symbol": "<:Kspades:980639174350741554>"},
            "club": {"symbol": "<:Kclub:980639174392676382>", "original_symbol": "<:Kclub:980639174392676382>"},
        }
    }
}

wj_pack = []
for number, card in cards.items():
    for symbol in card["symbols"]:
        card_symbol = card["symbols"][symbol]
        wj_pack.append(Card2(card_symbol["symbol"], number, card["points"], card_symbol["original_symbol"]))
