from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank109_htf_premium_discount_long_bias_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank109_htf_premium_discount_long_bias_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "109",
        "candidate": "HTF premium-discount long-bias context gate",
        "source": "carlosrod723/MQL5-Trading-Bot + 2026-03-20 03:23 digest",
        "source_type": "repo / long-bias context overlay / crypto 15m adaptable",
        "why_now": "当前 EMA due-check 仍如实返回 waiting_not_due，最近 due 仍是 A 股三条 lane -> 2026-03-20 07:00 UTC；而 Rank 108 已在最小 clean replication 后正式压回 park / evidence pool，因此按 desk 最新 Next 3，本轮合法主动作必须切到 Rank 109 的 source intake + 两条轻量诚实守门。重新比较 active Scout 的边际价值后，Rank 109 当前高于 Rank 110 / PSAR pre-flip SAR dot reclaim，因为它更直接服务 Fib retest_hold / EMA continuation 的 long-side context，且下一手就是最便宜的 queue-facing intake。",
        "trade_on": "只把上一根完整 4h K 线的 midline（prev4h_mid=(high+low)/2）当 long-side context gate，不单独开仓：默认先服务 Fib retest_hold / EMA continuation long，首轮只回答 entry 是否位于 prev4h_mid 下方（discount），以及这层 context 是否值得作为 long-only allow / size-up，而不是 shared mandatory gate。可以保留对 short 侧的 adverse-long-context 观察，但不默认写成 short 放行键。",
        "trade_off": "若这层 premium/discount 只能在 long 侧给出轻微 pocket 改善、而 short 侧没有一致帮助甚至更差，就不得镜像成多空对称 shared gate；它也不能替代原始 trigger，不负责创造方向，不把 repo 里的 Fib 语义偷渡成精细 swing-based retracement alpha。若 clean replication 主要靠大砍 trade count 才变好，也只能停在 context note / park。",
        "honesty_gate": "规则能清楚写成 trade on / trade off，而且 lookahead / repaint / leakage 风险可控：prev4h_high / prev4h_low / prev4h_mid 都只取上一根完整 4h bar；entry 判断与 gate 计算都冻结在 signal 当根及之前数据；下一轮 clean replication 强制 next-bar open + no-overlap。禁止用 future 4h bar 重写当前 zone，禁止事后换更漂亮的 swing anchor，禁止把 short 侧代理快检的弱结果藏掉后再包装成对称 gate。",
        "minimal_test": "固定复用 BTC/ETH/SOL 120d~180d 15m 本地 cache；优先挂到 fib_retest_long / ema_psar_long / breakout_short 三条 archetype，只比较 baseline / long_only_discount_gate / symmetric_discount_premium_gate 三臂；先回答 post-cost expectancy@6bps、long_vs_short_decomposition、trade_retention、4~8 bar failure ratio，直接给出 keep_P1 / promote_to_P2 / park。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "Rank 109 当前高于 Rank 110 / PSAR pre-flip SAR dot reclaim，因为这轮 digest 已经把它收紧成一个便宜、方向不对称且直接服务 Fib/EMA 的 long-side context 问题；而 Rank 110 目前更像 raw-alpha reserve，不应在 Rank 109 尚未 intake 前抢主资源位。它也高于 fresh pool / P1 evidence_pool / P3 continuity，因为当前 desk 明确要求先处理 queue-facing 的当前默认 Scout Seat。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 109 1 次最小 clean replication：固定 BTC/ETH/SOL 15m cache，统一 next-bar open + no-overlap，只比较 baseline / long_only_discount_gate / symmetric_discount_premium_gate。若结果验证它只适合 long-side context，就直接写死为 asymmetric context note；若 long-only 也不诚实或主要靠缩样本，则快速压回 park，并把主资源切到 Rank 110 source intake。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank109_htf_premium_discount_long_bias_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 109 · HTF premium-discount long-bias context gate source intake</title>
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
  <h1>Rank 109 · HTF premium-discount long-bias context gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank109_htf_premium_discount_long_bias_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 本轮 due-check 仍如实返回 <code>waiting_not_due</code>；当前没有 <code>due-now / overdue</code> lane，最近 due 仍是 <code>A股三条 lane -&gt; 2026-03-20 07:00 UTC</code>。</li>
      <li><code>Rank 108</code> 已在上一轮最小 clean replication 后正式压回 <code>park / evidence pool</code>，所以本轮不能继续磨同一条线。</li>
      <li>重新比较 active Scout 的边际价值后，<b>Rank 109</b> 当前高于 <code>Rank 110 / PSAR pre-flip SAR dot reclaim</code>：它下一手就是最便宜的 queue-facing intake，而且直接服务 <code>Fib retest_hold</code> / <code>EMA continuation</code> 的 long-side context。</li>
      <li>这轮默认不再把它写成 breakout-short shared gate；真正有价值的是先把“long-side asymmetric context”钉死。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>只把上一根完整 <code>4h</code> K 线的 <code>prev4h_mid=(high+low)/2</code> 当 long-side context gate。首轮只回答：<code>entry &lt; prev4h_mid</code>（discount）是否值得给 <code>Fib retest_hold</code> / <code>EMA continuation</code> 做 long-only 放行或 size-up。</li>
      <li><b>trade off：</b>若 short 侧的 <code>entry &gt; prev4h_mid</code>（premium）没有一致帮助，甚至更差，就不得把它镜像成多空对称 shared gate；它不能单独开仓，也不替代原始 trigger。</li>
      <li><b>lookahead / repaint / leakage：</b><code>prev4h_high / low / mid</code> 只取上一根完整 4h bar；实现统一冻结为 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。禁止 future 4h zone 倒灌，禁止事后换更漂亮的 swing/fib anchor，禁止只报 long 侧好看的结果后偷渡成 shared gate。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>它给 desk 一个很便宜的 <b>HTF 上下文读数</b>：不用重新发明 trigger，只回答当前 long setup 是不是站在更友好的 H4 discount 区。</td></tr>
      <tr><th>关键保留</th><td>本轮 digest 已经明确：<code>discount 做多</code> 有轻度改善，但 <code>premium 做空</code> 在代理快检里更差，所以不能把它包装成多空对称 shared filter。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；下一轮重点不是把它吹成新 alpha，而是直接回答它究竟只配做 <code>long-side context note</code>，还是能升到更硬的 <code>P2</code> 候选。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 15m</code> 本地 cache，不扩大成新的重下载任务。</li>
      <li>统一冻结成 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</li>
      <li>先比较最小三臂：<code>baseline</code>、<code>long_only_discount_gate</code>、<code>symmetric_discount_premium_gate</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_expectancy</code>、<code>long_vs_short_decomposition</code>、<code>trade_retention</code>、<code>4~8 bar failure ratio</code>。</li>
      <li>默认不允许：扩成 Fib 大框架重写、等下一根 bar、或同时再开第二条 fresh intake。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-20_0323_htf-premium-discount-long-bias-context.md</code></li>
      <li>repo：<code>carlosrod723 / MQL5-Trading-Bot</code></li>
      <li>关键实现：上一根完整 <code>H4</code> K 线的 <code>high/low</code> 与 <code>midline</code>，再把 bullish FT 与 <code>discount</code>、bearish FT 与 <code>premium</code> 绑定。</li>
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
