---
icon: lucide/spade
---

# Blackjack

Blackjack is a card game where players must try to beat the dealer by getting a hand as close to 21 as possible without going over.

## Structure

Code relating to blackjack is stored under `casino/games/blackjack/`. The overall structure of the folder is given below.

```
blackjack/
├── variants/
│   ├── __init__.py
│   └── standard.py
├── views/
│   ├── __init__.py
│   └── view.py
├── __init__.py
├── base.py
├── constants.py
└── hand.py
```

| Path | Purpose |
|-------|---|
| `base.py` | The core game loop shared by every variant (betting, dealing, player turns, payouts). |
| `hand.py` | Tracks a single hand's cards, bet, and result. |
| `constants.py` | Static text and configuration used throughout the game (headers, prompts, messages). |
| `variants/` | Rulesets for different types of blackjack. Each variant overrides only the steps that differ. |
| `views/` | Contains all terminal rendering and input. Game logic should always call a function from `views/` when rendering UI. |
| `__init__.py` | Public exports for the package. |

`base.py`, the base class for Blackjack, contains 8 functions.

| Step | Function | Description |
|:---:|---|---|
| 1 | `Blackjack.bet()` | Users place bets. Take placed bet amount from users |
| 2 | `Blackjack.deal_cards()` | Deal cards to users |
| 3 | `Blackjack.blackjack_check()` | Check if players or dealer has blackjack. Offer insurance. |
| 4 | `Blackjack.player_decision()` | Player chooses desired moves during round |
| 5 | `Blackjack.dealer_draw()` | Dealer draws once every player has busted or stands |
| 6 | `Blackjack.check_win()` | Check which player has won |
| 7 | `Blackjack.payout()` | Pay players who won or tied the appropriate amount |
| 8 | `Blackjack.display_results()` | Show who won or lost |

It is recommended to call the functions in that order when implementing new variants.

### Variants

There are currently two variants:

- Standard Blackjack
- European Blackjack

At the end of a round, choose **M** to return to game selection and choose
another game. Choosing **N** ends the casino session.
