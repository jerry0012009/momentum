#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path('/root/clawd/jerry/momentum')
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'rank32b'
OUT_PATH = SITE_DIR / 'exp12_decision.html'
SUMMARY_PATH = ROOT / 'reports' / 'artifacts' / 'rank32b_frozen_ablation_exp1_exp2' / 'summary.json'
BASE = '/momentum'
PAGES = {
    'portal': f'{BASE}/factors/rank32b/report.html',
    'decomposition': f'{BASE}/factors/rank32b/decomposition.html',
    'stability': f'{BASE}/factors/rank32b/global_live_like_stability.html',
    'research': f'{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/report.html',
}


def fmt_bj(ts: datetime) -> str:
    bj = ts.astimezone(timezone(timedelta(hours=8)))
    utc = ts.astimezone(timezone.utc)
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def pct(x: float | None) -> str:
    if x is None:
        return '-'
    return f'{x*100:.2f}%'


def signed_pct(x: float | None) -> str:
    if x is None:
        return '-'
    return f'{x*100:+.2f} pct'


def load_summary() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding='utf-8'))


def get_row(summary: dict, window: str, variant: str) -> dict:
    for row in summary['windows'][window]['overall']:
        if row['variant'] == variant:
            return row
    raise KeyError((window, variant))


def build_html(summary: dict) -> str:
    final = summary['final']
    short_delta = summary['windows']['short_120d']['delta']
    mid_delta = summary['windows']['mid_365d']['delta']
    long_delta = summary['windows']['long_730d']['delta']

    worth_next = '值得进入下一轮，但只能以最小可推进版本进入；不是毕业结论。'

    def delta_line(d: dict) -> str:
        return (
            f"交易数 {d['delta_trade_count']:+d}；"
            f"win rate {signed_pct(d['delta_win_rate'])}；"
            f"pnl {signed_pct(d['delta_pnl'])}；"
            f"expectancy {signed_pct(d['delta_expectancy'])}；"
            f"max drawdown {signed_pct(d['delta_max_drawdown'])}"
        )

    rows = []
    for key, label in [('short_120d', '短窗 120d'), ('mid_365d', '中窗 365d'), ('long_730d', '长窗 730d')]:
        exp1 = get_row(summary, key, 'ema_cross_only')
        exp2 = get_row(summary, key, 'ema_cross_plus_slope_floor')
        rows.append(
            f"<tr><td>{label}</td><td>{int(exp1['trade_count'])}</td><td>{int(exp2['trade_count'])}</td><td>{pct(exp1['expectancy'])}</td><td>{pct(exp2['expectancy'])}</td><td>{pct(exp1['max_drawdown'])}</td><td>{pct(exp2['max_drawdown'])}</td></tr>"
        )
    rows_html = ''.join(rows)

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>32B 冻结决策报告：Exp1 vs Exp2</title>
  <style>
    :root{{--bg:#0b1120;--panel:#111827;--line:#24324a;--text:#e5e7eb;--muted:#94a3b8;--accent:#7dd3fc;--good:#34d399;--warn:#fbbf24;--bad:#f87171;color-scheme:dark}}
    *{{box-sizing:border-box}}
    body{{margin:0;background:linear-gradient(180deg,#0b1120,#0f172a);color:var(--text);font:16px/1.7 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}}
    .wrap{{max-width:1080px;margin:0 auto;padding:28px 20px 60px}}
    .hero,.card{{background:rgba(17,24,39,.94);border:1px solid var(--line);border-radius:18px;padding:20px 22px;margin-bottom:18px;box-shadow:0 10px 28px rgba(0,0,0,.22)}}
    h1,h2,h3{{margin:0 0 10px}}
    p{{margin:0 0 12px;color:var(--muted)}}
    a{{color:var(--accent);text-decoration:none;font-weight:700}}
    .badge{{display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid #28456d;background:#13233f;color:#bfdbfe;font-size:12px;margin-right:8px;margin-bottom:8px}}
    .lead{{font-size:18px;color:#dbeafe}}
    .nav{{display:flex;flex-wrap:wrap;gap:10px 12px;margin-top:10px}}
    .nav a{{padding:8px 10px;border:1px solid #26415f;border-radius:10px;background:#0f1a2f}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
    .box{{padding:14px 16px;border-radius:14px;background:#0d1525;border:1px solid #22324a}}
    .box strong{{color:#dbeafe}}
    ul{{margin:8px 0 0 18px;color:#cbd5e1}}
    li{{margin:6px 0}}
    table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}
    th,td{{border:1px solid #24324a;padding:8px 10px;text-align:left;vertical-align:top}}
    th{{background:#0f1a2f;color:#dbeafe}}
    .final{{border-left:4px solid #38bdf8;padding-left:12px;margin:12px 0}}
    .final strong{{color:#dbeafe}}
    .small{{font-size:13px;color:var(--muted)}}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <div>
        <span class=\"badge\">32b</span>
        <span class=\"badge\">frozen ablation</span>
        <span class=\"badge\">Exp1 vs Exp2 only</span>
        <span class=\"badge\">极简决策报告</span>
      </div>
      <h1>32B 冻结决策报告</h1>
      <p class=\"lead\">只回答一件事：在冻结定义下，<code>aligned slope floor</code> 相对 baseline 到底是不是值得保留的真实增量。</p>
      <p>页面生成时间：{escape(fmt_bj(datetime.now(timezone.utc)))}</p>
      <div class=\"nav\">
        <a href=\"{PAGES['portal']}\">32b 主页面</a>
        <a href=\"{PAGES['decomposition']}\">结构拆解页</a>
        <a href=\"{PAGES['research']}\">主研究报告</a>
        <a href=\"{PAGES['stability']}\">稳定性拆解页</a>
      </div>
    </div>

    <div class=\"grid\">
      <div class=\"card\">
        <h2>baseline 抓什么</h2>
        <p>baseline 只抓一件事：<strong>higher-tf 方向已经成立时，15m close 重新穿回 fast EMA 的 continuation</strong>。它不管信号强弱，只要方向对、回穿成立，就记一笔。</p>
      </div>
      <div class=\"card\">
        <h2>aligned slope floor 想解决什么</h2>
        <p>它想解决的是：baseline 太容易把<strong>很平、很弱、只是机械回穿</strong>的 bar 也算进去。slope floor 的作用不是再加一个花哨故事，而是把“方向对但动量太弱”的 continuation 过滤掉。</p>
      </div>
    </div>

    <div class=\"card\">
      <h2>Exp2 相对 Exp1 到底改善了什么</h2>
      <div class=\"grid\">
        <div class=\"box\">
          <strong>交易数</strong>
          <ul>
            <li>120d：{short_delta['delta_trade_count']:+d}</li>
            <li>365d：{mid_delta['delta_trade_count']:+d}</li>
            <li>730d：{long_delta['delta_trade_count']:+d}</li>
          </ul>
          <p class=\"small\">结论：明显降频，但不是唯一变化。</p>
        </div>
        <div class=\"box\">
          <strong>单笔质量</strong>
          <ul>
            <li>120d expectancy：{signed_pct(short_delta['delta_expectancy'])}</li>
            <li>365d expectancy：{signed_pct(mid_delta['delta_expectancy'])}</li>
            <li>730d expectancy：{signed_pct(long_delta['delta_expectancy'])}</li>
          </ul>
          <p class=\"small\">结论：不是只少做，而是每笔平均质量更高。</p>
        </div>
        <div class=\"box\">
          <strong>回撤</strong>
          <ul>
            <li>120d MDD：{signed_pct(short_delta['delta_max_drawdown'])}</li>
            <li>365d MDD：{signed_pct(mid_delta['delta_max_drawdown'])}</li>
            <li>730d MDD：{signed_pct(long_delta['delta_max_drawdown'])}</li>
          </ul>
          <p class=\"small\">这里的正号表示“回撤没那么深了”。</p>
        </div>
        <div class=\"box\">
          <strong>时间窗</strong>
          <ul>
            <li>短窗 120d：{delta_line(short_delta)}</li>
            <li>中窗 365d：{delta_line(mid_delta)}</li>
            <li>长窗 730d：{delta_line(long_delta)}</li>
          </ul>
        </div>
      </div>
      <table>
        <thead>
          <tr><th>窗口</th><th>Exp1 trade count</th><th>Exp2 trade count</th><th>Exp1 expectancy</th><th>Exp2 expectancy</th><th>Exp1 MDD</th><th>Exp2 MDD</th></tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>

    <div class=\"card\">
      <h2>必须区分：真实改善 vs 只是减少交易</h2>
      <p><strong>这次不是“只是减少交易”。</strong> 如果只是降频，你应该只看到 trade count 下去；但这里同时看到：</p>
      <ul>
        <li>win rate 三个窗口都抬升</li>
        <li>expectancy 三个窗口都改善</li>
        <li>max drawdown 三个窗口都显著缓和</li>
        <li>pnl 也在短 / 中 / 长三个窗口相对 baseline 明显更好</li>
      </ul>
      <p>所以更准确的判断是：<strong>aligned slope floor 对 baseline 是真实改善</strong>，只是它还没有把 730d 长窗整体翻成足够强的独立毕业版本。</p>
    </div>

    <div class=\"card\">
      <h2>最终输出</h2>
      <div class=\"final\"><strong>Verdict：</strong> {escape(final['verdict'])}</div>
      <div class=\"final\"><strong>Keep/Watch/Drop：</strong> {escape(final['keep_watch_drop'])}</div>
      <div class=\"final\"><strong>是否值得进入下一轮：</strong> {escape(worth_next)}</div>
      <div class=\"final\"><strong>下一步唯一动作：</strong> {escape(final['next_single_action'])}</div>
    </div>

    <p class=\"small\">实验冻结条件：同一因果口径、同一 warmup、同一 universe、同一成本、同一 entry/exit 壳、non-overlap、hold 8 bars；未做参数优化，也未叠加别的过滤器。</p>
  </div>
</body>
</html>
"""


def main() -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    summary = load_summary()
    OUT_PATH.write_text(build_html(summary), encoding='utf-8')
    print(json.dumps({'out': str(OUT_PATH), 'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
