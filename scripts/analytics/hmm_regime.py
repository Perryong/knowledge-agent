"""
HMM Regime Filter — 3-state Bull/Bear/Crisis classifier.

Usage:
  python scripts/analytics/hmm_regime.py SPY --period 2y
  python scripts/analytics/hmm_regime.py SPY --period 2y --json

Outputs JSON:
  {
    "ticker": "SPY",
    "state": "Bull",
    "state_index": 0,
    "probs": [0.85, 0.12, 0.03],
    "recent_sequence": ["Bull","Bull","Bear","Bull"],
    "crisis_warning": false,
    "confidence": 0.85
  }
"""

import argparse
import json
import sys
import warnings
import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")

# HMM parameters — calibrated to US equity market history
STATES = ["Bull", "Bear", "Crisis"]
MEANS  = np.array([ 0.0009, -0.0006, -0.0020])
STDS   = np.array([ 0.0080,  0.0145,  0.0310])
TRANS  = np.array([
    [0.970, 0.025, 0.005],   # from Bull
    [0.040, 0.945, 0.015],   # from Bear
    [0.020, 0.080, 0.900],   # from Crisis
])
INIT   = np.array([0.70, 0.20, 0.10])


def _gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def _forward_backward(obs):
    """Viterbi + forward-backward for most likely state sequence and smoothed posteriors."""
    T = len(obs)
    K = len(STATES)

    # Emission probabilities
    B = np.zeros((T, K))
    for k in range(K):
        B[:, k] = _gaussian(obs, MEANS[k], STDS[k])
    B = np.clip(B, 1e-300, None)

    # Forward pass
    alpha = np.zeros((T, K))
    alpha[0] = INIT * B[0]
    alpha[0] /= alpha[0].sum()
    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ TRANS) * B[t]
        s = alpha[t].sum()
        if s > 0:
            alpha[t] /= s

    # Backward pass
    beta = np.ones((T, K))
    for t in range(T - 2, -1, -1):
        beta[t] = (TRANS * B[t + 1] * beta[t + 1]).sum(axis=1)
        s = beta[t].sum()
        if s > 0:
            beta[t] /= s

    # Smoothed posteriors
    gamma = alpha * beta
    row_sums = gamma.sum(axis=1, keepdims=True)
    gamma = gamma / np.where(row_sums > 0, row_sums, 1)

    return gamma


def run(ticker: str, period: str = "2y") -> dict:
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty or len(hist) < 60:
        return {"error": f"Insufficient data for {ticker}"}

    returns = hist["Close"].pct_change().dropna().values
    gamma = _forward_backward(returns)

    # Current (last day) state
    last_probs = gamma[-1].tolist()
    state_idx = int(np.argmax(last_probs))

    # Recent 10-day sequence
    recent_states = [STATES[int(np.argmax(gamma[i]))] for i in range(-10, 0)]

    # Crisis warning: Crisis posterior > 5% AND rising for 3 consecutive days
    crisis_probs = gamma[-5:, 2]
    crisis_warning = bool(
        crisis_probs[-1] > 0.05
        and len(crisis_probs) >= 3
        and all(crisis_probs[i] < crisis_probs[i + 1] for i in range(len(crisis_probs) - 1))
    )

    return {
        "ticker": ticker,
        "state": STATES[state_idx],
        "state_index": state_idx,
        "probs": [round(p, 4) for p in last_probs],
        "recent_sequence": recent_states,
        "crisis_warning": crisis_warning,
        "confidence": round(last_probs[state_idx], 4),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("--period", default="2y")
    args = parser.parse_args()
    print(json.dumps(run(args.ticker, args.period), indent=2))
