from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank50_chanlun_structural_reclaim_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank50_chanlun_structural_reclaim_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "50",
        "candidate": "chanlun-pro structural reclaim gate / higher-low + reclaim confirmation",
        "source": "yijixiuxin/chanlun-pro",
        "source_type": "repo / docs / incremental structure-confirmation engine",
        "why_now": "当前 EMA 已回到 running paper / waiting_not_due，而 Rank 48/49 也都在允许预算内完成 clean replication 后压回 park；因此 Scout Seat 必须回到 fresh paper/repo based 5m/15m crypto intake。对比本轮 active fresh sources，Rank 50 直接服务 breakout/Fib/EMA-PSAR 三条主线的共用结构确认层，边际价值高于新出现但 0-star 且 ES/MES session 依赖更重的 VWAP repo，也高于 Rank 35b 这种 queue-only fallback。",
        "trade_on": "先有因果可确认的突破/回抽锚点；随后 pullback 不跌破最近确认结构低点（long）或不突破最近确认结构高点（short），并在 1~4 根内重新站回/跌回锚点，形成 higher-low/lower-high + reclaim/fail-reclaim。若 1h EMA fast>slow 或 PSAR 未反向翻转，则允许把它当 continuation confirmation。",
        "trade_off": "没有已确认结构锚点、pullback 直接破坏结构地板/天花板、或回抽后一直不能 reclaim 触发位；若只有事后画图才能看出二买/二卖，而逐 Bar 因果版无法提前识别，则本线失效。",
        "honesty_gate": "规则已经能冻结成 trade on / trade off；源码与 README 明说结构对象是逐 Bar 增量确认，因此所有 pivot/segment/zone 代理都必须用因果确认版本，不能把事后画好的笔/中枢/买卖点回填成入场依据；当前未见必须直接判死刑的 lookahead/repaint/leakage，但 clean replication 必须统一 next-bar open + no-overlap。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | next-bar open | no-overlap；比较 raw breakout/retest baseline vs +structural reclaim vs +structural reclaim + HTF direction；先看 post_cost_return / 2~4 bar fail rate / trade_count retention / false_reclaim_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "Rank 50 > Rank 51(vwap-trend-defense queue) > Rank 35b。原因：Rank 50 的 repo 规则更能直接压成跨 breakout/Fib/EMA-PSAR 的共用结构确认层，而且上游 repo 更成熟；Rank 51 虽也像确认层，但 24/7 crypto 上的 session 定义与 0-star 社会证明让它更适合排在下一条 fresh intake，而不是本轮主资源。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许做 1 次最小 clean replication：冻结 structural higher-low/lower-high reclaim 与 HTF direction overlay，先回答它是否能在不过度砍样本的前提下降低 2~4 bar fail rate；若不能，快速压回 park。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank50_chanlun_structural_reclaim_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 50 · chanlun-pro structural reclaim source intake</title>
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
  <h1>Rank 50 · chanlun-pro structural reclaim gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank50_chanlun_structural_reclaim_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，没有新的 due-now / overdue lane。</li>
      <li><code>Rank 48 / 49</code> 已在允许预算内给出 hard verdict 并压回 <code>park / evidence pool</code>，Scout Seat 必须回到 fresh source intake。</li>
      <li>本轮比较的是 <code>Rank 50 / chanlun structural reclaim</code>、刚出现的 <code>Rank 51 / vwap-trend-defense</code>、以及 <code>Rank 35b</code> fallback。结论是 <b>Rank 50 > Rank 51 > Rank 35b</b>：它更直接服务 breakout / Fib / EMA-PSAR 三条主线的共用结构确认层，而且 repo 成熟度更高。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>先有因果可确认的突破/回抽锚点；随后 pullback 不破最近确认结构低点/高点，并在 <code>1~4</code> 根内完成 <code>higher-low / lower-high + reclaim / fail-reclaim</code>。若 <code>1h EMA fast &gt; slow</code> 或 <code>PSAR</code> 未反向翻转，可作为 continuation confirm。</li>
      <li><b>trade off：</b>没有已确认结构锚点、pullback 直接破坏结构地板/天花板、或回抽后一直不能 reclaim 触发位；若只能靠事后画图才能看出二买/二卖，而逐 Bar 因果版无法提前识别，则本线失效。</li>
      <li><b>lookahead / repaint / leakage 读法：</b>必须坚持 repo 自己写明的逐 Bar / 增量确认语义；所有 pivot / segment / zone 代理都只能用因果确认版本，clean replication 必须统一 <code>next-bar open + no-overlap</code>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 guard-passed</h2>
    <table>
      <tr><th>真实优点</th><td>它不是第四条新主线，而是给现有 breakout/Fib/EMA-PSAR 补一个共用的结构确认层。</td></tr>
      <tr><th>关键保留</th><td><code>chanlun-pro</code> 的原始对象体系很重，若直接照搬就容易把事后确认倒灌成入场依据；因此本轮只承认其结构确认骨架，不承认整套图形系统。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；若 replication 不能在不过度砍样本的前提下降低 fail rate，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache。</li>
      <li>统一冻结成 <code>next-bar open + no-overlap</code>。</li>
      <li>先比较三个最小臂：<code>raw_breakout_or_retest</code>、<code>+structural_reclaim</code>、<code>+structural_reclaim+HTF_direction</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>2~4 bar fail rate</code>、<code>trade_count retention</code>、<code>false_reclaim_ratio</code>。</li>
      <li>默认不允许：一上来扩成完整缠论研究包、追最新 bar、或同时再开第二条 fresh intake。</li>
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
