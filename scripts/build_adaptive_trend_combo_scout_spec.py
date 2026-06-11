#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_adaptive_trend_combo_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_adaptive_trend_combo_15m"
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
        "value": "EMA 当前 waiting_not_due；Rank 1/3/4/5 均已 park；Rank 2 已进入 narrow paper pilot 且只剩 append/review need 时再继续。",
        "why_it_matters": "当前 Scout Seat 的最高边际价值不是再补 Rank 2 wiring，而是补一条新的 paper-based 15m crypto 候选 intake。",
        "operator_rule": "本轮只做 source intake + clean-room spec，不伪造成绩，不重开 breakout heavy analysis。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_adaptive_trend_combo_15m_v1",
        "why_it_matters": "给新的 Scout intake 一个稳定句柄，方便后续 clean replication / log / site 统一命名。",
        "operator_rule": "后续若进入 clean replication、Light Stability Pack、paper candidate，都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Mugueta-Aguinaga et al. (2023) / Trend following with machine learning in cryptocurrency markets",
        "why_it_matters": "论文核心启发不是上 ML，而是把 EMA / breakout / retest 看成按市场状态切换的组件池。",
        "operator_rule": "v1 严禁引入训练器；只允许固定权重、手写状态、现有组件，先测组合思路是否值得继续。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 2 / Rank 5 同级别样本，优先复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不延长样本、不切新数据源。",
    },
    {
        "section": "component",
        "item": "direction_component",
        "value": "ema_direction = sign(EMA20 - EMA50)",
        "why_it_matters": "保留当前 desk 最接近 paper 的 EMA 方向层，但把它降级成组合里的一个组件。",
        "operator_rule": "若 ema_direction = 0，则该组件记为 no-vote，不允许强行补方向。",
    },
    {
        "section": "component",
        "item": "breakout_component",
        "value": "combo_breakout = Rank 2 combo_all 的 breakout confirmation vote（与 clean-room spec 保持同一因果口径）",
        "why_it_matters": "优先复用当前唯一 surviving Scout 证据，不重复发明新的 breakout 家族。",
        "operator_rule": "若当前没有现成 combo_all signal 产物，就先用同口径事件检测补出 signal layer；禁止回退到 bench 的 raw breakout headline。",
    },
    {
        "section": "component",
        "item": "retest_component",
        "value": "retest_guard = price stays beyond breakout boundary for 2-of-3 closes or support-flip persists within 3 bars",
        "why_it_matters": "把 retest/fib 角色收窄成确认组件，而不是让它单独扛 alpha。",
        "operator_rule": "v1 只允许做 confirmation vote，不允许单独开仓。",
    },
    {
        "section": "regime",
        "item": "state_definition",
        "value": "state ∈ {trend, turbulent, chop}; trend 由 EMA20/EMA50 spread sign + magnitude 定义；turbulent 由 20-bar realized_vol 分位定义；其余归入 chop",
        "why_it_matters": "先把论文里的‘状态切换’压成手写 regime，而不是直接变成大框架或训练问题。",
        "operator_rule": "regime 只能用当下可见 bar 计算；禁止用未来回报或后验标签定义状态。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "fixed_priority | equal_vote | state_weighted_vote",
        "why_it_matters": "先回答最核心的问题：状态切换组合是否比固定组件顺序更诚实、更有增量。",
        "operator_rule": "三档共用同一 data window / execution / cost；差异只来自组件聚合方式。",
    },
    {
        "section": "variants",
        "item": "fixed_priority_rule",
        "value": "先看 ema_direction，再要求 combo_breakout 同向，最后要求 retest_guard 确认；三者顺序固定",
        "why_it_matters": "这是当前 desk 里最接近‘固定规则串联’的对照组。",
        "operator_rule": "若任一层失败则 no-trade。",
    },
    {
        "section": "variants",
        "item": "equal_vote_rule",
        "value": "ema_direction / combo_breakout / retest_guard 各 1 票；同向票数 >= 2 才开仓",
        "why_it_matters": "先看简单组合本身有没有增量，不把全部改进都归因于 state switch。",
        "operator_rule": "若多空同票或票数 < 2，则 no-trade。",
    },
    {
        "section": "variants",
        "item": "state_weighted_rule",
        "value": "trend: EMA 0.5 / breakout 0.3 / retest 0.2；turbulent: EMA 0.2 / breakout 0.3 / retest 0.5；chop: EMA 0.2 / breakout 0.1 / retest 0.2，额外保留 0.5 no-trade 倾向",
        "why_it_matters": "把论文里的‘组件池 + 状态切换’压成最小可实现规则。",
        "operator_rule": "仅当同向加权得分 >= 0.6 且反向得分 < 0.4 时开仓；否则 no-trade。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "保持与 Rank 2 / Rank 5 同一执行口径，避免因为出场规则变化而误读组合增量。",
        "operator_rule": "第一刀不改 SL/TP/time stop。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | cost_survival | regime_bucket_return",
        "why_it_matters": "这条线最容易靠‘更少交易’看起来更稳，因此必须把 no-trade 与 cost survival 一起盯。",
        "operator_rule": "网页与 artifact 同时展示 aggregate + per-asset + per-regime。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 state_weighted_vote 相对 fixed_priority 不能同时改善 post_cost_return 与 cost_survival，或只是靠 no-trade_ratio 飙升 > 70% 才勉强守住收益，则直接 park；若 equal_vote 已明显优于 fixed_priority，则优先保留更简单版本。",
        "why_it_matters": "提前写死失败条件，避免后续把‘更少交易’误写成组合优势。",
        "operator_rule": "first verdict 后必须给出 park / paper candidate / narrow paper pilot 三选一，不留 spec-only 漂浮状态。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补 signal layer + fixed_priority / equal_vote / state_weighted_vote 的最小回测，不再继续补 intake wording。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 EMA / Rank 2 combo_all / retest 边界逻辑与 Binance 15m cache。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_adaptive_trend_combo_15m_v1",
                "source": "Mugueta-Aguinaga et al. (2023)",
                "desk_role": "new Scout intake / paper-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的新 intake 不是再发明一条更花的 alpha，而是把‘状态切换下的 EMA+breakout+retest 组件组合’压成 implementation-ready clean-room spec；它暂时只通过 source intake，不应误写成已通过 clean replication。",
                "next_step": "优先补最小 signal layer 与 fixed_priority / equal_vote / state_weighted_vote 三档 clean replication，再用成本 / 交易数 / 跨标的四项快筛决定是 park 还是进入 paper candidate pool。",
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
  <title>Scout Seat · adaptive trend combo · clean-room spec</title>
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
  <h1>Scout Seat · adaptive trend combo · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 本页不是成绩宣判页，而是把新的 paper-based 15m crypto intake 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“是否值得做最小 clean replication”，不是立刻去争 `Live Seat`。</li>
      <li>它也不是要重写整个框架；v1 只允许固定权重 + 手写状态 + 现有组件。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么这条 intake 现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 1 / 3 / 4 / 5</b> 已分别给出 <code>park</code>，继续重看更像 closeout copy。</li>
      <li>这条线复用的是当前 desk 已有组件（EMA / breakout confirmation / retest guard），但换成更窄的 paper-based 组合假设，因此更适合当下一条 Scout intake。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_adaptive_trend_combo_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 `time-to-clean-replication`。</li>
      <li><b>为什么不用 ML？</b> 因为当前 Scout Seat 的要求是快筛，不是新开大框架；先验证状态切换组合是否有增量，再谈更复杂的训练器。</li>
      <li><b>为什么要同时盯 no-trade_ratio？</b> 因为组合/状态切换最容易靠少做交易制造“看起来更稳”的错觉。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与已有 EMA / Rank 2 confirmation 逻辑；不要切到新数据源或更复杂出场规则。</p>
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
    print("[ok] adaptive trend combo scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
