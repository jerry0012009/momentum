#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from run_manual_narrow_paper_lanes import build_rank29_trades_baseline  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "rank29_trigger_tf_monthly"
CACHE_DIR = ARTIFACT_DIR / "cache"
PLOT_PATH = ARTIFACT_DIR / "rank29_trigger_tf_monthly_lines.svg"
REPORT_PATH = ARTIFACT_DIR / "report.md"

ASSET_TO_BINANCE = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
COSTS = [6.0, 10.0, 15.0, 20.0]
DAYS = 365 * 5 + 10
INTERVAL = "15m"
COLORS = {"short": "#d62728", "medium": "#ff7f0e", "long": "#1f77b4"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def download_binance_bars(symbol: str, *, interval: str = INTERVAL, days: int = DAYS) -> pd.DataFrame:
    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        last_close_time = int(data[-1][6])
        current = last_close_time + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "close_ts": pd.to_datetime(df["close_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    out = out.dropna().sort_values("timestamp").reset_index(drop=True)
    now_ts = pd.Timestamp.now("UTC")
    out = out[out["close_ts"] < now_ts].copy().reset_index(drop=True)
    return out


def load_bars(asset: str) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    symbol = ASSET_TO_BINANCE[asset]
    path = CACHE_DIR / f"{symbol}__5y__15m.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
        df["close_ts"] = pd.to_datetime(df["close_ts"], utc=True, format="mixed")
        return df
    df = download_binance_bars(symbol)
    df.to_csv(path, index=False)
    return df


def recompute_cost(df: pd.DataFrame, cost_bps_per_side: float) -> pd.DataFrame:
    out = df.copy()
    cost_rate = cost_bps_per_side / 10000.0
    out["cost_bps_per_side"] = cost_bps_per_side
    out["net_ret"] = (1.0 + out["gross_ret"]) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    return out


def _asset_month_panel(trades: pd.DataFrame, group_col: str) -> pd.DataFrame:
    x = trades.copy()
    x["month"] = pd.to_datetime(x["exit_ts"], utc=True).dt.to_period("M").astype(str)
    out = (
        x.groupby(["month", "asset", group_col], as_index=False)
        .agg(
            trades=("net_ret", "size"),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            asset_month_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            avg_net_ret=("net_ret", "mean"),
        )
        .sort_values(["month", group_col, "asset"])
        .reset_index(drop=True)
    )
    return out


def monthly_trigger_panel(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    asset_month = _asset_month_panel(trades, "trigger_tf")
    monthly = (
        asset_month.groupby(["month", "trigger_tf"], as_index=False)
        .agg(
            active_assets=("asset", "nunique"),
            total_trades=("trades", "sum"),
            mean_asset_month_return=("asset_month_return", "mean"),
            median_asset_month_return=("asset_month_return", "median"),
            positive_asset_ratio=("asset_month_return", lambda s: float((s > 0).mean())),
        )
        .sort_values(["month", "trigger_tf"])
        .reset_index(drop=True)
    )
    return asset_month, monthly


def trigger_stability_summary(trades: pd.DataFrame) -> pd.DataFrame:
    asset_month, monthly = monthly_trigger_panel(trades)
    asset_total = (
        trades.groupby(["trigger_tf", "asset"], as_index=False)
        .agg(
            trades=("net_ret", "size"),
            total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            avg_net_ret=("net_ret", "mean"),
        )
    )
    total_summary = (
        asset_total.groupby("trigger_tf", as_index=False)
        .agg(
            mean_asset_total_return=("total_return", "mean"),
            median_asset_total_return=("total_return", "median"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_asset_win_rate=("win_rate", "mean"),
            mean_asset_avg_net_ret=("avg_net_ret", "mean"),
            total_trades=("trades", "sum"),
        )
        .sort_values("trigger_tf")
        .reset_index(drop=True)
    )
    monthly_summary = (
        monthly.groupby("trigger_tf", as_index=False)
        .agg(
            months=("month", "size"),
            positive_month_ratio=("mean_asset_month_return", lambda s: float((s > 0).mean())),
            mean_month_return=("mean_asset_month_return", "mean"),
            median_month_return=("mean_asset_month_return", "median"),
            worst_month_return=("mean_asset_month_return", "min"),
            best_month_return=("mean_asset_month_return", "max"),
            mean_month_trades=("total_trades", "mean"),
        )
        .sort_values("trigger_tf")
        .reset_index(drop=True)
    )
    return monthly_summary.merge(total_summary, on="trigger_tf", how="left")


def variant_summary(trades: pd.DataFrame, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    variants = {
        "baseline": trades,
        "drop_short": trades[trades["trigger_tf"] != "short"].copy(),
        "drop_medium": trades[trades["trigger_tf"] != "medium"].copy(),
        "long_only": trades[trades["trigger_tf"] == "long"].copy(),
    }
    rows: list[dict[str, object]] = []
    monthly_rows: list[pd.DataFrame] = []
    for variant, df in variants.items():
        if df.empty:
            continue
        asset_month = _asset_month_panel(df, "asset")
        asset_month = asset_month.rename(columns={"asset": "group_asset"})
        monthly = (
            asset_month.groupby("month", as_index=False)
            .agg(
                active_assets=("group_asset", "nunique"),
                total_trades=("trades", "sum"),
                mean_asset_month_return=("asset_month_return", "mean"),
                positive_asset_ratio=("asset_month_return", lambda s: float((s > 0).mean())),
            )
            .sort_values("month")
            .reset_index(drop=True)
        )
        monthly["variant"] = variant
        monthly["cost_bps_per_side"] = cost_bps_per_side
        monthly_rows.append(monthly)

        asset_total = (
            df.groupby("asset", as_index=False)
            .agg(
                trades=("net_ret", "size"),
                total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
                win_rate=("net_ret", lambda s: float((s > 0).mean())),
                avg_net_ret=("net_ret", "mean"),
            )
        )
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": cost_bps_per_side,
                "trades": int(len(df)),
                "mean_asset_total_return": float(asset_total["total_return"].mean()),
                "median_asset_total_return": float(asset_total["total_return"].median()),
                "positive_asset_ratio": float((asset_total["total_return"] > 0).mean()),
                "mean_asset_win_rate": float(asset_total["win_rate"].mean()),
                "mean_asset_avg_net_ret": float(asset_total["avg_net_ret"].mean()),
                "months": int(len(monthly)),
                "positive_month_ratio": float((monthly["mean_asset_month_return"] > 0).mean()),
                "mean_month_return": float(monthly["mean_asset_month_return"].mean()),
                "worst_month_return": float(monthly["mean_asset_month_return"].min()),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant"]).reset_index(drop=True)
    monthly_panel = pd.concat(monthly_rows, ignore_index=True) if monthly_rows else pd.DataFrame()
    return summary, monthly_panel


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def _polyline(points: list[tuple[float, float]], color: str) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    circles = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}" />' for x, y in points
    )
    return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}" />{circles}'


def plot_monthly_lines_svg(monthly: pd.DataFrame) -> None:
    pivot = monthly.pivot(index="month", columns="trigger_tf", values="mean_asset_month_return").sort_index().fillna(0.0)
    cum = (1.0 + pivot).cumprod() - 1.0

    width = 1400
    height = 900
    margin_left = 80
    margin_right = 40
    margin_top = 60
    panel_gap = 80
    panel_h = 280
    plot_w = width - margin_left - margin_right

    x_labels = list(pivot.index)
    x_vals = list(range(len(x_labels)))
    if len(x_vals) <= 1:
        x_positions = [margin_left + plot_w / 2]
    else:
        x_positions = [margin_left + plot_w * i / (len(x_vals) - 1) for i in x_vals]

    def scale(vals: pd.DataFrame, y_top: float) -> tuple[float, float, dict[str, list[tuple[float, float]]]]:
        ymin = min(float(vals.min().min()), 0.0)
        ymax = max(float(vals.max().max()), 0.0)
        pad = max((ymax - ymin) * 0.12, 0.01)
        ymin -= pad
        ymax += pad
        def y_map(v: float) -> float:
            return y_top + panel_h * (1 - (v - ymin) / (ymax - ymin))
        series_points: dict[str, list[tuple[float, float]]] = {}
        for col in vals.columns:
            series_points[col] = [(x_positions[i], y_map(float(vals.iloc[i][col]))) for i in range(len(vals))]
        return ymin, ymax, series_points

    y1_top = margin_top
    y2_top = margin_top + panel_h + panel_gap
    ymin1, ymax1, pts1 = scale(pivot, y1_top)
    ymin2, ymax2, pts2 = scale(cum, y2_top)

    def axis_and_grid(y_top: float, ymin: float, ymax: float, title: str) -> str:
        elems = [
            f'<text x="{margin_left}" y="{y_top - 20}" font-size="22" font-family="Arial" font-weight="bold">{title}</text>',
            f'<line x1="{margin_left}" y1="{y_top}" x2="{margin_left}" y2="{y_top + panel_h}" stroke="#333" />',
            f'<line x1="{margin_left}" y1="{y_top + panel_h}" x2="{margin_left + plot_w}" y2="{y_top + panel_h}" stroke="#333" />',
        ]
        ticks = 5
        for i in range(ticks + 1):
            frac = i / ticks
            y = y_top + panel_h * frac
            val = ymax - (ymax - ymin) * frac
            elems.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{margin_left + plot_w}" y2="{y:.1f}" stroke="#ddd" />')
            elems.append(f'<text x="10" y="{y + 5:.1f}" font-size="12" font-family="Arial">{val * 100:.1f}%</text>')
        return "".join(elems)

    x_tick_elems = []
    tick_step = max(1, len(x_labels) // 12)
    for i, label in enumerate(x_labels):
        if i % tick_step != 0 and i != len(x_labels) - 1:
            continue
        x = x_positions[i]
        x_tick_elems.append(f'<line x1="{x:.1f}" y1="{y2_top + panel_h}" x2="{x:.1f}" y2="{y2_top + panel_h + 6}" stroke="#333" />')
        x_tick_elems.append(f'<text x="{x:.1f}" y="{y2_top + panel_h + 22}" font-size="12" text-anchor="middle" font-family="Arial">{label}</text>')

    legend = []
    lx = width - 250
    ly = 30
    for idx, key in enumerate([c for c in ["short", "medium", "long"] if c in pivot.columns]):
        y = ly + idx * 24
        color = COLORS[key]
        legend.append(f'<line x1="{lx}" y1="{y}" x2="{lx+24}" y2="{y}" stroke="{color}" stroke-width="3" />')
        legend.append(f'<text x="{lx+34}" y="{y+4}" font-size="14" font-family="Arial">{key}</text>')

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white" />',
        '<text x="40" y="28" font-size="26" font-family="Arial" font-weight="bold">Rank29 trigger_tf monthly lines (5y, equal-weight across BTC/ETH/SOL, 6bps)</text>',
        axis_and_grid(y1_top, ymin1, ymax1, 'Mean asset monthly return by trigger_tf'),
        axis_and_grid(y2_top, ymin2, ymax2, 'Cumulative equal-weight monthly return by trigger_tf'),
        *legend,
    ]
    for key, points in pts1.items():
        body.append(_polyline(points, COLORS.get(key, '#000')))
    for key, points in pts2.items():
        body.append(_polyline(points, COLORS.get(key, '#000')))
    body.extend(x_tick_elems)
    body.append('</svg>')
    PLOT_PATH.write_text("\n".join(body), encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    all_trades = []
    asset_rows = []
    for asset in ASSET_TO_BINANCE:
        bars = load_bars(asset)
        trades = build_rank29_trades_baseline(asset, bars)
        trades = trades[trades["complete_trade"]].copy().reset_index(drop=True)
        for col in ["event_ts", "entry_ts", "exit_ts"]:
            trades[col] = pd.to_datetime(trades[col], utc=True)
        all_trades.append(trades)
        asset_rows.append(
            {
                "asset": asset,
                "bars": len(bars),
                "trades": len(trades),
                "sample_start_utc": bars["timestamp"].min(),
                "sample_end_utc": bars["timestamp"].max(),
            }
        )

    trades = pd.concat(all_trades, ignore_index=True).sort_values(["entry_ts", "asset"]).reset_index(drop=True)
    asset_df = pd.DataFrame(asset_rows)
    asset_df.to_csv(ARTIFACT_DIR / "asset_coverage.csv", index=False)
    trades.to_csv(ARTIFACT_DIR / "all_trades_6bps.csv", index=False)

    asset_month, monthly = monthly_trigger_panel(trades)
    asset_month.to_csv(ARTIFACT_DIR / "asset_month_by_trigger_tf_6bps.csv", index=False)
    monthly.to_csv(ARTIFACT_DIR / "monthly_by_trigger_tf_6bps.csv", index=False)
    stability = trigger_stability_summary(trades)
    stability.to_csv(ARTIFACT_DIR / "trigger_tf_stability_6bps.csv", index=False)
    plot_monthly_lines_svg(monthly)

    variant_frames = []
    variant_month_frames = []
    for cost in COSTS:
        c_trades = recompute_cost(trades, cost)
        v_summary, v_monthly = variant_summary(c_trades, cost)
        variant_frames.append(v_summary)
        variant_month_frames.append(v_monthly)
    variant_df = pd.concat(variant_frames, ignore_index=True)
    variant_month_df = pd.concat(variant_month_frames, ignore_index=True)
    variant_df.to_csv(ARTIFACT_DIR / "variant_summary_by_cost.csv", index=False)
    variant_month_df.to_csv(ARTIFACT_DIR / "variant_monthly_by_cost.csv", index=False)

    lines = [
        "# Rank29 trigger_tf monthly history",
        "",
        f"- Generated at: `{utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        "- Sample: Binance spot 15m, ~5 years, BTC-USD + ETH-USD + SOL-USD",
        "- Strategy lens: Rank29 / breakout_align_ge2 / no_overlap_guard / hold 8 bars",
        "- Trigger split: `short`, `medium`, `long` refers to the breakout timeframe that actually triggered the trade",
        "- Monthly return is grouped by **exit month** and aggregated as the **equal-weight mean of asset-level month returns**. This avoids overstating performance by naively chaining three assets into one artificial compounding stream.",
        "",
        "## Validation logic for a `long_only` filter",
        "",
        "To justify adding a `long_only` trigger filter, we should see **both** of these on the long history:",
        "1. `long` trigger_tf has better total return and better month-to-month stability than `medium` / `short` after using an honest aggregation method.",
        "2. A `long_only` variant remains competitive not just in one recent pocket, but across higher friction assumptions too.",
        "",
        "## 6bps trigger_tf stability",
        "",
    ]
    for _, row in stability.iterrows():
        lines.append(
            f"- {row['trigger_tf']}: trades={int(row['total_trades'])}, mean_asset_total_return={pct(row['mean_asset_total_return'])}, "
            f"positive_asset_ratio={pct(row['positive_asset_ratio'])}, positive_month_ratio={pct(row['positive_month_ratio'])}, "
            f"mean_month_return={pct(row['mean_month_return'])}, worst_month={pct(row['worst_month_return'])}"
        )

    lines.extend(["", "## Variant summary by cost", ""])
    for cost in COSTS:
        sub = variant_df[variant_df['cost_bps_per_side'] == cost]
        lines.append(f"### {int(cost)}bps / side")
        for _, row in sub.iterrows():
            lines.append(
                f"- {row['variant']}: trades={int(row['trades'])}, mean_asset_total_return={pct(row['mean_asset_total_return'])}, "
                f"positive_asset_ratio={pct(row['positive_asset_ratio'])}, positive_month_ratio={pct(row['positive_month_ratio'])}, "
                f"mean_month_return={pct(row['mean_month_return'])}, worst_month={pct(row['worst_month_return'])}"
            )
        lines.append("")

    lines.extend(
        [
            "## Output files",
            "",
            "- `asset_month_by_trigger_tf_6bps.csv`",
            "- `monthly_by_trigger_tf_6bps.csv`",
            "- `trigger_tf_stability_6bps.csv`",
            "- `variant_summary_by_cost.csv`",
            "- `variant_monthly_by_cost.csv`",
            "- `rank29_trigger_tf_monthly_lines.svg`",
            "- `all_trades_6bps.csv`",
            "",
            f"![rank29 trigger monthly lines]({PLOT_PATH.name})",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
