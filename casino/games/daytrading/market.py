import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Simulated stock catalog with realistic base prices
MOCK_STOCKS: dict[str, float] = {
    "AAPL": 189.50,
    "GOOGL": 141.80,
    "MSFT": 415.60,
    "AMZN": 178.25,
    "TSLA": 248.40,
    "NVDA": 875.30,
    "META": 505.75,
    "NFLX": 605.90,
    "AMD": 165.20,
    "DIS": 112.45,
}


@dataclass
class Quote:
    symbol: str
    price: float
    change: float  # dollar change from "previous close"


class MarketProvider(ABC):
    @abstractmethod
    def get_quote(self, symbol: str) -> Quote | None:
        ...

    @abstractmethod
    def list_all(self) -> list[str]:
        ...

    @abstractmethod
    def search(self, query: str) -> list[str]:
        ...

    @abstractmethod
    def provider_name(self) -> str:
        ...


class MockMarket(MarketProvider):
    """Simulated market with randomized price movement."""

    def __init__(self) -> None:
        self._prices: dict[str, float] = {
            sym: price for sym, price in MOCK_STOCKS.items()
        }

    def get_quote(self, symbol: str) -> Quote | None:
        symbol = symbol.upper()
        base = self._prices.get(symbol)
        if base is None:
            return None
        # Simulate price movement: -3% to +3%
        pct = random.uniform(-0.03, 0.03)
        change = round(base * pct, 2)
        new_price = round(base + change, 2)
        self._prices[symbol] = new_price
        return Quote(symbol=symbol, price=new_price, change=change)

    def list_all(self) -> list[str]:
        return sorted(self._prices.keys())

    def search(self, query: str) -> list[str]:
        query = query.upper()
        return [s for s in self._prices if query in s]

    def provider_name(self) -> str:
        return "Simulated Market"


class AlpacaMarket(MarketProvider):
    """Live paper-trading market via Alpaca API (optional)."""

    def __init__(self, api_key: str, secret_key: str) -> None:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.trading.client import TradingClient

        self._data_client = StockHistoricalDataClient(api_key, secret_key)
        self._trading_client = TradingClient(api_key, secret_key, paper=True)

    def get_quote(self, symbol: str) -> Quote | None:
        from alpaca.data.requests import StockLatestQuoteRequest

        symbol = symbol.upper()
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self._data_client.get_stock_latest_quote(request)
            quote = quotes[symbol]
            price = float(quote.ask_price + quote.bid_price) / 2
            return Quote(symbol=symbol, price=round(price, 2), change=0.0)
        except Exception:
            return None

    def list_all(self) -> list[str]:
        try:
            assets = self._trading_client.get_all_assets()
            return sorted([
                a.symbol for a in assets
                if a.tradable and a.status == "active"
            ])[:50]
        except Exception:
            return []

    def search(self, query: str) -> list[str]:
        query = query.upper()
        try:
            assets = self._trading_client.get_all_assets()
            return [
                a.symbol for a in assets
                if query in a.symbol and a.tradable and a.status == "active"
            ][:10]
        except Exception:
            return []

    def provider_name(self) -> str:
        return "Alpaca Paper Trading"


def create_market() -> MarketProvider:
    """Create the best available market provider.
    Uses Alpaca if APCA_API_KEY_ID and APCA_API_SECRET_KEY env vars are set,
    otherwise falls back to simulated market."""
    import os

    api_key = os.environ.get("APCA_API_KEY_ID", "")
    secret_key = os.environ.get("APCA_API_SECRET_KEY", "")

    if api_key and secret_key:
        try:
            market = AlpacaMarket(api_key, secret_key)
            # Quick sanity check
            market.get_quote("AAPL")
            return market
        except Exception:
            pass

    return MockMarket()
