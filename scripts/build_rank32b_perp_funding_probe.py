#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"
R32B_EXT_SCRIPT = ROOT / "scripts" / "build_rank32b_extended_history_probe.py"
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"

PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
PRIMARY_COST = 6.0
DEFAULT_DAYS = 1825
DEFAULT_FUNDING_HOURS = 48
BINANCE_LIMIT = 1000
REQ_TIMEOUT = 30
FUTURES_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
SCENARIO_ORDER = ["spot_raw", "perp_raw", "perp_plus_funding_48h"]
SIDE_ORDER = ["long_short", "long_only", "short_only"]
SCENARIO_LABELS = {
    "spot_raw": "Spot 5y（现货原始）",
    "perp_raw": "Perp 5y（永续原始）",
    "perp_plus_funding_48h": "Perp 5y + 48h funding（永续 + 两天资金费率）",
}
SIDE_LABELS = {
    "long_short": "多空都做",
    "long_only": "只做多",
    "short_only": "只做空",
}
ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base_mod = load_module(BASE_SCRIPT, "rank32_base_mod_for_perp_probe")
ext_mod = load_module(R32B_EXT_SCRIPT, "rank32b_extended_probe_mod")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def load_cached_csv(path: Path, time_cols: list[str] | None = None) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, on_bad_lines="skip")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    for col in time_cols or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce", format="mixed")
    if time_cols:
        present = [col for col in time_cols if col in df.columns]
        if present:
            df = df.dropna(subset=present)
    return df.reset_index(drop=True)


def fetch_futures_klines(symbol: str, days: int, interval: str = "15m") -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        resp = requests.get(
            FUTURES_KLINES_URL,
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": BINANCE_LIMIT,
            },
            timeout=REQ_TIMEOUT,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        current = int(batch[-1][6]) + 1
        if len(batch) < BINANCE_LIMIT:
            break
        time.sleep(0.03)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
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
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    return out.dropna().sort_values("timestamp").reset_index(drop=True)


def fetch_funding(symbol: str, days: int) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[dict] = []
    current = start_ms
    while current < end_ms:
        resp = requests.get(
            FUNDING_URL,
            params={
                "symbol": symbol,
                "startTime": current,
                "endTime": end_ms,
                "limit": BINANCE_LIMIT,
            },
            timeout=REQ_TIMEOUT,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        current = int(batch[-1]["fundingTime"]) + 1
        if len(batch) < BINANCE_LIMIT:
            break
        time.sleep(0.03)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "funding_rate"])
    df = pd.DataFrame(rows)
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["fundingTime"], unit="ms", utc=True),
            "funding_rate": pd.to_numeric(df["fundingRate"], errors="coerce"),
        }
    )
    return out.dropna().drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)


def merge_perp_bars_cache(existing: pd.DataFrame, fresh: pd.DataFrame, *, days: int) -> pd.DataFrame:
    frames = [df for df in (existing, fresh) if not df.empty]
    if not frames:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    merged = pd.concat(frames, ignore_index=True)
    merged["timestamp"] = pd.to_datetime(merged["timestamp"], utc=True)
    merged = merged.dropna(subset=["timestamp"])
    merged = merged.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=max(1, int(days)))
    merged = merged.loc[merged["timestamp"] >= cutoff]
    return merged.reset_index(drop=True)


def load_or_fetch_perp_bars(
    symbol: str,
    days: int,
    refresh: bool = False,
    incremental_refresh_days: int | None = None,
) -> pd.DataFrame:
    cache_dir = ensure_dir(ART_DIR / "perp_cache")
    path = cache_dir / f"{symbol}__{days}d__15m__perp.csv"
    cached = load_cached_csv(path, ["timestamp"]) if path.exists() else pd.DataFrame()
    if not refresh:
        if not cached.empty:
            return cached
        df = fetch_futures_klines(symbol, days=days)
        df.to_csv(path, index=False)
        return df

    if cached.empty:
        df = fetch_futures_klines(symbol, days=days)
    else:
        tail_days = incremental_refresh_days if incremental_refresh_days is not None else min(days, 2)
        tail_days = max(1, min(int(tail_days), int(days)))
        fresh = fetch_futures_klines(symbol, days=tail_days)
        df = merge_perp_bars_cache(cached, fresh, days=days)
    df.to_csv(path, index=False)
    return df


def load_or_fetch_funding(symbol: str, days: int, refresh: bool = False) -> pd.DataFrame:
    cache_dir = ensure_dir(ART_DIR / "perp_cache")
    path = cache_dir / f"{symbol}__{days}d__funding.csv"
    if path.exists() and not refresh:
        return load_cached_csv(path, ["timestamp"])
    df = fetch_funding(symbol, days=days)
    df.to_csv(path, index=False)
    return df


def enrich_trades_with_funding(trades: pd.DataFrame, funding: pd.DataFrame, funding_hours: int) -> pd.DataFrame:
    if trades.empty:
        out = trades.copy()
        out["funding_events_48h"] = []
        out["funding_rate_sum_48h"] = []
        out["funding_net_ret_48h"] = []
        out["net_ret_with_funding_48h"] = []
        return out

    fund = funding.copy().sort_values("timestamp").reset_index(drop=True)
    fund_ts = fund["timestamp"].to_numpy(dtype="datetime64[ns]")
    fund_rates = fund["funding_rate"].to_numpy(dtype=float)
    horizon = np.timedelta64(funding_hours, "h")

    rows = []
    for _, row in trades.iterrows():
        entry_ts = pd.to_datetime(row["entry_ts"], utc=True).to_datetime64()
        cutoff = entry_ts + horizon
        left = np.searchsorted(fund_ts, entry_ts, side="right")
        right = np.searchsorted(fund_ts, cutoff, side="right")
        rates = fund_rates[left:right]
        direction_sign = 1.0 if str(row["direction"]) == "long" else -1.0
        factor = 1.0
        if len(rates):
            factor = float(np.prod(1.0 - direction_sign * rates))
        funding_net_ret = factor - 1.0
        price_net_ret = float(row["net_ret"])
        rows.append(
            {
                **row.to_dict(),
                "funding_events_48h": int(len(rates)),
                "funding_rate_sum_48h": float(rates.sum()) if len(rates) else 0.0,
                "funding_net_ret_48h": float(funding_net_ret),
                "net_ret_with_funding_48h": float((1.0 + price_net_ret) * factor - 1.0),
            }
        )
    return pd.DataFrame(rows)


def summarize_trades(trades: pd.DataFrame, *, scenario: str, side: str, asset: str | None = None, ret_col: str = "net_ret") -> dict[str, object]:
    label_asset = asset if asset is not None else "ALL"
    if trades.empty:
        return {
            "scenario": scenario,
            "side": side,
            "asset": label_asset,
            "trades": 0,
            "total_return": 0.0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "avg_funding_net_ret_48h": np.nan,
            "total_funding_net_ret_48h": 0.0,
            "avg_funding_events_48h": np.nan,
        }
    total_funding = float((1.0 + trades["funding_net_ret_48h"].fillna(0.0)).prod() - 1.0) if "funding_net_ret_48h" in trades.columns else 0.0
    return {
        "scenario": scenario,
        "side": side,
        "asset": label_asset,
        "trades": int(len(trades)),
        "total_return": float((1.0 + trades[ret_col]).prod() - 1.0),
        "win_rate": float((trades[ret_col] > 0).mean()),
        "avg_net_ret": float(trades[ret_col].mean()),
        "median_net_ret": float(trades[ret_col].median()),
        "avg_funding_net_ret_48h": float(trades["funding_net_ret_48h"].mean()) if "funding_net_ret_48h" in trades.columns else np.nan,
        "total_funding_net_ret_48h": total_funding,
        "avg_funding_events_48h": float(trades["funding_events_48h"].mean()) if "funding_events_48h" in trades.columns else np.nan,
    }


def build_side_views(trades: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "long_short": trades.copy(),
        "long_only": trades[trades["direction"] == "long"].copy(),
        "short_only": trades[trades["direction"] == "short"].copy(),
    }


def build_compare_tables(spot_trades: pd.DataFrame, perp_trades: pd.DataFrame, perp_funding_trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    scenario_inputs = {
        "spot_raw": (spot_trades, "net_ret"),
        "perp_raw": (perp_trades, "net_ret"),
        "perp_plus_funding_48h": (perp_funding_trades, "net_ret_with_funding_48h"),
    }
    asset_rows: list[dict[str, object]] = []
    overall_rows: list[dict[str, object]] = []

    for scenario in SCENARIO_ORDER:
        trades_df, ret_col = scenario_inputs[scenario]
        for side in SIDE_ORDER:
            scoped = build_side_views(trades_df)[side]
            side_asset_rows = []
            for asset in ASSETS.keys():
                part = scoped[scoped["asset"] == asset].copy()
                row = summarize_trades(part, scenario=scenario, side=side, asset=asset, ret_col=ret_col)
                side_asset_rows.append(row)
                asset_rows.append(row)
            asset_df = pd.DataFrame(side_asset_rows)
            total_returns = asset_df["total_return"].to_numpy(dtype=float)
            overall_rows.append(
                {
                    "scenario": scenario,
                    "side": side,
                    "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
                    "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
                    "mean_trades": float(asset_df["trades"].mean()) if len(asset_df) else np.nan,
                    "mean_win_rate": float(asset_df["win_rate"].mean()) if len(asset_df) else np.nan,
                    "mean_avg_net_ret": float(asset_df["avg_net_ret"].mean()) if len(asset_df) else np.nan,
                    "mean_funding_net_ret_48h": float(asset_df["avg_funding_net_ret_48h"].mean()) if len(asset_df) else np.nan,
                    "mean_funding_events_48h": float(asset_df["avg_funding_events_48h"].mean()) if len(asset_df) else np.nan,
                }
            )
    asset_summary = pd.DataFrame(asset_rows)
    overall_summary = pd.DataFrame(overall_rows)
    return overall_summary, asset_summary


def inject_section(report_path: Path, html_block: str, marker_id: str) -> None:
    html = report_path.read_text(encoding="utf-8")
    start_marker = f"<!-- {marker_id}:start -->"
    end_marker = f"<!-- {marker_id}:end -->"
    wrapped = f"{start_marker}\n{html_block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace("</body>", wrapped + "\n</body>")
    report_path.write_text(html, encoding="utf-8")


def ordered_overall_view(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["scenario"] = pd.Categorical(work["scenario"], categories=SCENARIO_ORDER, ordered=True)
    work["side"] = pd.Categorical(work["side"], categories=SIDE_ORDER, ordered=True)
    work = work.sort_values(["scenario", "side"]).reset_index(drop=True)
    work["scenario"] = work["scenario"].map(SCENARIO_LABELS)
    work["side"] = work["side"].map(SIDE_LABELS)
    return work


def ordered_asset_view(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work = work[work["scenario"] == "perp_plus_funding_48h"].copy()
    work["side"] = pd.Categorical(work["side"], categories=SIDE_ORDER, ordered=True)
    work["asset"] = pd.Categorical(work["asset"], categories=list(ASSETS.keys()), ordered=True)
    work = work.sort_values(["side", "asset"]).reset_index(drop=True)
    work["side"] = work["side"].map(SIDE_LABELS)
    return work


def build_reader_notes(overall_summary: pd.DataFrame) -> tuple[str, str, list[str]]:
    view = overall_summary.set_index(["scenario", "side"])
    spot_all = view.loc[("spot_raw", "long_short")]
    perp_all = view.loc[("perp_raw", "long_short")]
    perp_funding_all = view.loc[("perp_plus_funding_48h", "long_short")]
    perp_funding_long = view.loc[("perp_plus_funding_48h", "long_only")]
    perp_funding_short = view.loc[("perp_plus_funding_48h", "short_only")]

    headline = (
        f"5 年 Binance 永续 15m 下，Rank 32b 在多空都做时：perp 原始 mean_total_return≈{pct(perp_all['mean_total_return'])}，"
        f"叠加 48h funding 后≈{pct(perp_funding_all['mean_total_return'])}；"
        f"方向拆开看，只做多≈{pct(perp_funding_long['mean_total_return'])}，只做空≈{pct(perp_funding_short['mean_total_return'])}。"
    )
    delta_all = float(perp_funding_all["mean_total_return"] - perp_all["mean_total_return"])
    delta_long = float(perp_funding_long["mean_total_return"] - view.loc[("perp_raw", "long_only")]["mean_total_return"])
    delta_short = float(perp_funding_short["mean_total_return"] - view.loc[("perp_raw", "short_only")]["mean_total_return"])
    notes = [
        f"对照现货 5 年原始结果（多空都做≈{pct(spot_all['mean_total_return'])}），永续原始价格口径本身就和 spot 不完全一样；真正要看的，是 funding 叠加后有没有把 edge 吃掉。",
        f"在这组 48h 资金费率占用假设下，多空都做的 funding 影响约为 {pct(delta_all)}；只做多约 {pct(delta_long)}，只做空约 {pct(delta_short)}。",
        f"如果你关心的是 desk 上真实方向偏好，这页现在可以直接看 long-only / short-only / long+short 三条腿，而不是只看混在一起的 aggregate。",
    ]
    return headline, f"48h funding 假设 = 从进场后开始，累计未来 48 小时内的 funding prints（最多约 6 笔）；价格退出规则仍保持原报告的 next-bar open 入场 + 持有 {base_mod.HOLD_BARS} 根 15m bar。", notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Add 5y perp + 48h funding comparison to Rank 32b report.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--funding-hours", type=int, default=DEFAULT_FUNDING_HOURS)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    days = int(args.days)
    funding_hours = int(args.funding_hours)
    ensure_dir(ART_DIR)

    spot_trades_path = ART_DIR / f"extended_history_{days}d_trades.csv"
    if not spot_trades_path.exists():
        raise FileNotFoundError(f"spot trades not found: {spot_trades_path}")
    spot_trades = load_cached_csv(spot_trades_path, ["event_ts", "entry_ts", "exit_ts"])
    spot_trades["funding_events_48h"] = 0
    spot_trades["funding_rate_sum_48h"] = 0.0
    spot_trades["funding_net_ret_48h"] = 0.0
    spot_trades["net_ret_with_funding_48h"] = spot_trades["net_ret"]

    perp_trade_rows: list[pd.DataFrame] = []
    perp_funding_rows: list[pd.DataFrame] = []
    asset_meta_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        bars = load_or_fetch_perp_bars(symbol, days=days, refresh=bool(args.refresh))
        funding = load_or_fetch_funding(symbol, days=days, refresh=bool(args.refresh))
        frame = ext_mod.build_rank32b_frame_from_bars(asset, bars)
        trades, no_trade_ratio, eligible_bars = base_mod.build_trades(frame, asset, PRIMARY_VARIANT, PRIMARY_COST)
        trades = trades.copy()
        trades["sample_kind"] = "perp_raw"
        trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], utc=True)
        trades["exit_ts"] = pd.to_datetime(trades["exit_ts"], utc=True)
        trades["event_ts"] = pd.to_datetime(trades["event_ts"], utc=True)
        enriched = enrich_trades_with_funding(trades, funding, funding_hours=funding_hours)
        perp_trade_rows.append(trades)
        perp_funding_rows.append(enriched)
        asset_meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "perp_bars": int(len(bars)),
                "funding_rows": int(len(funding)),
                "perp_trades": int(len(trades)),
                "eligible_structure_bars": int(eligible_bars),
                "no_trade_ratio": float(no_trade_ratio),
                "first_bar_utc": bars["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(bars) else "-",
                "last_bar_utc": bars["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(bars) else "-",
            }
        )

    perp_trades = pd.concat(perp_trade_rows, ignore_index=True) if perp_trade_rows else pd.DataFrame()
    perp_funding_trades = pd.concat(perp_funding_rows, ignore_index=True) if perp_funding_rows else pd.DataFrame()

    overall_summary, asset_summary = build_compare_tables(spot_trades, perp_trades, perp_funding_trades)
    overall_view = ordered_overall_view(overall_summary)
    asset_view = ordered_asset_view(asset_summary)
    headline, assumption_note, notes = build_reader_notes(overall_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    perp_trades_out = perp_trades.copy()
    perp_funding_out = perp_funding_trades.copy()
    for col in ["event_ts", "entry_ts", "exit_ts"]:
        if col in perp_trades_out.columns:
            perp_trades_out[col] = pd.to_datetime(perp_trades_out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        if col in perp_funding_out.columns:
            perp_funding_out[col] = pd.to_datetime(perp_funding_out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    overall_summary.to_csv(ART_DIR / f"perp_funding_compare_{days}d_overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / f"perp_funding_compare_{days}d_asset_summary.csv", index=False)
    pd.DataFrame(asset_meta_rows).to_csv(ART_DIR / f"perp_funding_compare_{days}d_meta.csv", index=False)
    perp_trades_out.to_csv(ART_DIR / f"perp_{days}d_trades_raw.csv", index=False)
    perp_funding_out.to_csv(ART_DIR / f"perp_{days}d_trades_with_funding_{funding_hours}h.csv", index=False)

    marker_id = f"rank32b-perp-funding-{days}d-{funding_hours}h"
    block = f"""
  <div class='card'>
    <h2>perp vs spot + funding carry 对比（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 样本：Binance USDT-M perpetual 15m + fundingRate 公共接口 ｜ 窗口：最近 {days} 天 ｜ 角色：reader-facing 补充对比。</p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(assumption_note)}</p>
    <h3>5y 总览：spot / perp / perp+funding</h3>
    {render_table(overall_view[["scenario","side","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate","mean_funding_net_ret_48h","mean_funding_events_48h"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_funding_net_ret_48h"}, digits_cols={"mean_trades":1, "mean_funding_events_48h":1})}
    <h3>Perp + 48h funding：分资产 / 分方向</h3>
    {render_table(asset_view[["side","asset","trades","total_return","win_rate","avg_net_ret","avg_funding_net_ret_48h","total_funding_net_ret_48h","avg_funding_events_48h"]], percent_cols={"total_return","win_rate","avg_net_ret","avg_funding_net_ret_48h","total_funding_net_ret_48h"}, digits_cols={"trades":0, "avg_funding_events_48h":1})}
    <h3>reader-facing 结论</h3>
    <ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul>
    <p class='muted'>artifact：<code>reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_funding_compare_{days}d_overall_summary.csv</code>、<code>perp_funding_compare_{days}d_asset_summary.csv</code>、<code>perp_{days}d_trades_with_funding_{funding_hours}h.csv</code></p>
  </div>"""

    for path in [SITE_DIR / "report.html", READING_PATH]:
        inject_section(path, block, marker_id=marker_id)

    print(
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "days": days,
            "funding_hours": funding_hours,
            "perp_trades": int(len(perp_trades)),
            "perp_funding_trades": int(len(perp_funding_trades)),
            "overall_rows": int(len(overall_summary)),
            "asset_rows": int(len(asset_summary)),
        }
    )


if __name__ == "__main__":
    main()
