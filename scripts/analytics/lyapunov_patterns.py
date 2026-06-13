"""
Lyapunov Phase-Space Pattern Matcher — historical analogue scanner.

Embeds current price microstructure into phase space and finds the
closest historical match. Returns the analogue date and forward returns.

Usage:
  python scripts/analytics/lyapunov_patterns.py AAPL
  python scripts/analytics/lyapunov_patterns.py AAPL --lookback 30 --period 5y

Outputs JSON:
  {
    "ticker": "AAPL",
    "current_window": "2026-04-15 to 2026-05-04",
    "best_match_date": "2024-03-12",
    "similarity_score": 0.94,
    "distance": 0.031,
    "forward_return_5d":  0.034,
    "forward_return_10d": 0.051,
    "forward_return_21d": 0.078,
    "match_quality": "high",
    "note": "Strong historical analogue found. Forward returns were bullish."
  }
"""

import argparse
import json
import warnings
from datetime import timedelta

import numpy as np
import yfinance as yf
from scipy.spatial import KDTree

warnings.filterwarnings("ignore")

TAU = 5    # time-delay embedding lag (days)
DIM = 3    # embedding dimension


def _embed(series, tau=TAU, dim=DIM):
    """Time-delay embedding into phase space."""
    N = len(series) - (dim - 1) * tau
    if N <= 0:
        return np.array([])
    return np.array([series[i: i + dim * tau: tau] for i in range(N)])


def _normalize(arr):
    std = arr.std(axis=0)
    std[std == 0] = 1
    return (arr - arr.mean(axis=0)) / std


def run(ticker: str, lookback: int = 20, period: str = "5y", theiler: int = 30) -> dict:
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty or len(hist) < lookback + 100:
        return {"error": f"Insufficient data for {ticker}"}

    prices = hist["Close"].values
    dates  = hist.index.tolist()

    # Log-return series
    returns = np.log(prices[1:] / prices[:-1])
    dates   = dates[1:]

    embedded = _embed(returns, tau=TAU, dim=DIM)
    if len(embedded) < lookback + theiler + 21:
        return {"error": "Not enough embedded points"}

    # Normalize
    embedded_norm = _normalize(embedded)

    # Current window = last `lookback` embedded points averaged into one query vector
    current_vec = embedded_norm[-lookback:].mean(axis=0).reshape(1, -1)

    # Historical library = all points except recent lookback + theiler window
    lib_end = len(embedded_norm) - lookback - theiler
    if lib_end < 10:
        return {"error": "Not enough historical library points"}

    library  = embedded_norm[:lib_end]
    lib_dates = dates[:lib_end]

    # KD-Tree nearest neighbor
    tree = KDTree(library)
    dist, idx = tree.query(current_vec, k=1)
    dist = float(dist[0])
    idx  = int(idx[0])

    match_date = lib_dates[idx]

    # Forward returns from match date
    match_price_idx = idx + (DIM - 1) * TAU + 1  # approximate offset back to price index
    def _fwd_return(days):
        end_idx = match_price_idx + days
        if end_idx >= len(prices):
            return None
        return round(float((prices[end_idx] - prices[match_price_idx]) / prices[match_price_idx]), 6)

    fwd_5  = _fwd_return(5)
    fwd_10 = _fwd_return(10)
    fwd_21 = _fwd_return(21)

    # Similarity score: 1 / (1 + distance)
    similarity = round(1 / (1 + dist * 10), 4)

    if similarity >= 0.85:
        quality = "high"
    elif similarity >= 0.65:
        quality = "moderate"
    else:
        quality = "low"

    # Narrative
    fwd_desc = []
    if fwd_21 is not None:
        direction = "bullish" if fwd_21 > 0 else "bearish"
        fwd_desc.append(f"21d forward return was {fwd_21:+.1%} ({direction})")
    note = f"{quality.capitalize()} analogue match at {str(match_date)[:10]}. " + (", ".join(fwd_desc) or "No forward data.")

    return {
        "ticker": ticker,
        "best_match_date": str(match_date)[:10],
        "similarity_score": similarity,
        "distance": round(dist, 6),
        "forward_return_5d":  fwd_5,
        "forward_return_10d": fwd_10,
        "forward_return_21d": fwd_21,
        "match_quality": quality,
        "note": note,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--period", default="5y")
    args = parser.parse_args()
    print(json.dumps(run(args.ticker, args.lookback, args.period), indent=2))
