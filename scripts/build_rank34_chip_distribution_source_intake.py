from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank34_chip_distribution_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank34_chip_distribution_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "34",
        "candidate": "chip-distribution trapped-holder reclaim / winner-ratio gate",
        "source": "repo factor chip_distribution.py + CHIP_DISTRIBUTION.md",
        "source_type": "repo / docs / factor-engine",
        "why_now": "当前 EMA 仍是 waiting_not_due；Rank 17 / Rank 2 / Rank 29 没有新的真实 append/review need；Rank 30 / 31 / 32 / 33 都已完成当前允许动作并 park；Rank 5 / Rank 6 仍偏外部数据。相比继续磨旧 P3 或再开外部依赖，这条线是现有 repo 里尚未消费、且仍贴近 support / reclaim / trapped-holder 语义的 paper/repo based 新候补。",
        "trade_on": "higher_tf_bias_up=1，且价格在一次 pullback 后重新站回估算 cost_p50 / avg_cost 带上方，同时 winner_ratio 从拥挤区下缘回升到阈值之上；做空反向可用 trapped_ratio 上升 + 跌回 cost 带下方表达，但当前 intake 默认先不偷做完整空头升格。",
        "trade_off": "higher_tf_bias 缺失或反向；价格始终站不回 cost_p50 / avg_cost 带；winner_ratio 没有恢复、或 trapped_ratio 继续抬升导致所谓 reclaim 只是拥挤反弹；若 shares 假设一改结果就翻脸，也应直接停掉。",
        "honesty_gate": "规则能清楚写成 trade on / trade off；没有明显 lookahead / repaint——chip 只能逐 bar 递推，不能用未来成交回填；但分钟级 crypto 没有天然 shares，所以下一轮 clean replication 必须把 synthetic shares / turnover anchors 当成第一优先诚实门槛，而不是假装筹码分布是真实账本。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d 15m | 固定现有 cache；先定义 3 档 synthetic shares / turnover anchor（保守 / 中性 / 激进），比较 raw baseline vs chip_cost_reclaim vs chip_cost_reclaim_plus_winner_ratio；第一刀先回答 post_cost_return / trade_count / assumption-sensitivity / false_reclaim_ratio。",
        "desk_fit": "medium_high",
        "marginal_value_vs_other_fresh_intakes": "高于 Rank 5 / Rank 6 的外部依赖方向，因为它完全基于本地 repo 与现有 OHLCV cache；低于 Rank 33 当时的纯因果结构线，但在 Rank 33 已 park 之后，它成为当前最像下一条 support/reclaim 家族候补、同时又不需要凭空发明新框架的 repo-based intake。",
        "current_hard_verdict": "fresh intake only / admit_to_clean_replication_queue_with_assumption_gate",
        "next_step": "只允许下一轮做 1 个最小 clean replication：先把 synthetic shares 假设固定成 3 档敏感度梯子；如果主 verdict 对 shares 假设高度脆弱，就直接 park，不进入完整 stability pack。",
        "reader_facing_page": "reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 34 · chip-distribution source intake</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 980px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href=\"report.html\">← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 34 · chip-distribution trapped-holder reclaim / winner-ratio gate</h1>
  <p class=\"muted\">生成时间：{NOW} ｜ 类型：fresh source intake ｜ 角色：Scout Seat 的 repo-based support/reclaim 新候补</p>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>waiting_not_due</code>，没有 due-now / overdue lane。</li>
      <li><code>Rank 17 / Rank 2 / Rank 29</code> 当前没有新的真实 <code>append/review</code> need；<code>Rank 30 / 31 / 32 / 33</code> 都已经用完当前允许动作并 park。</li>
      <li><code>Rank 5 / Rank 6</code> 仍偏外部数据；相较之下，<code>chip_distribution.py</code> 是现有 repo 里还没被 desk 正式消费、但仍贴近 <b>support / reclaim / trapped-holder</b> 语义的现成因子模块。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源与边界</h2>
    <table>
      <tr><th>source family</th><td><code>src/momentum/factors/chip_distribution.py</code> + <code>docs/CHIP_DISTRIBUTION.md</code></td></tr>
      <tr><th>为什么不是凭空发明</th><td>这条线直接复用 repo 已有的筹码分布递推、<code>avg_cost / cost_p50 / winner_ratio / trapped_ratio</code> 输出，不是另起一个新研究框架。</td></tr>
      <tr><th>本轮最大边界</th><td>分钟级 crypto 没有天然 shares，因此 <b>shares / turnover 只是 synthetic anchor，不是真实股本账本</b>。这一点必须在下一轮先过诚实门槛，不能偷装成“精确筹码”。</td></tr>
      <tr><th>本轮范围</th><td>这轮只做 source intake，不偷跑 clean replication，也不假装已经解决 shares 口径。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b><code>higher_tf_bias_up=1</code>，且价格在一次 pullback 后重新站回估算 <code>cost_p50 / avg_cost</code> 带上方，同时 <code>winner_ratio</code> 从拥挤区下缘回升到阈值之上。</li>
      <li><b>trade off：</b>higher-tf bias 缺失或反向；价格始终站不回 <code>cost_p50 / avg_cost</code> 带；<code>winner_ratio</code> 没有恢复，或 <code>trapped_ratio</code> 继续抬升导致所谓 reclaim 只是拥挤反弹。</li>
      <li><b>lookahead / data-leakage 风险读法：</b>筹码分布只能逐 bar 递推；不能用未来成交回填历史 <code>chip_pct</code>。但真正的第一风险不是 repaint，而是 <b>shares 假设是否太脆弱</b>，所以下一轮必须把 synthetic shares 敏感度当成第一诚实门槛。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache。</li>
      <li>只做 <b>1 次最小 clean replication</b>：先定义 3 档 synthetic shares / turnover anchors（保守 / 中性 / 激进）。</li>
      <li>只比较 <code>raw baseline</code>、<code>chip_cost_reclaim</code>、<code>chip_cost_reclaim_plus_winner_ratio</code> 三档最小规则。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>trade_count</code>、<code>assumption_sensitivity</code>、<code>false_reclaim_ratio</code>。</li>
      <li>默认不允许：先上完整 stability pack、追最新 bar、或跳去外部 proxy / prediction-market 数据。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>当前 hard verdict</h2>
    <p><b>fresh intake only / admit_to_clean_replication_queue_with_assumption_gate</b></p>
    <p class=\"muted\">更直白地说：它现在只是下一条值得花 1 轮预算验证的 repo-based support/reclaim 候选；但这轮预算不该拿去美化筹码故事，而是先诚实回答 <code>shares 假设一改，结论会不会直接翻脸</code>。</p>
    <p class=\"muted\">artifact：<a href=\"../../../artifacts/literature/scout_rank34_chip_distribution_source_intake_card.csv\">scout_rank34_chip_distribution_source_intake_card.csv</a></p>
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
