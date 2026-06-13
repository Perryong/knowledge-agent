"""
Shannon Entropy Market Regime Detector — pre-trade predictability filter.

Low entropy = concentrated return distribution = predictable/trending market.
High entropy = dispersed returns = chaotic/efficient = reduced edge.

Usage:
  python scripts/analytics/shannon_entropy.py SPY
  python scripts/analytics/shannon_entropy.py SPY --window 63

Outputs JSON:
  {
    "ticker": "SPY",
    "entropy": 2.31,
    "percentile": 18,
    "regime": "predictable",
    "trade_filter": "GO",
    "note": "Entropy in bottom 20% — market is predictable. Edge exists."
  }
"""

import argparse
import json
import warnings
import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")

BINS = 30
LOOKBACK = 504   # 2 years for percentile baseline


def _entropy(returns, bins=BINS):
    """Shannon entropy of the return distribution."""
    counts, _ = np.histogram(returns, bins=bins, density=False)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


def run(ticker: str, window: int = 63, period: str = "2y") -> dict:
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty or len(hist) < window + 30:
        return {"error": f"Insufficient data for {ticker}"}

    returns = hist["Close"].pct_change().dropna().values

    # Rolling entropy series for percentile context
    rolling_entropies = []
    for i in range(window, len(returns)):
        rolling_entropies.append(_entropy(returns[i - window: i]))

    if not rolling_entropies:
        return {"error": "Not enough data for rolling entropy"}

    current = rolling_entropies[-1]
    pct = float(np.mean(np.array(rolling_entropies) <= current) * 100)

    if pct <= 20:
        regime = "predictable"
        trade_filter = "GO"
        note = f"Entropy in bottom {pct:.0f}% — market structure is predictable. Edge elevated."
    elif pct >= 80:
        regime = "chaotic"
        trade_filter = "AVOID"
        note = f"Entropy in top {100 - pct:.0f}% — market is chaotic. Reduce position sizing or stand aside."
    else:
        regime = "neutral"
        trade_filter = "CAUTION"
        note = f"Entropy at {pct:.0f}th percentile — neutral conditions. Normal sizing."

    return {
        "ticker": ticker,
        "entropy": round(current, 4),
        "percentile": round(pct, 1),
        "regime": regime,
        "trade_filter": trade_filter,
        "note": note,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--window", type=int, default=63)
    parser.add_argument("--period", default="2y")
    args = parser.parse_args()
    print(json.dumps(run(args.ticker, args.window, args.period), indent=2))
