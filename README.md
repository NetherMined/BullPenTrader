# BullPenTrader

Paper trading testnet bot that mirrors top traders / smart money signals from Bullpen (via CLI) onto Binance-style execution.

## Features
- Paper money / testnet mode
- Bullpen CLI data source (leaderboard, smart-money, wallet flow)
- Binance-like frontend (charts + order panel)
- Risk rules and position tracking

## Setup
1. Install Bullpen CLI: `curl -fsSL https://cli.bullpen.fi/install.sh | sh`
2. Python backend: `cd backend && pip install -r requirements.txt`
3. Frontend: `cd frontend && npm install && npm run dev`

## Bullpen CLI Limits
- No strict public rate limit documented for CLI itself.
- Underlying services (Polymarket, Hyperliquid) can rate-limit.
- Recommended poll interval: 30–60 seconds.
- Use `--output json` and `--read-only` where possible.
- Wallet Status API: ~10 req/s (not the main path).
