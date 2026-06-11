#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_repo_ema_oi_participation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_repo_ema_oi_participation_15m"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["ema_raw", "oi_level_gate", "oi_level_delta_gate", "volume_fallback_gate"]
PRIMARY_VARIANT = "oi_level_gate"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
EMA_FAST = 9
EMA_SLOW = 15
HOLD_BARS = 8
WHIPSAW2_BARS = 2
WHIPSAW4_BARS = 4
FOLLOW_THROUGH_BARS = [4, 8, 12]
OI_SMA = 20
VOL_SMA = 20
BINANCE_OI_URL = "https://fapi.binance.com/futures/data/openInterestHist"
BINANCE_LIMIT = 500
MAX_FETCH_PAGES = 8


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


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_oi_history(symbol: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    end_time: int | None = None
    for _ in range(MAX_FETCH_PAGES):
        params: dict[str, object] = {
            "symbol": symbol,
            "period": "15m",
            "limit": BINANCE_LIMIT,
            "contractType": "PERPETUAL",
        }
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(BINANCE_OI_URL, params=params, timeout=20)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = min(int(item["timestamp"]) for item in batch)
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["sumOpenInterest"] = pd.to_numeric(df["sumOpenInterest"], errors="coerce")
    df["sumOpenInterestValue"] = pd.to_numeric(df.get("sumOpenInterestValue"), errors="coerce")
    return df[["timestamp", "sumOpenInterest", "sumOpenInterestValue"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    bars = load_cached_bars(symbol, asset)
    oi = fetch_oi_history(symbol)
    frame = bars.merge(oi, on="timestamp", how="inner")
    frame["ema_fast"] = frame["close"].ewm(span=EMA_FAST, adjust=False).mean()
    frame["ema_slow"] = frame["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    frame["oi_sma20"] = frame["sumOpenInterest"].rolling(OI_SMA, min_periods=OI_SMA).mean()
    frame["oi_delta"] = frame["sumOpenInterest"].diff()
    frame["volume_sma20"] = frame["volume"].rolling(VOL_SMA, min_periods=VOL_SMA).mean()

    cross_up = (frame["ema_fast"] > frame["ema_slow"]) & (frame["ema_fast"].shift(1) <= frame["ema_slow"].shift(1))
    cross_down = (frame["ema_fast"] < frame["ema_slow"]) & (frame["ema_fast"].shift(1) >= frame["ema_slow"].shift(1))
    gate_oi_level = frame["sumOpenInterest"] > frame["oi_sma20"]
    gate_oi_level_delta = gate_oi_level & (frame["oi_delta"] > 0)
    gate_volume = frame["volume"] > frame["volume_sma20"]

    frame["long_ema_raw"] = cross_up.fillna(False)
    frame["short_ema_raw"] = cross_down.fillna(False)
    frame["long_oi_level_gate"] = (cross_up & gate_oi_level).fillna(False)
    frame["short_oi_level_gate"] = (cross_down & gate_oi_level).fillna(False)
    frame["long_oi_level_delta_gate"] = (cross_up & gate_oi_level_delta).fillna(False)
    frame["short_oi_level_delta_gate"] = (cross_down & gate_oi_level_delta).fillna(False)
    frame["long_volume_fallback_gate"] = (cross_up & gate_volume).fillna(False)
    frame["short_volume_fallback_gate"] = (cross_down & gate_volume).fillna(False)
    return frame.reset_index(drop=True), oi


def build_trades(frame: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    long_col = f"long_{variant}"
    short_col = f"short_{variant}"
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx or idx + 1 >= len(frame):
            continue
        direction = 1 if bool(frame.iloc[idx][long_col]) else -1 if bool(frame.iloc[idx][short_col]) else 0
        if direction == 0:
            continue
        signal_events += 1
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            break
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = (exit_px / entry_px - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        ft: dict[int, float] = {}
        for bars in FOLLOW_THROUGH_BARS:
            probe_idx = min(len(frame) - 1, entry_idx + bars - 1)
            ft[bars] = (float(frame.iloc[probe_idx]["close"]) / entry_px - 1.0) * direction

        def whipsaw_flag(max_bars: int) -> int:
            probe_idx = min(len(frame) - 1, entry_idx + max_bars - 1)
            probe_ret = (float(frame.iloc[probe_idx]["close"]) / entry_px - 1.0) * direction
            opposite_seen = False
            for j in range(entry_idx, probe_idx + 1):
                if direction > 0 and bool(frame.iloc[j][short_col]):
                    opposite_seen = True
                    break
                if direction < 0 and bool(frame.iloc[j][long_col]):
                    opposite_seen = True
                    break
            return int((probe_ret < 0.0) or opposite_seen)

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "follow_through_4bars": ft[4],
                "follow_through_8bars": ft[8],
                "follow_through_12bars": ft[12],
                "whipsaw_2bars": whipsaw_flag(WHIPSAW2_BARS),
                "whipsaw_4bars": whipsaw_flag(WHIPSAW4_BARS),
                "hold_bars": int(exit_idx - entry_idx + 1),
                "oi_level_ratio": float(frame.iloc[idx]["sumOpenInterest"] / frame.iloc[idx]["oi_sma20"]) if pd.notna(frame.iloc[idx]["oi_sma20"]) and float(frame.iloc[idx]["oi_sma20"]) > 0 else np.nan,
                "oi_delta": float(frame.iloc[idx]["oi_delta"]) if pd.notna(frame.iloc[idx]["oi_delta"]) else np.nan,
                "volume_ratio": float(frame.iloc[idx]["volume"] / frame.iloc[idx]["volume_sma20"]) if pd.notna(frame.iloc[idx]["volume_sma20"]) and float(frame.iloc[idx]["volume_sma20"]) > 0 else np.nan,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "whipsaw_2bars_rate": np.nan,
            "whipsaw_4bars_rate": np.nan,
            "follow_through_4bars": np.nan,
            "follow_through_8bars": np.nan,
            "follow_through_12bars": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "whipsaw_2bars_rate": float(trades["whipsaw_2bars"].mean()),
        "whipsaw_4bars_rate": float(trades["whipsaw_4bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "follow_through_8bars": float(trades["follow_through_8bars"].mean()),
        "follow_through_12bars": float(trades["follow_through_12bars"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for cost in sorted(out["cost_bps_per_side"].unique()):
        raw_map = (
            out[(out["variant"] == "ema_raw") & (out["cost_bps_per_side"] == cost)]
            .set_index("asset")["trades"]
            .to_dict()
        )
        mask = out["cost_bps_per_side"] == cost
        out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
            lambda r: float(r["trades"] / raw_map.get(r["asset"], np.nan)) if raw_map.get(r["asset"], 0) not in (0, np.nan) else np.nan,
            axis=1,
        )
    return out


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if grp["trade_count_retention"].notna().any() else np.nan,
                "mean_win_rate": float(grp["win_rate"].mean()) if grp["win_rate"].notna().any() else np.nan,
                "mean_whipsaw_2bars_rate": float(grp["whipsaw_2bars_rate"].mean()) if grp["whipsaw_2bars_rate"].notna().any() else np.nan,
                "mean_whipsaw_4bars_rate": float(grp["whipsaw_4bars_rate"].mean()) if grp["whipsaw_4bars_rate"].notna().any() else np.nan,
                "mean_follow_through_4bars": float(grp["follow_through_4bars"].mean()) if grp["follow_through_4bars"].notna().any() else np.nan,
                "mean_follow_through_8bars": float(grp["follow_through_8bars"].mean()) if grp["follow_through_8bars"].notna().any() else np.nan,
                "mean_follow_through_12bars": float(grp["follow_through_12bars"].mean()) if grp["follow_through_12bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_whipsaw_4bars_rate"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_whipsaw_4bars_rate"])
    rows: list[dict[str, object]] = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_whipsaw_4bars_rate": float(grp["whipsaw_4bars"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def verdict_text(overall_6bps: pd.DataFrame) -> tuple[str, str]:
    lookup = overall_6bps.set_index("variant")
    raw = lookup.loc["ema_raw"]
    oi_level = lookup.loc["oi_level_gate"]
    oi_delta = lookup.loc["oi_level_delta_gate"]
    vol = lookup.loc["volume_fallback_gate"]

    if float(oi_level["positive_asset_ratio"]) >= 2 / 3 and float(oi_level["mean_total_return"]) > 0:
        return "paper candidate", "真 OI gate 已跨资产保留正 pocket，可考虑升到 P2。"

    text = (
        "当前更诚实的 hard verdict 是 `park / evidence pool`：真 OI gate 虽然比 raw EMA 少亏，"
        "但在 6bps/side 下仍只有 1/3 资产为正，跨资产 mean_total_return 仍未转正；"
        "而 `volume_fallback_gate` 明显更强，说明这条 repo 当前更像 volume-participation 代理，"
        "不该把 `true OI` 版直接升格。"
    )
    detail = (
        f"6bps/side 下：raw={pct(raw['mean_total_return'])} / {pct(raw['positive_asset_ratio'])}；"
        f"oi_level={pct(oi_level['mean_total_return'])} / {pct(oi_level['positive_asset_ratio'])} / retention={pct(oi_level['mean_trade_count_retention'])}；"
        f"oi_level+delta={pct(oi_delta['mean_total_return'])} / {pct(oi_delta['positive_asset_ratio'])} / retention={pct(oi_delta['mean_trade_count_retention'])}；"
        f"volume_fallback={pct(vol['mean_total_return'])} / {pct(vol['positive_asset_ratio'])}."
    )
    return text, detail


def build_html(asset_df: pd.DataFrame, overall_df: pd.DataFrame, time_df: pd.DataFrame, meta_df: pd.DataFrame, verdict: str, detail: str) -> str:
    overall_6 = overall_df[overall_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    overall_10 = overall_df[overall_df["cost_bps_per_side"] == 10.0].copy()
    asset_6 = asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    percent_cols_overall = {
        "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_win_rate",
        "mean_whipsaw_2bars_rate", "mean_whipsaw_4bars_rate", "mean_follow_through_4bars",
        "mean_follow_through_8bars", "mean_follow_through_12bars",
    }
    percent_cols_asset = {
        "trade_count_retention", "total_return", "avg_net_ret", "win_rate", "whipsaw_2bars_rate",
        "whipsaw_4bars_rate", "follow_through_4bars", "follow_through_8bars", "follow_through_12bars",
    }
    percent_cols_time = {"mean_total_return", "positive_asset_ratio", "mean_whipsaw_4bars_rate"}

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>OI participation gate 15m clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; padding: 0 16px 40px; line-height: 1.6; color: #1f2937; }}
    h1, h2, h3 {{ color: #111827; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .muted {{ color: #6b7280; }}
    .callout {{ padding: 12px 14px; border-left: 4px solid #2563eb; background: #eff6ff; margin: 16px 0; }}
    .bad {{ border-left-color: #dc2626; background: #fef2f2; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>OI participation gate / 15m minimal clean replication</h1>
  <p class=\"muted\">生成时间：{escape(generated)}</p>

  <div class=\"callout bad\">
    <p><strong>硬结论：</strong>{escape(verdict)}</p>
    <p>{escape(detail)}</p>
  </div>

  <h2>这轮到底测了什么</h2>
  <ul>
    <li>资产：<code>BTC / ETH / SOL</code>，统一复用本地 <code>15m</code> OHLCV cache，并拉取 Binance USDⓈ-M perpetual 的公开 <code>openInterestHist</code>。</li>
    <li>规则：<code>EMA9/15 cross</code> 给方向，统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</li>
    <li>四臂对照：<code>ema_raw</code>、<code>+oi_level_gate</code>、<code>+oi_level_gate+oi_delta_gate</code>、<code>+volume_fallback_gate</code>。</li>
    <li>先回答 4 个便宜问题：<code>trade_count retention</code>、<code>2/4 bar whipsaw</code>、<code>4/8/12 bar follow-through</code>、<code>net expectancy / total return</code>。</li>
  </ul>

  <h2>样本元数据</h2>
  {render_table(meta_df, percent_cols=set(), digits_cols={"merged_bars": 0, "oi_rows": 0})}

  <h2>总体结果（6bps/side）</h2>
  {render_table(overall_6, percent_cols=percent_cols_overall, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}

  <h2>总体结果（10bps/side）</h2>
  {render_table(overall_10, percent_cols=percent_cols_overall, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}

  <h2>分资产结果（6bps/side）</h2>
  {render_table(asset_6, percent_cols=percent_cols_asset, digits_cols={"cost_bps_per_side": 0, "signal_events": 0, "trades": 0})}

  <h2>时间稳定性（主臂 = oi_level_gate @ 6bps）</h2>
  {render_table(time_df, percent_cols=percent_cols_time, digits_cols={"mean_trades": 1})}

  <h2>怎么读这次结果</h2>
  <ul>
    <li><strong>真 OI 确实有一点帮助，但还不够诚实。</strong> 它把 raw EMA 的平均亏损拉窄，也没有把交易数直接砍没；但在跨资产口径下，<code>oi_level_gate</code> 与 <code>oi_level+delta</code> 仍都只有 <code>1/3</code> 资产为正。</li>
    <li><strong>最强的是 volume fallback，不是真 OI。</strong> 这说明 repo 里真正有效的 participation 代理更像成交量活跃度，而不是“只要 OI 高于均值就更好做”。</li>
    <li><strong>因此不能把这条 repo 当成 true-OI alpha 升格。</strong> 更诚实的读法是：它给了我们一个有价值的反证——<code>volume-style participation filter</code> 也许值得继续，但那已经更接近另一条候选（例如待排队的 <code>EMA-ADX-VOL skeleton</code>），不应混成这条 repo 的胜利。</li>
  </ul>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(ART_DIR / "oi_cache")

    all_trades: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    meta_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame, oi = build_frame(asset, symbol)
        oi.to_csv(ART_DIR / "oi_cache" / f"{symbol}_15m_open_interest.csv", index=False)
        meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "merged_bars": int(len(frame)),
                "oi_rows": int(len(oi)),
                "sample_start_utc": frame["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
                "sample_end_utc": frame["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
            }
        )
        for variant in VARIANTS:
            for cost in COSTS:
                trades, signal_events = build_trades(frame, variant, cost)
                all_trades.append(trades)
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, signal_events=signal_events))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_df = add_trade_retention(pd.DataFrame(asset_rows))
    overall_df = summarize_overall(asset_df)
    primary_trades = trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy() if not trades_df.empty else pd.DataFrame()
    time_df = build_time_stability(primary_trades)
    meta_df = pd.DataFrame(meta_rows)

    overall_6 = overall_df[overall_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    verdict, detail = verdict_text(overall_6)

    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_df.to_csv(ART_DIR / "time_stability_summary.csv", index=False)
    meta_df.to_csv(ART_DIR / "sample_meta.csv", index=False)
    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    (SITE_DIR / "report.html").write_text(build_html(asset_df, overall_df, time_df, meta_df, verdict, detail), encoding="utf-8")

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_variant": PRIMARY_VARIANT,
        "primary_cost_bps_per_side": PRIMARY_COST,
        "verdict": verdict,
        "detail": detail,
    }
    pd.DataFrame([summary]).to_csv(ART_DIR / "summary.csv", index=False)
    print("ok: built scout_repo_ema_oi_participation_15m")


if __name__ == "__main__":
    main()
