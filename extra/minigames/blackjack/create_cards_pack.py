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

cards_pack = []
# Create a standard 52-card deck
for card_type, number, points in zip(card_types, numbers, pointss):
    symbol = '`' + number + card_type + '`'
    cards_pack.append(Card(card_type, number, points, symbol))