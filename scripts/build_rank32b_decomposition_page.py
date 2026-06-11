#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path("/root/clawd/jerry/momentum")
OUT_DIR = ROOT / "reports" / "site" / "factors" / "rank32b"
OUT_PATH = OUT_DIR / "decomposition.html"
BASE = "/momentum"

PAGES = {
    "portal": f"{BASE}/factors/rank32b/report.html",
    "live": f"{BASE}/factors/rank32b_canary/report.html",
    "transparency": f"{BASE}/factors/rank32b/transparency.html",
    "research": f"{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/report.html",
    "stability": f"{BASE}/factors/rank32b/global_live_like_stability.html",
    "expansion": f"{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/cross_asset_expansion.html",
    "clean": f"{BASE}/reading/trendline_alpha_scout/rank32b_slope_floor_continuation_clean_replication.html",
    "scope": f"{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/scope_promotion_check.html",
    "admission": f"{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/universe_admission.html",
    "global_live": f"{BASE}/factors/rank32b_shadow_global_winner/report.html",
}


def fmt_bj(ts: datetime) -> str:
    bj = ts.astimezone(timezone(timedelta(hours=8)))
    utc = ts.astimezone(timezone.utc)
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def ema_update(prev: float, price: float, span: int) -> float:
    alpha = 2.0 / (span + 1.0)
    return alpha * price + (1.0 - alpha) * prev


def build_live_ema_demo() -> str:
    hour_closes = [
        ("09:00", 98.60),
        ("10:00", 99.40),
        ("11:00", 100.10),
        ("12:00", 99.80),
    ]
    fast = slow = None
    warm_rows: list[tuple[str, float, float, float]] = []
    for label, close in hour_closes:
        if fast is None:
            fast = close
            slow = close
        else:
            fast = ema_update(fast, close, 20)
            slow = ema_update(slow, close, 50)
        warm_rows.append((label, close, fast, slow))

    anchor_fast = warm_rows[-1][2]
    anchor_slow = warm_rows[-1][3]

    focus_bars = [
        ("12:15", 99.30),
        ("12:30", 99.55),
        ("12:45", 99.95),
    ]
    focus_rows: list[tuple[str, float | None, float | None, float, float, float, float, str]] = []
    prev15_close = None
    prev15_fast = None
    for label, close in focus_bars:
        cur_fast = ema_update(anchor_fast, close, 20)
        cur_slow = ema_update(anchor_slow, close, 50)
        read = "当前 bar 只能用上一已完成小时的 EMA 锚点 + 当前 15m close 递推"
        if prev15_fast is not None and prev15_close is not None:
            if prev15_close <= prev15_fast and close > cur_fast:
                read = "满足 prev15_close ≤ prev15_fast 且 close > ema_fast_1h，可记为 long cross"
            else:
                read = "上一根 15m 的 close / fast 只作为比较对象，不会把未来 15m 带进来"
        focus_rows.append((label, prev15_close, prev15_fast, close, anchor_fast, cur_fast, cur_slow, read))
        prev15_close = close
        prev15_fast = cur_fast

    warm_tbody = "".join(
        f"<tr><td>{label}</td><td>{close:.2f}</td><td>{fast:.4f}</td><td>{slow:.4f}</td></tr>"
        for label, close, fast, slow in warm_rows
    )
    focus_tbody = "".join(
        (
            f"<tr><td>{label}</td>"
            f"<td>{('-' if prev_close is None else f'{prev_close:.2f}')}</td>"
            f"<td>{('-' if prev_fast is None else f'{prev_fast:.4f}')}</td>"
            f"<td>{close:.2f}</td>"
            f"<td>{anchor_fast:.4f}</td>"
            f"<td>{cur_fast:.4f}</td>"
            f"<td>{cur_slow:.4f}</td>"
            f"<td>{read}</td></tr>"
        )
        for label, prev_close, prev_fast, close, anchor_fast, cur_fast, cur_slow, read in focus_rows
    )

    count_rows = [
        ("K1", "[00:00,00:15)", "00:15", "还没形成完整 1h", "只拿到 K1 自己的 close；还不能有稳定 hour 锚点", "-", "-", "只是攒小时，不应该拿未来 01:00 的小时结果回填"),
        ("K2", "[00:15,00:30)", "00:30", "还没形成完整 1h", "只拿到 K2 自己的 close；还不能有稳定 hour 锚点", "-", "-", "仍在攒首个完整小时"),
        ("K3", "[00:30,00:45)", "00:45", "还没形成完整 1h", "只拿到 K3 自己的 close；还不能有稳定 hour 锚点", "-", "-", "仍在攒首个完整小时"),
        ("K4", "[00:45,01:00)", "01:00", "H1 在这一刻完成", "K4.close 会成为 H1.hour_close", "-", "-", "K1~K4 共同形成第一个完整小时 H1"),
        ("K5", "[01:00,01:15)", "01:15", "fast(H1), slow(H1)", "K5.close + prev_hour_fast(H1)", "通常先不强调", "K1~K4", "这是第一根真正使用 H1 锚点递推的 15m bar"),
        ("K6", "[01:15,01:30)", "01:30", "fast(H1), slow(H1)", "K6.close + prev_hour_fast(H1)", "fast(K5)", "K1~K4", "K6 真正在比较：上一根 15m 的 fast vs 当前这根 15m 递推出来的 fast"),
        ("K7", "[01:30,01:45)", "01:45", "fast(H1), slow(H1)", "K7.close + prev_hour_fast(H1)", "fast(K6)", "K1~K4", "和 K6 一样，hour 锚点不变，但 prev15_fast 会滚动"),
        ("K8", "[01:45,02:00)", "02:00", "仍然用 fast(H1), slow(H1)", "K8.close + prev_hour_fast(H1)", "fast(K7)", "K1~K4", "K8 自己算完的同时，K5~K8 也凑齐了 H2；下一根开始换锚点"),
        ("K9", "[02:00,02:15)", "02:15", "fast(H2), slow(H2)", "K9.close + prev_hour_fast(H2)", "fast(K8)", "K5~K8", "这是换锚点后的第一根 15m bar；从这里起 hour 锚点改成 H2"),
    ]
    count_tbody = "".join(
        f"<tr><td>{k}</td><td>{window}</td><td>{close_ts}</td><td>{anchor}</td><td>{current_input}</td><td>{prev_src}</td><td>{anchor_src}</td><td>{note}</td></tr>"
        for k, window, close_ts, anchor, current_input, prev_src, anchor_src, note in count_rows
    )
    return f"""
    <div class=\"card\">
      <h2>只看 current live：warmup → prev_hour_fast/slow → prev15_fast 的可视化</h2>
      <p>下面这块专门对应 <code>src/momentum/execution/canary32b/signal_adapter.py</code> 的 live 口径，不再混用简化回测。读法只有三步：</p>
      <ul>
        <li>先用很多根历史 15m bar 拼出<strong>已完成小时</strong>的 hour close，递推出 <code>prev_hour_fast</code> / <code>prev_hour_slow</code>。</li>
        <li>当前这根 15m close 到来时，用 <strong>上一已完成小时锚点</strong> + <strong>当前 15m close</strong> 递推当前 <code>ema_fast_1h</code> / <code>ema_slow_1h</code>。</li>
        <li><code>prev15_fast</code> 不是“上一小时的 fast”，而是<strong>上一根已完成 15m 决策 bar 当时算出来的 fast</strong>。</li>
      </ul>
      <div class=\"formula\">
        <div><strong>current live 核心公式</strong></div>
        <div class=\"math\" style=\"margin-top:8px\">ema_fast_1h(now) = α_fast · close_15m(now) + (1-α_fast) · prev_hour_fast</div>
        <div class=\"math\" style=\"margin-top:8px\">ema_slow_1h(now) = α_slow · close_15m(now) + (1-α_slow) · prev_hour_slow</div>
        <div class=\"math\" style=\"margin-top:8px\">prev15_fast = ema_fast_1h(previous completed 15m bar)</div>
      </div>
      <div class=\"formula\">
        <div><strong>一眼看懂这张图</strong></div>
        <div style=\"margin-top:8px\">灰色块 = 更早的 15m 历史；金色块 = 每个已完成小时的 hour close，会进入 warmup / prev_hour_fast 计算；绿色块 = 当前关注的连续 15m 决策 bar；蓝色箭头 = 用上一已完成小时的 EMA 锚点去递推当前 fast/slow；橙色箭头 = 上一根 15m 算出来的 <code>prev15_fast</code> 只用于比较，不会带未来 15m。</div>
      </div>
      <svg viewBox=\"0 0 1140 320\" role=\"img\" aria-label=\"Rank32B current live EMA walkthrough\" style=\"width:100%;margin-top:14px\">
        <rect x=\"16\" y=\"16\" width=\"1108\" height=\"288\" rx=\"18\" fill=\"#0f172a\" stroke=\"#274768\" stroke-width=\"1.4\"/>
        <text x=\"38\" y=\"44\" fill=\"#e5e7eb\" font-size=\"20\" font-weight=\"800\">current live EMA 计算时间轴（示例）</text>
        <text x=\"38\" y=\"68\" fill=\"#94a3b8\" font-size=\"13\">重点：先 warmup 出上一已完成小时的 EMA 状态，再用当前 15m close 递推；prev15_fast 来自上一根 15m，而不是“静态回填的一小时值”。</text>
        <g>
          <rect x=\"40\" y=\"108\" width=\"80\" height=\"54\" rx=\"10\" fill=\"#1f2937\" stroke=\"#334155\"/><text x=\"57\" y=\"130\" fill=\"#e5e7eb\" font-size=\"13\">11:15</text><text x=\"53\" y=\"151\" fill=\"#94a3b8\" font-size=\"12\">历史15m</text>
          <rect x=\"130\" y=\"108\" width=\"80\" height=\"54\" rx=\"10\" fill=\"#1f2937\" stroke=\"#334155\"/><text x=\"147\" y=\"130\" fill=\"#e5e7eb\" font-size=\"13\">11:30</text><text x=\"143\" y=\"151\" fill=\"#94a3b8\" font-size=\"12\">历史15m</text>
          <rect x=\"220\" y=\"108\" width=\"80\" height=\"54\" rx=\"10\" fill=\"#1f2937\" stroke=\"#334155\"/><text x=\"237\" y=\"130\" fill=\"#e5e7eb\" font-size=\"13\">11:45</text><text x=\"233\" y=\"151\" fill=\"#94a3b8\" font-size=\"12\">历史15m</text>
          <rect x=\"310\" y=\"108\" width=\"92\" height=\"54\" rx=\"10\" fill=\"#422006\" stroke=\"#92400e\"/><text x=\"323\" y=\"130\" fill=\"#fde68a\" font-size=\"13\">12:00</text><text x=\"321\" y=\"151\" fill=\"#fbbf24\" font-size=\"12\">hour close</text>
          <rect x=\"470\" y=\"108\" width=\"92\" height=\"54\" rx=\"10\" fill=\"#0f3a2f\" stroke=\"#047857\"/><text x=\"483\" y=\"130\" fill=\"#d1fae5\" font-size=\"13\">12:15</text><text x=\"479\" y=\"151\" fill=\"#6ee7b7\" font-size=\"12\">决策bar</text>
          <rect x=\"574\" y=\"108\" width=\"92\" height=\"54\" rx=\"10\" fill=\"#0f3a2f\" stroke=\"#047857\"/><text x=\"587\" y=\"130\" fill=\"#d1fae5\" font-size=\"13\">12:30</text><text x=\"583\" y=\"151\" fill=\"#6ee7b7\" font-size=\"12\">决策bar</text>
          <rect x=\"678\" y=\"108\" width=\"92\" height=\"54\" rx=\"10\" fill=\"#0f3a2f\" stroke=\"#047857\"/><text x=\"691\" y=\"130\" fill=\"#d1fae5\" font-size=\"13\">12:45</text><text x=\"687\" y=\"151\" fill=\"#6ee7b7\" font-size=\"12\">决策bar</text>
          <rect x=\"782\" y=\"108\" width=\"92\" height=\"54\" rx=\"10\" fill=\"#422006\" stroke=\"#92400e\"/><text x=\"795\" y=\"130\" fill=\"#fde68a\" font-size=\"13\">13:00</text><text x=\"787\" y=\"151\" fill=\"#fbbf24\" font-size=\"12\">边界/换锚点</text>
        </g>
        <text x=\"307\" y=\"214\" fill=\"#fbbf24\" font-size=\"12\">这根 12:00 作为上一已完成小时的收盘，会先进入 warmup，得到 prev_hour_fast / prev_hour_slow</text>
        <line x1=\"356\" y1=\"168\" x2=\"356\" y2=\"228\" stroke=\"#fbbf24\" stroke-width=\"2\"/>
        <rect x=\"250\" y=\"230\" width=\"220\" height=\"48\" rx=\"10\" fill=\"#13233f\" stroke=\"#274768\"/>
        <text x=\"268\" y=\"250\" fill=\"#dbeafe\" font-size=\"13\">warmup 输出</text>
        <text x=\"268\" y=\"270\" fill=\"#93c5fd\" font-size=\"12\">prev_hour_fast / prev_hour_slow</text>
        <line x1=\"470\" y1=\"86\" x2=\"724\" y2=\"86\" stroke=\"#38bdf8\" stroke-width=\"2.4\"/>
        <text x=\"540\" y=\"78\" fill=\"#7dd3fc\" font-size=\"12\">这里先只画同一个上一小时锚点下的 12:15 / 12:30 / 12:45 三根 15m；跨到下一小时时会重取新的 prev_hour_fast/slow</text>
        <line x1=\"516\" y1=\"168\" x2=\"516\" y2=\"228\" stroke=\"#38bdf8\" stroke-width=\"2\"/>
        <line x1=\"620\" y1=\"168\" x2=\"620\" y2=\"228\" stroke=\"#38bdf8\" stroke-width=\"2\"/>
        <line x1=\"724\" y1=\"168\" x2=\"724\" y2=\"228\" stroke=\"#38bdf8\" stroke-width=\"2\"/>
        <rect x=\"486\" y=\"230\" width=\"360\" height=\"48\" rx=\"10\" fill=\"#13233f\" stroke=\"#274768\"/>
        <text x=\"504\" y=\"250\" fill=\"#dbeafe\" font-size=\"13\">当前 bar 的 EMA</text>
        <text x=\"504\" y=\"270\" fill=\"#93c5fd\" font-size=\"12\">ema_fast_1h(now), ema_slow_1h(now) = f(prev_hour_fast/slow, close_15m(now))</text>
        <line x1=\"516\" y1=\"135\" x2=\"620\" y2=\"135\" stroke=\"#fb923c\" stroke-width=\"2\" marker-end=\"url(#arrow2)\"/>
        <line x1=\"620\" y1=\"135\" x2=\"724\" y2=\"135\" stroke=\"#fb923c\" stroke-width=\"2\" marker-end=\"url(#arrow2)\"/>
        <defs><marker id=\"arrow2\" markerWidth=\"10\" markerHeight=\"10\" refX=\"7\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L0,6 L7,3 z\" fill=\"#fb923c\"/></marker></defs>
        <text x=\"515\" y=\"196\" fill=\"#fdba74\" font-size=\"12\">prev15_fast 来自上一根 15m 决策 bar 的 fast</text>
      </svg>
      <div class=\"grid2\" style=\"margin-top:14px\">
        <div>
          <h3>Step A · warmup：先把很多根 15m 拼成已完成小时</h3>
          <table class=\"ex-table\">
            <thead><tr><th>已完成小时 close</th><th>hour_close</th><th>prev_hour_fast</th><th>prev_hour_slow</th></tr></thead>
            <tbody>{warm_tbody}</tbody>
          </table>
          <p class=\"small\">这一步只用<strong>已经结束的小时</strong>。它的作用不是直接发信号，而是生成下一批 15m bar 会共用的 hour-level EMA 锚点。</p>
        </div>
        <div>
          <h3>Step B · 当前关注的连续 15m bar</h3>
          <table class=\"ex-table\">
            <thead><tr><th>15m close</th><th>prev15_close</th><th>prev15_fast</th><th>close</th><th>prev_hour_fast</th><th>ema_fast_1h(now)</th><th>ema_slow_1h(now)</th><th>读法</th></tr></thead>
            <tbody>{focus_tbody}</tbody>
          </table>
          <p class=\"small\">重点看两列：<code>prev_hour_fast</code> 在这一组 15m bar 里是固定锚点；<code>prev15_fast</code> 则是一根一根往前滚的“上一根 15m fast”。所以 current live 里它通常和当前 <code>ema_fast_1h(now)</code> 不一样。</p>
        </div>
      </div>
      <h3 style=\"margin-top:18px\">按第几根 15m K 线数：K1 到 K9 逐根计数表</h3>
      <p>这张表只回答一个问题：<strong>每一根 K 线在收盘时，到底用了谁的数据？</strong> 记法固定如下：K1 = [00:00, 00:15) 在 00:15 收盘；K4 = [00:45, 01:00) 在 01:00 收盘，因此 K1~K4 合起来形成第一个完整小时 H1。</p>
      <table class=\"ex-table\">
        <thead>
          <tr>
            <th>K线</th>
            <th>时间段</th>
            <th>收盘时刻</th>
            <th>当前可用的 hour 锚点</th>
            <th>当前 fast 直接用了谁</th>
            <th>prev15_fast 来自谁</th>
            <th>hour 锚点来自哪几根 15m</th>
            <th>一句话说明</th>
          </tr>
        </thead>
        <tbody>{count_tbody}</tbody>
      </table>
      <div class=\"formula\">
        <div><strong>把这张表读成两句话就够了</strong></div>
        <div style=\"margin-top:8px\">1）<strong>同一小时里固定的是 hour 锚点</strong>：比如 K5/K6/K7/K8 都挂在同一个 <code>fast(H1)</code> 上。</div>
        <div style=\"margin-top:8px\">2）<strong>每一根 15m 都会重新算自己的当前 fast</strong>：K6 用 <code>K6.close + fast(H1)</code>，K7 用 <code>K7.close + fast(H1)</code>，所以 K6 的 <code>prev15_fast = fast(K5)</code> 通常不等于 K6 当前的 <code>ema_fast_1h(now)</code>。</div>
      </div>
    </div>
    """


HTML = """<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank32B 结构拆解：baseline / components / ablation</title>
  <style>
    :root{--bg:#0b1120;--panel:#111827;--panel2:#0f172a;--line:#24324a;--text:#e5e7eb;--muted:#94a3b8;--accent:#7dd3fc;--good:#34d399;--warn:#fbbf24;--bad:#f87171;--soft:#cbd5e1;color-scheme:dark}
    *{box-sizing:border-box}
    body{margin:0;background:linear-gradient(180deg,#0b1120,#0f172a);color:var(--text);font:16px/1.68 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}
    a{color:var(--accent);text-decoration:none;font-weight:700}
    code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;background:#0b1322;border:1px solid #22324a;border-radius:8px;padding:1px 6px;color:#dbeafe}
    .wrap{max-width:1180px;margin:0 auto;padding:28px 20px 72px}
    .hero,.card,.component,.exp{background:rgba(17,24,39,.94);border:1px solid var(--line);border-radius:18px;padding:20px 22px;box-shadow:0 10px 28px rgba(0,0,0,.22)}
    .hero{margin-bottom:18px}
    .card{margin-bottom:16px}
    .badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
    .badge{display:inline-block;padding:4px 10px;border-radius:999px;background:#13233f;border:1px solid #28456d;color:#bfdbfe;font-size:12px;font-weight:700}
    h1,h2,h3{margin:0 0 10px}
    h1{font-size:34px;line-height:1.2}
    h2{font-size:24px;margin-bottom:12px}
    h3{font-size:18px}
    p{margin:0 0 12px;color:var(--muted)}
    ul{margin:8px 0 0 18px;color:var(--soft)}
    li{margin:6px 0}
    .lead{font-size:18px;color:#dbeafe}
    .muted{color:var(--muted)}
    .nav{display:flex;flex-wrap:wrap;gap:10px 14px;margin-top:12px}
    .nav a{padding:8px 10px;border:1px solid #26415f;border-radius:10px;background:#0f1a2f}
    .grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
    .grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
    .big-quote{font-size:24px;line-height:1.5;color:#e0f2fe;font-weight:800}
    .note{padding:14px 16px;border-radius:14px;background:#0d1525;border:1px solid #22324a;color:#cbd5e1}
    .stack{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;align-items:stretch}
    .stack .layer{padding:14px 14px;border-radius:14px;border:1px solid #274261;background:#0e192d}
    .stack .layer strong{display:block;margin-bottom:6px;color:#dbeafe}
    .section-title{margin:30px 0 12px}
    .component-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
    .component{padding:18px 18px 16px}
    .component .k{display:block;color:#dbeafe;font-weight:800;margin-top:8px}
    .component .v{color:#cbd5e1}
    .pill{display:inline-block;padding:4px 9px;border-radius:999px;font-size:12px;font-weight:800;margin-right:8px}
    .pill.good{background:rgba(52,211,153,.14);color:#a7f3d0;border:1px solid rgba(52,211,153,.34)}
    .pill.warn{background:rgba(251,191,36,.12);color:#fde68a;border:1px solid rgba(251,191,36,.30)}
    .pill.bad{background:rgba(248,113,113,.12);color:#fecaca;border:1px solid rgba(248,113,113,.28)}
    .exp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
    .exp h3{margin-bottom:8px}
    .judgement{border-left:4px solid #38bdf8;padding-left:12px;margin:12px 0}
    .footer-links a{display:inline-block;margin:6px 10px 0 0}
    .small{font-size:13px;color:var(--muted)}
    .formula{padding:14px 16px;border-radius:14px;background:#0d1525;border:1px solid #22324a;color:#cbd5e1;margin-top:10px}
    .math{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:#dbeafe}
    table.ex-table{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}
    table.ex-table th,table.ex-table td{border:1px solid #24324a;padding:8px 10px;text-align:left;vertical-align:top}
    table.ex-table th{background:#0f1a2f;color:#dbeafe}
    .hint{color:#cbd5e1}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <div class=\"badges\">
        <span class=\"badge\">32b</span>
        <span class=\"badge\">baseline → components → ablation</span>
        <span class=\"badge\">研究母体 vs live 叠加层</span>
        <span class=\"badge\">reader-facing decomposition</span>
      </div>
      <h1>Rank32B 结构拆解页</h1>
      <p class=\"lead\">这页不发明新规则，也不重写旧研究；它只做一件事：把现有 Rank32B 还原成 <strong>最小 baseline + 若干可检验增量</strong>，并把 <strong>alpha 本体</strong> 和 <strong>live 部署层</strong> 分开。</p>
      <p>页面生成时间：__GENERATED_AT__</p>
      <div class=\"nav\">
        <a href=\"__PORTAL__\">32b 主页面</a>
        <a href=\"__TRANSPARENCY__\">交易逻辑透明页</a>
        <a href=\"__LIVE__\">实盘 Dashboard</a>
        <a href=\"__RESEARCH__\">主研究报告</a>
        <a href=\"__STABILITY__\">稳定性拆解页</a>
      </div>
    </div>

    <div class=\"grid2\">
      <div class=\"card\">
        <h2>这页的边界</h2>
        <ul>
          <li>只使用现有 32b 页面已经明示过的规则与口径。</li>
          <li>如果某条规则只属于 live execution，不把它硬塞进 baseline alpha。</li>
          <li>如果某条规则只是研究壳（例如固定持有 8 根 15m bar），会明确标注为 <strong>实验载体</strong>，不是母体 edge 主张。</li>
          <li>如果某条旧文案已经被 32b 当前主线删掉（例如 <code>spread-mid reclaim</code>），这页会把它视为 <strong>已删除历史层</strong>，而不是继续当核心规则。</li>
        </ul>
      </div>
      <div class=\"card\">
        <h2>一句话结论</h2>
        <p class=\"big-quote\">Rank32B 的母题是：<br/>先用 <code>1h EMA</code> 定结构方向，再只追那些 <code>15m close</code> 重新穿回 fast EMA、而且 <code>EMA slope</code> 已经明显同向展开的 continuation。</p>
        <p class=\"small\">翻成人话：不是“看到均线就追”，而是“方向先对、回穿先确认、斜率还得够强”。</p>
      </div>
    </div>

    <div class=\"card\">
      <h2>最小 baseline</h2>
      <div class=\"grid2\">
        <div>
          <ul>
            <li><strong>方向定义</strong>：<code>ema_fast_1h &gt; ema_slow_1h</code> 才允许 long；<code>ema_fast_1h &lt; ema_slow_1h</code> 才允许 short。</li>
            <li><strong>触发定义</strong>：long 为 <code>prev_close &lt;= prev_fast</code> 且 <code>close &gt; ema_fast_1h</code>；short 镜像。</li>
            <li><strong>baseline 不包含</strong>：<code>slope floor</code>、<code>strongest-only</code>、official-close freshness veto、并发限制、tiered universe、ATR TP/SL/timeout。</li>
          </ul>
        </div>
        <div class=\"note\">
          <strong>研究壳说明</strong>
          <p style=\"margin-top:8px\">为了让 ablation 可跑、可对照，这页把研究执行壳固定为 <code>signal close → next-bar open → non-overlap → hold 8 bars</code>。但这层只是实验载体，不算 Rank32B 的 alpha 主张。</p>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>术语与公式：先把 fast / slow / previous fast 说清楚</h2>
      <div class="grid2">
        <div>
          <ul>
            <li><strong>EMA fast</strong>：不是“更短周期图”，而是 <strong>同样基于 1h close</strong> 算出来的较快均线。在 clean replication 脚本里，它是 <code>EMA_FAST_1H = 20</code>。</li>
            <li><strong>EMA slow</strong>：同样基于 <strong>1h close</strong> 算出来的较慢均线。在 clean replication 脚本里，它是 <code>EMA_SLOW_1H = 50</code>。</li>
            <li><strong>1h 的意思</strong>：先把价格序列按 1 小时聚合，用每个 1h bar 的 <code>close</code> 形成 higher-tf 序列，再在这条 1h 序列上算 EMA；然后再把结果回填到 15m 决策行。</li>
            <li><strong>previous fast / prev_fast</strong>：广义上就是“上一根决策 bar 看到的 fast EMA 值”。但<strong>具体实现要分 clean research 和 current live</strong>。</li>
            <li><strong>previous close / prev_close</strong>：同理，就是上一根决策 bar 的收盘价；在 live 口径里通常写成 <code>prev15_close</code>。</li>
          </ul>
          <div class="formula">
            <div><strong>EMA 递推公式</strong></div>
            <div class="math" style="margin-top:8px">EMA_t = α · Price_t + (1 - α) · EMA_(t-1)</div>
            <div class="math" style="margin-top:8px">α = 2 / (N + 1)</div>
            <div style="margin-top:8px">所以在 32b 里：</div>
            <div class="math" style="margin-top:8px">ema_fast_1h = EMA(close_1h, N=20)</div>
            <div class="math" style="margin-top:8px">ema_slow_1h = EMA(close_1h, N=50)</div>
            <div class="math" style="margin-top:8px">fast_slope = ema_fast_1h.pct_change()</div>
            <div class="math" style="margin-top:8px">slow_slope = ema_slow_1h.pct_change()</div>
          </div>
        </div>
        <div>
          <div class="formula">
            <div><strong>baseline long 触发公式</strong></div>
            <div class="math" style="margin-top:8px">long_structure = (ema_fast_1h &gt; ema_slow_1h)</div>
            <div class="math" style="margin-top:8px">cross_only_long = long_structure ∧ (prev_close &lt;= prev_fast) ∧ (close &gt; ema_fast_1h)</div>
            <div style="margin-top:10px" class="hint">直白说：上一根 15m 收盘还在 fast EMA 下方或贴着它，这一根 15m 收盘重新站回 fast EMA 上方；同时 higher-tf 结构已经是 fast 在 slow 上方。</div>
          </div>
          <div class="formula">
            <div><strong>这里要订正：current live 的定义更精确</strong></div>
            <div style="margin-top:8px">clean replication 里，常见写法是先算完已收盘 1h EMA，再 <code>merge_asof(backward)</code> 回填到 15m，所以同一个小时里的多根 15m 可能拿到同一个 <code>ema_fast_1h</code>；此时 <code>prev_fast = frame["ema_fast_1h"].shift(1)</code> 的确可能和当前 <code>ema_fast_1h</code> 一样。</div>
            <div style="margin-top:8px">但 <strong>current live source-of-truth</strong>（<code>src/momentum/execution/canary32b/signal_adapter.py</code>）不是这么做的：它先拿上一已完成小时的 <code>prev_hour_fast</code>，再用当前这根 15m 的 <code>close</code> 递推当前的 <code>ema_fast_1h</code>；上一根则单独取 <code>prev15_fast</code>。所以在 live 里，<code>prev15_fast</code> 和当前 <code>ema_fast_1h</code> 通常<strong>不会</strong>一样，除非价格刚好让递推结果几乎不变。</div>
          </div>
        </div>
      </div>
      <h3 style="margin-top:16px">示例数据：current live 里 prev15_fast 到底是什么意思</h3>
      <table class="ex-table">
        <thead>
          <tr>
            <th>15m bar</th>
            <th>prev_close</th>
            <th>prev15_fast</th>
            <th>close</th>
            <th>ema_fast_1h</th>
            <th>ema_slow_1h</th>
            <th>读法</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>t-1</td>
            <td>-</td>
            <td>-</td>
            <td>99.8</td>
            <td>100.0</td>
            <td>98.7</td>
            <td>结构已经偏多（fast &gt; slow），但这根 15m close 还在 fast 下方。</td>
          </tr>
          <tr>
            <td>t</td>
            <td>99.8</td>
            <td>100.0</td>
            <td>100.6</td>
            <td>100.2</td>
            <td>98.7</td>
            <td>这一根满足 <code>prev15_close &lt;= prev15_fast</code> 且 <code>close &gt; ema_fast_1h</code>，所以这是一次 long cross。</td>
          </tr>
          <tr>
            <td>t+1</td>
            <td>100.6</td>
            <td>100.2</td>
            <td>100.9</td>
            <td>100.3</td>
            <td>98.7</td>
            <td>虽然价格还在 fast 上方，但因为上一根 close 已经在上方，<code>prev15_close &lt;= prev15_fast</code> 不再成立，所以不会连续重复记成新 cross。</td>
          </tr>
        </tbody>
      </table>
      <p class="small">这个表只是解释变量含义，不代表真实 market sample；真正的 32b 还会在 baseline 之上继续叠加 <code>aligned slope floor</code>，而 live 层还会再叠加 strongest-only、freshness、risk veto 等约束。</p>
    </div>

    __LIVE_EMA_DEMO__

    <div class=\"card\">
      <h2>把 baseline 推成 Rank32B 的结构树</h2>
      <div class=\"stack\">
        <div class=\"layer\">
          <strong>Layer 0 · baseline</strong>
          1h EMA 定方向 + 15m close 重新穿回 fast EMA。
        </div>
        <div class=\"layer\">
          <strong>Layer 1 · 核心 alpha 增量</strong>
          加 <code>aligned slope floor</code>，只留明显同向展开的 continuation。
        </div>
        <div class=\"layer\">
          <strong>Layer 2 · 组合选择层</strong>
          加 <code>same-bar strongest-only</code>，同窗只留最强币。
        </div>
        <div class=\"layer\">
          <strong>Layer 3 · live 执行卫生层</strong>
          official-close only、freshness、same-symbol / cross-lane veto、并发限制。
        </div>
        <div class=\"layer\">
          <strong>Layer 4 · 部署层</strong>
          ATR OCO exit、timeout、下单与状态同步。
        </div>
        <div class=\"layer\">
          <strong>Layer 5 · universe 层</strong>
          core3 → 扩池 → admission / whitelist / tiering。
        </div>
      </div>
    </div>

    <h2 class=\"section-title\">① entry filters</h2>
    <div class=\"component-grid\">
      <div class=\"component\">
        <h3>aligned slope floor</h3>
        <span class=\"pill good\">核心增量</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">要求 fast / slow EMA slope 同向，且 <code>|fast slope|</code> 过最小门槛，避免把很平、很弱的结构也认成 continuation。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 只知道“重新穿回 fast EMA”，却分不清这次回穿发生在强趋势里，还是发生在弱震荡里。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">减少假突破、提高胜率、降低无效 churn、改善成本后表现。</div>
      </div>
      <div class=\"component\">
        <h3>official-close only</h3>
        <span class=\"pill warn\">执行一致性层</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">只接受 15m official close 确认后的信号，不把 preview / 盘中碰一下当成真正 continuation。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 如果被 live 误实现，容易把未收盘噪音混成交易信号。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">减少假信号、降低 live / shadow 偏差、提高可复现性。</div>
      </div>
    </div>

    <h2 class=\"section-title\">② selection filters</h2>
    <div class=\"component-grid\">
      <div class=\"component\">
        <h3>same-bar strongest-only</h3>
        <span class=\"pill good\">组合层关键一刀</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">多个币在同一 timestamp 同时出信号时，只保留 <code>slope_strength</code> 最强的那个。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 默认会把一篮子相关币一起收进来，导致最强 continuation 被弱信号稀释，也把组合变成同质化暴露。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">提高平均单笔质量、减少同窗重复暴露、降低换手与拥挤、改善组合 tail。</div>
      </div>
    </div>

    <h2 class=\"section-title\">③ exit rules</h2>
    <div class=\"component-grid\">
      <div class=\"component\">
        <h3>fixed hold 8×15m</h3>
        <span class=\"pill warn\">研究壳</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">给 baseline 一个最朴素、最低自由度的兑现方式，让 entry ablation 能在统一口径下比较。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 只有 entry，没有可对照的 exit 壳。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">提高可解释性、降低过拟合风险、让不同 entry 版本能在同一执行口径下对比。</div>
      </div>
      <div class=\"component\">
        <h3>ATR OCO exit（TP / SL / timeout）</h3>
        <span class=\"pill warn\">部署层</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">入场后立刻形成 <code>TP + SL + timeout</code> 的风险闭环，把 live 退出从研究壳推进到实盘可执行。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">fixed hold 对 live 过于粗糙：不会提早兑现好单，也不会更快切掉坏单，还容易占用仓位。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低回撤、改善尾部、缩短平均持仓、提高 live 可部署性。</div>
      </div>
    </div>

    <h2 class=\"section-title\">④ risk veto / regime veto</h2>
    <div class=\"card\">
      <p>现有 32b 页面里，没有看到一个像“牛市/熊市开关”那样明确的市场状态型 regime gate；这层更像 <strong>execution veto</strong>，不是新的 alpha 母题。</p>
    </div>
    <div class=\"component-grid\">
      <div class=\"component\">
        <h3>signal freshness gate</h3>
        <span class=\"pill warn\">卫生条件</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">即便会扫描较长窗口，真正进入交易决策的信号也必须足够新，不允许历史 backlog 被误下成当前单。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline/backfill 风格实现容易把旧信号混进 live 执行。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">减少 stale fill、减少 live/backtest 偏差、提高事件归因正确性。</div>
      </div>
      <div class=\"component\">
        <h3>same-symbol single-position</h3>
        <span class=\"pill warn\">风险约束</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">同一 symbol 已有 live / pending 仓位时，不再重复叠仓。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 在连续重复触发时，可能把同一标的不断加码，导致暴露失真。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低单标的尾部风险、减少重复暴露、提高组合可控性。</div>
      </div>
      <div class=\"component\">
        <h3>max_concurrent_positions / max_new_signals_per_run</h3>
        <span class=\"pill warn\">容量约束</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">限制同一时刻总仓位数，以及单轮 run 最多新开多少个仓。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 在宽 universe 下可能从“抓最强 continuation”滑成“批量扫信号”。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低拥挤、控制保证金占用、约束组合 tail risk。</div>
      </div>
      <div class=\"component\">
        <h3>cross-lane conflict veto</h3>
        <span class=\"pill warn\">账户层约束</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">如果别的 lane 已经占了某个 symbol，32b 当前 lane 直接跳过。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 不知道账户里别的策略已经持有同一标的，容易跨策略重复暴露。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低跨系统重复风险、提高全账户风险一致性。</div>
      </div>
      <div class=\"component\">
        <h3>execution health gates</h3>
        <span class=\"pill warn\">基础设施层</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">只在 <code>trade_enabled</code>、API、行情延迟、ATR、状态同步都正常时放行。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 假设世界永远正常，但 live 世界里 data delay、API 故障、缺指标都是实实在在的问题。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低事故率、提高 live 可靠性、减少伪交易与错误归因。</div>
      </div>
    </div>

    <h2 class=\"section-title\">⑤ symbol / universe constraints</h2>
    <div class=\"component-grid\">
      <div class=\"component\">
        <h3>core3 universe（BTC / ETH / SOL）</h3>
        <span class=\"pill good\">研究起点</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">先在最清楚、最液、最容易解释的三条腿上验证母体 alpha。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">如果一开始就上宽 universe，很难区分“alpha 真的对”还是“扩池碰巧更好看”。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">提高解释性、降低微结构噪音、减少样本异质性。</div>
      </div>
      <div class=\"component\">
        <h3>cross-asset expansion</h3>
        <span class=\"pill good\">外推验证</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">把 <code>EMA cross + aligned slope floor</code> 外推到更多主流币，验证 edge 不是只在 core3 站住。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">core3 的最大问题是：它可能只是三条腿特例，而不是真正可扩展的 rotation alpha。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">提高 trade density、增加机会覆盖、验证 edge 是否可外推。</div>
      </div>
      <div class=\"component\">
        <h3>tiered admission / whitelist</h3>
        <span class=\"pill warn\">质量控制层</span>
        <div class=\"k\">理论作用：</div><div class=\"v\">不是“能做的都做”，而是按流动性、长窗稳定性、盘口质量把币分层放行。</div>
        <div class=\"k\">它试图解决 baseline 的什么缺陷：</div><div class=\"v\">baseline 扩池后容易把“回测看着行、实盘口子不友好”的币也一并带进来。</div>
        <div class=\"k\">预期改善指标：</div><div class=\"v\">降低滑点/深度风险、提高 live 可复制性、减少 universe 噪音。</div>
      </div>
    </div>

    <h2 class=\"section-title\">哪些组件彼此独立，哪些高度重叠</h2>
    <div class=\"grid2\">
      <div class=\"card\">
        <h3>看起来较独立的</h3>
        <ul>
          <li><code>aligned slope floor</code> vs <code>ATR OCO exit</code>：一个管 entry 质量，一个管 exit 风险闭环。</li>
          <li><code>same-bar strongest-only</code> vs <code>tiered admission</code>：一个管同窗谁最强，一个管哪些币有资格入池。</li>
          <li><code>cross-asset expansion</code> vs <code>signal freshness</code>：一个扩机会池，一个防 stale 执行。</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3>看起来高度重叠的</h3>
        <ul>
          <li><code>official-close only</code> 与 <code>freshness gate</code>：都在做 entry hygiene，只是一个防未收盘噪音，一个防过期信号。</li>
          <li><code>strongest-only</code>、<code>max_new_signals_per_run</code>、<code>max_concurrent_positions</code>：都在压缩暴露，目标高度相近。</li>
          <li><code>same-symbol single-position</code> 与 <code>cross-lane conflict veto</code>：都在防重复暴露，只是一个 lane 内，一个 lane 间。</li>
          <li><code>fixed hold 8 bars</code> 与 <code>ATR OCO exit</code>：这是两套互相竞争的 exit 家族，不该同时当作独立增量往上堆。</li>
        </ul>
      </div>
    </div>

    <h2 class=\"section-title\">最小 ablation 实验矩阵</h2>
    <div class=\"card\">
      <p>建议先把研究执行壳固定为：<code>official 15m close / next-bar open / non-overlap / hold 8 bars</code>。先只动一个组件轴，避免把“信号质量”与“部署层收益实现”搅在一起。</p>
    </div>
    <div class=\"exp-grid\">
      <div class=\"exp\"><h3>Exp1</h3><p><strong>baseline only</strong></p><p class=\"muted\">只保留 <code>ema_cross_only</code>，core3。</p></div>
      <div class=\"exp\"><h3>Exp2</h3><p><strong>baseline + aligned slope floor</strong></p><p class=\"muted\">先钉死 32b 最核心增量到底是不是这刀。</p></div>
      <div class=\"exp\"><h3>Exp3</h3><p><strong>baseline + strongest-only</strong></p><p class=\"muted\">不加 slope floor，单测 selection 有没有独立价值。</p></div>
      <div class=\"exp\"><h3>Exp4</h3><p><strong>baseline + aligned slope floor + strongest-only</strong></p><p class=\"muted\">看核心 entry 增量和组合选择能不能叠加。</p></div>
      <div class=\"exp\"><h3>Exp5</h3><p><strong>Exp2 + cross-asset expansion</strong></p><p class=\"muted\">从 core3 扩到更宽 universe，测 edge 是否能外推。</p></div>
      <div class=\"exp\"><h3>Exp6</h3><p><strong>Exp4 + cross-asset expansion</strong></p><p class=\"muted\">看“强 entry + 组合选择 + 扩池”是不是当前主线雏形。</p></div>
      <div class=\"exp\"><h3>Exp7</h3><p><strong>Exp6 + risk veto pack</strong></p><p class=\"muted\">加 <code>same-symbol / max-concurrent / cross-lane</code>，测组合约束值不值。</p></div>
      <div class=\"exp\"><h3>Exp8</h3><p><strong>Exp6 + ATR OCO exit</strong></p><p class=\"muted\">单测 live exit 家族到底给了什么，而不是把它混进 entry 归因里。</p></div>
    </div>

    <h2 class=\"section-title\">最后 3 个判断</h2>
    <div class=\"card\">
      <div class=\"judgement\">
        <h3>最值得优先验证的 1 个组件</h3>
        <p><strong>aligned slope floor</strong>。现有 clean replication 证据最直接支持这件事：删掉 reclaim 后 pocket 没塌，真正站住的更像就是这层 slope 约束。</p>
      </div>
      <div class=\"judgement\">
        <h3>最可能只是制造复杂度的 1 个组件</h3>
        <p><strong>ATR OCO exit</strong>。这里的意思不是它对部署没价值，而是：如果目标是解释 32b 的 alpha 母体，它更像部署/风控组件，不像第一层 edge 来源。</p>
      </div>
      <div class=\"judgement\">
        <h3>下一步最该做的唯一动作</h3>
        <p><strong>先只做 Exp1 vs Exp2</strong>：<code>ema_cross_only</code> 对 <code>ema_cross_only + aligned slope floor</code>。先把“edge 到底是不是 slope floor 提供的”钉死，再去讨论 strongest-only、扩池、ATR exit。</p>
      </div>
    </div>

    <div class=\"card\">
      <h2>这页依赖的 source-of-truth 页面</h2>
      <ul>
        <li><a href=\"__CLEAN__\">Rank32B clean replication</a>：给出 <code>baseline = ema_cross_only</code>、<code>Rank32B = ema_cross_plus_slope_floor</code>，并明确说明已经删除 <code>spread-mid reclaim</code>。</li>
        <li><a href=\"__RESEARCH__\">主研究报告</a>：提供研究主线与 exit / 成本 / live-like 版本的 reader-facing 汇总。</li>
        <li><a href=\"__TRANSPARENCY__\">交易逻辑透明页</a>：给出当前 live 的 strongest-only、freshness、risk、下单与退出链路。</li>
        <li><a href=\"__EXPANSION__\">跨资产扩展</a>：证明扩池时保留骨架不变，不混入新的 entry 规则优化。</li>
        <li><a href=\"__SCOPE__\">scope promotion check</a> 与 <a href=\"__ADMISSION__\">universe admission</a>：说明 admission / whitelist / paper promotion 是 quality-control 层，不是 baseline alpha 本体。</li>
        <li><a href=\"__GLOBAL_LIVE__\">global live / shadow 页面</a> 与 <a href=\"__STABILITY__\">稳定性拆解页</a>：回答 official-close、strongest-only、TP/SL/timeout、长窗稳定性这些 live 主线问题。</li>
      </ul>
      <p class=\"small\">如果以后 32b 改版，这页最该跟着更新的不是措辞，而是这条分层：<strong>baseline / core alpha / selection / live hygiene / exit / universe</strong>。</p>
    </div>

    <p class=\"small\">说明：这是一页解释型文档，不替代 Dashboard、透明页或研究页；它的价值在于减少“页面都看过，但还是说不清 32b 到底由哪几层组成”的沟通成本。</p>
  </div>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = HTML
    replacements = {
        "__GENERATED_AT__": escape(fmt_bj(datetime.now(timezone.utc))),
        "__PORTAL__": escape(PAGES["portal"]),
        "__TRANSPARENCY__": escape(PAGES["transparency"]),
        "__LIVE__": escape(PAGES["live"]),
        "__RESEARCH__": escape(PAGES["research"]),
        "__STABILITY__": escape(PAGES["stability"]),
        "__CLEAN__": escape(PAGES["clean"]),
        "__EXPANSION__": escape(PAGES["expansion"]),
        "__SCOPE__": escape(PAGES["scope"]),
        "__ADMISSION__": escape(PAGES["admission"]),
        "__GLOBAL_LIVE__": escape(PAGES["global_live"]),
        "__LIVE_EMA_DEMO__": build_live_ema_demo(),
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    OUT_PATH.write_text(html, encoding="utf-8")
    print({"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "out": str(OUT_PATH)})


if __name__ == "__main__":
    main()
