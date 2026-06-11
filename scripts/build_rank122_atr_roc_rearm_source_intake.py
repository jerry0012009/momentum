from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank122_atr_compression_roc_ignition_short_rearm_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank122_atr_compression_roc_ignition_short_rearm_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "122",
        "candidate": "ATR compression + ROC ignition short re-arm gate",
        "source": "ricketter1984/my-futures-trading-bot + 2026-03-20 12:53 quant digest",
        "source_type": "repo / breakout-short short-side re-arm overlay / crypto 15m",
        "why_now": "按 2026-03-20 12:56 UTC 的最新 desk review，这轮必须先执行 EMA due-check；结果继续如实返回 waiting_not_due，因此本轮 Run 2 合法主动作只能落在 Rank 122 的 source intake + 两条轻量诚实守门，而不是回头续磨 Rank 121/120 或提前回 tiny-live plumbing。与此同时，12:53 UTC 的新 quant digest 已经补进一条 paper/repo based 的 15m crypto fresh source，说明 fresh intake 并未 exhausted。",
        "trade_on": "它只配先当 breakout-short 的 short-side re-arm / follow-up filter：先有 baseline short breakout / breakdown setup，再检查 signal 前是否出现可见的 ATR compression，随后是否由 short-side ROC ignition 触发『重新发动』。strict 版先冻结为 ATR14/avgATR20<0.7 且 ROC5<-0.5%；mild 版只允许作为对照组，放宽为近4根最小 ATR ratio<0.8 且 ROC5<-0.4%。它当前不该 shared 到 Fib retest_hold，也不该接到 EMA long continuation。",
        "trade_off": "它不是独立 alpha，也不是三条主线共享的 anti-chop gate。若没有既定 short-side base trigger，它不能单独开仓；若 clean replication 发现改善主要来自极端稀疏样本、或只是把 trade count 大砍但成本后并未形成更诚实 uplift，就应直接 park。尤其 long 侧现有代理证据已经偏负，因此不得镜像成 Fib/EMA long 的默认放行键。",
        "honesty_gate": "两条轻量守门当前都能如实通过，但边界要写死：1) 所有 ATR ratio、ROC5、compression / ignition 状态只能来自 signal 当根及之前已完成的 15m bar；2) 下一轮 clean replication 必须统一为 next-bar open + no-overlap，禁止同 bar 既判 breakout 又按同 bar 成交；3) strict / mild 阈值只能在训练段冻结，再去测试段验证，禁止事后按全样本最好看的版本回填；4) 当前角色只允许 short-side re-arm，不允许偷渡成 shared anti-chop label。",
        "minimal_test": "最小 clean replication 只挂到 1 条 breakout-short archetype，固定复用 BTC/ETH/SOL 120d 15m 本地 cache，比较 baseline short vs strict short re-arm vs mild short re-arm 三臂，并统一 signal当根及之前数据 + next-bar open + no-overlap。主看 post-cost expectancy、trade_retention、false-follow / back-inside rate、以及 short-side symbol dispersion。若 strict 样本过稀但 mild 保留 honest uplift，再决定 keep_P1 或 park；若两臂都只是稀疏幻觉，则直接 park。",
        "desk_fit": "high_for_short_followup_only",
        "marginal_value_vs_other_active_scouts": "当前 active Scout 顺序应写成：Rank 122 > Rank 112 > Rank 111 > Rank 121/120/119/118/117(P0)。原因不是 Rank 122 已经更硬，而是它是当前唯一新的 repo-based 15m crypto fresh source；Rank 112/111 都已是 evidence_pool / budget used，旧 P0 更不该继续占主资源。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 122 1 次最小 clean replication：先测 strict vs mild 的 short-side re-arm 版本，统一 next-bar open + no-overlap；若 short 侧能在至少 2 个 symbol 上保留 honest uplift 且无 decisive fail，则再补 1 个真正会改变级别的最小检查（默认优先成本/交易数稳定性）并给出 P2 / park；若 clean replication hard-fail，则回 fresh intake，而不是回头续磨旧 rank。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank122_atr_compression_roc_ignition_short_rearm_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 122 · ATR compression + ROC ignition short re-arm source intake</title>
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
  <h1>Rank 122 · ATR compression + ROC ignition short re-arm gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：repo source intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank122_atr_compression_roc_ignition_short_rearm_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> due-check 继续如实返回 <code>waiting_not_due</code>，Paper Seat 没有新的 due-now / overdue 动作。</li>
      <li><code>Rank 121</code> 已完成 clean replication 并回到 <code>P0 / park</code>；旧 <code>Rank 112 / 111</code> 也都只是 <code>evidence_pool / budget used</code>，不该继续抢主资源。</li>
      <li><code>2026-03-20 12:53 UTC</code> 的新 quant digest 已补进一条 fresh repo source，因此这轮更诚实的动作不是 tiny-live fallback，而是先把它正式编为 <b>Rank 122</b>，做 source intake + 两条轻量诚实守门。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>只允许把它写成 <b>breakout-short 的 short-side re-arm / follow-up filter</b>。先有现成 short-side base trigger，再检查 signal 前是否先经历压缩、随后出现 short-side ROC 点火；当前先测 <code>strict</code> 与 <code>mild</code> 两个版本。</li>
      <li><b>trade off：</b>它不是独立 alpha，也不是三条主线共享的 anti-chop gate；没有 base short trigger 时不能单独开仓，更不能镜像搬去 <code>Fib retest_hold</code> 或 <code>EMA long continuation</code>。</li>
      <li><b>lookahead / leakage：</b>ATR ratio、ROC5、compression / ignition 状态只能来自 <code>signal 当根及之前</code> 的已完成 bar；下一轮 clean replication 必须统一 <code>next-bar open + no-overlap</code>，阈值只能在训练段冻结，再去测试段检验。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>当前最关键的代理证据</h2>
    <table>
      <tr><th>strict short</th><td>样本只有 <b>16</b> 笔，但 4-bar signed return 约 <b>+38.7 bps</b>，re-entry 约 <b>56.7%</b>，明显好于 short raw 的 <b>+5.7 bps / 72.2%</b>。</td></tr>
      <tr><th>strict long</th><td>同一套 strict 规则放到 long 侧，均值反而掉到约 <b>-58.7 bps</b>，说明它当前不该 shared 到 long continuation。</td></tr>
      <tr><th>mild short</th><td>样本放宽到 <b>217</b> 笔后，short 侧仍保留约 <b>+9.9 bps</b>、re-entry <b>68.9%</b>，适合拿来做下一轮最小 clean replication 的对照臂。</td></tr>
      <tr><th>desk 含义</th><td>这条线更像 <b>short-side re-arm 候选</b>，不是 desk-wide shared gate；因此当前最诚实的状态是 <code>guard-passed</code>，还不是已验证 alpha。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d 15m</code> 本地 cache，不扩成新的大下载。</li>
      <li>只挂到 <b>1 条 breakout-short short-side archetype</b>，不并开 Fib / EMA long。</li>
      <li>统一执行 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>，只比较三臂：<code>baseline short</code>、<code>strict short re-arm</code>、<code>mild short re-arm</code>。</li>
      <li>主看 <code>post-cost expectancy</code>、<code>trade_retention</code>、<code>false-follow / back-inside rate</code>、<code>symbol dispersion</code>；若 strict 只是极端稀疏、mild 也没有 honest uplift，就直接 park。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-20_1253_atr-compression-roc-ignition-short-rearm-gate.md</code></li>
      <li>repo：<code>ricketter1984/my-futures-trading-bot</code></li>
      <li>关键文件：<code>src/strategy.py::is_consolidating()</code>、<code>src/strategy.py::get_momentum_ignition_signal()</code></li>
      <li>当前最诚实的角色：不是 shared anti-chop，而是 <b>short-side follow-up / re-arm filter</b>。</li>
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
