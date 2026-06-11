from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_rank57_ttm_squeeze_release_regime_gate_source_intake_card.csv"
HTML_PATH = SITE_DIR / "rank57_ttm_squeeze_release_regime_gate_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "rank": "57",
        "candidate": "TTM squeeze release regime gate / avoid-chop expansion filter",
        "source": "GiustiRo/squeezem-adx-ttm + hackingthemarkets/ttm-squeeze",
        "source_type": "repo / volatility-compression regime overlay / 15m adaptable",
        "why_now": "当前 EMA 仍是 running paper / waiting_not_due，而 Rank 55 已 park、Rank 56 已退到 P1 weak candidate / evidence pool。按顶板顺序，当前 Run 2 必须继续 fresh paper/repo intake；在允许动作里，Rank 57 比 pullback-quality / CQI、Rank 35b、Rank 16b 与 tiny-live plumbing 更有边际价值，因为它只依赖现有 15m OHLCV，就能横向服务 breakout-short / Fib retest_hold / EMA-PSAR 三条主线的 avoid-chop / expansion-confirmation 需求。",
        "trade_on": "base setup 继续负责方向与价位；TTM squeeze 只负责回答当前是不是还困在低波压缩里，以及是否刚完成 release。默认只在 sqz_on=0 且最近 1~4 根内刚从 sqz_on 切到 sqz_off / release 时，才允许它作为 shared regime gate；可选再叠 momentum_sign 只做方向一致确认。",
        "trade_off": "若仍处在 sqz_on（BB 仍完全包在 KC 里）、release 已过久、或 momentum_sign 与 base setup 方向不一致，则 overlay 只能 veto / 延后，不单独开仓，也不该把低波压缩状态偷换成主 alpha。",
        "honesty_gate": "源码层规则足够可冻结：hackingthemarkets 直接把 squeeze_on 定义成 lowerBB > lowerKC 且 upperBB < upperKC，并检测从 squeeze_on 到 not squeeze_on 的 release；GiustiRo 的 Pine 版本也明确写出 sqzOn / sqzOff 与线性回归 momentum。上述计算都只用 rolling BB(20,2)、KC(20,1.5*ATR) 与 linreg(momentum)，没有一眼可见的 lookahead / repaint / leakage。desk 迁移时的诚实约束必须写死为：全部状态只用 signal 当根及之前数据计算，统一 next-bar open + no-overlap，先把它降级成 shared avoid-chop / expansion gate，而不是第四条 entry 框架。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | 复用 breakout_short / fib_retest_long / ema_psar_long 三条 archetype；比较 base、+no_sqz_on_veto、+release_recent_gate(1~4 bars)、+release_recent_gate+momentum_sign 四臂；统一 next-bar open + no-overlap + hold 8 bars，先看 post_cost_return@6bps、whipsaw_2bars/4bars、trade_count_retention、positive_asset_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "当前允许动作里，Rank 57 > pullback-quality / CQI > Rank 35b > Rank 16b > tiny-live plumbing。原因不是它已验证，而是它只依赖现有 OHLCV、接线成本最低，并且更像能横向减少三条 base setup 的假启动；相比之下，CQI 仍偏 4H/Daily long-only 弱线索，Rank 35b/16b 属于派生 fallback。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮若 EMA 仍 waiting_not_due，只允许给 Rank 57 1 次最小 clean replication：固定 BTC/ETH/SOL 15m cache，统一测 no_sqz_on_veto / release_recent_gate / momentum_sign 三层是否能在不明显砍死 trade count 的前提下减少 2~4 bar 假启动；若改善只来自极端减样本、跨资产不稳或只在单一 archetype 上成立，就快速压回 park / evidence pool。",
        "reader_facing_page": "reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 57 · TTM squeeze release regime gate source intake</title>
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
  <h1>Rank 57 · TTM squeeze release regime gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_rank57_ttm_squeeze_release_regime_gate_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，没有新的 due-now / overdue lane。</li>
      <li><code>Rank 55</code> 已 park，<code>Rank 56</code> 已退到 <code>P1 weak candidate / evidence pool</code>；按顶板顺序，当前 Run 2 必须继续 fresh paper / repo intake。</li>
      <li>当前允许动作里的边际价值比较是 <b>Rank 57 &gt; pullback-quality / CQI &gt; Rank 35b &gt; Rank 16b &gt; tiny-live plumbing</b>：它不重写 entry，只给三条现有主线补一个共享的 <code>avoid-chop / expansion-confirmation</code> 层。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>base setup 继续负责方向与价位；TTM squeeze 只负责回答当前是否仍困在压缩里，或是否刚从压缩释放。默认只在 <code>sqz_on=0</code> 且最近 <code>1~4</code> 根内刚出现 <code>release</code> 时，把它作为 shared regime gate；可选再叠 <code>momentum_sign</code> 只做方向一致确认。</li>
      <li><b>trade off：</b>若仍处在 <code>sqz_on</code>、release 已过久、或 momentum_sign 与 base 方向不一致，则 overlay 只能 veto / 延后，不能单独开仓，也不能把低波压缩状态偷换成主 alpha。</li>
      <li><b>lookahead / repaint / leakage 读法：</b><code>hackingthemarkets/ttm-squeeze</code> 直接把 <code>squeeze_on</code> 写成 <code>lowerBB &gt; lowerKC</code> 且 <code>upperBB &lt; upperKC</code>，再检测从 <code>squeeze_on</code> 到非 squeeze 的 release；<code>GiustiRo</code> 的 Pine 版本也明确写出 <code>sqzOn / sqzOff</code> 与线性回归 momentum。它们都只依赖 rolling <code>BB(20,2)</code>、<code>KC(20,1.5*ATR)</code> 与历史价格，没有一眼可见的未来函数；desk 迁移时必须统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么现在只升到 guard-passed</h2>
    <table>
      <tr><th>真实优点</th><td>它是共享 regime gate，不是第四条主线；如果有效，价值会体现在更少 chop 假启动、而不是单独造一条新信号。</td></tr>
      <tr><th>关键保留</th><td>TTM squeeze 很容易被参数与“release 后几根”窗口美化；而且它可能通过砍掉大量样本来显得更干净，所以最先要盯的不是收益最好，而是 <code>trade_count_retention</code> 与 <code>whipsaw</code> 是否真的更诚实。</td></tr>
      <tr><th>当前最诚实结论</th><td>两条轻量守门已通过，因此值得拿 <b>1 次最小 clean replication</b> 预算；但若改善主要来自极端减样本、跨资产不稳，或只在单一 archetype 上成立，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache，不追新 bar。</li>
      <li>只比较四个最小臂：<code>base</code>、<code>+no_sqz_on_veto</code>、<code>+release_recent_gate</code>、<code>+release_recent_gate+momentum_sign</code>。</li>
      <li>统一执行口径：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return@6bps</code>、<code>whipsaw_2bars/4bars</code>、<code>trade_count_retention</code>、<code>positive_asset_ratio</code>。</li>
      <li>默认不允许：一上来扩成完整 ADX/TTM 组合大框架、同时再开第二条 fresh intake、或把 release 状态机偷换成主 alpha。</li>
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
