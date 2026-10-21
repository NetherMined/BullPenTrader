from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from bullpen_client import (
    get_top_traders,
    get_smart_money,
    get_wallet_flow,
    crypto_signals,
)

app = FastAPI(title="BullPenTrader Paper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "paper", "source": "bullpen-cli"}


@app.get("/signals")
def signals(
    period: str = Query("7d", description="1d, 7d, 30d, 90d, all"),
    limit: int = Query(15, ge=1, le=50),
    category: Optional[str] = Query("crypto"),
):
    """Combined crypto-focused signals (smart-money preferred, leaderboard fallback)."""
    data = crypto_signals(limit=limit)
    return {"count": len(data), "signals": data, "period": period, "category": category}


@app.get("/signals/leaderboard")
def leaderboard(
    period: str = Query("7d"),
    limit: int = Query(15, ge=1, le=50),
    sort: str = Query("pnl"),
):
    traders = get_top_traders(period=period, limit=limit, sort=sort)
    return {"count": len(traders), "traders": traders}


@app.get("/signals/smart-money")
def smart_money(
    signal_type: str = Query("top_traders"),
    category: str = Query("crypto"),
    limit: int = Query(20, ge=1, le=50),
):
    signals = get_smart_money(signal_type=signal_type, category=category, limit=limit)
    return {"count": len(signals), "signals": signals}


@app.get("/signals/wallet/{address}")
def wallet_flow(address: str, limit: int = Query(20, ge=1, le=100)):
    trades = get_wallet_flow(address, limit=limit)
    return {"address": address, "count": len(trades), "trades": trades}
