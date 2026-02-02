"""UNO game implementation."""
import random
from typing import Optional, Literal
from dataclasses import dataclass

from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar
from casino.uno_cards import uno_card_dict
from .constants import (
    COLORS, COLOR_CODES, NUMBER_CARDS, ACTION_CARDS, WILD_CARDS,
    INITIAL_HAND_SIZE, NUM_AI_PLAYERS, HEADER_OPTIONS
)


@dataclass
class Card:
    """Represents a UNO card."""
    color: Optional[str]  # None for wild cards
    value: str | int

    def __str__(self) -> str:
        if self.color is None:
            return f"Wild {self.value}"
        return f"{self.color.title()} {self.value}"

    def get_card_id(self) -> str:
        """Get the card ID for looking up in uno_card_dict."""
        if self.color is None:
            return str(self.value)
        color_code = COLOR_CODES[self.color]
        return f"{color_code}{self.value}"

    def can_play_on(self, other: "Card", chosen_color: Optional[str] = None) -> bool:
        """Check if this card can be played on another card."""
        # Wild cards can always be played
        if self.color is None:
            return True

        # If the previous card was wild, check against chosen color
        if other.color is None and chosen_color:
            return self.color == chosen_color

        # Otherwise check color or value match
        return self.color == other.color or self.value == other.value


class Deck:
    """UNO deck manager."""

    def __init__(self):
        self.cards: list[Card] = []
        self.discard_pile: list[Card] = []
        self._initialize_deck()

    def _initialize_deck(self):
        """Create a standard UNO deck."""
        # Number cards (0-9) - one 0 per color, two of each 1-9
        for color in COLORS:
            self.cards.append(Card(color, 0))
            for value in NUMBER_CARDS[1:]:
                self.cards.append(Card(color, value))
                self.cards.append(Card(color, value))

        # Action cards - two of each per color
        for color in COLORS:
            for action in ACTION_CARDS:
                self.cards.append(Card(color, action))
                self.cards.append(Card(color, action))

        # Wild cards - four of each
        for _ in range(4):
            self.cards.append(Card(None, "wild"))
            self.cards.append(Card(None, "wild+4"))

        self.shuffle()

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> list[Card]:
        """Draw cards from the deck."""
        drawn = []
        for _ in range(count):
            if not self.cards:
                # Reshuffle discard pile if deck is empty
                if len(self.discard_pile) > 1:
                    top_card = self.discard_pile.pop()
                    self.cards = self.discard_pile[:]
                    self.discard_pile = [top_card]
                    self.shuffle()
                else:
                    break  # No more cards available
            if self.cards:
                drawn.append(self.cards.pop())
        return drawn

    def play_card(self, card: Card):
        """Add a card to the discard pile."""
        self.discard_pile.append(card)

    def get_top_card(self) -> Optional[Card]:
        """Get the top card of the discard pile."""
        return self.discard_pile[-1] if self.discard_pile else None


class Player:
    """Represents a UNO player."""

    def __init__(self, name: str, is_ai: bool = False):
        self.name = name
        self.hand: list[Card] = []
        self.is_ai = is_ai
        self.said_uno = False

    def draw_cards(self, cards: list[Card]):
        """Add cards to hand."""
        self.hand.extend(cards)
        if len(self.hand) != 1:
            self.said_uno = False

    def play_card(self, card: Card) -> bool:
        """Remove card from hand if present."""
        if card in self.hand:
            self.hand.remove(card)
            if len(self.hand) == 1:
                self.said_uno = True
            return True
        return False

    def has_playable_card(self, top_card: Card, chosen_color: Optional[str] = None) -> bool:
        """Check if player has any playable cards."""
        return any(card.can_play_on(top_card, chosen_color) for card in self.hand)


class UnoGame:
    """Main UNO game logic."""

    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.deck = Deck()
        self.players: list[Player] = []
        self.current_player_idx = 0
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.chosen_color: Optional[str] = None
        self.game_over = False

    def setup_game(self):
        """Initialize the game."""
        # Create players
        self.players.append(Player(self.ctx.account.name, is_ai=False))
        for i in range(NUM_AI_PLAYERS):
            self.players.append(Player(f"AI {i+1}", is_ai=True))

        # Deal initial hands
        for player in self.players:
            player.draw_cards(self.deck.draw(INITIAL_HAND_SIZE))

        # Flip first card (make sure it's not a wild or action card)
        first_card = self.deck.draw(1)[0]
        while first_card.color is None or first_card.value in ACTION_CARDS:
            self.deck.cards.insert(0, first_card)
            self.deck.shuffle()
            first_card = self.deck.draw(1)[0]
        self.deck.play_card(first_card)

    def next_player(self, skip: bool = False):
        """Move to the next player."""
        if skip:
            self.current_player_idx = (self.current_player_idx + 2 * self.direction) % len(self.players)
        else:
            self.current_player_idx = (self.current_player_idx + self.direction) % len(self.players)

    def reverse_direction(self):
        """Reverse the play direction."""
        self.direction *= -1

    def get_current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_idx]

    def display_game_state(self, message: str = ""):
        """Display the current game state."""
        clear_screen()
        display_topbar(self.ctx.account, **HEADER_OPTIONS)

        top_card = self.deck.get_top_card()
        if top_card:
            cprint(f"\n{'='*50}")
            cprint(f"Top Card: {top_card}")
            if self.chosen_color:
                cprint(f"Current Color: {self.chosen_color.title()}")
            cprint(f"{'='*50}\n")

        # Show other players' hand sizes
        cprint("Other Players:")
        for i, player in enumerate(self.players):
            if i != self.current_player_idx:
                uno_status = " (UNO!)" if len(player.hand) == 1 else ""
                cprint(f"  {player.name}: {len(player.hand)} cards{uno_status}")

        cprint("")

        if message:
            cprint(f"\n{message}\n")

    def display_hand(self, player: Player):
        """Display player's hand."""
        cprint(f"\n{player.name}'s Hand ({len(player.hand)} cards):")
        for i, card in enumerate(player.hand, 1):
            cprint(f"  [{i}] {card}")

    def choose_color(self, player: Player) -> str:
        """Let player choose a color for wild card."""
        if player.is_ai:
            # AI picks random color from their hand, or just random
            colors_in_hand = [c.color for c in player.hand if c.color]
            if colors_in_hand:
                return random.choice(colors_in_hand)
            return random.choice(COLORS)

        cprint("\nChoose a color:")
        for i, color in enumerate(COLORS, 1):
            cprint(f"  [{i}] {color.title()}")

        while True:
            choice = cinput("Enter choice (1-4): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 4:
                return COLORS[int(choice) - 1]
            cprint("Invalid choice. Please enter 1-4.")

    def _handle_action_card(self, card: Card, player: Player) -> bool:
        """
        Handle action card effects. Returns True if turn should end immediately.
        """
        if card.value == "skip":
            self.next_player(skip=True)
            return True
        elif card.value == "reverse":
            self.reverse_direction()
            return False
        elif card.value == "+2":
            self.next_player()
            next_player = self.get_current_player()
            next_player.draw_cards(self.deck.draw(2))
            self.display_game_state(f"{next_player.name} drew 2 cards!")
            cinput("\nPress Enter to continue...")
            return True
        elif card.value == "wild+4":
            self.next_player()
            next_player = self.get_current_player()
            next_player.draw_cards(self.deck.draw(4))
            self.display_game_state(f"{next_player.name} drew 4 cards!")
            cinput("\nPress Enter to continue...")
            return True
        return False

    def _process_played_card(self, card: Card, player: Player) -> bool:
        """
        Process a played card (wild colors, action effects, win check).
        Returns True if game should continue, False if game over.
        """
        # Handle wild cards
        if card.color is None:
            self.chosen_color = self.choose_color(player)
            if player.is_ai:
                cprint(f"{player.name} chose {self.chosen_color.title()}!")
                cinput("\nPress Enter to continue...")
        else:
            self.chosen_color = None

        # Check win condition
        if len(player.hand) == 0:
            self.game_over = True
            winner_msg = "\nCongratulations! You win!" if not player.is_ai else f"\n{player.name} wins!"
            self.display_game_state(winner_msg)
            if not player.is_ai:
                cinput("\nPress Enter to continue...")
            return False

        # Handle action cards
        return not self._handle_action_card(card, player)

    def ai_turn(self, player: Player) -> bool:
        """Execute AI player's turn. Returns True if game should continue."""
        top_card = self.deck.get_top_card()
        if not top_card:
            return False

        # Find playable cards
        playable_cards = [c for c in player.hand if c.can_play_on(top_card, self.chosen_color)]

        if playable_cards:
            # AI plays first playable card
            card_to_play = playable_cards[0]
            player.play_card(card_to_play)
            self.deck.play_card(card_to_play)

            self.display_game_state(f"{player.name} played: {card_to_play}")
            cinput("\nPress Enter to continue...")

            return self._process_played_card(card_to_play, player)
        else:
            # AI draws a card
            drawn = self.deck.draw(1)
            if drawn:
                player.draw_cards(drawn)
                self.display_game_state(f"{player.name} drew a card.")
                cinput("\nPress Enter to continue...")

        return True

    def human_turn(self, player: Player) -> bool:
        """Execute human player's turn. Returns True if game should continue."""
        top_card = self.deck.get_top_card()
        if not top_card:
            return False

        while True:
            self.display_game_state()
            self.display_hand(player)

            # Find playable cards
            playable_cards = [c for c in player.hand if c.can_play_on(top_card, self.chosen_color)]

            if playable_cards:
                cprint("\n[D] Draw a card")
                cprint("[Q] Quit game")
                choice = cinput("\nEnter card number to play, or D/Q: ").strip().lower()

                if choice == 'q':
                    return False
                elif choice == 'd':
                    drawn = self.deck.draw(1)
                    if drawn:
                        player.draw_cards(drawn)
                        cprint(f"\nYou drew: {drawn[0]}")
                        cinput("Press Enter to continue...")
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(player.hand):
                        card_to_play = player.hand[idx]
                        if card_to_play.can_play_on(top_card, self.chosen_color):
                            player.play_card(card_to_play)
                            self.deck.play_card(card_to_play)
                            return self._process_played_card(card_to_play, player)
                        else:
                            cprint("\nYou can't play that card!")
                            cinput("Press Enter to continue...")
                    else:
                        cprint("\nInvalid card number!")
                        cinput("Press Enter to continue...")
            else:
                cprint("\nYou have no playable cards. You must draw.")
                cinput("Press Enter to draw a card...")
                drawn = self.deck.draw(1)
                if drawn:
                    player.draw_cards(drawn)
                    cprint(f"\nYou drew: {drawn[0]}")

                    # Check if drawn card is playable
                    if drawn[0].can_play_on(top_card, self.chosen_color):
                        cprint("This card is playable!")
                        play_it = cinput("Play it now? (y/n): ").strip().lower()
                        if play_it == 'y':
                            player.play_card(drawn[0])
                            self.deck.play_card(drawn[0])
                            return self._process_played_card(drawn[0], player)
                    else:
                        cinput("Press Enter to continue...")
                break

        return True

    def play(self):
        """Main game loop."""
        self.setup_game()

        while not self.game_over:
            current_player = self.get_current_player()

            if current_player.is_ai:
                if not self.ai_turn(current_player):
                    break
            else:
                if not self.human_turn(current_player):
                    break

            if not self.game_over:
                self.next_player()


def play_uno(ctx: GameContext) -> None:
    """Entry point for UNO game."""
    game = UnoGame(ctx)
    game.play()
