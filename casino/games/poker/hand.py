from itertools import combinations
from collections import Counter

from casino.cards import StandardCard


def get_card_value(rank: int | str) -> int:
    """Get the numeric value of a card rank."""
    if isinstance(rank, int):
        return rank

    face_values = {
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14
    }

    if rank in face_values:
        return face_values[rank]

    return int(rank)


def evaluate_hand(cards: list[StandardCard]) -> int:
    """Score a 5-card hand. Returns an integer 1-9."""
    ranks = [get_card_value(card.rank) for card in cards]
    suits = [card.suit for card in cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    is_flush = 5 in suit_counts.values()

    is_straight = (
        len(rank_counts) == 5 and
        (
            max(ranks) - min(ranks) == 4
            or set(ranks) == {14, 2, 3, 4, 5}
        )
    )

    count_values = sorted(rank_counts.values(), reverse=True)

    if is_straight and is_flush:
        return 9
    elif count_values == [4, 1]:
        return 8
    elif count_values == [3, 2]:
        return 7
    elif is_flush:
        return 6
    elif is_straight:
        return 5
    elif count_values == [3, 1, 1]:
        return 4
    elif count_values == [2, 2, 1]:
        return 3
    elif count_values == [2, 1, 1, 1]:
        return 2
    else:
        return 1


def get_partial_hand_score(hand: list[StandardCard]) -> int:
    """Evaluate hands with fewer than 5 cards."""
    if len(hand) < 2:
        return 1

    rank_counts = Counter(card.rank for card in hand)
    count_values = sorted(rank_counts.values(), reverse=True)

    if 4 in count_values:
        return 8
    elif 3 in count_values:
        return 4
    elif count_values.count(2) == 2:
        return 3
    elif 2 in count_values:
        return 2

    return 1


def hand_score(
    hand: list[StandardCard],
    board: list[StandardCard]
) -> int:
    """Return the best score achievable from hand + board cards."""
    all_cards = hand + board

    if len(all_cards) < 5:
        return get_partial_hand_score(all_cards)

    return max(
        evaluate_hand(list(combo))
        for combo in combinations(all_cards, 5)
    )


def hand_name(score: int) -> str:
    """Return the name of a poker hand."""
    names = {
        9: "Straight Flush",
        8: "Four of a Kind",
        7: "Full House",
        6: "Flush",
        5: "Straight",
        4: "Three of a Kind",
        3: "Two Pair",
        2: "One Pair",
        1: "High Card",
    }

    return names.get(score, "Unknown Hand")
