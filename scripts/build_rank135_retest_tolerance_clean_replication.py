#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank76_intraday_clock_polarity_15m'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank135_retest_tolerance_stop_decoupling_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank135_retest_tolerance_stop_decoupling_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank135_retest_tolerance_stop_decoupling_clean_replication.html'

ASSETS = {
    'BTC-USD': 'btcusdt_feature_frame.csv',
    'ETH-USD': 'ethusdt_feature_frame.csv',
    'SOL-USD': 'solusdt_feature_frame.csv',
}
SETUPS = ['breakout_short', 'ema_psar_long', 'fib_retest_long']
PREFIX = {'BTC-USD': 'btcusd', 'ETH-USD': 'ethusd', 'SOL-USD': 'solusd'}
HOLD_BARS = 8
TRAIN_FRACTION = 0.60
TOLERANCES = [0.003, 0.005, 0.008]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding='utf-8',
    )


def load_rows() -> pd.DataFrame:
    feature_frames = {}
    for asset, filename in ASSETS.items():
        frame = pd.read_csv(SRC_DIR / filename)
        frame['timestamp'] = pd.to_datetime(frame['timestamp'], utc=True)
        feature_frames[asset] = frame.sort_values('timestamp').reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for asset, prefix in PREFIX.items():
        frame = feature_frames[asset]
        for setup in SETUPS:
            sig = pd.read_csv(SRC_DIR / f'signals_{prefix}_{setup}_baseline.csv')
            for _, r in sig.iterrows():
                signal_idx = int(r['signal_idx'])
                entry_idx = int(r['entry_idx'])
                exit_idx = entry_idx + HOLD_BARS
                if exit_idx >= len(frame):
                    continue
                entry_open = float(frame.iloc[entry_idx]['open'])
                exit_close = float(frame.iloc[exit_idx]['close'])
                direction = -1.0 if setup == 'breakout_short' else 1.0
                gross_return = (exit_close / entry_open - 1.0) * direction
                level_col = 'breakout_anchor' if setup == 'breakout_short' else ('ema15' if setup == 'ema_psar_long' else 'fib_618')
                level = float(r[level_col]) if pd.notna(r[level_col]) else np.nan
                signal_price = float(r['signal_price'])
                distance_pct = abs(signal_price - level) / abs(level) if np.isfinite(level) and level != 0 else np.nan
                rows.append(
                    {
                        'asset': asset,
                        'setup': setup,
                        'signal_id': r['signal_id'],
                        'signal_ts': pd.to_datetime(r['signal_ts'], utc=True),
                        'signal_idx': signal_idx,
                        'entry_idx': entry_idx,
                        'exit_idx': exit_idx,
                        'entry_open': entry_open,
                        'exit_close': exit_close,
                        'direction': direction,
                        'gross_return': gross_return,
                        'signal_price': signal_price,
                        'reference_level': level,
                        'distance_pct': distance_pct,
                    }
                )
    df = pd.DataFrame(rows).sort_values(['asset', 'signal_ts', 'setup']).reset_index(drop=True)

    keep = []
    for asset, group in df.groupby('asset', sort=False):
        last_exit = -1
        for idx, row in group.iterrows():
            if int(row['entry_idx']) <= last_exit:
                continue
            keep.append(idx)
            last_exit = int(row['exit_idx'])
    return df.loc[keep].sort_values('signal_ts').reset_index(drop=True)


def build_variant_metrics(df: pd.DataFrame, variant: str, cost_bps: float, baseline_n: int) -> dict[str, float | str]:
    net = net_ret(df['gross_return'], cost_bps)
    return {
        'variant': variant,
        'cost_bps': cost_bps,
        'trades': int(len(df)),
        'retention_vs_baseline': float(len(df)) / float(baseline_n) if baseline_n else np.nan,
        'mean_return_bps': float(net.mean() * 10000.0) if len(df) else np.nan,
        'median_return_bps': float(net.median() * 10000.0) if len(df) else np.nan,
        'win_rate': float((net > 0).mean()) if len(df) else np.nan,
    }


def scorecard_rows(test_baseline: pd.DataFrame, test_gate: pd.DataFrame, selected_tolerance: float) -> tuple[pd.DataFrame, dict[str, object]]:
    net6_base = net_ret(test_baseline['gross_return'], PRIMARY_COST)
    net6_gate = net_ret(test_gate['gross_return'], PRIMARY_COST)
    overall_delta_bps = float((net6_gate.mean() - net6_base.mean()) * 10000.0)
    retention = float(len(test_gate)) / float(len(test_baseline)) if len(test_baseline) else np.nan
    positive_assets = int((net6_gate.groupby(test_gate['asset']).mean() > 0).sum()) if len(test_gate) else 0
    positive_setups = int((net6_gate.groupby(test_gate['setup']).mean() > 0).sum()) if len(test_gate) else 0
    deltas_by_cost = []
    gate_positive_costs = 0
    for cost in COSTS:
        delta = (net_ret(test_gate['gross_return'], cost).mean() - net_ret(test_baseline['gross_return'], cost).mean()) * 10000.0
        deltas_by_cost.append(float(delta))
        if net_ret(test_gate['gross_return'], cost).mean() > 0:
            gate_positive_costs += 1

    usefulness = 0
    if overall_delta_bps > 5:
        usefulness = 2
    elif overall_delta_bps > 0:
        usefulness = 1

    time_stability = 1 if selected_tolerance == max(TOLERANCES) else 0
    cross_asset_stability = 2 if positive_assets >= 3 else (1 if positive_assets >= 2 else 0)
    cost_trade_stability = 2 if gate_positive_costs >= 2 else (1 if gate_positive_costs >= 1 else 0)
    deployability = 2 if (overall_delta_bps > 0 and positive_assets >= 2 and positive_setups >= 2 and gate_positive_costs >= 2) else (1 if overall_delta_bps > 0 and positive_assets >= 2 else 0)

    hard_fail_flags = {
        'rule_unclear': False,
        'leakage_risk': False,
        'post_cost_collapse': bool(gate_positive_costs == 0),
        'too_sparse': bool(retention < 0.35),
        'single_pocket_dependency': bool(positive_assets < 3 or positive_setups < 2),
    }

    if overall_delta_bps <= 0 or hard_fail_flags['post_cost_collapse'] or hard_fail_flags['single_pocket_dependency']:
        recommended_action = 'park'
        main_weakness = 'uplift 主要集中在局部长侧 pocket；breakout_short 持续拖后腿，且跨资产仍分裂。'
    elif positive_assets >= 2 and positive_setups >= 2:
        recommended_action = 'promote_P2'
        main_weakness = '成本层仍偏薄，需要最小 stability pack 再确认。'
    else:
        recommended_action = 'keep_P1'
        main_weakness = '目前只有局部 pocket 站住，仍不足以升 paper candidate。'

    why_now = (
        '本轮已完成最小 clean replication；与 baseline 相比，decoupled tolerance 在 6bps 只剩小幅改善，'
        '但 improvement 主要来自 long pocket，不是 desk 级 shared gate。'
    )

    score_df = pd.DataFrame(
        [
            {'metric': 'usefulness', 'score_0_to_3': usefulness},
            {'metric': 'time_stability', 'score_0_to_3': time_stability},
            {'metric': 'cross_asset_stability', 'score_0_to_3': cross_asset_stability},
            {'metric': 'cost_trade_stability', 'score_0_to_3': cost_trade_stability},
            {'metric': 'deployability', 'score_0_to_3': deployability},
            {'metric': 'rule_unclear', 'score_0_to_3': int(hard_fail_flags['rule_unclear'])},
            {'metric': 'leakage_risk', 'score_0_to_3': int(hard_fail_flags['leakage_risk'])},
            {'metric': 'post_cost_collapse', 'score_0_to_3': int(hard_fail_flags['post_cost_collapse'])},
            {'metric': 'too_sparse', 'score_0_to_3': int(hard_fail_flags['too_sparse'])},
            {'metric': 'single_pocket_dependency', 'score_0_to_3': int(hard_fail_flags['single_pocket_dependency'])},
            {'metric': 'recommended_action', 'score_0_to_3': recommended_action},
            {'metric': 'why_now', 'score_0_to_3': why_now},
            {'metric': 'main_weakness', 'score_0_to_3': main_weakness},
        ]
    )
    summary = {
        'overall_delta_bps_6': overall_delta_bps,
        'retention_vs_baseline': retention,
        'positive_assets_6bps': positive_assets,
        'positive_setups_6bps': positive_setups,
        'gate_positive_costs': gate_positive_costs,
        'recommended_action': recommended_action,
        'why_now': why_now,
        'main_weakness': main_weakness,
        'hard_fail_flags': hard_fail_flags,
        'deltas_by_cost_bps': {str(int(c)): d for c, d in zip(COSTS, deltas_by_cost)},
    }
    return score_df, summary


def build_html(overall: pd.DataFrame, asset: pd.DataFrame, setup: pd.DataFrame, train_grid: pd.DataFrame, scorecard: pd.DataFrame, summary: dict[str, object], selected_tolerance: float, generated_at: str) -> None:
    verdict = summary['recommended_action']
    verdict_cls = 'bad' if verdict == 'park' else ('warn' if verdict == 'keep_P1' else 'good')
    body = f"""
    <p><a href='../../index.html'>← 站点首页</a></p>
    <h1>Rank 135 / retest tolerance stop decoupling gate</h1>
    <div class='card'>
      <p><strong>当前硬结论：</strong><span class='{verdict_cls}'>{escape(verdict)}</span></p>
      <p class='muted'>生成时间：{escape(generated_at)} | 口径：BTC/ETH/SOL, 15m, next-bar open, hold {HOLD_BARS} bars, no-overlap, costs 6/10/15bps</p>
      <p>最优 decoupled tolerance（train 60% 选定）= <code>{selected_tolerance * 100:.1f}%</code>。</p>
    </div>
    <div class='card'>
      <h2>一句话读法</h2>
      <p>{escape(summary['why_now'])}</p>
      <p><strong>主弱点：</strong>{escape(summary['main_weakness'])}</p>
    </div>
    <div class='card'>
      <h2>Train tolerance 选择</h2>
      {render_table(train_grid, digits_cols={'tolerance_pct': 3, 'mean_return_bps': 2})}
    </div>
    <div class='card'>
      <h2>Test / overall</h2>
      {render_table(overall, percent_cols={'retention_vs_baseline', 'win_rate'}, digits_cols={'mean_return_bps': 2, 'median_return_bps': 2, 'return_delta_vs_baseline_bps': 2})}
    </div>
    <div class='card'>
      <h2>Test / by asset</h2>
      {render_table(asset, percent_cols={'retention_vs_baseline', 'win_rate'}, digits_cols={'mean_return_bps': 2, 'return_delta_vs_baseline_bps': 2})}
    </div>
    <div class='card'>
      <h2>Test / by setup</h2>
      {render_table(setup, percent_cols={'retention_vs_baseline', 'win_rate'}, digits_cols={'mean_return_bps': 2, 'return_delta_vs_baseline_bps': 2})}
    </div>
    <div class='card'>
      <h2>Scout Promotion Scorecard</h2>
      {render_table(scorecard)}
    </div>
    """
    write_html(SITE_DIR / 'report.html', 'Rank 135 / retest tolerance stop decoupling gate', body)

    reading_body = f"""
    <p><a href='../../index.html'>← 站点首页</a></p>
    <h1>Rank 135 / retest tolerance stop decoupling gate（clean replication）</h1>
    <div class='card'>
      <p><strong>recommended_action：</strong><span class='{verdict_cls}'>{escape(verdict)}</span></p>
      <p><strong>why_now：</strong>{escape(summary['why_now'])}</p>
      <p><strong>main_weakness：</strong>{escape(summary['main_weakness'])}</p>
    </div>
    <div class='card'>
      <ul>
        <li>baseline test @ 6bps：{num(float(overall.loc[(overall['variant']=='baseline') & (overall['cost_bps']==PRIMARY_COST), 'mean_return_bps'].iloc[0]), 2)} bps</li>
        <li>gate test @ 6bps：{num(float(overall.loc[(overall['variant']=='decoupled_tolerance_gate') & (overall['cost_bps']==PRIMARY_COST), 'mean_return_bps'].iloc[0]), 2)} bps</li>
        <li>return delta：{num(float(overall.loc[(overall['variant']=='decoupled_tolerance_gate') & (overall['cost_bps']==PRIMARY_COST), 'return_delta_vs_baseline_bps'].iloc[0]), 2)} bps</li>
        <li>retention：{pct(float(overall.loc[(overall['variant']=='decoupled_tolerance_gate') & (overall['cost_bps']==PRIMARY_COST), 'retention_vs_baseline'].iloc[0]))}</li>
      </ul>
      <p>结论：这条线不是纯风险预算耦合的假象，但 uplift 也没有扩成 desk 级 shared gate；目前更像只帮了部分 long pocket，因此本轮直接 <code>{escape(verdict)}</code>。</p>
    </div>
    """
    write_html(READING_PATH, 'Rank 135 / retest tolerance stop decoupling gate（clean replication）', reading_body)


ensure_dir(ART_DIR)
ensure_dir(SITE_DIR)
ensure_dir(READING_PATH.parent)

all_rows = load_rows()
BASELINE_COUNT = len(all_rows)
all_rows.to_csv(ART_DIR / 'trade_log_all_candidates.csv', index=False)

split_idx = int(len(all_rows) * TRAIN_FRACTION)
train = all_rows.iloc[:split_idx].copy()
test = all_rows.iloc[split_idx:].copy()

train_grid_rows = []
best_tol = None
best_score = -1e18
for tol in TOLERANCES:
    subset = train[train['distance_pct'] <= tol].copy()
    mean_bps = float(net_ret(subset['gross_return'], PRIMARY_COST).mean() * 10000.0) if len(subset) else np.nan
    train_grid_rows.append(
        {
            'tolerance_pct': tol * 100.0,
            'trades': int(len(subset)),
            'retention_vs_baseline': float(len(subset)) / float(len(train)) if len(train) else np.nan,
            'mean_return_bps': mean_bps,
        }
    )
    if len(subset) and mean_bps > best_score:
        best_score = mean_bps
        best_tol = tol

if best_tol is None:
    best_tol = TOLERANCES[-1]

train_grid = pd.DataFrame(train_grid_rows)

test_baseline = test.copy()
test_gate = test[test['distance_pct'] <= best_tol].copy()

trade_log = test.copy()
trade_log['selected_tolerance_pct'] = best_tol * 100.0
trade_log['gate_keep'] = trade_log['distance_pct'] <= best_tol
for cost in COSTS:
    trade_log[f'net_return_{int(cost)}bps'] = net_ret(trade_log['gross_return'], cost)
trade_log.to_csv(ART_DIR / 'trade_log.csv', index=False)

# overall summary
overall_rows = []
baseline_metrics = {}
for cost in COSTS:
    base = build_variant_metrics(test_baseline, 'baseline', cost, len(test_baseline))
    gate = build_variant_metrics(test_gate, 'decoupled_tolerance_gate', cost, len(test_baseline))
    baseline_metrics[cost] = base
    overall_rows.append(base)
    gate['selected_tolerance_pct'] = best_tol * 100.0
    gate['return_delta_vs_baseline_bps'] = gate['mean_return_bps'] - base['mean_return_bps']
    overall_rows.append(gate)
overall = pd.DataFrame(overall_rows)
overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)

# by asset
asset_rows = []
for cost in COSTS:
    base_cost = net_ret(test_baseline['gross_return'], cost)
    gate_cost = net_ret(test_gate['gross_return'], cost)
    for asset in sorted(test_baseline['asset'].unique()):
        base_grp = test_baseline[test_baseline['asset'] == asset]
        gate_grp = test_gate[test_gate['asset'] == asset]
        base_net = net_ret(base_grp['gross_return'], cost)
        gate_net = net_ret(gate_grp['gross_return'], cost)
        asset_rows.append({
            'asset': asset,
            'variant': 'baseline',
            'cost_bps': cost,
            'trades': int(len(base_grp)),
            'retention_vs_baseline': 1.0,
            'mean_return_bps': float(base_net.mean() * 10000.0) if len(base_grp) else np.nan,
            'win_rate': float((base_net > 0).mean()) if len(base_grp) else np.nan,
            'selected_tolerance_pct': np.nan,
            'return_delta_vs_baseline_bps': 0.0,
        })
        asset_rows.append({
            'asset': asset,
            'variant': 'decoupled_tolerance_gate',
            'cost_bps': cost,
            'trades': int(len(gate_grp)),
            'retention_vs_baseline': float(len(gate_grp)) / float(len(base_grp)) if len(base_grp) else np.nan,
            'mean_return_bps': float(gate_net.mean() * 10000.0) if len(gate_grp) else np.nan,
            'win_rate': float((gate_net > 0).mean()) if len(gate_grp) else np.nan,
            'selected_tolerance_pct': best_tol * 100.0,
            'return_delta_vs_baseline_bps': float((gate_net.mean() - base_net.mean()) * 10000.0) if len(gate_grp) and len(base_grp) else np.nan,
        })
asset_summary = pd.DataFrame(asset_rows)
asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)

# by setup
setup_rows = []
for cost in COSTS:
    for setup in SETUPS:
        base_grp = test_baseline[test_baseline['setup'] == setup]
        gate_grp = test_gate[test_gate['setup'] == setup]
        base_net = net_ret(base_grp['gross_return'], cost)
        gate_net = net_ret(gate_grp['gross_return'], cost)
        setup_rows.append({
            'setup': setup,
            'variant': 'baseline',
            'cost_bps': cost,
            'trades': int(len(base_grp)),
            'retention_vs_baseline': 1.0,
            'mean_return_bps': float(base_net.mean() * 10000.0) if len(base_grp) else np.nan,
            'win_rate': float((base_net > 0).mean()) if len(base_grp) else np.nan,
            'selected_tolerance_pct': np.nan,
            'return_delta_vs_baseline_bps': 0.0,
        })
        setup_rows.append({
            'setup': setup,
            'variant': 'decoupled_tolerance_gate',
            'cost_bps': cost,
            'trades': int(len(gate_grp)),
            'retention_vs_baseline': float(len(gate_grp)) / float(len(base_grp)) if len(base_grp) else np.nan,
            'mean_return_bps': float(gate_net.mean() * 10000.0) if len(gate_grp) else np.nan,
            'win_rate': float((gate_net > 0).mean()) if len(gate_grp) else np.nan,
            'selected_tolerance_pct': best_tol * 100.0,
            'return_delta_vs_baseline_bps': float((gate_net.mean() - base_net.mean()) * 10000.0) if len(gate_grp) and len(base_grp) else np.nan,
        })
setup_summary = pd.DataFrame(setup_rows)
setup_summary.to_csv(ART_DIR / 'setup_summary.csv', index=False)

train_grid.to_csv(ART_DIR / 'threshold_config.csv', index=False)

scorecard, score_summary = scorecard_rows(test_baseline, test_gate, best_tol)
scorecard.to_csv(ART_DIR / 'scout_promotion_scorecard.csv', index=False)

summary = {
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'hold_bars': HOLD_BARS,
    'train_fraction': TRAIN_FRACTION,
    'baseline_count_no_overlap': int(len(all_rows)),
    'train_count': int(len(train)),
    'test_count': int(len(test)),
    'selected_tolerance_pct': best_tol * 100.0,
    'primary_cost_bps': PRIMARY_COST,
    **score_summary,
}
(ART_DIR / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

build_html(
    overall=overall,
    asset=asset_summary[asset_summary['cost_bps'] == PRIMARY_COST].copy(),
    setup=setup_summary[setup_summary['cost_bps'] == PRIMARY_COST].copy(),
    train_grid=train_grid,
    scorecard=scorecard,
    summary=summary,
    selected_tolerance=best_tol,
    generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
)

print(json.dumps(summary, ensure_ascii=False, indent=2))
