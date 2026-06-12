#!/usr/bin/env python3
"""Rank 444 — 生成完整中文研究报告 HTML v2"""

import json
from pathlib import Path
from datetime import datetime

DATA = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/full_results_v2.json")
OUT = Path("/var/www/momentum-report/paper/rank444_rsi_bb.html")
LOCAL = Path("/root/clawd/jerry/momentum/reports/site/paper/rank444_rsi_bb.html")

with open(DATA) as f:
    D = json.load(f)

main = D["main_results"]
freq = D["freq_results"]
params = D["param_stability"]
times = D["time_stability"]
trades_data = D["main_trades"]

# ── helpers ──
def cr(v):
    if v > 0: return f'<span style="color:#16a34a;font-weight:600">+{v:.2f}%</span>'
    if v < 0: return f'<span style="color:#dc2626;font-weight:600">{v:.2f}%</span>'
    return f'{v:.2f}%'

def cs(v):
    if v > 1: return f'<span style="color:#16a34a;font-weight:600">{v:.3f}</span>'
    if v < 0: return f'<span style="color:#dc2626;font-weight:600">{v:.3f}</span>'
    return f'{v:.3f}'

def cw(v):
    if v >= 70: return f'<span style="color:#16a34a;font-weight:600">{v:.1f}%</span>'
    if v < 50: return f'<span style="color:#dc2626">{v:.1f}%</span>'
    return f'{v:.1f}%'

def pill(text, cls=""):
    return f'<span class="pill {cls}">{text}</span>'

# ── 分组 ──
mid_main = [r for r in main if r["exit_mode"] == "中轨出场"]
co_main = [r for r in main if r["exit_mode"] == "阳线出场(源码)"]

cats = {}
for r in mid_main:
    cats.setdefault(r["category"], []).append(r)

# ── 主回测表格 ──
def main_table(data):
    rows = ""
    for r in sorted(data, key=lambda x: -x["total_return_pct"]):
        rows += f"""<tr>
<td><b>{r['name']}</b><br><span class="muted">{r['symbol']}</span></td>
<td>{r.get('data_start','')}~{r.get('data_end','')}<br><span class="muted">{r.get('data_bars','')}根K线</span></td>
<td style="text-align:center">{r['n_trades']}</td>
<td style="text-align:center">{cw(r['win_rate'])}</td>
<td style="text-align:right">{cr(r['total_return_pct'])}</td>
<td style="text-align:right">{cr(r['annual_return_pct'])}</td>
<td style="text-align:right">{cr(r['max_dd_pct'])}</td>
<td style="text-align:right">{cs(r['sharpe'])}</td>
<td style="text-align:right">{r['profit_factor']:.2f}</td>
<td style="text-align:center">{r['avg_hold_bars']:.1f}根</td>
<td style="text-align:right">{cr(r['avg_pnl_pct'])}</td>
</tr>"""
    return f"""<table><thead><tr>
<th>标的</th><th>数据区间</th><th>交易笔数</th><th>胜率</th>
<th>总收益</th><th>年化收益</th><th>最大回撤</th><th>Sharpe</th>
<th>盈亏比</th><th>平均持仓</th><th>单笔收益</th>
</tr></thead><tbody>{rows}</tbody></table>"""

# ── 频率对比表 ──
freq_rows = ""
freq_by_sym = {}
for r in freq:
    freq_by_sym.setdefault(r["symbol"], {})[r["interval"]] = r
for sym, ivals in freq_by_sym.items():
    name = list(ivals.values())[0]["name"]
    d1 = ivals.get("1d", {})
    h1 = ivals.get("1h", {})
    freq_rows += f"""<tr>
<td><b>{name}</b></td>
<td style="text-align:center">{d1.get('n_trades', '-')}</td>
<td style="text-align:right">{cr(d1.get('total_return_pct', 0)) if d1 else '-'}</td>
<td style="text-align:right">{cs(d1.get('sharpe', 0)) if d1 else '-'}</td>
<td style="text-align:center">{cw(d1.get('win_rate', 0)) if d1 else '-'}</td>
<td style="text-align:center">{h1.get('n_trades', '-')}</td>
<td style="text-align:right">{cr(h1.get('total_return_pct', 0)) if h1 else '-'}</td>
<td style="text-align:right">{cs(h1.get('sharpe', 0)) if h1 else '-'}</td>
<td style="text-align:center">{cw(h1.get('win_rate', 0)) if h1 else '-'}</td>
<td style="text-align:center;font-weight:600">{'日线' if d1.get('total_return_pct',0) > h1.get('total_return_pct',0) else '1小时'}</td>
</tr>"""

freq_table = f"""<table><thead><tr>
<th>标的</th>
<th colspan="4" style="text-align:center;background:#eff6ff">日线 (1d)</th>
<th colspan="4" style="text-align:center;background:#fef3c7">1小时 (1h)</th>
<th>胜出</th>
</tr><tr>
<th></th><th>笔数</th><th>收益</th><th>Sharpe</th><th>胜率</th>
<th>笔数</th><th>收益</th><th>Sharpe</th><th>胜率</th><th></th>
</tr></thead><tbody>{freq_rows}</tbody></table>"""

# ── 参数稳定性表 ──
param_rows = ""
for p in sorted(params, key=lambda x: -x["return_mean"]):
    best = p["best_params"]
    worst = p["worst_params"]
    param_rows += f"""<tr>
<td><b>{p['name']}</b></td>
<td style="text-align:center">{p['total_combos']}</td>
<td style="text-align:center">{cw(p['pct_profitable'])}</td>
<td style="text-align:right">{cr(p['return_mean'])}</td>
<td style="text-align:right">{p['return_std']:.2f}%</td>
<td style="text-align:right">{cr(p['return_min'])}</td>
<td style="text-align:right">{cr(p['return_max'])}</td>
<td style="text-align:right">{cs(p['sharpe_mean'])}</td>
<td style="font-size:11px">RSI({best.get('rsi_period','–')},{best.get('rsi_limit','–')}) BB({best.get('bb_period','–')},{best.get('bb_mult','–')})</td>
</tr>"""

param_table = f"""<table><thead><tr>
<th>标的</th><th>参数组合数</th><th>盈利占比</th>
<th>收益均值</th><th>收益标准差</th><th>最差收益</th><th>最好收益</th>
<th>Sharpe均值</th><th>最优参数</th>
</tr></thead><tbody>{param_rows}</tbody></table>"""

# ── 时间稳定性表 ──
time_rows = ""
for t in sorted(times, key=lambda x: -x["consistency"]):
    yrs = ""
    for y in t["years"]:
        color = "#16a34a" if y["total_return_pct"] > 0 else "#dc2626"
        yrs += f'<span style="color:{color};font-weight:600;margin-right:8px">{y["year"]}: {y["total_return_pct"]:+.1f}%</span>'
    time_rows += f"""<tr>
<td><b>{t['name']}</b></td>
<td style="text-align:center">{t['n_years']}</td>
<td style="text-align:center">{cw(t['consistency'])}</td>
<td style="text-align:right">{cr(t['year_return_mean'])}</td>
<td style="text-align:right">{t['year_return_std']:.2f}%</td>
<td style="text-align:left">{yrs}</td>
</tr>"""

time_table = f"""<table><thead><tr>
<th>标的</th><th>测试年数</th><th>盈利年份占比</th>
<th>年均收益</th><th>年收益标准差</th><th>逐年收益明细</th>
</tr></thead><tbody>{time_rows}</tbody></table>"""

# ── 汇总统计 ──
n_mid_profitable = sum(1 for r in mid_main if r["total_return_pct"] > 0)
avg_mid_ret = sum(r["total_return_pct"] for r in mid_main) / len(mid_main) if mid_main else 0
best_mid = max(mid_main, key=lambda x: x["total_return_pct"]) if mid_main else {}
worst_mid = min(mid_main, key=lambda x: x["total_return_pct"]) if mid_main else {}

now = datetime.now().strftime("%Y-%m-%d %H:%M")

html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rank 444 — RSI+BB 均值回复策略 完整研究报告</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;max-width:1200px;margin:0 auto;padding:20px;line-height:1.7;color:#111827;background:#f8fafc;font-size:15px}}
h1{{font-size:28px;margin:0 0 8px}}h2{{font-size:22px;margin:32px 0 12px;border-bottom:2px solid #e5e7eb;padding-bottom:6px}}h3{{font-size:18px;margin:20px 0 8px}}
.muted{{color:#6b7280;font-size:13px}}
.hero{{border:1px solid #e5e7eb;border-radius:16px;background:white;padding:24px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.hero-metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0}}
.metric{{border:1px solid #e5e7eb;border-radius:10px;padding:12px;background:#f9fafb}}
.metric span{{display:block;color:#6b7280;font-size:11px}}
.metric b{{display:block;font-size:24px;line-height:1.2;margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin:12px 0;background:white;border-radius:8px;overflow:hidden}}
th{{background:#f1f5f9;padding:8px 10px;text-align:left;border-bottom:2px solid #e2e8f0;font-weight:600;font-size:12px}}
td{{padding:8px 10px;border-bottom:1px solid #f1f5f9}}
tr:hover{{background:#f8fafc}}
.insight{{background:#eff6ff;border-left:4px solid #3b82f6;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-warn{{background:#fef3c7;border-left:4px solid #f59e0b;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-good{{background:#ecfdf5;border-left:4px solid #10b981;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.insight-bad{{background:#fef2f2;border-left:4px solid #ef4444;padding:14px 18px;border-radius:0 10px 10px 0;margin:16px 0}}
.card{{border:1px solid #e5e7eb;border-radius:14px;background:white;padding:18px 20px;margin:14px 0}}
.pill{{display:inline-block;padding:3px 10px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px}}
.pill-green{{background:#ecfdf5;color:#065f46}}
.pill-red{{background:#fef2f2;color:#991b1b}}
.pill-yellow{{background:#fef3c7;color:#92400e}}
code{{background:#f1f5f9;padding:2px 6px;border-radius:4px;font-size:13px}}
.toc{{background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;margin:16px 0}}
.toc a{{color:#2563eb;text-decoration:none}}
.toc a:hover{{text-decoration:underline}}
.toc ol{{margin:4px 0;padding-left:20px}}
.toc li{{margin:4px 0}}
pre{{background:#1e293b;color:#e2e8f0;padding:16px;border-radius:10px;overflow-x:auto;font-size:13px;line-height:1.5}}
.good{{color:#16a34a;font-weight:600}}.bad{{color:#dc2626;font-weight:600}}
</style>
</head>
<body>

<div class="hero">
<p class="muted">Rank 444 · 完整研究报告 · {now} 北京时间</p>
<h1>RSI + 布林线均值回复策略</h1>
<p>来源：<a href="https://github.com/fmzquant/strategies">fmzquant/strategies</a></p>
<p>本报告对该策略进行了<b>系统性、多维度</b>的回测验证，涵盖：</p>
<ul>
<li>15个标的 × 2种出场方式 = <b>30组日线主回测</b></li>
<li><b>参数稳定性</b>：21个标的各108种参数组合的网格搜索</li>
<li><b>时间稳定性</b>：15个标的的逐年拆分回测</li>
<li><b>多频率对比</b>：日线 vs 1小时线</li>
<li><b>未来函数审计</b>：逐行检查代码是否存在"偷看未来"</li>
</ul>

<div class="hero-metrics">
<div class="metric"><span>日线主回测</span><b>{len(mid_main)} 标的</b></div>
<div class="metric"><span>盈利标的占比</span><b>{n_mid_profitable}/{len(mid_main)}</b></div>
<div class="metric"><span>平均总收益</span><b>{avg_mid_ret:.1f}%</b></div>
<div class="metric"><span>最佳标的</span><b style="font-size:15px">{best_mid.get('name','')}</b></div>
<div class="metric"><span>最佳收益</span><b class="good">{best_mid.get('total_return_pct',0):.1f}%</b></div>
<div class="metric"><span>最差标的</span><b style="font-size:15px">{worst_mid.get('name','')}</b></div>
<div class="metric"><span>最差收益</span><b class="bad">{worst_mid.get('total_return_pct',0):.1f}%</b></div>
<div class="metric"><span>参数组合测试</span><b>{sum(p['total_combos'] for p in params)}组</b></div>
</div>
</div>

<div class="toc">
<b>📑 目录</b>
<ol>
<li><a href="#s1">策略原理（通俗讲解）</a></li>
<li><a href="#s2">未来函数审计</a></li>
<li><a href="#s3">参数说明</a></li>
<li><a href="#s4">日线主回测结果</a></li>
<li><a href="#s5">两种出场方式对比</a></li>
<li><a href="#s6">分市场分析</a></li>
<li><a href="#s7">参数稳定性检验</a></li>
<li><a href="#s8">时间稳定性检验</a></li>
<li><a href="#s9">多频率回测对比</a></li>
<li><a href="#s10">典型交易案例</a></li>
<li><a href="#s11">核心结论与优化方向</a></li>
</ol>
</div>

<!-- ═══════════════ Section 1 ═══════════════ -->
<h2 id="s1">1. 策略原理（通俗讲解）</h2>

<div class="card">
<h3>🎯 一句话总结</h3>
<p><b>"弹簧被压得太低时买入，等弹簧弹回正常位置时卖出。"</b></p>

<h3>📖 详细解释</h3>
<p>想象一根弹簧代表价格，它总是在一个"正常范围"内波动。这根弹簧有两条看不见的边界——布林带的上轨和下轨。统计上说，大约95%的时间价格都在这个通道里。</p>
<p>当发生以下两件事<b>同时</b>出现时，说明弹簧被压得过低了：</p>
<ol>
<li><b>RSI < 30</b>（RSI = 相对强弱指数）：衡量最近一段时间涨跌的力度。RSI低于30意味着"卖过头了"——市场上恐慌情绪过重，价格被过度打压。</li>
<li><b>价格跌破布林带下轨</b>：布林带下轨 = 20日均线 - 2倍标准差。跌破下轨在统计上是不正常的（只有约2.5%的概率），说明价格偏离了正常范围。</li>
</ol>
<p>当两个条件同时满足，策略认为：<b>"弹簧压得太低了，大概率要弹回来"</b>——于是买入。</p>
<p>卖出时机：<b>价格回到布林带中轨</b>（20日均线）——弹簧回到正常位置，任务完成，获利了结。</p>

<h3>🔄 均值回复 vs 趋势跟踪</h3>
<table>
<tr><th>类型</th><th>核心思想</th><th>类比</th></tr>
<tr><td><b>均值回复（本策略）</b></td><td>价格偏离均值后会回归</td><td>弹簧被压后会弹回</td></tr>
<tr><td>趋势跟踪</td><td>价格突破后会延续</td><td>火车启动后会继续前进</td></tr>
</table>
<p>均值回复策略在<b>震荡市</b>中表现好（价格来回波动），在<b>单边趋势市</b>中可能反复抄底被套（弹簧越压越深不弹回）。</p>
</div>

<!-- ═══════════════ Section 2 ═══════════════ -->
<h2 id="s2">2. 未来函数审计</h2>

<div class="insight-warn">
<b>⚠️ 什么是未来函数？</b><br>
未来函数（Look-Ahead Bias）是指回测时"偷看了未来的数据"来做出交易决策。这会导致回测结果虚高——因为你在现实中不可能提前知道未来的价格。这是回测中最危险的陷阱。
</div>

<div class="card">
<h3>🔍 逐项审计清单</h3>
<table>
<tr><th>检查项</th><th>结论</th><th>详细说明</th></tr>
<tr>
<td><b>RSI 计算</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>使用 <code>ewm(com=period-1)</code> 指数加权移动平均，只看历史数据。第 N 根 bar 的 RSI 只用到 bar 0~N 的数据。</td>
</tr>
<tr>
<td><b>布林带计算</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>中轨 = <code>rolling(period).mean()</code>，标准差 = <code>rolling(period).std()</code>，都是滚动窗口，只用历史数据。</td>
</tr>
<tr>
<td><b>开仓信号</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>判断 <code>rsi[i] < 30 AND close[i] < bb_lower[i]</code>，全部是当前 bar 的已知数据。</td>
</tr>
<tr>
<td><b>平仓信号（中轨版）</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>判断 <code>close[i] > bb_mid[i]</code>，用当前 bar 的收盘价和当前 bar 的中轨值。</td>
</tr>
<tr>
<td><b>平仓信号（源码版）</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>判断 <code>close[i] > open[i]</code>，只用当前 bar 的 OHLC 数据。</td>
</tr>
<tr>
<td><b>交易价格</b></td>
<td><span class="pill pill-green">✅ 无未来函数</span></td>
<td>开仓和平仓都用当前 bar 的 <code>close</code> 价格，没有用下一 bar 的数据。</td>
</tr>
<tr>
<td><b>手续费</b></td>
<td><span class="pill pill-green">✅ 合理假设</span></td>
<td>单边 0.1%（双边 0.2%），对现货交易合理；期货实际更低（约万分之几），所以回测偏保守。</td>
</tr>
</table>

<h3>⚠️ 已知局限（不是未来函数，但需要注意）</h3>
<table>
<tr><th>局限项</th><th>影响</th><th>严重程度</th></tr>
<tr>
<td><b>收盘价成交假设</b></td>
<td>回测假设信号触发时能以收盘价成交，实际交易中如果收盘前才触发信号，可能有滑点。</td>
<td><span class="pill pill-yellow">中等</span></td>
</tr>
<tr>
<td><b>无流动性限制</b></td>
<td>回测假设无限流动性，实际大资金可能有冲击成本。</td>
<td><span class="pill pill-yellow">中等</span></td>
</tr>
<tr>
<td><b>无涨跌停限制（A股）</b></td>
<td>A股有10%涨跌停，极端情况下可能无法成交。</td>
<td><span class="pill pill-yellow">中等</span></td>
</tr>
<tr>
<td><b>日线级别信号</b></td>
<td>日线策略需要每天收盘前检查信号，不能盘中实时触发。</td>
<td><span class="pill pill-green">低</span></td>
</tr>
</table>

<h3>✅ 审计结论</h3>
<p><b>本策略的回测代码不存在未来函数。</b>所有指标计算和信号判断都只使用当前及历史数据，交易价格使用当前 bar 的收盘价。回测结果是可信的——但需要接受上述"收盘价成交"等合理假设的限制。</p>
</div>

<!-- ═══════════════ Section 3 ═══════════════ -->
<h2 id="s3">3. 策略参数说明</h2>

<div class="card">
<table>
<tr><th>参数</th><th>默认值</th><th>通俗解释</th><th>为什么选这个值？</th></tr>
<tr><td><b>RSI 周期</b></td><td>7</td><td>用最近7天的涨跌来算RSI</td><td>周期越短越敏感。7天是短期超卖的经典设置</td></tr>
<tr><td><b>RSI 阈值</b></td><td>30</td><td>RSI低于30才算"超卖"</td><td>传统技术分析标准：>70超买，<30超卖</td></tr>
<tr><td><b>布林带周期</b></td><td>20</td><td>用最近20天算均线和标准差</td><td>20日≈一个月的交易日，是布林带最常用的周期</td></tr>
<tr><td><b>布林带倍数</b></td><td>2.0</td><td>通道宽度=2倍标准差</td><td>正态分布下约95%数据在±2σ内，突破=统计异常</td></tr>
<tr><td><b>手续费</b></td><td>0.1% 单边</td><td>每笔交易扣0.1%</td><td>主流券商费率；期货实际更低，所以偏保守</td></tr>
</table>
</div>

<!-- ═══════════════ Section 4 ═══════════════ -->
<h2 id="s4">4. 日线主回测结果</h2>

<h3>4.1 中轨出场（推荐版）</h3>
<p class="muted">买入条件：RSI &lt; 30 且 收盘价 &lt; 布林带下轨 → 卖出条件：收盘价上穿布林带中轨</p>
{main_table(mid_main)}

<h3>4.2 阳线出场（源码版）</h3>
<p class="muted">买入条件相同 → 卖出条件：当天收阳线（收盘价 > 开盘价）即卖出</p>
{main_table(co_main)}

<!-- ═══════════════ Section 5 ═══════════════ -->
<h2 id="s5">5. 两种出场方式对比</h2>

<div class="insight-good">
<b>核心发现：中轨出场在绝大多数标的上显著优于阳线出场。</b><br>
中轨出场让利润多跑一段，直到价格"回归均值"；阳线出场太急躁，反弹刚开始就跑了。
</div>

<!-- ═══════════════ Section 6 ═══════════════ -->
<h2 id="s6">6. 分市场分析</h2>

<div class="card">
<h3>🇺🇸 美股（AAPL / TSLA / SPY / QQQ / MSFT）</h3>
<p>{pill('整体表现良好', 'pill-green')}</p>
<ul>
<li>5个标的中轨出场全部盈利，平均收益 <b>+24.1%</b></li>
<li><b>SPY 最稳</b>：胜率85.7%，Sharpe 3.37，参数稳定性100%盈利——因为标普500长期向上，超卖后反弹几乎必然</li>
<li><b>TSLA 收益最高</b>：+40.1%，但波动大（Sharpe 0.99），参数稳定性只有74%——高弹性股更适合这个策略</li>
<li><b>MSFT 相对较弱</b>：+13.7%，因为微软波动率较低，超卖信号少</li>
<li>阳线出场全部变差，TSLA 甚至从 +40% 变成 -8%</li>
</ul>
</div>

<div class="card">
<h3>🥇 黄金/贵金属</h3>
<p>{pill('策略有效', 'pill-green')}</p>
<ul>
<li>COMEX黄金 +6.5%，GLD +11.4%，白银 +45.6%（！）</li>
<li><b>白银表现远超黄金</b>：波动率更高，超卖反弹更剧烈，Sharpe 5.02 是全场最高</li>
<li>沪金 +7.3%，国内外黄金市场一致</li>
<li>交易次数少（7~9笔），说明贵金属的超卖机会不太多但质量高</li>
</ul>
</div>

<div class="card">
<h3>🛢️ 大宗商品期货</h3>
<p>{pill('分化明显', 'pill-yellow')}</p>
<ul>
<li><b>WTI原油</b>：+37.9%，Sharpe 3.81，原油的均值回复特性非常好</li>
<li><b>COMEX铜</b>：+30.4%，铜的工业属性使其有规律的超卖反弹</li>
<li><b>铁矿石</b>：+21.4%，国内期货中表现最好的</li>
<li><b>碳酸锂</b>：<span class="bad">-41.5%</span>，上市以来持续下跌，均值回复策略反复抄底失败</li>
<li><b>螺纹钢</b>：<span class="bad">-14.7%</span>，趋势性强于均值回复性</li>
<li><b>沪铜</b>：<span class="bad">-7.5%</span>，国内铜期货与国际铜表现不一致（可能因为人民币汇率影响）</li>
</ul>
</div>

<!-- ═══════════════ Section 7 ═══════════════ -->
<h2 id="s7">7. 参数稳定性检验</h2>

<div class="insight">
<b>💡 什么是参数稳定性？为什么重要？</b><br>
一个好策略不应该只在特定参数下才能赚钱。我们测试了 RSI周期(5/7/10/14) × RSI阈值(25/30/35) × 布林带周期(15/20/25) × 布林带倍数(1.5/2.0/2.5) = <b>108种参数组合</b>。如果大部分组合都赚钱，说明策略抓住的是真实的市场规律，而不是"恰好某个参数碰巧有效"。
</div>

{param_table}

<div class="card">
<h3>📊 参数稳定性解读</h3>
<ul>
<li><b>SPY/QQQ/铜</b>：100%参数组合盈利——这是最强的信号，说明策略在这些标的上抓住了真实的均值回复规律</li>
<li><b>AAPL/黄金/GLD/白银</b>：96~99%盈利——接近完美，只有极端参数才会亏</li>
<li><b>TSLA/原油</b>：74~91%盈利——收益高但参数敏感，需要选对参数</li>
<li><b>碳酸锂/螺纹钢</b>：参数稳定性低——说明这些标的不适合均值回复策略</li>
</ul>
<h3>⚠️ 收益标准差的意义</h3>
<p>标准差越小，说明不同参数下的表现越一致。SPY 的标准差只有5.87%（均值11.35%），意味着不管怎么调参数，收益都在5~17%之间——非常稳定。而原油的标准差是25%（均值33%），参数选得好可以赚58%，选得差可能只赚8%。</p>
</div>

<!-- ═══════════════ Section 8 ═══════════════ -->
<h2 id="s8">8. 时间稳定性检验</h2>

<div class="insight">
<b>💡 什么是时间稳定性？为什么重要？</b><br>
一个好策略应该在不同年份都能赚钱，而不是"恰好2024年赚了很多但2023年亏惨了"。我们将3年数据按年拆分，逐年回测，检查策略在牛熊转换中的表现一致性。
</div>

{time_table}

<div class="card">
<h3>📊 时间稳定性解读</h3>
<ul>
<li><b>SPY/QQQ/AAPL/白银/铜/GLD</b>：100%年份盈利——这是最可靠的信号，牛熊市都能赚钱</li>
<li><b>TSLA/原油/铁矿石</b>：75%年份盈利——有1年亏损，但整体正期望</li>
<li><b>碳酸锂/螺纹钢/沪铜</b>：年份盈利占比低——策略在这些标的上不稳定</li>
</ul>
<h3>💡 年收益标准差的意义</h3>
<p>标准差越小，说明各年的表现越一致。SPY 年均 4.8%、标准差小，意味着"每年稳稳地赚5%左右"。TSLA 年均 13% 但标准差大，意味着"好年赚30%、差年亏10%"——高收益伴随高波动。</p>
</div>

<!-- ═══════════════ Section 9 ═══════════════ -->
<h2 id="s9">9. 多频率回测对比</h2>

<div class="insight">
<b>💡 为什么测试不同频率？</b><br>
同一个策略在日线和小时线上可能表现完全不同。日线信号更"宏观"，信号少但质量高；小时线信号更频繁，但噪声也更多。了解频率的影响有助于选择最佳的交易节奏。
</div>

{freq_table}

<div class="card">
<h3>📊 频率对比的关键发现</h3>
<ol>
<li><b>日线全面胜出</b>：3个标的（SPY/AAPL/黄金）在日线上的收益都高于1小时线</li>
<li><b>小时线信号更多但质量差</b>：
  <ul>
    <li>SPY：日线14笔赚22%，1小时线52笔只赚5.8%——交易多了4倍，收益少了75%</li>
    <li>AAPL：日线13笔赚24.6%，1小时线58笔亏3.9%——更多交易反而亏钱</li>
    <li>黄金：日线7笔赚6.5%，1小时线188笔亏25%——灾难性的频率退化</li>
  </ul>
</li>
<li><b>原因分析</b>：RSI+布林带是"统计异常"检测器。在日线上，价格跌破2倍标准差下轨是真正的异常，反弹概率高；在小时线上，这种"异常"太频繁，很多是正常波动，导致大量假信号</li>
</ol>

<div class="insight-warn">
<b>⚠️ 结论：本策略只适合日线或更长周期。</b> 在小时线及以下频率，信号噪声比急剧恶化，策略失效。
</div>
</div>

<!-- ═══════════════ Section 10 ═══════════════ -->
<h2 id="s10">10. 典型交易案例</h2>
"""

# 添加典型交易案例
def trade_examples_html(trades_key, label, max_examples=3):
    trades = trades_data.get(trades_key, [])
    if not trades:
        return ""
    winners = sorted([t for t in trades if t["net_pnl_pct"] > 0], key=lambda x: -x["net_pnl_pct"])
    losers = sorted([t for t in trades if t["net_pnl_pct"] <= 0], key=lambda x: x["net_pnl_pct"])
    html = f'<div class="card"><h3>{label}</h3>'
    if winners:
        html += '<p><b>✅ 典型盈利交易：</b></p><table><tr><th>入场日</th><th>出场日</th><th>入场价</th><th>出场价</th><th>收益</th><th>持仓</th></tr>'
        for t in winners[:max_examples]:
            html += f'<tr><td>{t["entry_date"]}</td><td>{t["exit_date"]}</td><td>{t["entry_price"]}</td><td>{t["exit_price"]}</td><td class="good">+{t["net_pnl_pct"]:.2f}%</td><td>{t["hold_bars"]}根</td></tr>'
        html += '</table>'
    if losers:
        html += '<p><b>❌ 典型亏损交易：</b></p><table><tr><th>入场日</th><th>出场日</th><th>入场价</th><th>出场价</th><th>亏损</th><th>持仓</th></tr>'
        for t in losers[:2]:
            html += f'<tr><td>{t["entry_date"]}</td><td>{t["exit_date"]}</td><td>{t["entry_price"]}</td><td>{t["exit_price"]}</td><td class="bad">{t["net_pnl_pct"]:.2f}%</td><td>{t["hold_bars"]}根</td></tr>'
        html += '</table>'
    html += '</div>'
    return html

# SPY trades
html += trade_examples_html("SPY_中轨出场", "标普500 (SPY) 典型交易 — 中轨出场")
html += trade_examples_html("AAPL_中轨出场", "苹果 (AAPL) 典型交易 — 中轨出场")
html += trade_examples_html("GC=F_中轨出场", "黄金期货 (GC=F) 典型交易 — 中轨出场")

html += f"""
<!-- ═══════════════ Section 11 ═══════════════ -->
<h2 id="s11">11. 核心结论与优化方向</h2>

<div class="insight-good">
<h3>✅ 策略有效的场景（可以放心用的）</h3>
<ul>
<li><b>美股大盘ETF（SPY/QQQ）</b>：参数100%稳定，时间100%稳定，Sharpe 2.7~3.4——这是策略的"甜蜜区"</li>
<li><b>贵金属（白银/黄金）</b>：白银 Sharpe 5.0（全场最高），黄金稳定盈利</li>
<li><b>原油/铜期货</b>：大宗商品均值回复特性好，收益 +30~38%</li>
<li><b>日线频率</b>：信号质量最高，小时线及以下频率失效</li>
</ul>
</div>

<div class="insight-bad">
<h3>❌ 策略无效的场景（不要用的）</h3>
<ul>
<li><b>趋势性下跌标的（碳酸锂）</b>：持续下跌中反复抄底，亏损 -41%</li>
<li><b>趋势性强的商品（螺纹钢/沪铜）</b>：均值回复信号不可靠</li>
<li><b>小时线/分钟线</b>：信号噪声比急剧恶化，交易越多亏越多</li>
<li><b>源码的"阳线平仓"</b>：是个严重 bug，把大部分利润截断</li>
</ul>
</div>

<div class="insight-warn">
<h3>⚠️ 需要注意的风险</h3>
<ul>
<li><b>纯做多策略</b>：在持续下跌市场中没有做空保护，会反复被套</li>
<li><b>信号稀少</b>：3年只有7~23笔交易，大部分时间空仓（对耐心是考验）</li>
<li><b>极端行情风险</b>：如果"超卖"后继续暴跌（如2022年TSLA），策略会亏</li>
<li><b>收盘价成交假设</b>：实际交易可能有滑点，尤其在波动大的标的上</li>
</ul>
</div>

<div class="card">
<h3>🚀 优化方向（如果要继续推进）</h3>
<ol>
<li><b>加止损</b>：当前策略没有止损。建议加 5~8% 固定止损，防止"抄底抄在半山腰"</li>
<li><b>加趋势过滤</b>：只在长期上升趋势中做多（如价格 > 200日均线），避免在熊市中反复抄底</li>
<li><b>加做空</b>：对称策略——RSI>70 且 价格>上轨 → 做空，回归中轨平仓</li>
<li><b>动态仓位</b>：RSI越低（超卖越严重）仓位越大，反之越小</li>
<li><b>多标的组合</b>：同时在SPY/QQQ/黄金/原油上运行，分散风险</li>
<li><b>参数自适应</b>：根据近期波动率动态调整布林带倍数（高波动时用更宽的通道）</li>
</ol>
</div>

<div class="card">
<h3>📋 一句话总结</h3>
<p><b>RSI+布林带均值回复策略在美股ETF和贵金属上是一个简单、可靠、参数稳健的策略</b>（3年+20~45%收益，Sharpe 2~5）。但它不是万能的——在趋势性标的和短周期上会失效。源码的"阳线平仓"是个bug。如果要实际使用，建议加止损和趋势过滤，并作为多策略组合的一部分。</p>
</div>

<p class="muted" style="margin-top:40px;text-align:center">
Rank 444 · RSI + BB 均值回复策略 · 完整研究报告 · {now}<br>
数据来源：Yahoo Finance / 新浪期货 · 回测代码：scripts/rank444_full_backtest.py
</p>

</body>
</html>"""

# 写入两个位置
OUT.parent.mkdir(parents=True, exist_ok=True)
LOCAL.parent.mkdir(parents=True, exist_ok=True)
for path in [OUT, LOCAL]:
    with open(path, "w") as f:
        f.write(html)
    print(f"✓ 报告写入 {path} ({path.stat().st_size/1024:.1f}KB)")
