"""
RMT Correlation Filter — noise-cleaned portfolio diversification checker.

Uses Marchenko-Pastur law to strip noise eigenvalues from the correlation matrix,
revealing true asset co-movements. Returns a diversification score for your positions.

Usage:
  python scripts/analytics/rmt_correlation.py AAPL MSFT NVDA TSLA
  python scripts/analytics/rmt_correlation.py AAPL MSFT NVDA TSLA --period 1y

Outputs JSON:
  {
    "tickers": ["AAPL", "MSFT", "NVDA", "TSLA"],
    "diversification_score": 0.72,
    "noise_eigenvalue_fraction": 0.68,
    "true_pairs": [
      {"pair": ["AAPL", "MSFT"], "raw_corr": 0.78, "clean_corr": 0.81, "verdict": "HIGH — not diversified"}
    ],
    "recommendation": "AAPL-MSFT are highly correlated. Consider replacing one."
  }
"""

import argparse
import json
import warnings

import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")


def _marchenko_pastur_threshold(n_obs, n_assets):
    """Upper edge of the Marchenko-Pastur distribution (noise eigenvalue range)."""
    Q = n_obs / n_assets
    return (1 + 1 / Q) ** 2


def _clean_correlation(corr_matrix, n_obs):
    n = corr_matrix.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)
    lambda_plus = _marchenko_pastur_threshold(n_obs, n)

    # Replace noise eigenvalues with their mean
    noise_mask = eigenvalues <= lambda_plus
    noise_mean = eigenvalues[noise_mask].mean() if noise_mask.any() else 1.0
    clean_evals = eigenvalues.copy()
    clean_evals[noise_mask] = noise_mean

    noise_fraction = float(noise_mask.sum() / n)

    # Reconstruct clean correlation matrix
    clean_corr = eigenvectors @ np.diag(clean_evals) @ eigenvectors.T

    # Re-normalize to unit diagonal
    diag = np.sqrt(np.diag(clean_corr))
    diag[diag == 0] = 1
    clean_corr = clean_corr / np.outer(diag, diag)
    clean_corr = np.clip(clean_corr, -1, 1)

    return clean_corr, noise_fraction


def _diversification_score(clean_corr):
    """Average off-diagonal absolute correlation — lower = more diversified."""
    n = clean_corr.shape[0]
    if n < 2:
        return 1.0
    off_diag = [abs(clean_corr[i, j]) for i in range(n) for j in range(i + 1, n)]
    avg_corr = float(np.mean(off_diag))
    return round(1 - avg_corr, 4)   # 1 = perfectly diversified, 0 = all correlated


def run(tickers: list, period: str = "1y") -> dict:
    if len(tickers) < 2:
        return {"error": "Need at least 2 tickers"}

    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)["Close"]
    if data.empty:
        return {"error": "Could not fetch data"}

    returns = data.pct_change().dropna()
    if len(returns) < 30:
        return {"error": "Insufficient return history"}

    n_obs, n_assets = returns.shape
    raw_corr = returns.corr().values
    clean_corr, noise_fraction = _clean_correlation(raw_corr, n_obs)
    div_score = _diversification_score(clean_corr)

    # Identify high-correlation pairs
    pairs = []
    cols = list(returns.columns)
    for i in range(n_assets):
        for j in range(i + 1, n_assets):
            rc = round(float(raw_corr[i, j]), 4)
            cc = round(float(clean_corr[i, j]), 4)
            if abs(cc) >= 0.65:
                verdict = "HIGH — not diversified" if abs(cc) >= 0.75 else "MODERATE — watch"
            else:
                verdict = "LOW — diversified"
            pairs.append({
                "pair": [cols[i], cols[j]],
                "raw_corr": rc,
                "clean_corr": cc,
                "verdict": verdict,
            })

    pairs.sort(key=lambda x: abs(x["clean_corr"]), reverse=True)

    # Recommendation
    high_corr_pairs = [p for p in pairs if "HIGH" in p["verdict"]]
    if high_corr_pairs:
        worst = high_corr_pairs[0]
        rec = f"{worst['pair'][0]}-{worst['pair'][1]} are highly correlated ({worst['clean_corr']:+.2f}). Consider replacing one for true diversification."
    elif div_score >= 0.7:
        rec = "Portfolio is well-diversified. No action needed."
    else:
        rec = "Moderate correlation detected. Monitor positions for co-movement risk."

    return {
        "tickers": cols,
        "diversification_score": div_score,
        "noise_eigenvalue_fraction": round(noise_fraction, 4),
        "pairs": pairs[:10],   # top 10 pairs by correlation
        "recommendation": rec,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("--period", default="1y")
    args = parser.parse_args()
    print(json.dumps(run(args.tickers, args.period), indent=2))
