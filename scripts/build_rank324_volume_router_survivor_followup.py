#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'rank324_volume_router_followup'
ASSETS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
COSTS = [4.0, 8.0, 12.0]
VARIANTS = [
    {'name': 'router_hard_16_16_z05', 'mom_window': 16, 'xs_window': 16, 'vol_short': 8, 'vol_long': 96, 'z_hi': 0.5, 'z_lo': -0.5},
    {'name': 'router_hard_16_16_z10', 'mom_window': 16, 'xs_window': 16, 'vol_short': 8, 'vol_long': 96, 'z_hi': 1.0, 'z_lo': -1.0},
    {'name': 'router_hard_32_16_z05', 'mom_window': 32, 'xs_window': 16, 'vol_short': 8, 'vol_long': 96, 'z_hi': 0.5, 'z_lo': -0.5},
    {'name': 'router_hard_16_32_z05', 'mom_window': 16, 'xs_window': 32, 'vol_short': 8, 'vol_long': 96, 'z_hi': 0.5, 'z_lo': -0.5},
]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def load_panel() -> pd.DataFrame:
    frames = []
    for symbol in ASSETS:
        df = pd.read_csv(CACHE_DIR / f'{symbol}__120d__15m.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df['asset'] = symbol
        frames.append(df[['timestamp', 'asset', 'open', 'close', 'volume']])
    panel = pd.concat(frames, ignore_index=True).sort_values(['timestamp', 'asset']).reset_index(drop=True)
    panel['bar_ret'] = panel['close'] / panel['close'].groupby(panel['asset']).shift(1) - 1.0
    panel['bar_ret'] = panel['bar_ret'].fillna(0.0)
    return panel


def attach_features(panel: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = panel.copy()
    g = out.groupby('asset')
    out['mom_ret'] = g['close'].pct_change(cfg['mom_window'])
    out['xs_ret'] = g['close'].pct_change(cfg['xs_window'])
    out['log_vol'] = np.log(out['volume'].clip(lower=1e-12))
    out['vol_short_mean'] = g['log_vol'].transform(lambda s: s.rolling(cfg['vol_short'], min_periods=cfg['vol_short']).mean())
    out['vol_long_mean'] = g['log_vol'].transform(lambda s: s.rolling(cfg['vol_long'], min_periods=cfg['vol_long']).mean())
    out['vol_long_std'] = g['log_vol'].transform(lambda s: s.rolling(cfg['vol_long'], min_periods=cfg['vol_long']).std(ddof=0))
    out['vol_z'] = (out['vol_short_mean'] - out['vol_long_mean']) / out['vol_long_std'].replace(0.0, np.nan)
    xs = out.pivot(index='timestamp', columns='asset', values='xs_ret').sort_index()
    ranks = xs.rank(axis=1, method='first', ascending=True)
    centered = ranks.sub(ranks.mean(axis=1), axis=0)
    scaled = centered.div(centered.abs().sum(axis=1).replace(0.0, np.nan), axis=0).fillna(0.0)
    xs_rev = (-scaled).stack().rename('xs_reversal_weight').reset_index()
    out = out.merge(xs_rev, on=['timestamp', 'asset'], how='left')
    out['xs_reversal_weight'] = out['xs_reversal_weight'].fillna(0.0)
    return out


def build_positions(feat: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = feat.copy()
    out['cont_weight_raw'] = np.sign(out['mom_ret']).fillna(0.0)
    out['high_gate'] = (out['vol_z'] >= cfg['z_hi']).astype(float)
    out['low_gate'] = (out['vol_z'] <= cfg['z_lo']).astype(float)
    out['cont_weight'] = out['cont_weight_raw'] * out['high_gate']
    out['rev_weight'] = out['xs_reversal_weight'] * out['low_gate']

    # Normalize each book cross-sectionally per timestamp to honest gross <= 1
    for col in ['cont_weight', 'rev_weight']:
        gross = out.groupby('timestamp')[col].transform(lambda s: s.abs().sum())
        out[col] = np.where(gross > 0, out[col] / gross, 0.0)

    out['router_weight'] = out['cont_weight'] + out['rev_weight']
    for col in ['router_weight', 'cont_weight', 'rev_weight']:
        out[f'{col}_pos'] = out.groupby('asset')[col].shift(1).fillna(0.0)
        out[f'{col}_turnover'] = (out[f'{col}_pos'] - out.groupby('asset')[f'{col}_pos'].shift(1).fillna(0.0)).abs()
    return out


def summarize(sim: pd.DataFrame, pos_col: str, turnover_col: str, cost: float, variant: str, sleeve: str) -> pd.DataFrame:
    rows = []
    cost_rate = cost / 10000.0
    for asset, g in sim.groupby('asset'):
        gross_ret = g[pos_col] * g['bar_ret']
        net_ret = gross_ret - g[turnover_col] * cost_rate
        nav = (1.0 + net_ret).cumprod()
        running_peak = nav.cummax()
        dd = nav / running_peak - 1.0
        rows.append({
            'variant': variant,
            'sleeve': sleeve,
            'asset': asset,
            'cost_bps_per_side': cost,
            'bars': int(len(g)),
            'active_bar_ratio': float((g[pos_col] != 0).mean()),
            'trade_events': int((g[turnover_col] > 1e-12).sum()),
            'mean_turnover': float(g[turnover_col].mean()),
            'mean_net_ret_bps': float(net_ret.mean() * 10000.0),
            'total_return': float(nav.iloc[-1] - 1.0),
            'max_drawdown': float(dd.min()),
            'positive_bar_ratio': float((net_ret > 0).mean()),
        })
    return pd.DataFrame(rows)


def aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    return (
        asset_summary.groupby(['variant', 'sleeve', 'cost_bps_per_side'], as_index=False)
        .agg(
            assets=('asset', 'nunique'),
            positive_assets=('total_return', lambda s: int((s > 0).sum())),
            mean_total_return=('total_return', 'mean'),
            median_total_return=('total_return', 'median'),
            mean_net_ret_bps=('mean_net_ret_bps', 'mean'),
            mean_active_bar_ratio=('active_bar_ratio', 'mean'),
            mean_trade_events=('trade_events', 'mean'),
            mean_turnover=('mean_turnover', 'mean'),
            mean_max_drawdown=('max_drawdown', 'mean'),
        )
        .assign(positive_asset_ratio=lambda d: d['positive_assets'] / d['assets'])
        .sort_values(['sleeve', 'cost_bps_per_side', 'mean_total_return'], ascending=[True, True, False])
        .reset_index(drop=True)
    )


def main() -> int:
    ensure_dir(ART_DIR)
    panel = load_panel()
    asset_rows = []
    meta = []
    for cfg in VARIANTS:
        feat = attach_features(panel, cfg)
        sim = build_positions(feat, cfg)
        meta.append({**cfg})
        for cost in COSTS:
            asset_rows.append(summarize(sim, 'router_weight_pos', 'router_weight_turnover', cost, cfg['name'], 'router'))
            asset_rows.append(summarize(sim, 'cont_weight_pos', 'cont_weight_turnover', cost, cfg['name'], 'continuation_only'))
            asset_rows.append(summarize(sim, 'rev_weight_pos', 'rev_weight_turnover', cost, cfg['name'], 'reversal_only'))
    asset_summary = pd.concat(asset_rows, ignore_index=True)
    overall = aggregate(asset_summary)
    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    pd.DataFrame(meta).to_csv(ART_DIR / 'variant_meta.csv', index=False)
    print('[ok] wrote', ART_DIR / 'overall_summary.csv')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
