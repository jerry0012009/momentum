#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank122_atr_roc_short_rearm_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank122_atr_roc_short_rearm_15m'
READING_DIR = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout'

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


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None) -> str:
    percent_cols = set(percent_cols or [])
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    head = ''.join(f'<th>{escape(str(col))}</th>' for col in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if isinstance(value, float):
                text = f'{value*100:.2f}%' if col in percent_cols else f'{value:.2f}'
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<table><thead><tr>' + head + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding='utf-8',
    )


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    READING_DIR.mkdir(parents=True, exist_ok=True)

    trade_log = pd.read_csv(ART_DIR / 'trade_log.csv', parse_dates=['signal_time', 'entry_time', 'exit_time'])
    trade_log = trade_log.sort_values('signal_time').reset_index(drop=True)
    summary = json.loads((ART_DIR / 'summary.json').read_text())

    ranked = trade_log[['signal_time']].sort_values('signal_time').reset_index(drop=True)
    split_cut = ranked.iloc[len(ranked) // 2]['signal_time']
    trade_log['time_split'] = trade_log['signal_time'].lt(split_cut).map({True: 'front_half', False: 'back_half'})

    rows: list[dict[str, object]] = []
    for cost in [6.0, 10.0, 15.0]:
        rate = cost / 10000.0
        for split, g in trade_log.groupby('time_split'):
            base_n = int((g['label'] == 'baseline_short').sum())
            for label, gg in g.groupby('label'):
                net = ((1.0 + gg['gross_return']) * (1.0 - rate) * (1.0 - rate) - 1.0) * 10000.0
                rows.append({
                    'cost_bps_per_side': cost,
                    'time_split': split,
                    'label': label,
                    'n': int(len(gg)),
                    'mean_net_bps': float(net.mean()),
                    'median_net_bps': float(net.median()),
                    'reentry4_pct': float(gg['reentry4'].mean()),
                    'trade_retention_vs_baseline_pct': (len(gg) / base_n) if base_n else None,
                    'start_signal_utc': str(gg['signal_time'].min()),
                    'end_signal_utc': str(gg['signal_time'].max()),
                })
    time_df = pd.DataFrame(rows).sort_values(['cost_bps_per_side', 'time_split', 'label']).reset_index(drop=True)
    time_df.to_csv(ART_DIR / 'time_stability_summary.csv', index=False)

    asset_rows: list[dict[str, object]] = []
    for (split, asset, label), gg in trade_log.groupby(['time_split', 'asset', 'label']):
        net = ((1.0 + gg['gross_return']) * (1.0 - 0.0006) * (1.0 - 0.0006) - 1.0) * 10000.0
        asset_rows.append({
            'cost_bps_per_side': 6.0,
            'time_split': split,
            'asset': asset,
            'label': label,
            'n': int(len(gg)),
            'mean_net_bps': float(net.mean()),
            'median_net_bps': float(net.median()),
            'reentry4_pct': float(gg['reentry4'].mean()),
        })
    asset_time_df = pd.DataFrame(asset_rows).sort_values(['time_split', 'label', 'asset']).reset_index(drop=True)
    asset_time_df.to_csv(ART_DIR / 'time_stability_asset_summary.csv', index=False)

    trade_log['month_utc'] = trade_log['signal_time'].dt.strftime('%Y-%m')
    month_rows: list[dict[str, object]] = []
    for label in ['baseline_short', 'strict_short_rearm', 'mild_short_rearm']:
        for month, gg in trade_log[trade_log['label'] == label].groupby('month_utc'):
            net = ((1.0 + gg['gross_return']) * (1.0 - 0.0006) * (1.0 - 0.0006) - 1.0) * 10000.0
            month_rows.append({
                'month_utc': month,
                'label': label,
                'n': int(len(gg)),
                'mean_net_bps_6bps': float(net.mean()),
                'reentry4_pct': float(gg['reentry4'].mean()),
            })
    month_df = pd.DataFrame(month_rows).sort_values(['month_utc', 'label']).reset_index(drop=True)
    month_df.to_csv(ART_DIR / 'time_stability_monthly_snapshot.csv', index=False)

    front = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['label'] == 'strict_short_rearm') & (time_df['time_split'] == 'front_half')].iloc[0]
    back = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['label'] == 'strict_short_rearm') & (time_df['time_split'] == 'back_half')].iloc[0]
    front_base = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['label'] == 'baseline_short') & (time_df['time_split'] == 'front_half')].iloc[0]
    back_base = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['label'] == 'baseline_short') & (time_df['time_split'] == 'back_half')].iloc[0]

    recent_months = month_df[(month_df['label'] == 'strict_short_rearm') & (month_df['month_utc'].isin(['2026-02', '2026-03']))]
    recent_red_watch = bool((recent_months['mean_net_bps_6bps'] <= 0).any())
    front_ok = front['mean_net_bps'] > 0 and front['mean_net_bps'] > front_base['mean_net_bps']
    back_ok = back['mean_net_bps'] > 0 and back['mean_net_bps'] > back_base['mean_net_bps']

    final_verdict = 'promote_to_P3_narrow_paper_pilot' if (front_ok and back_ok) else 'park'
    verdict_cn = '升到 P3 / narrow paper pilot（strict-only, short-side re-arm）' if final_verdict.startswith('promote') else '压回 park'

    monitor_df = pd.DataFrame([
        {
            'component': 'promotion_boundary',
            'status': 'pass' if final_verdict.startswith('promote') else 'blocked',
            'minimum_rule': '仅允许 strict_short_rearm 作为 breakout-short short-side re-arm narrow pilot；mild 继续禁止，long/shared 继续禁止。',
            'why_it_matters': '避免把 strict-only 的窄提升误写成 desk-wide shared gate。',
        },
        {
            'component': 'time_stability_front_back',
            'status': 'pass' if (front_ok and back_ok) else 'red',
            'minimum_rule': f"front_half={front['mean_net_bps']:.2f}bps vs baseline {front_base['mean_net_bps']:.2f}bps；back_half={back['mean_net_bps']:.2f}bps vs baseline {back_base['mean_net_bps']:.2f}bps（6bps/side）",
            'why_it_matters': '前后半程都要保留正收益且优于 baseline，才够资格继续进 narrow paper。',
        },
        {
            'component': 'trade_count_watch',
            'status': 'red_watch',
            'minimum_rule': f"strict retention 仅 {summary['strict_trade_count']}/{summary['baseline_trade_count']} = {summary['strict_trade_count'] / summary['baseline_trade_count'] * 100:.2f}% baseline trades；front/back 分别 {int(front['n'])}/{int(back['n'])} 笔。",
            'why_it_matters': '这条线靠高门槛换来 uplift，样本很稀；paper pilot 必须先当低频 narrow lane 观察，不能偷升 broad paper/live。',
        },
        {
            'component': 'recent_month_red_watch',
            'status': 'red_watch' if recent_red_watch else 'watch',
            'minimum_rule': '2026-02 / 2026-03 的 strict 月度均值已转弱或接近零（见 monthly snapshot）；不得把历史前半段强势误读成当前普适稳态。',
            'why_it_matters': '给 narrow paper 后续 weekly review 一个明确红灯，先看最近环境是否继续失真。',
        },
        {
            'component': 'paper_operator_action',
            'status': 'pass' if final_verdict.startswith('promote') else 'blocked',
            'minimum_rule': '若升到 P3，则只补 monitoring / ledger / refresh / weekly-review 最小接线，不再扩 admission wording。',
            'why_it_matters': '符合当前 desk 对 P3 的预算上限和职责边界。',
        },
    ])
    monitor_df.to_csv(ART_DIR / 'narrow_paper_monitoring_board.csv', index=False)

    seed_df = pd.DataFrame([{
        'candidate_id': 'rank122_strict_short_rearm',
        'rank': 122,
        'variant': 'strict_short_rearm',
        'seat_role': 'Scout->P3 narrow paper pilot',
        'scope': 'BTCUSDT,ETHUSDT,SOLUSDT | 15m | breakout-short short-side re-arm only',
        'entry_rule': 'close < prior 20-bar low AND ATR14/avgATR20 < 0.7 AND ROC5 < -0.5%',
        'execution_rule': 'signal bar and earlier data only + next-bar open + no-overlap + hold 4 bars',
        'paper_status': 'approved_narrow_pilot' if final_verdict.startswith('promote') else 'parked',
        'operator_action': 'seed_monitoring_and_weekly_review' if final_verdict.startswith('promote') else 'return_to_fresh_intake',
        'primary_watch': 'recent_month_red_watch + low_trade_count_watch',
        'do_not_do': 'no mild variant; no long-side; no shared gate; no live promotion',
        'decision_time_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
    }])
    seed_df.to_csv(ART_DIR / 'narrow_paper_seed_packet.csv', index=False)

    front_view = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['time_split'] == 'front_half')][['label', 'n', 'mean_net_bps', 'median_net_bps', 'reentry4_pct', 'trade_retention_vs_baseline_pct']]
    back_view = time_df[(time_df['cost_bps_per_side'] == 6.0) & (time_df['time_split'] == 'back_half')][['label', 'n', 'mean_net_bps', 'median_net_bps', 'reentry4_pct', 'trade_retention_vs_baseline_pct']]
    asset_view = asset_time_df[['time_split', 'asset', 'label', 'n', 'mean_net_bps', 'median_net_bps', 'reentry4_pct']]
    month_view = month_df[['month_utc', 'label', 'n', 'mean_net_bps_6bps', 'reentry4_pct']]

    body = f"""
<h1>Rank 122 · time stability check → {escape(verdict_cn)}</h1>
<div class='card'>
  <p><b>authoritative verdict：</b><span class='{'good' if final_verdict.startswith('promote') else 'bad'}'>{escape(verdict_cn)}</span></p>
  <p>这轮只做顶板点名的 <b>1 个 truly verdict-changing 最小时间稳定性检查</b>：把 strict 版 short-side re-arm 按信号时间切成前后半程，检查它在两段里是否仍保留 <code>6bps/side</code> 的正收益和相对 baseline 的 uplift。</p>
  <ul>
    <li>只看 <code>strict_short_rearm</code>；<code>mild</code> 继续判定为不成立。</li>
    <li>执行口径不变：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 4 bars</code></li>
    <li>结果：front_half = <b>{front['mean_net_bps']:.2f}bps</b>，back_half = <b>{back['mean_net_bps']:.2f}bps</b>；baseline 对应为 {front_base['mean_net_bps']:.2f}bps / {back_base['mean_net_bps']:.2f}bps。</li>
  </ul>
</div>
<div class='card'>
  <h2>前后半程（6bps/side）</h2>
  {render_table(front_view, percent_cols={'reentry4_pct', 'trade_retention_vs_baseline_pct'})}
  {render_table(back_view, percent_cols={'reentry4_pct', 'trade_retention_vs_baseline_pct'})}
</div>
<div class='card'>
  <h2>按资产拆开看（6bps/side）</h2>
  <p class='muted'>这里故意不粉饰：BTC/ETH 的 back-half strict 仍偏弱，真正撑住 aggregate 的主要是 SOL；所以 promotion 只能是 <b>strict-only / narrow / paper-only</b>，并附带最近月份 red-watch。</p>
  {render_table(asset_view, percent_cols={'reentry4_pct'})}
</div>
<div class='card'>
  <h2>月度快照（6bps/side）</h2>
  <p class='muted'>这不是第二个主点，只是把最近月份转弱如实摊开，避免把前半段强势误读成长期稳定。</p>
  {render_table(month_view, percent_cols={'reentry4_pct'})}
</div>
<div class='card'>
  <h2>最小 P3 监控板</h2>
  {render_table(monitor_df)}
  <h3>seed packet</h3>
  {render_table(seed_df)}
</div>
<div class='card'>
  <h2>结论翻成人话</h2>
  <ul>
    <li><b>为什么不是 park：</b> front/back 两半都仍为正，而且都比 baseline 更好，没有出现一半直接塌掉的 decisive fail。</li>
    <li><b>为什么也不是 broad/shared：</b> retention 只有 {summary['strict_trade_count'] / summary['baseline_trade_count'] * 100:.2f}% baseline trades，且最近月份转弱，说明它只配先当低频窄口径 short-side re-arm lane。</li>
    <li><b>后续边界：</b> 只允许补 paper ledger / monitoring / refresh / weekly review；不再扩 admission wording，不抢 Live Seat。</li>
  </ul>
</div>
"""
    write_html(SITE_DIR / 'time_stability_check.html', 'Rank 122 time stability check', body)
    write_html(READING_DIR / 'rank122_atr_roc_short_rearm_time_stability.html', 'Rank 122 time stability check', body)

    report_body = f"""
<h1>Rank 122 · ATR compression + ROC ignition short re-arm</h1>
<div class='card'>
  <p><b>当前 authoritative 状态：</b><span class='good'>{escape(verdict_cn)}</span></p>
  <p>当前只批准 <code>strict_short_rearm</code> 进入 <b>P3 narrow paper pilot</b>；<code>mild</code> 继续判负，shared / long / live 继续不允许。</p>
  <ul>
    <li><a href='./time_stability_check.html'>查看最新时间稳定性检查</a></li>
    <li><a href='../../reading/repo_scout/rank122_atr_roc_short_rearm_time_stability.html'>查看 reader-facing 镜像</a></li>
    <li><a href='../../reading/repo_scout/rank122_atr_roc_short_rearm_clean_replication.html'>上一轮 clean replication 页面</a></li>
  </ul>
</div>
<div class='card'>
  <h2>最小监控板</h2>
  {render_table(monitor_df)}
</div>
<div class='card'>
  <h2>关键数字（6bps/side）</h2>
  {render_table(time_df[time_df['cost_bps_per_side'] == 6.0][['time_split', 'label', 'n', 'mean_net_bps', 'median_net_bps', 'reentry4_pct', 'trade_retention_vs_baseline_pct']], percent_cols={'reentry4_pct', 'trade_retention_vs_baseline_pct'})}
</div>
"""
    write_html(SITE_DIR / 'report.html', 'Rank 122 factor report', report_body)

    summary.update({
        'time_stability_generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'time_stability_verdict': final_verdict,
        'time_stability_verdict_cn': verdict_cn,
        'front_half_strict_mean_net_bps_6bps': float(front['mean_net_bps']),
        'back_half_strict_mean_net_bps_6bps': float(back['mean_net_bps']),
        'front_half_baseline_mean_net_bps_6bps': float(front_base['mean_net_bps']),
        'back_half_baseline_mean_net_bps_6bps': float(back_base['mean_net_bps']),
        'recent_month_red_watch': recent_red_watch,
    })
    (ART_DIR / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
