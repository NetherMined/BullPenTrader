"""Map Bullpen signals to Binance futures actions."""
from typing import Dict, Optional, List

SYMBOL_KEYWORDS = {
    "BTCUSDT": ["btc", "bitcoin"],
    "ETHUSDT": ["eth", "ethereum"],
    "SOLUSDT": ["sol", "solana"],
}


def map_signal(signal: Dict) -> Optional[Dict]:
    """Return a Binance-style action or None if no clear mapping."""
    text = " ".join([
        str(signal.get("market", "")),
        str(signal.get("outcome", "")),
        str(signal.get("title", "")),
        str(signal.get("question", "")),
        str(signal.get("username", "")),
    ]).lower()

    symbol = None
    for sym, keys in SYMBOL_KEYWORDS.items():
        if any(k in text for k in keys):
            symbol = sym
            break
    if not symbol:
        return None

    outcome = str(signal.get("outcome", "") or signal.get("side", "")).lower()
    side = "BUY"
    if any(x in outcome for x in ["no", "sell", "short", "lower", "below"]):
        side = "SELL"
    elif any(x in outcome for x in ["yes", "buy", "long", "higher", "above"]):
        side = "BUY"
    else:
        # Default long on positive PnL / size signals
        pnl = signal.get("pnl") or signal.get("pnl_usd") or 0
        try:
            if float(pnl) < 0:
                side = "SELL"
        except (TypeError, ValueError):
            pass

    size_usd = float(signal.get("size_usd") or signal.get("volume") or signal.get("size") or 0)
    confidence = 0.6 if size_usd > 10000 else 0.4

    return {
        "symbol": symbol,
        "side": side,
        "confidence": confidence,
        "source_size_usd": size_usd,
        "raw_preview": text[:120],
    }


def map_signals(signals: List[Dict]) -> List[Dict]:
    mapped = []
    for s in signals:
        action = map_signal(s)
        if action:
            mapped.append({**action, "original": s})
    return mapped
