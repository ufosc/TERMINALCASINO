from casino.cards import StandardDeck, Card

class BlackjackCore:
    """
    Handles the game state and rules logic. 
    Decoupled from UI to allow future refactoring of other variants.
    """
    def __init__(self, num_decks: int = 1):
        self.deck = StandardDeck(num_decks)
        self.player_hand: list[Card] = []
        self.dealer_hand: list[Card] = []
        
    def deal_card_to_player(self):
        self.player_hand.append(self.deck.draw())

    def deal_card_to_dealer(self):
        self.dealer_hand.append(self.deck.draw())

    def reset_hands(self):
        self.player_hand = []
        self.dealer_hand = []

    def get_hand_total(self, hand: list[Card]) -> int:
        """Calculates the blackjack value of a hand."""
        total = 0
        aces = 0
        for card in hand:
            if card.rank in {"J", "Q", "K"}:
                total += 10
            elif card.rank == "A":
                total += 11
                aces += 1
            else:
                total += int(card.rank)
        
        while aces > 0 and total > 21:
            total -= 10
            aces -= 1
        return total

    @property
    def player_total(self) -> int:
        return self.get_hand_total(self.player_hand)

    @property
    def dealer_total(self) -> int:
        return self.get_hand_total(self.dealer_hand)

    def is_blackjack(self, hand: list[Card]) -> bool:
        return self.get_hand_total(hand) == 21 and len(hand) == 2

    def is_busted(self, hand: list[Card]) -> bool:
        return self.get_hand_total(hand) > 21