#!/usr/bin/env python3
"""Build v1.6a deep stratification report page and append to existing HTML."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
REPORT_DIR = ROOT / 'reports/site/paper'
DS_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_deep_stratification'
HTML_FILE = REPORT_DIR / 'binance_event_study_v1_6a_momentum_ignition_report.html'


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def fmt_pct(v, dp=2):
    if pd.isna(v):
        return '—'
    return f'{v * 100:+.{dp}f}%'


def fmt_ratio(v, dp=2):
    if pd.isna(v):
        return '—'
    return f'{v:.{dp}f}'


def build_section() -> str:
    best = load_csv(DS_ART / 'best_candidates_25bps.csv')
    yearly = load_csv(DS_ART / 'yearly_stability.csv')
    yr_sum = load_csv(DS_ART / 'yearly_stability_summary.csv')
    verdict = json.loads((DS_ART / 'verdict.json').read_text()) if (DS_ART / 'verdict.json').exists() else {}

    # Two-way bests
    tw_rank_ret = load_csv(DS_ART / 'twoway_rank_bucket_x_ret_bucket_best_25bps.csv')
    tw_rank_fund = load_csv(DS_ART / 'twoway_rank_bucket_x_fund_bucket_best_25bps.csv')
    tw_ret_fund = load_csv(DS_ART / 'twoway_ret_bucket_x_fund_bucket_best_25bps.csv')

    # Cross-strata (for full table)
    cross_8_24 = load_csv(DS_ART / 'cross_strata_8_24h_25bps.csv')
    cross_24_48 = load_csv(DS_ART / 'cross_strata_24_48h_25bps.csv')

    parts = []

    # ── Header ──
    parts.append('''
    <section id="sec9">
    <h2>9. 深层交叉分层验证：寻找可交易子集</h2>
    <p class="section-subtitle">
      <strong>目标</strong>：在全量 Binance 1h 数据（无 rank450 筛选偏差）上，通过
      <code>rank分段 × 涨幅分段 × 资金费率分段</code> 三维交叉分层，
      找到"极端事件后二段拉升"最厚的窄子集。所有结果已扣除 25bps 滑点成本。
    </p>
    ''')

    # ── Verdict banner ──
    v = verdict.get('verdict', 'CLOSE')
    color = '#27ae60' if v == 'GO' else '#f39c12' if v == 'WATCH' else '#e74c3c'
    v_reasons = '<br>'.join(f'• {r}' for r in verdict.get('reasons', []))
    parts.append(f'''
    <div style="border:2px solid {color}; border-radius:8px; padding:16px; margin:16px 0; background:rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},0.05);">
      <h3 style="color:{color}; margin:0 0 8px 0;">综合评级：{v}</h3>
      <p style="margin:0; font-size:0.95em;">{v_reasons}</p>
    </div>
    ''')

    # ── 9.1 方法论 ──
    parts.append('''
    <h3>9.1 方法论：三维交叉分层</h3>
    <p>在全量 Binance 1h 数据上（2022-01 至 2026-04，683 symbols，89,509 条 V4 信号），对每条极端事件（rank≤20, ret24≥30%, vol24≥$5m, 无未来函数实时检测）后的首个 V4 信号，按三个维度交叉分桶：</p>
    <ul>
      <li><strong>rank 分段</strong>：rank1 / rank2-5 / rank6-10 / rank11-20</li>
      <li><strong>涨幅分段</strong>：&lt;30% / 30-40% / 40-60% / 60+% </li>
      <li><strong>资金费率分段</strong>：负费率 / near_zero(0-5bps) / 正5-20bps / 正&gt;20bps</li>
    </ul>
    <p>两个入场时机窗口：事件后 8-24h 和 24-48h。每个 cell 只取每事件首信号（去重复），扣除 25bps 成本后计算全指标。</p>
    ''')

    # ── 9.2 三维最佳子集 ──
    parts.append('<h3>9.2 三维最佳子集（25bps 成本后）</h3>')
    if not best.empty:
        rows_html = ''
        for _, r in best.iterrows():
            rk = r.get('rank_bucket', '?')
            rb = r.get('ret_bucket', '?')
            fb = r.get('fund_bucket', '?')
            w = r.get('window', '?')
            rows_html += f'''<tr>
              <td><strong>{rk} | {rb} | {fb}</strong></td>
              <td>{w}</td>
              <td>{int(r['n'])}</td>
              <td>{int(r['symbols'])}</td>
              <td>{fmt_pct(r['net4_mean'])}</td>
              <td>{fmt_pct(r['net4_median'])}</td>
              <td>{fmt_pct(r['net4_winrate'])}</td>
              <td>{fmt_ratio(r['net4_pf'])}</td>
              <td>{fmt_pct(r['net4_drop_top5pct'])}</td>
              <td>{fmt_pct(r['net8_mean'])}</td>
            </tr>\n'''
        parts.append(f'''
        <table class="data-table">
          <thead>
            <tr>
              <th>子集</th><th>窗口</th><th>n</th><th>币种</th>
              <th>4h均值</th><th>4h中位</th><th>胜率</th><th>PF</th>
              <th>去top5%均值</th><th>8h均值</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        ''')

    # ── 9.3 年度稳定性 ──
    parts.append('<h3>9.3 年度稳定性（25bps 成本后）</h3>')
    if not yearly.empty:
        # Group by candidate
        for cand, cg in yearly.groupby('candidate'):
            w = cg['window'].iloc[0]
            rows = ''
            for _, r in cg.iterrows():
                color = '#27ae60' if r['net4_mean'] > 0 else '#e74c3c'
                rows += f'''<tr>
                  <td>{int(r['year'])}</td>
                  <td>{int(r['n'])}</td>
                  <td style="color:{color}; font-weight:bold;">{fmt_pct(r['net4_mean'])}</td>
                  <td>{fmt_pct(r['net4_winrate'])}</td>
                  <td>{fmt_ratio(r['net4_pf'])}</td>
                </tr>\n'''
            # Summary
            s = yr_sum[yr_sum['candidate'] == cand]
            if not s.empty:
                s = s.iloc[0]
                yr_p = int(s['years_positive'])
                yr_t = int(s['years_total'])
                stable = '✅' if yr_p >= 3 else '⚠️' if yr_p >= 2 else '❌'
                summary_line = f'{stable} {yr_p}/{yr_t} 年正收益，跨年均值 {fmt_pct(s["mean_across_years"])}，最差年 {fmt_pct(s["min_year_mean"])}'
            else:
                summary_line = ''

            parts.append(f'''
            <h4>{cand} ({w}) — {summary_line}</h4>
            <table class="data-table" style="max-width:500px;">
              <thead><tr><th>年份</th><th>n</th><th>4h均值</th><th>胜率</th><th>PF</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
            ''')
    else:
        parts.append('<p>无足够数据进行年度分析。</p>')

    # ── 9.4 二维分层概览 ──
    parts.append('<h3>9.4 二维分层概览（25bps 成本后，n≥80, mean>0, wr≥45%）</h3>')

    for label, df_ in [('Rank × 涨幅', tw_rank_ret), ('Rank × 资金费率', tw_rank_fund), ('涨幅 × 资金费率', tw_ret_fund)]:
        if df_.empty:
            continue
        rows = ''
        for _, r in df_.iterrows():
            rows += f'''<tr>
              <td>{r.get('strata_key','?')}</td>
              <td>{r.get('window','?')}</td>
              <td>{int(r['n'])}</td>
              <td>{fmt_pct(r['net4_mean'])}</td>
              <td>{fmt_pct(r['net4_winrate'])}</td>
              <td>{fmt_ratio(r['net4_pf'])}</td>
              <td>{fmt_pct(r.get('net4_drop_top5pct', float('nan')))}</td>
            </tr>\n'''
        parts.append(f'''
        <h4>{label}</h4>
        <table class="data-table">
          <thead><tr><th>子集</th><th>窗口</th><th>n</th><th>4h均值</th><th>胜率</th><th>PF</th><th>去top5%均值</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        ''')

    # ── 9.5 综合判断 ──
    parts.append('''
    <h3>9.5 综合判断与结论</h3>
    <div style="background:#1a1a2e; border-left:4px solid #f39c12; padding:16px; margin:16px 0; border-radius:4px;">
      <h4 style="color:#f39c12; margin-top:0;">⚠️ WATCH — 有线索，但不够稳</h4>
      <p><strong>发现：</strong></p>
      <ul>
        <li><strong>30-40% 涨幅段</strong>是最有价值的窄区间——不像 &lt;30% 被噪音稀释，也不像 60+% 已经过热反转。</li>
        <li><strong>rank2-5</strong> 比 rank1 更好（rank1 透支严重，rank6-10 信号太弱）。</li>
        <li><strong>正资金费率（&gt;20bps）</strong>在 24-48h 窗口有边际增益，说明市场仍在追涨、多头拥挤时二段 squeeze 概率更高。</li>
        <li>最窄子集 <code>rank2-5 | 30-40% | pos_gt20bps | 24-48h</code> 有 n=78, PF=2.28, 但 <strong>2023 和 2024 年均为负收益</strong>，仅 2025 年大涨 +10.8% 撑起整体。</li>
      </ul>
      <p><strong>风险：</strong></p>
      <ul>
        <li>所有子集的 <strong>中位数收益仍为负</strong>（-0.6% ~ -0.02%），说明大部分交易是小亏，靠少数大赚拉均值。</li>
        <li>年度稳定性差：最好的子集也只有 2/4 年正收益，且最差年亏损 -3.3%。</li>
        <li>样本量偏小（n=78~94），统计显著性不足。</li>
      </ul>
      <p><strong>建议下一步：</strong></p>
      <ol>
        <li>如果要继续，<strong>只做 rank2-5 × 30-40% 的子集</strong>，且用小仓位 tail sleeve 评估（而非普通动量策略标准）。</li>
        <li>加入<strong>盘口/滑点代理</strong>：这类极端事件后流动性差，实际滑点可能远超 25bps。</li>
        <li>考虑<strong>移动止盈</strong>而非固定 4h/8h 持仓，让赢家跑、尽早砍亏。</li>
        <li>如果以上优化后仍然只有 2/4 年正收益，<strong>正式关闭 1.6a</strong>。</li>
      </ol>
    </div>
    ''')

    parts.append('</section>')
    return '\n'.join(parts)


def main():
    section = build_section()

    # Read existing HTML
    html = HTML_FILE.read_text(encoding='utf-8')

    # Insert before </body>
    insert_marker = '</body>'
    if insert_marker in html:
        html = html.replace(insert_marker, section + '\n' + insert_marker)
    else:
        html += '\n' + section

    HTML_FILE.write_text(html, encoding='utf-8')
    print(f'[done] Section 9 appended to {HTML_FILE}')


if __name__ == '__main__':
    main()
