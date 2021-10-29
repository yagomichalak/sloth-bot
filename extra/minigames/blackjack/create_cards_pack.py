class Card:
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
symbols = [
    "<:ASpade:861377742066286632>",
    "<:2Spade:861377740681510912>",
    "<:3Spade:861377740698550282>",
    "<:4Spade:861377740737609728>",
    "<:5Spade:861377740828311573>",
    "<:6Spade:861377740825296908>",
    "<:7Spade:861377740682166293>",
    "<:8Spade:861377741610024980>",
    "<:9Spade:861377741135282197>",
    "<:10Spade:861377741752631296>",
    "<:JSpade:861377741748305950>",
    "<:QSpade:861377742012809236>",
    "<:KSpade:861377741525090335>",

    "<:ADiamond:861377742003634187>",
    "<:2Diamond:861377740623839242>",
    "<:3Diamond:861377740623970324>",
    "<:4Diamond:861377740695797780>",
    "<:5Diamond:861377740414124063>",
    "<:6Diamond:861377740829491210>",
    "<:7Diamond:861377740897124423>",
    "<:8Diamond:861377740615712769>",
    "<:9Diamond:861377741521551380>",
    "<:10Diamond:861377741411713024>",
    "<:JDiamond:861377741529939998>",
    "<:QDiamond:861377742058422312>",
    "<:KDiamond:861377741513031710>",

    "`A♥`",
    "<:2Heart:861377740624232488>",
    "<:3Heart:861377740442828821>",
    "<:4Heart:861377740707725342>",
    "<:5Heart:861377740871434261>",
    "<:6Heart:861377740825296907>",
    "<:7Heart:861377740838404106>",
    "<:8Heart:861377741043662868>",
    "<:9Heart:861377741076955199>",
    "<:10Heart:861377741416169472>",
    "<:JHeart:861377741222969376>",
    "`Q♥`",
    "<:KHeart:861377741546061824>",

    "<:AClub:861377742109016134>"
    "<:2Club:861377740619776030>",
    "<:3Club:861377740639961088>",
    "<:4Club:861377740687409192>",
    "<:5Club:861377740875497472>",
    "<:6Club:861377740766838784>",
    "<:7Club:861377740795543562>",
    "<:8Club:861377740863045632>",
    "<:9Club:861377741437403156>",
    "<:10Club:861377741391134740>",
    "`J♠`",
    "<:QClub:861377741752500225>",
    "<:KClub:861377741344210985>"
]

cards_pack = []
# Create a standard 52-card deck
for card_type, number, points, symbol in zip(card_types, numbers, pointss, symbols):
    # symbol = '`' + number + card_type + '`'
    cards_pack.append(Card(card_type, number, points, symbol))