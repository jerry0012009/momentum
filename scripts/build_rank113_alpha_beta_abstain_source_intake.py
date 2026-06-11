from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank113_alpha_beta_abstain_profit_window_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank113_alpha_beta_abstain_profit_window_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "113",
        "candidate": "alpha-beta abstain / profit-window gate",
        "source": "Parente, Rizzuti, Trerotola (2024) + CryptoTrading repo + 2026-03-20 05:39 digest",
        "source_type": "paper + repo / ex-ante admission-veto overlay / crypto 15m adaptable",
        "why_now": "本轮先按 desk 规则执行 EMA due-check，结果继续如实返回 waiting_not_due；而 Rank 112 已完成那 1 次最小 clean replication 并降到 evidence_pool / budget used，因此当前 Run 2 只能切到 alpha-beta abstain / profit-window 的 ex-ante honesty gate source intake。为了遵守 queue-facing 新方向必须先拿顺序 Rank 的规则，这轮先把它正式冻结为 Rank 113，再决定是否配得上下一轮的最小 clean replication 预算。",
        "trade_on": "只把它当现有 setup 的 ex-ante admission / veto overlay，不当独立 alpha，也不用论文里的 forward label 直接发单。先有既定 base setup（如 breakout-short / fib retest / EMA-PSAR），再只用 signal 当根及之前可见的数据构造『当前位移是否过小/过大』的代理：例如过去 k 根绝对收益、rolling true range、event-size percentile 或 setup-to-level distance。若 proxy 落在训练段事先冻结的 no-trade band 内（类似 alpha：太小、像噪音）则 abstain；若已超出 upper shock band（类似 beta：太大、像追尾）也 abstain；只有中间窗口才允许 base setup 继续。profit-window 也只允许在训练段按 post-cost expectancy 选出并冻结一个 hold horizon，再拿去 OOS 用。",
        "trade_off": "它不能把论文里的 forward return label 直接翻译成实时信号，也不能在没有 base setup 时单独开仓；若要用 alpha/beta 概念，也只能翻成『当下已知的 move-size proxy admission/veto』，不能偷看 future path 再决定这笔该不该做。若 clean replication 证明改善主要来自大砍 trade count、或只在单一 symbol / 单一窗口偶然好看，就应直接 park，不得包装成 shared engine。",
        "honesty_gate": "当前两条轻量守门可以如实通过，但前提必须写死：1) alpha/beta 阈值只能由训练段或滚动过去窗口估计，并在测试段冻结，不得用全样本分位；2) 所有 gating 特征只能来自 signal 当根及之前数据，禁止用 forward k-bar return、future volatility、事后最优 window 倒灌当前 admission；3) profit-window selection 只能在训练段按净收益/回撤/交易保留率冻结，再在独立测试段检验，不能拿 accuracy 最优或全样本最优冒充 ex-ante。也就是说，这条线只有在被改写成『pre-signal move-size abstain overlay』后才诚实，不再是原论文的 label 机制直搬。",
        "minimal_test": "固定复用 BTC/ETH/SOL 15m 本地 cache，并优先挂到一个现成 archetype（首选 breakout-short 或 fib retest）上；最小 clean replication 只比较 baseline vs lower-band-only abstain vs lower+upper dual-band abstain 三臂，并把 hold horizon 限制在 train-split 冻结出的 1 个窗口。主看 post-cost expectancy、trade_retention、false-break / fail-rate、symbol dispersion，直接回答 keep_P1 / promote_to_P2 / park。",
        "desk_fit": "medium-high",
        "marginal_value_vs_other_active_scouts": "当前边际顺序应改成：Rank 113 / alpha-beta abstain / profit-window > Rank 112 / basis dislocation short veto > Rank 111 / abnormal-return event clock > 旧 P1 evidence_pool > P0 park > P3 continuity / tiny-live plumbing。原因不是它证据更硬，而是 Rank 112 与 Rank 111 的默认预算都已使用，本轮最便宜、最可能改变 fresh intake judgment 的动作只剩 Rank 113 的 ex-ante honesty gate。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 113 1 次最小 clean replication：选 1 条 base archetype、冻结 1 组 train-split quantile band 与 1 个 profit-window，然后统一 next-bar open + no-overlap 比较三臂。若结果只是靠缩样本但没有改善成本后期望或 fail-rate，就直接 park；若 dual-band 在至少 2 个 symbol 上保留 honest uplift，才考虑升到 P2 / paper candidate pool。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank113_alpha_beta_abstain_profit_window_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 113 · alpha-beta abstain / profit-window source intake</title>
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
  <h1>Rank 113 · alpha-beta abstain / profit-window gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：paper + repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank113_alpha_beta_abstain_profit_window_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 本轮 due-check 继续如实返回 <code>waiting_not_due</code>，Paper Seat 没有新的 due-now / overdue 动作可做。</li>
      <li><code>Rank 112</code> 已完成那 1 次最小 clean replication，当前更诚实的位置是 <code>evidence_pool / budget used</code>，不该继续续命。</li>
      <li>因此当前 Run 2 合法主动作只剩：把 <b>alpha-beta abstain / profit-window</b> 先翻译成一个诚实的、可 queue 的 ex-ante overlay；如果连这一步都过不了，就没资格拿下一轮 replication 预算。</li>
      <li>同时，为遵守新方向进入 queue-facing 层必须先拿顺序 Rank 的规则，这轮先正式编号为 <b>Rank 113</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>它只回答“这笔现有 setup 该不该做”，不是自己创造一笔交易。先有 base setup，再用 <code>signal 当根及之前</code> 的 move-size proxy（如 rolling abs return / true range / event-size percentile）判断：太小像噪音就不做，太大像冲击尾端也不追，只有中间窗口才放行。</li>
      <li><b>trade off：</b>它不能直接搬论文里的 <code>forward return labels</code> 当实时信号，也不能在没有 base trigger 时单独开仓；若改善只来自大量砍掉样本、或只在单一 symbol 偶然有效，就应直接 <code>park</code>。</li>
      <li><b>lookahead / leakage：</b><code>alpha / beta</code> 阈值与 <code>profit-window</code> 只能在训练段估计并冻结，再去独立测试段验证；禁止用全样本分位、禁止用 future k-bar return 当 gating 特征、禁止拿事后最优 horizon 倒灌当前 admission。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>它把论文里最可迁移的部分收缩成一个很便宜的 desk 问题：<b>先别做噪音单，也别追已经冲太远的单</b>，并且明确要求按收益而非 accuracy 选 horizon。</td></tr>
      <tr><th>关键保留</th><td>原论文靠 forward labels 定义 alpha/beta；如果不先翻译成 ex-ante proxy，这条线天然带 leakage 风险。所以这轮真正完成的不是“证明它有效”，而是先证明它可以被诚实地翻成 queue-facing overlay。</td></tr>
      <tr><th>当前最诚实结论</th><td>它现在只配拿 <b>1 次最小 clean replication</b> 预算：挑 1 条 archetype、冻结 1 组 quantile band 与 1 个 hold window，先看成本后 uplift 是否真实存在。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 15m</code> 本地 cache，不扩成新的大下载。</li>
      <li>只挂 1 条 base archetype（优先 breakout-short 或 fib retest），不同时多开多个 setup。</li>
      <li>训练段先冻结：<code>lower no-trade band</code>、<code>upper shock band</code>、<code>1 个 profit-window</code>。</li>
      <li>测试段统一 <code>next-bar open + no-overlap</code>，只比较三臂：<code>baseline</code>、<code>lower-band-only</code>、<code>dual-band</code>。</li>
      <li>主看 <code>post-cost expectancy</code>、<code>trade_retention</code>、<code>false-break / fail-rate</code>、<code>symbol dispersion</code>；若只是 trade count 掉很多却没变更诚实，就直接 park。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>来源</h2>
    <ul>
      <li>digest：<code>research/quant_digests/2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md</code></li>
      <li>paper：Parente, Rizzuti, Trerotola (2024), <code>A profitable trading algorithm for cryptocurrencies using a Neural Network model</code></li>
      <li>repo / code mirror：<code>CryptoTrading</code></li>
      <li>可迁移核心：不是 MLP 本身，而是 <code>dual-threshold abstain</code> + <code>profit-window over accuracy-window</code> 这两个交易语义。</li>
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
