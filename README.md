# BullPenTrader

Paper trading bot that pulls top-trader / smart-money signals from the Bullpen CLI and lets you act on them in a Binance-style paper trading UI with live prices.

**Current mode:** Paper only (no real money). Prices come from the public Binance API.

## What you need
- Python 3.10+
- Node.js 18+
- Bullpen CLI (for signals)
- Git

---

## 1. Clone the repo

```bash
git clone https://github.com/NetherMined/BullPenTrader.git
cd BullPenTrader
```

---

## 2. Install Bullpen CLI

### macOS / Linux
```bash
curl -fsSL https://cli.bullpen.fi/install.sh | sh
```

### Windows
Use WSL2 (Ubuntu) and run the command above inside the Ubuntu terminal.  
Or download the latest binary from [Bullpen CLI Releases](https://github.com/BullpenFi/bullpen-cli-releases/releases) and add it to your PATH.

Verify:
```bash
bullpen --version
bullpen status
```

Log in (opens a browser):
```bash
bullpen login
```

Optional (for richer smart-money data):
```bash
bullpen experimental enable prediction_analytics
```

---

## 3. Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal running.  
Check: http://localhost:8000/health

---

## 4. Frontend setup

Open a **new terminal**:

```bash
cd BullPenTrader/frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173).

---

## 5. Using the app

1. Select a symbol (BTCUSDT / ETHUSDT / SOLUSDT) — chart loads live candles.
2. Click **Refresh** in the Signals panel (requires Bullpen CLI to be logged in).
3. On a mapped signal, click **Paper open $100** to open a paper position at the current Binance price.
4. Watch unrealized PnL update. Click **Close** to exit at the current price.
5. Paper state is saved to `backend/paper_state.json` and survives backend restarts.

---

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /signals?mapped=true` | Crypto signals (mapped to Binance symbols) |
| `GET /signals/leaderboard` | Top traders |
| `GET /signals/smart-money` | Smart-money feed |
| `GET /klines?symbol=BTCUSDT&interval=1h` | Chart candles |
| `GET /paper` | Paper balance, equity, positions (live PnL) |
| `POST /paper/open?symbol=BTCUSDT&side=BUY&size_usd=100` | Open paper position |
| `POST /paper/close/{id}` | Close paper position |

---

## Notes
- Paper balance starts at $10,000.
- Mapping from Bullpen signals to Binance pairs is keyword-based (BTC / ETH / SOL only).
- Poll signals sparingly (30–60s). Underlying services can rate-limit.
- No real trading happens. This is a paper testbed.

## Troubleshooting
- **Signals empty:** Run `bullpen status` and `bullpen login`. Check backend logs.
- **Chart blank:** Confirm backend is running and http://localhost:8000/klines?symbol=BTCUSDT returns data.
- **CORS / frontend can't reach backend:** Backend must be on port 8000; frontend expects `http://localhost:8000`.
