from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank83_fib_trend_strength_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank83_fib_trend_strength_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "83",
        "candidate": "Fib trend-strength admission layer",
        "source": "Khattak et al. (2024) / Profitability trend prediction in crypto financial markets using Fibonacci technical indicator and hybrid CNN model",
        "source_type": "paper / Fib retest strength-bucket admission-scaling layer / 15m adaptable",
        "why_now": "本轮先实际执行了 EMA guarded refresh require-due，结果仍是 waiting_not_due；同时 07:40 UTC 的 desk board 已把 Rank 82 / 80 / 81 全部压回 P1 evidence_pool，并把当前默认 Scout 主资源位写死成 Rank 83 source intake next。因此本轮合法主动作不是继续磨旧 P1，而是把 Fib trend-strength admission layer 正式冻结成 queue-facing fresh source。",
        "trade_on": "保留现有 Fib retest_hold base event（impulse leg -> 回踩 0.5/0.618 -> 0.618 未收破），但 admission 不再只看二元 hold/fail，而是按确认强度分三档：weak=守住但确认 bar 仍收在 0.5 下方；medium=确认 bar 收回 0.5 上方；strong=在 medium 基础上再满足收回 0.382 或突破 retest bar high。desk 迁移先把它当 deny / half-size / full-size 的 shared admission-scaling layer。",
        "trade_off": "若只是碰到 0.618 但确认 bar 仍弱、没有收回 0.5、或后续重新跌破 0.618/0.5 失效线，则不得放大仓位，弱档默认不放行或只允许 half-size；这条线不能被偷渡成新的独立 alpha，也不能用未来 continuation 强弱倒灌回当前分档。",
        "honesty_gate": "论文里的 strength 标签本质上来自未来价格变化分层，因此 desk 迁移时必须把标签改写成当根即可判定的规则化 admission state：只用 signal 当根及之前的 Fib 相对位置、确认 bar 收盘层级与 retest bar high/0.382 reclaim 条件，统一冻结到 signal 当根及之前数据 + next-bar open + no-overlap；不得把未来 2~4 bar 的 continuation 结果回填成 strong/weak，也不得把 1m CNN 结果伪装成 15m 规则特征。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | next-bar open | no-overlap；版本：base_binary / strength_filter(只做 medium+strong) / strength_sizing(weak=0, medium=0.5x, strong=1.0x)。优先看 2~4 bar fail rate、post_cost_expectancy@6/10/15bps、trade_count_retention、positive_asset_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "当前 active Scout 边际价值顺序应读成 Rank 83 > Rank 85 > Rank 84 > Rank 82/80/81 evidence_pool > P3 continuity > tiny-live plumbing。Rank 83 之所以排第一，不是因为论文更漂亮，而是它直接服务当前 Fib retest_hold 主线，而且比继续给已做过 cheap check 的 Rank 82/80/81 续命更符合先 hard gate、再 clean replication 的 desk 纪律。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 83 1 次最小 clean replication：固定 BTC/ETH/SOL 15m 现有 Fib retest lane，比较 base_binary / strength_filter / strength_sizing，并直接做 keep_P1 / promote_to_P2 / park 判断；若这条线在 clean replication 后直接 hard-fail，再切 Rank 85 / fresh pullback -> reclaim re-arm gate source intake。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank83_fib_trend_strength_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 83 · Fib trend-strength admission layer source intake</title>
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
  <h1>Rank 83 · Fib trend-strength admission layer</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh paper intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank83_fib_trend_strength_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>Run 1 / EMA due-check</code> 已实际执行，结果仍是 <code>waiting_not_due</code>；当前没有 due-now / overdue lane，不允许伪造 refresh。</li>
      <li><code>Rank 82 / 80 / 81</code> 都已做过那次允许的便宜检查，当前更诚实的位置都是 <code>P1 evidence_pool</code>，不该继续占默认 Scout 主资源。</li>
      <li>07:40 UTC 的 desk board 已把本轮默认主资源位写死成 <code>Rank 83 / Fib trend-strength admission layer source intake</code>，因此这轮合法动作是 fresh intake，不是继续续磨旧 P1。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>保留现有 <code>Fib retest_hold</code> 基础事件，但把 admission 从二元 hold/fail 改成三档：<code>weak</code>（守住但确认 bar 仍在 0.5 下方）、<code>medium</code>（确认 bar 收回 0.5 上方）、<code>strong</code>（在 medium 基础上再收回 0.382 或突破 retest bar high）。它当前只负责 <code>deny / half-size / full-size</code>。</li>
      <li><b>trade off：</b>若只是碰到 0.618 却没有收回 0.5、或后续又跌回 0.618/0.5 失效线，就不得放大仓位；这条线不能单独开仓，也不能把未来 continuation 好坏倒灌回当前分档。</li>
      <li><b>lookahead / repaint / leakage：</b>论文里的 strength 标签来自未来价格变化分层，所以 desk 迁移必须把它改写成当根即可判定的规则化 state，只用 signal 当根及之前可得的 Fib 相对位置与确认 bar 收盘层级，统一冻结成 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只是 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>它直接补的是当前 Fib 主线缺的“位置 + 强度”确认层，比继续加一个普通 veto 更贴主线。</td></tr>
      <tr><th>关键保留</th><td>原论文基于 1m + CNN + future strength 标签，不能把论文里的 ROI 数字直接拿来当 15m 规则化结论。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但若三档之间没有可分性，或 improvement 主要靠大幅砍样本换来，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache。</li>
      <li>统一冻结成 <code>next-bar open + no-overlap</code>。</li>
      <li>先比较 3 个最小版本：<code>base_binary</code>、<code>strength_filter</code>、<code>strength_sizing</code>。</li>
      <li>先回答四个便宜问题：<code>2~4 bar fail rate</code>、<code>post-cost expectancy</code>、<code>trade_count_retention</code>、<code>positive_asset_ratio</code>。</li>
      <li>默认不允许：把它扩成新的大框架、去追最新 bar、或同时再开第二条 fresh intake。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-19_0525_fib-trend-strength-admission-layer.md</code></li>
      <li>paper：Khattak et al. (2024), <code>10.1186/s40537-024-00908-7</code></li>
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
