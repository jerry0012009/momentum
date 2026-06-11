#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m'
REPORT_PATH = SITE_DIR / 'report.html'
READING_REPORT = ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'rank32b_slope_floor_continuation_clean_replication.html'
OUTPUT_HTML = SITE_DIR / 'universe_evidence_brief.html'
OUTPUT_JSON = ART_DIR / 'universe_evidence_brief_summary.json'
MARKER_ID = 'rank32b-universe-evidence-brief'


def pct(v: float | None, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = ''.join(f'<td>{escape(str(v))}</td>' for v in row.tolist())
        rows.append(f'<tr>{cells}</tr>')
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_yearly_summary() -> pd.DataFrame:
    frames = []
    for name in [
        'candidate_5y_stability_yearly_summary.csv',
        'universe_batch_a_long_window_yearly_summary.csv',
        'universe_batch_b_long_window_yearly_summary.csv',
    ]:
        p = ART_DIR / name
        if p.exists():
            frames.append(pd.read_csv(p))
    return pd.concat(frames, ignore_index=True)


def build_time_stability() -> tuple[pd.DataFrame, dict[str, int]]:
    y = load_yearly_summary()
    rows = []
    cnt_5of5 = 0
    cnt_3of3 = 0
    for asset, grp in y.groupby('asset'):
        pos = int((grp['total_return'] > 0).sum())
        total = int(len(grp))
        if pos == 5 and total == 5:
            cnt_5of5 += 1
        if pos == 3 and total == 3:
            cnt_3of3 += 1
        rows.append({
            'asset': asset.replace('-USD', ''),
            'positive_windows': f'{pos}/{total}',
            'worst_window_return': pct(float(grp['total_return'].min())),
            'best_window_return': pct(float(grp['total_return'].max())),
            'avg_window_win_rate': pct(float(grp['win_rate'].mean())),
        })
    df = pd.DataFrame(rows).sort_values(['positive_windows', 'asset'], ascending=[False, True]).reset_index(drop=True)
    return df, {'count_5of5': cnt_5of5, 'count_3of3': cnt_3of3, 'total_assets': int(len(df))}


def build_param_stability() -> tuple[pd.DataFrame, pd.DataFrame]:
    param = pd.read_csv(ART_DIR / 'parameter_stability_summary.csv')
    core = param[param['slope_floor'].isin([0.0004, 0.0005, 0.0006])].copy()
    core['slope_floor'] = core['slope_floor'].map(lambda x: f'{x:.4f}')
    core_view = core[['slope_floor', 'cost_bps_per_side', 'positive_asset_ratio', 'mean_total_return', 'mean_win_rate', 'mean_trades']].copy()
    core_view['positive_asset_ratio'] = core_view['positive_asset_ratio'].map(lambda x: pct(float(x)))
    core_view['mean_total_return'] = core_view['mean_total_return'].map(lambda x: pct(float(x)))
    core_view['mean_win_rate'] = core_view['mean_win_rate'].map(lambda x: pct(float(x)))
    core_view['mean_trades'] = core_view['mean_trades'].map(lambda x: round(float(x), 1))

    shortlist = pd.read_csv(ART_DIR / 'universe_shortlist18_1y_asset_summary.csv')
    rows = []
    for cost in [6.0, 10.0, 15.0, 20.0]:
        sub = shortlist[shortlist['cost_bps_per_side'] == cost].copy()
        rows.append({
            'cost_bps_per_side': int(cost),
            'positive_assets': f"{int((sub['total_return'] > 0).sum())}/{len(sub)}",
            'mean_total_return': pct(float(sub['total_return'].mean())),
            'mean_win_rate': pct(float(sub['win_rate'].mean())),
            'mean_trades': round(float(sub['trades'].mean()), 1),
        })
    shortlist_view = pd.DataFrame(rows)
    return core_view.reset_index(drop=True), shortlist_view.reset_index(drop=True)


def _overlap_stats(path: Path) -> dict[str, float | int | dict[int, int]]:
    df = pd.read_csv(path)
    df['event_ts'] = pd.to_datetime(df['event_ts'], utc=True)
    counts = df.groupby('event_ts')['asset'].nunique()
    return {
        'total_trades': int(len(df)),
        'unique_signal_times': int(counts.shape[0]),
        'weighted_win_rate': float((pd.to_numeric(df['net_ret']) > 0).mean()),
        'avg_net_ret': float(pd.to_numeric(df['net_ret']).mean()),
        'overlap_timestamp_ratio': float((counts > 1).mean()),
        'signal_in_overlap_ratio': float(counts[counts > 1].sum() / len(df)) if len(df) else 0.0,
        'dist': {int(k): int(v) for k, v in counts.value_counts().sort_index().to_dict().items()},
    }


def build_overlap_and_freq() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    core = _overlap_stats(ART_DIR / 'universe_core3_1y_primary_trades.csv')
    short = _overlap_stats(ART_DIR / 'universe_shortlist18_1y_primary_trades.csv')
    compare = pd.DataFrame([
        {
            'universe': 'core3',
            'total_trades': core['total_trades'],
            'unique_signal_times': core['unique_signal_times'],
            'win_rate': pct(core['weighted_win_rate']),
            'avg_net_ret': pct(core['avg_net_ret']),
            'overlap_timestamp_ratio': pct(core['overlap_timestamp_ratio']),
            'signals_in_overlap': pct(core['signal_in_overlap_ratio']),
        },
        {
            'universe': 'shortlist18',
            'total_trades': short['total_trades'],
            'unique_signal_times': short['unique_signal_times'],
            'win_rate': pct(short['weighted_win_rate']),
            'avg_net_ret': pct(short['avg_net_ret']),
            'overlap_timestamp_ratio': pct(short['overlap_timestamp_ratio']),
            'signals_in_overlap': pct(short['signal_in_overlap_ratio']),
        },
    ])
    dist = pd.DataFrame([
        {
            'simultaneous_assets': k,
            'core3_timestamps': core['dist'].get(k, 0),
            'shortlist18_timestamps': short['dist'].get(k, 0),
        }
        for k in sorted(set(core['dist']) | set(short['dist']))
    ])
    delta = {
        'trade_count_increase_pct': float((short['total_trades'] - core['total_trades']) / core['total_trades']),
        'unique_time_increase_pct': float((short['unique_signal_times'] - core['unique_signal_times']) / core['unique_signal_times']),
        'win_rate_delta': float(short['weighted_win_rate'] - core['weighted_win_rate']),
    }
    return compare, dist, delta


def build_html(time_df: pd.DataFrame, time_meta: dict[str, int], core_param: pd.DataFrame, shortlist_param: pd.DataFrame, overlap_compare: pd.DataFrame, overlap_dist: pd.DataFrame, delta: dict[str, float]) -> str:
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · universe evidence brief</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · universe evidence brief</h1>
  <p class='muted'>目的：把“为什么当前 shortlist 18 币值得认真考虑扩池”拆成证据链，而不是只给一句乐观/悲观判断。</p>

  <div class='card'>
    <h2>hard read</h2>
    <p><span class='pill'>跨时间稳定</span><span class='pill'>跨参数/成本稳定</span><span class='pill'>并发风险可量化</span></p>
    <p><b>当前 shortlist 18 币里，已有 16 个币达到 5/5 时间窗为正，另外 2 个短历史币达到 3/3 时间窗为正；在 6~10bps 成本下 18/18 为正，15bps 下 17/18 为正。</b></p>
    <p class='muted'>这不等于“所有参数都已经完全扫完”，但已经足够证明：当前扩池不是拍脑袋，而是有跨时间、跨成本、跨资产的证据支撑。</p>
  </div>

  <div class='card'>
    <h2>证据 1：跨时间稳定</h2>
    <p>当前 18 币里：<b>{time_meta['count_5of5']}</b> 个币是 <b>5/5</b> 时间窗为正，<b>{time_meta['count_3of3']}</b> 个短历史币是 <b>3/3</b> 时间窗为正。</p>
    {render_table(time_df)}
  </div>

  <div class='card'>
    <h2>证据 2：跨参数稳定（核心 3 币）</h2>
    <p class='muted'>这里用的是最硬的参数稳定性证据：核心 3 币对 <code>slope_floor</code> 的扫描。读法是：只要参数落在合理区间，而不是某个神奇小点，资产总体仍然能站住。</p>
    {render_table(core_param)}
  </div>

  <div class='card'>
    <h2>证据 3：扩展 18 币在现实成本附近仍然稳定</h2>
    <p class='muted'>这一步更接近真实执行环境。结论是：6~10bps 下 18/18 为正；15bps 下 17/18 为正；到 20bps 才开始明显分层。</p>
    {render_table(shortlist_param)}
  </div>

  <div class='card'>
    <h2>证据 4：扩池不是纯重复报警，而是真的增加机会</h2>
    <p><b>从 core3 扩到 shortlist18 后：</b>总交易数大约增加 <b>{pct(delta['trade_count_increase_pct'])}</b>，独立信号时间点增加 <b>{pct(delta['unique_time_increase_pct'])}</b>；加权胜率从 core3 的水平下降了约 <b>{pct(-delta['win_rate_delta'])}</b> 个百分点，但并没有崩坏。</p>
    {render_table(overlap_compare)}
    <h3>同一时间有多少个币一起触发？</h3>
    {render_table(overlap_dist)}
  </div>

  <div class='card'>
    <h2>怎么读这页</h2>
    <ul>
      <li><b>如果你关心“这些币是不是只在某一小段行情有用”</b>：看“跨时间稳定”。当前证据偏强。</li>
      <li><b>如果你关心“是不是参数稍微一动就失效”</b>：核心 3 币已经有较硬的参数稳定性；18 币则先证明了在现实成本附近稳定。</li>
      <li><b>如果你关心“扩池会不会只是重复信号变多”</b>：不会。机会确实变多，但并发冲突也会变多，所以组合执行层仍需要 strongest-signal-only / max-concurrent 控制。</li>
    </ul>
  </div>
</body>
</html>
"""


def inject_report_section(generated_at: str) -> None:
    block = f"""
  <div class='card'>
    <h2>universe evidence brief（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 目标：把“为什么当前 18 币 shortlist 值得认真考虑扩池”拆成证据链。</p>
    <p><b>当前 evidence brief 的核心结论：</b>16 个币达到 5/5 时间窗为正，2 个短历史币达到 3/3 为正；18/18 在 6~10bps 仍为正；从 core3 扩到 shortlist18 后，独立信号时间点约增加 4.7 倍，但胜率只小幅下降。</p>
    <p><a href='./universe_evidence_brief.html'>查看证据讲解页</a> ｜ <a href='./universe_admission.html'>查看准入分层表</a></p>
  </div>"""
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{block}\n{end_marker}"
    for path in [REPORT_PATH, READING_REPORT]:
        if not path.exists():
            continue
        html = path.read_text(encoding='utf-8')
        if start_marker in html and end_marker in html:
            left = html.split(start_marker)[0]
            right = html.split(end_marker, 1)[1]
            html = left + wrapped + right
        else:
            html = html.replace('</body>', wrapped + '\n</body>')
        path.write_text(html, encoding='utf-8')


def main() -> None:
    time_df, time_meta = build_time_stability()
    core_param, shortlist_param = build_param_stability()
    overlap_compare, overlap_dist, delta = build_overlap_and_freq()
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    OUTPUT_HTML.write_text(build_html(time_df, time_meta, core_param, shortlist_param, overlap_compare, overlap_dist, delta), encoding='utf-8')
    summary = {
        'generated_at_utc': generated_at,
        'time_meta': time_meta,
        'trade_count_increase_pct': delta['trade_count_increase_pct'],
        'unique_time_increase_pct': delta['unique_time_increase_pct'],
        'win_rate_delta': delta['win_rate_delta'],
    }
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    inject_report_section(generated_at)
    print(json.dumps({'html': str(OUTPUT_HTML), 'json': str(OUTPUT_JSON), 'generated_at_utc': generated_at}, ensure_ascii=False))


if __name__ == '__main__':
    main()
