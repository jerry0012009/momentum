#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'reports' / 'artifacts' / 'quant_digests' / 'ewmac_breakout_alignment_20260323'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_breakout_short_family_honest_gate_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank151_breakout_short_family_honest_gate_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank151_breakout_short_family_honest_gate.html'
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
VARIANTS = ['baseline', 'hard_positive', 'band_pass']
CSS = "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:1160px;margin:32px auto;padding:0 18px 48px;line-height:1.68;color:#111827;background:#f8fafc}.card{border:1px solid #e5e7eb;border-radius:14px;background:#fff;padding:18px 20px;margin:16px 0}.muted{color:#6b7280}code{background:#f3f4f6;padding:1px 5px;border-radius:6px}table{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;background:#fff}th,td{border-bottom:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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
            elif isinstance(value, (float, int)):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def variant_mask(df: pd.DataFrame, q20: float, q80: float, variant: str) -> pd.Series:
    if variant == 'baseline':
        return pd.Series(True, index=df.index)
    if variant == 'hard_positive':
        return df['align_score'] > 0
    if variant == 'band_pass':
        return (df['align_score'] > q20) & (df['align_score'] <= q80)
    raise ValueError(variant)


def summarize(group: pd.DataFrame, signal_count: int, cost_bps: float, variant: str, asset: str) -> dict:
    if group.empty:
        return {
            'asset': asset,
            'variant': variant,
            'cost_bps_per_side': cost_bps,
            'signal_events': signal_count,
            'trades': 0,
            'trade_retention': 0.0,
            'mean_net_bps': 0.0,
            'median_net_bps': 0.0,
            'win_rate': 0.0,
            'total_net_bps': 0.0,
        }
    return {
        'asset': asset,
        'variant': variant,
        'cost_bps_per_side': cost_bps,
        'signal_events': signal_count,
        'trades': int(len(group)),
        'trade_retention': float(len(group) / signal_count) if signal_count else 0.0,
        'mean_net_bps': float(group['net_bps'].mean()),
        'median_net_bps': float(group['net_bps'].median()),
        'win_rate': float((group['net_bps'] > 0).mean()),
        'total_net_bps': float(group['net_bps'].sum()),
    }


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    events = pd.read_csv(SRC_DIR / 'event_table.csv')
    thresholds = json.loads((SRC_DIR / 'thresholds.json').read_text())
    q20 = float(thresholds['q20'])
    q80 = float(thresholds['q80'])

    events = events[events['event_side'] == -1].copy()
    events['ts'] = pd.to_datetime(events['ts'], utc=True)
    events['family'] = 'breakout_short'

    asset_rows = []
    trade_frames = []
    for cost in COSTS:
        for variant in VARIANTS:
            mask = variant_mask(events, q20, q80, variant)
            subset = events.loc[mask].copy()
            subset['variant'] = variant
            subset['cost_bps_per_side'] = cost
            subset['gross_bps'] = subset['signed_bps']
            subset['net_bps'] = subset['signed_bps'] - 2.0 * cost
            trade_frames.append(subset)
            for symbol, sym_df in events.groupby('symbol'):
                signal_count = len(sym_df)
                picked = subset[subset['symbol'] == symbol]
                asset_rows.append(summarize(picked, signal_count, cost, variant, symbol))

    trades = pd.concat(trade_frames, ignore_index=True)
    asset_summary = pd.DataFrame(asset_rows)

    pooled_rows = []
    for (variant, cost), g in asset_summary.groupby(['variant', 'cost_bps_per_side']):
        pooled_rows.append({
            'variant': variant,
            'cost_bps_per_side': float(cost),
            'signal_events': int(g['signal_events'].sum()),
            'trades': int(g['trades'].sum()),
            'trade_retention': float(g['trades'].sum() / g['signal_events'].sum()) if g['signal_events'].sum() else 0.0,
            'mean_net_bps': float((g['mean_net_bps'] * g['trades'].clip(lower=1)).sum() / g['trades'].clip(lower=1).sum()),
            'median_asset_net_bps': float(g['median_net_bps'].median()),
            'win_rate': float((g['win_rate'] * g['trades'].clip(lower=1)).sum() / g['trades'].clip(lower=1).sum()),
            'total_net_bps': float(g['total_net_bps'].sum()),
            'positive_asset_ratio': float((g['total_net_bps'] > 0).mean()),
        })
    pooled = pd.DataFrame(pooled_rows)

    trades.to_csv(ART_DIR / 'trades.csv', index=False)
    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    pooled.to_csv(ART_DIR / 'pooled_summary.csv', index=False)

    primary = pooled[pooled['cost_bps_per_side'] == PRIMARY_COST].copy().set_index('variant')
    base = primary.loc['baseline']
    hard = primary.loc['hard_positive']
    band = primary.loc['band_pass']

    if band['mean_net_bps'] > base['mean_net_bps'] and band['positive_asset_ratio'] >= base['positive_asset_ratio']:
        verdict = 'keep_P1 but stronger：breakout-short family 上，band-pass 明显优于 baseline / hard-positive，值得保留为 family-specific 守门层。'
    else:
        verdict = 'keep_P1：family honest gate 没有形成足够强的 desk-family 升层证据。'

    meta = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'rank': 'Rank 151',
        'family': 'breakout-short',
        'thresholds': {'q20': q20, 'q80': q80},
        'primary_cost_bps_per_side': PRIMARY_COST,
        'primary_result': {
            'baseline': base.to_dict(),
            'hard_positive': hard.to_dict(),
            'band_pass': band.to_dict(),
        },
        'verdict': verdict,
    }
    (ART_DIR / 'family_honest_gate_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    title = 'Rank 151 · breakout-short family honest gate'
    primary_tbl = primary.reset_index()[['variant','signal_events','trades','trade_retention','mean_net_bps','win_rate','total_net_bps','positive_asset_ratio']]
    asset_tbl = asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST][['asset','variant','signal_events','trades','trade_retention','mean_net_bps','win_rate','total_net_bps']]
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(meta['generated_at_utc'])} ｜ family：breakout-short ｜ 事件源：Rank151 digest event_table ｜ frozen 阈值：q20={q20:.4f}, q80={q80:.4f} ｜ 成本层：6/10/15 bps per side</p>
<div class='card'><h2>一句话结论</h2><p>{escape(verdict)}</p><ul>
<li>baseline：mean_net_bps={num(base['mean_net_bps'])}，retention={pct(base['trade_retention'])}</li>
<li>hard_positive：mean_net_bps={num(hard['mean_net_bps'])}，retention={pct(hard['trade_retention'])}</li>
<li>band_pass：mean_net_bps={num(band['mean_net_bps'])}，retention={pct(band['trade_retention'])}</li>
</ul></div>
<div class='card'><h2>Pooled summary @ 6bps/side</h2>{render_table(primary_tbl, percent_cols={'trade_retention','win_rate','positive_asset_ratio'}, digits_cols={'mean_net_bps':2,'total_net_bps':2})}</div>
<div class='card'><h2>Asset breakdown @ 6bps/side</h2>{render_table(asset_tbl, percent_cols={'trade_retention','win_rate'}, digits_cols={'mean_net_bps':2,'total_net_bps':2})}</div>
"""
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"
    (SITE_DIR / 'report.html').write_text(html, encoding='utf-8')
    READING_PATH.write_text(html, encoding='utf-8')

if __name__ == '__main__':
    main()
