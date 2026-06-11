#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_repo_ema_adx_vol_skeleton_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_repo_ema_adx_vol_skeleton_15m"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["ema_stack_only", "adx_di_gate", "volume_gate", "range_filter_gate", "full_stack"]
PRIMARY_VARIANT = "full_stack"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
EMA_LENGTHS = [8, 13, 21, 34, 55]
ADX_LEN = 21
ADX_THRESHOLD = 20.0
VOL_FAST_LEN = 20
VOL_FAST_MULT = 3.2
VOL_SLOW_LEN = 22
VOL_SLOW_MULT = 1.9
RF_PERIOD = 15
RF_MULT = 2.6
ATR_LEN = 14
HOLD_BARS = 8
FALSE_START_BARS = 4
FOLLOW_THROUGH_BARS = [4, 8, 12]


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


def wilder_rma(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(alpha=1.0 / length, adjust=False).mean()


def range_filter(close: pd.Series, period: int, mult: float) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    wper = period * 2 - 1
    avrng = close.diff().abs().ewm(span=period, adjust=False).mean()
    smoothrng = avrng.ewm(span=wper, adjust=False).mean() * mult

    filt = close.copy().astype(float)
    upward = pd.Series(index=close.index, dtype=float)
    downward = pd.Series(index=close.index, dtype=float)

    filt.iloc[0] = float(close.iloc[0])
    upward.iloc[0] = 0.0
    downward.iloc[0] = 0.0
    for i in range(1, len(close)):
        prev_filt = float(filt.iloc[i - 1])
        src = float(close.iloc[i])
        rng = float(smoothrng.iloc[i]) if pd.notna(smoothrng.iloc[i]) else 0.0
        if src > prev_filt:
            filt.iloc[i] = prev_filt if (src - rng) < prev_filt else (src - rng)
        else:
            filt.iloc[i] = prev_filt if (src + rng) > prev_filt else (src + rng)

        if filt.iloc[i] > prev_filt:
            upward.iloc[i] = float(upward.iloc[i - 1]) + 1.0
            downward.iloc[i] = 0.0
        elif filt.iloc[i] < prev_filt:
            downward.iloc[i] = float(downward.iloc[i - 1]) + 1.0
            upward.iloc[i] = 0.0
        else:
            upward.iloc[i] = float(upward.iloc[i - 1])
            downward.iloc[i] = float(downward.iloc[i - 1])

    hband = filt + smoothrng
    lband = filt - smoothrng
    return smoothrng, hband, lband, upward, downward


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    frame = load_cached_bars(symbol, asset)
    close = frame["close"]
    high = frame["high"]
    low = frame["low"]
    prev_close = close.shift(1)

    for length in EMA_LENGTHS:
        frame[f"ema_{length}"] = close.ewm(span=length, adjust=False).mean()

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=frame.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=frame.index)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = wilder_rma(tr, ATR_LEN)
    truerange = wilder_rma(tr, ADX_LEN)
    plus = 100.0 * wilder_rma(plus_dm, ADX_LEN) / truerange.replace(0, np.nan)
    minus = 100.0 * wilder_rma(minus_dm, ADX_LEN) / truerange.replace(0, np.nan)
    dx = 100.0 * (plus - minus).abs() / (plus + minus).replace(0, np.nan)
    adx = wilder_rma(dx.fillna(0.0), ADX_LEN)

    frame["atr14"] = atr
    frame["di_plus"] = plus.fillna(0.0)
    frame["di_minus"] = minus.fillna(0.0)
    frame["adx"] = adx.fillna(0.0)

    frame["vol_sma20"] = frame["volume"].rolling(VOL_FAST_LEN, min_periods=VOL_FAST_LEN).mean()
    frame["vol_sma22"] = frame["volume"].rolling(VOL_SLOW_LEN, min_periods=VOL_SLOW_LEN).mean()
    smoothrng, hband, lband, upward, downward = range_filter(close, RF_PERIOD, RF_MULT)
    frame["rf_smoothrng"] = smoothrng
    frame["rf_hband"] = hband
    frame["rf_lband"] = lband
    frame["rf_upward"] = upward
    frame["rf_downward"] = downward

    ema_cols = [frame[f"ema_{length}"] for length in EMA_LENGTHS]
    long_ema = pd.concat([(close > s) for s in ema_cols], axis=1).all(axis=1)
    short_ema = pd.concat([(close < s) for s in ema_cols], axis=1).all(axis=1)
    long_adx = (frame["di_plus"] > frame["di_minus"]) & (frame["adx"] > ADX_THRESHOLD)
    short_adx = (frame["di_plus"] < frame["di_minus"]) & (frame["adx"] > ADX_THRESHOLD)
    long_volume = ((frame["volume"] > frame["vol_sma20"] * VOL_FAST_MULT) | (frame["volume"] > frame["vol_sma22"] * VOL_SLOW_MULT)).fillna(False)
    short_volume = long_volume.copy()
    long_rf = ((high > frame["rf_hband"]) & (frame["rf_upward"] > 0)).fillna(False)
    short_rf = ((low < frame["rf_lband"]) & (frame["rf_downward"] > 0)).fillna(False)

    frame["long_ema_stack_only"] = long_ema.fillna(False)
    frame["short_ema_stack_only"] = short_ema.fillna(False)
    frame["long_adx_di_gate"] = (long_ema & long_adx).fillna(False)
    frame["short_adx_di_gate"] = (short_ema & short_adx).fillna(False)
    frame["long_volume_gate"] = (long_ema & long_volume).fillna(False)
    frame["short_volume_gate"] = (short_ema & short_volume).fillna(False)
    frame["long_range_filter_gate"] = (long_ema & long_rf).fillna(False)
    frame["short_range_filter_gate"] = (short_ema & short_rf).fillna(False)
    frame["long_full_stack"] = (long_ema & long_adx & long_volume & long_rf).fillna(False)
    frame["short_full_stack"] = (short_ema & short_adx & short_volume & short_rf).fillna(False)

    return frame.reset_index(drop=True)


def build_trades(frame: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    long_col = f"long_{variant}"
    short_col = f"short_{variant}"
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    timestamps = frame["timestamp"].to_numpy()
    opens = frame["open"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    atr = frame["atr14"].to_numpy(dtype=float)
    adx = frame["adx"].to_numpy(dtype=float)
    di_plus = frame["di_plus"].to_numpy(dtype=float)
    di_minus = frame["di_minus"].to_numpy(dtype=float)
    volume = frame["volume"].to_numpy(dtype=float)
    vol_sma20 = frame["vol_sma20"].to_numpy(dtype=float)
    vol_sma22 = frame["vol_sma22"].to_numpy(dtype=float)
    long_sig = frame[long_col].to_numpy(dtype=bool)
    short_sig = frame[short_col].to_numpy(dtype=bool)
    asset = str(frame.iloc[0]["asset"])

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx or idx + 1 >= len(frame):
            continue
        direction = 1 if long_sig[idx] else -1 if short_sig[idx] else 0
        if direction == 0:
            continue
        signal_events += 1
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            break
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = opens[entry_idx]
        exit_px = closes[exit_idx]
        gross_ret = (exit_px / entry_px - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        ft: dict[int, float] = {}
        for bars in FOLLOW_THROUGH_BARS:
            probe_idx = min(len(frame) - 1, entry_idx + bars - 1)
            ft[bars] = (closes[probe_idx] / entry_px - 1.0) * direction

        probe_idx = min(len(frame) - 1, entry_idx + FALSE_START_BARS - 1)
        if direction > 0:
            adverse_excursion = float(np.min(lows[entry_idx:probe_idx + 1] / entry_px - 1.0))
            opposite_seen = bool(np.any(short_sig[entry_idx:probe_idx + 1]))
        else:
            adverse_excursion = float(np.min(-(highs[entry_idx:probe_idx + 1] / entry_px - 1.0)))
            opposite_seen = bool(np.any(long_sig[entry_idx:probe_idx + 1]))
        atr_ratio = atr[entry_idx] / entry_px if entry_px > 0 and not np.isnan(atr[entry_idx]) else np.nan
        adverse_flag = (adverse_excursion < -(0.5 * atr_ratio)) if not np.isnan(atr_ratio) else False
        false_start = int(adverse_flag or opposite_seen)

        vol_ratio_20 = volume[idx] / vol_sma20[idx] if not np.isnan(vol_sma20[idx]) and vol_sma20[idx] > 0 else np.nan
        vol_ratio_22 = volume[idx] / vol_sma22[idx] if not np.isnan(vol_sma22[idx]) and vol_sma22[idx] > 0 else np.nan

        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.Timestamp(timestamps[idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.Timestamp(timestamps[entry_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.Timestamp(timestamps[exit_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "follow_through_4bars": ft[4],
                "follow_through_8bars": ft[8],
                "follow_through_12bars": ft[12],
                "false_start_4bars": false_start,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "adx": adx[idx],
                "di_spread": di_plus[idx] - di_minus[idx],
                "volume_ratio_20": vol_ratio_20,
                "volume_ratio_22": vol_ratio_22,
                "atr_ratio": float(atr_ratio) if not np.isnan(atr_ratio) else np.nan,
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
            "false_start_4bars_rate": np.nan,
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
        "false_start_4bars_rate": float(trades["false_start_4bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "follow_through_8bars": float(trades["follow_through_8bars"].mean()),
        "follow_through_12bars": float(trades["follow_through_12bars"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for cost in sorted(out["cost_bps_per_side"].unique()):
        raw_map = (
            out[(out["variant"] == "ema_stack_only") & (out["cost_bps_per_side"] == cost)]
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
                "mean_false_start_4bars_rate": float(grp["false_start_4bars_rate"].mean()) if grp["false_start_4bars_rate"].notna().any() else np.nan,
                "mean_follow_through_4bars": float(grp["follow_through_4bars"].mean()) if grp["follow_through_4bars"].notna().any() else np.nan,
                "mean_follow_through_8bars": float(grp["follow_through_8bars"].mean()) if grp["follow_through_8bars"].notna().any() else np.nan,
                "mean_follow_through_12bars": float(grp["follow_through_12bars"].mean()) if grp["follow_through_12bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_start_4bars_rate"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].astype("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_start_4bars_rate"])
    rows: list[dict[str, object]] = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_false_start_4bars_rate": float(grp["false_start_4bars"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def verdict_text(overall_6bps: pd.DataFrame) -> tuple[str, str]:
    lookup = overall_6bps.set_index("variant")
    base = lookup.loc["ema_stack_only"]
    adx = lookup.loc["adx_di_gate"]
    vol = lookup.loc["volume_gate"]
    rf = lookup.loc["range_filter_gate"]
    full = lookup.loc["full_stack"]

    if float(full["positive_asset_ratio"]) >= 2 / 3 and float(full["mean_total_return"]) > 0 and float(full["mean_trade_count_retention"]) >= 0.25:
        return "paper candidate", "full stack 在 6bps/side 下仍保留跨资产正 pocket，且 trade retention 未塌到失真，可考虑升到 P2。"

    text = (
        "当前更诚实的 hard verdict 是 `park / evidence pool`：`EMA-ADX-VOL skeleton` 虽然比 `EMA_stack_only` 更少亏、"
        "false-start 也更低，但主要改善来自大幅砍样本；在 6bps/side 下 full stack 仍未形成可靠跨资产正 pocket，"
        "因此它更像 execution veto 模板，不该直接升格成新的 raw-alpha 候选。"
    )
    detail = (
        f"6bps/side 下：ema={pct(base['mean_total_return'])} / {pct(base['positive_asset_ratio'])} / trades={num(base['mean_trades'],1)}；"
        f"+adx={pct(adx['mean_total_return'])} / {pct(adx['positive_asset_ratio'])} / retention={pct(adx['mean_trade_count_retention'])}；"
        f"+volume={pct(vol['mean_total_return'])} / {pct(vol['positive_asset_ratio'])} / retention={pct(vol['mean_trade_count_retention'])}；"
        f"+range={pct(rf['mean_total_return'])} / {pct(rf['positive_asset_ratio'])} / retention={pct(rf['mean_trade_count_retention'])}；"
        f"full={pct(full['mean_total_return'])} / {pct(full['positive_asset_ratio'])} / retention={pct(full['mean_trade_count_retention'])}."
    )
    return text, detail


def build_html(asset_df: pd.DataFrame, overall_df: pd.DataFrame, time_df: pd.DataFrame, meta_df: pd.DataFrame, verdict: str, detail: str) -> str:
    overall_6 = overall_df[overall_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    overall_10 = overall_df[overall_df["cost_bps_per_side"] == 10.0].copy()
    asset_6 = asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    percent_cols_overall = {
        "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_win_rate",
        "mean_false_start_4bars_rate", "mean_follow_through_4bars", "mean_follow_through_8bars", "mean_follow_through_12bars",
    }
    percent_cols_asset = {
        "trade_count_retention", "total_return", "avg_net_ret", "win_rate", "false_start_4bars_rate",
        "follow_through_4bars", "follow_through_8bars", "follow_through_12bars",
    }
    percent_cols_time = {"mean_total_return", "positive_asset_ratio", "mean_false_start_4bars_rate"}
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <title>EMA-ADX-VOL skeleton 15m clean replication</title>
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
  <h1>EMA-ADX-VOL skeleton / 15m minimal clean replication</h1>
  <p class="muted">生成时间：{escape(generated)}</p>

  <div class="callout bad">
    <p><strong>硬结论：</strong>{escape(verdict)}</p>
    <p>{escape(detail)}</p>
  </div>

  <h2>这轮到底测了什么</h2>
  <ul>
    <li>资产：<code>BTC / ETH / SOL</code>，统一复用本地 <code>120d 15m</code> OHLCV cache。</li>
    <li>规则冻结：统一 <code>next-bar open + no-overlap + hold 8 bars</code>，不沿用原仓库 TP/SL。</li>
    <li>五臂对照：<code>EMA_stack_only</code>、<code>+ADX_DI</code>、<code>+volume_gate</code>、<code>+range_filter</code>、<code>full_stack</code>。</li>
    <li>先回答四个便宜问题：<code>trade_count retention</code>、<code>false_start_4bars</code>、<code>4/8/12 bar follow-through</code>、<code>post-cost total return</code>。</li>
  </ul>

  <h2>样本元数据</h2>
  {render_table(meta_df, percent_cols=set(), digits_cols={"bars": 0})}

  <h2>总体结果（6bps/side）</h2>
  {render_table(overall_6, percent_cols=percent_cols_overall, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}

  <h2>总体结果（10bps/side）</h2>
  {render_table(overall_10, percent_cols=percent_cols_overall, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}

  <h2>分资产结果（6bps/side）</h2>
  {render_table(asset_6, percent_cols=percent_cols_asset, digits_cols={"cost_bps_per_side": 0, "signal_events": 0, "trades": 0})}

  <h2>时间稳定性（主臂 = full_stack @ 6bps）</h2>
  {render_table(time_df, percent_cols=percent_cols_time, digits_cols={"mean_trades": 1})}

  <h2>怎么读这次结果</h2>
  <ul>
    <li><strong>它更像 veto stack，不像新 alpha。</strong> 如果 full stack 的改善主要来自 trade-count 大幅缩小，那它适合做执行过滤层，不适合直接接管 raw-alpha 席位。</li>
    <li><strong>这轮故意不沿用原仓库 TP/SL。</strong> 我们只回答 entry skeleton 有没有最小诚实性，不把工程止盈止损包装成 entry edge。</li>
    <li><strong>若要继续复用它，应该拆层拿。</strong> ADX / volume / range 哪一层最值钱，才是后续能反哺 EMA / breakout / Fib confirmation 的东西；full stack 本身并不自动等于 deployable candidate。</li>
  </ul>
</body>
</html>'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    all_trades: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    meta_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bars": int(len(frame)),
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
    print("ok: built scout_repo_ema_adx_vol_skeleton_15m")


if __name__ == "__main__":
    main()
