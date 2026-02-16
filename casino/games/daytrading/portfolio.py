import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

PORTFOLIO_DIR = Path(__file__).resolve().parent / "portfolios"


@dataclass
class Transaction:
    symbol: str
    side: str  # "buy" or "sell"
    qty: int
    price: float
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "qty": self.qty,
            "price": self.price,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        return Transaction(
            symbol=data["symbol"],
            side=data["side"],
            qty=data["qty"],
            price=data["price"],
            timestamp=data["timestamp"],
        )


@dataclass
class Portfolio:
    owner: str
    cash: float = 0.0
    holdings: dict[str, int] = field(default_factory=dict)
    history: list[Transaction] = field(default_factory=list)

    def buy(self, symbol: str, qty: int, price: float) -> None:
        cost = qty * price
        if cost > self.cash:
            raise ValueError("Insufficient trading funds")
        self.cash -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + qty
        self.history.append(Transaction(
            symbol=symbol,
            side="buy",
            qty=qty,
            price=price,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        ))

    def sell(self, symbol: str, qty: int, price: float) -> None:
        held = self.holdings.get(symbol, 0)
        if qty > held:
            raise ValueError(f"You only hold {held} shares of {symbol}")
        self.holdings[symbol] -= qty
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.cash += qty * price
        self.history.append(Transaction(
            symbol=symbol,
            side="sell",
            qty=qty,
            price=price,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        ))

    def stock_value(self, prices: dict[str, float]) -> float:
        return sum(
            prices.get(sym, 0.0) * qty for sym, qty in self.holdings.items()
        )

    # --- JSON persistence ---

    def to_dict(self) -> dict:
        return {
            "owner": self.owner,
            "cash": self.cash,
            "holdings": self.holdings,
            "history": [t.to_dict() for t in self.history],
        }

    @staticmethod
    def from_dict(data: dict) -> "Portfolio":
        return Portfolio(
            owner=data["owner"],
            cash=data.get("cash", 0.0),
            holdings=data.get("holdings", {}),
            history=[Transaction.from_dict(t) for t in data.get("history", [])],
        )

    def save(self, path: Optional[str] = None) -> str:
        if path is None:
            PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
            path = str(PORTFOLIO_DIR / f"{self.owner}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    @staticmethod
    def load(path: str) -> "Portfolio":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Portfolio.from_dict(data)

    @staticmethod
    def load_or_create(owner: str) -> "Portfolio":
        PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
        path = PORTFOLIO_DIR / f"{owner}.json"
        if path.exists():
            return Portfolio.load(str(path))
        return Portfolio(owner=owner)
