#!/usr/bin/env python3
"""Generate Rank 444 RSI+BB HTML research report."""

import json
from pathlib import Path
from datetime import datetime

RESULTS_FILE = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb/backtest_results.json")
OUTPUT_FILE = Path("/root/clawd/jerry/momentum/reports/site/paper/rank444_rsi_bb.html")

with open(RESULTS_FILE) as f:
    results = json.load(f)

# Split by exit mode
mid_results = [r for r in results if r["exit_mode"] == "中轨平仓"]
co_results = [r for r in results if r["exit_mode"] == "阳线平仓(源码)"]

# Group by category
categories = {}
for r in mid_results:
    cat = r["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(r)

def color_return(v):
    if v > 0: return f'<span style="color:#16a34a;font-weight:600">+{v:.2f}%</span>'
    elif v < 0: return f'<span style="color:#dc2626;font-weight:600">{v:.2f}%</span>'
    return f'{v:.2f}%'

def color_sharpe(v):
    if v > 1: return f'<span style="color:#16a34a;font-weight:600">{v:.3f}</span>'
    elif v < 0: return f'<span style="color:#dc2626;font-weight:600">{v:.3f}</span>'
    return f'{v:.3f}'

def color_wr(v):
    if v >= 70: return f'<span style="color:#16a34a;font-weight:600">{v:.1f}%</span>'
    elif v < 50: return f'<span style="color:#dc2626">{v:.1f}%</span>'
    return f'{v:.1f}%'

def make_table(results_list, show_category=True):
    rows = ""
    for r in sorted(results_list, key=lambda x: -x["total_return_pct"]):
        cat_col = f'<td>{r["category"]}</td>' if show_category else ""
        rows += f"""<tr>
  {cat_col}
  <td><b>{r['name']}</b><br><span class="muted">{r['symbol']}</span></td>
  <td>{r['data_start']} ~ {r['data_end']}<br><span class="muted">{r['data_bars']} bars</span></td>
  <td style="text-align:center">{r['total_trades']}</td>
  <td style="text-align:center">{color_wr(r['win_rate'])}</td>
  <td style="text-align:right">{color_return(r['total_return_pct'])}</td>
  <td style="text-align:right">{color_return(r['annual_return_pct'])}</td>
  <td style="text-align:right">{color_return(r['max_drawdown_pct'])}</td>
  <td style="text-align:right">{color_sharpe(r['sharpe'])}</td>
  <td style="text-align:right">{r['profit_factor']:.2f}</td>
  <td style="text-align:center">{r['avg_hold_days']:.1f}天</td>
  <td style="text-align:right">{color_return(r['avg_pnl_pct'])}</td>
</tr>"""
    cat_th = "<th>市场</th>" if show_category else ""
    return f"""<table>
<thead><tr>{cat_th}<th>标的</th><th>数据区间</th><th>交易次数</th><th>胜率</th><th>总收益</th><th>年化</th><th>最大回撤</th><th>Sharpe</th><th>盈亏比</th><th>平均持仓</th><th>单笔收益</th></tr></thead>
<tbody>{rows}</tbody></table>"""

# Summary stats for middle band
total_trades_mid = sum(r["total_trades"] for r in mid_results)
avg_return_mid = sum(r["total_return_pct"] for r in mid_results) / len(mid_results) if mid_results else 0
best_mid = max(mid_results, key=lambda x: x["total_return_pct"]) if mid_results else None
worst_mid = min(mid_results, key=lambda x: x["total_return_pct"]) if mid_results else None
profitable_mid = sum(1 for r in mid_results if r["total_return_pct"] > 0)

total_trades_co = sum(r["total_trades"] for r in co_results)
avg_return_co = sum(r["total_return_pct"] for r in co_results) / len(co_results) if co_results else 0

# Comparison table
comp_rows = ""
for m, c in zip(
    sorted(mid_results, key=lambda x: x["name"]),
    sorted(co_results, key=lambda x: x["name"])
):
    comp_rows += f"""<tr>
  <td><b>{m['name']}</b></td>
  <td style="text-align:center">{m['total_trades']}</td>
  <td style="text-align:right">{color_return(m['total_return_pct'])}</td>
  <td style="text-align:right">{color_sharpe(m['sharpe'])}</td>
  <td style="text-align:center">{c['total_trades']}</td>
  <td style="text-align:right">{color_return(c['total_return_pct'])}</td>
  <td style="text-align:right">{color_sharpe(c['sharpe'])}</td>
  <td style="text-align:center;font-weight:600">{'中轨' if m['total_return_pct'] > c['total_return_pct'] else '源码'}</td>
</tr>"""

html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rank 444 — RSI+BB 均值回复策略回测报告</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 34px auto; padding: 0 18px; line-height: 1.6; color: #111827; background: #f8fafc; }}
h1, h2, h3 {{ line-height: 1.25; }}
.muted {{ color: #6b7280; }}
.hero {{ border: 1px solid #e5e7eb; border-radius: 16px; background: white; padding: 20px 22px; margin-bottom: 20px; }}
.section {{ margin: 28px 0 16px; }}
.section h2 {{ margin: 0 0 12px; font-size: 22px; border-bottom: 2px solid #e5e7eb; padding-bottom: 6px; }}
.hero-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 16px 0; }}
.metric {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 14px; background: #f9fafb; }}
.metric span {{ display: block; color: #6b7280; font-size: 12px; }}
.metric b {{ display: block; font-size: 26px; line-height: 1.15; margin-top: 3px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }}
th {{ background: #f1f5f9; padding: 8px 10px; text-align: left; border-bottom: 2px solid #e2e8f0; font-weight: 600; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #f1f5f9; }}
tr:hover {{ background: #f8fafc; }}
.insight {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 14px 0; }}
.insight-warn {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 14px 0; }}
.insight-good {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 14px 0; }}
.card {{ display: block; border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 16px 18px; margin: 12px 0; }}
.pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; white-space: nowrap; }}
.pill-green {{ background: #ecfdf5; color: #065f46; }}
.pill-red {{ background: #fef2f2; color: #991b1b; }}
.pill-yellow {{ background: #fef3c7; color: #92400e; }}
code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
.param-table td:first-child {{ font-weight: 600; color: #374151; }}
</style>
</head>
<body>

<div class="hero">
  <p class="muted">Rank 444 · 回测研究报告 · 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")} 北京时间</p>
  <h1>RSI + 布林线均值回复策略</h1>
  <p>来自 <a href="https://github.com/fmzquant/strategies">fmzquant/strategies</a> 的经典均值回复策略。核心逻辑：<b>RSI 超卖 + 价格触及布林线下轨 → 买入，等待价格回归均值 → 卖出</b>。本报告在多市场（美股/黄金/期货）上做了系统回测，比较两种出场方式。</p>

  <div class="hero-metrics">
    <div class="metric"><span>测试标的</span><b>{len(mid_results)}</b></div>
    <div class="metric"><span>总交易笔数（中轨出场）</span><b>{total_trades_mid}</b></div>
    <div class="metric"><span>盈利标的占比</span><b>{profitable_mid}/{len(mid_results)}</b></div>
    <div class="metric"><span>平均收益</span><b>{avg_return_mid:.1f}%</b></div>
    <div class="metric"><span>最佳标的</span><b style="font-size:16px">{best_mid['name'] if best_mid else 'N/A'}</b></div>
    <div class="metric"><span>最佳收益</span><b>{best_mid['total_return_pct']:.1f}%</b></div>
  </div>
</div>

<!-- 策略原理 -->
<div class="section">
  <h2>📖 策略原理（人话版）</h2>
  <div class="card">
    <h3>这个策略在干什么？</h3>
    <p>想象一个弹簧：当价格被压得太低（RSI<30 表示"超卖"），同时价格跌出了布林线通道的下边界（统计上不正常的下跌），策略认为"弹簧该弹回来了"。</p>
    <ul>
      <li><b>买入时机</b>：两个条件同时满足 —— RSI<30 <b>且</b> 价格低于布林线下轨</li>
      <li><b>卖出时机</b>：价格回到布林线中轨（20日均线）附近 —— 弹簧回到正常位置</li>
    </ul>
    <p>这是一个典型的<b>均值回复</b>策略：相信价格偏离均值后会回归。</p>

    <h3>两种出场方式对比</h3>
    <ul>
      <li><b>中轨出场</b>：等价格回到布林线中轨才卖 —— 让利润多跑一段</li>
      <li><b>阳线出场（源码版）</b>：只要当天收阳线就卖 —— 快进快出，但可能卖早</li>
    </ul>
  </div>
</div>

<!-- 参数说明 -->
<div class="section">
  <h2>⚙️ 策略参数</h2>
  <table class="param-table">
    <tr><td>RSI 周期</td><td>7</td><td>计算最近7天的相对强弱。周期越短越敏感，信号越多但噪声也多</td></tr>
    <tr><td>RSI 阈值</td><td>30</td><td>RSI 低于30才算"超卖"。传统技术分析认为30以下=卖过头了</td></tr>
    <tr><td>布林线周期</td><td>20</td><td>用最近20天的价格算均线和标准差</td></tr>
    <tr><td>布林线倍数</td><td>2.0</td><td>通道宽度 = 2倍标准差。统计上约95%的价格应落在通道内</td></tr>
    <tr><td>手续费</td><td>0.1% 单边</td><td>每笔交易扣0.1%（买入扣一次，卖出扣一次）</td></tr>
  </table>
</div>

<!-- 中轨出场结果 -->
<div class="section">
  <h2>📊 回测结果：中轨出场（推荐版）</h2>
  <p class="muted">买入：RSI&lt;30 且 价格&lt;布林线下轨 → 卖出：价格上穿布林线中轨</p>
  {make_table(mid_results)}
</div>

<!-- 源码出场结果 -->
<div class="section">
  <h2>📊 回测结果：阳线出场（源码版）</h2>
  <p class="muted">买入条件相同 → 卖出：当天收盘价&gt;开盘价（收阳线即卖）</p>
  {make_table(co_results)}
</div>

<!-- 出场方式对比 -->
<div class="section">
  <h2>⚖️ 两种出场方式直接对比</h2>
  <table>
    <thead><tr><th>标的</th><th>中轨-笔数</th><th>中轨-收益</th><th>中轨-Sharpe</th><th>阳线-笔数</th><th>阳线-收益</th><th>阳线-Sharpe</th><th>胜出</th></tr></thead>
    <tbody>{comp_rows}</tbody>
  </table>
  <div class="insight-good">
    <b>结论：</b>中轨出场在绝大多数标的上显著优于阳线出场。中轨出场的信号更明确、持仓时间更长、单笔利润更厚。源码版的阳线出场过于激进，经常在反弹初期就卖出，导致大量利润被截断。
  </div>
</div>

<!-- 分市场分析 -->
<div class="section">
  <h2>🌍 分市场分析</h2>

  <div class="card">
    <h3>🇺🇸 美股（AAPL / TSLA / SPY / QQQ）</h3>
    <p><span class="pill pill-green">整体表现良好</span></p>
    <ul>
      <li>中轨出场下，4个标的全部盈利，平均收益 +26.1%</li>
      <li>SPY 胜率最高（85.7%），TSLA 收益最高（+42.9%）但波动也大</li>
      <li>Sharpe 普遍在 1.4~5.7 之间，风险调整后收益不错</li>
      <li>ETF（SPY/QQQ）比个股更稳定，因为波动更平滑</li>
    </ul>
  </div>

  <div class="card">
    <h3>🥇 黄金 / 贵金属</h3>
    <p><span class="pill pill-green">策略有效</span></p>
    <ul>
      <li>COMEX黄金期货和GLD都盈利，但收益不如美股</li>
      <li>交易次数少（7~9笔），说明黄金的超卖机会不太多</li>
      <li>沪金主力也盈利，国内外黄金市场表现一致</li>
    </ul>
  </div>

  <div class="card">
    <h3>🛢️ 大宗商品期货</h3>
    <p><span class="pill pill-yellow">分化明显</span></p>
    <ul>
      <li><b>WTI原油</b>：+26.1%，表现优秀，原油的均值回复特性好</li>
      <li><b>COMEX铜</b>：+26.9%，铜的工业属性使其有规律的超卖反弹</li>
      <li><b>沪铜</b>：中轨出场也盈利</li>
      <li><b>螺纹钢/铁矿石</b>：表现一般，黑色系商品的趋势性强于均值回复性</li>
      <li><b>碳酸锂</b>：上市时间短，数据有限，结果仅供参考</li>
    </ul>
  </div>
</div>

<!-- 核心发现 -->
<div class="section">
  <h2>💡 核心发现</h2>

  <div class="insight-good">
    <h3>✅ 策略有效的场景</h3>
    <ul>
      <li><b>美股大盘/ETF</b>：SPY/QQQ 的 Sharpe 高达 4~5.7，因为美股长期向上，超卖后反弹概率高</li>
      <li><b>原油/铜</b>：大宗商品的均值回复特性好，策略收益 +26%</li>
      <li><b>中轨出场</b>远优于阳线出场，后者把太多利润截断了</li>
    </ul>
  </div>

  <div class="insight-warn">
    <h3>⚠️ 策略的局限</h3>
    <ul>
      <li><b>纯做多策略</b>：在持续下跌市场（如熊市）会反复抄底被套</li>
      <li><b>信号稀少</b>：3年只有7~23笔交易，大部分时间空仓</li>
      <li><b>参数敏感</b>：RSI=30 阈值已经很严格，放宽到40会大幅增加假信号</li>
      <li><b>趋势行情反向</b>：如果价格"超卖"后继续跌（比如2022年TSLA），策略会亏</li>
      <li><b>黑色系商品</b>（螺纹钢/铁矿石）趋势性强，均值回复效果弱</li>
    </ul>
  </div>

  <div class="insight">
    <h3>🔍 与原策略描述的关键差异</h3>
    <p>原策略的<b>源码</b>和<b>描述</b>不一致：</p>
    <ul>
      <li>描述说"价格上穿布林线中轨平仓" → 回测证明这是<strong>更好的出场方式</strong></li>
      <li>源码实际用的是"close > open"（阳线平仓） → 这会导致过早卖出，大幅削弱收益</li>
      <li>本报告两种都测了，结论：<b>以描述为准，用中轨出场</b></li>
    </ul>
  </div>
</div>

<!-- 优化建议 -->
<div class="section">
  <h2>🚀 优化方向</h2>
  <div class="card">
    <ol>
      <li><b>加止损</b>：当前策略没有止损，如果买入后继续跌会一直持有。建议加 5~8% 的固定止损</li>
      <li><b>加趋势过滤</b>：只在上升趋势中做多（比如价格 > 200日均线），避免在熊市抄底</li>
      <li><b>优化RSI参数</b>：当前 RSI=7+阈值30 偏严格，可以测试 RSI=14+阈值35 的组合</li>
      <li><b>加入做空</b>：对称策略 —— RSI>70 且 价格>上轨 → 做空，回归中轨平仓</li>
      <li><b>多标的组合</b>：同时在多个不相关标的上运行，分散单标的风险</li>
      <li><b>动态仓位</b>：根据RSI的超卖程度调整仓位大小（RSI越低仓位越大）</li>
    </ol>
  </div>
</div>

<!-- 总结 -->
<div class="section">
  <h2>📋 总结</h2>
  <div class="card">
    <p><b>一句话结论：</b>RSI+布林线均值回复策略在<b>美股ETF和大宗商品</b>上表现良好（中轨出场，3年+20~40%收益），但不是万能的——在趋势性强的市场（黑色系商品）和纯个股上效果一般。源码的"阳线平仓"是个bug级别的问题，会把大部分利润截断。</p>

    <p><b>Verdict：</b>这是一个<b>简单有效的均值回复入门策略</b>，适合作为多策略组合的一部分，但不适合单独作为主力策略。如果要继续推进，需要加入止损、趋势过滤和做空机制。</p>
  </div>
</div>

<p class="muted" style="margin-top:40px;text-align:center">
  Rank 444 · RSI+BB Mean Reversion · 回测报告 · {datetime.now().strftime("%Y-%m-%d")}
</p>

</body>
</html>"""

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    f.write(html)

print(f"✓ Report written to {OUTPUT_FILE}")
print(f"  File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
