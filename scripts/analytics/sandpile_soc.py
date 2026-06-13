"""
Sandpile SOC (Self-Organized Criticality) — tail risk / volatility warning.

Applies the Bak-Tang-Wiesenfeld sandpile model to daily returns.
A high criticality ratio signals the market is near a tipping point.

Usage:
  python scripts/analytics/sandpile_soc.py SPY
  python scripts/analytics/sandpile_soc.py BTC-USD --period 1y

Outputs JSON:
  {
    "ticker": "SPY",
    "criticality_ratio": 0.04,
    "risk_level": "low",
    "tail_risk_warning": false,
    "avg_avalanche_size": 12.3,
    "max_avalanche_size": 48,
    "note": "Market is below criticality threshold. Normal risk environment."
  }
"""

import argparse
import json
import warnings
import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")

GRID_SIZE    = 15       # 15x15 sandpile grid
TOPPLE_THRESHOLD = 4    # grains to trigger toppling
SCALE_FACTOR = 200      # maps |return| → grains added (1% return ≈ 2 grains)
AVALANCHE_THRESHOLD = 8   # avalanches > this size = critical event
CRITICAL_RATIO_WARN = 0.10  # >10% of steps are critical = warning


def _run_sandpile(returns):
    """Run the BTW sandpile on a return series and return criticality metrics."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    critical_steps = 0
    avalanche_sizes = []

    for ret in returns:
        # Add grains proportional to |return|
        grains = max(1, int(abs(ret) * SCALE_FACTOR))
        x, y = np.random.randint(0, GRID_SIZE, 2)
        grid[x, y] += grains

        # Toppling
        avalanche_size = 0
        for _ in range(500):  # max iterations per step
            unstable = np.argwhere(grid >= TOPPLE_THRESHOLD)
            if len(unstable) == 0:
                break
            for cx, cy in unstable:
                grid[cx, cy] -= 4
                avalanche_size += 1
                if cx > 0:              grid[cx - 1, cy] += 1
                if cx < GRID_SIZE - 1: grid[cx + 1, cy] += 1
                if cy > 0:              grid[cx, cy - 1] += 1
                if cy < GRID_SIZE - 1: grid[cx, cy + 1] += 1
            # Clip boundaries (grains fall off the edge)
            grid = np.clip(grid, 0, None)

        if avalanche_size > 0:
            avalanche_sizes.append(avalanche_size)
        if avalanche_size >= AVALANCHE_THRESHOLD:
            critical_steps += 1

    criticality_ratio = critical_steps / len(returns) if len(returns) > 0 else 0
    return criticality_ratio, avalanche_sizes


def run(ticker: str, period: str = "1y") -> dict:
    np.random.seed(42)
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty or len(hist) < 60:
        return {"error": f"Insufficient data for {ticker}"}

    returns = hist["Close"].pct_change().dropna().values
    criticality_ratio, avalanche_sizes = _run_sandpile(returns)

    avg_size = float(np.mean(avalanche_sizes)) if avalanche_sizes else 0
    max_size = int(max(avalanche_sizes)) if avalanche_sizes else 0

    if criticality_ratio >= CRITICAL_RATIO_WARN:
        risk_level = "critical"
        warning = True
        note = (
            f"Criticality ratio {criticality_ratio:.2%} exceeds {CRITICAL_RATIO_WARN:.0%} threshold. "
            "Market near tipping point — tighten stops, reduce sizing."
        )
    elif criticality_ratio >= CRITICAL_RATIO_WARN * 0.6:
        risk_level = "elevated"
        warning = False
        note = f"Criticality ratio {criticality_ratio:.2%} — moderately elevated tail risk. Normal sizing with wider stops."
    else:
        risk_level = "low"
        warning = False
        note = f"Criticality ratio {criticality_ratio:.2%} — below threshold. Normal risk environment."

    return {
        "ticker": ticker,
        "criticality_ratio": round(criticality_ratio, 6),
        "risk_level": risk_level,
        "tail_risk_warning": warning,
        "avg_avalanche_size": round(avg_size, 2),
        "max_avalanche_size": max_size,
        "note": note,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--period", default="1y")
    args = parser.parse_args()
    print(json.dumps(run(args.ticker, args.period), indent=2))
