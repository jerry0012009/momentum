from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "literature"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"

CSV_PATH = ARTIFACT_DIR / "scout_repo_fibtrend_confirmation_source_intake_card.csv"
HTML_PATH = SITE_DIR / "fibtrend_confirmation_source_intake.html"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ROWS = [
    {
        "candidate": "FibTrend-Pro / Fib 0.618 reclaim + volume>SMA24 + SMA200/EMA trend gate",
        "source": "11Muhil/FibTrend-Pro-Strategy_Pinescript",
        "source_type": "repo / Pine strategy / crypto-friendly skeleton",
        "why_now": "当前 EMA 仍是 waiting_not_due，P3 continuity 继续由专属 cron 低频托管；而 bot7 刚补进一条 fresh repo source，边际价值高于继续沿 Rank 35b 这种 park-reframe fallback 往下磨。按顶板顺序，本轮应先做 FibTrend-Pro 的两条轻量诚实守门。",
        "trade_on": "shared-core: close 重新站上 rolling-50 bar Fib 0.618，且 volume > SMA(volume,24)，且 close > SMA200；ATR 版本再额外要求 EMA9 > EMA26 作为 continuation confirm；默认只做 long-only，不镜像 short。",
        "trade_off": "价格未回到 Fib 0.618 强侧、volume 没有超过 SMA24、close 仍在 SMA200 下方，或 ATR 版本里 EMA9<=EMA26；另外若 close 跌回 Fib 0.5 下方，则 setup 直接视为失效/退出。",
        "honesty_gate": "源码层未见一眼可判死刑的 lookahead / repaint / leakage：Fib、SMA、EMA、ATR、volume 全是 trailing 计算；但 replication 必须冻结为 next-bar open + no-overlap，因为原 Pine 默认 bar-close 触发 + 当前 bar rolling extrema，若直接照抄容易把同 bar 确认和成交混在一起。",
        "minimal_test": "BTC/ETH/SOL perpetual | 120d~180d | 15m | next-bar open | no-overlap；比较 fib_touch_raw vs +volume_gate vs +trend_gate(shared) vs +ema_confirm(ATR variant)；先看 post_cost_return / false_retest_rate / trade_count / positive_asset_ratio。",
        "desk_fit": "high",
        "marginal_value_vs_other_active_scouts": "高于 Rank 35b，因为它是 fresh repo source 且直接服务 Fibonacci confirmation / retest_hold 主线；当前也略高于 EMA-ADX-VOL skeleton，因为它给桌面补的是尚缺的 Fib confirmation 骨架，而不是继续给 EMA 家族叠同类过滤。",
        "current_hard_verdict": "guard-passed / admit_to_clean_replication_queue",
        "next_step": "下一轮只允许做 1 次最小 clean replication：先用共享 shared-core（Fib 0.618 reclaim + volume>SMA24 + close>SMA200）跑 baseline，再单独比较是否加 EMA9>EMA26 真的能减少 false-retest，而不是一上来扩成完整高周期 Fib 研究包。",
        "reader_facing_page": "reports/site/reading/repo_scout/fibtrend_confirmation_source_intake.html",
        "generated_at_utc": NOW,
    }
]

HTML = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>FibTrend-Pro · source intake honesty gate</title>
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
  <h1>FibTrend-Pro · Fib 0.618 reclaim + volume/trend gate</h1>

  <div class=\"card\">
    <span class=\"pill\">更新时间：{NOW}</span>
    <span class=\"pill\">类型：fresh repo intake</span>
    <span class=\"pill\">当前 verdict：guard-passed / admit_to_clean_replication_queue</span>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_repo_fibtrend_confirmation_source_intake_card.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前仍是 <code>running paper / waiting_not_due</code>，不是 due-now refresh 窗口。</li>
      <li><code>Rank 2 / 17 / 29 / 32b</code> 这些 <code>P3</code> lane 继续由专属 refresh / monitoring 托管，没有新的 append/review 状态变化。</li>
      <li>相比继续沿 <code>Rank 35b</code> 这种 park-reframe fallback 往下磨，<code>FibTrend-Pro</code> 是更高边际价值的 fresh repo source，而且直接服务当前还缺 repo skeleton 的 <code>Fibonacci confirmation / retest_hold</code> 主线。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>两条轻量诚实守门</h2>
    <ul>
      <li><b>trade on：</b>共享核心可以清楚冻结成：<code>close</code> 重新站上 rolling-50 bar 的 <code>Fib 0.618</code>，同时 <code>volume &gt; SMA(volume, 24)</code>，且 <code>close &gt; SMA200</code>；ATR 版本再额外要求 <code>EMA9 &gt; EMA26</code> 作为 continuation confirm。</li>
      <li><b>trade off：</b>价格没有回到 <code>Fib 0.618</code> 强侧、volume 没有放大、价格仍在 <code>SMA200</code> 下方，或 ATR 版本里 <code>EMA9 &lt;= EMA26</code>；若后续 <code>close &lt; Fib 0.5</code>，则 setup 直接失效/退出。</li>
      <li><b>lookahead / repaint / leakage 读法：</b>源码里的 Fib/SMA/EMA/ATR/volume 都是 trailing 计算，没有一眼可判死刑的未来函数；但 replication 必须强制 <code>next-bar open + no-overlap</code>，避免把同 bar 的确认与成交混写成乐观填单。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>为什么只是 admitted，不是已验证 alpha</h2>
    <table>
      <tr><th>真实优点</th><td>把 Fib 从“碰线就进”压成了更像确认层的组合门：<code>Fib reclaim + volume + trend</code>，而不是再发明新大框架。</td></tr>
      <tr><th>关键保留</th><td>README 明说高周期 <code>4H/1D/1W</code> 更可靠，说明它对 <code>15m</code> 更像 skeleton / overlay，而不是现成 alpha。</td></tr>
      <tr><th>当前最诚实结论</th><td>它通过了 source-intake 的两条守门，因此值得拿 <b>1 次最小 clean replication</b> 预算；但如果成本后还是只能靠重过滤换低交易数，就应快速压回 <code>park</code>。</td></tr>
    </table>
  </div>

  <div class=\"card\">
    <h2>下一轮只允许做什么</h2>
    <ul>
      <li>固定复用 <code>BTC / ETH / SOL 120d~180d 15m</code> cache。</li>
      <li>统一冻结成 <code>next-bar open + no-overlap</code>。</li>
      <li>先比较 4 个最小臂：<code>fib_touch_raw</code>、<code>+volume_gate</code>、<code>+trend_gate(shared)</code>、<code>+ema_confirm(ATR variant)</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_retest_rate</code>、<code>trade_count</code>、<code>positive_asset_ratio</code>。</li>
      <li>默认不允许：一上来扩成高周期 Fib 大研究、追最新 bar、或同时再开第二条 fresh intake。</li>
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
