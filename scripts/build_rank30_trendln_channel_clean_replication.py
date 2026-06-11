#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank30_trendln_channel_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank30_trendln_channel_15m'
READING_REPORT = ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'report.html'
TODO_PATH = ROOT / 'docs' / 'TODO.md'

ASSETS = {
    'BTC-USD': 'BTCUSDT',
    'ETH-USD': 'ETHUSDT',
    'SOL-USD': 'SOLUSDT',
}
LOOKBACK_BARS = 96
PIVOT_LEFT = 3
PIVOT_RIGHT = 1
MIN_POINTS = 3
WIDTH_STABILITY_LOOKBACK = 12
WIDTH_STABILITY_MAX_CV = 0.35
SLOPE_REL_TOL = 0.35
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
FAILURE_LOOKAHEAD = 4
VARIANTS = ['raw_corridor_breach', 'breach_plus_reclaim_hold']
PRIMARY_VARIANT = 'breach_plus_reclaim_hold'
PRIMARY_COST = 6.0


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
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


def confirmed_pivot_high(high: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(high)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = high[center]
        if np.isnan(v):
            continue
        if np.all(v > high[center-left:center]) and np.all(v > high[center+1:center+right+1]):
            prices[center + right] = v
            origins[center + right] = center
    return prices, origins


def confirmed_pivot_low(low: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(low)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = low[center]
        if np.isnan(v):
            continue
        if np.all(v < low[center-left:center]) and np.all(v < low[center+1:center+right+1]):
            prices[center + right] = v
            origins[center + right] = center
    return prices, origins


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f'{symbol}__120d__15m.csv'
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['asset'] = asset
    return df.sort_values('timestamp').reset_index(drop=True)


def compute_channel_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    high = df['high'].to_numpy(dtype=float)
    low = df['low'].to_numpy(dtype=float)
    close = df['close'].to_numpy(dtype=float)
    ph_price, ph_origin = confirmed_pivot_high(high, PIVOT_LEFT, PIVOT_RIGHT)
    pl_price, pl_origin = confirmed_pivot_low(low, PIVOT_LEFT, PIVOT_RIGHT)

    cols = {
        'res_line': np.full(len(df), np.nan),
        'sup_line': np.full(len(df), np.nan),
        'res_slope': np.full(len(df), np.nan),
        'sup_slope': np.full(len(df), np.nan),
        'corridor_width': np.full(len(df), np.nan),
        'width_cv': np.full(len(df), np.nan),
        'channel_ready': np.zeros(len(df), dtype=int),
        'channel_direction': np.zeros(len(df), dtype=int),
        'raw_long_break': np.zeros(len(df), dtype=int),
        'raw_short_break': np.zeros(len(df), dtype=int),
        'hold_long_break': np.zeros(len(df), dtype=int),
        'hold_short_break': np.zeros(len(df), dtype=int),
        'paired_high_points': np.zeros(len(df), dtype=int),
        'paired_low_points': np.zeros(len(df), dtype=int),
    }

    width_hist: list[float] = []
    prev_raw_long = False
    prev_raw_short = False
    prev_close = np.nan
    prev_res = np.nan
    prev_sup = np.nan
    prev_ready = False

    for i in range(len(df)):
        window_start = max(0, i - LOOKBACK_BARS + 1)
        hi_mask = (ph_origin >= window_start) & (ph_origin < i) & (~np.isnan(ph_price))
        lo_mask = (pl_origin >= window_start) & (pl_origin < i) & (~np.isnan(pl_price))
        hi_idx = ph_origin[hi_mask]
        hi_val = ph_price[hi_mask]
        lo_idx = pl_origin[lo_mask]
        lo_val = pl_price[lo_mask]
        cols['paired_high_points'][i] = len(hi_idx)
        cols['paired_low_points'][i] = len(lo_idx)

        ready = False
        direction = 0
        res_line = np.nan
        sup_line = np.nan
        res_slope = np.nan
        sup_slope = np.nan
        width = np.nan
        width_cv = np.nan

        if len(hi_idx) >= MIN_POINTS and len(lo_idx) >= MIN_POINTS:
            hi_coef = np.polyfit(hi_idx.astype(float), hi_val.astype(float), 1)
            lo_coef = np.polyfit(lo_idx.astype(float), lo_val.astype(float), 1)
            res_slope, res_intercept = float(hi_coef[0]), float(hi_coef[1])
            sup_slope, sup_intercept = float(lo_coef[0]), float(lo_coef[1])
            res_line = res_slope * i + res_intercept
            sup_line = sup_slope * i + sup_intercept
            width = res_line - sup_line
            mean_abs_slope = max((abs(res_slope) + abs(sup_slope)) / 2.0, 1e-9)
            slope_gap = abs(res_slope - sup_slope) / mean_abs_slope
            width_hist.append(width if width > 0 else np.nan)
            recent_widths = [w for w in width_hist[-WIDTH_STABILITY_LOOKBACK:] if not (pd.isna(w) or w <= 0)]
            if recent_widths:
                width_mean = float(np.mean(recent_widths))
                width_std = float(np.std(recent_widths, ddof=0))
                width_cv = width_std / width_mean if width_mean > 0 else np.nan
            if width > 0 and slope_gap <= SLOPE_REL_TOL and not pd.isna(width_cv) and width_cv <= WIDTH_STABILITY_MAX_CV:
                avg_slope = (res_slope + sup_slope) / 2.0
                direction = 1 if avg_slope > 0 else -1 if avg_slope < 0 else 0
                ready = direction != 0

        cols['res_line'][i] = res_line
        cols['sup_line'][i] = sup_line
        cols['res_slope'][i] = res_slope
        cols['sup_slope'][i] = sup_slope
        cols['corridor_width'][i] = width
        cols['width_cv'][i] = width_cv
        cols['channel_ready'][i] = int(ready)
        cols['channel_direction'][i] = direction

        raw_long = bool(ready and direction > 0 and prev_ready and not pd.isna(prev_res) and not pd.isna(prev_close) and prev_close <= prev_res and close[i] > res_line)
        raw_short = bool(ready and direction < 0 and prev_ready and not pd.isna(prev_sup) and not pd.isna(prev_close) and prev_close >= prev_sup and close[i] < sup_line)
        hold_long = bool(raw_long or (ready and prev_raw_long and close[i] > res_line))
        hold_short = bool(raw_short or (ready and prev_raw_short and close[i] < sup_line))
        cols['raw_long_break'][i] = int(raw_long)
        cols['raw_short_break'][i] = int(raw_short)
        cols['hold_long_break'][i] = int(hold_long)
        cols['hold_short_break'][i] = int(hold_short)

        prev_raw_long = raw_long
        prev_raw_short = raw_short
        prev_ready = ready
        prev_close = close[i]
        prev_res = res_line
        prev_sup = sup_line

    for k, v in cols.items():
        df[k] = v
    return df


@dataclass
class TradeSpec:
    asset: str
    variant: str
    cost: float
    signal_idx: int
    entry_idx: int
    exit_idx: int
    direction: int
    event_ts: str
    entry_ts: str
    exit_ts: str
    entry_price: float
    exit_price: float
    gross_ret: float
    net_ret: float
    false_break_ratio: float
    corridor_width: float
    width_cv: float
    res_slope: float
    sup_slope: float


def variant_trigger(frame: pd.DataFrame, idx: int, variant: str) -> tuple[int, str] | None:
    if variant == 'raw_corridor_breach':
        if frame.iloc[idx]['raw_long_break'] == 1:
            return 1, 'raw_corridor_breach'
        if frame.iloc[idx]['raw_short_break'] == 1:
            return -1, 'raw_corridor_breach'
    if variant == 'breach_plus_reclaim_hold':
        if frame.iloc[idx]['hold_long_break'] == 1 and frame.iloc[idx - 1]['raw_long_break'] == 1:
            return 1, 'breach_plus_reclaim_hold'
        if frame.iloc[idx]['hold_short_break'] == 1 and frame.iloc[idx - 1]['raw_short_break'] == 1:
            return -1, 'breach_plus_reclaim_hold'
    return None


def detect_false_break(frame: pd.DataFrame, signal_idx: int, direction: int) -> int:
    for step in range(1, FAILURE_LOOKAHEAD + 1):
        j = signal_idx + step
        if j >= len(frame):
            break
        row = frame.iloc[j]
        if row['channel_ready'] != 1:
            return 1
        close = float(row['close'])
        if direction > 0 and close <= float(row['res_line']):
            return 1
        if direction < 0 and close >= float(row['sup_line']):
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost) / 10000.0
    last_exit = -1
    for idx in range(1, len(frame) - 1):
        if idx <= last_exit:
            continue
        trigger = variant_trigger(frame, idx, variant)
        if trigger is None:
            continue
        direction, trigger_name = trigger
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        if entry_idx >= len(frame):
            continue
        entry_price = float(frame.iloc[entry_idx]['open'])
        exit_price = float(frame.iloc[exit_idx]['close'])
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append({
            'asset': asset,
            'variant': trigger_name,
            'cost_bps_per_side': float(cost),
            'signal_idx': int(idx),
            'event_ts': pd.to_datetime(frame.iloc[idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'entry_ts': pd.to_datetime(frame.iloc[entry_idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'exit_ts': pd.to_datetime(frame.iloc[exit_idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'direction': 'long' if direction > 0 else 'short',
            'entry_price': entry_price,
            'exit_price': exit_price,
            'gross_ret': gross_ret,
            'net_ret': net_ret,
            'hold_bars': int(exit_idx - entry_idx + 1),
            'false_break_ratio': float(detect_false_break(frame, idx, direction)),
            'corridor_width': float(frame.iloc[idx]['corridor_width']) if not pd.isna(frame.iloc[idx]['corridor_width']) else np.nan,
            'width_cv': float(frame.iloc[idx]['width_cv']) if not pd.isna(frame.iloc[idx]['width_cv']) else np.nan,
            'res_slope': float(frame.iloc[idx]['res_slope']) if not pd.isna(frame.iloc[idx]['res_slope']) else np.nan,
            'sup_slope': float(frame.iloc[idx]['sup_slope']) if not pd.isna(frame.iloc[idx]['sup_slope']) else np.nan,
        })
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, asset: str, variant: str, cost: float) -> dict[str, object]:
    if trades.empty:
        return {
            'asset': asset,
            'variant': variant,
            'cost_bps_per_side': float(cost),
            'trades': 0,
            'win_rate': np.nan,
            'avg_net_ret': np.nan,
            'median_net_ret': np.nan,
            'total_return': 0.0,
            'false_break_ratio': np.nan,
            'avg_width_cv': np.nan,
            'avg_corridor_width_pct': np.nan,
            'long_share': np.nan,
            'short_share': np.nan,
        }
    return {
        'asset': asset,
        'variant': variant,
        'cost_bps_per_side': float(cost),
        'trades': int(len(trades)),
        'win_rate': float((trades['net_ret'] > 0).mean()),
        'avg_net_ret': float(trades['net_ret'].mean()),
        'median_net_ret': float(trades['net_ret'].median()),
        'total_return': float((1.0 + trades['net_ret']).prod() - 1.0),
        'false_break_ratio': float(trades['false_break_ratio'].mean()),
        'avg_width_cv': float(trades['width_cv'].mean()),
        'avg_corridor_width_pct': float((trades['corridor_width'] / trades['entry_price']).mean()),
        'long_share': float((trades['direction'] == 'long').mean()),
        'short_share': float((trades['direction'] == 'short').mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(['variant', 'cost_bps_per_side'], sort=False):
        total_returns = grp['total_return'].to_numpy(dtype=float)
        rows.append({
            'variant': variant,
            'cost_bps_per_side': float(cost),
            'mean_total_return': float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
            'median_total_return': float(np.nanmedian(total_returns)) if len(total_returns) else np.nan,
            'positive_asset_ratio': float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
            'mean_trades': float(grp['trades'].mean()),
            'mean_false_break_ratio': float(grp['false_break_ratio'].mean()),
            'mean_width_cv': float(grp['avg_width_cv'].mean()),
            'mean_corridor_width_pct': float(grp['avg_corridor_width_pct'].mean()),
            'mean_win_rate': float(grp['win_rate'].mean()),
        })
    return pd.DataFrame(rows)


def build_width_stability_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for asset, frame in frames.items():
        ready = frame[frame['channel_ready'] == 1].copy()
        if ready.empty:
            rows.append({
                'asset': asset,
                'ready_ratio': 0.0,
                'mean_width_cv': np.nan,
                'median_width_cv': np.nan,
                'p90_width_cv': np.nan,
                'mean_corridor_width_pct': np.nan,
                'mean_high_points': float(frame['paired_high_points'].mean()),
                'mean_low_points': float(frame['paired_low_points'].mean()),
            })
            continue
        rows.append({
            'asset': asset,
            'ready_ratio': float((frame['channel_ready'] == 1).mean()),
            'mean_width_cv': float(ready['width_cv'].mean()),
            'median_width_cv': float(ready['width_cv'].median()),
            'p90_width_cv': float(ready['width_cv'].quantile(0.9)),
            'mean_corridor_width_pct': float((ready['corridor_width'] / ready['close']).mean()),
            'mean_high_points': float(ready['paired_high_points'].mean()),
            'mean_low_points': float(ready['paired_low_points'].mean()),
        })
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
    if primary.empty:
        return 'park / evidence pool', '没有形成足够样本，连最小 clean replication 都不够站住。'
    row = primary.iloc[0]
    positive = float(row['positive_asset_ratio']) if not pd.isna(row['positive_asset_ratio']) else 0.0
    mean_ret = float(row['mean_total_return']) if not pd.isna(row['mean_total_return']) else -1.0
    mean_trades = float(row['mean_trades']) if not pd.isna(row['mean_trades']) else 0.0
    false_break = float(row['mean_false_break_ratio']) if not pd.isna(row['mean_false_break_ratio']) else 1.0
    width_cv = float(row['mean_width_cv']) if not pd.isna(row['mean_width_cv']) else 9.9
    if mean_ret > 0 and positive >= 2/3 and mean_trades >= 15 and false_break <= 0.45 and width_cv <= 0.25:
        return 'P1 weak candidate', '最小 clean replication 过了 Stage A 的便宜门槛：成本后仍为正、跨资产没有塌成单腿、交易数也不算太稀。'
    return 'park / evidence pool', '最小 clean replication 没把它拉进候选池：要么成本后回报仍偏弱，要么假突破率 / 宽度稳定性 / 交易密度没有一起过关。'


def update_reading_report(report_path: Path) -> None:
    if not report_path.exists():
        return
    text = report_path.read_text()
    if 'rank30_trendln_channel_clean_replication.html' in text:
        return
    anchor = 'rank30_trendln_channel_source_intake.html'
    idx = text.find(anchor)
    if idx == -1:
        return
    end = text.find('</li>', idx)
    if end == -1:
        return
    insert = ' ｜ <a href="rank30_trendln_channel_clean_replication.html">clean replication</a>'
    text = text[:end] + insert + text[end:]
    report_path.write_text(text)


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, width_summary: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
    if primary.empty:
        headline = '主变体没有形成可用样本。'
    else:
        row = primary.iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下："
            f"跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio={num(row['positive_asset_ratio'] * 3 if not pd.isna(row['positive_asset_ratio']) else np.nan, 1)}/3、"
            f"mean_trades≈{num(row['mean_trades'], 1)}、"
            f"mean_false_break_ratio≈{pct(row['mean_false_break_ratio'])}。"
        )
    overall_view = overall.copy()
    overall_view['cost_bps_per_side'] = overall_view['cost_bps_per_side'].astype(int)
    asset_view = asset_summary.copy()
    asset_view['cost_bps_per_side'] = asset_view['cost_bps_per_side'].astype(int)
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 30 · trendln paired-channel breach clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='report.html'>← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 30 · trendln paired-channel breach / corridor breakout gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较两档最小规则：<code>raw_corridor_breach</code> vs <code>breach_plus_reclaim_hold</code>。</li>
      <li>只回答四个便宜问题：<code>trade_count</code>、<code>false_break_ratio</code>、<code>post_cost_return</code>、<code>width-stability</code>。</li>
      <li>执行口径固定：信号 bar 只用当时已确认的 pivot 线；入场 = <code>next-bar open</code>；持有 = <code>{HOLD_BARS}</code> 根 15m bar。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>通道成立：</b>过去 {LOOKBACK_BARS} 根里，support / resistance 两条拟合线都至少有 {MIN_POINTS} 个因果确认 pivot，斜率方向一致，且最近 {WIDTH_STABILITY_LOOKBACK} 根的 corridor width 变异系数 <code>≤ {WIDTH_STABILITY_MAX_CV:.2f}</code>。</li>
      <li><b>raw corridor breach：</b>上一根还在外轨内侧，本根收盘真正穿出 outer line，且平均斜率同向。</li>
      <li><b>breach + reclaim hold：</b>先出现 raw breach，再要求下一根收盘仍留在 corridor 外侧，避免只靠一根 wick / 单根假动作入场。</li>
      <li><b>假突破定义：</b>触发后 {FAILURE_LOOKAHEAD} 根内，收盘重新回到同一方向边界内，或通道状态直接失效。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(verdict_reason)}</p>
  </div>

  <div class='card'>
    <h2>跨资产总表</h2>
    {render_table(overall_view[['variant','cost_bps_per_side','mean_total_return','positive_asset_ratio','mean_trades','mean_false_break_ratio','mean_width_cv','mean_corridor_width_pct','mean_win_rate']], percent_cols={'mean_total_return','positive_asset_ratio','mean_false_break_ratio','mean_corridor_width_pct','mean_win_rate'}, digits_cols={'mean_trades':1,'mean_width_cv':3})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_view[['asset','variant','cost_bps_per_side','trades','total_return','false_break_ratio','avg_width_cv','avg_corridor_width_pct','win_rate','long_share','short_share']], percent_cols={'total_return','false_break_ratio','avg_corridor_width_pct','win_rate','long_share','short_share'}, digits_cols={'trades':0,'avg_width_cv':3})}
  </div>

  <div class='card'>
    <h2>corridor width stability 审计</h2>
    {render_table(width_summary[['asset','ready_ratio','mean_width_cv','median_width_cv','p90_width_cv','mean_corridor_width_pct','mean_high_points','mean_low_points']], percent_cols={'ready_ratio','mean_corridor_width_pct'}, digits_cols={'mean_width_cv':3,'median_width_cv':3,'p90_width_cv':3,'mean_high_points':1,'mean_low_points':1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank30_trendln_channel_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank30_trendln_channel_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank30_trendln_channel_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../../artifacts/scout_rank30_trendln_channel_15m/width_stability_summary.csv'>width_stability_summary.csv</a></li>
      <li><a href='../../../reading/trendline_alpha_scout/rank30_trendln_channel_source_intake.html'>source intake card</a></li>
    </ul>
  </div>
</body>
</html>
"""
    return html


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame) -> None:
    text = TODO_PATH.read_text()
    old = """  30. `Rank 30 trendln paired-channel breach / corridor breakout gate`（GitHub `trendln` repo + clean-room channel derivative）→ **`fresh intake only / admit_to_clean_replication_queue`**
     - 本轮只做了 1 张 **source-intake** 卡，不偷跑 clean replication：当前默认把 `trendln` 的 extrema -> paired-line / channel geometry 语义，压成 desk 可执行的下一条 `paper / repo based 15m crypto` 候选。
     - 冻结入口规则：`trade on = 先得到因果配对的 support/resistance lines，且 corridor width 没有异常漂移；随后只有 close-confirm breach outer line、且 composite trend 同向时才允许进场`；`trade off = 没有 paired active lines / 只有 wick 穿越 / breach 后很快收回 corridor 内`。
     - 当前 hard verdict 只有一个：**`admit_to_clean_replication_queue`**。它的价值在于：比继续磨 `Rank 29` 的 P3 近义 wiring 更有边际价值，也比 prediction-market / equity-proxy 这类额外数据依赖线更便宜诚实。
     - 下一轮若继续认领，默认只允许做 **1 个最小 clean replication**：固定复用 `BTC/ETH/SOL 120d 15m` cache，比较 `raw corridor breach` vs `breach_plus_reclaim_hold`，先回答 `trade_count / false_break_ratio / post_cost_return / width-stability`，然后快速判 `park / P1`。
     - 网页落点：`reports/site/reading/trendline_alpha_scout/rank30_trendln_channel_source_intake.html`。
"""
    primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
    if not primary.empty:
        row = primary.iloc[0]
        stats = (
            f"主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(row['mean_total_return'])}`、"
            f"`positive_asset_ratio≈{pct(row['positive_asset_ratio'])}`、`mean_trades≈{num(row['mean_trades'],1)}`、"
            f"`mean_false_break_ratio≈{pct(row['mean_false_break_ratio'])}`、`mean_width_cv≈{num(row['mean_width_cv'],3)}`"
        )
    else:
        stats = '主变体没有形成可用样本'
    new = f"""  30. `Rank 30 trendln paired-channel breach / corridor breakout gate`（GitHub `trendln` repo + clean-room channel derivative）→ **`{verdict}`**
     - 已完成 `fresh source intake -> 最小 clean replication`，全程固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `raw corridor breach` 与 `breach_plus_reclaim_hold`，不追新 bar，也不扩成完整 stability pack。
     - 冻结后的 clean-room 规则：`trade on = 过去 {LOOKBACK_BARS} 根里用因果确认 pivot 拟合出成对 support/resistance 线，且 corridor width 最近 {WIDTH_STABILITY_LOOKBACK} 根的变异系数不过阈值；随后只有 close-confirm breach outer line、且平均斜率同向时才允许入场`；`trade off = paired line 不成立 / width 漂移过大 / 只有 wick 穿越 / breach 后很快收回 corridor 内`。
     - 当前最诚实的主证据：{stats}。
     - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：它已经不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只允许按这个 verdict 走下一步——`P1` 才能拿到那唯一允许的一次便宜诚实检查，`park` 则应回到证据池，而不是继续停在 intake 文案上。
     - 网页落点：`reports/site/factors/scout_rank30_trendln_channel_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank30_trendln_channel_source_intake.html`。
"""
    if old in text:
        text = text.replace(old, new, 1)
    else:
        marker = "  30. `Rank 30 trendln paired-channel breach / corridor breakout gate`"
        start = text.find(marker)
        if start != -1:
            # replace until next rank or double newline before duplicated stale block
            next_rank = text.find('\n\n     - 已完成 `fresh source intake -> 最小 clean replication', start)
            if next_rank != -1:
                end = next_rank
            else:
                end = text.find('\n\n', start)
                end = len(text) if end == -1 else end
            text = text[:start] + new + text[end:]
    TODO_PATH.write_text(text)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    frames = {asset: compute_channel_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    all_trades = []
    asset_rows = []
    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f'{asset.lower().replace("-usd","")}_channel_frame.csv', index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades = build_trades(frame, asset, variant, cost)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    trades.to_csv(ART_DIR / f'trades_primary_6bps_{asset.lower().replace("-usd","")}.csv', index=False)
                all_trades.append(trades)
                asset_rows.append(summarize_asset(trades, asset, variant, cost))

    all_trades_df = pd.concat([t for t in all_trades if t is not None], ignore_index=True) if all_trades else pd.DataFrame()
    if not all_trades_df.empty:
        primary_all = all_trades_df[(all_trades_df['variant'] == PRIMARY_VARIANT) & (all_trades_df['cost_bps_per_side'] == PRIMARY_COST)].copy()
        primary_all.to_csv(ART_DIR / 'trades_primary_6bps.csv', index=False)
    else:
        pd.DataFrame().to_csv(ART_DIR / 'trades_primary_6bps.csv', index=False)
    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    width_summary = build_width_stability_summary(frames)
    verdict, verdict_reason = build_verdict(overall)

    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    width_summary.to_csv(ART_DIR / 'width_stability_summary.csv', index=False)

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = build_html(overall, asset_summary, width_summary, verdict, verdict_reason, generated_at)
    (SITE_DIR / 'report.html').write_text(html)
    (SITE_DIR / 'rank30_trendln_channel_clean_replication.html').write_text(html)

    update_reading_report(READING_REPORT)
    update_todo(verdict, generated_at, overall)

    print(f'verdict={verdict}')
    if not overall.empty:
        primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
        if not primary.empty:
            row = primary.iloc[0]
            print('primary_stats', row.to_dict())


if __name__ == '__main__':
    main()
