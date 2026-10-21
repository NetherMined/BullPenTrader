"""Bullpen CLI wrapper for paper testing."""
import subprocess
import json
from typing import List, Dict

def run_bullpen(args: List[str]) -> dict:
    cmd = ["bullpen"] + args + ["--output", "json", "--read-only"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": result.stderr}
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def get_top_traders(period: str = "7d", limit: int = 10) -> List[Dict]:
    data = run_bullpen([
        "polymarket", "data", "leaderboard",
        "--time-period", period,
        "--sort", "pnl",
        "--hide-bots",
        "--limit", str(limit)
    ])
    return data.get("leaderboard", [])
