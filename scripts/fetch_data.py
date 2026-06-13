#!/usr/bin/env python3
"""Prefetch market data for a ticker. Outputs JSON to stdout."""

import json
import sys
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


def fetch_price(ticker: yf.Ticker, history: pd.DataFrame) -> dict:
    info = ticker.info
    current = info.get("currentPrice") or info.get("regularMarketPrice")
    prev_close = info.get("previousClose")
    change_pct = None
    if current and prev_close and prev_close != 0:
        change_pct = round((current - prev_close) / prev_close * 100, 2)

    high_52w = info.get("fiftyTwoWeekHigh")
    low_52w = info.get("fiftyTwoWeekLow")

    recent = []
    if not history.empty:
        tail = history.tail(10)
        for idx, row in tail.iterrows():
            recent.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(row.get("Open", 0), 2),
                "high": round(row.get("High", 0), 2),
                "low": round(row.get("Low", 0), 2),
                "close": round(row.get("Close", 0), 2),
                "volume": int(row.get("Volume", 0)),
            })

    return {
        "current": current,
        "previous_close": prev_close,
        "change_pct": change_pct,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "recent_history": recent,
    }


def fetch_technicals(history: pd.DataFrame) -> dict:
    if history.empty or len(history) < 20:
        return {"error": "Insufficient data for technical analysis"}

    close = history["Close"]
    result = {}

    if len(close) >= 10:
        result["sma_10"] = round(close.rolling(10).mean().iloc[-1], 2)
    if len(close) >= 20:
        result["sma_20"] = round(close.rolling(20).mean().iloc[-1], 2)
    if len(close) >= 50:
        result["sma_50"] = round(close.rolling(50).mean().iloc[-1], 2)
    if len(close) >= 200:
        result["sma_200"] = round(close.rolling(200).mean().iloc[-1], 2)

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
    result["rsi_14"] = round(100 - (100 / (1 + rs)), 2)

    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9).mean()
    result["macd"] = {
        "macd_line": round(macd_line.iloc[-1], 4),
        "signal_line": round(signal_line.iloc[-1], 4),
        "histogram": round((macd_line.iloc[-1] - signal_line.iloc[-1]), 4),
    }

    vol = history["Volume"]
    result["volume_current"] = int(vol.iloc[-1])
    result["volume_avg_20"] = int(vol.rolling(20).mean().iloc[-1])

    high = history["High"]
    low = history["Low"]
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    result["atr_14"] = round(tr.rolling(14).mean().iloc[-1], 2)

    return result


def fetch_fundamentals(ticker: yf.Ticker) -> dict:
    info = ticker.info
    fields = {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "eps_ttm": info.get("trailingEps"),
        "forward_eps": info.get("forwardEps"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "revenue_ttm": info.get("totalRevenue"),
        "ebitda": info.get("ebitda"),
        "profit_margin": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "roe": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "free_cash_flow": info.get("freeCashflow"),
    }
    return {k: v for k, v in fields.items() if v is not None}


def fetch_news(ticker: yf.Ticker) -> list:
    try:
        news = ticker.get_news(count=15)
    except Exception:
        return []

    articles = []
    for article in (news or []):
        if "content" in article:
            content = article["content"]
            title = content.get("title", "")
            summary = content.get("summary", "")
            provider = content.get("provider", {})
            publisher = provider.get("displayName", "Unknown")
            pub_date = content.get("pubDate", "")
        else:
            title = article.get("title", "")
            summary = ""
            publisher = article.get("publisher", "Unknown")
            pub_date = ""

        if title:
            articles.append({
                "title": title,
                "summary": summary,
                "publisher": publisher,
                "published": pub_date,
            })

    return articles


def fetch_options(ticker: yf.Ticker) -> dict:
    try:
        expirations = ticker.options
    except Exception:
        return {"error": "No options data available"}

    if not expirations:
        return {"error": "No options expirations found"}

    nearest = list(expirations[:3])
    chains = {}

    for exp in nearest:
        try:
            opt = ticker.option_chain(exp)
        except Exception:
            continue

        def summarize_chain(df: pd.DataFrame) -> list:
            if df.empty:
                return []
            rows = []
            for _, r in df.iterrows():
                rows.append({
                    "strike": r.get("strike"),
                    "last_price": r.get("lastPrice"),
                    "bid": r.get("bid"),
                    "ask": r.get("ask"),
                    "volume": int(r.get("volume", 0)) if pd.notna(r.get("volume")) else 0,
                    "open_interest": int(r.get("openInterest", 0)) if pd.notna(r.get("openInterest")) else 0,
                    "implied_volatility": round(r.get("impliedVolatility", 0), 4),
                })
            return rows

        chains[exp] = {
            "calls": summarize_chain(opt.calls),
            "puts": summarize_chain(opt.puts),
        }

    return {"expirations": nearest, "chains": chains}


def fetch_insiders(ticker: yf.Ticker) -> list:
    try:
        insider = ticker.insider_transactions
    except Exception:
        return []

    if insider is None or insider.empty:
        return []

    txns = []
    for _, row in insider.head(10).iterrows():
        txns.append({
            "insider": str(row.get("Insider", "")),
            "relation": str(row.get("Position", "")),
            "transaction": str(row.get("Transaction", "")),
            "shares": int(row.get("Shares", 0)) if pd.notna(row.get("Shares")) else 0,
            "date": str(row.get("Start Date", "")),
        })

    return txns


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python fetch_data.py <TICKER>"}))
        sys.exit(1)

    symbol = sys.argv[1].upper()
    ticker = yf.Ticker(symbol)

    end = datetime.now()
    start = end - timedelta(days=365)
    history = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    data = {
        "ticker": symbol,
        "fetched_at": datetime.now().isoformat(),
        "price": fetch_price(ticker, history),
        "technicals": fetch_technicals(history),
        "fundamentals": fetch_fundamentals(ticker),
        "news": fetch_news(ticker),
        "options": fetch_options(ticker),
        "insiders": fetch_insiders(ticker),
    }

    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
