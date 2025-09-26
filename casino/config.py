from dataclasses import dataclass


@dataclass
class Config:
    blackjack_min_bet: int
    slots_min_line_bet: int
    
    @classmethod
    def default(cls) -> "Config":
        return cls(
            blackjack_min_bet=10,
            slots_min_line_bet=2,
        )
