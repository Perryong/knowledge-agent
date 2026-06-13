"""
Hurst Exponent Regime Gate — trending vs mean-reverting classifier.

Usage:
  python scripts/analytics/hurst.py AAPL
  python scripts/analytics/hurst.py AAPL --period 1y

Outputs JSON:
  {
    "ticker": "AAPL",
    "H": 0.62,
    "regime": "trending",
    "confidence": "high",
    "suggested_strategies": ["ORB", "TCEP", "Gap-and-Go"],
    "avoid_strategies": ["MRF"],
    "note": "H > 0.55 — price is trending. Favor momentum entries."
  }
"""

import argparse
import json
import warnings
import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")

WINDOWS = [30, 60, 90, 120, 180, 252]


def _rs_analysis(series, n):
    """Rescaled range for a subsequence of length n."""
    if len(series) < n:
        return None
    results = []
    for start in range(0, len(series) - n + 1, n):
        sub = series[start: start + n]
        mean = sub.mean()
        deviations = np.cumsum(sub - mean)
        R = deviations.max() - deviations.min()
        S = sub.std(ddof=1)
        if S > 0:
            results.append(R / S)
    return np.mean(results) if results else None


def _hurst(prices):
    """Estimate H via log-log regression of R/S across multiple window sizes."""
    log_returns = np.log(prices / np.roll(prices, 1))[1:]
    rs_values, valid_ns = [], []
    for n in WINDOWS:
        rs = _rs_analysis(log_returns, n)
        if rs is not None and rs > 0:
            rs_values.append(np.log(rs))
            valid_ns.append(np.log(n))
    if len(valid_ns) < 3:
        return 0.5
    coeffs = np.polyfit(valid_ns, rs_values, 1)
    return float(coeffs[0])


def run(ticker: str, period: str = "1y") -> dict:
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty or len(hist) < 60:
        return {"error": f"Insufficient data for {ticker}"}

    prices = hist["Close"].values
    H = round(_hurst(prices), 4)

    if H > 0.55:
        regime = "trending"
        confidence = "high" if H > 0.65 else "moderate"
        suggested = ["ORB", "TCEP", "Gap-and-Go", "VCP", "SMR"]
        avoid = ["MRF"]
        note = f"H={H:.3f} > 0.55 — price is trending. Favor momentum entries."
    elif H < 0.45:
        regime = "mean-reverting"
        confidence = "high" if H < 0.35 else "moderate"
        suggested = ["MRF", "SMR"]
        avoid = ["ORB", "TCEP", "Gap-and-Go"]
        note = f"H={H:.3f} < 0.45 — price is mean-reverting. Favor reversion entries."
    else:
        regime = "random-walk"
        confidence = "low"
        suggested = []
        avoid = []
        note = f"H={H:.3f} ≈ 0.5 — near random walk. Edge is reduced across all strategies."

    return {
        "ticker": ticker,
        "H": H,
        "regime": regime,
        "confidence": confidence,
        "suggested_strategies": suggested,
        "avoid_strategies": avoid,
        "note": note,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--period", default="1y")
    args = parser.parse_args()
    print(json.dumps(run(args.ticker, args.period), indent=2))
