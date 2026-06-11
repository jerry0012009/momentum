from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank51_vwap_trend_defense_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank51_vwap_trend_defense_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "51",
        "candidate": "vwap-trend-defense / session VWAP reclaim + above-VWAP breadth gate",
        "source": "JinHwaChiu/vwap-trend-defense",
        "source_type": "repo / Python strategy / session VWAP reclaim confirmation skeleton",
        "why_now": "当前 EMA 已重新回到 running paper / waiting_not_due，而 Rank 49/50 也都在允许预算内给出 hard verdict 后压回 park；按最新 authoritative board，本轮应先比较 active fresh Scout 候选，再只认领 Rank 51 的 source intake，而不是直接掉回 Rank 35b / tiny-live plumbing。当前 fresh 队列里，Rank 51 虽然比 Rank 50 更依赖 session 迁移，但仍高于 queue-only 的 Rank 35b。",
        "trade_on": "保留现有 breakout / Fib retest_hold / EMA-PSAR continuation 作为 base setup；只有当价格先回踩 session VWAP 附近，然后 close 重新站回 VWAP 上方（short 则重新跌回 VWAP 下方），且最近 4~6 根里超过半数 close 仍站在 VWAP 强侧，才允许把这次回踩/反抽视为 defense-confirmed continuation。",
        "trade_off": "若价格只是碰到 VWAP 但没有 reclaim，或 recent breadth 已明显掉到 VWAP 弱侧（例如最近 4~6 根里不足半数站在强侧），则不交易；若 base setup 本身已失效（例如 Fib reclaim 被重新跌回 0.5 下方、EMA/PSAR 方向翻转、breakout retest 失守），VWAP defense 也不能单独救活这笔交易。",
        "honesty_gate": "repo 里的 VWAP / breadth / reclaim 逻辑本身可写成清楚的 trade on / trade off，没有一眼可判死刑的 lookahead / repaint / leakage；但它原始语境是 ES/MES session-long 模板，迁移到 24/7 crypto 时必须把 session 明确冻结成 UTC 日内重置 VWAP，并统一使用 next-bar open + no-overlap，避免把 bar-close reclaim 与同 bar fill 混成乐观成交。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | UTC session VWAP reset | next-bar open | no-overlap；比较 base_retetst_or_continuation vs +vwap_reclaim vs +vwap_reclaim+breadth_gate 三臂；先看 post_cost_return / false_retest_rate / trade_count_retention / positive_asset_ratio。",
        "desk_fit": "medium-high",
        "marginal_value_vs_other_active_scouts": "当前 active fresh Scout 队列里，Rank 51 > Rank 35b。原因不是它已更强，而是 Rank 35b 仍只是 queue-only fallback；Rank 51 至少是新的 repo-based 15m confirmation skeleton，且能同时服务 Fib retest_hold 与 EMA/PSAR continuation 两条现有 desk 主线。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 51 1 次最小 clean replication：固定 BTC/ETH/SOL 15m cache，把 session 明确冻结成 UTC VWAP，先回答真正有增量的是 reclaim 本身，还是 reclaim+breadth；若改善主要来自砍样本而不是降低 false-retest，就快速压回 park / evidence pool。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank51_vwap_trend_defense_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 51 · vwap-trend-defense source intake</title>
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
  <h1>Rank 51 · session VWAP reclaim + breadth gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank51_vwap_trend_defense_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，没有新的 due-now / overdue lane。</li>
      <li><code>Rank 49</code> 与 <code>Rank 50</code> 都已在允许预算内给出 hard verdict 并压回 <code>park / evidence pool</code>，因此 Scout Seat 必须继续沿 fresh repo intake 往前走，而不是提前掉回 <code>Rank 35b</code>。</li>
      <li>当前 active fresh Scout 候选的边际价值比较是 <b>Rank 51 &gt; Rank 35b</b>：它虽然有 session 迁移风险，但至少是新的 repo-based 15m confirmation skeleton，而且直接服务 <code>Fib retest_hold</code> 与 <code>EMA / PSAR continuation</code> 两条主线。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>先保留 base setup（例如 <code>Fib retest_hold</code>、<code>EMA/PSAR continuation</code>、<code>breakout retest</code>），只有当价格回踩 <code>session VWAP</code> 后重新 <code>reclaim</code> 到强侧，且最近 <code>4~6</code> 根里多数 close 仍站在 VWAP 强侧，才允许入场。</li>
      <li><b>trade off：</b>只碰到 VWAP 但没有 reclaim、recent breadth 已掉到弱侧、或 base setup 本身已经失效时，不交易；VWAP defense 只是确认层，不能单独把已失效 setup 救活。</li>
      <li><b>lookahead / repaint / leakage 读法：</b>VWAP 与 breadth 都能做成 trailing 计算，没有一眼可判死刑的未来函数；但 clean replication 必须把 session 明确冻结成 <code>UTC 日内重置 VWAP</code>，并统一 <code>next-bar open + no-overlap</code>，避免同 bar reclaim + 同 bar fill 的乐观写法。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 guard-passed</h2>
    <table>
      <tr><th>真实优点</th><td>它不是新大框架，而是给现有 retest/continuation setup 补一个更像“防守有没有重新站稳”的确认层。</td></tr>
      <tr><th>关键保留</th><td>原 repo 的主语境是 ES/MES session-long 模板，迁移到 24/7 crypto 时最容易过拟合的不是 VWAP 本身，而是 <code>session 定义</code> 与 breadth 窗口。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但若改善主要来自砍样本而不是降低 false-retest，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache。</li>
      <li>统一冻结成 <code>UTC session VWAP + next-bar open + no-overlap</code>。</li>
      <li>先比较三个最小臂：<code>base_setup</code>、<code>+vwap_reclaim</code>、<code>+vwap_reclaim+breadth_gate</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_retest_rate</code>、<code>trade_count_retention</code>、<code>positive_asset_ratio</code>。</li>
      <li>默认不允许：一上来扩成 session 微切片大研究、追最新 bar、或同时再开第二条 fresh intake。</li>
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
