"""Public Binance market data (no API key required)."""
from binance.client import Client
from typing import List, Dict

client = Client()  # public endpoints only


def get_price(symbol: str) -> float:
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


def get_klines(symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict]:
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    candles = []
    for k in raw:
        candles.append({
            "time": int(k[0] / 1000),  # lightweight-charts expects seconds
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
        })
    return candles


def get_prices(symbols: List[str]) -> Dict[str, float]:
    out = {}
    for s in symbols:
        try:
            out[s] = get_price(s)
        except Exception:
            pass
    return out
