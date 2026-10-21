# BullPenTrader

Paper trading testnet bot that mirrors top traders / smart money signals from Bullpen (via CLI) onto Binance-style execution.

## Features
- Paper money / testnet mode
- Bullpen CLI data source (leaderboard, smart-money, wallet flow)
- Binance-like frontend (charts + order panel)
- Risk rules and position tracking

## Setup
1. Install Bullpen CLI: `curl -fsSL https://cli.bullpen.fi/install.sh | sh`
2. Log in: `bullpen login` (or follow CLI prompts)
3. Python backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
4. Frontend: `cd frontend && npm install && npm run dev`

## Signal Endpoints (backend)
- `GET /signals` — crypto-focused smart money (falls back to leaderboard)
- `GET /signals/leaderboard?period=7d&limit=15&sort=pnl`
- `GET /signals/smart-money?category=crypto&signal_type=top_traders`
- `GET /signals/wallet/{address}` — recent flow for a wallet

## Bullpen CLI Limits
- No strict public rate limit documented for CLI itself.
- Underlying services (Polymarket, Hyperliquid) can rate-limit.
- Recommended poll interval: 30–60 seconds.
- Use `--output json` and `--read-only` where possible.
- Some analytics commands may require experimental features (`bullpen experimental enable prediction_analytics`).
- Wallet Status API: ~10 req/s (not the main path).
