from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank110_psar_preflip_dot_reclaim_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank110_psar_preflip_dot_reclaim_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "110",
        "candidate": "PSAR pre-flip SAR dot reclaim gate",
        "source": "hasnocool/tradingview-pine-scripts + 2026-03-20 03:54 digest",
        "source_type": "repo / continuation admission filter / crypto 15m adaptable",
        "why_now": "当前 EMA due-check 仍如实返回 waiting_not_due，最近 due 仍是 A 股三条 lane -> 2026-03-20 07:00 UTC；而 Rank 109 已在最小 clean replication 后正式压回 park / evidence pool，因此按 desk 最新 Next 3，本轮合法主动作必须切到 Rank 110 的 source intake + 两条轻量诚实守门。重新比较 active Scout 的边际价值后，Rank 110 当前高于 fresh paper/repo reserve，因为它直接服务 EMA / PSAR raw alpha focus，且下一手就是最便宜的 queue-facing intake。",
        "trade_on": "只把 pre-flip SAR dot reclaim 当 continuation admission gate，不单独创造方向：先有 PSAR flip，再在固定 nBars 窗口内只用 signal 当根及之前数据检查价格是否重新穿回 flip 前最后一个 SAR dot。首轮默认只把它写成 long-side optional filter：bullish gate=先出现 bullish PSAR flip，随后在 nBars 内出现 open < pre_flip_dot 且 close > pre_flip_dot，再叠 EMA side 作为 continuation 放行；short 侧默认只保留观察或 veto 候选，不偷渡成 shared mandatory gate。",
        "trade_off": "若这层 gate 的改善主要来自显著砍掉 trade count、而不是把 post-cost expectancy 与 fail-rate 一起改善，就不得把它包装成 shared admission layer；若 short 侧结果更差，则不得镜像成对称 short gate。它也不能替代原始 EMA / PSAR trigger，更不能把 repo 里的 squeeze/volatility 厚模板偷渡进当前最小问题。",
        "honesty_gate": "规则能清楚写成 trade on / trade off，而且 lookahead / repaint / leakage 风险可控：pre_flip_dot 只能取 flip 前最后一个已确认 SAR dot；reclaim 检查只能用 signal 当根及之前数据；下一轮 clean replication 强制 next-bar open + no-overlap。禁止 future bars 延长 reclaim 窗口、禁止同 bar 成交、禁止事后重配 nBars 或只报 long 侧较好结果后偷渡成多空共享 gate。",
        "minimal_test": "固定复用 BTC/ETH/SOL 120d~180d 15m 本地 cache；优先挂到 ema_psar_long / fib_retest_long / breakout_short 三条 archetype，只比较 baseline / preflip_reclaim_long_only / symmetric_preflip_reclaim 三臂；先回答 post-cost expectancy@6bps、trade_retention、4-bar fail-rate、long_vs_short decomposition，直接给出 keep_P1 / promote_to_P2 / park。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "Rank 110 当前高于 fresh paper/repo reserve 与旧 P1 evidence_pool，因为这轮 digest 已把它收紧成一个直接服务 EMA / PSAR raw alpha focus 的便宜 queue-facing 问题；而 Rank 109 已预算用尽并压回 park，不该继续续命；P3 continuity 与 tiny-live plumbing 当前也没有新的 status-changing event 足以插队。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 110 1 次最小 clean replication：固定 BTC/ETH/SOL 15m cache，统一 next-bar open + no-overlap，只比较 baseline / preflip_reclaim_long_only / symmetric_preflip_reclaim。若结果证明它只是 long-side optional filter，就直接写死为 asymmetric context/filter note；若主要靠缩样本或 short 侧继续恶化，则快速压回 park，并把主资源切回 fresh paper/repo intake reserve。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank110_psar_preflip_dot_reclaim_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 110 · PSAR pre-flip SAR dot reclaim gate source intake</title>
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
  <h1>Rank 110 · PSAR pre-flip SAR dot reclaim gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank110_psar_preflip_dot_reclaim_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 本轮 due-check 仍如实返回 <code>waiting_not_due</code>；当前没有 <code>due-now / overdue</code> lane，最近 due 仍是 <code>A股三条 lane -&gt; 2026-03-20 07:00 UTC</code>。</li>
      <li><code>Rank 109</code> 已在上一轮最小 clean replication 后正式压回 <code>park / evidence pool</code>，所以本轮不能继续磨同一条线。</li>
      <li>重新比较 active Scout 的边际价值后，<b>Rank 110</b> 当前高于 fresh paper/repo reserve：它下一手就是最便宜的 queue-facing intake，而且直接服务 <code>EMA / PSAR raw alpha focus</code>。</li>
      <li>这轮默认不再把它吹成多空共享 shared gate；真正有价值的是先把“pre-flip reclaim 更像 long-side optional filter”这个最小问题钉死。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>先有 <code>PSAR flip</code>，再在固定 <code>nBars</code> 窗口内检查价格是否重新穿回 <code>pre_flip_dot</code>。首轮默认只把它写成 <code>long-side optional filter</code>：<code>open &lt; pre_flip_dot &amp;&amp; close &gt; pre_flip_dot</code> 才允许 continuation 放行。</li>
      <li><b>trade off：</b>若改善主要来自大砍样本、或 short 侧没有一致帮助甚至更差，就不得把它包装成多空对称 shared gate；它不能单独开仓，也不替代原始 EMA / PSAR trigger。</li>
      <li><b>lookahead / repaint / leakage：</b><code>pre_flip_dot</code> 只能取 flip 前最后一个已确认 SAR dot；实现统一冻结为 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。禁止 future bars 延长 reclaim 窗口，禁止同 bar 成交，禁止事后重配 <code>nBars</code> 或只报 long 侧好看的结果后偷渡成 shared gate。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>它给 desk 一个很便宜的 <b>continuation admission 读数</b>：不用重写 trigger，只回答 flip 之后有没有出现更诚实的 delayed reclaim。</td></tr>
      <tr><th>关键保留</th><td>当前 digest 已明确：这层结构在 long 侧最多只是可选滤层，short 侧更像不推荐分支，所以现在还不能把它包装成 shared alpha。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；下一轮重点不是把它吹成新 alpha，而是直接回答它究竟只配做 <code>long-side filter note</code>，还是能升到更硬的 <code>P2</code> 候选。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 15m</code> 本地 cache，不扩大成新的重下载任务。</li>
      <li>统一冻结成 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</li>
      <li>先比较最小三臂：<code>baseline</code>、<code>preflip_reclaim_long_only</code>、<code>symmetric_preflip_reclaim</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_expectancy</code>、<code>trade_retention</code>、<code>4-bar fail-rate</code>、<code>long_vs_short decomposition</code>。</li>
      <li>默认不允许：扩成 squeeze/volatility 大模板、等下一根 bar、或同时再开第二条 fresh intake。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-20_0354_psar-preflip-dot-reclaim-not-shared-gate.md</code></li>
      <li>repo：<code>hasnocool / tradingview-pine-scripts</code></li>
      <li>关键实现：<code>BT-SAR Ema, Squeeze, Volatility</code> 里的 <code>SAR Breakout</code> 状态机，也就是先 flip，再在固定窗口内要求价格 reclaim flip 前最后一个 SAR dot。</li>
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
    print(f"wrote {CSV_PATH}")
    print(f"wrote {HTML_PATH}")


if __name__ == "__main__":
    main()
