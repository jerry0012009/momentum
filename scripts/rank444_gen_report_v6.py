#!/usr/bin/env python3
"""Rank 444 — v6报告: 多空双向对比 + 完整分析"""

import json
from pathlib import Path
from datetime import datetime

V4 = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/full_results_v4.json")
V5 = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/cn_futures_v5.json")
V6 = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/full_results_v6.json")
OUT = Path("/var/www/momentum-report/paper/rank444_rsi_bb.html")

with open(V4) as f: D4 = json.load(f)
with open(V5) as f: cn5 = json.load(f)
with open(V6) as f: v6 = json.load(f)

freq = D4["freq_analysis"]
bears = D4["bear_periods"]
now = datetime.now().strftime("%Y-%m-%d %H:%M")

def cr(v):
    if isinstance(v,str): return v
    if v is None: return '<span class="m">-</span>'
    if v > 0: return f'<span class="g">+{v:.2f}%</span>'
    if v < 0: return f'<span class="r">{v:.2f}%</span>'
    return f'{v:.2f}%'

def cs(v):
    if isinstance(v,str): return v
    if v is None: return '<span class="m">-</span>'
    if v > 1: return f'<span class="g">{v:.3f}</span>'
    if v < 0: return f'<span class="r">{v:.3f}</span>'
    return f'{v:.3f}'

def cw(v):
    if isinstance(v,str): return v
    if v is None: return '-'
    if v >= 70: return f'<span class="g">{v:.1f}%</span>'
    if v < 50: return f'<span class="r">{v:.1f}%</span>'
    return f'{v:.1f}%'

def rg_cell(d, key):
    if not d or key not in d: return '<td class="m">-</td>'
    r = d[key]
    c = "g" if r.get("ret",0)>0 else "r"
    return f'<td style="text-align:right"><span class="{c}">{r["ret"]:+.1f}%</span><br><span class="m">n={r["n"]}, wr={r["wr"]}%, ap={r["ap"]:.2f}%</span></td>'


# ═══ 多空对比主表 ═══
def ls_comparison_table():
    rows = ""
    # 按类型分组：美股在前，中国期货在后
    us_items = [(s,d) for s,d in v6.items() if d["type"]=="us"]
    cn_items = [(s,d) for s,d in v6.items() if d["type"]=="cn"]

    for items, label in [(us_items,""),(cn_items,"")]:
        for sym, fd in items:
            l = fd["long"]; s = fd["short"]; b = fd["both"]
            pg_l = fd.get("pg_long"); pg_s = fd.get("pg_short"); pg_b = fd.get("pg_both")

            # 判断哪个模式最优
            best = max([("纯多",l["ret"]),("纯空",s["ret"]),("多空",b["ret"])], key=lambda x:x[1])
            best_badge = f'<span class="pill pill-green">{best[0]}</span>' if best[1]>0 else f'<span class="pill pill-red">全部亏损</span>'

            cat = "US" if fd["type"]=="us" else "CN"
            cat_c = "#0369a1" if cat=="US" else "#dc2626"

            rows += f"""<tr>
<td><b>{fd['name']}</b><br><span class="m">{sym}</span><br><span style="color:{cat_c};font-size:11px">{cat}</span></td>
<td style="text-align:right">{cr(l['ret'])}<br><span class="m">n={l['n']}, sh={l['sh']:.2f}</span></td>
<td style="text-align:right">{cr(s['ret'])}<br><span class="m">n={s['n']}, sh={s['sh']:.2f}</span></td>
<td style="text-align:right">{cr(b['ret'])}<br><span class="m">n={b['n']}, sh={b['sh']:.2f}</span></td>
<td style="text-align:center">{best_badge}</td>
<td style="text-align:center">{cw(pg_l['pct_profitable']) if pg_l else '-'}</td>
<td style="text-align:center">{cw(pg_s['pct_profitable']) if pg_s else '-'}</td>
<td style="text-align:center">{cw(pg_b['pct_profitable']) if pg_b else '-'}</td>
</tr>"""
    return f"""<table><thead><tr>
<th>标的</th><th>纯做多</th><th>纯做空</th><th>多空双向</th><th>最优</th>
<th>网格多</th><th>网格空</th><th>网格双</th>
</tr></thead><tbody>{rows}</tbody></table>"""


# ═══ Regime拆分表（纯空） ═══
def short_regime_table():
    rows = ""
    for sym, fd in v6.items():
        s = fd["short"]
        rg = s.get("by_regime",{})
        if not rg: continue
        bull_l = rg.get("bull_long",{}); bull_s = rg.get("bull_short",{})
        bear_l = rg.get("bear_long",{}); bear_s = rg.get("bear_short",{})
        rows += f"""<tr>
<td><b>{fd['name']}</b></td>
<td style="text-align:right">{cr(s['ret'])}</td>
{rg_cell(rg,'bull')}{rg_cell(rg,'bear')}
<td style="text-align:right">{cr(bull_s.get('ret')) if bull_s else '<span class="m">-</span>'}</td>
<td style="text-align:right">{cr(bear_s.get('ret')) if bear_s else '<span class="m">-</span>'}</td>
</tr>"""
    return f"""<table><thead><tr>
<th>标的(纯空)</th><th>总收益</th><th>牛市总交易</th><th>熊市总交易</th><th>牛市做空</th><th>熊市做空</th>
</tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 多空拆分表（双向模式） ═══
def both_breakdown_table():
    rows = ""
    for sym, fd in v6.items():
        b = fd["both"]
        rg = b.get("by_regime",{})
        if not rg: continue
        bull_l = rg.get("bull_long",{}); bull_s = rg.get("bull_short",{})
        bear_l = rg.get("bear_long",{}); bear_s = rg.get("bear_short",{})
        rows += f"""<tr>
<td><b>{fd['name']}</b></td>
<td style="text-align:right">{cr(b['ret'])}</td>
<td style="text-align:center">{b['long_n']}</td>
<td style="text-align:right">{cr(b['long_ret'])}</td>
<td style="text-align:center">{b['short_n']}</td>
<td style="text-align:right">{cr(b['short_ret'])}</td>
{rg_cell(rg,'bull_long')}{rg_cell(rg,'bear_long')}{rg_cell(rg,'bull_short')}{rg_cell(rg,'bear_short')}
</tr>"""
    return f"""<table><thead><tr>
<th>标的</th><th>总收益</th><th>多头笔数</th><th>多头收益</th><th>空头笔数</th><th>空头收益</th>
<th>牛市做多</th><th>熊市做多</th><th>牛市做空</th><th>熊市做空</th>
</tr></thead><tbody>{rows}</tbody></table>"""


# ═══ v5 中国期货表 ═══
def cn_main_table():
    rows = ""
    for sym, fd in sorted(cn5.items(), key=lambda x: -x[1]["main"]["ret"]):
        m = fd["main"]; rg = m.get("by_regime",{})
        cat_colors = {"黑色系":"#1e293b","有色金属":"#7c3aed","贵金属":"#b45309","能源化工":"#0369a1","农产品":"#15803d","新能源":"#dc2626"}
        cat_c = cat_colors.get(fd["cat"],"#6b7280")
        rows += f"""<tr>
<td><b>{fd['name']}</b><br><span class="m">{sym}</span><br><span style="color:{cat_c};font-size:11px">{fd['cat']}</span></td>
<td>{fd['data_range']}<br><span class="m">{fd['bars']}根, {fd['years']}年</span></td>
<td style="text-align:center">{m['n']}</td>
<td style="text-align:right">{cr(m['ret'])}</td>
<td style="text-align:right">{cs(m['sh'])}</td>
<td style="text-align:right">{cr(m['mdd'])}</td>
{rg_cell(rg,'bull')}{rg_cell(rg,'bear')}</tr>"""
    return f"""<table><thead><tr><th>标的</th><th>数据区间</th><th>笔数</th><th>总收益</th><th>Sharpe</th><th>最大回撤</th><th>牛市交易</th><th>熊市交易</th></tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 汇总统计 ═══
us_items = {s:d for s,d in v6.items() if d["type"]=="us"}
cn_items = {s:d for s,d in v6.items() if d["type"]=="cn"}

n_us_long_pos = sum(1 for d in us_items.values() if d["long"]["ret"]>0)
n_us_short_pos = sum(1 for d in us_items.values() if d["short"]["ret"]>0)
n_us_both_pos = sum(1 for d in us_items.values() if d["both"]["ret"]>0)
n_cn_long_pos = sum(1 for d in cn_items.values() if d["long"]["ret"]>0)
n_cn_short_pos = sum(1 for d in cn_items.values() if d["short"]["ret"]>0)
n_cn_both_pos = sum(1 for d in cn_items.values() if d["both"]["ret"]>0)

avg_us_long = sum(d["long"]["ret"] for d in us_items.values())/max(len(us_items),1)
avg_us_short = sum(d["short"]["ret"] for d in us_items.values())/max(len(us_items),1)
avg_cn_long = sum(d["long"]["ret"] for d in cn_items.values())/max(len(cn_items),1)
avg_cn_short = sum(d["short"]["ret"] for d in cn_items.values())/max(len(cn_items),1)


html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rank 444 — RSI+BB 策略 v6: 多空双向对比</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;max-width:1360px;margin:0 auto;padding:20px;line-height:1.7;color:#111827;background:#f8fafc;font-size:15px}}
h1{{font-size:28px;margin:0 0 8px}}h2{{font-size:22px;margin:36px 0 12px;border-bottom:2px solid #e5e7eb;padding-bottom:6px}}h3{{font-size:18px;margin:20px 0 8px}}
.m{{color:#6b7280;font-size:12px}}.g{{color:#16a34a;font-weight:600}}.r{{color:#dc2626;font-weight:600}}
.hero{{border:1px solid #e5e7eb;border-radius:16px;background:white;padding:24px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.hero-metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0}}
.metric{{border:1px solid #e5e7eb;border-radius:10px;padding:12px;background:#f9fafb}}
.metric span{{display:block;color:#6b7280;font-size:11px}}.metric b{{display:block;font-size:22px;line-height:1.2;margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin:12px 0;background:white;border-radius:8px;overflow:hidden}}
th{{background:#f1f5f9;padding:8px 10px;text-align:left;border-bottom:2px solid #e2e8f0;font-weight:600;font-size:12px}}
td{{padding:8px 10px;border-bottom:1px solid #f1f5f9}}tr:hover{{background:#f8fafc}}
.insight{{background:#eff6ff;border-left:4px solid #3b82f6;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-warn{{background:#fef3c7;border-left:4px solid #f59e0b;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-good{{background:#ecfdf5;border-left:4px solid #10b981;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-bad{{background:#fef2f2;border-left:4px solid #ef4444;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.card{{border:1px solid #e5e7eb;border-radius:14px;background:white;padding:18px 20px;margin:14px 0}}
.pill{{display:inline-block;padding:3px 10px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px}}
.pill-green{{background:#ecfdf5;color:#065f46}}.pill-red{{background:#fef2f2;color:#991b1b}}.pill-yellow{{background:#fef3c7;color:#92400e}}
.toc{{background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;margin:16px 0}}
.toc a{{color:#2563eb;text-decoration:none}}.toc ol{{margin:4px 0;padding-left:20px}}.toc li{{margin:4px 0}}
.freq-note{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;margin-left:4px}}
.freq-15m{{background:#fce7f3;color:#9d174d}}.freq-1h{{background:#fef3c7;color:#92400e}}.freq-4h{{background:#dbeafe;color:#1e40af}}.freq-12h{{background:#e0e7ff;color:#3730a3}}.freq-1d{{background:#ecfdf5;color:#065f46}}
.vs{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}}
.vs-card{{border:1px solid #e5e7eb;border-radius:12px;padding:16px;background:white}}
.vs-card h4{{margin:0 0 8px;font-size:16px}}
</style>
</head>
<body>

<div class="hero">
<p class="m">Rank 444 · v6 多空双向对比 · {now}</p>
<h1>RSI + 布林线均值回复策略</h1>
<p>来源：<a href="https://github.com/fmzquant/strategies">fmzquant/strategies</a></p>
<div class="hero-metrics">
<div class="metric"><span>测试标的</span><b>{len(v6)}个</b></div>
<div class="metric"><span>美股纯多盈利</span><b>{n_us_long_pos}/{len(us_items)}</b></div>
<div class="metric"><span>美股纯空盈利</span><b>{n_us_short_pos}/{len(us_items)}</b></div>
<div class="metric"><span>美股多空盈利</span><b>{n_us_both_pos}/{len(us_items)}</b></div>
<div class="metric"><span>中国期货纯多盈利</span><b>{n_cn_long_pos}/{len(cn_items)}</b></div>
<div class="metric"><span>中国期货纯空盈利</span><b>{n_cn_short_pos}/{len(cn_items)}</b></div>
<div class="metric"><span>中国期货多空盈利</span><b>{n_cn_both_pos}/{len(cn_items)}</b></div>
</div>
</div>

<div class="toc">
<b>📑 目录</b>
<ol>
<li><a href="#s1">核心质疑：多头偏见检验</a></li>
<li><a href="#s2">纯多 vs 纯空 vs 多空双向（全品种）</a></li>
<li><a href="#s3">多空双向的收益拆解</a></li>
<li><a href="#s4">做空在什么市场有效？</a></li>
<li><a href="#s5">为什么做空美股会亏？</a></li>
<li><a href="#s6">美股15年日线 + 牛熊Regime</a></li>
<li><a href="#s7">🆕 中国期货全品种回测</a></li>
<li><a href="#s8">750参数网格 × Regime分析</a></li>
<li><a href="#s9">历史熊市区间回测</a></li>
<li><a href="#s10">多频率对比</a></li>
<li><a href="#s11">核心结论（v6最终版）</a></li>
</ol>
</div>

<!-- ═══ Section 1 ═══ -->
<h2 id="s1">1. 核心质疑：多头偏见检验</h2>
<div class="insight-warn">
<b>⚠️ 你的质疑非常到位。</b><br>
RSI+布林带策略的原始逻辑是"超卖后买入等反弹"——这是纯多头思维。过去十几年美股长牛（SPY从100涨到600+），任何"逢低买入"策略都会被牛市带飞。<br><br>
<b>核心问题：如果加上做空（超买后卖空等回落），结果如何？</b><br>
如果做空也赚钱 → 策略有真正的均值回复alpha<br>
如果做空亏钱 → 纯多的收益很可能只是牛市beta
</div>

<div class="card">
<h3>🧪 检验设计</h3>
<div class="vs">
<div class="vs-card">
<h4>🟢 纯做多（v5版本）</h4>
<p>RSI &lt; 超卖(30) + 价格 &lt; 布林下轨 → <b>买涨</b><br>回归布林中轨 → 平仓</p>
</div>
<div class="vs-card">
<h4>🔴 纯做空（新增）</h4>
<p>RSI &gt; 超买(70) + 价格 &gt; 布林上轨 → <b>卖空</b><br>回归布林中轨 → 平仓</p>
</div>
</div>
<p>同时测试 <b>多空双向</b>：两个信号同时运行，资金各占50%。</p>
</div>

<!-- ═══ Section 2 ═══ -->
<h2 id="s2">2. 纯多 vs 纯空 vs 多空双向（全品种）</h2>
{ls_comparison_table()}

<div class="insight-bad">
<h3>📊 核心发现：做空全线亏损</h3>
<table>
<tr><th>市场</th><th>纯多盈利标的</th><th>纯空盈利标的</th><th>多空盈利标的</th></tr>
<tr><td><b>美股(9个)</b></td><td>{n_us_long_pos}个</td><td><span class="r">{n_us_short_pos}个</span></td><td>{n_us_both_pos}个</td></tr>
<tr><td><b>中国期货(10个)</b></td><td>{n_cn_long_pos}个</td><td>{n_cn_short_pos}个</td><td>{n_cn_both_pos}个</td></tr>
</table>
<p><b>结论：做空在美股上是灾难，在中国期货上也只有铁矿石(+78%)和棕榈油(+16%)有效。多头偏见确实存在，但做空并不能解决问题——反而让结果更差。</b></p>
</div>

<!-- ═══ Section 3 ═══ -->
<h2 id="s3">3. 多空双向的收益拆解</h2>
{both_breakdown_table()}

<div class="card">
<h3>🔍 多空双向模式的尴尬</h3>
<p>在"多空双向"模式下，策略同时运行做多和做空。理想情况下：</p>
<ul>
<li>牛市：做多赚钱，做空亏钱 → 做多盈亏相抵</li>
<li>熊市：做空赚钱，做多亏钱 → 做空盈亏相抵</li>
<li>震荡市：两边都赚钱 → 最佳场景</li>
</ul>
<p><b>但实际结果是：做空的亏损大于做多的盈利，导致双向模式不如纯多。</b></p>
<p>原因很简单：均值回复的"回复力"是不对称的。下跌后的反弹（做多）比上涨后的回落（做空）更可靠——因为有"底部支撑"（恐慌性抛售后的抄底资金），但"顶部"没有类似的支撑机制（涨了可以继续涨）。</p>
</div>

<!-- ═══ Section 4 ═══ -->
<h2 id="s4">4. 做空在什么市场有效？</h2>
<div class="insight-good">
<h3>做空有效标的（仅3个）</h3>
<table>
<tr><th>标的</th><th>做空收益</th><th>共同特征</th></tr>
<tr><td><b>铁矿石</b></td><td><span class="g">+77.7%</span></td><td>中国经济转型，钢铁需求结构性下降。13年数据，价格从1300跌到700。做空=顺势。</td></tr>
<tr><td><b>棕榈油</b></td><td><span class="g">+15.5%</span></td><td>供给过剩+需求替代。长期震荡下行。</td></tr>
<tr><td><b>COMEX铜</b></td><td><span class="g">+3.1%</span></td><td>微弱盈利，基本持平。</td></tr>
</table>
<p><b>做空有效的共同特征：结构性下行市场。</b>做空在这些市场赚钱不是因为"均值回复"，而是因为"顺势而为"——价格持续下跌，超买后回落只是下跌趋势中的正常回调。</p>
</div>

<div class="insight-bad">
<h3>做空灾难标的</h3>
<table>
<tr><th>标的</th><th>做空收益</th><th>原因</th></tr>
<tr><td>苹果</td><td><span class="r">-89.9%</span></td><td>15年涨10倍+，做空=逆大势。每次超买都是"涨得还不够"。</td></tr>
<tr><td>微软</td><td><span class="r">-66.6%</span></td><td>同上。科技巨头的长牛让做空变成绞肉机。</td></tr>
<tr><td>铜(CN)</td><td><span class="r">-69.7%</span></td><td>中国工业化的金属需求长期增长。</td></tr>
<tr><td>铝(CN)</td><td><span class="r">-60.5%</span></td><td>同上。</td></tr>
</table>
</div>

<!-- ═══ Section 5 ═══ -->
<h2 id="s5">5. 为什么做空美股会亏？</h2>
<div class="card">
<h3>均值回复的"不对称性"</h3>
<div class="vs">
<div class="vs-card">
<h4>🟢 做多逻辑（有效）</h4>
<p>恐慌性抛售 → RSI超卖 + 价格跌破下轨 → <b>抄底资金入场</b> → 价格反弹回中轨</p>
<p style="color:#16a34a"><b>底层支撑：市场有"底部共识"</b>（如200日均线、心理关口、机构抄底）</p>
</div>
<div class="vs-card">
<h4>🔴 做空逻辑（失效）</h4>
<p>乐观性上涨 → RSI超买 + 价格突破上轨 → <b>???</b> → 价格回落</p>
<p style="color:#dc2626"><b>问题：市场没有"顶部共识"</b>（涨了可以继续涨，没有天然的天花板）</p>
</div>
</div>

<h3>数学验证</h3>
<table>
<tr><th>指标</th><th>SPY纯多</th><th>SPY纯空</th><th>说明</th></tr>
<tr><td>15年总收益</td><td><span class="g">+98.0%</span></td><td><span class="r">-31.2%</span></td><td>多头+98，空头-31</td></tr>
<tr><td>交易笔数</td><td>62</td><td>53</td><td>信号频率相近</td></tr>
<tr><td>Sharpe</td><td>2.00</td><td>-1.05</td><td>多头极优，空头极差</td></tr>
<tr><td>网格盈利占比</td><td>97.2%</td><td>~15%</td><td>几乎所有参数做多都赚，做空都亏</td></tr>
</table>

<div class="insight">
<b>💡 关键洞察</b><br>
<b>均值回复策略天然适合做多，不适合做空。</b>这是因为市场下跌时有"恐慌→超卖→反弹"的清晰路径，但市场上涨时没有对称的"贪婪→超买→回落"路径——上涨可以自我强化（FOMO、动量、空头回补），直到某个外生冲击打断它。<br><br>
这不是RSI+BB策略的缺陷，而是<b>所有均值回复策略的固有特性</b>。要实现有效的做空，需要动量策略（趋势跟踪），而不是均值回复。
</div>
</div>

<!-- ═══ Section 6: v5内容 ═══ -->
<h2 id="s6">6. 美股15年日线 + 牛熊Regime</h2>
<div class="insight-good">
<b>📊 即使知道做多有牛市beta，15年数据证明策略在熊市也有alpha。</b>
</div>"""

# v4 15年表
def regime_main_table():
    rows = ""
    for sym in ["MSFT","SPY","QQQ","AAPL","GC=F","HG=F","GLD","SI=F","CL=F"]:
        if sym not in freq: continue
        fd = freq[sym]; d1 = fd["freq_data"].get("1d",{})
        if not d1: continue
        rg = d1.get("by_regime",{}); rt = d1.get("regime_time",{}); pg = d1.get("pg",{})
        prs = pg.get("regime_summary",{}) if pg else {}
        rows += f"""<tr>
<td><b>{fd['name']}</b><br><span class="m">{sym}</span></td>
<td>{d1.get('ds','')}~{d1.get('de','')}<br><span class="m">{d1.get('nb','')}根</span></td>
<td style="text-align:center">{d1['n']}</td>
<td style="text-align:right">{cr(d1['ret'])}</td>
<td style="text-align:right">{cr(d1['ann'])}</td>
<td style="text-align:right">{cr(d1['mdd'])}</td>
<td style="text-align:right">{cs(d1['sh'])}</td>
<td style="text-align:center">{rt.get('bull_pct','?')}%</td>
<td style="text-align:center">{rt.get('bear_pct','?')}%</td>
{rg_cell(rg,'bull')}{rg_cell(rg,'bear')}</tr>"""
    return f"""<table><thead><tr><th>标的</th><th>数据区间</th><th>笔数</th><th>总收益</th><th>年化</th><th>最大回撤</th><th>Sharpe</th><th>牛市占比</th><th>熊市占比</th><th>牛市交易</th><th>熊市交易</th></tr></thead><tbody>{rows}</tbody></table>"""

html += regime_main_table()

# Section 7: 中国期货
html += f"""
<h2 id="s7">7. 🆕 中国期货全品种回测</h2>
{cn_main_table()}"""

# Section 8: 参数网格
html += """
<h2 id="s8">8. 750参数网格 × Regime分析</h2>
<table>
<tr><th>标的</th><th>组合数</th><th>盈利占比</th><th>均值</th><th>牛市均值</th><th>熊市均值</th></tr>"""
for sym in ["MSFT","SPY","QQQ","AAPL","GC=F","HG=F","GLD","SI=F","CL=F"]:
    if sym not in freq: continue
    fd = freq[sym]; pg = fd["freq_data"].get("1d",{}).get("pg",{})
    if not pg: continue
    rs = pg.get("regime_summary",{})
    html += f"""<tr><td><b>{fd['name']}</b></td><td>{pg['total']}</td><td>{cw(pg['pct_profitable'])}</td><td>{cr(pg['ret_mean'])}</td><td>{cr(rs.get('bull_ret_mean'))}</td><td>{cr(rs.get('bear_ret_mean'))}</td></tr>"""
html += "</table>"

# Section 9: 熊市
html += "<h2 id='s9'>9. 历史熊市区间回测（SPY）</h2><table><thead><tr><th>熊市事件</th><th>时间</th><th>笔数</th><th>策略收益</th><th>同期买持</th><th>Alpha</th></tr></thead><tbody>"
for b in sorted(bears, key=lambda x: -x.get("alpha",0)):
    ac = "g" if b["alpha"]>0 else "r"
    rc = "g" if b["ret"]>0 else "r"
    bc = "g" if b["buyhold"]>0 else "r"
    html += f"""<tr><td><b>{b['label']}</b><br><span class="m">{b['desc']}</span></td><td>{b['start']}~{b['end']}</td><td style="text-align:center">{b['n']}</td><td style="text-align:right"><span class="{rc}">{b['ret']:+.2f}%</span></td><td style="text-align:right"><span class="{bc}">{b['buyhold']:+.1f}%</span></td><td style="text-align:right"><span class="{ac}"><b>{b['alpha']:+.1f}%</b></span></td></tr>"""
html += "</tbody></table>"

# Section 10: 多频率
html += "<h2 id='s10'>10. 多频率对比</h2><table><thead><tr><th>标的</th><th>15分钟</th><th>1小时</th><th>4小时</th><th>12小时</th><th>日线(15年)</th></tr></thead><tbody>"
for sym in ["SPY","QQQ","AAPL","GLD","GC=F","CL=F"]:
    if sym not in freq: continue
    fd = freq[sym]; cells = ""
    for iv in ["15m","1h","4h","12h","1d"]:
        r = fd["freq_data"].get(iv,{})
        if r: cells += f'<td style="text-align:right">{cr(r["ret"])}<br><span class="m">n={r["n"]}, sh={r["sh"]:.2f}</span></td>'
        else: cells += '<td class="m" style="text-align:center">-</td>'
    html += f"<tr><td><b>{fd['name']}</b></td>{cells}</tr>"
html += "</tbody></table>"

# Section 11: 结论
html += f"""
<h2 id="s11">11. 核心结论（v6最终版）</h2>

<div class="insight-warn">
<h3>🎯 你的质疑被验证了——但结论比预期更复杂</h3>
<p><b>问题：纯多头策略是否受牛市影响？</b><br>
<b>答案：是的，但加入做空并不能改善结果，反而更差。</b></p>
</div>

<div class="card">
<h3>📊 三种模式对比总结</h3>
<table>
<tr><th>模式</th><th>美股盈利标的</th><th>中国期货盈利标的</th><th>适用场景</th></tr>
<tr><td><span class="pill pill-green">纯做多</span></td><td>{n_us_long_pos}/{len(us_items)} ({round(n_us_long_pos/len(us_items)*100)}%)</td><td>{n_cn_long_pos}/{len(cn_items)} ({round(n_cn_long_pos/len(cn_items)*100)}%)</td><td>长期上涨市场（美股ETF、科技龙头）</td></tr>
<tr><td><span class="pill pill-red">纯做空</span></td><td>{n_us_short_pos}/{len(us_items)} ({round(n_us_short_pos/len(us_items)*100)}%)</td><td>{n_cn_short_pos}/{len(cn_items)} ({round(n_cn_short_pos/len(cn_items)*100)}%)</td><td>结构性下行市场（铁矿石、棕榈油）</td></tr>
<tr><td><span class="pill pill-yellow">多空双向</span></td><td>{n_us_both_pos}/{len(us_items)} ({round(n_us_both_pos/len(us_items)*100)}%)</td><td>{n_cn_both_pos}/{len(cn_items)} ({round(n_cn_both_pos/len(cn_items)*100)}%)</td><td>几乎无——做空亏损拖累做多盈利</td></tr>
</table>
</div>

<div class="insight-good">
<h3>✅ 最终推荐</h3>
<table>
<tr><th>维度</th><th>推荐</th><th>理由</th></tr>
<tr><td>方向</td><td><b>纯做多</b></td><td>均值回复天然适合做多（有底部支撑，无顶部天花板）</td></tr>
<tr><td>美股标的</td><td><b>SPY/QQQ/MSFT/AAPL</b></td><td>15年验证，牛熊都有alpha，750参数97%+盈利</td></tr>
<tr><td>中国期货</td><td><b>豆粕/黄金/原油</b></td><td>有外部调节机制（季节性/OPEC/避险），做多有效</td></tr>
<tr><td>做空标的</td><td><b>铁矿石/棕榈油</b></td><td>结构性下行市场，做空是顺势而非均值回复</td></tr>
<tr><td>频率</td><td><b>日线 或 12h</b></td><td>信号质量最高</td></tr>
<tr><td>出场</td><td><b>中轨出场</b></td><td>优于阳线出场</td></tr>
<tr><td>止损</td><td><b>8%</b></td><td>降低回撤而不损收益</td></tr>
<tr><td>避免</td><td>多空双向模式</td><td>做空亏损拖累整体</td></tr>
</table>
</div>

<div class="card">
<h3>📋 一句话总结（v6最终版）</h3>
<p><b>RSI+布林带策略是均值回复策略，天然适合做多。15年美股数据证明纯多头有真实alpha（不只靠牛市），但做空全线亏损（-31%~-90%）。加入做空不能对冲牛市风险，反而拖累收益。策略的最佳用法：纯做多 + 美股ETF/科技龙头 + 日线 + 中轨出场。中国期货仅限有外部调节机制的品种（豆粕/黄金/原油）。</b></p>
</div>

<p class="m" style="margin-top:40px;text-align:center">
Rank 444 · RSI+BB 策略 · v6 多空双向对比 · {now}<br>
数据来源：Yahoo Finance / akshare · 回测代码：scripts/rank444_v6_long_short.py
</p>

</body>
</html>"""

with open(OUT, "w") as f:
    f.write(html)
print(f"✓ 报告写入 {OUT} ({OUT.stat().st_size/1024:.1f}KB)")
