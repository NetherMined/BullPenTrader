from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from bullpen_client import (
    get_top_traders,
    get_smart_money,
    get_wallet_flow,
    crypto_signals,
)
from signal_mapper import map_signals
from paper_engine import paper

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
    period: str = Query("7d"),
    limit: int = Query(15, ge=1, le=50),
    category: Optional[str] = Query("crypto"),
    mapped: bool = Query(True),
):
    data = crypto_signals(limit=limit)
    if mapped:
        data = map_signals(data)
    return {"count": len(data), "signals": data, "period": period, "category": category, "mapped": mapped}


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


# --- Paper trading ---
@app.get("/paper")
def paper_summary():
    return paper.summary()


@app.post("/paper/open")
def paper_open(symbol: str, side: str, size_usd: float = 100.0, price: float = 65000.0):
    try:
        pos = paper.open_position(symbol, side.upper(), size_usd, price)
        return {"ok": True, "position": pos}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/paper/close/{pos_id}")
def paper_close(pos_id: str, price: float = 65000.0):
    try:
        pos = paper.close_position(pos_id, price)
        return {"ok": True, "closed": pos}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
