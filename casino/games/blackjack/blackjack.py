import random
from typing import Optional

from casino.card_assets import assign_card_art
from casino.cards import StandardCard, StandardDeck, Card
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

BLACKJACK_HEADER = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘
"""

BLACKJACK_HEADER_OPTIONS = {
    "header": BLACKJACK_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
DECK_NUMBER_SELECTION  = "🤵: How many decks would you like to play with?"
DECK_NUMBER_BOUNDS_MSG = "🤵: That won't work, please be serious. Try again."
INVALID_NUMBER_MSG     = "🤵: Invalid number. Try again."
INVALID_YES_OR_NO      = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
BET_PROMPT             = "🤵: How much would you like to bet?"
INVALID_BET_MSG        = "🤵: That's not a valid bet."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

FULL_DECK: StandardDeck = StandardDeck()
#add a class to represent each player's hand
class PlayerHand:
    def __init__(self, cards: list[Card], bet: int):
        self.cards = cards
        self.bet = bet
        self.is_finished = False
        self.is_doubled = False

def deal_card(turn: list[Card], deck: StandardDeck) -> None:
    """Deal a card to the player."""
    card = deck.draw()
    turn.append(card)

def double_down(ctx: GameContext, player_hand: list[Card], deck: StandardDeck, bet: int) -> int:
    account = ctx.account
    account.withdraw(bet)
    bet = bet * 2
    deal_card(player_hand, deck)
    return bet

def hand_total(turn: list[StandardCard]) -> int:
    """Calculate the total of each hand."""
    total = 0
    aces = 0
    for card in turn:
        if not isinstance(card, StandardCard):
            raise ValueError(f"Expected StandardCard, got {type(card)}")
        if card.rank in {"J", "Q", "K"}:
            # Face card
            total += 10
        elif card.rank == "A":
            # Ace special case
            total += 11
            aces += 1
        else:
            # Numeric card (2-10)
            total += int(card.rank)
    # Ace adjustment
    while aces > 0 and total > 21:
        total -= 10
        aces -= 1
    return total

def print_dealer_cards(dealer_hand: list[Card]) -> None:
    """Print the dealer's cards side by side."""
    if len(dealer_hand) == 0:
        cprint("")
    # first card shown, rest hidden
    first_card = dealer_hand[0].front
    hidden_card = dealer_hand[1].back
    hand_string = "\n".join([
        "  ".join(lines)
        for lines in zip(first_card.strip("\n").splitlines(),
                         hidden_card.strip("\n").splitlines())
    ])
    cprint(hand_string)


def print_cards(hand: list[Card]) -> None:
    """Print the cards side by side."""
    card_lines = [
        card.front.strip("\n").splitlines()
        for card in hand
    ]
    max_lines = max(len(lines) for lines in card_lines)

    # pad cards
    for lines in card_lines:
        while len(lines) < max_lines:
            lines.append(" " * len(lines[0]))

    # combine lines horizontally
    combined_lines = []
    for i in range(max_lines):
        combined_lines.append(
            "  ".join(card_lines[j][i] for j in range(len(hand)))
        )
    
    hand_string = "\n".join(combined_lines)
    cprint(hand_string)


def print_hand_total(hand: list[Card], label: str = "Total") -> None:
    """Print the total of the hand."""
    total = hand_total(hand)
    if total == 21 and len(hand) == 2:
        total_string = "Blackjack"
    else: 
        total_string = f"{total}"
    cprint(f"{label}: {total_string}")


def print_hand(hand: list[Card], hidden: bool = False) -> None:
    """Print a blackjack hand."""
    if hidden:
        print_dealer_cards(hand)
    else:
        print_cards(hand)
        print_hand_total(hand)

#define a new function to print dealer's hand and player's multiple hands
def print_all_hands(
        dealer_hand: list[Card],
        player_hands: list[PlayerHand],
        current_hand_index: int,
        hide_dealer: bool = True):
    cprint("Dealer hand: ")
    print_hand(dealer_hand, hidden = hide_dealer)
    cprint("-" * 30)

    for index, hand in enumerate(player_hands):
        if index == current_hand_index and not hand.is_finished:
            prefix = "👉  "
        else:
            prefix = "    "
        total = hand_total(hand.cards)
        status_info = ""
        if total > 21:
            status_info = " (BUSTED)"
        elif total == 21 and len(hand.cards) == 2:
            status_info = " (BLACKJACK)"
        cprint(f"{prefix}Player hand {index + 1} (Bet: {hand.bet}){status_info}")
        print_cards(hand.cards)
        print_hand_total(hand.cards, label="   Total")
        cprint("")



def display_blackjack_topbar(ctx: GameContext, bet: Optional[int]) -> None:
    display_topbar(ctx.account, **BLACKJACK_HEADER_OPTIONS)
    if bet is not None:
        cprint(f"Bet: {bet}")


def offer_insurance(ctx, bet, dealer_hand, player_hand, account):
    """Offers insurance when dealer shows Ace."""
    upcard = dealer_hand[0]
    if upcard.rank != "A":
        return 0, False
    
    # display hands
    cprint("Dealer hand:")
    print_hand(dealer_hand, hidden=True)
    cprint("Your hand:")
    print_hand(player_hand)

    cprint("Dealer shows an Ace.")
    cprint("Would you like to buy insurance?")

    choice = cinput(YES_OR_NO_PROMPT)
    while choice not in "YyNn" or choice == "":
        clear_screen()
        display_blackjack_topbar(ctx, bet)
        cprint(INVALID_YES_OR_NO)
        choice = cinput(YES_OR_NO_PROMPT)

    while choice in "Yy":
        max_bet = bet // 2
        insurance_bet_str = cinput(f"You can bet up to {max_bet} chips. How much would you like to bet for insurance?").strip()
        insurance_bet = 0
        try:
            insurance_bet = int(insurance_bet_str)
            if insurance_bet > max_bet:
                cprint(f"The maximum bet is {max_bet} chips.")
                continue
        except ValueError:
            cprint(INVALID_BET_MSG)
            continue
        try:
            account.withdraw(insurance_bet)
        except ValueError:
            cprint(f"Insufficient funds. You only have {account.balance} chips.")
            continue
        return insurance_bet, True # success

    return 0, False

def resolve_insurance_win(account, insurance_bet, insurance_taken):
    """Payout 2:1 insurance if dealer has blackjack."""
    if insurance_taken and insurance_bet > 0:
        # payout = return bet + 2× profit
        account.deposit(insurance_bet * 3)
        return f"Insurance pays out: +{insurance_bet * 2} chips\n"
    else:
        return ""

def resolve_insurance_loss(insurance_bet, insurance_taken):
    """Player loses insurance immediately when dealer does not have blackjack."""
    if insurance_taken and insurance_bet > 0:
        return f"You lose your insurance bet: -{insurance_bet} chips\n"
    else:
        return ""


def play_blackjack(ctx: GameContext) -> None:
    """Play a blackjack game."""
    account = ctx.account
    min_bet = ctx.config.blackjack_min_bet
    if account.balance < min_bet:
        clear_screen()
        display_blackjack_topbar(ctx, None)
        cprint(NO_FUNDS_MSG)
        cinput("Press enter to continue.")
        return
    continue_game = True
    stubborn = 0 # gets to 7 and you're out
    err_msg = None
    while (True):
        clear_screen()
        display_blackjack_topbar(ctx, None)
        # let user choose number of decks being dealt
        if err_msg is not None:
            cprint(err_msg)
        decks_str = cinput(DECK_NUMBER_SELECTION).strip()
        try:
            decks = int(decks_str)
        except ValueError:
            err_msg = INVALID_NUMBER_MSG
            continue
        if decks <= 0:
            err_msg = DECK_NUMBER_BOUNDS_MSG
            continue
        break

    while continue_game:
        # determine the bet amount
        initial_hand = True
        err_msg = None
        while True:
            clear_screen()
            display_blackjack_topbar(ctx, None)
            if err_msg is not None:
                cprint(err_msg)
            bet_str = cinput(BET_PROMPT).strip()
            try:
                bet = int(bet_str)
                if bet < min_bet:
                    err_msg = f"The minimum bet is {min_bet} chips."
                    continue
            except ValueError:
                err_msg = INVALID_BET_MSG
                continue
            try:
                initial_bet = bet
                account.withdraw(bet)
            except ValueError:
                err_msg = f"Insufficient funds. You only have {account.balance} chips."
                continue
            break

        clear_screen()
        display_blackjack_topbar(ctx, bet)

        # local variables
        player_status = True
        dealer_status = True
        player_bj = False
        dealer_bj = False

        # two decks of cards (values + string IDs)
        FULL_DECK = StandardDeck(decks)
        deck = FULL_DECK

        # hands
        player_hand = []
        dealer_hand = []

        # initial deal (player first)
        for _ in range(2):
            deal_card(player_hand, deck)
            deal_card(dealer_hand, deck)

        #initialize PlayerHand object
        player_hands = [PlayerHand(player_hand, initial_bet)]


        #insurance offered first hand change to player hands[0]
        insurance_bet, insurance_taken = offer_insurance(ctx, bet, dealer_hand, player_hand, account)

        # player BJ check
        if hand_total(player_hand) == 21:
            player_bj = True
            player_status = False

        # dealer BJ check
        if hand_total(dealer_hand) == 21:
            # dealer blackjack in initial deal
            dealer_bj = True
            player_status = False
            dealer_status = False
            cprint("Dealer hand:")
            print_hand(dealer_hand)
            cprint("Your hand:")
            print_hand(player_hand)

        # player turn
        current_hand_index = 0;

        # Change to a loop to play each hand of player hands
        while not dealer_bj and current_hand_index < len(player_hands):
            current_hand = player_hands[current_hand_index]
            if hand_total(current_hand.cards) >= 21:
                current_hand.is_finished = True
                current_hand_index += 1
                continue
            #check the condition for splitting
            #the player can split into maximum 4 hands
            #treat 10, J, Q, K equivalent to each other(i.e. 10+Q can be splitted)
            account = ctx.account
            can_split = (len(current_hand.cards) == 2 and len(player_hands) < 4
                         and account.balance >= current_hand.bet
                         and hand_total([current_hand.cards[0]])==hand_total([current_hand.cards[1]]))
            can_double = (len(current_hand.cards) == 2 and account.balance >= current_hand.bet)

            #call function print all hands
            clear_screen()
            display_blackjack_topbar(ctx, None)
            print_all_hands(dealer_hand, player_hands, current_hand_index, hide_dealer=True)

            #build prompt
            actions_str = "[S]tay   [H]it"
            actions = "SsHh"
            if can_double:
                actions_str += "   [D]ouble Down"
                actions += "Dd"
            if can_split:
                actions_str += "   S[p]lit"
                actions += "Pp"

            cprint(f"Playing hand {current_hand_index+1}...")


            # action choice input
            action = cinput(actions_str).strip().lower()

            # check valid answer
            while action not in actions or action == "":
                stubborn += 1
                if stubborn >= 13:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    return
                clear_screen()
                #do not show bet in top bar
                display_blackjack_topbar(ctx, None)
                cprint(INVALID_CHOICE_MSG + "\n")
                #call print all hands
                print_all_hands(dealer_hand, player_hands, current_hand_index,hide_dealer= True)
                action = cinput(actions_str).strip().lower()

            clear_screen()
            display_blackjack_topbar(ctx, None)
            #update logic for multiple player hands
            # handle action
            if action == "s":
                current_hand.is_finished = True
                current_hand_index += 1

            elif action == "h":
                deal_card(current_hand.cards, deck)

            elif action == "d":
                account.withdraw(current_hand.bet)
                current_hand.bet *= 2
                deal_card(current_hand.cards, deck)
                #according to game rule once double will finish the hand
                current_hand.is_finished = True
                current_hand_index += 1
                clear_screen()
                display_blackjack_topbar(ctx, None)

            #add splitting logic
            elif action == "p":
                cprint("Splitting hand...")
                account.withdraw(current_hand.bet)
                card_to_split = current_hand.cards.pop()
                new_hand = PlayerHand([card_to_split], current_hand.bet)
                deal_card(current_hand.cards, deck)
                deal_card(new_hand.cards, deck)
                player_hands.insert(current_hand_index + 1, new_hand)

            else:
                raise ValueError(f"Invalid choice: {action}")

            print_all_hands(dealer_hand,player_hands,current_hand_index,hide_dealer=True)

        # dealer turn
        #check if all player hands busted
        all_busted = True
        for hand in player_hands:
            if hand_total(hand.cards) <= 21:
                all_busted = False
                break
        if all_busted:
            dealer_status = False

        while dealer_status:
            dealer_total = hand_total(dealer_hand)
            # dealer status check/update
            if hand_total(dealer_hand) > 21 or hand_total(dealer_hand) > 16:
                # display hands
                #updated using print_all_hands
                clear_screen()
                display_blackjack_topbar(ctx,None)
                print_all_hands(dealer_hand,player_hands,-1,hide_dealer=False)
                dealer_status = False
            else:
                deal_card(dealer_hand, deck)
                clear_screen()
                display_blackjack_topbar(ctx, None)
                print_all_hands(dealer_hand, player_hands, -1, hide_dealer=False)
                import time
                time.sleep(2)#add pause between drawing cards


        ############## WIN CHECKS ##############
        #first print all cards
        clear_screen()
        display_blackjack_topbar(ctx, None)
        print_all_hands(dealer_hand, player_hands, -1, hide_dealer=False)

        cprint("\n------ Game Results ------")
        # insurance resolution
        if dealer_bj:
            insurance_msg = resolve_insurance_win(account, insurance_bet, insurance_taken)
            if insurance_msg:
                cprint(insurance_msg)
        else:
            insurance_msg = resolve_insurance_loss(insurance_bet, insurance_taken)
            if insurance_msg:
                cprint(insurance_msg)

        # main game resolution
        #use for loop to resolve each player hand
        dealer_total = hand_total(dealer_hand)

        for i, hand in enumerate(player_hands):
            current_hand_total = hand_total(hand.cards)
            current_bet = hand.bet
            current_hand_bj = (current_hand_total == 21 and len(hand.cards) == 2)
            prefix = f"Hand {i + 1}: "

            if current_hand_bj and dealer_bj:
                cprint(f"{prefix}Player and dealer both blackjack. Push.")
                account.deposit(current_bet)
                # player gets back bet, +1 draw

            elif not current_hand_bj and dealer_bj:
                cprint(f"{prefix}Dealer has a blackjack. You lose: -{current_bet} chips")
                # player loses bet, +1 loss

            elif current_hand_bj and not dealer_bj:
                cprint(f"{prefix}Player has a blackjack. You win: +{current_bet} chips")
                account.deposit(current_bet * 2)
                # player gets back 2x bet, +1 win, +1 bj counter

            elif current_hand_total > 21:
                cprint(f"{prefix}You busted. You lose: -{current_bet} chips")
                # player loses bet, +1 loss

            elif current_hand_total <= 21 and dealer_total > 21:
                cprint(f"{prefix}Dealer busted. You win: +{current_bet} chips")
                account.deposit(current_bet * 2)
                # player gets back 2x bet, +1 win

            elif current_hand_total == dealer_total:
                cprint(f"{prefix}Player and dealer have same total. Push.")
                account.deposit(current_bet)
                # player gets back bet, +1 draw

            elif current_hand_total < dealer_total:
                cprint(f"{prefix}Dealer wins. You lose: -{current_bet} chips")
                # player loses bet, +1 loss

            elif current_hand_total > dealer_total:
                cprint(f"{prefix}Player wins. You win: +{current_bet} chips")
                account.deposit(current_bet * 2)
                # player gets back 2x bet, +1 win

            else:
                raise ValueError(
                    f"Unaccounted for win condition! P: {current_hand_total} D: {dealer_total}"
                )
        print()


        # game restart?
        if account.balance < min_bet:
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
            display_blackjack_topbar(ctx, None)
            cprint(INVALID_YES_OR_NO)
            play_again = cinput(YES_OR_NO_PROMPT)

        # play / leave
        if play_again in "Nn":
            clear_screen()
            cprint(f"\nThanks for playing.\n\n")
            continue_game = False
