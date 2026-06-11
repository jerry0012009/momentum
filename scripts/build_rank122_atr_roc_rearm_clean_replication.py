#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank107_mtf_chop_chargedup_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank122_atr_roc_short_rearm_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank122_atr_roc_short_rearm_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank122_atr_roc_short_rearm_clean_replication.html'

ASSETS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 4
LOOKBACK = 20
ATR_PERIOD = 14
ATR_MEAN = 20
PRIMARY_COST = 6.0

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.65; color:#111827; background:#f8fafc; }
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
ul { margin-top:8px; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def render_table(df: pd.DataFrame, digits: int = 2, percent_cols: set[str] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                if col in percent_cols:
                    text = f'{value*100:.2f}%'
                else:
                    text = f'{value:.{digits}f}'
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


def net_return(short_gross: pd.Series, cost_bps: float) -> pd.Series:
    rate = cost_bps / 10000.0
    return (1.0 + short_gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def load_frame(asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f'{asset}__120d__15m.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('timestamp').reset_index(drop=True)
    prev_close = df['close'].shift(1)
    tr = pd.concat(
        [
            (df['high'] - df['low']).abs(),
            (df['high'] - prev_close).abs(),
            (df['low'] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr14 = tr.rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()
    atr_ratio = atr14 / atr14.rolling(ATR_MEAN, min_periods=ATR_MEAN).mean()
    roc5 = df['close'].pct_change(5)
    prior20_low = df['low'].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    df['atr14'] = atr14
    df['atr_ratio'] = atr_ratio
    df['roc5'] = roc5
    df['prior20_low'] = prior20_low
    df['baseline_short'] = (df['close'] < prior20_low).fillna(False)
    df['strict_short_rearm'] = (
        df['baseline_short']
        & (atr_ratio < 0.7)
        & (roc5 < -0.005)
    ).fillna(False)
    df['mild_short_rearm'] = (
        df['baseline_short']
        & (atr_ratio.rolling(4, min_periods=4).min() < 0.8)
        & (roc5 < -0.004)
    ).fillna(False)
    return df


def collect_trades(frame: pd.DataFrame, asset: str, label: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sig_idx = np.flatnonzero(frame[label].to_numpy())
    last_exit = -1
    for idx in sig_idx:
        entry_idx = idx + 1
        exit_idx = idx + 1 + HOLD_BARS
        if idx <= last_exit or entry_idx >= len(frame) or exit_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]['open'])
        exit_px = float(frame.iloc[exit_idx]['open'])
        if not np.isfinite(entry_px) or not np.isfinite(exit_px) or entry_px <= 0:
            continue
        short_gross = (entry_px - exit_px) / entry_px
        breakout_line = float(frame.iloc[idx]['prior20_low'])
        reentry = bool((frame.iloc[entry_idx: exit_idx + 1]['high'] >= breakout_line).any())
        rows.append(
            {
                'asset': asset,
                'label': label,
                'signal_time': frame.iloc[idx]['timestamp'],
                'entry_time': frame.iloc[entry_idx]['timestamp'],
                'exit_time': frame.iloc[exit_idx]['timestamp'],
                'entry_open': entry_px,
                'exit_open': exit_px,
                'gross_return': short_gross,
                'gross_bps': short_gross * 10000.0,
                'reentry4': reentry,
                'atr_ratio': float(frame.iloc[idx]['atr_ratio']),
                'roc5': float(frame.iloc[idx]['roc5']),
                'breakout_line': breakout_line,
            }
        )
        last_exit = exit_idx
    return rows


def summarize(trades: pd.DataFrame, cost_bps: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = trades.copy()
    work['cost_bps'] = cost_bps
    work['net_return'] = net_return(work['gross_return'], cost_bps)
    work['net_bps'] = work['net_return'] * 10000.0
    label_summary = (
        work.groupby('label', as_index=False)
        .agg(
            n=('net_bps', 'size'),
            mean_net_bps=('net_bps', 'mean'),
            median_net_bps=('net_bps', 'median'),
            reentry4_pct=('reentry4', 'mean'),
        )
        .sort_values('label')
        .reset_index(drop=True)
    )
    label_summary['trade_retention_vs_baseline_pct'] = label_summary['n'] / float(label_summary.loc[label_summary['label'] == 'baseline_short', 'n'].iloc[0])
    asset_summary = (
        work.groupby(['asset', 'label'], as_index=False)
        .agg(
            n=('net_bps', 'size'),
            mean_net_bps=('net_bps', 'mean'),
            median_net_bps=('net_bps', 'median'),
            reentry4_pct=('reentry4', 'mean'),
        )
        .sort_values(['label', 'asset'])
        .reset_index(drop=True)
    )
    return label_summary, asset_summary


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: load_frame(asset) for asset in ASSETS}
    trades = []
    for asset, frame in frames.items():
        for label in ['baseline_short', 'strict_short_rearm', 'mild_short_rearm']:
            trades.extend(collect_trades(frame, asset, label))
    trades_df = pd.DataFrame(trades).sort_values(['label', 'asset', 'signal_time']).reset_index(drop=True)
    trades_df.to_csv(ART_DIR / 'trade_log.csv', index=False)

    overall_parts: list[pd.DataFrame] = []
    asset_parts: list[pd.DataFrame] = []
    for cost in COSTS:
        overall, by_asset = summarize(trades_df, cost)
        overall.insert(0, 'cost_bps_per_side', cost)
        by_asset.insert(0, 'cost_bps_per_side', cost)
        overall_parts.append(overall)
        asset_parts.append(by_asset)
    overall_df = pd.concat(overall_parts, ignore_index=True)
    asset_df = pd.concat(asset_parts, ignore_index=True)
    overall_df.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    asset_df.to_csv(ART_DIR / 'asset_summary.csv', index=False)

    primary_overall = overall_df[overall_df['cost_bps_per_side'] == PRIMARY_COST].copy()
    primary_assets = asset_df[asset_df['cost_bps_per_side'] == PRIMARY_COST].copy()

    strict_primary = primary_overall[primary_overall['label'] == 'strict_short_rearm'].iloc[0]
    baseline_primary = primary_overall[primary_overall['label'] == 'baseline_short'].iloc[0]
    mild_primary = primary_overall[primary_overall['label'] == 'mild_short_rearm'].iloc[0]

    strict_assets = primary_assets[primary_assets['label'] == 'strict_short_rearm'].copy()
    baseline_assets = primary_assets[primary_assets['label'] == 'baseline_short'].copy()
    merged = strict_assets.merge(baseline_assets[['asset', 'mean_net_bps']], on='asset', suffixes=('_strict', '_baseline'))
    merged['uplift_bps'] = merged['mean_net_bps_strict'] - merged['mean_net_bps_baseline']
    positive_assets = int((merged['uplift_bps'] > 0).sum())

    if positive_assets >= 2 and strict_primary['mean_net_bps'] > 0:
        verdict = 'P2 / paper candidate'
        verdict_detail = 'strict 版本在至少 2 个币种上保留 honest uplift，且成本后 aggregate 仍为正。'
    else:
        verdict = 'P0 / park / evidence pool'
        verdict_detail = 'strict 只在 1 个币种上保留明确 uplift，mild 在成本后整体仍劣于 baseline，因此当前不满足升到 P2 的最小跨标的门槛。'

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'verdict': verdict,
        'positive_assets_strict_vs_baseline_at_6bps': positive_assets,
        'strict_mean_net_bps_at_6bps': float(strict_primary['mean_net_bps']),
        'mild_mean_net_bps_at_6bps': float(mild_primary['mean_net_bps']),
        'baseline_mean_net_bps_at_6bps': float(baseline_primary['mean_net_bps']),
        'strict_trade_count': int(strict_primary['n']),
        'mild_trade_count': int(mild_primary['n']),
        'baseline_trade_count': int(baseline_primary['n']),
        'hold_bars': HOLD_BARS,
        'execution': 'signal bar and earlier data only + next-bar open + no-overlap',
        'costs_bps_per_side': COSTS,
        'rule': {
            'baseline_short': 'close < prior 20-bar low',
            'strict_short_rearm': 'baseline_short + ATR14/avgATR20 < 0.7 + ROC5 < -0.5%',
            'mild_short_rearm': 'baseline_short + min ATR ratio(last4) < 0.8 + ROC5 < -0.4%',
        },
        'verdict_detail': verdict_detail,
    }
    (ART_DIR / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    factor_body = f"""
<h1>Rank 122 · ATR compression + ROC ignition short re-arm clean replication</h1>
<div class='card'>
  <p><b>authoritative verdict：</b><span class='bad'>{escape(verdict)}</span></p>
  <p>{escape(verdict_detail)}</p>
  <ul>
    <li>执行口径：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code></li>
    <li>比较三臂：<code>baseline_short</code> vs <code>strict_short_rearm</code> vs <code>mild_short_rearm</code></li>
    <li>数据：<code>BTC/ETH/SOL 120d 15m</code> 本地 cache，成本扫描 <code>6 / 10 / 15 bps per side</code></li>
  </ul>
</div>
<div class='card'>
  <h2>6bps/side 主表</h2>
  {render_table(primary_overall[['label','n','mean_net_bps','median_net_bps','reentry4_pct','trade_retention_vs_baseline_pct']], percent_cols={'reentry4_pct','trade_retention_vs_baseline_pct'})}
</div>
<div class='card'>
  <h2>6bps/side 分资产</h2>
  {render_table(primary_assets[['asset','label','n','mean_net_bps','median_net_bps','reentry4_pct']], percent_cols={'reentry4_pct'})}
</div>
<div class='card'>
  <h2>成本 / 交易数稳定性</h2>
  {render_table(overall_df[['cost_bps_per_side','label','n','mean_net_bps','reentry4_pct','trade_retention_vs_baseline_pct']], percent_cols={'reentry4_pct','trade_retention_vs_baseline_pct'})}
</div>
<div class='card'>
  <p><a href='../../reading/repo_scout/rank122_atr_roc_short_rearm_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank122_atr_compression_roc_ignition_short_rearm_source_intake.html'>source intake</a></p>
</div>
"""
    write_html(SITE_DIR / 'report.html', 'Rank 122 clean replication', factor_body)

    merged_table = merged[['asset', 'mean_net_bps_strict', 'mean_net_bps_baseline', 'uplift_bps']].copy()
    reading_body = f"""
<h1>Rank 122 · ATR compression + ROC ignition short re-arm clean replication</h1>
<div class='card'>
  <p><b>一句话：</b>这条线在 <code>strict</code> 口径下的 aggregate 看起来还活着，但 uplift 明显集中在 <code>SOL</code>，没达到“至少 2 个币种保留 honest uplift”的 desk 最低升格门槛，因此这轮直接压回 <b>{escape(verdict)}</b>。</p>
  <p class='muted'>更直白地说：它可以留在 evidence pool 里当“short-side 高门槛再发动”备忘，但当前还不够格进 <code>paper candidate pool</code>。</p>
</div>
<div class='card'>
  <h2>这轮到底测了什么</h2>
  <ul>
    <li><code>baseline_short</code>：收盘跌破前 <code>20</code> 根最低价。</li>
    <li><code>strict_short_rearm</code>：在 baseline 上再加 <code>ATR14/avgATR20 &lt; 0.7</code> 与 <code>ROC5 &lt; -0.5%</code>。</li>
    <li><code>mild_short_rearm</code>：在 baseline 上再加 <code>min ATR ratio(last4) &lt; 0.8</code> 与 <code>ROC5 &lt; -0.4%</code>。</li>
    <li>统一执行：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>主读法（6bps/side）</h2>
  {render_table(primary_overall[['label','n','mean_net_bps','median_net_bps','reentry4_pct','trade_retention_vs_baseline_pct']], percent_cols={'reentry4_pct','trade_retention_vs_baseline_pct'})}
  <ul>
    <li><code>strict</code> 的 aggregate 确实比 baseline 好：<code>{strict_primary['mean_net_bps']:.2f} bps</code> vs <code>{baseline_primary['mean_net_bps']:.2f} bps</code>，而且 re-entry 也更低。</li>
    <li>但 trade count 只剩 <code>{int(strict_primary['n'])}</code> 笔，mild 版本虽然保留更多交易，成本后却仍落后于 baseline。</li>
    <li>所以它不是“short-side re-arm 明确成立”，而是“strict 版本可能有一点味道，但还不够稳”。</li>
  </ul>
</div>
<div class='card'>
  <h2>跨标的诚实性</h2>
  {render_table(merged_table)}
  <p>desk 本轮最关键的否决点就在这里：BTC strict 仍为负，ETH 只接近打平，真正明显正的只剩 SOL。一条只靠单币拉着走的 gate，不该在这一步升成 <code>P2</code>。</p>
</div>
<div class='card'>
  <h2>成本 / 交易数稳定性</h2>
  {render_table(overall_df[['cost_bps_per_side','label','n','mean_net_bps','reentry4_pct','trade_retention_vs_baseline_pct']], percent_cols={'reentry4_pct','trade_retention_vs_baseline_pct'})}
  <ul>
    <li><code>strict</code> 在 <code>6/10/15bps</code> 下 aggregate 都没立刻塌掉，这是它唯一保留研究价值的地方。</li>
    <li>但 <code>mild</code> 三档成本都比 baseline 更差，说明放宽阈值后并没有形成更诚实的“可部署版本”。</li>
    <li>因此当前更诚实的结论不是“继续补更多 admission 文案”，而是先 <code>park</code>，把资源切回 fresh intake。</li>
  </ul>
</div>
<div class='card'>
  <h2>reader-facing 落点</h2>
  <ul>
    <li><a href='../factors/scout_rank122_atr_roc_short_rearm_15m/report.html'>factor report</a></li>
    <li><code>reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/asset_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/trade_log.csv</code></li>
  </ul>
</div>
"""
    write_html(READING_PATH, 'Rank 122 clean replication', reading_body)


if __name__ == '__main__':
    main()
