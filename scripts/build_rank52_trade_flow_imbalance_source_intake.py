from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank52_trade_flow_imbalance_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank52_trade_flow_imbalance_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "52",
        "candidate": "trade-flow imbalance veto / aggTrades active buy-sell pressure gate",
        "source": "tsuithomas/crypto_research_order_book_imbalance",
        "source_type": "repo / microstructure pressure proxy / Binance aggTrades-based confirmation filter",
        "why_now": "当前 EMA 仍是 running paper / waiting_not_due，而 Rank 50/51 都已在允许预算内给出 hard verdict 并压回 park。按 authoritative board，这一轮默认必须先回到 fresh paper/repo based 15m crypto intake；在当前 source pool 里，最新 quant digest 对应的主动买卖量失衡 veto 比继续掉回 Rank 35b 更有边际价值，因为它能同时服务 breakout、Fib retest_hold 与 EMA/PSAR continuation 三条现有主线。",
        "trade_on": "保留现有 base setup（breakout-short、Fib retest_hold、EMA/PSAR continuation）负责方向与价位，只把 trade-flow imbalance 当确认层：当 setup 已触发且最近 3~5 分钟主动成交量同向占优（long 要 buy_vol > sell_vol，short 要 sell_vol > buy_vol），才允许放行；更强一档可再要求 |flow_align| 进入最近 20 个 setup 的上半区。",
        "trade_off": "若价格 setup 已触发，但最近 3~5 分钟主动成交量失衡与方向相反，或 flow strength 只剩中性/接近零，则直接 veto；它不能单独开仓，只能负责拒绝明显缺少真实跟随盘的 entry。",
        "honesty_gate": "源码里真正可复刻的是 aggTrades trade-flow imbalance，不是完整 L2 order-book imbalance；这一点必须降级表达。feature_engineering 用 is_buyer_maker 拆主动买/卖量，再用 resample 后的 obi 预测未来 5 分钟收益，时间方向本身是 trailing -> forward，不是一眼可判死刑的 lookahead/repaint；但若迁移到 15m desk，clean replication 必须统一冻结成 setup 前最后几分钟的 flow summary + next-bar open + no-overlap，不能把 setup 后的成交量倒灌回入场判断。",
        "minimal_test": "BTC/ETH/SOL perpetual | 90d~180d | 15m setup + 1m aggTrades micro window | next-bar open | no-overlap；比较 base vs +same_direction_flow_gate vs +strong_flow_gate vs opposite_flow_veto 三臂/四臂，先看 false-break_or_false-hold rate、2/4-bar follow-through、post-cost expectancy@6/10bps、trade_count_retention。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "当前 active fresh Scout 候选里，Rank 52 > Rank 35b。不是因为它已经更强，而是 Rank 35b 仍只是 queue-only fallback；Rank 52 至少是新的 repo-based 15m-adjacent pressure filter，而且能给 breakout/Fib/EMA-PSAR 三条线提供共享的参与度 veto。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 52 1 次最小 clean replication：固定 BTC/ETH/SOL 15m base setups，并用 setup 前最后 3~5 分钟 aggTrades 流量摘要比较 base / same-direction gate / strong-flow gate / opposite-flow veto；若改善主要只在极低成本或样本被砍太狠时成立，就快速压回 park / evidence pool。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank52_trade_flow_imbalance_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 52 · trade-flow imbalance veto source intake</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 980px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px 20px; margin: 16px 0; background: white; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 22px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th, td {{ border-bottom:1px solid #e5e7eb; text-align:left; padding:8px 10px; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
  <h1>Rank 52 · trade-flow imbalance veto</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank52_trade_flow_imbalance_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，没有新的 due-now / overdue lane。</li>
      <li><code>Rank 50</code> 与 <code>Rank 51</code> 都已在允许预算内给出 hard verdict 并压回 <code>park / evidence pool</code>，所以 Scout Seat 不能回头磨旧 intake wording，也不该过早掉到 <code>Rank 35b</code>。</li>
      <li>当前 active fresh Scout 候选的边际价值比较是 <b>Rank 52 &gt; Rank 35b</b>：它不是新大框架，而是给 breakout / Fib / EMA-PSAR 三条现有主线补一个共享的主动成交压力 veto。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>base setup 先负责方向与价位；只有当 setup 已触发，且最近 <code>3~5</code> 分钟主动成交量同向占优时，才允许放行。对 long，要求主动买量占优；对 short，要求主动卖量占优。</li>
      <li><b>trade off：</b>若 flow 与价格方向相反，或 flow 只剩中性/接近零，则直接 veto；它不能单独开仓，只能负责拒绝缺少真实跟随盘的 entry。</li>
      <li><b>lookahead / repaint / leakage 读法：</b>repo 真正可复刻的是 <code>aggTrades trade-flow imbalance</code>，不是完整 L2 深度失衡；当前源码是 trailing flow -> forward return，不是一眼可判死刑的未来函数。但迁移到 15m desk 时必须把 flow window 冻结在 setup 前，统一 <code>next-bar open + no-overlap</code>，不能把 setup 后成交量倒灌回入场判断。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 guard-passed</h2>
    <table>
      <tr><th>真实优点</th><td>它不是再堆一层价格确认，而是补一个更贴近因果的“有没有真跟随盘”压力层，可同时服务 breakout、Fib retest_hold 与 EMA/PSAR continuation。</td></tr>
      <tr><th>关键保留</th><td>repo README 的正收益依赖 maker + threshold 假设；这更支持把它当 15m filter / veto，而不支持直接把它吹成主 alpha。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但如果只有极低成本或极端砍样本才好看，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL</code> 的 15m base setup 与最小 aggTrades micro window。</li>
      <li>统一冻结成 <code>setup 前最后 3~5 分钟 flow summary + next-bar open + no-overlap</code>。</li>
      <li>只比较最小四臂：<code>base</code>、<code>+same_direction_flow_gate</code>、<code>+strong_flow_gate</code>、<code>opposite_flow_veto</code>。</li>
      <li>先回答四个便宜问题：<code>false-break/false-hold rate</code>、<code>2/4-bar follow-through</code>、<code>post-cost expectancy</code>、<code>trade_count_retention</code>。</li>
      <li>默认不允许：一上来扩成 ML 预测器、盘口大框架，或同时再开第二条 fresh intake。</li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ROWS)
    HTML_PATH.write_text(HTML, encoding="utf-8")


if __name__ == "__main__":
    main()
