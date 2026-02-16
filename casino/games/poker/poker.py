import random
import os
import shutil

from casino.card_assets import assign_card_art
from casino.cards import Deck, StandardDeck, StandardCard
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

from itertools import combinations
from collections import Counter


POKER_HEADER = """
┌───────────────────────────────┐
│         ♥ P O K E R ♥         │
└───────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": POKER_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
INVALID_YES_OR_NO_MSG  = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

FULL_DECK: StandardDeck = StandardDeck()


def deal_card(turn: list[StandardCard], deck: StandardDeck) -> None:
    """Deal a card to the player."""
    card = deck.draw()
    turn.append(card)

def hand_score(hand: list[StandardCard], board: list[StandardCard]) -> int:
    """Calculate the score of a poker hand."""

    all_cards = hand + board

    if len(all_cards) < 5:
        return get_partial_hand_score(all_cards)


    score=0
    for five_cards in combinations(hand + board, 5):
        current_score = evaluate_hand(list(five_cards))
        if current_score > score:
            score = current_score

    return score

def evaluate_hand(cards: list[StandardCard]) -> int:
    ranks = [get_card_value(card.rank) for card in cards]
    suits = [card.suit for card in cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    is_flush = 5 in suit_counts.values()
    is_straight = (len(rank_counts) == 5 and 
                   (max(ranks) - min(ranks) == 4 or 
                    set(ranks) == {14, 2, 3, 4, 5}))  # this is for the Ace-low straight (A, 2, 3, 4, 5)
    
    rank_counts = sorted(rank_counts.values(), reverse=True)

    if is_straight and is_flush:
        return 9  # Straight Flush
    elif rank_counts == [4, 1]:
        return 8  # Four of a Kind
    elif rank_counts == [3, 2]:
        return 7  # Full House
    elif is_flush:
        return 6  # Flush
    elif is_straight:
        return 5  # Straight
    elif rank_counts == [3, 1, 1]:
        return 4  # Three of a Kind
    elif rank_counts == [2, 2, 1]:
        return 3  # Two Pair
    elif rank_counts == [2, 1, 1, 1]:
        return 2  # One Pair
    else:
        return 1  # High Card

def get_partial_hand_score(hand: list[StandardCard]) -> int:
    """Evaluate hands with less than 5 cards"""
    if len(hand) < 2:
        return 1  # High Card
    
    ranks = [card.rank for card in hand]
    rank_counts = Counter(ranks)
    count_values = sorted(rank_counts.values(), reverse=True)

    if 4 in count_values:
        return 8  # Four of a Kind
    elif 3 in count_values:
        return 4
    elif count_values.count(2) == 2:
        return 3  # Two Pair
    elif 2 in count_values: 
        return 2  # One Pair
    else:
        return 1  # High Card


def get_card_value(rank: int | str) -> int:
    """Get the value of a rank."""
    if isinstance(rank, int):
        return rank
    if rank == "J":
        return 11
    if rank == "Q":
        return 12
    if rank == "K":
        return 13
    if rank == "A":
        return 14
    return int(rank)
    
def hand_name(score: int) -> str:
    """Get the name of a poker hand based on its score."""
    names = {
        9: "Straight Flush",
        8: "Four of a Kind",
        7: "Full House",
        6: "Flush",
        5: "Straight",
        4: "Three of a Kind",
        3: "Two Pair",
        2: "One Pair",
        1: "High Card"
    }
    return names.get(score, "Unknown Hand")

def print_game(ctx, stage: str, player_hand: list[StandardCard], opponent_hand: list[StandardCard], board: list[StandardCard], pot: int, message: str = "") -> None:
    clear_screen()
    display_poker_topbar(ctx)
    if message:
        cprint(message + "\n")
    cprint(f"=== {stage.upper()} ===\n")
    cprint("Opponent hand:")
    if stage != "SHOWDOWN":
        print_hand(opponent_hand, hidden=True)
    else:
        print_hand(opponent_hand, hidden=False)
    cprint("Board:")
    if len(board) == 0:
        cprint("No cards on the board yet.")
    else:
        print_hand(board)
    cprint("Your hand:")
    print_hand(player_hand)
    cprint(f"Your current hand type: {hand_name(hand_score(player_hand,board))}")
    cprint(f"Pot: {pot} chips")
    cprint(f"Your balance: {ctx.account.balance} chips\n")

def print_opponent_cards(opponent_hand: list[StandardCard]) -> None:
    """Print the opponent's cards face down."""
    if len(opponent_hand) == 0:
        cprint("")
        return
    
    hidden_cards = [card.back for card in opponent_hand]
    hand_string = "\n".join([
        "  ".join(lines)
        for lines in zip(*[card.strip("\n").splitlines() for card in hidden_cards])
    ])
    cprint(hand_string)

def print_cards(hand: list[StandardCard]) -> None:
    """Print the cards side by side."""
    if len(hand) == 0:
        return
    card_lines = [
        card.front.strip("\n").splitlines()
        for card in hand
    ]
    max_lines = max(len(lines) for lines in card_lines)

    for lines in card_lines:
        while len(lines) < max_lines:
            lines.append(" " * len(lines[0]))

    combined_lines = []
    for i in range(max_lines):
        combined_lines.append(
            "  ".join(card_lines[j][i] for j in range(len(hand)))
        )
    
    hand_string = "\n".join(combined_lines)
    cprint(hand_string)



def print_hand(hand: list[StandardCard], hidden: bool = False) -> None:
    """Print a blackjack hand."""
    if hidden:
        print_opponent_cards(hand)
    else:
        print_cards(hand)

def display_poker_topbar(ctx: GameContext) -> None:
    display_topbar(ctx.account, **HEADER_OPTIONS)

def get_and_validate_raise_amount(min_raise, account_balance, current_bet: int = 0):
    raise_amount = cinput("Raise amount:")
    try:
        raise_amount_int = int(raise_amount)
        if raise_amount_int <= 0:
            return None, "🤵: Raise must be positive number"
        if raise_amount_int < min_raise:
            return None, f"🤵: Raise must be at least {min_raise}"
        required = current_bet + raise_amount_int
        if account_balance < required:
            return None, "🤵: You don't have enough chips to raise that much."
        return raise_amount_int, ""
    except ValueError:
        return None,  "🤵: Raise amount must be number"

def play_poker(ctx: GameContext) -> None:
    """Play a poker game."""
    account = ctx.account
    min_raise = ctx.config.poker_min_raise
    if account.balance < 20:
        clear_screen()
        display_poker_topbar(ctx)
        cprint(NO_FUNDS_MSG)
        cinput("Press enter to continue.")
        return
    continue_game = True
    stubborn = 0 # gets to 7 and you're out

    while continue_game:
        clear_screen()
        display_poker_topbar(ctx)
        
        player_status = True
        opponent_status = True
        player_chips = 1000
        opponent_chips = 1000
        pot = 10 # small blind 
        current_bet = 20 #  + big blind (10 + 20)
        player_folded = False

        deck = FULL_DECK

        player_hand = []
        opponent_hand = []
        board = []

        #first deal of the game
        for _ in range(2):
            deal_card(player_hand, deck)
            deal_card(opponent_hand, deck)

        while player_status and opponent_status:
            print_game(ctx, "PRE-FLOP", player_hand, opponent_hand, board, pot)

            action = cinput(f"[F]old   [C]all {current_bet}   [R]aise\n")
            raise_amount = 0

            #get a proper action from the player
            while action not in "FfCcRr" or action == "" or (action.lower() == "r") or (action.lower() == "c" and account.balance < current_bet):
                stubborn += 1
                if stubborn >= 7:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    cprint("You have been banned from the casino for being too stubborn.")
                    return

                if (action.lower() == "r"):
                    raise_amount, validation_msg = get_and_validate_raise_amount(min_raise, account.balance, current_bet)
                    if validation_msg:
                        print_game(ctx, "PRE-FLOP", player_hand, opponent_hand, board, pot, validation_msg)
                    else:
                        break

                if (action.lower() == "c" and account.balance < current_bet):
                    print_game(ctx, "PRE-FLOP", player_hand, opponent_hand, board, pot, f"🤵: You don't have enough chips to call {current_bet}.")
                if action not in "FfCcRr" or action == "":
                    print_game(ctx, "PRE-FLOP", player_hand, opponent_hand, board, pot, INVALID_CHOICE_MSG + "\n")
                
                action = cinput(f"[F]old   [C]all {current_bet}   [R]aise\n")

            clear_screen()
            display_poker_topbar(ctx)

            if action.lower() == "f":
                player_folded = True
                player_status = False
                opponent_status = False
            elif action.lower() == "c":
                account.withdraw(current_bet)
                pot += current_bet
                player_status = False
            elif action.lower() == "r":
                current_bet += raise_amount
                account.withdraw(current_bet)
                pot += current_bet

                # as of right now, i will make the bot always call a raise
                opponent_chips -= current_bet
                pot += current_bet
                player_status = False
            else:
                raise ValueError(f"Invalid choice: {action}")
            
        # flop
        if not player_folded:
            
            # burn a card (standard in most casinos)
            deck.draw()

            # deal flop (3 cards)
            for _ in range(3):
                deal_card(board, deck)
            
            print_game(ctx, "FLOP", player_hand, opponent_hand, board, pot)

            action = cinput("[F]old   [C]heck   [R]aise\n")
            raise_amount = 0

            while action not in "FfCcRr" or action == "" or (action.lower() == "r"):
                if (action.lower() == "r"):
                    raise_amount, validation_msg = get_and_validate_raise_amount(min_raise, account.balance)
                    if validation_msg:
                        print_game(ctx, "FLOP", player_hand, opponent_hand, board, pot, validation_msg)
                    else:
                        break
                stubborn += 1
                if stubborn >= 7: 
                    clear_screen()
                    cprint(SECURITY_MSG)
                    return
                action = cinput("[F]old   [C]heck   [R]aise\n")
            current_bet = 0
            if action.lower() == "f":
                player_folded = True
                player_status = False
                opponent_status = False
            elif action.lower() == "c":
                account.withdraw(current_bet)
                pot += current_bet
                player_status = False
            elif action.lower() == "r":
                current_bet += raise_amount
                account.withdraw(current_bet)
                pot += current_bet

                # as of right now, i will make the bot always call a raise
                opponent_chips -= 50
                pot += 50
                player_status = False
            

        #turn
        if not player_folded:
            
            # burn a card (standard in most casinos)
            deal_card([], deck)

            # deal turn (1 card)
            deal_card(board, deck)

            print_game(ctx, "TURN", player_hand, opponent_hand, board, pot)

            action = cinput("[F]old   [C]heck   [R]aise\n")
            raise_amount = 0
            while action not in "FfCcRr" or action == "" or (action.lower() == "r"):
                if (action.lower() == "r"):
                    raise_amount, validation_msg = get_and_validate_raise_amount(min_raise, account.balance)
                    if validation_msg:
                        print_game(ctx, "TURN", player_hand, opponent_hand, board, pot, validation_msg)
                    else:
                        break
                stubborn += 1
                if stubborn >= 7:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    return
                action = cinput("[F]old   [C]heck   [R]aise\n")
            current_bet = 0
            if action.lower() == "f":
                player_folded = True
                player_status = False
                opponent_status = False
            elif action.lower() == "c":
                account.withdraw(current_bet)
                pot += current_bet
                player_status = False
            elif action.lower() == "r":
                current_bet += raise_amount
                account.withdraw(current_bet)
                pot += current_bet

                # as of right now, i will make the bot always call a raise
                opponent_chips -= 50
                pot += 50
                player_status = False
        
        
        #river
        if not player_folded:
            # burn a card (standard in most casinos)
            deck.draw()

            # deal river (1 card)
            deal_card(board, deck)

            print_game(ctx, "RIVER", player_hand, opponent_hand, board, pot)

            action = cinput("[F]old   [C]heck   [R]aise\n")
            raise_amount = 0
            while action not in "FfCcRr" or action == "" or (action.lower() == "r"):
                if (action.lower() == "r"):
                    raise_amount, validation_msg = get_and_validate_raise_amount(min_raise, account.balance)
                    if validation_msg:
                        print_game(ctx, "RIVER", player_hand, opponent_hand, board, pot, validation_msg)
                    else:
                        break
                stubborn += 1
                if stubborn >= 7:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    return
                action = cinput("[F]old   [C]heck   [R]aise\n")
            current_bet = 0
            if action.lower() == "f":
                player_folded = True
                player_status = False
                opponent_status = False
            elif action.lower() == "c":
                account.withdraw(current_bet)
                pot += current_bet
                player_status = False
            elif action.lower() == "r":
                current_bet += raise_amount
                account.withdraw(current_bet)
                pot += current_bet

                # as of right now, i will make the bot always call a raise
                opponent_chips -= 50
                pot += 50
                player_status = False

        #showdown
        if not player_folded:
            print_game(ctx, "SHOWDOWN", player_hand, opponent_hand, board, pot)

            player_score = hand_score(player_hand, board)
            opponent_score = hand_score(opponent_hand, board)

            if player_score > opponent_score:
                cprint(f"You win with a {hand_name(player_score)}!")
                account.deposit(pot)
            elif opponent_score > player_score:
                cprint(f"Opponent wins with a {hand_name(opponent_score)}.")
                opponent_chips += pot
            else:
                cprint(f"It's a tie with both players having a {hand_name(player_score)}.")
                account.deposit(pot//2)
                opponent_chips += pot // 2
                
            cprint(f"Your balance: {account.balance} chips\n")
        else:
            clear_screen()
            display_poker_topbar(ctx)
            cprint("You folded. Opponent wins the pot.")
            opponent_chips += pot
            cprint(f"Your balance: {account.balance} chips\n")
        
        # Regenerate the deck (i.e. return all cards to deck and shuffle)
        deck.generate_deck()
        
        # game restart?
        if account.balance < 20: # The starting bet pre-flop
            cprint(NO_FUNDS_MSG)
            cinput("Press enter to continue.")
            continue_game = False
            continue
        cprint(STAY_AT_TABLE_PROMPT)
        play_again = cinput(YES_OR_NO_PROMPT)
        # check valid answer
        while play_again not in "YyNn" or play_again == "":
            stubborn += 1
            if stubborn >= 13:
                clear_screen()
                cprint(SECURITY_MSG)
                return
            clear_screen()
            display_poker_topbar(ctx)
            cprint(INVALID_YES_OR_NO_MSG)
            play_again = cinput(YES_OR_NO_PROMPT)

        # play / leave
        if play_again in "Nn":
            clear_screen()
            cprint(f"\nThanks for playing.\n\n")
            continue_game = False
