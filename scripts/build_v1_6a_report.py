#!/usr/bin/env python3
"""Build v1.6a Momentum Ignition backtest report."""
from pathlib import Path
import html
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone

ROOT = Path('/root/clawd/jerry/momentum')
ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a'
OOS_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_oos'
POST_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_post_event'
RT_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay'
SS_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze'
SLIP_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_slippage_sensitivity'
AUDIT_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_audit'
SENS_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_v4_ret_sensitivity'
OUT = ROOT / 'reports/site/paper/binance_event_study_v1_6a_momentum_ignition_report.html'

res = pd.read_csv(ART / 'param_scan_results.csv')
ft = pd.read_csv(ART / 'factor_analysis_trades.csv')

# Full-history / full-universe anti-bias validation.
# This is intentionally separate from the event-window scan because it answers:
# "Does V4 work when we do NOT preselect known top-gainer event windows?"
oos_summary_path = OOS_ART / 'summary_full_universe.json'
oos = json.loads(oos_summary_path.read_text(encoding='utf-8')) if oos_summary_path.exists() else None

# Post-event and causal real-time overlay explorations.
post_v4_path = POST_ART / 'v4_summary_by_window.csv'
post_v4 = pd.read_csv(post_v4_path) if post_v4_path.exists() else pd.DataFrame()
if not post_v4.empty:
    post_v4['window_label'] = post_v4['window'].map({
        'pre_control_h-20_0': '事件日前/早期 h=-20~0（控制口径，含未来事件偏差）',
        'event_day_h0_16': '事件日内 h=0~16（盘中已出现事件）',
        'event_day_late_h8_24': '事件日后半段 h=8~24（盘中/尾盘跟随）',
        'strict_after_daily_close_h24_48': '日线确认后 h=24~48（严格无未来）',
        'strict_after_daily_close_h24_72': '日线确认后 h=24~72（严格无未来）',
        'strict_late_h48_120': '更晚 h=48~120（严格无未来）',
    }).fillna(post_v4['window'])
rt_summary_path = RT_ART / 'realtime_event_overlay_summary.csv'
rt_sum = pd.read_csv(rt_summary_path) if rt_summary_path.exists() else pd.DataFrame()
if not rt_sum.empty:
    rt_sum['rule_desc'] = rt_sum.apply(lambda r: f"rank≤{int(r.rank_max)} · 24h涨幅≥{r.ret24_min*100:.0f}% · 24h成交额≥${r.vol24_min/1e6:.0f}m", axis=1)
    rt_sum['lag_desc'] = rt_sum['lag_window'].map({
        'same_hour_0': '同小时', 'after_1_4h': '事件后1~4h', 'after_1_8h': '事件后1~8h',
        'after_1_24h': '事件后1~24h', 'after_4_24h': '事件后4~24h', 'after_8_24h': '事件后8~24h',
        'after_24_48h': '事件后24~48h'
    }).fillna(rt_sum['lag_window'])
    rt_main = rt_sum[rt_sum['rule'].eq('rank20_ret10_vol5m')].copy()
    rt_top = rt_sum[rt_sum['n'] >= 100].sort_values('net4_mean', ascending=False).head(12).copy()
else:
    rt_main = pd.DataFrame(); rt_top = pd.DataFrame()

# Extreme second-squeeze follow-up: narrow right-tail diagnostics after causal extreme events.
ss_summary_path = SS_ART / 'second_squeeze_summary.csv'
ss_cost_path = SS_ART / 'second_squeeze_cost_curve.csv'
ss_year_path = SS_ART / 'second_squeeze_by_year.csv'
ss_strata_path = SS_ART / 'second_squeeze_strata.csv'
ss_counts_path = SS_ART / 'second_squeeze_event_counts.csv'
ss_summary = pd.read_csv(ss_summary_path) if ss_summary_path.exists() else pd.DataFrame()
ss_cost = pd.read_csv(ss_cost_path) if ss_cost_path.exists() else pd.DataFrame()
ss_year = pd.read_csv(ss_year_path) if ss_year_path.exists() else pd.DataFrame()
ss_strata = pd.read_csv(ss_strata_path) if ss_strata_path.exists() else pd.DataFrame()
ss_counts = pd.read_csv(ss_counts_path) if ss_counts_path.exists() else pd.DataFrame()
if not ss_summary.empty:
    ss_summary['lag_desc'] = ss_summary['lag_window'].map({
        'after_1_4h': '事件后1~4h', 'after_1_8h': '事件后1~8h', 'after_1_24h': '事件后1~24h',
        'after_4_24h': '事件后4~24h', 'after_8_24h': '事件后8~24h', 'after_24_48h': '事件后24~48h',
    }).fillna(ss_summary['lag_window'])
    ss_summary['mode_desc'] = ss_summary['mode'].map({'all_signals': '所有V4信号', 'first_signal_per_event': '每事件首个V4'}).fillna(ss_summary['mode'])
    ss_summary['rule_desc'] = ss_summary['rule'].map({
        'rank20_ret20_vol5m': '精确：rank≤20 · 24h涨幅≥20% · vol≥$5m',
        'rank20_ret30_vol5m': '精确：rank≤20 · 24h涨幅≥30% · vol≥$5m',
        'derived_rank10_ret30_vol5m': '派生：rank≤10 · 24h涨幅≥30% · vol≥$5m',
        'derived_rank20_ret40_vol5m': '派生：rank≤20 · 24h涨幅≥40% · vol≥$5m',
        'derived_rank20_ret50_vol5m': '派生：rank≤20 · 24h涨幅≥50% · vol≥$5m',
        'derived_rank20_ret30_vol20m': '派生：rank≤20 · 24h涨幅≥30% · vol≥$20m',
        'derived_rank20_ret30_vol50m': '派生：rank≤20 · 24h涨幅≥30% · vol≥$50m',
    }).fillna(ss_summary['rule'])
    ss_main = ss_summary[(ss_summary['rule'].eq('rank20_ret30_vol5m')) & (ss_summary['lag_window'].isin(['after_4_24h','after_8_24h','after_24_48h']))].copy()
    ss_top_first = ss_summary[(ss_summary['mode'].eq('first_signal_per_event')) & (ss_summary['n'] >= 100)].sort_values(['net4_mean','net4_drop_top1pct_mean'], ascending=False).head(12).copy()
else:
    ss_main = pd.DataFrame(); ss_top_first = pd.DataFrame()
if not ss_cost.empty:
    ss_cost['lag_desc'] = ss_cost['lag_window'].map({'after_8_24h':'事件后8~24h','after_24_48h':'事件后24~48h'}).fillna(ss_cost['lag_window'])
    ss_cost_main = ss_cost[(ss_cost['rule'].eq('rank20_ret30_vol5m')) & (ss_cost['mode'].eq('first_signal_per_event')) & (ss_cost['lag_window'].isin(['after_8_24h','after_24_48h']))].copy()
else:
    ss_cost_main = pd.DataFrame()
if not ss_year.empty:
    ss_year_main = ss_year[(ss_year['rule'].eq('rank20_ret30_vol5m')) & (ss_year['mode'].eq('first_signal_per_event')) & (ss_year['lag_window'].isin(['after_8_24h','after_24_48h']))].copy()
    ss_year_main['lag_desc'] = ss_year_main['lag_window'].map({'after_8_24h':'事件后8~24h','after_24_48h':'事件后24~48h'}).fillna(ss_year_main['lag_window'])
else:
    ss_year_main = pd.DataFrame()
if not ss_strata.empty:
    ss_strata_main = ss_strata[(ss_strata['rule'].eq('rank20_ret30_vol5m')) & (ss_strata['lag_window'].isin(['after_8_24h','after_24_48h'])) & (ss_strata['strata_type'].isin(['funding_bucket','btc_regime','event_ret24_bucket']))].copy()
    ss_strata_main['lag_desc'] = ss_strata_main['lag_window'].map({'after_8_24h':'事件后8~24h','after_24_48h':'事件后24~48h'}).fillna(ss_strata_main['lag_window'])
else:
    ss_strata_main = pd.DataFrame()

# Trailing-stop / slippage follow-up and full-universe event audit.
slip_combo_path = SLIP_ART / 'trail_slippage_combos.csv'
slip_year_path = SLIP_ART / 'yearly_stability.csv'
slip_bucket_path = SLIP_ART / 'ret_bucket_breakdown.csv'
slip_summary_path = SLIP_ART / 'summary.json'
slip_combo = pd.read_csv(slip_combo_path) if slip_combo_path.exists() else pd.DataFrame()
slip_year = pd.read_csv(slip_year_path) if slip_year_path.exists() else pd.DataFrame()
slip_bucket = pd.read_csv(slip_bucket_path) if slip_bucket_path.exists() else pd.DataFrame()
slip_summary = json.loads(slip_summary_path.read_text(encoding='utf-8')) if slip_summary_path.exists() else {}

q1_audit_path = AUDIT_ART / 'q1_universe_audit.json'
q2_audit_path = AUDIT_ART / 'q2_v4_trailing_stop.json'
q1_audit = json.loads(q1_audit_path.read_text(encoding='utf-8')) if q1_audit_path.exists() else {}
q2_audit = json.loads(q2_audit_path.read_text(encoding='utf-8')) if q2_audit_path.exists() else {}

sens_summary_path = SENS_ART / 'v4_ret_threshold_summary.csv'
sens_year_path = SENS_ART / 'v4_ret_threshold_yearly.csv'
sens_summary = pd.read_csv(sens_summary_path) if sens_summary_path.exists() else pd.DataFrame()
sens_year = pd.read_csv(sens_year_path) if sens_year_path.exists() else pd.DataFrame()

COST = 0.0013

def pct(x, d=2, signed=True):
    if pd.isna(x): return '—'
    return (f'{x*100:+.{d}f}%' if signed else f'{x*100:.{d}f}%')

def num(x, d=0):
    if pd.isna(x): return '—'
    return f'{x:,.{d}f}' if d else f'{int(round(x)):,}'

def cls_val(x):
    if pd.isna(x): return ''
    return 'pos' if x > 0 else ('neg' if x < 0 else '')

def td(v, fmt=None, cls=None):
    s = fmt(v) if fmt else str(v)
    c = f' class="{cls}"' if cls else ''
    return f'<td{c}>{s}</td>'

def render_df(df, cols, labels=None, formats=None, classes=None, max_rows=None):
    labels = labels or {c:c for c in cols}
    formats = formats or {}
    classes = classes or {}
    if max_rows:
        df = df.head(max_rows)
    out = '<table><thead><tr>' + ''.join(f'<th>{html.escape(labels.get(c,c))}</th>' for c in cols) + '</tr></thead><tbody>'
    for _, r in df.iterrows():
        out += '<tr>'
        for c in cols:
            val = r.get(c, np.nan)
            f = formats.get(c)
            s = f(val) if f else (html.escape(str(val)) if not pd.isna(val) else '—')
            klass = classes.get(c)
            if callable(klass): klass = klass(val)
            out += f'<td class="{klass}">{s}</td>' if klass else f'<td>{s}</td>'
        out += '</tr>'
    out += '</tbody></table>'
    return out

def row_from_dict(label, d, *, med_digits=2):
    return (
        f'<tr><td>{label}</td>'
        f'<td>{num(d.get("n", np.nan))}</td>'
        f'<td class="{cls_val(d.get("mean", np.nan))}">{pct(d.get("mean", np.nan))}</td>'
        f'<td class="{cls_val(d.get("med", np.nan))}">{pct(d.get("med", np.nan), med_digits)}</td>'
        f'<td>{pct(d.get("wr", np.nan), 1, False)}</td>'
        f'<td>{d.get("pf", np.nan):.2f}</td></tr>'
    )

def render_v4_ret_sensitivity_subsection():
    if sens_summary.empty:
        return '<h3 id="v4ret">10.5 V4 1h涨幅阈值敏感性：artifact missing</h3>'

    base = sens_summary[sens_summary['slippage_bps'].eq(0)].copy()
    stress = sens_summary[sens_summary['slippage_bps'].eq(30)].copy()
    base['threshold_show'] = base['threshold_label'].map(lambda x: f'{x}（当前）' if x == '1.0%' else x)
    stress['threshold_show'] = stress['threshold_label'].map(lambda x: f'{x}（当前）' if x == '1.0%' else x)

    yearly_score = pd.DataFrame()
    if not sens_year.empty:
        yearly_score = sens_year.groupby(['threshold', 'threshold_label'], as_index=False).agg(
            years=('year', 'nunique'),
            positive_years=('median', lambda x: int((x > 0).sum())),
            worst_year_median=('median', 'min'),
            best_year_median=('median', 'max'),
            min_year_n=('n', 'min'),
        )
        yearly_score['threshold_show'] = yearly_score['threshold_label'].map(lambda x: f'{x}（当前）' if x == '1.0%' else x)

    yearly_html = (
        render_df(
            yearly_score,
            ['threshold_show','years','positive_years','worst_year_median','best_year_median','min_year_n'],
            labels={'threshold_show':'1h涨幅阈值','years':'覆盖年份','positive_years':'正中位数年份','worst_year_median':'最差年度中位','best_year_median':'最好年度中位','min_year_n':'最少年样本'},
            formats={'years':num,'positive_years':num,'worst_year_median':pct,'best_year_median':pct,'min_year_n':num},
            classes={'worst_year_median':cls_val,'best_year_median':cls_val},
        )
        if not yearly_score.empty else '<p>yearly artifact missing.</p>'
    )

    return f'''
<h3 id="v4ret">10.5 V4 1h涨幅阈值敏感性：1% 是否太低</h3>
<p>这里专门固定其他条件，只扫 <code>ret_1h</code> 阈值：事件仍为 <code>rank≤20 + 24h涨幅≥30% + 24h成交额≥$5m</code>，量能仍为 <code>vol_ratio≥3x</code>，入场仍取每个事件后的首个 V4 信号，退出仍为 <code>trail 2%</code>、最长 48h。成本口径与第 10 节一致：基础结果已扣 13bps 往返成本；30bps 表示再额外扣单边 30bps、往返 60bps。</p>
<p class="small">为和 Phase2a 历史回测严格可比，本节使用旧回测 V4 定义：<code>ret_1h = close-to-close pct_change</code>，<code>vol_ratio = 当前小时 quote volume / rolling20 均值</code>（均值包含当前小时）。Paper/shadow 页面会另外透明记录实盘口径的 previous-20 与 close/open 差异。</p>

<h4>基础成本下的阈值扫描</h4>
{render_df(base, ['threshold_show','n','events_with_trade','symbols','mean','median','winrate','pf','p5','p95','avg_lag_hours','avg_ret_1h','avg_vol_ratio'], labels={'threshold_show':'1h涨幅阈值','n':'交易数','events_with_trade':'事件数','symbols':'symbol数','mean':'均值','median':'中位数','winrate':'胜率','pf':'PF','p5':'P5','p95':'P95','avg_lag_hours':'平均滞后h','avg_ret_1h':'真实信号均值','avg_vol_ratio':'量能倍数均值'}, formats={'n':num,'events_with_trade':num,'symbols':num,'mean':pct,'median':pct,'winrate':lambda x:pct(x,1,False),'pf':lambda x:f'{x:.2f}','p5':pct,'p95':pct,'avg_lag_hours':lambda x:f'{x:.1f}','avg_ret_1h':pct,'avg_vol_ratio':lambda x:f'{x:.2f}x'}, classes={'mean':cls_val,'median':cls_val,'p5':cls_val,'p95':cls_val})}

<h4>30bps 单边滑点压力</h4>
{render_df(stress, ['threshold_show','n','mean','median','winrate','pf','p5','p95'], labels={'threshold_show':'1h涨幅阈值','n':'交易数','mean':'均值','median':'中位数','winrate':'胜率','pf':'PF','p5':'P5','p95':'P95'}, formats={'n':num,'mean':pct,'median':pct,'winrate':lambda x:pct(x,1,False),'pf':lambda x:f'{x:.2f}','p5':pct,'p95':pct}, classes={'mean':cls_val,'median':cls_val,'p5':cls_val,'p95':cls_val})}

<h4>年度稳定性摘要</h4>
{yearly_html}

<div class="note good"><b>回测结论：</b><code>1%</code> 不是脆弱单点。0.5%、1%、1.5%、2%、3%、5% 在基础成本和 30bps 单边滑点下全部保持正中位数，且 5/5 年年度中位数为正。说明“只要 1h 涨幅门槛稍微动一下策略就失效”的风险较低。</div>
<div class="note warn"><b>但 1% 偏宽，不是最优。</b>阈值越高，样本从 1,952 笔降到 1,468 笔，但中位数从 +1.43% 提高到 +2.09%，30bps 后也从 +0.83% 提高到 +1.49%。这说明真正有效的二次点火往往不是刚刚涨 1%，而是信号小时本身已经明显放量上冲。5% 是历史最优，但样本更少、选择更激进；更稳妥的实盘候选区间是 <code>2%~3%</code>。</div>
<div class="note"><b>参数选择建议：</b>Paper 阶段先保留 <code>1%</code> 作为与历史基准完全可比的主口径，同时在网页和日志里并行标记每笔信号是否也通过 <code>2%</code>、<code>3%</code>、<code>5%</code>。等 paper 累积真实滑点和成交质量后，再决定是否把执行阈值提高到 2% 或 3%。不要直接因为历史最优就切到 5%，那更容易变成尾部样本拟合。</div>
'''

def render_trailing_stop_section():
    if slip_combo.empty:
        return '<h2 id="trail">10. 移动止盈验证：artifact missing</h2>'

    trail_key_rows = slip_combo[
        (slip_combo['trail_label'].isin(['trail_1pct', 'trail_2pct', 'trail_3pct', 'trail_5pct'])) &
        (slip_combo['slippage_bps'].isin([0, 10, 30, 50]))
    ].copy()
    trail_key_rows['trail_name'] = trail_key_rows['trail_label'].map({
        'trail_1pct': 'trail 1%', 'trail_2pct': 'trail 2%', 'trail_3pct': 'trail 3%', 'trail_5pct': 'trail 5%',
    })
    trail_key_rows['slip_name'] = trail_key_rows['slippage_bps'].map(lambda x: f'{int(x)} bps')

    trail2_year = slip_year[(slip_year['trail_label'].eq('trail_2pct')) & (slip_year['slippage_bps'].isin([0, 30]))].copy()
    trail2_year['cost'] = trail2_year['slippage_bps'].map(lambda x: f'{int(x)} bps')
    trail2_bucket = slip_bucket[(slip_bucket['trail_label'].eq('trail_2pct')) & (slip_bucket['slippage_bps'].isin([0, 30]))].copy()
    trail2_bucket['cost'] = trail2_bucket['slippage_bps'].map(lambda x: f'{int(x)} bps')

    trail2_0 = slip_combo[(slip_combo['trail_label'].eq('trail_2pct')) & (slip_combo['slippage_bps'].eq(0))].iloc[0]
    trail2_30 = slip_combo[(slip_combo['trail_label'].eq('trail_2pct')) & (slip_combo['slippage_bps'].eq(30))].iloc[0]
    trail3_30 = slip_combo[(slip_combo['trail_label'].eq('trail_3pct')) & (slip_combo['slippage_bps'].eq(30))].iloc[0]

    best = slip_summary.get('best_config', {})
    return f'''
<h2 id="trail">10. 移动止盈验证：固定持仓的坏分布能否被修复</h2>
<div class="note good"><b>本节是对第 9 节的关键补丁：</b>固定 4h/8h 持仓下，事件+V4 看起来是“右尾有、但中位数差”；换成移动止盈后，收益分布被明显重塑。主配置 <code>事件 + V4 + trail 2%</code> 在 1,951 笔上，0bps 中位数 {pct(trail2_0['median'])}、PF {trail2_0['pf']:.2f}；30bps 单边滑点后仍有中位数 {pct(trail2_30['median'])}、PF {trail2_30['pf']:.2f}。</div>

<h3>10.1 为什么移动止盈改变结论</h3>
<p>固定持仓把所有交易强行拿满 4h/8h，等于让已经失败的二次点火继续暴露在均值回归和获利盘回吐里。移动止盈的作用不是“预测更准”，而是改变 payoff：价格一旦上冲就抬高止盈线，回落时退出；没有延续的交易更快离场。它把第 9 节的右尾结构保留下来，同时显著减少尾部回吐。</p>

<h3>10.2 参数与滑点矩阵（关键组合）</h3>
{render_df(trail_key_rows, ['trail_name','slip_name','n','mean','median','winrate','pf','p5','p95'], labels={'trail_name':'移动止盈','slip_name':'单边滑点','n':'样本','mean':'均值','median':'中位数','winrate':'胜率','pf':'PF','p5':'P5','p95':'P95'}, formats={'n':num,'mean':pct,'median':pct,'winrate':lambda x:pct(x,1,False),'pf':lambda x:f'{x:.2f}','p5':pct,'p95':pct}, classes={'mean':cls_val,'median':cls_val,'p5':cls_val,'p95':cls_val})}
<div class="note"><b>读法：</b>trail 1% 指标最好（best: {pct(best.get('mean', np.nan))} 均值 / {pct(best.get('median', np.nan))} 中位数 / PF {best.get('pf', np.nan):.2f}），但执行要求最苛刻。trail 2% 是更稳妥的折中：30bps 后仍是正中位数；trail 3% 在 30bps 时中位数转负但均值和 PF 仍为正；trail 5% 太宽，中位数基本被磨掉。</div>

<h3>10.3 trail 2% 年度稳定性</h3>
{render_df(trail2_year, ['year','cost','n','mean','median','winrate','pf'], labels={'year':'年份','cost':'单边滑点','n':'样本','mean':'均值','median':'中位数','winrate':'胜率','pf':'PF'}, formats={'n':num,'mean':pct,'median':pct,'winrate':lambda x:pct(x,1,False),'pf':lambda x:f'{x:.2f}'}, classes={'mean':cls_val,'median':cls_val})}
<p>这里比固定持仓版本更重要的是“中位数是否还能站住”。trail 2% 在 0bps 与 30bps 下都保持 5/5 年正中位数，说明结果不是单一年份的孤立爆点。</p>

<h3>10.4 事件强度分层</h3>
{render_df(trail2_bucket, ['ret_bucket','cost','n','mean','median','winrate','pf','p5','p95'], labels={'ret_bucket':'事件24h涨幅','cost':'单边滑点','n':'样本','mean':'均值','median':'中位数','winrate':'胜率','pf':'PF','p5':'P5','p95':'P95'}, formats={'n':num,'mean':pct,'median':pct,'winrate':lambda x:pct(x,1,False),'pf':lambda x:f'{x:.2f}','p5':pct,'p95':pct}, classes={'mean':cls_val,'median':cls_val,'p5':cls_val,'p95':cls_val})}
{render_v4_ret_sensitivity_subsection()}
<div class="note good"><b>更新后的 Phase 2a 判断：</b>不是“V4 全市场追涨可用”，而是 <b>实时极端事件 + V4 二次点火 + 2% 移动止盈</b> 可进入 paper lane 验证。核心监控不应只看均值，而要同时看实际滑点、持仓时间、单事件多次触发、以及 30bps 后中位数是否继续为正。</div>
'''

def render_audit_section():
    if not q1_audit or not q2_audit:
        return '<h2 id="audit">11. 宇宙审计：artifact missing</h2>'

    trail_rows = []
    for label, key in [
        ('4h固定（全市场 V4 基线）', 'v4_4h_fixed'),
        ('trail 0.5%', 'trail_0.5pct'),
        ('trail 1%', 'trail_1.0pct'),
        ('trail 2%', 'trail_2.0pct'),
        ('trail 3%', 'trail_3.0pct'),
        ('trail 5%', 'trail_5.0pct'),
    ]:
        if key in q2_audit:
            trail_rows.append(row_from_dict(label, q2_audit[key], med_digits=3 if key == 'trail_2.0pct' else 2))
    trail_table = '<table><thead><tr><th>配置</th><th>样本</th><th>均值</th><th>中位数</th><th>胜率</th><th>PF</th></tr></thead><tbody>' + ''.join(trail_rows) + '</tbody></table>'

    yearly_rows = []
    for year, d in q2_audit.get('trail_2pct_yearly', {}).items():
        yearly_rows.append(row_from_dict(year, d, med_digits=3))
    yearly_table = '<table><thead><tr><th>年份</th><th>样本</th><th>均值</th><th>中位数</th><th>胜率</th><th>PF</th></tr></thead><tbody>' + ''.join(yearly_rows) + '</tbody></table>'

    v4 = q2_audit['trail_2.0pct']
    event_trail2_0 = slip_combo[(slip_combo['trail_label'].eq('trail_2pct')) & (slip_combo['slippage_bps'].eq(0))].iloc[0] if not slip_combo.empty else None
    event_trail2_30 = slip_combo[(slip_combo['trail_label'].eq('trail_2pct')) & (slip_combo['slippage_bps'].eq(30))].iloc[0] if not slip_combo.empty else None
    event0_cells = (
        f'<td>{int(event_trail2_0["n"]):,}</td><td class="pos">{pct(event_trail2_0["mean"])}</td>'
        f'<td class="pos">{pct(event_trail2_0["median"])}</td><td>{pct(event_trail2_0["winrate"],1,False)}</td><td>{event_trail2_0["pf"]:.2f}</td>'
        if event_trail2_0 is not None else '<td colspan="5">missing</td>'
    )
    event30_cells = (
        f'<td>{int(event_trail2_30["n"]):,}</td><td class="pos">{pct(event_trail2_30["mean"])}</td>'
        f'<td class="pos">{pct(event_trail2_30["median"])}</td><td>{pct(event_trail2_30["winrate"],1,False)}</td><td>{event_trail2_30["pf"]:.2f}</td>'
        if event_trail2_30 is not None else '<td colspan="5">missing</td>'
    )
    event_median_phrase = pct(event_trail2_0["median"]) if event_trail2_0 is not None else '—'
    return f'''
<h2 id="audit">11. 宇宙审计：确认不是数据集偏差，也不是 V4 单独创造 alpha</h2>
<h3>11.1 事件检测一致性</h3>
<p>为了排除“只在 rank450 面板里找事件”的偏差，我从全量 Binance 1h 数据重新跑事件检测：<code>rank≤20</code>、<code>24h收益率≥30%</code>、<code>24h成交额≥$5M</code>、<code>24h cooldown</code>。</p>
<table><thead><tr><th>指标</th><th>现有事件叠加层</th><th>全量扫描</th><th>差异</th></tr></thead><tbody>
<tr><td>事件数</td><td>{q1_audit['existing']['events']:,}</td><td>{q1_audit['full_scan']['events']:,}</td><td>0</td></tr>
<tr><td>标的数</td><td>{q1_audit['existing']['symbols']:,}</td><td>{q1_audit['full_scan']['symbols']:,}</td><td>0</td></tr>
<tr><td>小时覆盖</td><td>—</td><td>{q1_audit['full_scan']['timestamps']:,}</td><td>—</td></tr>
<tr><td>逐条重叠</td><td colspan="3">{q1_audit['overlap']['n']:,} ({q1_audit['overlap']['pct']})；仅 1 条 XVGUSDT 出现 21:00/22:00 小时边界差异</td></tr>
</tbody></table>
<div class="note good"><b>审计结论：</b>事件叠加层就是从全量数据检测出来的，不存在 rank450 预筛选导致的事件遗漏。第 10 节的“事件上下文有效”不是数据集偏差造成的。</div>

<h3>11.2 V4 裸信号 + 移动止盈</h3>
<p>第二个问题是：如果完全不要事件上下文，只在全市场扫 V4，然后加移动止盈，是否也能赚钱？答案是能翻正，但中位数极薄。</p>
{trail_table}
{yearly_table}

<h3>11.3 事件上下文才是核心 alpha</h3>
<table><thead><tr><th>策略</th><th>样本</th><th>均值</th><th>中位数</th><th>胜率</th><th>PF</th></tr></thead><tbody>
<tr><td>V4 裸信号 + trail 2%</td><td>{v4['n']:,}</td><td class="pos">{pct(v4['mean'])}</td><td class="pos">{pct(v4['med'],3)}</td><td>{pct(v4['wr'],1,False)}</td><td>{v4['pf']:.2f}</td></tr>
<tr><td>事件 + V4 + trail 2% (0bps)</td>{event0_cells}</tr>
<tr><td>事件 + V4 + trail 2% (30bps)</td>{event30_cells}</tr>
</tbody></table>
<div class="note good"><b>最终读法：</b>移动止盈能把 V4 裸信号从固定持仓负期望修成正期望，但裸信号的 trail 2% 中位数只有 {pct(v4['med'],3)}，接近零。事件+V4 的 0bps 中位数达到 {event_median_phrase}，高一个数量级，说明 alpha 的主来源是“已经暴涨 30%+ 后再次点火”的条件概率优势；移动止盈主要负责把这个优势转化成可交易的收益分布。</div>
'''

# Top tables
top_net = res[res.n_trades >= 100].sort_values('net_mean', ascending=False).head(15).copy()
top_net['signal'] = top_net.apply(lambda r: f"vol>{r.vol_thresh:g}x · ret>{r.ret_thresh*100:.1f}% · w={int(r.vol_window)}h", axis=1)
top_net['funding_split'] = top_net.apply(lambda r: f"neg {pct(r.get('neg_fund_net',np.nan))} / pos {pct(r.get('pos_fund_net',np.nan))}", axis=1)

top_wr = res[res.n_trades >= 100].sort_values('win_rate', ascending=False).head(12).copy()
top_wr['signal'] = top_wr.apply(lambda r: f"vol>{r.vol_thresh:g}x · ret>{r.ret_thresh*100:.1f}% · w={int(r.vol_window)}h", axis=1)

stab = res[(res.vol_thresh==3.0)&(res.ret_thresh==0.01)&(res.vol_window==20)].sort_values('net_mean', ascending=False).copy()
stab['exit_desc'] = stab['exit_rule']

# Parameter stability pivots for selected exits
selected_exits = ['hold_4h','hold_8h','tp_10pct_8h','funding_flip']
pivot_tables = {}
for ex in selected_exits:
    sub = res[(res.exit_rule==ex)&(res.vol_window==20)].copy()
    piv = sub.pivot_table(index='ret_thresh', columns='vol_thresh', values='net_mean', aggfunc='mean')
    pivot_tables[ex] = piv

def render_pivot(piv):
    out = '<table><thead><tr><th>ret阈值 \\ vol阈值</th>'
    for c in piv.columns:
        out += f'<th>vol>{c:g}x</th>'
    out += '</tr></thead><tbody>'
    for idx, row in piv.iterrows():
        out += f'<tr><td>ret>{idx*100:.1f}%</td>'
        for c in piv.columns:
            v = row[c]
            out += f'<td class="{cls_val(v)}">{pct(v)}</td>'
        out += '</tr>'
    return out + '</tbody></table>'

# Factor correlation and quintiles
ft['net'] = ft['net_return'] if 'net_return' in ft.columns else ft['total_return'] - COST
features = ['vol_ratio','ret_at_signal','cumret_3h','cumret_6h','tbr_at_signal','funding_at_signal','trigger_hour','vol_at_signal']
factor_rows = []
for feat in features:
    corr = ft[feat].corr(ft['net'])
    lo, hi = ft[feat].quantile(0.01), ft[feat].quantile(0.99)
    q = pd.qcut(ft[feat].clip(lo,hi), 5, duplicates='drop')
    means = ft.groupby(q, observed=True)['net'].mean().tolist()
    wins = ft.groupby(q, observed=True)['net'].apply(lambda s: (s>0).mean()).tolist()
    factor_rows.append({
        'feature': feat,
        'corr': corr,
        'q1': means[0] if len(means)>0 else np.nan,
        'q2': means[1] if len(means)>1 else np.nan,
        'q3': means[2] if len(means)>2 else np.nan,
        'q4': means[3] if len(means)>3 else np.nan,
        'q5': means[4] if len(means)>4 else np.nan,
        'q5_win': wins[-1] if wins else np.nan,
    })
factor_df = pd.DataFrame(factor_rows)

# Combined score on factor trades
ft['fund_rank'] = ft['funding_at_signal'].rank(pct=True)  # lower is better for long carry
ft['vol_rank'] = ft['vol_ratio'].rank(pct=True)
ft['ret_rank'] = ft['ret_at_signal'].rank(pct=True)
ft['combo_score'] = (1-ft['fund_rank'])*0.4 + ft['vol_rank']*0.3 + ft['ret_rank']*0.3
ft['combo_q'] = pd.qcut(ft['combo_score'], 5, duplicates='drop')
combo = ft.groupby('combo_q', observed=True).agg(
    n=('net','size'), net=('net','mean'), win=('net', lambda s:(s>0).mean()),
    ret=('ret_at_signal','mean'), vol=('vol_ratio','mean'), fund=('funding_at_signal','mean')
).reset_index()
combo['bucket'] = [f'Q{i+1}' for i in range(len(combo))]

# Best combo/year/hour/funding pulled from top row
best = top_net.iloc[0]
by_year = []
for yr in range(2022, 2027):
    nk = f'yr{yr}_n'
    if nk in best and not pd.isna(best[nk]):
        by_year.append({'year': yr, 'n': best[nk], 'net': best[f'yr{yr}_net'], 'win': best[f'yr{yr}_win']})
by_year = pd.DataFrame(by_year)

hour_rows=[]
for lo,hi in [(-20,-12),(-12,-6),(-6,0),(0,4),(4,8),(8,12),(12,17)]:
    k=f'h{lo}_{hi}'
    if f'{k}_n' in best and not pd.isna(best[f'{k}_n']):
        hour_rows.append({'hour':f'h={lo:+d}~{hi:+d}', 'n':best[f'{k}_n'], 'net':best[f'{k}_net'], 'win':best[f'{k}_win']})
hour_df=pd.DataFrame(hour_rows)

# Verdict metrics
base = stab[stab.exit_rule=='hold_4h'].iloc[0]
base8 = stab[stab.exit_rule=='hold_8h'].iloc[0]
base_tp10 = stab[stab.exit_rule=='tp_10pct_8h'].iloc[0]
base_flip = stab[stab.exit_rule=='funding_flip'].iloc[0]

style = r'''
:root { --bg:#0b1220; --card:#111827; --card2:#0f172a; --border:#243044; --text:#e5e7eb; --muted:#94a3b8; --blue:#7dd3fc; --green:#4ade80; --red:#f87171; --yellow:#fbbf24; --purple:#c084fc; }
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font:15px/1.72 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif} .wrap{max-width:1180px;margin:0 auto;padding:28px 18px 64px} a{color:var(--blue);text-decoration:none} a:hover{text-decoration:underline} h1{font-size:1.8em;margin:0 0 8px} h2{margin:32px 0 12px;color:#cbd5e1;border-bottom:1px solid var(--border);padding-bottom:6px} h3{margin:22px 0 8px;color:var(--purple)} code{background:#020617;color:#fde68a;padding:2px 6px;border-radius:6px} .muted{color:var(--muted);font-size:13px}.hero{background:linear-gradient(135deg,#111827,#0f172a);border:1px solid #334155;border-radius:16px;padding:22px 26px;margin-bottom:20px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0 24px}.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:15px}.card .k{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}.card .v{font-size:22px;font-weight:800;margin-top:4px}.card.good .v{color:var(--green)}.card.warn .v{color:var(--yellow)}.card.bad .v{color:var(--red)}.note{border-left:4px solid var(--blue);background:#1e3a5f22;padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0}.note.good{border-left-color:#22c55e;background:#14532d22}.note.warn{border-left-color:#f59e0b;background:#78350f22}.note.bad{border-left-color:#ef4444;background:#7f1d1d22} table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin:12px 0 22px}th,td{padding:8px 10px;border-bottom:1px solid var(--border);font-size:13px;text-align:right;vertical-align:top}th{background:var(--card2);color:#cbd5e1;white-space:nowrap}td:first-child,th:first-child{text-align:left}tr:last-child td{border-bottom:0}.pos{color:var(--green);font-weight:700}.neg{color:var(--red);font-weight:700}.toc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 18px}.toc ol{margin:6px 0 0;padding-left:24px}.small{font-size:13px;color:var(--muted)}.tag{display:inline-block;border:1px solid #334155;border-radius:999px;padding:2px 9px;margin:2px;color:#cbd5e1;background:#0f172a}.footer{margin-top:36px;padding-top:14px;border-top:1px solid var(--border);color:#64748b;font-size:12px}
'''

html_body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v1.6a 动量点火策略回测：量能爆发 + 价格突变</title><style>{style}</style></head><body><div class="wrap">
<p class="muted"><a href="binance_event_study_hub.html">← 回到 Binance 事件研究统一入口</a></p>
<div class="hero"><h1>v1.6a 动量点火策略回测：量能爆发 + 价格突变</h1><p class="muted">扫描 h=-20 到 h=+16 的小时线，寻找“成交量突然放大 + 当前小时上涨”的爆发点。Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p></div>

<div class="grid">
<div class="card good"><div class="k">核心基准信号</div><div class="v">{pct(base.net_mean)}</div><div class="muted">vol&gt;3x · ret&gt;1% · 4h fixed · n={num(base.n_trades)}</div></div>
<div class="card good"><div class="k">8h 固定持有</div><div class="v">{pct(base8.net_mean)}</div><div class="muted">同一信号，hold 8h，胜率 {pct(base8.win_rate,1,False)}</div></div>
<div class="card warn"><div class="k">最高均值组合</div><div class="v">{pct(best.net_mean)}</div><div class="muted">vol&gt;7x · ret&gt;5% · funding flip · n={num(best.n_trades)}</div></div>
<div class="card good"><div class="k">最佳组合中的负 funding 子集</div><div class="v">{pct(best.neg_fund_net)}</div><div class="muted">n={num(best.neg_fund_n)}，胜率 {pct(best.neg_fund_win,1,False)}</div></div>
<div class="card bad"><div class="k">全市场完整小时验证</div><div class="v">{pct(oos['net_4h_mean']) if oos else '—'}</div><div class="muted">vol&gt;3x · ret&gt;1% · 4h · n={num(oos['n_trades']) if oos else '—'}</div></div>
</div>

<div class="toc"><b>目录</b><ol>
<li><a href="#verdict">结论先行</a></li>
<li><a href="#definition">策略定义：1.6a 是什么</a></li>
<li><a href="#scan">参数扫描结果</a></li>
<li><a href="#exit">退出规则比较</a></li>
<li><a href="#stability">参数稳定性</a></li>
<li><a href="#factor">哪些因子和胜率/收益有关</a></li>
<li><a href="#oos">反偏差验证：放进完整历史 1h 数据后还有效吗</a></li>
<li><a href="#postevent">追加探索：事件出现后再等 1h 量价齐涨，还有 alpha 吗</a></li>
<li><a href="#secondsqueeze">二次点火验证：极端事件后是否有可交易尾部</a></li>
<li><a href="#trail">移动止盈验证：固定持仓的坏分布能否被修复</a></li>
<li><a href="#v4ret">V4 1h涨幅阈值敏感性</a></li>
<li><a href="#audit">宇宙审计：确认不是数据集偏差</a></li>
<li><a href="#risk">风险、偏差与下一步</a></li>
<li><a href="#artifacts">产物索引</a></li>
</ol></div>

<h2 id="verdict">1. 结论先行</h2>
<div class="note bad"><b>更新后的核心结论：1.6a 不能作为全市场 standalone 策略。</b>在涨幅榜事件窗口里，核心基准 <code>vol&gt;3x + ret&gt;1% + trailing20h</code> 4h 固定持有净收益 {pct(base.net_mean)}，8h 固定持有 {pct(base8.net_mean)}；但放到完整 Binance 小时历史、全市场扫描后，4h 变成 {pct(oos['net_4h_mean']) if oos else '—'}，8h 变成 {pct(oos['net_8h_mean']) if oos else '—'}。这说明原结果高度依赖“已经处在涨幅榜事件上下文”的筛选。</div>
<div class="note warn"><b>更准确的定位：</b>1.6a 不是“看到量能爆发就追多”的通用 alpha，而可能只是一个 <b>事件内 timing filter</b>：当我们已经知道某个币进入异常事件/涨幅榜语境后，它可以帮助选择更好的小时级入场点。离开这个事件语境，信号本身不够强，扣 0.13% 往返成本后为负。</div>
<div class="note good"><b>Phase 2a 更新后的可交易形态：</b><code>实时极端事件(rank≤20, ret24≥30%, vol24≥$5m)</code> + <code>V4 二次点火</code> + <code>2% 移动止盈</code>。固定持仓下它只是右尾线索；加入移动止盈后，30bps 单边滑点下仍保持正中位数和健康 PF。因此结论不是“V4 被证明为通用 alpha”，而是“事件上下文 + 出场结构”共同成立。</div>
<p>我的建议从 <b>NO-GO standalone</b> 调整为：<b>standalone 继续 NO-GO；Phase 2a 事件内版本可进入 paper lane 验证</b>。下一步重点不是继续调 V4 阈值，而是验证实盘滑点、信号延迟、同事件多次触发和移动止盈执行质量。</p>

<h2 id="definition">2. 策略定义：1.6a 是什么</h2>
<p><b>交易对象：</b>v1.5 涨幅榜事件对应的 Binance U 本位永续合约小时线 panel，共 31,370 个有效事件。</p>
<p><b>扫描窗口：</b>每个事件从 <code>h=-20</code> 到 <code>h=+16</code> 逐小时扫描。这里的 h=0 是事件日 00:00 UTC，不是价格真正开始涨的时刻，所以必须向前扫。</p>
<p><b>入场信号：</b></p>
<ul>
<li><code>vol_ratio = 当前小时成交额 / 过去 N 小时平均成交额</code>，测试 N=12 和 N=20。</li>
<li><code>ret_1h = 当前小时 close / 上一小时 close - 1</code>，测试阈值 0.5%、1%、2%、3%、5%。这是历史 Phase2a 回测口径；paper/shadow 实盘页会单独记录 close/open 的实盘可执行口径。</li>
<li>当 <code>vol_ratio &gt; 阈值</code> 且 <code>ret_1h &gt; 阈值</code>，认为发生“动量点火”。</li>
<li>同一事件内信号去重：4 小时内不重复触发。</li>
</ul>
<p><b>成本假设：</b>每笔交易扣 0.13% 往返成本 = 2 × 0.04% taker fee + 0.05% 滑点。这个成本对妖币可能偏乐观，后续要做更高滑点测试。</p>

<h2 id="scan">3. 参数扫描结果</h2>
<p>本次扫描：5 个成交量阈值 × 5 个价格阈值 × 2 个 trailing window × 18 个退出规则 = <b>{num(len(res))}</b> 组组合。</p>
<h3>按净收益排序的前 15 组</h3>
{render_df(top_net, ['signal','exit_rule','n_trades','net_mean','win_rate','profit_factor','funding_split'], labels={'signal':'信号参数','exit_rule':'退出规则','n_trades':'交易数','net_mean':'平均净收益','win_rate':'胜率','profit_factor':'Profit Factor','funding_split':'Funding 分组'}, formats={'n_trades':num,'net_mean':pct,'win_rate':lambda x:pct(x,1,False),'profit_factor':lambda x:f'{x:.2f}'}, classes={'net_mean':cls_val})}
<div class="note warn">最高均值组合有明显的“尾部收益”特征：胜率只有 49.4%，但平均盈利远大于平均亏损。它赚钱不是靠稳定小胜，而是靠少数爆炸行情。</div>

<h3>按胜率排序的前 12 组</h3>
{render_df(top_wr, ['signal','exit_rule','n_trades','net_mean','win_rate','profit_factor'], labels={'signal':'信号参数','exit_rule':'退出规则','n_trades':'交易数','net_mean':'平均净收益','win_rate':'胜率','profit_factor':'Profit Factor'}, formats={'n_trades':num,'net_mean':pct,'win_rate':lambda x:pct(x,1,False),'profit_factor':lambda x:f'{x:.2f}'}, classes={'net_mean':cls_val})}
<div class="note">高胜率基本来自 <code>tp_2pct_8h</code>：很快止盈 2%，胜率 75%~78%，但平均收益只有 0.1%~0.7%。这类规则适合降低心理压力，但会砍掉妖币尾部。</div>

<h2 id="exit">4. 退出规则比较：固定持有、止盈止损、Funding flip</h2>
<p>下面固定信号为 <code>vol&gt;3x + ret&gt;1% + trailing20h</code>，只比较退出规则。</p>
{render_df(stab, ['exit_desc','n_trades','net_mean','win_rate','profit_factor','sharpe','pct_sl','pct_tp','pct_max_hold'], labels={'exit_desc':'退出规则','n_trades':'交易数','net_mean':'平均净收益','win_rate':'胜率','profit_factor':'PF','sharpe':'Sharpe*','pct_sl':'止损触发','pct_tp':'止盈触发','pct_max_hold':'到期退出'}, formats={'n_trades':num,'net_mean':pct,'win_rate':lambda x:pct(x,1,False),'profit_factor':lambda x:f'{x:.2f}','sharpe':lambda x:f'{x:.2f}','pct_sl':lambda x:pct(x,1,False),'pct_tp':lambda x:pct(x,1,False),'pct_max_hold':lambda x:pct(x,1,False)}, classes={'net_mean':cls_val}, max_rows=18)}
<p class="small">* Sharpe 只用于内部比较，不建议当成真实年化可交易 Sharpe。</p>
<div class="note good"><b>退出规则的直觉：</b>8h 固定持有和 TP10 都明显好于 1h/2h，说明这个信号不是“只吃下一根 K 线”，而是有 4~8 小时的延续性。TP2 胜率高，但削弱收益；严格止损会明显降低胜率，说明妖币正常波动很大，过窄止损会被洗掉。</div>

<h2 id="stability">5. 参数稳定性</h2>
<p>下面只看 trailing20h，不同 vol/ret 阈值下的平均净收益。绿色越多，说明不是单点过拟合。</p>
<h3>固定持有 4h</h3>{render_pivot(pivot_tables['hold_4h'])}
<h3>固定持有 8h</h3>{render_pivot(pivot_tables['hold_8h'])}
<h3>TP10 + 最多 8h</h3>{render_pivot(pivot_tables['tp_10pct_8h'])}
<h3>Funding flip</h3>{render_pivot(pivot_tables['funding_flip'])}
<div class="note good"><b>稳定性观察：</b>收益随 ret 阈值提高通常上升，尤其 ret&gt;3%/5% 的妖币点火更强。vol 阈值提高也有帮助，但不如 ret 阈值稳定。换句话说：<b>价格冲击幅度比成交量倍数更重要</b>，成交量是“确认有资金进场”，价格冲击是“资金真的打穿盘口”。</div>

<h2 id="factor">6. 哪些因子和收益有关？</h2>
<p>使用中等信号 <code>vol&gt;3x + ret&gt;1% + trailing20h + hold4h</code>，共 {num(len(ft))} 笔交易，计算信号发生时可见因子与后续净收益的关系。</p>
{render_df(factor_df, ['feature','corr','q1','q2','q3','q4','q5','q5_win'], labels={'feature':'因子','corr':'相关','q1':'Q1净收益','q2':'Q2','q3':'Q3','q4':'Q4','q5':'Q5净收益','q5_win':'Q5胜率'}, formats={'corr':lambda x:f'{x:+.4f}','q1':pct,'q2':pct,'q3':pct,'q4':pct,'q5':pct,'q5_win':lambda x:pct(x,1,False)}, classes={'q1':cls_val,'q2':cls_val,'q3':cls_val,'q4':cls_val,'q5':cls_val})}
<div class="note good"><b>最有用的三个优化方向：</b><ol><li><b>funding_at_signal 越低越好</b>：相关 -0.115，是所有因子里最强。负 funding 代表空头付费，做多不但收 carry，还可能遇到 squeeze。</li><li><b>ret_at_signal 越强越好</b>：Q1 +0.63%，Q5 +2.14%。这支持你的判断：0.5% 太温和，妖币真正点火通常更猛烈。</li><li><b>cumret_3h / cumret_6h 有帮助</b>：说明单小时爆发之外，前面几小时的连续动量也有信息。</li></ol></div>

<h3>组合评分：funding + vol + ret</h3>
<p>构造一个简单组合分：<code>0.4 × 负funding排名 + 0.3 × vol_ratio排名 + 0.3 × ret_at_signal排名</code>。</p>
{render_df(combo, ['bucket','n','net','win','ret','vol','fund'], labels={'bucket':'组合分组','n':'交易数','net':'平均净收益','win':'胜率','ret':'信号小时涨幅','vol':'vol_ratio','fund':'funding'}, formats={'n':num,'net':pct,'win':lambda x:pct(x,1,False),'ret':pct,'vol':lambda x:f'{x:.2f}x','fund':pct}, classes={'net':cls_val,'fund':cls_val})}
<div class="note good">组合评分从 Q1 到 Q5 的收益提升比较干净：Q1 +0.81% → Q5 +2.11%。这说明 1.6a 后续有优化空间，不是只有一个硬阈值。</div>

<h2 id="oos">7. 反偏差验证：放进完整历史 1h 数据后还有效吗</h2>
<div class="note bad"><b>答案：作为全市场扫描信号，不有效。</b>这次验证专门针对 Jerry 提出的核心风险：原始 panel 来自涨幅榜/跌幅榜事件，本身可能已经知道“未来会暴涨”，所以在这个 panel 上回测会偏乐观。我们把同一套 V4 信号放进更完整的小时历史里重跑，收益直接从正变负。</div>

<h3>验证设计</h3>
<ul>
<li><b>原始事件窗口：</b>v1.6a 只扫描涨幅榜事件前后 <code>h=-20~+16</code> 的小时线。</li>
<li><b>完整历史重测：</b>不再使用事件窗口；对 Binance USDT 永续/历史合约的完整 1h K 线逐小时扫描。</li>
<li><b>全市场 universe：</b>当前 Binance USDT 永续 + 本地 funding archive 出现过的历史合约 + 已缓存 kline 合约，并集共 699 个 symbol；最终 686 个 symbol 有足够 kline 可回测。</li>
<li><b>信号保持不变：</b><code>vol_ratio &gt; 3x</code> 且 <code>ret_1h &gt; 1%</code>，trailing volume window = 20h，4h 内不重复触发。</li>
<li><b>成本保持不变：</b>每笔扣 0.13% 往返成本，和原 1.6a 一致。</li>
</ul>

<table><thead><tr><th>测试口径</th><th>Universe / 样本</th><th>4h 平均净收益</th><th>4h 胜率</th><th>8h 平均净收益</th><th>8h 胜率</th><th>解读</th></tr></thead><tbody>
<tr><td>原 v1.6a 事件窗口</td><td>涨幅榜事件 panel，n=12,831</td><td class="pos">{pct(base.net_mean)}</td><td>{pct(base.win_rate,1,False)}</td><td class="pos">{pct(base8.net_mean)}</td><td>{pct(base8.win_rate,1,False)}</td><td>看起来有明显延续性</td></tr>
<tr><td>完整历史全市场扫描</td><td>{num(oos['n_symbols']) if oos else '—'} 个 symbol，n={num(oos['n_trades']) if oos else '—'}</td><td class="neg">{pct(oos['net_4h_mean']) if oos else '—'}</td><td>{pct(oos['net_4h_winrate'],1,False) if oos else '—'}</td><td class="neg">{pct(oos['net_8h_mean']) if oos else '—'}</td><td>{pct(oos['net_8h_winrate'],1,False) if oos else '—'}</td><td>离开事件筛选后 alpha 消失并转负</td></tr>
<tr><td>收益衰减</td><td>完整历史 − 事件窗口</td><td class="neg">{pct(oos['alpha_decay_4h']) if oos else '—'}</td><td>—</td><td class="neg">{pct(oos['alpha_decay_8h']) if oos else '—'}</td><td>—</td><td>不是轻微衰减，是结构性坍塌</td></tr>
</tbody></table>

<h3>年度分解：不是某一年偶然拖累</h3>
<table><thead><tr><th>年份</th><th>交易数</th><th>4h 平均净收益</th><th>胜率</th><th>Profit Factor</th></tr></thead><tbody>
<tr><td>2022</td><td>8,398</td><td class="neg">-0.500%</td><td>37.5%</td><td>0.69</td></tr>
<tr><td>2023</td><td>13,804</td><td>+0.002%</td><td>43.6%</td><td>1.00</td></tr>
<tr><td>2024</td><td>18,075</td><td class="neg">-0.151%</td><td>43.5%</td><td>0.89</td></tr>
<tr><td>2025</td><td>33,634</td><td class="neg">-0.123%</td><td>41.7%</td><td>0.93</td></tr>
<tr><td>2026</td><td>15,598</td><td class="neg">-0.194%</td><td>40.2%</td><td>0.89</td></tr>
</tbody></table>

<div class="note bad"><b>反偏差结论：</b>原 1.6a 的收益主要来自“我们已经把样本限定在涨幅榜事件附近”这个上下文，而不是 <code>vol&gt;3x + ret&gt;1%</code> 本身拥有通用预测力。换成人话：在已经知道这里可能有妖币行情时，点火信号能帮忙挑入场时机；但如果把它扔到全市场所有小时里扫，它会追在大量普通噪音冲高后面，扣成本后亏钱。</div>

<div class="note warn"><b>保留价值：</b>不要把 1.6a 直接扔掉。它仍可作为“事件发现器之后的二级 timing filter”。但下一版必须先构造一个不带未来函数的实时事件触发器，例如：历史 TopN 流动性 universe 内的实时涨幅榜/成交额异常/负 funding squeeze 候选；然后只在这些事件候选里使用 1.6a。</div>


<h2 id="postevent">8. 追加探索：事件出现后再等 1h 量价齐涨，还有 alpha 吗</h2>
<div class="note bad"><b>更细的答案：</b>如果“事件出现”指<b>日线涨幅榜收盘确认后</b>，再等 <code>vol&gt;3x + ret&gt;1%</code> 去追多，整体还是失败；如果“事件出现”指<b>盘中已经被实时异动榜捕捉到</b>，事件 panel 内看起来还有 edge，但完整历史重建实时涨幅榜后，朴素版本仍不够强。</div>

<h3>8.1 在原事件 panel 内，把可交易窗口往后移</h3>
<p>固定 V4 信号 <code>vol&gt;3x + ret&gt;1% + trailing20h</code>，比较不同“事件后窗口”。这一步回答：不吃 h&lt;0 的提前窗口后，信号还剩多少。</p>
{render_df(post_v4, ['window_label','n','net4_mean','net4_median','net4_winrate','net4_pf','net8_mean','net8_median','net8_winrate','net8_pf'], labels={'window_label':'口径','n':'交易数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net8_mean':'8h均值','net8_median':'8h中位','net8_winrate':'8h胜率','net8_pf':'8h PF'}, formats={'n':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net8_mean':pct,'net8_median':pct,'net8_winrate':lambda x:pct(x,1,False),'net8_pf':lambda x:f'{x:.2f}'}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net8_mean':cls_val,'net8_median':cls_val}) if not post_v4.empty else '<p>post-event artifact missing.</p>'}
<div class="note"><b>读法：</b>事件日内 h=0~16 仍有 +1.02% / +1.51% 的 4h/8h 平均净收益；但严格等日线确认后 h=24~72，变成 -0.15% / -0.20%。这说明“日线榜单确认后再追”太晚，真正的信息主要在盘中爆发早段。</div>

<h3>8.2 用完整 1h 历史重建一个无未来函数的实时涨幅榜事件</h3>
<p>我又用完整 1h 历史做了一个更严格的 overlay：每个小时只用当时已完成 K 线，筛出 24h 涨幅榜 TopN + 成交额阈值事件；事件出现后，再要求 V4 量价点火才入场。</p>
{render_df(rt_main, ['lag_desc','n','net4_mean','net4_median','net4_winrate','net4_pf','net8_mean','net8_median','net8_winrate','net8_pf'], labels={'lag_desc':'V4 信号相对实时事件的滞后','n':'交易数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net8_mean':'8h均值','net8_median':'8h中位','net8_winrate':'8h胜率','net8_pf':'8h PF'}, formats={'n':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net8_mean':pct,'net8_median':pct,'net8_winrate':lambda x:pct(x,1,False),'net8_pf':lambda x:f'{x:.2f}'}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net8_mean':cls_val,'net8_median':cls_val}) if not rt_main.empty else '<p>realtime overlay artifact missing.</p>'}
<div class="note bad"><b>主规则结论：</b>实时事件定义为 <code>24h涨幅榜rank≤20 + 24h涨幅≥10% + 24h成交额≥$5m</code> 时，事件后 1~24h 的 V4 平均 4h 净收益为负，事件后 24~48h 也只有接近 0。朴素实时涨幅榜事件没有把 standalone V4 救回来。</div>

<h3>8.3 哪些实时事件组合看起来“勉强有戏”</h3>
{render_df(rt_top, ['rule_desc','lag_desc','n','net4_mean','net4_median','net4_winrate','net4_pf','net8_mean','net8_median','net8_winrate','net8_pf'], labels={'rule_desc':'实时事件规则','lag_desc':'滞后窗口','n':'交易数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net8_mean':'8h均值','net8_median':'8h中位','net8_winrate':'8h胜率','net8_pf':'8h PF'}, formats={'n':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net8_mean':pct,'net8_median':pct,'net8_winrate':lambda x:pct(x,1,False),'net8_pf':lambda x:f'{x:.2f}'}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net8_mean':cls_val,'net8_median':cls_val}) if not rt_top.empty else '<p>realtime overlay artifact missing.</p>'}
<div class="note warn"><b>唯一值得继续看的窄方向：</b><code>24h涨幅≥30%</code> 这种“极端事件”在事件后 8~48h 有小正均值，但中位数仍是负的、胜率只有 44% 左右，形态更像少数尾部大赚撑起来。它不能直接上 paper，只能作为 rank450 后续窄假设：极端 squeeze 事件 + 更强过滤（funding、流动性、BTC regime、每事件首信号）再测。</div>

<h2 id="secondsqueeze">9. 二次点火验证：极端事件后是否有可交易尾部</h2>
<div class="note warn"><b>本节回答固定持仓版本的问题：</b>如果实时极端事件已经出现，例如 <code>24h涨幅榜rank≤20 + 24h涨幅≥30% + 24h成交额≥$5m</code>，后面再等 V4 量价点火，是否有“二段 squeeze”的可交易尾部？固定 4h/8h 退出下，结论是：<b>有右尾，但中位数和年份稳定性不够；不能仅凭固定持仓版本上 paper。</b>第 10 节继续回答移动止盈能否修复这个分布。</div>

<h3>9.1 验证口径</h3>
<ul>
<li><b>事件：</b>复用完整 1h 历史上已经重建好的无未来函数实时事件。核心事件为 <code>rank≤20 + ret24≥30% + vol24≥$5m</code>，共 4,605 个事件、625 个 symbol。</li>
<li><b>入场：</b>事件发生后，再等全历史 V4 信号 <code>vol&gt;3x + ret_1h&gt;1% + trailing20h</code>。不允许使用事件前信号。</li>
<li><b>关键修正：</b>除了“所有 V4 信号”，还看 <b>每事件只取第一个 V4 信号</b>，避免同一个妖币事件连续多次触发把样本伪装成独立交易。</li>
<li><b>风险审计：</b>成本曲线、去掉 top 1%/5% 后收益、top trades 贡献、年份稳定性、funding/BTC regime/事件强度分层。</li>
</ul>
<div class="note">表中“派生”规则是从精确 <code>rank20_ret30_vol5m</code> 事件文件继续过滤出来的保守子集，不是重新做 cooldown/dedup 的新事件扫描；它们只用于鲁棒性诊断，主结论看“精确”规则。</div>

<h3>9.2 主规则：rank≤20 · 24h涨幅≥30% · vol≥$5m</h3>
{render_df(ss_main, ['lag_desc','mode_desc','n','symbols','events','net4_mean','net4_median','net4_winrate','net4_pf','net4_drop_top1pct_mean','net4_drop_top5pct_mean','top1_trade_contrib_sum4','top5_trade_contrib_sum4','net8_mean','net8_median','net8_winrate','net8_pf'], labels={'lag_desc':'V4滞后窗口','mode_desc':'信号口径','n':'交易数','symbols':'symbol数','events':'事件数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net4_drop_top1pct_mean':'去top1%后4h','net4_drop_top5pct_mean':'去top5%后4h','top1_trade_contrib_sum4':'top1贡献/总收益','top5_trade_contrib_sum4':'top5贡献/总收益','net8_mean':'8h均值','net8_median':'8h中位','net8_winrate':'8h胜率','net8_pf':'8h PF'}, formats={'n':num,'symbols':num,'events':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net4_drop_top1pct_mean':pct,'net4_drop_top5pct_mean':pct,'top1_trade_contrib_sum4':lambda x:f'{x:.2f}x','top5_trade_contrib_sum4':lambda x:f'{x:.2f}x','net8_mean':pct,'net8_median':pct,'net8_winrate':lambda x:pct(x,1,False),'net8_pf':lambda x:f'{x:.2f}'}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net4_drop_top1pct_mean':cls_val,'net4_drop_top5pct_mean':cls_val,'net8_mean':cls_val,'net8_median':cls_val}) if not ss_main.empty else '<p>second-squeeze artifact missing.</p>'}
<div class="note warn"><b>读法：</b>最像“二段 squeeze”的窗口是事件后 8~24h 和 24~48h。每事件首个 V4 在 8~24h 的 4h 均值为 +1.05%，8h 为 +1.16%；24~48h 的 4h 均值为 +0.73%，8h 为 +1.09%。但中位数仍是负的（约 -0.76%~-1.48%），胜率只有 43%~44%。这不是稳定胜率型 alpha，而是少数右尾大行情拉动均值。</div>
<div class="note bad"><b>最关键的坏消息：</b>去掉 top 1% 交易后，8~24h 的 4h 均值从 +1.05% 变成 -0.25%；去掉 top 5% 后变成 -1.92%。这说明收益高度依赖极少数妖币尾部。能不能交易，核心不在“均值为正”，而在你能否接受长期小亏、偶尔抓二段爆炸的 payoff。</div>

<h3>9.3 成本曲线：滑点一上来，尾部还剩多少</h3>
{render_df(ss_cost_main, ['lag_desc','cost','n','net4_mean','net4_winrate','net4_pf','net8_mean'], labels={'lag_desc':'窗口','cost':'往返成本','n':'交易数','net4_mean':'4h均值','net4_winrate':'4h胜率','net4_pf':'4h PF','net8_mean':'8h均值'}, formats={'cost':lambda x:pct(x,2,False),'n':num,'net4_mean':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net8_mean':pct}, classes={'net4_mean':cls_val,'net8_mean':cls_val}) if not ss_cost_main.empty else '<p>cost curve artifact missing.</p>'}
<div class="note warn"><b>成本结论：</b>8~24h 窗口在 100bps 往返成本后 4h 均值仍勉强 +0.18%，24~48h 在 100bps 后 4h 转为 -0.14%。这说明 gross tail 确实比较厚，但它不是“舒服的厚”：中位数负、胜率低、尾部集中。</div>

<h3>9.4 年份稳定性：不是每年都工作</h3>
{render_df(ss_year_main, ['lag_desc','year','n','symbols','events','net4','med4','wr4','net8','wr8'], labels={'lag_desc':'窗口','year':'年份','n':'交易数','symbols':'symbol数','events':'事件数','net4':'4h均值','med4':'4h中位','wr4':'4h胜率','net8':'8h均值','wr8':'8h胜率'}, formats={'n':num,'symbols':num,'events':num,'net4':pct,'med4':pct,'wr4':lambda x:pct(x,1,False),'net8':pct,'wr8':lambda x:pct(x,1,False)}, classes={'net4':cls_val,'med4':cls_val,'net8':cls_val}) if not ss_year_main.empty else '<p>year artifact missing.</p>'}
<div class="note warn"><b>稳定性结论：</b>8~24h 的收益明显依赖 2026，2023/2024 是负的；24~48h 在 2025 比较好，2022/2024 偏弱。它更像 regime/tail trade，不是跨年份稳定小 alpha。</div>

<h3>9.5 分层诊断：什么条件下二段更像真 squeeze</h3>
{render_df(ss_strata_main.sort_values(['strata_type','lag_desc','net4_mean'], ascending=[True,True,False]), ['lag_desc','strata_type','bucket','n','net4_mean','net4_median','net4_winrate','net4_pf','net8_mean'], labels={'lag_desc':'窗口','strata_type':'分层','bucket':'桶','n':'交易数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net8_mean':'8h均值'}, formats={'n':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net8_mean':pct}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net8_mean':cls_val}, max_rows=30) if not ss_strata_main.empty else '<p>strata artifact missing.</p>'}
<div class="note"><b>几个有用的线索：</b><ol><li>事件不是越极端越好：30%~40% 事件好于 40%~60%，已经过热的币反而更容易回吐。</li><li>rank1 不一定最好，rank2~10 通常更好；第一名往往已经太 crowded。</li><li>funding 在这次二段验证里不再呈现“负 funding 最好”，部分正 funding 桶反而更强，说明这里捕捉的是追涨尾部，不是 carry。</li><li>BTC 大涨时并不明显更好；部分窗口在 BTC 温和下跌/震荡时更强，可能是局部山寨 squeeze，而不是纯市场 beta。</li></ol></div>

<h3>9.6 鲁棒性候选：只看每事件首个 V4</h3>
{render_df(ss_top_first, ['rule_desc','lag_desc','n','symbols','events','net4_mean','net4_median','net4_winrate','net4_pf','net4_drop_top1pct_mean','net4_drop_top5pct_mean','net8_mean'], labels={'rule_desc':'事件规则','lag_desc':'窗口','n':'交易数','symbols':'symbol数','events':'事件数','net4_mean':'4h均值','net4_median':'4h中位','net4_winrate':'4h胜率','net4_pf':'4h PF','net4_drop_top1pct_mean':'去top1%后4h','net4_drop_top5pct_mean':'去top5%后4h','net8_mean':'8h均值'}, formats={'n':num,'symbols':num,'events':num,'net4_mean':pct,'net4_median':pct,'net4_winrate':lambda x:pct(x,1,False),'net4_pf':lambda x:f'{x:.2f}','net4_drop_top1pct_mean':pct,'net4_drop_top5pct_mean':pct,'net8_mean':pct}, classes={'net4_mean':cls_val,'net4_median':cls_val,'net4_drop_top1pct_mean':cls_val,'net4_drop_top5pct_mean':cls_val,'net8_mean':cls_val}) if not ss_top_first.empty else '<p>shortlist artifact missing.</p>'}
<div class="note warn"><b>固定持仓版本结论：WATCH，不是 GO。</b>极端事件后的二次点火确实存在“右尾”：成本承压能力比朴素实时涨幅榜强，8h 均值也有正数。但固定持仓没有达到可直接进入 paper lane 的标准，因为中位数为负、胜率低、收益依赖 top 1%/5%、年份不稳定。这个问题在第 10 节通过移动止盈重新评估。</div>
<div class="note"><b>如果继续研究，下一步不是继续调 V4 阈值，而是改交易结构：</b>每事件只允许一次入场；只做 rank2~10、ret24 30%~40% 的不过热事件；加盘口滑点代理；尝试更宽止损/时间退出/移动止盈；用小仓位 tail sleeve 的方式评估，而不是按普通高胜率策略评估。</div>

{render_trailing_stop_section()}

{render_audit_section()}

<h2 id="risk">12. 风险、偏差与下一步</h2>
<h3>关键风险</h3>
<ul>
<li><b>幸存者偏差：</b>当前 panel 只覆盖仍有数据的合约，退市妖币可能缺失，真实结果可能更差。</li>
<li><b>滑点偏乐观：</b>暴涨币追进去，实际滑点可能远高于 5bps。下一版必须做 10/20/50bps cost curve。</li>
<li><b>同事件多信号相关：</b>虽然 4h 去重，但同一事件可能多次触发，收益不是独立样本。</li>
<li><b>regime 依赖：</b>最强组合 2025/2026 表现远好于 2022-2024，可能依赖山寨币大行情。</li>
<li><b>Funding flip 规则有现实约束：</b>历史 funding 是结算数据，实时交易只能用预测 funding 或下一次 settlement 观察，不能假设提前知道未来 funding。</li>
</ul>

<h3>最高均值组合的年度稳定性</h3>
{render_df(by_year, ['year','n','net','win'], labels={'year':'年份','n':'交易数','net':'平均净收益','win':'胜率'}, formats={'n':num,'net':pct,'win':lambda x:pct(x,1,False)}, classes={'net':cls_val})}

<h3>最高均值组合按触发时间</h3>
{render_df(hour_df, ['hour','n','net','win'], labels={'hour':'触发时间','n':'交易数','net':'平均净收益','win':'胜率'}, formats={'n':num,'net':pct,'win':lambda x:pct(x,1,False)}, classes={'net':cls_val})}

<div class="note warn"><b>我的下一步建议：</b><ol><li><b>停止把 1.6a 当全市场追涨策略优化。</b>完整历史验证已经失败，继续调阈值大概率是在拟合噪音。</li><li><b>Phase 2a 只保留事件内版本：</b>事件发现器先给出极端上涨上下文，V4 只负责二次点火入场，移动止盈负责把右尾结构转成可交易分布。</li><li><b>paper lane 的验收重点：</b>实际滑点、信号延迟、每事件最多一次入场、trail 2% 是否能真实成交、30bps 后中位数是否继续为正。</li><li><b>风控定位：</b>它仍是小仓位 tail sleeve，不是高胜率常规动量策略；若实盘中位数快速回到零附近，应停止。</li></ol></div>

<h2 id="artifacts">13. 产物索引</h2>
<table><thead><tr><th>文件</th><th>用途</th></tr></thead><tbody>
<tr><td><code>scripts/backtest_v1_6a.py</code></td><td>1.6a 参数扫描与回测引擎</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a/param_scan_results.csv</code></td><td>900 组参数扫描结果</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a/factor_analysis_trades.csv</code></td><td>中等信号配置下的逐笔交易与因子数据</td></tr>
<tr><td><code>scripts/validate_v1_6a_on_full_data.py</code></td><td>完整历史/全市场反偏差验证脚本</td></tr>
<tr><td><code>scripts/download_full_binance_1h_universe.py</code></td><td>补齐 Binance USDT 永续历史 1h kline 的下载脚本</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_oos/summary_full_universe.json</code></td><td>全市场完整小时历史验证摘要</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_oos/full_universe_scan.log</code></td><td>全市场扫描日志与年度分解</td></tr>
<tr><td><code>scripts/explore_v1_6a_post_event_confirmation.py</code></td><td>事件出现后再等 V4 量价确认的窗口/参数探索</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_post_event/v4_summary_by_window.csv</code></td><td>V4 在事件日内、日线确认后等不同窗口的表现</td></tr>
<tr><td><code>scripts/explore_v1_6a_realtime_event_overlay.py</code></td><td>完整 1h 历史上的无未来函数实时涨幅榜事件 overlay</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay/realtime_event_overlay_summary.csv</code></td><td>实时事件 + V4 确认的规则/滞后窗口汇总</td></tr>
<tr><td><code>scripts/explore_v1_6a_extreme_second_squeeze.py</code></td><td>极端事件后二次点火 / 二段 squeeze 的尾部鲁棒性验证脚本</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze/second_squeeze_summary.csv</code></td><td>二次点火主汇总：均值/中位数/胜率/PF/去尾部后收益</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze/second_squeeze_cost_curve.csv</code></td><td>13/25/50/100bps 成本曲线</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze/second_squeeze_by_year.csv</code></td><td>年份稳定性分解</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze/second_squeeze_strata.csv</code></td><td>funding、BTC regime、事件强度分层</td></tr>
<tr><td><code>scripts/explore_v1_6a_slippage_sensitivity.py</code></td><td>事件+V4 移动止盈与滑点敏感性实验</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_slippage_sensitivity/trail_slippage_combos.csv</code></td><td>trail 1%-10% × 0-50bps 单边滑点矩阵</td></tr>
<tr><td><code>scripts/explore_v1_6a_v4_ret_sensitivity.py</code></td><td>V4 1h 涨幅阈值敏感性：0.5%-5% × trail 2%</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_v4_ret_sensitivity/v4_ret_threshold_summary.csv</code></td><td>1h 涨幅阈值扫描汇总与 30bps 压力测试</td></tr>
<tr><td><code>scripts/explore_v1_6a_universe_audit_and_v4_trail.py</code></td><td>全量事件检测审计 + V4 裸信号移动止盈对照</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_audit/q1_universe_audit.json</code></td><td>事件叠加层与全量扫描一致性审计</td></tr>
<tr><td><code>reports/artifacts/binance_event_study_v1_6a_audit/q2_v4_trailing_stop.json</code></td><td>V4 裸信号 + 移动止盈对照结果</td></tr>
<tr><td><code>reports/site/paper/binance_event_study_v1_6a_momentum_ignition_report.html</code></td><td>本报告</td></tr>
</tbody></table>
<div class="footer">v1.6a Momentum Ignition Report · built from hourly Binance event panel</div>
</div></body></html>'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html_body, encoding='utf-8')
print(f'Wrote {OUT} ({len(html_body):,} chars)')
print(f'URL: https://jp.jerrypsy.top/momentum/paper/{OUT.name}')
