"""
Wasserstein Drift Detector — strategy health monitor.

Detects when live trading returns have drifted from the baseline (first N trades).
A high Wasserstein distance signals regime shift or strategy degradation.

Usage:
  python scripts/analytics/wasserstein_drift.py --strategy TCEP
  python scripts/analytics/wasserstein_drift.py --returns "0.02,0.01,-0.005,0.03" --baseline "0.015,0.008,0.012,-0.002"

Reads from: _bmad/memory/tm/raw/trade-logs/ (YYYY-MM-DD-TICKER.json files)

Outputs JSON:
  {
    "strategy": "TCEP",
    "distance_1d": 0.004,
    "distance_2d": 0.012,
    "drift_detected": false,
    "alert": null,
    "baseline_trades": 8,
    "recent_trades": 5,
    "recommendation": "Strategy performing within expected range."
  }
"""

import argparse
import glob
import json
import os
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import wasserstein_distance

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TRADE_LOG_DIR = PROJECT_ROOT / "_bmad/memory/tm/raw/trade-logs"

DRIFT_THRESHOLD_1D = 0.008   # Wasserstein distance on returns
DRIFT_THRESHOLD_2D = 0.025   # 2D (returns + vol) combined


def _load_strategy_returns(strategy: str):
    """Load all trade returns for a given strategy from trade log JSONs."""
    returns = []
    pattern = str(TRADE_LOG_DIR / "**/*.json")
    for path in glob.glob(pattern, recursive=True):
        try:
            with open(path) as f:
                trade = json.load(f)
            if trade.get("strategy", "").upper() == strategy.upper():
                ret = trade.get("return_pct") or trade.get("pnl_pct") or trade.get("pnl")
                if ret is not None:
                    returns.append(float(ret))
        except Exception:
            continue
    return returns


def run(strategy: str = None, returns_raw: str = None, baseline_raw: str = None) -> dict:
    if returns_raw and baseline_raw:
        live = [float(x) for x in returns_raw.split(",")]
        baseline = [float(x) for x in baseline_raw.split(",")]
    elif strategy:
        all_returns = _load_strategy_returns(strategy)
        if len(all_returns) < 6:
            return {
                "strategy": strategy,
                "drift_detected": False,
                "alert": None,
                "baseline_trades": len(all_returns),
                "recent_trades": 0,
                "recommendation": f"Only {len(all_returns)} trades logged — need at least 6 to detect drift.",
            }
        split = max(4, len(all_returns) // 2)
        baseline = all_returns[:split]
        live = all_returns[split:]
    else:
        return {"error": "Provide --strategy or --returns + --baseline"}

    if len(live) < 2 or len(baseline) < 2:
        return {"error": "Need at least 2 values in each distribution"}

    dist_1d = float(wasserstein_distance(baseline, live))

    # 2D: (return, abs_return as vol proxy)
    b2 = np.column_stack([baseline, np.abs(baseline)])
    l2 = np.column_stack([live, np.abs(live)])
    dist_2d_components = [
        wasserstein_distance(b2[:, i], l2[:, i]) for i in range(2)
    ]
    dist_2d = float(np.mean(dist_2d_components))

    drift = dist_1d > DRIFT_THRESHOLD_1D or dist_2d > DRIFT_THRESHOLD_2D

    if drift:
        alert = (
            f"Drift detected (1D={dist_1d:.4f}, 2D={dist_2d:.4f}). "
            "Live returns diverging from baseline. Consider pausing or reviewing strategy."
        )
        rec = "Pause new entries. Review recent trades for systematic cause."
    else:
        alert = None
        rec = "Strategy performing within expected range."

    return {
        "strategy": strategy or "custom",
        "distance_1d": round(dist_1d, 6),
        "distance_2d": round(dist_2d, 6),
        "drift_detected": drift,
        "alert": alert,
        "baseline_trades": len(baseline),
        "recent_trades": len(live),
        "recommendation": rec,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default=None)
    parser.add_argument("--returns", dest="returns_raw", default=None)
    parser.add_argument("--baseline", dest="baseline_raw", default=None)
    args = parser.parse_args()
    print(json.dumps(run(args.strategy, args.returns_raw, args.baseline_raw), indent=2))
