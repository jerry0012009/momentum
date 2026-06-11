from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank31_chanlun_second_buy_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank31_chanlun_second_buy_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "31",
        "candidate": "chanlun-pro second-buy / breakout-retest continuation gate",
        "source": "chanlun-pro repo + MAINLINE1 strategy map",
        "source_type": "repo / docs / incremental bar structure engine",
        "why_now": "当前 EMA 继续 waiting_not_due，且 Rank 17 / Rank 2 / Rank 29 没有新的真实 append/review need，Rank 26 / 27 / 28 / 30 已 park。fresh intake 默认应回到 paper / repo based 15m crypto 候选里；相比 Polymarket lag-arb 与 BTC-equity proxy，这条线不需要外部执行数据，又比继续扩 trendline 旁支更贴近已证明有边际价值的 pullback / recovery 家族。",
        "trade_on": "higher_tf_bias_up=1 且先前已出现结构突破；随后 pullback 不跌破最新因果确认的结构低点 / 中枢下沿，并由当前 close 重新站上 pre-pullback reclaim level（可先用 latest swing high 或 breakout neckline 近似）。",
        "trade_off": "没有已确认结构突破、pullback 直接跌破结构地板、或回抽后一直无法 reclaim 触发位；short 侧默认暂不镜像升格，避免把 repo 里的全套缠论对象偷扩成新框架。",
        "honesty_gate": "规则能写成 trade on / trade off；必须坚持 chanlun-pro README 明说的逐 Bar / 增量确认口径，所有 pivot/pen/zone 代理都只能用因果确认版本，不得把事后画出的笔段中枢直接回填成入场依据。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m；对照 raw pullback-recovery baseline vs structural higher-low reclaim vs center-breakout-retest-reclaim；先看 post_cost_return / false_reclaim_ratio / trade_count / no_trade_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_fresh_intakes": "高于 Rank 5 Polymarket lag-arb（缺 prediction-market 执行数据）与 Rank 6 BTC-equity proxy spread（缺同步 equity proxy 数据）；也高于继续重开已 park 的 Rank 30，因为它更贴近 Rank 17 当前已存活的 pullback / recovery 家族，但来源变成明确 repo 语义。",
        "current_hard_verdict": "admit_to_clean_replication_queue",
        "next_step": "只允许下一轮做 1 个最小 clean replication：冻结 structural higher-low reclaim 与 center-breakout-retest-reclaim 两档规则，复用现有 15m crypto cache 跑 first verdict；若 trade_count 过薄或 post-cost 继续显著转负，就快速 park。",
        "reader_facing_page": "reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 31 · chanlun-pro second-buy source intake</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 980px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
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
  <h1>Rank 31 · chanlun-pro second-buy / breakout-retest continuation gate</h1>
  <p class=\"muted\">生成时间：{NOW} ｜ 类型：fresh source intake ｜ 角色：Scout Seat 的 repo-based 15m crypto 新候补</p>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>waiting_not_due</code>，没有 due-now / overdue lane。</li>
      <li><code>Rank 17 / Rank 2 / Rank 29</code> 当前没有新的真实 <code>append/review</code> need；<code>Rank 26 / Rank 27 / Rank 28 / Rank 30</code> 已 park，不值得重开。</li>
      <li>如果要回到 fresh intake，当前最有边际价值的不是 prediction-market / equity proxy 这种要新数据源的方向，而是一个 <b>repo-based、能直接复用 15m crypto cache、且贴近现有 pullback / recovery 主线</b> 的结构候选。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源与边界</h2>
    <table>
      <tr><th>source family</th><td><code>chanlun-pro</code> 的逐 Bar 结构更新、分型 / 笔 / 中枢 / 买卖点语义</td></tr>
      <tr><th>上游来源</th><td><a href=\"https://github.com/yijixiuxin/chanlun-pro\">yijixiuxin/chanlun-pro</a></td></tr>
      <tr><th>为什么不是凭空发明</th><td>这条线直接继承 repo 明说的增量确认逻辑：先等结构突破成立，再看第一次不破结构地板的回抽与 reclaim，而不是事后凭主观图形补定义。</td></tr>
      <tr><th>本轮边界</th><td>本轮只做 source intake，不偷跑 clean replication，也不把整套缠论对象一次性扩写成新大框架。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b><code>higher_tf_bias_up=1</code> 且先前已出现结构突破；随后 pullback 不跌破最新因果确认的结构低点 / 中枢下沿，并由当前 <code>close</code> 重新站上 <code>pre-pullback reclaim level</code>。</li>
      <li><b>trade off：</b>没有已确认结构突破、pullback 直接跌破结构地板、或回抽后一直无法 reclaim 触发位。</li>
      <li><b>lookahead / repaint 风险读法：</b>必须坚持 repo 自己写明的逐 Bar / 增量确认；所有 pivot / pen / zone 代理都只能用因果确认版本，不能把事后画出的结构回填成入场依据。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d~180d 15m</code> cache。</li>
      <li>只做 <b>1 次最小 clean replication</b>：比较 <code>raw pullback-recovery baseline</code>、<code>structural higher-low reclaim</code>、<code>center-breakout-retest-reclaim</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_reclaim_ratio</code>、<code>trade_count</code>、<code>no_trade_ratio</code>。</li>
      <li>默认不允许：一上来扩成完整缠论研究包、追最新 bar、或同时再开第二条 fresh intake。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>当前 hard verdict</h2>
    <p><b>admit_to_clean_replication_queue</b></p>
    <p class=\"muted\">更直白地说：它现在只是下一条值得花 1 轮预算验证的 repo-based 15m crypto 候选；如果最小 clean replication 不能快速给出比现有 pullback / recovery baseline 更诚实的结构增益，就应尽快 <code>park</code>。</p>
    <p class=\"muted\">artifact：<a href=\"../../../artifacts/literature/scout_rank31_chanlun_second_buy_source_intake_card.csv\">scout_rank31_chanlun_second_buy_source_intake_card.csv</a></p>
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
