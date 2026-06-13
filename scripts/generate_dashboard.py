"""Generate a static HTML P&L dashboard from ghost trade records."""
from __future__ import annotations

import argparse
import html as _html
import json
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except ImportError as e:
    raise ImportError("pandas is required: pip install pandas") from e

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_closed_trades(data_dir: Path) -> "pd.DataFrame":
    frames = []
    ghost_dir = data_dir / "ghost_trades"
    if ghost_dir.is_dir():
        for f in sorted(ghost_dir.glob("*.jsonl")):
            try:
                df = pd.read_json(f, lines=True)
                frames.append(df)
            except Exception:
                continue
    if not frames:
        return pd.DataFrame()
    all_trades = pd.concat(frames, ignore_index=True)
    if "status" not in all_trades.columns:
        return pd.DataFrame()
    return all_trades[all_trades["status"] == "closed"].copy()


def load_registry(data_dir: Path) -> dict:
    path = data_dir / "strategies" / "registry_state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# P&L computation
# ---------------------------------------------------------------------------

def _extract_pnl(outcome) -> float:
    if isinstance(outcome, dict):
        val = outcome.get("pnl", 0) or 0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def compute_strategy_pnl(trades_df: "pd.DataFrame") -> dict[str, dict]:
    if trades_df.empty or "strategy_id" not in trades_df.columns:
        return {}
    results: dict[str, dict] = {}
    for sid, group in trades_df.groupby("strategy_id"):
        pnls = group["outcome"].apply(_extract_pnl) if "outcome" in group.columns else pd.Series([0.0] * len(group))
        wins = pnls[pnls > 0]
        losses = pnls[pnls <= 0]
        cumulative = pnls.cumsum()
        peak = cumulative.cummax()
        drawdown = float((cumulative - peak).min()) if len(pnls) > 0 else 0.0
        results[str(sid)] = {
            "total_trades": len(group),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(group) if len(group) > 0 else 0.0,
            "avg_win": float(wins.mean()) if len(wins) > 0 else 0.0,
            "avg_loss": float(losses.mean()) if len(losses) > 0 else 0.0,
            "net_expectancy": float(pnls.mean()) if len(pnls) > 0 else 0.0,
            "max_drawdown": drawdown,
            "net_pnl": float(pnls.sum()),
        }
    return results


def compute_regime_attribution(trades_df: "pd.DataFrame") -> dict[str, dict[str, dict]]:
    """Returns {strategy_id: {regime: {count, net_pnl, win_rate}}}."""
    if trades_df.empty:
        return {}
    # GhostTrade schema serialises the field as "regime"
    if "regime" not in trades_df.columns:
        trades_df = trades_df.copy()
        trades_df["regime"] = "unknown"
    result: dict[str, dict[str, dict]] = {}
    for (sid, regime), group in trades_df.groupby(["strategy_id", "regime"]):
        pnls = group["outcome"].apply(_extract_pnl) if "outcome" in group.columns else pd.Series([0.0] * len(group))
        wins = pnls[pnls > 0]
        sid, regime = str(sid), str(regime)
        if sid not in result:
            result[sid] = {}
        result[sid][regime] = {
            "count": len(group),
            "net_pnl": float(pnls.sum()),
            "win_rate": len(wins) / len(group) if len(group) > 0 else 0.0,
        }
    return result


def format_regime_breakdown(regime_data: dict[str, dict]) -> str:
    parts = []
    for regime, stats in sorted(regime_data.items()):
        pnl = stats["net_pnl"]
        sign = "+" if pnl >= 0 else "-"
        parts.append(f"{_html.escape(regime)}: {sign}${abs(pnl):.0f} ({stats['count']} trades)")
    return " | ".join(parts) if parts else "—"


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

_CSS = """
body{font-family:system-ui,sans-serif;margin:2rem;background:#1a1a2e;color:#e0e0e0}
h1{color:#a0c4ff}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.9rem}
th,td{padding:.45rem .9rem;border:1px solid #333;text-align:right}
th{background:#16213e;color:#a0c4ff;text-align:center}
td:first-child{text-align:left;font-weight:600}
.positive{color:#4caf50}
.negative{color:#f44336}
.neutral{color:#9e9e9e}
.regime{font-size:.8rem;color:#b0bec5}
footer{margin-top:2rem;color:#555;font-size:.8rem}
"""

def _pnl_class(val: float) -> str:
    if val > 0:
        return "positive"
    if val < 0:
        return "negative"
    return "neutral"


def _fmt_money(val: float) -> str:
    if val > 0:
        return f"+${val:.2f}"
    if val < 0:
        return f"-${abs(val):.2f}"
    return "$0.00"


def _build_strategy_table(
    pnl: dict[str, dict],
    regime_attr: dict[str, dict[str, dict]],
    registry: dict,
) -> str:
    if not pnl:
        return "<p class='neutral'>No closed ghost trades found.</p>"

    rows = []
    for sid, m in sorted(pnl.items()):
        reg_html = ""
        if sid in regime_attr:
            reg_html = f"<div class='regime'>{format_regime_breakdown(regime_attr[sid])}</div>"
        net_cls = _pnl_class(m["net_pnl"])
        dd_cls = _pnl_class(-m["max_drawdown"])  # drawdown is negative; red if large
        rows.append(f"""
  <tr>
    <td>{_html.escape(sid)}{reg_html}</td>
    <td>{m['total_trades']}</td>
    <td>{m['win_rate']*100:.1f}%</td>
    <td class='positive'>{_fmt_money(m['avg_win'])}</td>
    <td class='{_pnl_class(m["avg_loss"])}'>{_fmt_money(m['avg_loss'])}</td>
    <td class='{_pnl_class(m["net_expectancy"])}'>{_fmt_money(m['net_expectancy'])}</td>
    <td class='{dd_cls}'>{_fmt_money(m['max_drawdown'])}</td>
    <td class='{net_cls}'><strong>{_fmt_money(m['net_pnl'])}</strong></td>
  </tr>""")

    header = """<table>
<thead><tr>
  <th>Strategy</th><th>Trades</th><th>Win %</th>
  <th>Avg Win</th><th>Avg Loss</th><th>Expectancy</th>
  <th>Max DD</th><th>Net P&amp;L</th>
</tr></thead>
<tbody>"""
    return header + "".join(rows) + "\n</tbody></table>"


def generate_dashboard(data_dir: Path) -> str:
    trades = load_closed_trades(data_dir)
    registry = load_registry(data_dir)
    pnl = compute_strategy_pnl(trades)
    regime_attr = compute_regime_attribution(trades) if not trades.empty else {}

    strategy_table = _build_strategy_table(pnl, regime_attr, registry)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Trading Desk Dashboard</title>
  <style>{_CSS}</style>
</head>
<body>
  <h1>Strategy P&amp;L Dashboard</h1>
  {strategy_table}
  <footer>Generated: {timestamp}</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate static P&L dashboard HTML")
    parser.add_argument("--data-dir", default="data/tm", help="Path to data/tm directory")
    parser.add_argument("--output", default="data/tm/dashboard.html", help="Output HTML path")
    parser.add_argument("--open", action="store_true", dest="open_browser", help="Open in browser after generation")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output = Path(args.output)

    html = generate_dashboard(data_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {output.resolve()}")

    if args.open_browser:
        webbrowser.open(output.resolve().as_uri())


if __name__ == "__main__":
    main()
