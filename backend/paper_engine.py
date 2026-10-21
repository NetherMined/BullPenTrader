"""In-memory paper trading engine for testing."""
from typing import Dict, List
from datetime import datetime
import uuid

STARTING_BALANCE = 10000.0

class PaperEngine:
    def __init__(self):
        self.balance = STARTING_BALANCE
        self.positions: List[Dict] = []
        self.trades: List[Dict] = []

    def open_position(self, symbol: str, side: str, size_usd: float, price: float = 65000.0) -> Dict:
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
        return pos

    def close_position(self, pos_id: str, price: float) -> Dict:
        pos = next((p for p in self.positions if p["id"] == pos_id), None)
        if not pos:
            raise ValueError("Position not found")
        direction = 1 if pos["side"] == "BUY" else -1
        pnl = (price - pos["entry_price"]) * pos["qty"] * direction
        pos["pnl"] = pnl
        pos["closed_at"] = datetime.utcnow().isoformat()
        pos["exit_price"] = price
        self.balance += pos["size_usd"] + pnl
        self.positions = [p for p in self.positions if p["id"] != pos_id]
        self.trades.append({**pos, "action": "close"})
        return pos

    def summary(self) -> Dict:
        open_pnl = sum(p.get("pnl", 0) for p in self.positions)
        return {
            "balance": round(self.balance, 2),
            "equity": round(self.balance + open_pnl, 2),
            "open_positions": len(self.positions),
            "positions": self.positions,
            "recent_trades": self.trades[-10:],
        }

paper = PaperEngine()
