#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
OUT_DIR = ROOT / 'reports' / 'artifacts' / 'rank32b_frozen_ablation_exp1_exp2'
OUT_JSON = OUT_DIR / 'summary.json'
OUT_MD = OUT_DIR / 'summary.md'

WINDOWS = [
    ('short_120d', 120),
    ('mid_365d', 365),
    ('long_730d', 730),
]
VARIANTS = [
    ('Exp1', 'ema_cross_only'),
    ('Exp2', 'ema_cross_plus_slope_floor'),
]
COST_BPS = 6.0


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def max_drawdown_from_returns(net_rets: pd.Series) -> float:
    if net_rets.empty:
        return float('nan')
    equity = (1.0 + net_rets.astype(float)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def summarize_trades(trades: pd.DataFrame) -> dict[str, float | int | None]:
    if trades.empty:
        return {
            'trade_count': 0,
            'win_rate': None,
            'pnl': 0.0,
            'expectancy': None,
            'max_drawdown': None,
        }
    net = trades['net_ret'].astype(float)
    return {
        'trade_count': int(len(trades)),
        'win_rate': float((net > 0).mean()),
        'pnl': float((1.0 + net).prod() - 1.0),
        'expectancy': float(net.mean()),
        'max_drawdown': max_drawdown_from_returns(net),
    }


def judge_increment(short: dict, mid: dict, long: dict) -> tuple[str, str, str, str]:
    improvements = 0
    local_only = False
    only_rate_reduction = False

    for rec in [short, mid, long]:
        d_pnl = rec['delta_pnl']
        d_exp = rec['delta_expectancy']
        d_win = rec['delta_win_rate']
        d_count = rec['delta_trade_count']
        if d_pnl is not None and d_exp is not None and d_win is not None:
            if d_pnl > 0 and d_exp > 0 and d_win > 0:
                improvements += 1
            if d_pnl <= 0 and d_count < 0:
                only_rate_reduction = True
    if improvements == 1 and ((short['delta_pnl'] or 0) <= 0 or (mid['delta_pnl'] or 0) <= 0 or (long['delta_pnl'] or 0) <= 0):
        local_only = True

    if improvements >= 2 and not only_rate_reduction:
        verdict = 'slope floor 是真实增量'
        keep = 'Keep'
        min_version = 'baseline + aligned slope floor'
        next_action = '冻结其余层不动，只把 Exp1/Exp2 结果扩展到网页并补一张短中长窗对照表。'
    elif local_only:
        verdict = 'slope floor 是局部增量'
        keep = 'Watch'
        min_version = 'baseline only 作为母体；slope floor 作为候选增量保留观察'
        next_action = '先定位增量只出现在短/中/长哪一窗，再决定是否值得进下一轮验证。'
    elif only_rate_reduction:
        verdict = 'slope floor 主要只是降频，不构成清晰增量'
        keep = 'Watch'
        min_version = 'baseline only'
        next_action = '不要继续叠层，先确认降频后是否真的带来更高 expectancy 或更低 drawdown。'
    else:
        verdict = 'slope floor 无效'
        keep = 'Drop'
        min_version = 'baseline only'
        next_action = '停止在这层继续花时间，回到 baseline 母体再看别的增量。'
    return verdict, keep, min_version, next_action


def fmt_pct(x):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return '-'
    return f'{x*100:.2f}%'


def fmt_num(x):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return '-'
    return f'{x:.4f}'


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    clean = load_module(ROOT / 'scripts' / 'build_rank32_ema_slope_clean_replication.py', 'clean_rank32')
    probe = load_module(ROOT / 'scripts' / 'build_rank32b_extended_history_probe.py', 'probe_rank32b')

    assets = clean.ASSETS
    by_window = {}

    bars_cache: dict[str, pd.DataFrame] = {}
    max_days = max(days for _, days in WINDOWS)
    for asset, symbol in assets.items():
        print(f'[fetch] {asset} {symbol} {max_days}d', flush=True)
        bars_cache[asset] = probe.fetch_binance_bars(symbol, days=max_days)

    for window_label, days in WINDOWS:
        print(f'[window] {window_label} {days}d', flush=True)
        asset_rows = []
        for asset, symbol in assets.items():
            bars_full = bars_cache[asset].copy()
            cutoff = bars_full['timestamp'] >= (bars_full['timestamp'].max() - pd.Timedelta(days=days))
            bars = bars_full.loc[cutoff].copy()
            print(f'  [frame] {asset} rows={len(bars)}', flush=True)
            frame = probe.build_rank32b_frame_from_bars(asset, bars)
            for exp_label, variant in VARIANTS:
                print(f'    [variant] {asset} {variant}', flush=True)
                trades, no_trade_ratio, eligible_bars = clean.build_trades(frame, asset, variant, COST_BPS)
                metrics = summarize_trades(trades)
                asset_rows.append({
                    'window': window_label,
                    'days': days,
                    'asset': asset,
                    'experiment': exp_label,
                    'variant': variant,
                    'no_trade_ratio': float(no_trade_ratio),
                    'eligible_bars': int(eligible_bars),
                    **metrics,
                })
        asset_df = pd.DataFrame(asset_rows)
        overall_rows = []
        for exp_label, variant in VARIANTS:
            grp = asset_df[asset_df['variant'] == variant].copy()
            overall_rows.append({
                'window': window_label,
                'days': days,
                'experiment': exp_label,
                'variant': variant,
                'trade_count': int(grp['trade_count'].sum()),
                'mean_trade_count': float(grp['trade_count'].mean()),
                'win_rate': float(grp['win_rate'].mean()),
                'pnl': float(grp['pnl'].mean()),
                'expectancy': float(grp['expectancy'].mean()),
                'max_drawdown': float(grp['max_drawdown'].mean()),
                'worst_asset_drawdown': float(grp['max_drawdown'].min()),
            })
        overall_df = pd.DataFrame(overall_rows)
        exp1 = overall_df[overall_df['variant'] == 'ema_cross_only'].iloc[0].to_dict()
        exp2 = overall_df[overall_df['variant'] == 'ema_cross_plus_slope_floor'].iloc[0].to_dict()
        delta = {
            'window': window_label,
            'days': days,
            'delta_trade_count': int(exp2['trade_count'] - exp1['trade_count']),
            'delta_win_rate': float(exp2['win_rate'] - exp1['win_rate']),
            'delta_pnl': float(exp2['pnl'] - exp1['pnl']),
            'delta_expectancy': float(exp2['expectancy'] - exp1['expectancy']),
            'delta_max_drawdown': float(exp2['max_drawdown'] - exp1['max_drawdown']),
        }
        by_window[window_label] = {
            'days': days,
            'asset_summary': asset_df.to_dict(orient='records'),
            'overall': overall_df.to_dict(orient='records'),
            'delta': delta,
        }

    short = by_window['short_120d']['delta']
    mid = by_window['mid_365d']['delta']
    long = by_window['long_730d']['delta']
    verdict, keep, min_version, next_action = judge_increment(short, mid, long)

    payload = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'frozen_definition_source': 'https://jp.jerrypsy.top/momentum/factors/rank32b/decomposition.html',
        'constraints': {
            'universe': list(assets.keys()),
            'cost_bps_per_side': COST_BPS,
            'entry_exit_shell': 'next-bar open / hold 8 bars / non-overlap',
            'warmup': 'current-live-like frame from build_rank32b_frame_from_bars',
            'filters_forbidden': ['strongest-only', 'extra filters', 'parameter optimization'],
        },
        'windows': by_window,
        'final': {
            'verdict': verdict,
            'keep_watch_drop': keep,
            'minimal_pushable_version': min_version,
            'next_single_action': next_action,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def overall_row(window_key: str, variant: str) -> dict:
        rows = by_window[window_key]['overall']
        for row in rows:
            if row['variant'] == variant:
                return row
        raise KeyError((window_key, variant))

    lines = []
    lines.append('# Rank32B frozen ablation — Exp1 vs Exp2')
    lines.append('')
    lines.append(f'- Generated at: {payload["generated_at_utc"]}')
    lines.append(f'- Universe: {", ".join(payload["constraints"]["universe"])}')
    lines.append(f'- Cost: {COST_BPS:.1f} bps/side')
    lines.append(f'- Shell: {payload["constraints"]["entry_exit_shell"]}')
    lines.append(f'- Warmup/frame: {payload["constraints"]["warmup"]}')
    lines.append('')
    for window_key, days in [('short_120d',120),('mid_365d',365),('long_730d',730)]:
        lines.append(f'## {window_key} ({days}d)')
        lines.append('')
        lines.append('| Experiment | trade count | win rate | pnl | expectancy | max drawdown |')
        lines.append('|---|---:|---:|---:|---:|---:|')
        for variant in ['ema_cross_only','ema_cross_plus_slope_floor']:
            row = overall_row(window_key, variant)
            exp_label = 'Exp1' if variant == 'ema_cross_only' else 'Exp2'
            lines.append(
                f'| {exp_label} ({variant}) | {row["trade_count"]} | {fmt_pct(row["win_rate"])} | {fmt_pct(row["pnl"])} | {fmt_pct(row["expectancy"])} | {fmt_pct(row["max_drawdown"])} |'
            )
        d = by_window[window_key]['delta']
        lines.append('')
        lines.append(f'- Delta (Exp2 - Exp1): trade count {d["delta_trade_count"]:+d}; win rate {fmt_pct(d["delta_win_rate"])}; pnl {fmt_pct(d["delta_pnl"])}; expectancy {fmt_pct(d["delta_expectancy"])}; max drawdown {fmt_pct(d["delta_max_drawdown"])}')
        lines.append('')
    lines.append('## Final')
    lines.append('')
    lines.append(f'- Verdict: **{verdict}**')
    lines.append(f'- Keep/Watch/Drop: **{keep}**')
    lines.append(f'- 最小可推进版本: **{min_version}**')
    lines.append(f'- 下一步唯一动作: **{next_action}**')
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'json': str(OUT_JSON), 'md': str(OUT_MD), 'final': payload['final']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
