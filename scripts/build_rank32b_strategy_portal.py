#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

ROOT = Path('/root/clawd/jerry/momentum')
SITE_DIR = ROOT / 'reports' / 'site'
PORTAL_DIR = SITE_DIR / 'factors' / 'rank32b'
PORTAL_PATH = PORTAL_DIR / 'report.html'

BASE = '/momentum'
PAGES = {
    'portal': f'{BASE}/factors/rank32b/report.html',
    'live': f'{BASE}/factors/rank32b_canary/report.html',
    'transparency': f'{BASE}/factors/rank32b/transparency.html',
    'decomposition': f'{BASE}/factors/rank32b/decomposition.html',
    'decision': f'{BASE}/factors/rank32b/exp12_decision.html',
    'rank_registry': f'{BASE}/factors/rank_registry_p3_p2/report.html',
    'control': f'{BASE}/canary-doc/',
    'research': f'{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/report.html',
    'stability': f'{BASE}/factors/rank32b/global_live_like_stability.html',
    'expansion': f'{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/cross_asset_expansion.html',
    'clean': f'{BASE}/reading/trendline_alpha_scout/rank32b_slope_floor_continuation_clean_replication.html',
    'home': f'{BASE}/index.html',
}

TARGET_HTMLS = [
    ROOT / 'reports' / 'site' / 'factors' / 'rank32b_canary' / 'report.html',
    ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m' / 'report.html',
    ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m' / 'cross_asset_expansion.html',
    ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'rank32b_slope_floor_continuation_clean_replication.html',
    ROOT / 'reports' / 'site' / 'factors' / 'rank32b' / 'decomposition.html',
    ROOT / 'reports' / 'site' / 'factors' / 'rank32b' / 'exp12_decision.html',
]

NAV_MARKER = 'rank32b-portal-nav'
NAV_STYLE = """
<style>
.rank32b-portal-nav{margin:16px 0 20px;padding:14px 16px;border:1px solid #24324a;border-radius:14px;background:#0d1525;color:#e5e7eb;font:14px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}
.rank32b-portal-nav .title{font-weight:700;margin-bottom:8px}
.rank32b-portal-nav .links{display:flex;flex-wrap:wrap;gap:10px 12px}
.rank32b-portal-nav a{color:#7dd3fc;text-decoration:none;font-weight:600}
.rank32b-portal-nav .muted{margin-top:8px;color:#94a3b8;font-size:13px}
</style>
""".strip()

NAV_HTML = f"""
<div class=\"{NAV_MARKER}\">
  <div class=\"title\">32b 策略导航</div>
  <div class=\"links\">
    <a href=\"{PAGES['portal']}\">32b 主页面</a>
    <a href=\"{PAGES['live']}\">实盘 Dashboard</a>
    <a href=\"{PAGES['transparency']}\">交易逻辑透明页</a>
    <a href=\"{PAGES['decomposition']}\">结构拆解页</a>
    <a href=\"{PAGES['decision']}\">Exp1 / Exp2 决策页</a>
    <a href=\"{PAGES['rank_registry']}\">全量 Rank（P3+P2）总表</a>
    <a href=\"{PAGES['control']}\">实盘控制台</a>
    <a href=\"{PAGES['research']}\">主研究报告</a>
    <a href=\"{PAGES['stability']}\">稳定性拆解页</a>
    <a href=\"{PAGES['expansion']}\">跨资产扩展</a>
    <a href=\"{PAGES['clean']}\">原始 Clean Replication</a>
  </div>
  <div class=\"muted\">建议使用顺序：主页面 → 实盘 Dashboard / 交易逻辑透明页 / 结构拆解页 / Exp1-Exp2 决策页 → 控制台 → 稳定性拆解页 / 主研究报告 → 跨资产扩展 → 原始 baseline。</div>
</div>
""".strip()


def fmt_bj(ts: datetime) -> str:
    bj = ts.astimezone(timezone(timedelta(hours=8)))
    utc = ts.astimezone(timezone.utc)
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def patch_page(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding='utf-8', errors='replace')
    changed = False

    if '</head>' in text and NAV_STYLE not in text:
        text = text.replace('</head>', NAV_STYLE + '\n</head>', 1)
        changed = True

    nav_pattern = re.compile(
        rf'<div class="{re.escape(NAV_MARKER)}">.*?<div class="muted">.*?</div>\s*</div>',
        re.S,
    )
    if NAV_MARKER in text:
        new_text, count = nav_pattern.subn(NAV_HTML, text, count=1)
        if count:
            text = new_text
            changed = True
    elif '<body>' in text:
        text = text.replace('<body>', '<body>\n' + NAV_HTML, 1)
        changed = True

    if changed:
        path.write_text(text, encoding='utf-8')


def build_portal() -> None:
    PORTAL_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = fmt_bj(datetime.now(timezone.utc))
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>32b 策略主页面</title>
  <style>
    :root{{color-scheme:dark;--bg:#0b1120;--panel:#111827;--panel2:#0f172a;--line:#24324a;--text:#e5e7eb;--muted:#94a3b8;--accent:#7dd3fc;--good:#34d399}}
    body{{margin:0;background:linear-gradient(180deg,#0b1120,#0f172a);color:var(--text);font:16px/1.65 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}}
    .wrap{{max-width:1100px;margin:0 auto;padding:28px 20px 60px}}
    h1,h2,h3{{margin:0 0 10px}}
    p{{margin:0 0 12px;color:var(--muted)}}
    .hero,.card{{background:rgba(17,24,39,.92);border:1px solid var(--line);border-radius:18px;padding:20px 22px;margin-bottom:18px;box-shadow:0 10px 28px rgba(0,0,0,.22)}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}
    .card h3{{font-size:18px}}
    .tag{{display:inline-block;padding:3px 8px;border-radius:999px;background:#13233f;border:1px solid #28456d;color:#bfdbfe;font-size:12px;margin-right:8px}}
    a{{color:var(--accent);text-decoration:none;font-weight:700}}
    ul{{margin:8px 0 0 18px;color:var(--muted)}}
    li{{margin:4px 0}}
    .lead{{font-size:18px;color:#dbeafe}}
    .primary{{display:inline-block;margin-top:12px;padding:11px 16px;border-radius:12px;background:#0ea5e9;color:#06121f;text-decoration:none;font-weight:800}}
    .small{{font-size:13px;color:var(--muted)}}
    .hard-note{{padding:14px 16px;border-radius:14px;border:1px solid #26415f;background:#0f1a2f;color:#dbeafe}}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <div class=\"tag\">32b</div><div class=\"tag\">实盘优先</div><div class=\"tag\">统一入口</div>
      <h1>32b 策略主页面</h1>
      <p class=\"lead\">以后你只需要从这个页面进入，就能找到 32b 的当前主入口。当前只把 <b>已按因果口径审计过</b> 的页面放在主路径里，旧研究页保留为历史归档，不再作为当前回测结果依据。</p>
      <p>页面生成时间：{generated_at}</p>
      <a class=\"primary\" href=\"{PAGES['live']}\">先看：32b 实盘 Dashboard</a>
    </div>

    <div class=\"card\">
      <h2>当前 live 运行方式（heartbeat）</h2>
      <div class=\"hard-note\">
        <p><b>真钱只保留 BTC / ETH；其余交易标的全部退回 shadow。</b></p>
        <p><b>当前参数：</b>BTCUSDT = 100 USDT；ETHUSDT = 20 USDT；max_concurrent = 1；TP = 1.00 ATR；SL = 1.00 ATR；timeout = 120m。</p>
        <p><b>边界：</b>32b 继续保留 live heartbeat，但不再作为主研发线，不再持续扩展维护。</p>
      </div>
    </div>

    <div class=\"card\">
      <h2>我现在最应该看什么？</h2>
      <div class=\"grid\">
        <div>
          <h3><a href=\"{PAGES['live']}\">1. 实盘 Dashboard</a></h3>
          <p>这是最重要的页面。看它能知道：策略是不是持续在跑、最近算到哪根 K 线、最近有没有信号、有没有触发交易、近期盈亏、告警、TP/SL/timeout 结构。</p>
        </div>
        <div>
          <h3><a href=\"{PAGES['transparency']}\">2. 交易逻辑透明页</a></h3>
          <p>这里把 live 开仓全流程可视化：信号怎么来、怎么选币、怎么判陈旧、为什么会被拒、何时下市价/限价、TP/SL/timeout 怎么挂。<strong>如果你要看执行链路和 source-of-truth，这页最合适。</strong></p>
        </div>
        <div>
          <h3><a href=\"{PAGES['decomposition']}\">3. 结构拆解页</a></h3>
          <p>这里专门回答“32b 到底是 baseline + 哪些可检验增量”。它把 alpha 本体、selection、risk veto、exit、universe 层拆开，适合研究讨论和 ablation 排序。</p>
        </div>
        <div>
          <h3><a href=\"{PAGES['decision']}\">4. Exp1 / Exp2 决策页</a></h3>
          <p>这里专门回答“aligned slope floor 相对 baseline 到底是不是值得保留的真实增量”。只保留冻结定义下的极简结论，不继续掺别的层。</p>
        </div>
        <div>
          <h3><a href=\"{PAGES['control']}\">5. 实盘控制台</a></h3>
          <p>这里用来改 live 关键配置：交易开关、仓位、杠杆、TP/SL/timeout、并发限制等。适合“我要改设置”。</p>
        </div>
        <div>
          <h3><a href=\"{PAGES['research']}\">6. 主研究报告</a></h3>
          <p>这里回答“这条策略在回测里到底长什么样、不同 exit 方案和成本口径表现如何”。适合研究和复盘。</p>
        </div>
      </div>
    </div>

    <div class=\"card\">
      <h2>最近新增：Exp1 / Exp2 极简决策页</h2>
      <p>如果你现在关心的是 <b>baseline 抓什么</b>、<b>aligned slope floor 到底改善了什么</b>，以及 <b>它是真实改善还是只是减少交易</b>，就先看这页。</p>
      <ul>
        <li>只看 Exp1 = baseline only vs Exp2 = baseline + aligned slope floor</li>
        <li>冻结同一因果口径、warmup、universe、成本、entry/exit 壳</li>
        <li>最后只给 Verdict / Keep-Watch-Drop / 是否值得进入下一轮 / 下一步唯一动作</li>
      </ul>
      <p><a class=\"primary\" href=\"{PAGES['decision']}\">打开：32b Exp1 / Exp2 决策页</a></p>
    </div>

    <div class=\"card\">
      <h2>结构拆解页</h2>
      <p>如果你现在关心的是 <b>32b 的最小 baseline 是什么</b>、<b>哪些层属于 alpha / selection / risk / exit / universe</b>，以及 <b>最小 ablation 应该先怎么做</b>，就看这页。</p>
      <ul>
        <li>把 Rank32B 还原成 baseline + 若干可检验增量</li>
        <li>明确区分研究母体和当前 live 叠加层</li>
        <li>给出最多 8 个最小 ablation 实验</li>
      </ul>
      <p><a class=\"primary\" href=\"{PAGES['decomposition']}\">打开：32b 结构拆解页</a></p>
    </div>

    <div class=\"card\">
      <h2>稳定性拆解页</h2>
      <p>如果你现在关心的是 <b>3/10/30/60d 短窗</b>、<b>180d 分段稳定性</b>，以及 <b>365d / 720d 长窗</b> 的当前正确口径，就直接看这页。</p>
      <ul>
        <li>整合最近 180d 的 18×10d / 6×30d 累计收益折线</li>
        <li>把 720d 拆成按月贡献，直接定位负贡献月份</li>
        <li>附 rolling 3m trade-return proxy / trade Sharpe</li>
      </ul>
      <p><a class=\"primary\" href=\"{PAGES['stability']}\">打开：32b 稳定性拆解页</a></p>
    </div>

    <div class=\"grid\">
      <div class=\"card\">
        <h3><a href=\"{PAGES['live']}\">A. 32b 实盘 Dashboard</a></h3>
        <p><b>讲什么：</b>当前正在运行的 live/canary 策略状态。</p>
        <ul>
          <li>最近算到哪根 K 线、最近信号时间、是否持续运行</li>
          <li>最近信号是否触发交易</li>
          <li>近期盈亏、方向分布、退出结构</li>
          <li>6 标的 strongest-only 实盘状态</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['transparency']}\">B. 交易逻辑透明页</a></h3>
        <p><b>讲什么：</b>把 32b 实盘的关键业务逻辑用流程图和 source-of-truth 方式摊开。</p>
        <ul>
          <li>重点是执行链路，不是研究归因</li>
          <li>信号如何触发、如何选币、如何判定延迟/陈旧</li>
          <li>same-bar / strongest-only / 单席位限制怎么起作用</li>
          <li>市价 / 限价 / TP / SL / timeout 的真实路径</li>
          <li>适合“我要看透明逻辑、找 bug、理解能力边界”</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['decomposition']}\">C. 结构拆解页</a></h3>
        <p><b>讲什么：</b>把 Rank32B 还原成 baseline、entry filters、selection、exit、risk veto、universe constraints。</p>
        <ul>
          <li>一句话母题</li>
          <li>最小 baseline</li>
          <li>每个组件的唯一增量主张</li>
          <li>最小 ablation 实验矩阵</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['decision']}\">D. Exp1 / Exp2 决策页</a></h3>
        <p><b>讲什么：</b>只回答 aligned slope floor 相对 baseline 是真实改善、局部改善、仅降频还是无效。</p>
        <ul>
          <li>冻结定义下的极简结论</li>
          <li>交易数 / 单笔质量 / 回撤 / 时间窗变化</li>
          <li>最后只保留决策动作</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['control']}\">E. 32b 实盘控制台</a></h3>
        <p><b>讲什么：</b>直接控制实盘策略运行的关键配置。</p>
        <ul>
          <li>trade_enabled / kill_switch</li>
          <li>目标仓位、并发、杠杆</li>
          <li>TP / SL / timeout</li>
          <li>适合“我要改 live 配置”</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['research']}\">F. 主研究报告</a></h3>
        <p><b>讲什么：</b>32b 主策略研究与执行/成本/退出版本比较。</p>
        <ul>
          <li>clean alpha 到执行版本的演变</li>
          <li>止盈 / 止损 / timeout 的回测比较</li>
          <li>适合回答“为什么 live 这样设”</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['stability']}\">G. 稳定性拆解页</a></h3>
        <p><b>讲什么：</b>把近期 180d 与长窗 720d 放在同一页里，回答“最近稳不稳、哪些月份拖后腿”。</p>
        <ul>
          <li>18×10d / 6×30d 累计收益折线</li>
          <li>720d 月度贡献拆解</li>
          <li>rolling 3m return / Sharpe proxy</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['rank_registry']}\">H. 全量 Rank（P3+P2）总表</a></h3>
        <p><b>讲什么：</b>把当前在 P3/P2 轨迹里的 rank 一次拉平，包含母题、角色、状态和下一步动作。</p>
        <ul>
          <li>排队视角：keep / watch / bench / archive</li>
          <li>研究视角：挑战 baseline 与唯一增量</li>
          <li>执行视角：下一步唯一动作（方便周更维护）</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['expansion']}\">I. 跨资产扩展</a></h3>
        <p><b>讲什么：</b>为什么从 3 标的扩到更宽资产池，以及跨资产 rotation 的回测结果。</p>
        <ul>
          <li>LTC / XRP / NEAR 等扩展资产表现</li>
          <li>多标的同时出信号时的轮动视角</li>
          <li>适合回答“为什么现在要做 strongest-only 扩池”</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['clean']}\">J. 原始 Clean Replication</a></h3>
        <p><b>讲什么：</b>最原始、最干净的 baseline，主要用于验证 alpha 本身，不带复杂 live 执行细节。</p>
        <ul>
          <li>更像“原始策略定义”</li>
          <li>适合回答“最初这条 alpha 是什么”</li>
        </ul>
      </div>
      <div class=\"card\">
        <h3><a href=\"{PAGES['home']}\">K. 返回站点首页</a></h3>
        <p><b>讲什么：</b>整个 momentum 站点的总入口。</p>
        <ul>
          <li>如果你想看其他策略，再回这里</li>
          <li>但对于 32b，建议优先从本页进入</li>
        </ul>
      </div>
    </div>

    <div class=\"card\">
      <h2>推荐使用顺序</h2>
      <ol style=\"margin:8px 0 0 20px;color:#cbd5e1\">
        <li>先看 <a href=\"{PAGES['live']}\">实盘 Dashboard</a>：确认是否在持续计算、是否有新信号、最近有没有交易和盈亏。</li>
        <li>再看 <a href=\"{PAGES['transparency']}\">交易逻辑透明页</a>：确认它到底按什么规则选币、判定陈旧信号、做风险拦截、下单和离场。</li>
        <li>如果你在问“32b 到底是 baseline 加了哪些增量”，第三步看 <a href=\"{PAGES['decomposition']}\">结构拆解页</a>。</li>
        <li>如果你在问“aligned slope floor 值不值得保留”，第四步看 <a href=\"{PAGES['decision']}\">Exp1 / Exp2 决策页</a>。</li>
        <li>需要改 live 参数时，再去 <a href=\"{PAGES['control']}\">实盘控制台</a>。</li>
        <li>如果你要拉平当前 P3/P2 队列，先看 <a href=\"{PAGES['rank_registry']}\">全量 Rank（P3+P2）总表</a>。</li>
        <li>如果你在问“最近稳不稳 / 哪个月拖后腿”，优先看 <a href=\"{PAGES['stability']}\">稳定性拆解页</a>。</li>
        <li>想知道为什么这样配置、回测里依据是什么，再看 <a href=\"{PAGES['research']}\">主研究报告</a> 和 <a href=\"{PAGES['expansion']}\">跨资产扩展</a>。</li>
        <li>想回到最原始定义，再看 <a href=\"{PAGES['clean']}\">Clean Replication</a>。</li>
      </ol>
    </div>

    <p class=\"small\">说明：这个页面是 32b 的统一信息架构入口，目标是减少“页面很多但没有主路径”的问题。当前请优先信任本页主路径上的 Dashboard / 透明页 / 结构拆解页 / Exp1-Exp2 决策页 / 稳定性页；旧研究页默认视为历史归档。</p>
  </div>
</body>
</html>
"""
    PORTAL_PATH.write_text(html, encoding='utf-8')


def main() -> None:
    build_portal()
    for path in TARGET_HTMLS:
        patch_page(path)
    print({'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'out': str(PORTAL_PATH), 'patched': [str(p) for p in TARGET_HTMLS if p.exists()]})


if __name__ == '__main__':
    main()
