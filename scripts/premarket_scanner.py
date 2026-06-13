#!/usr/bin/env python3
"""
Pre-market scanner for The Money morning workflow.

Scans a stock universe against all 6 strategy criteria using batch yfinance data.
Outputs a JSON watchlist grouped by strategy.

Usage:
    python premarket_scanner.py
    python premarket_scanner.py --regime path/to/regime.yaml
    python premarket_scanner.py --universe path/to/universe.json
    python premarket_scanner.py --output path/to/watchlist.json

The scanner does fast batch technical analysis. Slower per-ticker checks
(earnings dates, options chains, IV rank) are deferred to the orchestrator
which uses MCP tools.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_UNIVERSE = SCRIPT_DIR / "universe.json"
DEFAULT_REGIME_DIR = PROJECT_ROOT / "_bmad" / "memory" / "tm" / "wiki" / "regimes"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "_bmad" / "memory" / "tm" / "raw" / "watchlists"


def load_universe(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data["sectors"], data.get("sector_etfs", {})


def load_regime(path: str | None) -> dict:
    """Load regime from YAML/JSON or return defaults."""
    defaults = {
        "flag": "yellow",
        "leading_sectors": ["Technology", "Consumer Discretionary", "Real Estate"],
        "lagging_sectors": ["Energy", "Healthcare"],
        "rotating_into": [],
    }
    if not path:
        regime_files = sorted(DEFAULT_REGIME_DIR.glob("*.md"), reverse=True)
        if not regime_files:
            return defaults
        # Parse YAML frontmatter between --- markers
        text = regime_files[0].read_text(encoding="utf-8")
        try:
            import yaml as _yaml
            if text.startswith("---"):
                end = text.index("---", 3)
                frontmatter = _yaml.safe_load(text[3:end])
                if frontmatter:
                    if "flag" in frontmatter:
                        defaults["flag"] = str(frontmatter["flag"])
                    if "leading_sectors" in frontmatter:
                        defaults["leading_sectors"] = list(frontmatter["leading_sectors"])
                    elif "leading" in frontmatter:
                        defaults["leading_sectors"] = list(frontmatter["leading"])
                    if "lagging_sectors" in frontmatter:
                        defaults["lagging_sectors"] = list(frontmatter["lagging_sectors"])
                    elif "lagging" in frontmatter:
                        defaults["lagging_sectors"] = list(frontmatter["lagging"])
                    if "rotating_into" in frontmatter:
                        val = frontmatter["rotating_into"]
                        defaults["rotating_into"] = [v for v in (val or []) if v]
        except Exception:
            # Fallback: just read the flag line
            for line in text.splitlines():
                if line.startswith("flag:"):
                    defaults["flag"] = line.split(":")[1].strip()
        return defaults
    # Handle explicit path
    p = Path(path)
    if p.suffix == ".json":
        with open(p) as f:
            return json.load(f)
    return defaults


def fetch_batch_data(tickers: list[str], period: str = "6mo") -> pd.DataFrame:
    """Batch download price data for all tickers."""
    data = yf.download(tickers, period=period, group_by="ticker", progress=False, threads=True)
    return data


def calculate_technicals(history: pd.DataFrame) -> dict | None:
    """Calculate all technical indicators needed for strategy screening."""
    if history.empty or len(history) < 50:
        return None

    close = history["Close"].dropna()
    if len(close) < 50:
        return None

    high = history["High"].dropna()
    low = history["Low"].dropna()
    volume = history["Volume"].dropna()

    current_price = float(close.iloc[-1])

    ema_10 = close.ewm(span=10, adjust=False).mean()
    ema_21 = close.ewm(span=21, adjust=False).mean()
    sma_50 = close.rolling(50).mean()
    sma_200 = close.rolling(200).mean() if len(close) >= 200 else pd.Series([np.nan])

    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_14 = 100 - (100 / (1 + rs))

    # Bollinger Bands (20, 2)
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    bb_width = ((bb_upper - bb_lower) / bb_mid * 100) if bb_mid.iloc[-1] != 0 else pd.Series([np.nan])

    # ATR 14
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    atr_14 = tr.rolling(14).mean()

    # Volume metrics
    vol_avg_20 = volume.rolling(20).mean()
    recent_vol_declining = all(
        float(volume.iloc[-(i + 1)]) < float(vol_avg_20.iloc[-(i + 1)])
        for i in range(min(2, len(volume) - 20))
    ) if len(volume) > 20 else False

    # Relative strength vs SPY (approximate: % change over 1 month)
    if len(close) >= 21:
        rs_1mo = (float(close.iloc[-1]) / float(close.iloc[-21]) - 1) * 100
    else:
        rs_1mo = 0.0

    # Distance from 21 EMA
    ema_21_val = float(ema_21.iloc[-1]) if not np.isnan(ema_21.iloc[-1]) else 0
    dist_to_ema_21 = ((current_price - ema_21_val) / ema_21_val * 100) if ema_21_val else 0

    # Check if price recently touched 21 EMA (within last 3 days)
    ema_touch_recent = False
    for i in range(1, min(4, len(close))):
        day_low = float(low.iloc[-i])
        day_ema = float(ema_21.iloc[-i])
        if day_ema > 0 and abs(day_low - day_ema) / day_ema < 0.005:
            ema_touch_recent = True
            break

    # Prior swing high (highest close in last 20 days, excluding last 3)
    if len(close) > 5:
        prior_swing_high = float(close.iloc[-20:-3].max()) if len(close) >= 20 else float(close.iloc[:-3].max())
    else:
        prior_swing_high = current_price

    # Check for higher highs / higher lows (uptrend quality)
    uptrend = False
    if len(close) >= 20:
        recent_highs = [float(high.iloc[-i]) for i in range(1, 11)]
        recent_lows = [float(low.iloc[-i]) for i in range(1, 11)]
        # Simple check: most recent 5-day high > prior 5-day high
        if max(recent_highs[:5]) >= max(recent_highs[5:]) and min(recent_lows[:5]) >= min(recent_lows[5:]):
            uptrend = True

    return {
        "price": current_price,
        "ema_10": float(ema_10.iloc[-1]) if not np.isnan(ema_10.iloc[-1]) else None,
        "ema_21": ema_21_val if ema_21_val else None,
        "sma_50": float(sma_50.iloc[-1]) if not np.isnan(sma_50.iloc[-1]) else None,
        "sma_200": float(sma_200.iloc[-1]) if len(sma_200) > 0 and not np.isnan(sma_200.iloc[-1]) else None,
        "rsi_14": float(rsi_14.iloc[-1]) if not np.isnan(rsi_14.iloc[-1]) else None,
        "bb_upper": float(bb_upper.iloc[-1]) if not np.isnan(bb_upper.iloc[-1]) else None,
        "bb_lower": float(bb_lower.iloc[-1]) if not np.isnan(bb_lower.iloc[-1]) else None,
        "bb_mid": float(bb_mid.iloc[-1]) if not np.isnan(bb_mid.iloc[-1]) else None,
        "bb_width_pct": float(bb_width.iloc[-1]) if not np.isnan(bb_width.iloc[-1]) else None,
        "atr_14": float(atr_14.iloc[-1]) if not np.isnan(atr_14.iloc[-1]) else None,
        "volume_last": int(volume.iloc[-1]) if not np.isnan(volume.iloc[-1]) else 0,
        "volume_avg_20": int(vol_avg_20.iloc[-1]) if not np.isnan(vol_avg_20.iloc[-1]) else 0,
        "pullback_vol_declining": recent_vol_declining,
        "rs_1mo_pct": round(rs_1mo, 2),
        "dist_to_ema_21_pct": round(dist_to_ema_21, 2),
        "ema_touch_recent": ema_touch_recent,
        "prior_swing_high": round(prior_swing_high, 2),
        "uptrend": uptrend,
        "above_sma_50": current_price > float(sma_50.iloc[-1]) if not np.isnan(sma_50.iloc[-1]) else False,
        "above_sma_200": current_price > float(sma_200.iloc[-1]) if len(sma_200) > 0 and not np.isnan(sma_200.iloc[-1]) else False,
        "above_ema_21": current_price > ema_21_val if ema_21_val else False,
    }


def scan_tcep(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """TCEP: Trend continuation EMA pullback candidates."""
    if regime["flag"] in ("red", "black"):
        return None
    if sector not in regime["leading_sectors"]:
        return None
    if not tech["above_sma_50"] or not tech["above_sma_200"]:
        return None
    # Must be near 21 EMA (within 2% above, or touching)
    if tech["dist_to_ema_21_pct"] > 2.0 or tech["dist_to_ema_21_pct"] < -1.0:
        return None
    if not tech["pullback_vol_declining"]:
        return None

    # Calculate R/R
    entry = tech["price"]
    stop = tech["ema_21"] - tech["atr_14"] if tech["ema_21"] and tech["atr_14"] else None
    target = tech["prior_swing_high"]
    if not stop or entry <= stop or target <= entry:
        return None
    rr = (target - entry) / (entry - stop)
    if rr < 2.0:
        return None
    stop_width_pct = (entry - stop) / entry * 100
    if stop_width_pct > 3.0:
        return None

    score = min(1.0, (rr / 4.0) * 0.4 + (tech["rs_1mo_pct"] / 15.0) * 0.3 + (0.3 if tech["ema_touch_recent"] else 0.0))

    return {
        "ticker": ticker,
        "strategy": "TCEP",
        "sector": sector,
        "score": round(score, 2),
        "price": round(tech["price"], 2),
        "ema_21": round(tech["ema_21"], 2),
        "dist_to_ema_pct": tech["dist_to_ema_21_pct"],
        "stop": round(stop, 2),
        "target": round(target, 2),
        "rr": round(rr, 1),
        "rs_1mo_pct": tech["rs_1mo_pct"],
        "pullback_vol_declining": tech["pullback_vol_declining"],
        "ema_touch_recent": tech["ema_touch_recent"],
        "notes": f"{'EMA touched recently' if tech['ema_touch_recent'] else 'Approaching EMA'}, R/R {rr:.1f}:1",
    }


def scan_orb(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """ORB: Opening range breakout candidates. Pre-market identifies stocks likely to gap."""
    if regime["flag"] == "black":
        return None
    if tech["price"] < 10 or tech["price"] > 200:
        return None
    if tech["volume_avg_20"] < 1_000_000:
        return None
    # Prefer stocks in leading sectors for long-side ORB
    sector_match = sector in regime["leading_sectors"]
    if not sector_match and regime["flag"] != "green":
        return None
    # ORB candidates need recent volatility (ATR) but not excessive
    if not tech["atr_14"]:
        return None
    atr_pct = tech["atr_14"] / tech["price"] * 100
    if atr_pct < 0.8 or atr_pct > 5.0:
        return None

    score = min(1.0,
        (tech["volume_avg_20"] / 5_000_000) * 0.3
        + (0.3 if sector_match else 0.0)
        + min(0.4, atr_pct / 3.0 * 0.4)
    )

    return {
        "ticker": ticker,
        "strategy": "ORB",
        "sector": sector,
        "score": round(score, 2),
        "price": round(tech["price"], 2),
        "atr_14": round(tech["atr_14"], 2),
        "atr_pct": round(atr_pct, 2),
        "volume_avg": tech["volume_avg_20"],
        "in_leading_sector": sector_match,
        "notes": f"Avg vol {tech['volume_avg_20']:,}, ATR {atr_pct:.1f}% — confirm gap >1% at open",
    }


def scan_edvp(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """EDVP: Event-driven volatility play candidates. Earnings check deferred to orchestrator."""
    if regime["flag"] in ("red", "black"):
        return None
    if sector not in regime["leading_sectors"]:
        return None
    if not tech["above_sma_50"] or not tech["above_sma_200"]:
        return None
    # EDVP needs price low enough for options affordability
    # Under exploration mode, relax this but still flag it
    affordable = tech["price"] <= 100

    score = min(1.0,
        (0.3 if affordable else 0.1)
        + (tech["rs_1mo_pct"] / 15.0) * 0.3
        + (0.2 if tech["above_ema_21"] else 0.0)
        + (0.2 if tech["uptrend"] else 0.0)
    )

    return {
        "ticker": ticker,
        "strategy": "EDVP",
        "sector": sector,
        "score": round(score, 2),
        "price": round(tech["price"], 2),
        "above_ema_21": tech["above_ema_21"],
        "above_sma_50": tech["above_sma_50"],
        "rs_1mo_pct": tech["rs_1mo_pct"],
        "affordable_options": affordable,
        "notes": f"Earnings check needed via MCP. {'Options affordable' if affordable else 'May need spread'}",
    }


def scan_erp(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """ERP: Earnings reaction play candidates. Earnings check deferred to orchestrator."""
    # ERP works in any regime
    if regime["flag"] == "black":
        return None
    if tech["volume_avg_20"] < 500_000:
        return None
    # ERP needs liquid stocks that can gap meaningfully
    if tech["price"] < 10:
        return None
    # Check for recent volume spike (proxy for earnings reaction)
    if tech["volume_last"] > 0 and tech["volume_avg_20"] > 0:
        vol_ratio = tech["volume_last"] / tech["volume_avg_20"]
        if vol_ratio < 1.5:
            return None
    else:
        return None

    score = min(1.0,
        min(0.4, vol_ratio / 4.0 * 0.4)
        + (tech["rs_1mo_pct"] / 15.0) * 0.3
        + (0.3 if tech["above_sma_50"] else 0.1)
    )

    return {
        "ticker": ticker,
        "strategy": "ERP",
        "sector": sector,
        "score": round(score, 2),
        "price": round(tech["price"], 2),
        "volume_ratio": round(vol_ratio, 1),
        "above_sma_50": tech["above_sma_50"],
        "notes": f"Volume {vol_ratio:.1f}x avg — confirm earnings reported and gap >3% at open",
    }


def scan_mrf(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """MRF: Mean reversion fade candidates."""
    if regime["flag"] == "black":
        return None
    if not tech["bb_width_pct"] or not tech["bb_upper"] or not tech["bb_lower"]:
        return None
    if tech["bb_width_pct"] > 10.0:
        return None  # Not range-bound
    if tech["volume_avg_20"] < 500_000:
        return None

    price = tech["price"]
    bb_upper = tech["bb_upper"]
    bb_lower = tech["bb_lower"]
    bb_mid = tech["bb_mid"]
    rsi = tech["rsi_14"]

    direction = None
    # At upper band + RSI overbought = short fade candidate
    if price >= bb_upper * 0.995 and rsi and rsi > 75:
        direction = "short"
    # At lower band + RSI oversold = long fade candidate
    elif price <= bb_lower * 1.005 and rsi and rsi < 25:
        direction = "long"
    else:
        return None

    # Check R/R to midline
    if direction == "long":
        entry = price
        stop = bb_lower - (tech["atr_14"] * 0.5 if tech["atr_14"] else 0)
        target = bb_mid
    else:
        entry = price
        stop = bb_upper + (tech["atr_14"] * 0.5 if tech["atr_14"] else 0)
        target = bb_mid

    if direction == "long" and (entry <= stop or target <= entry):
        return None
    if direction == "short" and (entry >= stop or target >= entry):
        return None

    rr = abs(target - entry) / abs(entry - stop) if abs(entry - stop) > 0 else 0
    if rr < 1.5:
        return None

    # Breakdown check: if SMA 50 is declining, skip
    if tech["sma_50"] and direction == "long":
        # Rough check: is price well below SMA 50?
        if price < tech["sma_50"] * 0.95:
            return None

    score = min(1.0,
        min(0.3, rr / 3.0 * 0.3)
        + (0.3 if tech["bb_width_pct"] < 6 else 0.15)
        + (0.2 if (rsi < 20 or rsi > 80) else 0.1)
        + (0.2 if regime["flag"] in ("yellow", "red") else 0.1)
    )

    return {
        "ticker": ticker,
        "strategy": "MRF",
        "sector": sector,
        "score": round(score, 2),
        "direction": direction,
        "price": round(price, 2),
        "bb_upper": round(bb_upper, 2),
        "bb_lower": round(bb_lower, 2),
        "bb_mid": round(bb_mid, 2),
        "bb_width_pct": round(tech["bb_width_pct"], 2),
        "rsi_14": round(rsi, 1) if rsi else None,
        "stop": round(stop, 2),
        "target": round(target, 2),
        "rr": round(rr, 1),
        "notes": f"{'Long' if direction == 'long' else 'Short'} fade, BB width {tech['bb_width_pct']:.1f}%, RSI {rsi:.0f}",
    }


def scan_smr(ticker: str, sector: str, tech: dict, regime: dict) -> dict | None:
    """SMR: Sector momentum rotation candidates."""
    if regime["flag"] == "black":
        return None
    # SMR requires the sector to be rotating in
    if sector not in regime.get("rotating_into", []):
        return None
    if not tech["above_sma_50"] or not tech["above_sma_200"]:
        return None
    if tech["volume_avg_20"] < 1_000_000:
        return None
    if tech["price"] < 15:
        return None

    # Must be top RS in the rotating sector
    if tech["rs_1mo_pct"] < 3.0:
        return None

    # Entry: near 10 EMA or consolidating
    near_ema_10 = tech["ema_10"] and abs(tech["price"] - tech["ema_10"]) / tech["ema_10"] < 0.02

    # Calculate R/R for swing
    entry = tech["price"]
    stop = tech["ema_21"] - tech["atr_14"] if tech["ema_21"] and tech["atr_14"] else None
    if not stop or entry <= stop:
        return None
    target = entry * 1.10  # 10% target
    rr = (target - entry) / (entry - stop)
    if rr < 2.5:
        return None
    stop_width_pct = (entry - stop) / entry * 100
    if stop_width_pct > 5.0:
        return None

    score = min(1.0,
        (tech["rs_1mo_pct"] / 15.0) * 0.4
        + (0.3 if near_ema_10 else 0.1)
        + min(0.3, rr / 5.0 * 0.3)
    )

    return {
        "ticker": ticker,
        "strategy": "SMR",
        "sector": sector,
        "score": round(score, 2),
        "price": round(entry, 2),
        "rs_1mo_pct": tech["rs_1mo_pct"],
        "near_ema_10": near_ema_10,
        "stop": round(stop, 2),
        "target": round(target, 2),
        "rr": round(rr, 1),
        "stop_width_pct": round(stop_width_pct, 1),
        "notes": f"Sector rotating in, RS +{tech['rs_1mo_pct']:.1f}%, {'at EMA10' if near_ema_10 else 'watch for pullback'}",
    }


def get_spy_returns(batch_data: pd.DataFrame, tickers: list[str]) -> float:
    """Get SPY 1-month return for RS comparison. Returns 0 if SPY not in data."""
    if "SPY" not in tickers:
        return 0.0
    try:
        spy_close = batch_data["SPY"]["Close"].dropna()
        if len(spy_close) >= 21:
            return (float(spy_close.iloc[-1]) / float(spy_close.iloc[-21]) - 1) * 100
    except (KeyError, IndexError):
        pass
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="Pre-market scanner for The Money")
    parser.add_argument("--regime", help="Path to regime JSON/YAML file")
    parser.add_argument("--universe", default=str(DEFAULT_UNIVERSE), help="Path to universe JSON")
    parser.add_argument("--output", help="Output path for watchlist JSON")
    parser.add_argument("--top", type=int, default=5, help="Max candidates per strategy")
    args = parser.parse_args()

    start_time = time.time()

    regime = load_regime(args.regime)
    sectors, sector_etfs = load_universe(Path(args.universe))

    # Build flat ticker list with sector mapping
    ticker_sector_map = {}
    all_tickers = []
    for sector, tickers in sectors.items():
        for t in tickers:
            ticker_sector_map[t] = sector
            all_tickers.append(t)

    # Add SPY for relative strength baseline
    if "SPY" not in all_tickers:
        all_tickers.append("SPY")

    print(f"Scanning {len(all_tickers) - 1} stocks across {len(sectors)} sectors...", file=sys.stderr)
    print(f"Regime: {regime['flag']} | Leading: {', '.join(regime['leading_sectors'])}", file=sys.stderr)

    # Batch download
    batch_data = fetch_batch_data(all_tickers, period="1y")
    spy_return = get_spy_returns(batch_data, all_tickers)

    # Scan each ticker against all strategies
    scanners = [scan_tcep, scan_orb, scan_edvp, scan_erp, scan_mrf, scan_smr]
    candidates = {s.__name__.replace("scan_", "").upper(): [] for s in scanners}
    errors = []

    for ticker in all_tickers:
        if ticker == "SPY":
            continue
        sector = ticker_sector_map.get(ticker, "Unknown")

        try:
            if len(all_tickers) > 2:
                ticker_data = batch_data[ticker].copy()
            else:
                ticker_data = batch_data.copy()

            tech = calculate_technicals(ticker_data)
            if not tech:
                continue

            # Adjust RS relative to SPY
            tech["rs_1mo_pct"] = tech["rs_1mo_pct"] - spy_return

            for scanner in scanners:
                result = scanner(ticker, sector, tech, regime)
                if result:
                    strategy_key = result["strategy"]
                    candidates[strategy_key].append(result)
        except Exception as e:
            errors.append(f"{ticker}: {e}")

    # Sort each strategy's candidates by score, take top N
    for strategy in candidates:
        candidates[strategy].sort(key=lambda x: x.get("score", 0), reverse=True)
        candidates[strategy] = candidates[strategy][: args.top]

    total = sum(len(v) for v in candidates.values())
    duration = round(time.time() - start_time, 1)

    watchlist = {
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
        "scan_time": datetime.now().strftime("%H:%M:%S"),
        "regime": regime,
        "universe_size": len(all_tickers) - 1,
        "candidates": candidates,
        "total_candidates": total,
        "scan_duration_seconds": duration,
        "errors": errors[:10],
        "deferred_checks": [
            "Earnings dates (EDVP/ERP) — check via yahoo-finance MCP",
            "IV Rank (EDVP) — check via options chain MCP",
            "Pre-market gap/volume (ORB/ERP) — check at market open via MCP",
            "Options liquidity (all) — check via options chain MCP",
        ],
    }

    output_json = json.dumps(watchlist, indent=2, default=str)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"Watchlist written to {output_path}", file=sys.stderr)
    else:
        # Default: write to raw/watchlists/ with today's date
        default_path = DEFAULT_OUTPUT_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        default_path.parent.mkdir(parents=True, exist_ok=True)
        default_path.write_text(output_json, encoding="utf-8")
        print(f"Watchlist written to {default_path}", file=sys.stderr)

    # Always print to stdout for piping
    print(output_json)

    print(f"\nDone: {total} candidates across {sum(1 for v in candidates.values() if v)} strategies in {duration}s", file=sys.stderr)
    if errors:
        print(f"Warnings: {len(errors)} tickers had issues", file=sys.stderr)


if __name__ == "__main__":
    main()
