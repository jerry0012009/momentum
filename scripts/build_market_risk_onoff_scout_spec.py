#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_market_risk_onoff_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_market_risk_onoff_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "spec_meta.csv"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


SPEC_ROWS = [
    {
        "section": "run_context",
        "item": "why_this_candidate_now",
        "value": "EMA 当前 waiting_not_due；Rank 2 / Rank 17 都已进入 narrow paper pilot 且当前没有真实 append/review need；Rank 7~20 除 Rank 2/17 外均已 park。当前 fresh intake 应优先找更贴近 crypto cost/regime 约束、且能复用现有 repo 模块的 paper/repo based 候选。",
        "why_it_matters": "当前 Scout Seat 的最高边际价值不是继续补 P3 wiring，而是补一条能更快回答『regime gate 能不能让 15m crypto 动量/确认层更接近可交易 alpha』的新候选。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不伪造成 clean replication / paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_market_risk_onoff_15m_v1",
        "why_it_matters": "给这条新 intake 一个稳定句柄，方便后续 clean replication / Light Stability Pack / TODO / site 统一追踪。",
        "operator_rule": "后续所有 clean replication 与 verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Svogun & Bazán-Palomino (2022) Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter? + repo module market_risk_on_off_filter.py",
        "why_it_matters": "论文最值钱的启发不是再发明一条新 alpha，而是把『cost survival depends on regime / bubble state』压成可执行的 market-state gate；repo 里已存在最小可因果实现骨架。",
        "operator_rule": "v1 只允许把 regime gate 当环境门控；不允许把它包装成独立 alpha 主体。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m execution + 1h gate",
        "why_it_matters": "保持与当前 Scout 快筛同级样本，优先复用现有 15m crypto cache，并把 gate 降到 1h 背景层。",
        "operator_rule": "第一刀不扩币种、不延长样本、不追最新 completed bar。",
    },
    {
        "section": "pipeline",
        "item": "base_signal",
        "value": "baseline = existing multi-tf momentum long/short signal（5m + 15m momentum 同向）",
        "why_it_matters": "先把 regime gate 明确压在已知弱但可复核的 baseline 上，避免把改善误归因于换了一条全新 alpha。",
        "operator_rule": "v1 不叠加 breakout / retest / volume 组件；先只测 gate 本身是否有增量。",
    },
    {
        "section": "pipeline",
        "item": "market_state_features",
        "value": "1h gate features = trend_1h(close/close.shift(12)-1) + ema_ok_1h(close>EMA24) + vol_ok_1h(realized_vol_12h <= rolling_q80_72h)",
        "why_it_matters": "这是把论文里的『bubble / favorable regime 会改写技术规则生存性』翻译成最小、可因果、无外部标签的 gate。",
        "operator_rule": "所有 gate 特征都必须只用当下及过去 bar 计算；禁止用 future return 或后验 bubble 标注。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "baseline_mtf | trend_only_gate | market_risk_2of3 | market_risk_3of3",
        "why_it_matters": "先回答核心问题：更严格的 market-state gate 是否真能提升 cost survival，而不是只靠少交易。",
        "operator_rule": "四档共用同一 data window / execution / cost；差异只来自 gate 严格度。",
    },
    {
        "section": "variants",
        "item": "baseline_mtf_rule",
        "value": "只要 5m/15m momentum 同向即开仓；无额外 regime gate。",
        "why_it_matters": "给 gate 类候选一个朴素对照组，避免把少做交易误写成 alpha。",
        "operator_rule": "baseline 仅作对照，不因结果差就回避展示。",
    },
    {
        "section": "variants",
        "item": "trend_only_gate_rule",
        "value": "要求 trend_1h > 0.5% 才允许 baseline signal 生效；其余 no-trade。",
        "why_it_matters": "先测最便宜的一刀：只看 1h 方向背景能否改善成本后结果。",
        "operator_rule": "若 trend-only 已明显优于更复杂 gate，应优先保留更简单版本。",
    },
    {
        "section": "variants",
        "item": "market_risk_2of3_rule",
        "value": "trend_ok_1h + ema_ok_1h + vol_ok_1h 至少 2 项通过，baseline signal 才生效。",
        "why_it_matters": "这就是 repo 现有 market_risk_on_off_filter 的最小 clean-room 主版本。",
        "operator_rule": "若 gate 只是把交易数砍到极低，clean replication 后默认直接 park。",
    },
    {
        "section": "variants",
        "item": "market_risk_3of3_rule",
        "value": "trend_ok_1h + ema_ok_1h + vol_ok_1h 必须全部通过，baseline signal 才生效。",
        "why_it_matters": "给更严格 gate 一个上界，检验『更严』是不是只带来 no-trade。",
        "operator_rule": "若 3of3 的 no_trade_ratio > 85% 且未显著改善 cost survival，则直接 bench。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side first pass",
        "why_it_matters": "与当前 Scout 快筛保持同一执行口径，避免把改善误归因于不同出场规则。",
        "operator_rule": "第一刀不引入动态仓位、资金费率修正或更长持仓。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | cost_survival(6/10/15bps) | time_bucket_return",
        "why_it_matters": "这条线最容易靠少做交易看起来变稳，因此必须把 cost survival 与 no-trade 一起盯。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset；clean replication 后优先补四项 Light Stability Pack。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若最优 gate 在 6bps 下仍 positive_asset_ratio < 2/3，或相对 baseline 不能同时改善 post_cost_return / cost_survival，或只是靠 no_trade_ratio > 80% 才勉强守住收益，则直接 park；若 3of3 只是极端收缩交易数，也直接 park。",
        "why_it_matters": "提前写死失败条件，避免后续把『更少交易』误写成 regime alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先复用现有 market_risk_on_off_filter.py 与 Binance 15m cache，补 baseline_mtf / trend_only_gate / market_risk_2of3 / market_risk_3of3 四档最小回测，再按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "不要顺手扩写成 bubble labelling 大框架；先用现有可因果 proxy 做最小快筛。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_market_risk_onoff_15m_v1",
                "source": "Svogun & Bazán-Palomino (2022) + market_risk_on_off_filter.py",
                "desk_role": "new Scout intake / paper-repo based 15m crypto regime gate candidate",
                "hard_verdict": "当前最诚实的新 fresh intake，不是继续磨现有 P3 wiring，而是把『crypto cost / bubble-regime survival』压成可直接进入 clean replication 的 15m market risk-on/off gate spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先复用现有 market_risk_on_off_filter.py 与 Binance 15m cache，补 baseline_mtf / trend_only_gate / market_risk_2of3 / market_risk_3of3 四档最小 clean replication，再用时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
            }
        ]
    )
    return spec_df, meta_df



def render_table(df: pd.DataFrame) -> str:
    headers = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(row[col]))}</td>" for col in df.columns)
        rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"



def write_report(spec_df: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = meta_df.iloc[0]
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · market risk-on/off regime gate · clean-room spec</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · market risk-on/off regime gate · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把新的 paper/repo based regime-gate intake 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“regime gate 是否值得做最小 clean replication”，不是去争 <code>Live Seat</code>。</li>
      <li>它服务的是当前 desk 对 <code>cost survival / market-state honesty</code> 的需求，不是重开 breakout heavy follow-up。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2 / Rank 17</b> 都已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7~20</b> 除 Rank 2/17 外已完成 clean replication + Light Stability Pack 并压回 <code>park / evidence pool</code>。</li>
      <li>这条线既有外部论文锚点，又能直接复用 repo 现有 <code>market_risk_on_off_filter.py</code>，因此比再开一条更抽象的大框架更贴当前 desk。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_market_risk_onoff_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么先压成 gate？</b> 因为论文更像在说『什么时候技术规则还能活』，而不是直接发明一条新方向 alpha。</li>
      <li><b>为什么只保留 1h 三因子 gate？</b> 因为当前 desk 要的是最小可因果、可复核版本，不是先上 PSY bubble labelling 大框架。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 <code>market_risk_on_off_filter.py</code> 与 Binance 15m cache；不要顺手扩写成复杂 bubble classifier。</p>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> int:
    ensure_dir(ART_DIR)
    spec_df, meta_df = build_tables()
    spec_df.to_csv(SPEC_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    write_report(spec_df, meta_df)
    print("[ok] market risk-on/off scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
