from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank56_liquidation_map_path_overlay_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank56_liquidation_map_path_overlay_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "56",
        "candidate": "liquidation-map path overlay / cluster path score",
        "source": "aoki-h-jp/py-liquidation-map",
        "source_type": "repo / liquidation-path overlay / 15m adaptable",
        "why_now": "当前 EMA 仍是 running paper / waiting_not_due，Rank 55 已完成最小 clean replication 并落到 P1 weak candidate / evidence pool；按顶板规则 Run 2 必须继续 fresh paper/repo intake，而不是回头挤占 P3 continuity。当前允许动作里，Rank 56 比 Rank 55 的那 1 次便宜检查更优先，因为它是新的 shared path/risk overlay，可同时服务 breakout-short / Fib retest_hold / EMA-PSAR 三条现有主线。",
        "trade_on": "base setup 继续负责方向与价位；liquidation map 只负责回答入场后前方路况：long 侧看上方 short-liquidation fuel 相对下方 long-cascade trap 是否更占优，short 侧镜像。只有当 signal 前窗口推导出的 cluster_path_score 明显顺着 base 方向，才允许把它作为 path gate 或 size tilt。",
        "trade_off": "若 cluster_path_score 接近中性、前方顺势 fuel 不明显、或反方向 liquidation trap 更近，则 overlay 只能 veto / 降仓，不能单独开仓；它也不能把 liquidation 图误写成逐根 15m 方向预测。",
        "honesty_gate": "repo 的核心骨架是把公开 aggTrades 中的大额主动成交映射到固定杠杆假设下的潜在 loss-cut 价位：Buy 映射到 0.99/0.98/0.96/0.90 倍价位，Sell 映射到 1.01/1.02/1.04/1.10 倍价位，并支持 >=100k USDT / top_n / top 1% 三种筛选模式。源码层没有一眼可判死刑的 lookahead / repaint；但 desk 迁移时必须把全部 cluster 统计严格冻结在 signal 前 6h/24h 窗口，统一 next-bar open + no-overlap，并明确这只是 crowding/path proxy，不是真实 liquidation tape。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | 复用现有 breakout_short / fib_retest_long / ema_psar_long 三条 archetype；对 signal 前 6h/24h 的 aggTrades 计算 cluster_path_score，先比较 base / +binary path gate / +size tilt 三臂；先看 post_cost_return@6bps、false_follow_through_4bars、trade_count_retention、positive_asset_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "当前允许动作里，Rank 56 > Rank 55 的便宜时间稳定性检查 > Rank 35b > Rank 16b > tiny-live plumbing。原因不是 Rank 56 已被验证，而是它是新的 repo-based shared overlay，且复用公开 aggTrades 即可做诚实最小测试；相比之下，Rank 55 已进入 evidence pool，只剩 1 次便宜检查预算。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 56 1 次最小 clean replication：固定 BTC/ETH/SOL 15m cache，把 cluster 统计冻结在 signal 前窗口，先回答真正有增量的是顺势 fuel gate，还是反向 trap veto；若改善只来自极端砍样本或跨资产不稳，就快速压回 park / evidence pool。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 56 · liquidation-map path overlay source intake</title>
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
  <h1>Rank 56 · liquidation-map path overlay / cluster path score</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank56_liquidation_map_path_overlay_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，没有新的 due-now / overdue lane。</li>
      <li><code>Rank 55</code> 已完成最小 clean replication，并落到 <code>P1 weak candidate / evidence pool</code>；它还有 1 次便宜检查预算，但按顶板顺序，新的 fresh repo intake 仍优先于回头磨旧证据池。</li>
      <li>当前允许动作里的边际价值比较是 <b>Rank 56 &gt; Rank 55 的便宜检查 &gt; Rank 35b &gt; Rank 16b &gt; tiny-live plumbing</b>：它不是第四条新主线，而是能横向服务 <code>breakout-short</code>、<code>Fib retest_hold</code> 与 <code>EMA / PSAR</code> 的 shared path/risk overlay。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>base setup 继续负责方向与价位；liquidation map 只负责回答“前方顺势清算燃料是否明显强于反方向陷阱”。long 侧看上方 <code>short-liquidation fuel</code> 相对下方 <code>long-cascade trap</code> 是否更占优，short 侧镜像。</li>
      <li><b>trade off：</b>若 <code>cluster_path_score</code> 接近中性、顺势 fuel 不明显、或反方向 trap 更近，则 overlay 只能 veto / 降仓，不能单独开仓；它不是逐根 15m 方向神图。</li>
      <li><b>lookahead / repaint / leakage 读法：</b>repo 的核心只是把公开 <code>aggTrades</code> 中的大额主动成交映射到固定杠杆假设下的潜在 loss-cut 价位（Buy → <code>0.99/0.98/0.96/0.90</code>；Sell → <code>1.01/1.02/1.04/1.10</code>），源码层没有一眼可判死刑的未来函数；但 clean replication 必须把 cluster 统计严格冻结到 <code>signal 前 6h/24h 窗口 + next-bar open + no-overlap</code>，不能把 signal 后成交倒灌回 path score。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 guard-passed</h2>
    <table>
      <tr><th>真实优点</th><td>它不是新 entry 框架，而是给三条现有主线补一个共享的路径/仓位 overlay：前方有顺势燃料，还是反向陷阱更近。</td></tr>
      <tr><th>关键保留</th><td>repo 画的是基于大额主动成交与固定杠杆假设的 liquidation proxy，不是真实 liquidation tape；最容易出错的是把图像直觉误写成 alpha，或把 signal 后成交倒灌进评分。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但若改善只是来自极端砍样本、跨资产不稳，或只在单一 archetype 上有效，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache。</li>
      <li>对 signal 前 <code>6h / 24h</code> 的 <code>aggTrades</code> 计算 <code>cluster_path_score</code>。</li>
      <li>只比较三个最小臂：<code>base</code>、<code>+binary path gate</code>、<code>+size tilt</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_follow_through_4bars</code>、<code>trade_count_retention</code>、<code>positive_asset_ratio</code>。</li>
      <li>默认不允许：把 liquidation 热力图扩成大研究、追最新 bar、或同时再开第二条 fresh intake。</li>
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
