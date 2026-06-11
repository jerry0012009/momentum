#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
CAL_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank150_dfa_hurst_persistence_gate_15m'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank150_breakout_short_family_honest_gate_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank150_breakout_short_family_honest_gate_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank150_breakout_short_family_honest_gate.html'
ASSETS = {'BTC-USD': 'BTCUSDT', 'ETH-USD': 'ETHUSDT', 'SOL-USD': 'SOLUSDT'}
WINDOW = 192
STEP = 4
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
VARIANTS = ['baseline', 'high_only', 'low_veto_mid_half']
CSS = "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:1160px;margin:32px auto;padding:0 18px 48px;line-height:1.68;color:#111827;background:#f8fafc}.card{border:1px solid #e5e7eb;border-radius:14px;background:#fff;padding:18px 20px;margin:16px 0}.muted{color:#6b7280}code{background:#f3f4f6;padding:1px 5px;border-radius:6px}table{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;background:#fff}th,td{border-bottom:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def num(v, digits: int = 2) -> str:
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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding='utf-8')


def dfa_alpha(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if len(x) < 16 or not np.isfinite(x).all():
        return math.nan
    x = x - np.mean(x)
    y = np.cumsum(x)
    n = len(y)
    max_scale = n // 4
    if max_scale < 8:
        return math.nan
    scales = np.unique(np.floor(np.logspace(np.log10(8), np.log10(max_scale), 8)).astype(int))
    flucts, good_scales = [], []
    for scale in scales:
        segments = n // scale
        if segments < 2:
            continue
        trimmed = y[:segments * scale].reshape(segments, scale)
        t = np.arange(scale, dtype=float)
        rms_vals = []
        for seg in trimmed:
            coeffs = np.polyfit(t, seg, 1)
            trend = coeffs[0] * t + coeffs[1]
            resid = seg - trend
            rms = math.sqrt(float(np.mean(resid * resid)))
            if np.isfinite(rms) and rms > 0:
                rms_vals.append(rms)
        if rms_vals:
            flucts.append(float(np.mean(rms_vals)))
            good_scales.append(scale)
    if len(good_scales) < 2:
        return math.nan
    return float(np.polyfit(np.log(good_scales), np.log(flucts), 1)[0])


def rolling_dfa_sparse(close: pd.Series, window: int, step: int = STEP) -> pd.Series:
    values = close.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(window - 1, len(values), step):
        out[i] = dfa_alpha(values[i - window + 1:i + 1])
    return pd.Series(out, index=close.index)


def load_thresholds() -> tuple[float, float]:
    df = pd.read_csv(CAL_DIR / 'estimator_calibration_summary.csv')
    row = df.loc[df['window'] == WINDOW].iloc[0]
    return float(row['low_threshold']), float(row['high_threshold'])


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f'{symbol}__120d__15m.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['asset'] = asset
    return df.sort_values('timestamp').reset_index(drop=True)


def build_frame(asset: str, symbol: str, low_th: float, high_th: float) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['vol_ma20'] = df['volume'].rolling(20, min_periods=20).mean()
    df['roll_low_20'] = df['low'].rolling(20, min_periods=20).min().shift(1)
    df['roll_low_55'] = df['low'].rolling(55, min_periods=55).min().shift(1)
    df['ret_3'] = df['close'].pct_change(3)
    df['dfa_192_raw'] = rolling_dfa_sparse(df['close'], WINDOW)
    df['dfa_192'] = df['dfa_192_raw'].ffill()
    df['persistence_bucket'] = np.select([df['dfa_192'] < low_th, df['dfa_192'] > high_th], ['low', 'high'], default='mid')
    df.loc[df['dfa_192'].isna(), 'persistence_bucket'] = 'off'
    df['breakout_short_signal'] = ((df['close'] < df['roll_low_20']) & (df['ema9'] < df['ema21']) & (df['ret_3'] < -0.004) & (df['close'] <= df['roll_low_55'] * 1.01) & (df['volume'] > df['vol_ma20'])).fillna(False)
    return df


def variant_size(bucket: str, variant: str) -> float:
    if bucket == 'off':
        return 0.0
    if variant == 'baseline':
        return 1.0
    if variant == 'high_only':
        return 1.0 if bucket == 'high' else 0.0
    if variant == 'low_veto_mid_half':
        return {'low': 0.0, 'mid': 0.5, 'high': 1.0}.get(bucket, 0.0)
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows = []
    cost_rate = float(cost_bps) / 10000.0
    signal_events = 0
    last_exit = -1
    raw_signal = frame['breakout_short_signal'] & ~frame['breakout_short_signal'].shift(1).fillna(False)
    for idx in range(60, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit or not bool(raw_signal.iloc[idx]):
            continue
        signal_events += 1
        bucket = str(frame.iloc[idx]['persistence_bucket'])
        size = variant_size(bucket, variant)
        if size <= 0:
            continue
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS)
        entry_px = float(frame.iloc[entry_idx]['open'])
        exit_px = float(frame.iloc[exit_idx]['open'])
        gross_ret = (entry_px / exit_px - 1.0) * size
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate * size) * (1.0 - cost_rate * size) - 1.0
        path = frame.iloc[entry_idx:min(len(frame), entry_idx + EARLY_FAIL_BARS + 1)]
        early_fail = bool(((path['close'] > path['ema9']) | (path['close'] > path['ema21'])).any())
        rows.append({
            'asset': asset, 'variant': variant, 'cost_bps_per_side': float(cost_bps), 'bucket': bucket, 'size': size,
            'signal_ts': pd.to_datetime(frame.iloc[idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'entry_ts': pd.to_datetime(frame.iloc[entry_idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'exit_ts': pd.to_datetime(frame.iloc[exit_idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'entry_price': entry_px, 'exit_price': exit_px, 'gross_ret': gross_ret, 'net_ret': net_ret,
            'early_fail_4bars': int(early_fail), 'dfa_192': float(frame.iloc[idx]['dfa_192']) if pd.notna(frame.iloc[idx]['dfa_192']) else math.nan,
        })
        last_exit = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, asset: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {'asset': asset, 'variant': variant, 'cost_bps_per_side': cost_bps, 'signal_events': signal_events, 'trades': 0, 'trade_retention': 0.0, 'avg_size': 0.0, 'total_net_return': 0.0, 'mean_net_ret': 0.0, 'win_rate': 0.0, 'early_fail_rate': 0.0}
    return {
        'asset': asset, 'variant': variant, 'cost_bps_per_side': cost_bps, 'signal_events': signal_events,
        'trades': int(len(trades)), 'trade_retention': float(len(trades) / signal_events) if signal_events else 0.0,
        'avg_size': float(trades['size'].mean()), 'total_net_return': float(trades['net_ret'].sum()),
        'mean_net_ret': float(trades['net_ret'].mean()), 'win_rate': float((trades['net_ret'] > 0).mean()), 'early_fail_rate': float(trades['early_fail_4bars'].mean()),
    }


def pooled_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), g in asset_summary.groupby(['variant', 'cost_bps_per_side']):
        weights = np.maximum(g['trades'], 1)
        rows.append({
            'variant': variant, 'cost_bps_per_side': float(cost_bps), 'signal_events': int(g['signal_events'].sum()), 'trades': int(g['trades'].sum()),
            'trade_retention': float(g['trades'].sum() / g['signal_events'].sum()) if g['signal_events'].sum() else 0.0,
            'avg_size': float(np.average(g['avg_size'], weights=weights)), 'total_net_return': float(g['total_net_return'].sum()),
            'mean_net_ret': float(np.average(g['mean_net_ret'], weights=weights)), 'win_rate': float(np.average(g['win_rate'], weights=weights)),
            'early_fail_rate': float(np.average(g['early_fail_rate'], weights=weights)), 'positive_asset_ratio': float((g['total_net_return'] > 0).mean()),
        })
    return pd.DataFrame(rows)


def bucket_mix(trades: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, bucket), g in trades.groupby(['variant', 'bucket']):
        total = len(trades[trades['variant'] == variant])
        rows.append({'variant': variant, 'bucket': bucket, 'trades': int(len(g)), 'share': float(len(g) / total) if total else 0.0, 'mean_net_ret': float(g['net_ret'].mean()), 'avg_size': float(g['size'].mean())})
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    low_th, high_th = load_thresholds()
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    trade_frames, asset_rows = [], []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol, low_th, high_th)
        for cost in COSTS:
            for variant in VARIANTS:
                trades, signal_events = build_trades(frame, asset, variant, cost)
                trade_frames.append(trades)
                asset_rows.append(summarize_asset(trades, asset, variant, cost, signal_events))
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_summary = pd.DataFrame(asset_rows)
    pooled = pooled_summary(asset_summary)
    bucket_df = bucket_mix(trades_df[trades_df['cost_bps_per_side'] == PRIMARY_COST].copy())
    trades_df.to_csv(ART_DIR / 'trades.csv', index=False)
    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    pooled.to_csv(ART_DIR / 'pooled_summary.csv', index=False)
    bucket_df.to_csv(ART_DIR / 'bucket_mix_primary_cost.csv', index=False)
    primary = pooled[pooled['cost_bps_per_side'] == PRIMARY_COST].copy()
    base = primary.loc[primary['variant'] == 'baseline'].iloc[0]
    high = primary.loc[primary['variant'] == 'high_only'].iloc[0]
    soft = primary.loc[primary['variant'] == 'low_veto_mid_half'].iloc[0]
    verdict = 'keep_P1 only: 第二 family 复核没有把 shared persistence gate 升成更普适的 desk-family 守门层。' if high['mean_net_ret'] <= base['mean_net_ret'] else 'keep_P1 but evidence is mixed: 第二 family 复核有 uplift，但还不足以跨 family 稳定复现。'
    meta = {'generated_at_utc': generated_at, 'rank': 'Rank 150', 'family': 'breakout-short proxy', 'window': WINDOW, 'threshold_low': low_th, 'threshold_high': high_th, 'primary_cost_bps_per_side': PRIMARY_COST, 'primary_result': {'baseline': base.to_dict(), 'high_only': high.to_dict(), 'low_veto_mid_half': soft.to_dict()}, 'verdict': verdict}
    (ART_DIR / 'family_honest_gate_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    title = 'Rank 150 · breakout-short family honest gate'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：BTC/ETH/SOL 120d 15m cache ｜ family：breakout-short proxy ｜ 执行：signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars ｜ DFA window={WINDOW}</p>
<div class='card'><h2>一句话结论</h2><p>{escape(verdict)}</p><ul>
<li>baseline：mean_net_ret={escape(pct(base['mean_net_ret']))}，retention={escape(pct(base['trade_retention']))}</li>
<li>high_only：mean_net_ret={escape(pct(high['mean_net_ret']))}，retention={escape(pct(high['trade_retention']))}</li>
<li>low_veto_mid_half：mean_net_ret={escape(pct(soft['mean_net_ret']))}，retention={escape(pct(soft['trade_retention']))}</li>
</ul></div>
<div class='card'><h2>Primary pooled summary @ 6bps/side</h2>{render_table(primary[['variant','signal_events','trades','trade_retention','avg_size','total_net_return','mean_net_ret','win_rate','early_fail_rate','positive_asset_ratio']], percent_cols={'trade_retention','mean_net_ret','win_rate','early_fail_rate','positive_asset_ratio'}, digits_cols={'avg_size':2,'total_net_return':4})}</div>
<div class='card'><h2>By asset</h2>{render_table(asset_summary[asset_summary['cost_bps_per_side']==PRIMARY_COST][['asset','variant','trades','trade_retention','avg_size','total_net_return','mean_net_ret','win_rate','early_fail_rate']], percent_cols={'trade_retention','mean_net_ret','win_rate','early_fail_rate'}, digits_cols={'avg_size':2,'total_net_return':4})}</div>
<div class='card'><h2>Gate bucket mix @ 6bps/side</h2>{render_table(bucket_df, percent_cols={'share','mean_net_ret'}, digits_cols={'avg_size':2})}</div>
<p class='muted'>Artifacts：<code>pooled_summary.csv</code>、<code>asset_summary.csv</code>、<code>bucket_mix_primary_cost.csv</code>、<code>family_honest_gate_meta.json</code>。</p>
"""
    write_html(SITE_DIR / 'report.html', title, body)
    write_html(READING_PATH, title, body)
    print('wrote rank150 breakout-short family honest gate artifacts')


if __name__ == '__main__':
    main()
