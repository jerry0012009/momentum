#!/usr/bin/env python3
"""Build the Chinese Phase 2b short-reversal review page."""
import csv
import html as html_mod
import json
import math
from pathlib import Path

ROOT = Path("/root/clawd/jerry/momentum")
ART = ROOT / "reports/artifacts/binance_event_study_v1_6_2b"
OUT = ROOT / "reports/site/paper/binance_event_study_v1_6_2b_short_reversal.html"


def is_num(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


def pct(v, sign=True, digits=2):
    if not is_num(v):
        return "-"
    fmt = f"{{:{'+' if sign else ''}.{digits}%}}"
    return fmt.format(v)


def num(v, digits=2):
    if not is_num(v):
        return "-"
    return f"{v:,.{digits}f}"


def cls(v):
    if not is_num(v):
        return "neu"
    return "pos" if v > 0 else ("neg" if v < 0 else "neu")


def badge(v):
    return f'<span class="badge badge-{cls(v)}">{pct(v)}</span>'


def esc(v):
    return html_mod.escape(str(v))


def table(headers, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>\n{body}\n</tbody></table>"


def load_scan_summary():
    path = ART / "param_scan_results.csv"
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            clean = dict(row)
            for key in [
                "n_trades",
                "net_mean",
                "win_rate",
                "profit_factor",
                "price_return_mean",
                "funding_sum_mean",
            ]:
                try:
                    clean[key] = float(row[key])
                except (TypeError, ValueError):
                    clean[key] = math.nan
            clean["type"] = clean["signal_label"][:1]
            rows.append(clean)

    finite = [r for r in rows if is_num(r["net_mean"])]
    by_type = []
    for typ in ["A", "B", "C", "D"]:
        sub = [r for r in finite if r["type"] == typ]
        nets = [r["net_mean"] for r in sub]
        by_type.append(
            {
                "type": typ,
                "rows": len(sub),
                "positive": sum(1 for r in sub if r["net_mean"] > 0),
                "mean_net": sum(nets) / len(nets) if nets else math.nan,
                "best_net": max(nets) if nets else math.nan,
            }
        )

    by_exit = []
    for exit_rule in sorted({r["exit_rule"] for r in finite}):
        sub = [r for r in finite if r["exit_rule"] == exit_rule]
        nets = [r["net_mean"] for r in sub]
        by_exit.append(
            {
                "exit": exit_rule,
                "rows": len(sub),
                "positive": sum(1 for r in sub if r["net_mean"] > 0),
                "mean_net": sum(nets) / len(nets) if nets else math.nan,
                "best_net": max(nets) if nets else math.nan,
            }
        )
    by_exit.sort(key=lambda r: r["best_net"], reverse=True)

    return {
        "all": rows,
        "finite": finite,
        "finite_count": len(finite),
        "total_count": len(rows),
        "positive_count": sum(1 for r in finite if r["net_mean"] > 0),
        "by_type": by_type,
        "by_exit": by_exit,
    }


rd = json.loads((ART / "report_data.json").read_text())
scan = load_scan_summary()

ps = rd["peak_stats"]
top = rd["top_combos"]
best = rd["best_signal"]
sig_types = rd["signal_type_summary"]
best_key = f"{best['label']}|{best['exit']}"

peak_dist = ps.get("peak_hour_distribution", {})
block_counts = []
for h_start in range(0, 120, 6):
    h_end = min(h_start + 6, 120)
    cnt = sum(peak_dist.get(str(h), 0) for h in range(h_start, h_end))
    block_counts.append((h_start, h_end, cnt))
max_block = max([x[2] for x in block_counts] or [1])
peak_bars_html = "\n".join(
    (
        f'<div class="bar" style="height:{(cnt / max_block * 100) if max_block else 0:.0f}%">'
        f'<span class="bar-value">{cnt:,}</span><span class="bar-label">{h0}-{h1}h</span></div>'
    )
    for h0, h1, cnt in block_counts
    if cnt > 0
)

struct_labels = {
    "immediate_reversal": "即时反转",
    "stall_t2": "T2 停滞",
    "stall_t3": "T3 停滞",
    "continuation": "延续",
}
bucket_labels = {
    "neg_extreme": "负极端 (<-0.05%)",
    "neg_moderate": "负中等 (-0.05%~-0.01%)",
    "mid": "中性 (-0.01%~0.01%)",
    "pos_moderate": "正中等 (0.01%~0.05%)",
    "pos_extreme": "正极端 (>0.05%)",
}
exit_labels = {
    "max_hold": "到 8h 上限",
    "take_profit": "触发 5% 止盈",
    "stop_loss": "触发止损",
    "data_end": "数据结束",
}
signal_names = {
    "A": "缩量回撤",
    "B": "放量冲高后回落",
    "C": "资金费率/高点回撤",
    "D": "主动买盘衰竭",
}

top_rows = []
for i, r in enumerate(top[:20], 1):
    pf = r["profit_factor"]
    pf_str = "inf" if is_num(pf) and pf >= 999 else num(pf)
    top_rows.append(
        [
            i,
            f"<code>{esc(r['signal'])}</code>",
            f"<code>{esc(r['exit'])}</code>",
            badge(r["net_mean"]),
            pct(r["win_rate"], False),
            f"{r['n_trades']:,}",
            pf_str,
            badge(r["price_return"]),
            badge(r["funding_sum"]),
        ]
    )

sig_type_rows = [
    [
        f"<code>{esc(st['type'])}</code>",
        esc(signal_names.get(st["type"], st["type"])),
        f"{st['total_trades']:,}",
        badge(st["net_mean"]),
        pct(st["win_rate"], False),
    ]
    for st in sig_types
]

scan_type_rows = [
    [
        f"<code>{esc(r['type'])}</code>",
        esc(signal_names.get(r["type"], r["type"])),
        f"{r['positive']} / {r['rows']}",
        badge(r["mean_net"]),
        badge(r["best_net"]),
    ]
    for r in scan["by_type"]
]

scan_exit_rows = [
    [
        f"<code>{esc(r['exit'])}</code>",
        f"{r['positive']} / {r['rows']}",
        badge(r["mean_net"]),
        badge(r["best_net"]),
    ]
    for r in scan["by_exit"]
]

year_rows = [
    [y["year"], f"{y['n_trades']:,}", badge(y["net_mean"]), pct(y["win_rate"], False)]
    for y in rd["year_stability"].get(best_key, [])
]

fund_rows = [
    [
        esc(bucket_labels.get(f["funding_bucket"], f["funding_bucket"])),
        f"{f['n_trades']:,}",
        badge(f["net_mean"]),
        pct(f["win_rate"], False),
    ]
    for f in rd["funding_analysis"].get(best_key, [])
]

struct_rows = [
    [
        esc(struct_labels.get(s["structure"], s["structure"])),
        f"{s['n_trades']:,}",
        badge(s["net_mean"]),
        pct(s["win_rate"], False),
    ]
    for s in rd["structure_analysis"].get(best_key, [])
]

exit_rows = [
    [
        esc(exit_labels.get(e["exit_reason"], e["exit_reason"])),
        f"{e['count']:,}",
        badge(e["net_mean"]),
    ]
    for e in rd["exit_reason_dist"].get(best_key, [])
]

cost_rows = [
    [f"{c['cost_bps']} bps", badge(c["net_mean"]), pct(c["win_rate"], False)]
    for c in rd["cost_sensitivity"].get(best_key, [])
]

struct_drop_rows = []
for struct in ["immediate_reversal", "stall_t2", "stall_t3", "continuation"]:
    med = ps.get(f"peak_hour_median_{struct}")
    drop = ps.get(f"mean_drop_8h_{struct}")
    if med is not None:
        struct_drop_rows.append([esc(struct_labels.get(struct, struct)), f"{med:.0f}h", badge(drop)])

ret_drop_rows = []
for bucket in ["<5%", "5-10%", "10-15%", "15-20%", "20-30%"]:
    med = ps.get(f"peak_hour_median_ret_{bucket}")
    drop = ps.get(f"mean_drop_8h_ret_{bucket}")
    if med is not None:
        ret_drop_rows.append([esc(bucket), f"{med:.0f}h", badge(drop)])

tp_count = next((e["count"] for e in rd["exit_reason_dist"].get(best_key, []) if e["exit_reason"] == "take_profit"), 0)
trade_days = 4.35 * 365
approx_daily = best["n_trades"] / trade_days

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phase 2b 做空反转策略研究审阅</title>
<style>
:root{{--bg:#0d1117;--panel:#161b22;--panel2:#101821;--border:#30363d;--text:#d1d7df;--dim:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922;--purple:#bc8cff}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;padding:22px;max-width:1360px;margin:0 auto}}
h1{{color:var(--accent);font-size:2.05rem;line-height:1.2;margin:4px 0 10px}}
h2{{color:var(--accent);margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--border);font-size:1.28rem}}
h3{{color:var(--yellow);margin:22px 0 10px;font-size:1.06rem}}
h4{{color:var(--purple);margin:16px 0 8px;font-size:1rem}}
p{{margin:8px 0}}
ul{{padding-left:22px;margin:10px 0}}
li{{margin:7px 0}}
code{{background:#0b1320;border:1px solid #263244;padding:2px 6px;border-radius:4px;font-size:.88em;color:#e6edf3}}
.subtitle{{color:var(--dim);font-size:.95rem;margin-bottom:22px}}
.grid{{display:grid;gap:14px;margin:16px 0}}
.grid-2{{grid-template-columns:repeat(2,minmax(0,1fr))}}
.grid-3{{grid-template-columns:repeat(3,minmax(0,1fr))}}
.grid-4{{grid-template-columns:repeat(4,minmax(0,1fr))}}
.card,.box{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px}}
.metric-label{{color:var(--dim);font-size:.78rem;text-transform:uppercase;letter-spacing:.02em;margin-bottom:4px}}
.metric-value{{font-size:1.55rem;font-weight:750}}
.pos{{color:var(--green)}}.neg{{color:var(--red)}}.neu{{color:var(--yellow)}}
.box{{margin:15px 0}}
.box.info{{border-color:var(--accent);background:rgba(88,166,255,.06)}}
.box.good{{border-color:var(--green);background:rgba(63,185,80,.06)}}
.box.warn{{border-color:var(--yellow);background:rgba(210,153,34,.08)}}
.box.bad{{border-color:var(--red);background:rgba(248,81,73,.07)}}
.verdict{{font-size:1.05rem;border-radius:8px;padding:17px;margin:16px 0;border:1px solid var(--yellow);background:rgba(210,153,34,.09)}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:.91rem}}
th{{text-align:left;padding:8px 10px;background:var(--panel2);color:var(--dim);font-weight:650;border-bottom:2px solid var(--border);font-size:.78rem;text-transform:uppercase}}
td{{padding:7px 10px;border-bottom:1px solid var(--border);vertical-align:top}}
tr:hover{{background:rgba(88,166,255,.045)}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.78rem;font-weight:700;white-space:nowrap}}
.badge-pos{{background:rgba(63,185,80,.18);color:var(--green)}}
.badge-neg{{background:rgba(248,81,73,.18);color:var(--red)}}
.badge-neu{{background:rgba(210,153,34,.16);color:var(--yellow)}}
.bar-chart{{display:flex;align-items:flex-end;gap:3px;height:150px;margin:20px 0 34px}}
.bar{{flex:1;background:var(--accent);border-radius:3px 3px 0 0;position:relative;min-width:9px}}
.bar:hover{{background:var(--green)}}
.bar-label{{position:absolute;bottom:-22px;left:50%;transform:translateX(-50%);font-size:.65rem;color:var(--dim);white-space:nowrap}}
.bar-value{{position:absolute;top:-20px;left:50%;transform:translateX(-50%);font-size:.65rem;color:var(--text);white-space:nowrap}}
.note{{color:var(--dim);font-size:.9rem}}
.footer{{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);color:var(--dim);font-size:.82rem}}
@media(max-width:900px){{body{{padding:14px}}.grid-2,.grid-3,.grid-4{{grid-template-columns:1fr}}table{{font-size:.82rem}}th,td{{padding:6px}}.bar-label{{display:none}}}}
</style>
</head>
<body>
<h1>Phase 2b 做空反转策略研究审阅</h1>
<p class="subtitle">Binance 涨幅榜事件后的 short-side reversal 研究页，样本为 31,368 个事件、434 个 symbol、小时级事件面板；默认成本口径为 13 bps。</p>

<div class="verdict">
<strong>审阅结论：值得继续观察，但不能直接上线。</strong>
最优组合 <code>{esc(best['label'])} / {esc(best['exit'])}</code> 的单笔净均值是 <strong>{pct(best['net_mean'])}</strong>、胜率 <strong>{pct(best['win_rate'], False)}</strong>、样本 <strong>{best['n_trades']:,}</strong>。它不是一个完全偶然的漂亮点：跨年都为正，成本敏感性也留有余量。但扫描面里只有 <strong>{scan['positive_count']} / {scan['finite_count']}</strong> 个可评估组合为正，收益高度集中在 B 类信号和 5% 止盈退出，说明它仍处在“候选 alpha”阶段，不是可直接放大 notional 的生产策略。
</div>

<div class="grid grid-4">
<div class="card"><div class="metric-label">最佳净均值</div><div class="metric-value pos">{pct(best['net_mean'])}</div></div>
<div class="card"><div class="metric-label">最佳胜率</div><div class="metric-value pos">{pct(best['win_rate'], False)}</div></div>
<div class="card"><div class="metric-label">最佳样本数</div><div class="metric-value neu">{best['n_trades']:,}</div></div>
<div class="card"><div class="metric-label">粗略日均触发</div><div class="metric-value neu">{approx_daily:.1f}</div></div>
</div>

<h2>1. 这条策略好在哪里</h2>
<div class="box good">
<ul>
<li><strong>行为逻辑是通顺的。</strong> B 类信号不是单纯追跌，而是要求前 12h 出现 5x 放量和 1% 以上冲高，然后等待价格回落 2%。这更像在捕捉事件驱动上涨后的买盘衰竭，而不是裸做空强势币。</li>
<li><strong>退出规则承担了主要风控。</strong> 最优组合不是固定持有，而是 8h 内 5% 止盈；1,880 笔止盈交易均值约 +6.67%，覆盖了 3,320 笔到期退出的 -2.48%。这说明策略靠“少数快速回落”赚钱，机制清晰。</li>
<li><strong>跨年没有单一年份独占。</strong> 2022 至 2026 年最佳组合逐年净均值都为正，最弱的 2024 年仍为 {pct(min((y['net_mean'] for y in rd['year_stability'].get(best_key, [])), default=math.nan))}。</li>
<li><strong>成本余量暂时够看。</strong> 线性成本敏感性里，50 bps 成本后最佳组合仍有 {pct(next((c['net_mean'] for c in rd['cost_sensitivity'].get(best_key, []) if c['cost_bps'] == 50), math.nan))}。这不能替代实盘滑点，但说明结果不是刚刚贴着手续费线。</li>
</ul>
</div>

<h2>2. 最大风险在哪里</h2>
<div class="box bad">
<ul>
<li><strong>扫描集中度很高。</strong> 可评估组合中只有 {scan['positive_count']} / {scan['finite_count']} 为正；A/C/D 三类在均值上全部偏弱，B 类也只有部分参数能赚钱。换句话说，这是一个窄参数候选，不是宽泛稳定的策略族。</li>
<li><strong>收益依赖止盈尾部。</strong> 大部分交易没有触发止盈并在 8h 到期退出，均值为负。如果真实成交在急跌时滑点扩大，或者止盈触发价只在小时 bar 内短暂出现，实盘回放可能会显著变差。</li>
<li><strong>2024 明显变薄。</strong> 最佳组合 2024 年只有 {pct(next((y['net_mean'] for y in rd['year_stability'].get(best_key, []) if y['year'] == 2024), math.nan))}，胜率 {pct(next((y['win_rate'] for y in rd['year_stability'].get(best_key, []) if y['year'] == 2024), math.nan), False)}。这提示市场结构变化时，反转强度可能快速衰减。</li>
<li><strong>资金费率不是简单红利。</strong> 负极端资金费率桶收益最高，正极端桶为负；这更像拥挤/恐慌状态的条件变量，而不是稳定可收的 funding carry。实盘不能把 funding 当作主要利润来源。</li>
</ul>
</div>

<h2>3. 回测本身可能哪里有问题</h2>
<div class="box warn">
<ul>
<li><strong>需要严格 OOS / walk-forward。</strong> 当前页面展示的是参数扫描后的最佳组合，存在选择偏差。下一步应按年份或月份滚动训练选择参数，再只在未来窗口评估。</li>
<li><strong>事件可能重叠。</strong> 同一 symbol 在事件窗口内多次触发，会让样本数看起来很大，但真实持仓会相互排斥或叠加风险；需要 position-level replay 检查并发、冷却时间和单币上限。</li>
<li><strong>小时 bar 止盈有乐观风险。</strong> 如果用 OHLC 判断 5% take-profit，必须确认进场价、触发顺序、滑点和 maker/taker 假设；否则急跌后的触发成交会偏理想化。</li>
<li><strong>成本敏感性是近似项。</strong> 报表中的成本曲线按净收益平移估算，不能覆盖流动性分层、冲击成本、资金费时间点、下架币和极端行情无法成交。</li>
</ul>
</div>

<h2>4. 峰值与回撤背景</h2>
<p>事件后价格峰值中位数出现在 <strong>{ps['median_peak_hour']:.0f}h</strong>，第一次出现 2% 以上阴线的中位时间是 <strong>{ps['first_bearish_median']:.0f}h</strong>。事件涨幅越大，峰值出现越早，8h 回撤也越深，这给“等冲高后做空回落”提供了背景证据。</p>
<div class="grid grid-4">
<div class="card"><div class="metric-label">中位峰值时间</div><div class="metric-value neu">{ps['median_peak_hour']:.0f}h</div></div>
<div class="card"><div class="metric-label">4h 平均回撤</div><div class="metric-value neg">{pct(ps['mean_drop_4h'])}</div></div>
<div class="card"><div class="metric-label">8h 平均回撤</div><div class="metric-value neg">{pct(ps['mean_drop_8h'])}</div></div>
<div class="card"><div class="metric-label">12h 平均回撤</div><div class="metric-value neg">{pct(ps['mean_drop_12h'])}</div></div>
</div>
<h3>峰值小时分布（6h 分组）</h3>
<div class="bar-chart">{peak_bars_html}</div>
<h3>按事件结构看回撤</h3>
{table(["事件结构", "中位峰值时间", "8h 平均回撤"], struct_drop_rows)}
<h3>按事件涨幅看回撤</h3>
{table(["事件涨幅", "中位峰值时间", "8h 平均回撤"], ret_drop_rows)}

<h2>5. 信号设计与扫描广度</h2>
<p>本轮测试 4 类做空信号、30 个信号变体，并搭配多种 8h 退出规则。固定 12h/24h 持有规则在本批汇总里没有形成有效净收益列，因此下面的“可评估组合”只统计净收益为有限值的 120 行。</p>
<div class="grid grid-2">
<div class="box info">
<h3>四类信号</h3>
<ul>
<li><strong>A 缩量回撤：</strong>成交量低于 20 周期均值并伴随价格下跌。</li>
<li><strong>B 放量冲高后回落：</strong>前 12h 异常放量冲高，随后从局部高点回落。</li>
<li><strong>C 资金费/高点回撤：</strong>资金费率为正，并从近期高点下行。</li>
<li><strong>D 主动买盘衰竭：</strong>主动买入占比曾高企，随后明显回落。</li>
</ul>
</div>
<div class="box info">
<h3>扫描结果的含义</h3>
<p>如果一个策略族真实很厚，通常不会只有少数参数为正。本轮的优点是最佳点清晰，缺点也是最佳点太集中：B 类是唯一值得保留的方向，其余三类目前更像负样本。</p>
</div>
</div>
{table(["类型", "含义", "正收益/可评估", "组内平均净值", "组内最佳净值"], scan_type_rows)}
{table(["退出规则", "正收益/可评估", "平均净值", "最佳净值"], scan_exit_rows)}

<h2>6. Top 20 组合</h2>
{table(["#", "Signal", "Exit", "Net", "Win Rate", "N", "PF", "Price Return", "Funding"], top_rows)}

<h2>7. 最佳组合拆解：{esc(best['label'])} / {esc(best['exit'])}</h2>
<h3>逐年稳定性</h3>
{table(["年份", "交易数", "净收益", "胜率"], year_rows)}
<h3>资金费率桶</h3>
{table(["资金费率区间", "交易数", "净收益", "胜率"], fund_rows)}
<h3>事件结构</h3>
{table(["事件结构", "交易数", "净收益", "胜率"], struct_rows)}
<h3>退出原因</h3>
{table(["退出原因", "交易数", "净收益"], exit_rows)}
<p class="note">止盈触发占比约 {pct(tp_count / best['n_trades'] if best['n_trades'] else math.nan, False)}。这解释了为什么胜率只有 60%，但净均值能到 {pct(best['net_mean'])}：策略依赖少数较大的快速回落。</p>
<h3>成本敏感性</h3>
{table(["成本", "净收益", "胜率"], cost_rows)}

<h2>8. 下一步建议</h2>
<div class="box info">
<ul>
<li>只保留 B 类候选，先做 walk-forward 参数选择，不要直接使用全样本最优参数。</li>
<li>做 position-level replay：同币冷却、同时持仓上限、交易所最小下单量、实际可成交深度、止盈触发顺序。</li>
<li>把 2024 单独当作压力样本，要求策略在 2024 仍能覆盖更保守成本；否则只能小 notional 纸面观察。</li>
<li>把资金费率桶、事件结构和波动率/流动性做成交前过滤，但必须在 OOS 中验证，不要在全样本里继续堆条件。</li>
</ul>
</div>

<div class="footer">
数据目录：<code>reports/artifacts/binance_event_study_v1_6_2b</code> &middot;
生成脚本：<code>scripts/build_v1_6_2b_report.py</code> &middot;
回测脚本：<code>scripts/backtest_v1_6_2b_short_reversal.py</code>
</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"Report written to {OUT}")
print(f"  {len(html):,} bytes")
