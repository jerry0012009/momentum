from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank76_intraday_clock_polarity_event_blackout_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank76_intraday_clock_polarity_event_blackout_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "76",
        "candidate": "intraday clock polarity + event blackout gate",
        "source": "Wen et al. (2022) + FOMC public calendar",
        "source_type": "paper / intraday regime gate / 15m adaptable",
        "why_now": "当前 EMA 最新 due guardrail 仍是 waiting_not_due，P3 narrow-paper continuity 也没有新的 status-changing event；同时 Rank 75 已在最小 clean replication 后给出 park / evidence pool hard verdict，因此按顶板最新 Next 3，这轮合法主动作必须切到下一条 fresh source。当前 active Scout 顺序已收紧为 Rank 76 > one-regime-per-session overlay > Rank 35b > Rank 16b > tiny-live plumbing。",
        "trade_on": "先用 rolling 180d 的 hourly bucket 关系给每个小时打 continuation / reversal / neutral 极性标签：只有当某小时 pocket 的统计关系达到最小显著门槛时，才允许把它映射成 15m shared gate。首轮冻结成三档：polarity=+1 时放宽 breakout-short follow-up 与 EMA/PSAR continuation；polarity=-1 时放宽 Fib retest_hold；polarity=0 时 half-size 或 no-trade。事件层只加最小 blackout：FOMC 公告前后 ±2h 默认不新开仓。",
        "trade_off": "若 rolling hourly polarity 没过显著门槛、当前小时落在 neutral、或碰到 FOMC blackout 窗口，则 shared gate 只能 veto / half-size，不能单独开仓、不能自己创造方向，也不能把低频事件黑名单伪装成逐根 15m alpha。若改善只靠大幅砍单或只在单一 archetype 局部成立，就应停在 shared regime overlay / park。",
        "honesty_gate": "论文证据明确支持 crypto intraday return relation 同时存在 momentum 与 reversal，而且在 no-jump / 无 FOMC / 低流动性子样本更强；这给了 trade on / trade off 的因果口径。实现层必须统一冻结为 signal 当根及之前数据 + next-bar open + no-overlap：hourly polarity 只能用当前小时及之前的 rolling 历史估计，不能偷看未来小时结果；FOMC blackout 只能使用事先公开的会议时点，不能回填公告后市场反应；不得把论文里的 hourly 发现直接包装成 15m 已证实 alpha。",
        "minimal_test": "BTC/ETH/SOL perpetual | 365d 15m（若现成 cache 足够则先用当前可得历史样本）| next-bar open | no-overlap；把 gate 接到 breakout_short / fib_retest_long / ema_psar_long 三条 archetype，上比较 baseline / polarity_only / polarity_plus_blackout 三臂；先看 post-cost expectancy@6/10/15bps、4~8 bar failure rate、trade_retention、time-pocket stability。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "Rank 76 当前高于 one-regime-per-session overlay，因为它更 queue-facing：直接给 breakout-short / Fib retest_hold / EMA-PSAR 三条主线一个 shared session-polarity / event-blackout allow-deny 层；而 one-regime-per-session 更像 desk allocation overlay，在 Rank 76 还没跑 source intake 前不应先抢默认 fast lane。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 76 1 次最小 clean replication：固定现有 BTC/ETH/SOL 15m 样本，统一 next-bar open + no-overlap，只比较 baseline / polarity_only / polarity_plus_blackout。若结果主要靠极端砍单、跨 archetype 不稳、或只在局部小时 pocket 勉强成立，就快速压回 park / evidence pool；若没有爆出 decisive fail，再决定是否继续给 1 次 truly verdict-changing 的 stability check。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank76_intraday_clock_polarity_event_blackout_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 76 · intraday clock polarity + event blackout gate source intake</title>
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
  <h1>Rank 76 · intraday clock polarity + event blackout gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh paper intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank76_intraday_clock_polarity_event_blackout_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 最新 due guardrail 仍显示全 desk 没有新的 <code>due-now / overdue</code> lane；当前最近 due 点仍是 <code>A股 2026-03-19 07:00 UTC</code>，所以这轮不能回头刷 paper refresh。</li>
      <li><code>P3</code> narrow-paper continuity 继续由专属 cron 托管，没有新的 status-changing event；按规则也不该继续挤占这类托管位。</li>
      <li><code>Rank 75</code> 已在允许预算内完成 minimal clean replication 并压回 <code>park / evidence pool</code>，所以当前合法主动作必须切到下一条 fresh source。</li>
      <li>在剩余允许动作里，<b>Rank 76</b> 高于 <code>one-regime-per-session overlay</code>：它更 queue-facing，直接给 <code>breakout-short / Fib retest_hold / EMA-PSAR</code> 三条主线一个 shared session-polarity / event-blackout allow-deny 层，而不是先上更偏 allocation 的 desk overlay。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>先用 rolling 180d 的 hourly bucket 关系给每个小时打 <code>continuation / reversal / neutral</code> 极性标签；只有达到最小显著门槛的小时 pocket，才允许映射成 15m shared gate。首轮冻结成 <code>polarity=+1 / -1 / 0</code> 三档，再叠一层最小 <code>FOMC ±2h blackout</code>。</li>
      <li><b>trade off：</b>若 polarity 没过门槛、当前小时仍是 neutral、或碰到 FOMC blackout 窗口，则 shared gate 只能 veto / half-size；它不能单独开仓，也不能自己创造方向。</li>
      <li><b>lookahead / repaint / leakage：</b>hourly polarity 只能用当前小时及之前的 rolling 历史估计，不能偷看未来小时的 realized relation；FOMC blackout 只能用事先公开的会议时点，不能把公告后市场反应倒灌回 gate。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>它补的是 desk 当前缺的 shared spine：不是继续发明新 trigger，而是先回答“这个小时 pocket 更像 continuation 还是 reversal”，再决定放行哪种 archetype。</td></tr>
      <tr><th>关键保留</th><td>论文主频是 hourly，不是现成 15m alpha；而且 event blackout 属于低频风险层，很容易因为砍掉少量坏样本而看起来变好。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但若 clean replication 只是靠大幅砍单或只在单一 archetype / 局部时段勉强成立，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用现有 <code>BTC / ETH / SOL 15m</code> 样本，优先用已有 cache，不额外扩大下载。</li>
      <li>统一冻结成 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</li>
      <li>先比较最小三臂：<code>baseline</code>、<code>polarity_only</code>、<code>polarity_plus_blackout</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_expectancy</code>、<code>4~8 bar failure rate</code>、<code>trade_retention</code>、<code>time-pocket stability</code>。</li>
      <li>默认不允许：把它扩成全天宏观事件大研究、补全所有事件日历、或同时再开第二条 fresh intake。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-19_0133_intraday-clock-polarity-regime-gate.md</code></li>
      <li>paper：<code>Wen, Bouri, Xu, Zhao (2022) — Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both</code></li>
      <li>event source：<code>Federal Reserve FOMC Calendar</code></li>
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
