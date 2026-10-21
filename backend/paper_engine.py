"""Paper trading engine with JSON persistence."""
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import os

STARTING_BALANCE = 10000.0
STATE_FILE = os.path.join(os.path.dirname(__file__), "paper_state.json")


class PaperEngine:
    def __init__(self):
        self.balance = STARTING_BALANCE
        self.positions: List[Dict] = []
        self.trades: List[Dict] = []
        self.load()

    def load(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
            self.balance = data.get("balance", STARTING_BALANCE)
            self.positions = data.get("positions", [])
            self.trades = data.get("trades", [])
        except Exception:
            pass

    def save(self):
        data = {
            "balance": self.balance,
            "positions": self.positions,
            "trades": self.trades[-200:],  # keep recent history
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def open_position(self, symbol: str, side: str, size_usd: float, price: float) -> Dict:
        if size_usd > self.balance:
            raise ValueError("Insufficient paper balance")
        qty = size_usd / price
        pos = {
            "id": str(uuid.uuid4())[:8],
            "symbol": symbol,
            "side": side,
            "size_usd": size_usd,
            "qty": qty,
            "entry_price": price,
            "opened_at": datetime.utcnow().isoformat(),
            "pnl": 0.0,
        }
        self.positions.append(pos)
        self.balance -= size_usd
        self.trades.append({**pos, "action": "open"})
        self.save()
        return pos

    def close_position(self, pos_id: str, price: float) -> Dict:
        pos = next((p for p in self.positions if p["id"] == pos_id), None)
        if not pos:
            raise ValueError("Position not found")
        direction = 1 if pos["side"] == "BUY" else -1
        pnl = (price - pos["entry_price"]) * pos["qty"] * direction
        pos["pnl"] = round(pnl, 2)
        pos["closed_at"] = datetime.utcnow().isoformat()
        pos["exit_price"] = price
        self.balance += pos["size_usd"] + pnl
        self.positions = [p for p in self.positions if p["id"] != pos_id]
        self.trades.append({**pos, "action": "close"})
        self.save()
        return pos

    def update_unrealized(self, prices: Dict[str, float]):
        for p in self.positions:
            price = prices.get(p["symbol"])
            if price is None:
                continue
            direction = 1 if p["side"] == "BUY" else -1
            pnl = (price - p["entry_price"]) * p["qty"] * direction
            p["pnl"] = round(pnl, 2)
            p["mark_price"] = price

    def summary(self, prices: Optional[Dict[str, float]] = None) -> Dict:
        if prices:
            self.update_unrealized(prices)
        open_pnl = sum(p.get("pnl", 0) for p in self.positions)
        return {
            "balance": round(self.balance, 2),
            "equity": round(self.balance + open_pnl, 2),
            "open_pnl": round(open_pnl, 2),
            "open_positions": len(self.positions),
            "positions": self.positions,
            "recent_trades": self.trades[-10:],
        }


paper = PaperEngine()
