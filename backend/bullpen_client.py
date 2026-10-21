"""Bullpen CLI wrapper for paper testing.

Requires Bullpen CLI installed and authenticated.
All reads use --output json and --read-only where supported.
"""
import subprocess
import json
from typing import List, Dict, Any, Optional


def run_bullpen(args: List[str], timeout: int = 45) -> Dict[str, Any]:
    cmd = ["bullpen"] + args + ["--output", "json"]
    # Add --read-only when the command supports it (most data commands do)
    if "--read-only" not in args:
        cmd.append("--read-only")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return {"error": result.stderr.strip() or result.stdout.strip() or "CLI failed"}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "Bullpen CLI timed out"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from CLI", "raw": result.stdout[:500]}
    except Exception as e:
        return {"error": str(e)}


def get_top_traders(
    period: str = "7d",
    limit: int = 15,
    sort: str = "pnl",
    hide_bots: bool = True,
) -> List[Dict]:
    args = [
        "polymarket", "data", "leaderboard",
        "--time-period", period,
        "--sort", sort,
        "--limit", str(limit),
    ]
    if hide_bots:
        args.append("--hide-bots")
    data = run_bullpen(args)
    if "error" in data:
        return []
    return data.get("leaderboard", data.get("traders", []))


def get_smart_money(
    signal_type: str = "top_traders",
    category: str = "crypto",
    limit: int = 20,
    time_period: str = "7d",
) -> List[Dict]:
    args = [
        "polymarket", "data", "smart-money",
        "--type", signal_type,
        "--limit", str(limit),
    ]
    if category:
        args.extend(["--category", category])
    if time_period:
        args.extend(["--time-period", time_period])
    data = run_bullpen(args)
    if "error" in data:
        return []
    # CLI shape varies; normalize common keys
    return data.get("signals") or data.get("results") or data.get("data") or []


def get_wallet_flow(address: str, limit: int = 20) -> List[Dict]:
    """Recent trades for a specific wallet."""
    data = run_bullpen([
        "polymarket", "discover", "flow",
        "--address", address,
        "--limit", str(limit),
    ])
    if "error" in data:
        return []
    return data.get("trades") or data.get("flow") or data.get("activity") or []


def get_trader_profile(address: str) -> Dict:
    data = run_bullpen([
        "polymarket", "data", "trader-profile",
        "--address", address,
    ])
    return data if "error" not in data else {}


def crypto_signals(limit: int = 15) -> List[Dict]:
    """Convenience: crypto-focused smart money + top traders."""
    signals = get_smart_money(signal_type="top_traders", category="crypto", limit=limit)
    if not signals:
        # Fallback to leaderboard if smart-money is empty / gated
        traders = get_top_traders(period="7d", limit=limit)
        signals = [{"source": "leaderboard", **t} for t in traders]
    return signals
