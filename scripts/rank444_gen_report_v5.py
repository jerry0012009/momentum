#!/usr/bin/env python3
"""Rank 444 — v5报告生成: 在v4基础上补充中国期货"""

import json
from pathlib import Path
from datetime import datetime

V4 = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/full_results_v4.json")
V5 = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/cn_futures_v5.json")
OUT = Path("/var/www/momentum-report/paper/rank444_rsi_bb.html")

with open(V4) as f: D4 = json.load(f)
with open(V5) as f: cn = json.load(f)

freq = D4["freq_analysis"]
bears = D4["bear_periods"]
now = datetime.now().strftime("%Y-%m-%d %H:%M")

def cr(v):
    if isinstance(v,str): return v
    if v > 0: return f'<span class="g">+{v:.2f}%</span>'
    if v < 0: return f'<span class="r">{v:.2f}%</span>'
    return f'{v:.2f}%'

def cs(v):
    if isinstance(v,str): return v
    if v > 1: return f'<span class="g">{v:.3f}</span>'
    if v < 0: return f'<span class="r">{v:.3f}</span>'
    return f'{v:.3f}'

def cw(v):
    if isinstance(v,str): return v
    if v >= 70: return f'<span class="g">{v:.1f}%</span>'
    if v < 50: return f'<span class="r">{v:.1f}%</span>'
    return f'{v:.1f}%'

def rg_cell(d, key):
    if not d or key not in d: return '<td class="m">-</td>'
    r = d[key]
    c = "g" if r.get("ret",0)>0 else "r"
    return f'<td style="text-align:right"><span class="{c}">{r["ret"]:+.1f}%</span><br><span class="m">n={r["n"]}, wr={r["wr"]}%, ap={r["ap"]:.2f}%</span></td>'


# ═══ v4 15年主回测表 (同v4) ═══
def regime_main_table():
    rows = ""
    for sym in ["MSFT","SPY","QQQ","AAPL","GC=F","HG=F","GLD","SI=F","CL=F"]:
        if sym not in freq: continue
        fd = freq[sym]
        d1 = fd["freq_data"].get("1d",{})
        if not d1: continue
        rg = d1.get("by_regime",{})
        rt = d1.get("regime_time",{})
        pg = d1.get("pg",{})
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
{rg_cell(rg,'bull')}{rg_cell(rg,'bear')}
<td style="text-align:right">{cr(prs.get('bull_ret_mean')) if prs.get('bull_ret_mean') is not None else '<span class="m">-</span>'}</td>
<td style="text-align:right">{cr(prs.get('bear_ret_mean')) if prs.get('bear_ret_mean') is not None else '<span class="m">-</span>'}</td></tr>"""
    return f"""<table><thead><tr><th>标的</th><th>数据区间</th><th>笔数</th><th>总收益</th><th>年化</th><th>最大回撤</th><th>Sharpe</th><th>牛市占比</th><th>熊市占比</th><th>牛市交易</th><th>熊市交易</th><th>网格牛市均值</th><th>网格熊市均值</th></tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 中国期货主表 ═══
def cn_main_table():
    rows = ""
    # 分类排序：先按收益降序
    for sym, fd in sorted(cn.items(), key=lambda x: -x[1]["main"]["ret"]):
        m = fd["main"]
        rg = m.get("by_regime",{})
        rt = fd.get("regime_time",{})
        pg = fd.get("param_grid")
        prs = pg.get("regime_summary",{}) if pg else {}

        cat_colors = {"黑色系":"#1e293b","有色金属":"#7c3aed","贵金属":"#b45309",
                      "能源化工":"#0369a1","农产品":"#15803d","新能源":"#dc2626"}
        cat_c = cat_colors.get(fd["cat"],"#6b7280")

        rows += f"""<tr>
<td><b>{fd['name']}</b><br><span class="m">{sym}</span><br><span style="color:{cat_c};font-size:11px">{fd['cat']}</span></td>
<td>{fd['data_range']}<br><span class="m">{fd['bars']}根, {fd['years']}年</span></td>
<td style="text-align:center">{m['n']}</td>
<td style="text-align:right">{cr(m['ret'])}</td>
<td style="text-align:right">{cs(m['sh'])}</td>
<td style="text-align:right">{cr(m['mdd'])}</td>
<td style="text-align:center">{rt.get('bull_pct','?')}%</td>
<td style="text-align:center">{rt.get('bear_pct','?')}%</td>
{rg_cell(rg,'bull')}{rg_cell(rg,'bear')}
<td style="text-align:center">{cw(pg['pct_profitable']) if pg else '-'}</td>
<td style="text-align:right">{cr(prs.get('bull_ret_mean')) if prs.get('bull_ret_mean') is not None else '-'}</td>
<td style="text-align:right">{cr(prs.get('bear_ret_mean')) if prs.get('bear_ret_mean') is not None else '-'}</td></tr>"""
    return f"""<table><thead><tr><th>标的</th><th>数据区间</th><th>笔数</th><th>总收益</th><th>Sharpe</th><th>最大回撤</th><th>牛市占比</th><th>熊市占比</th><th>牛市交易</th><th>熊市交易</th><th>参数盈利占比</th><th>网格牛市均值</th><th>网格熊市均值</th></tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 中国期货止损表 ═══
def cn_stoploss_table():
    rows = ""
    for sym, fd in sorted(cn.items(), key=lambda x: -x[1]["main"]["ret"]):
        sl = fd.get("stop_loss",[])
        if not sl: continue
        cells = ""
        for s in sl:
            c = "g" if s["ret"]>0 else "r"
            cells += f'<td style="text-align:right"><span class="{c}">{s["ret"]:+.1f}%</span><br><span class="m">MDD:{s["mdd"]:.1f}%</span></td>'
        rows += f"<tr><td><b>{fd['name']}</b></td>{cells}</tr>"
    header = "<th>标的</th>" + "".join(f'<th style="text-align:center">SL={s["stop"]}</th>' for s in list(cn.values())[0].get("stop_loss",[]))
    return f"""<table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 中国期货止损分析结论 ═══
# 汇总赢家/输家
winners = {k:v for k,v in cn.items() if v["main"]["ret"]>0}
losers = {k:v for k,v in cn.items() if v["main"]["ret"]<=0}
n_win = len(winners); n_lose = len(losers); n_total = len(cn)

# v4 bear period table
def bear_period_table():
    rows = ""
    for b in sorted(bears, key=lambda x: -x.get("alpha",0)):
        ac = "g" if b["alpha"]>0 else "r"
        rc = "g" if b["ret"]>0 else "r"
        bc = "g" if b["buyhold"]>0 else "r"
        rows += f"""<tr>
<td><b>{b['label']}</b><br><span class="m">{b['desc']}</span></td>
<td>{b['start']}~{b['end']}</td>
<td style="text-align:center">{b['n']}</td>
<td style="text-align:right"><span class="{rc}">{b['ret']:+.2f}%</span></td>
<td style="text-align:right"><span class="{bc}">{b['buyhold']:+.1f}%</span></td>
<td style="text-align:right"><span class="{ac}"><b>{b['alpha']:+.1f}%</b></span></td></tr>"""
    return f"""<table><thead><tr><th>熊市事件</th><th>时间</th><th>笔数</th><th>策略收益</th><th>同期买持</th><th>Alpha</th></tr></thead><tbody>{rows}</tbody></table>"""


# ═══ 多频率表 ═══
def multifreq_table():
    rows = ""
    for sym in ["SPY","QQQ","AAPL","GLD","GC=F","CL=F"]:
        if sym not in freq: continue
        fd = freq[sym]
        cells = ""
        for iv in ["15m","1h","4h","12h","1d"]:
            r = fd["freq_data"].get(iv,{})
            if r:
                rg = r.get("by_regime",{})
                bull_ret = rg.get("bull",{}).get("ret","?")
                bear_ret = rg.get("bear",{}).get("ret","?")
                bull_n = rg.get("bull",{}).get("n","?")
                bear_n = rg.get("bear",{}).get("n","?")
                ri = ""
                if bull_ret != "?" or bear_ret != "?":
                    ri = f'<br><span class="m">牛:{bull_ret}%({bull_n}) 熊:{bear_ret}%({bear_n})</span>'
                cells += f'<td style="text-align:right">{cr(r["ret"])}<br><span class="m">n={r["n"]}, sh={r["sh"]:.2f}, wr={r["wr"]:.0f}%</span>{ri}</td>'
            else:
                cells += '<td class="m" style="text-align:center">-</td>'
        rows += f"<tr><td><b>{fd['name']}</b></td>{cells}</tr>"
    return f"""<table><thead><tr><th>标的</th><th>15分钟</th><th>1小时</th><th>4小时</th><th>12小时</th><th>日线(15年)</th></tr></thead><tbody>{rows}</tbody></table>"""


# ═══ v4 15年数据汇总 ═══
d1_all = {sym:freq[sym]["freq_data"].get("1d",{}) for sym in freq if freq[sym]["freq_data"].get("1d")}
n_profit_15y = sum(1 for r in d1_all.values() if r.get("ret",0)>0)
bear_profit = sum(1 for r in d1_all.values() if r.get("by_regime",{}).get("bear",{}).get("ret",0)>0)
bear_total = sum(1 for r in d1_all.values() if "bear" in r.get("by_regime",{}))

# ═══ HTML ═══
html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rank 444 — RSI+BB 策略 v5: 全品种牛熊分析+中国期货</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;max-width:1360px;margin:0 auto;padding:20px;line-height:1.7;color:#111827;background:#f8fafc;font-size:15px}}
h1{{font-size:28px;margin:0 0 8px}}h2{{font-size:22px;margin:36px 0 12px;border-bottom:2px solid #e5e7eb;padding-bottom:6px}}h3{{font-size:18px;margin:20px 0 8px}}
.m{{color:#6b7280;font-size:12px}}.g{{color:#16a34a;font-weight:600}}.r{{color:#dc2626;font-weight:600}}
.hero{{border:1px solid #e5e7eb;border-radius:16px;background:white;padding:24px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.hero-metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:16px 0}}
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
</style>
</head>
<body>

<div class="hero">
<p class="m">Rank 444 · v5 全品种牛熊分析+中国期货 · {now}</p>
<h1>RSI + 布林线均值回复策略</h1>
<p>来源：<a href="https://github.com/fmzquant/strategies">fmzquant/strategies</a></p>
<div class="hero-metrics">
<div class="metric"><span>全球标的数</span><b>{len(d1_all)+len(cn)}</b></div>
<div class="metric"><span>美股(15年)</span><b>{n_profit_15y}/{len(d1_all)} 盈利</b></div>
<div class="metric"><span>中国期货</span><b>{n_win}/{n_total} 盈利</b></div>
<div class="metric"><span>期货赢家</span><b style="font-size:14px">豆粕+53% / 黄金+11%</b></div>
<div class="metric"><span>期货输家</span><b style="font-size:14px">棕榈油-70% / 铜-67%</b></div>
<div class="metric"><span>熊市交易盈利</span><b>{bear_profit}/{bear_total} 美股</b></div>
</div>
</div>

<div class="toc">
<b>📑 目录</b>
<ol>
<li><a href="#s1">核心质疑：牛市偏见检验</a></li>
<li><a href="#s2">美股15年日线 + 牛熊Regime</a></li>
<li><a href="#s3">🆕 中国期货全品种回测</a></li>
<li><a href="#s4">中国期货止损优化</a></li>
<li><a href="#s5">中国期货成败原因分析</a></li>
<li><a href="#s6">750参数网格 × Regime分析（美股）</a></li>
<li><a href="#s7">历史熊市区间回测（SPY）</a></li>
<li><a href="#s8">多频率对比 (15m/1h/4h/12h/1d)</a></li>
<li><a href="#s9">核心结论（v5修订版）</a></li>
</ol>
</div>

<!-- ═══ Section 1 ═══ -->
<h2 id="s1">1. 核心质疑：牛市偏见检验</h2>
<div class="insight-warn">
<b>⚠️ 关键问题：策略靠的是牛市beta还是均值回复alpha？</b><br>
v5用15年美股+20年中国期货+6个历史熊市区间来回答这个问题。结论：<b>美股有真实alpha，中国期货大部分标不适用。</b>
</div>

<!-- ═══ Section 2 ═══ -->
<h2 id="s2">2. 美股15年日线 + 牛熊Regime</h2>
{regime_main_table()}
<div class="insight-good">
<b>📊 美股结论：策略不只靠牛市。</b>SPY/QQQ/MSFT/AAPL在熊市交易也盈利。MSFT熊市+131%比牛市+119%还多。
</div>

<!-- ═══ Section 3: 中国期货 ═══ -->
<h2 id="s3">3. 🆕 中国期货全品种回测</h2>
<div class="insight">
<b>💡 为什么测中国期货？</b><br>
RSI+BB策略在美股上表现好，但中国市场有完全不同的微观结构：散户比例高、涨跌停限制、T+1（股票）/T+0（期货）、换手率极高、政策干预频繁。测试中国期货可以回答：<b>这个策略的alpha是否跨市场有效？</b>
</div>

{cn_main_table()}

<div class="card">
<h3>📊 中国期货结果速览</h3>
<table>
<tr><th>类别</th><th>结论</th><th>代表标的</th></tr>
<tr><td><span class="pill pill-green">✅ 赢家</span></td><td>3个标的盈利</td><td><b>豆粕+53.4%</b>（78.7%参数盈利）、<b>黄金+11.3%</b>（97.2%参数盈利）、<b>原油+7.9%</b></td></tr>
<tr><td><span class="pill pill-red">❌ 输家</span></td><td>11个标的亏损</td><td>棕榈油-70%、铜-67%、铝-56%、铁矿石-53%、螺纹钢-52%、碳酸锂-42%、白糖-30%、锌-33%、焦煤-37%、焦炭-19%、白银-10%</td></tr>
</table>
<p><b>总体：14个中国期货标的中只有3个盈利（21%），远低于美股的80%+。</b></p>
</div>

<!-- ═══ Section 4: 止损 ═══ -->
<h2 id="s4">4. 中国期货止损优化</h2>
{cn_stoploss_table()}
<div class="card">
<h3>止损对赢家的影响</h3>
<ul>
<li><b>豆粕</b>：无止损+53%，3%止损+52%，5%止损+50%——止损略微降低收益但控制回撤</li>
<li><b>黄金</b>：无止损+11%，5%止损+12%——止损几乎不影响</li>
<li><b>原油</b>：无止损+8%，8%止损+14%——<b>止损反而提升收益！</b>（截断了大亏损交易）</li>
</ul>
<h3>止损对输家的影响</h3>
<ul>
<li>大部分输家即使用止损也还是亏——因为问题是<b>系统性的持续下跌</b>，不是单笔大亏</li>
<li>止损只是减少了亏损幅度，但没有改变"抄底失败"的本质</li>
</ul>
</div>

<!-- ═══ Section 5: 成败原因 ═══ -->
<h2 id="s5">5. 中国期货成败原因分析</h2>

<div class="insight-good">
<h3>✅ 为什么豆粕/黄金/原油能赢？</h3>
<table>
<tr><th>标的</th><th>核心原因</th><th>解释</th></tr>
<tr><td><b>豆粕</b></td><td>季节性均值回复</td><td>豆粕价格受种植/养殖周期驱动，有明显的季节性波动。超卖后往往在需求旺季反弹，均值回复逻辑成立。</td></tr>
<tr><td><b>黄金</b></td><td>避险需求均值回复</td><td>黄金在恐慌抛售后（如2013-2015下跌），避险买盘会托底。均值回复在"有底"的市场有效。</td></tr>
<tr><td><b>原油</b></td><td>OPEC调控均值回复</td><td>原油有OPEC减产/增产作为"调节器"，暴跌后往往会因为减产而反弹。但长期熊市（2014-2016）仍然危险。</td></tr>
</table>
</div>

<div class="insight-bad">
<h3>❌ 为什么大部分中国期货会输？</h3>
<table>
<tr><th>原因</th><th>详细解释</th><th>受影响标的</th></tr>
<tr><td><b>结构性熊市</b></td><td>中国经济从高速增长转向高质量增长，黑色系（螺纹钢/铁矿石/焦炭）需求长期走弱。价格不是"偏离均值后回归"，而是"均值本身在下降"——均值回复的理论前提不成立。</td><td>铁矿石-53%、螺纹钢-52%、焦炭-19%</td></tr>
<tr><td><b>政策主导市场</b></td><td>中国期货受政策调控影响极大（如钢铁限产、煤炭保供、碳中和目标）。政策突变导致价格不按统计规律运行。</td><td>焦煤-37%、焦炭-19%、螺纹钢-52%</td></tr>
<tr><td><b>持续阴跌</b></td><td>碳酸锂从60万跌到17万，棕榈油长期震荡下行。RSI反复触发"超卖"信号但价格持续下跌——每次抄底都是在半山腰。</td><td>碳酸锂-42%、棕榈油-70%、白糖-30%</td></tr>
<tr><td><b>有色金属的"假均值回复"</b></td><td>铜/铝/锌跟随全球宏观周期（美元强弱、中国PMI），周期长达数年。RSI+BB的日线均值回复捕捉不到这种长周期。</td><td>铜-67%、铝-56%、锌-33%</td></tr>
</table>
</div>

<div class="card">
<h3>🔍 深层对比：美股 vs 中国期货</h3>
<table>
<tr><th>维度</th><th>美股</th><th>中国期货</th></tr>
<tr><td>长期趋势</td><td>SPY 15年涨300%+，长牛</td><td>大部分品种震荡或下行</td></tr>
<tr><td>下跌特征</td><td>快跌快弹（V型）</td><td>慢跌阴跌（L型/U型）</td></tr>
<tr><td>均值回复前提</td><td>✅ "价格偏离后会回归"</td><td>❌ "均值本身在移动"</td></tr>
<tr><td>政策影响</td><td>市场主导</td><td>政策主导（限产/保供/碳中和）</td></tr>
<tr><td>散户结构</td><td>机构主导，定价效率高</td><td>散户多，趋势追涨杀跌严重</td></tr>
<tr><td>RSI+BB有效性</td><td>✅ 80%标的盈利</td><td>❌ 21%标的盈利</td></tr>
</table>
<p><b>结论：RSI+BB均值回复策略假设"价格偏离后会回归正常范围"，这在长期上涨、机构主导的美股市场成立；但在中国期货市场，很多品种的"正常范围"本身在移动，策略的前提条件不满足。</b></p>
</div>

<!-- ═══ Section 6 ═══ -->
<h2 id="s6">6. 750参数网格 × Regime分析（美股）</h2>
<div class="insight">
<b>💡 750参数组合验证：策略是否只在特定参数下有效？</b>
</div>
<table>
<tr><th>标的</th><th>组合数</th><th>盈利占比</th><th>均值</th><th>牛市均值</th><th>熊市均值</th><th>判断</th></tr>"""

for sym in ["MSFT","SPY","QQQ","AAPL","GC=F","HG=F","GLD","SI=F","CL=F"]:
    if sym not in freq: continue
    fd = freq[sym]
    pg = fd["freq_data"].get("1d",{}).get("pg",{})
    if not pg: continue
    rs = pg.get("regime_summary",{})
    bull_ok = rs.get("bull_ret_mean",0) is not None and rs.get("bull_ret_mean",0)>0
    bear_ok = rs.get("bear_ret_mean",0) is not None and rs.get("bear_ret_mean",0)>0
    judge = '<span class="pill pill-green">✅ 牛熊都有alpha</span>' if bull_ok and bear_ok else '<span class="pill pill-yellow">⚠️ 牛强熊弱</span>' if bull_ok else '<span class="pill pill-red">❌</span>'
    html += f"""<tr>
<td><b>{fd['name']}</b></td><td>{pg['total']}</td><td>{cw(pg['pct_profitable'])}</td>
<td>{cr(pg['ret_mean'])}</td>
<td>{cr(rs.get('bull_ret_mean'))}</td><td>{cr(rs.get('bear_ret_mean'))}</td>
<td>{judge}</td></tr>"""

html += """</table>

<!-- ═══ Section 7 ═══ -->
<h2 id="s7">7. 历史熊市区间回测（SPY）</h2>"""

html += bear_period_table()

html += """
<div class="insight-good">
<b>关键：策略在5/6个熊市中产生正alpha。</b>核心优势是"熊市空仓能力"——大部分时间不持有，天然避开大跌。
</div>

<!-- ═══ Section 8 ═══ -->
<h2 id="s8">8. 多频率对比 (15m / 1h / 4h / 12h / 1d)</h2>"""

html += multifreq_table()

html += """
<div class="card">
<h3>结论：日线最优，12h次之，短于4h不建议。</h3>
<p>布林带"2倍标准差突破"在日线上是罕见统计异常，在分钟线上太频繁——策略的前提被破坏。</p>
</div>

<!-- ═══ Section 9 ═══ -->
<h2 id="s9">9. 核心结论（v5修订版）</h2>

<div class="insight-good">
<h3>✅ 策略有效（有真实alpha）的场景</h3>
<ul>
<li><b>美股ETF + 科技龙头</b>（SPY/QQQ/MSFT/AAPL）：15年验证，750种参数97%+盈利，牛熊都有alpha</li>
<li><b>中国期货-豆粕</b>：+53%，78.7%参数盈利，季节性均值回复有效</li>
<li><b>中国期货-黄金</b>：+11%，97.2%参数盈利，避险需求提供"底部"</li>
<li><b>中国期货-原油</b>：+8%，OPEC调控使均值回复成立</li>
<li><b>频率：日线或12h</b></li>
</ul>
</div>

<div class="insight-bad">
<h3>❌ 策略无效（无alpha）的场景</h3>
<ul>
<li><b>中国期货-黑色系</b>（铁矿石/螺纹钢/焦炭/焦煤）：结构性下行，均值回复前提不成立</li>
<li><b>中国期货-有色金属</b>（铜/铝/锌）：长周期宏观驱动，日线均值回复捕捉不到</li>
<li><b>中国期货-农产品</b>（棕榈油/白糖）：持续阴跌，抄底反复失败</li>
<li><b>中国期货-碳酸锂</b>：从60万跌到17万，0%参数盈利</li>
<li><b>短周期</b>（15m/1h）：信号噪声比恶化</li>
</ul>
</div>

<div class="card">
<h3>📋 一句话总结（v5最终版）</h3>
<p><b>RSI+布林带均值回复策略在美股上有15年验证的真实alpha（不只靠牛市），在中国期货上只适用于有"外部调节机制"的品种（豆粕/OPEC原油/避险黄金）。大部分中国商品因结构性下行+政策主导，均值回复前提不成立。推荐：美股ETF日线+中轨出场+8%止损；中国期货仅限豆粕/黄金/原油。</b></p>
</div>

<p class="m" style="margin-top:40px;text-align:center">
Rank 444 · RSI+BB 策略 · v5 全品种牛熊分析+中国期货 · {now}<br>
数据来源：Yahoo Finance / akshare(中国期货) · 回测代码：scripts/rank444_v4_regime.py + rank444_v5_cn_futures.py
</p>

</body>
</html>"""

with open(OUT, "w") as f:
    f.write(html)
print(f"✓ 报告写入 {OUT} ({OUT.stat().st_size/1024:.1f}KB)")
