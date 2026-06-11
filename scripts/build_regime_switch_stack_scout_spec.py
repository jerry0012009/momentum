#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_regime_switch_stack_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_regime_switch_stack_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "spec_meta.csv"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


SPEC_ROWS = [
    {
        "section": "run_context",
        "item": "desk_reason",
        "value": "Paper Seat=EMA 当前 waiting_not_due；Rank 7/8 已 park；Rank 2 已 narrow paper pilot approved 且无真实 append/review need。",
        "why_it_matters": "当前 Scout Seat 的边际价值更高动作是补一条新的 paper-based 15m crypto intake，而不是继续磨旧候选 wiring。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication 或 paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_regime_switch_stack_15m_v1",
        "why_it_matters": "给新的 Scout intake 一个稳定句柄，方便后续 clean replication / log / site / TODO 同名追踪。",
        "operator_rule": "后续 clean replication、Light Stability Pack、verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Naganjaneyulu et al. (2023) / Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm",
        "why_it_matters": "论文最值得迁移的不是日频 headline 收益，而是 no-buy-in-downtrend + regime switch 的设计原则。",
        "operator_rule": "v1 不照搬日频参数、不追求 faithful profit 数字，只迁移可因果实现的状态切换框架。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 2/5/7/8 同级样本，继续复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不切新数据源、不追最新 bar。",
    },
    {
        "section": "regime",
        "item": "state_definition",
        "value": "regime ∈ {uptrend, downtrend, fluctuating}; 用 RSI14 的 EMA7 做 market-state proxy：>60=uptrend，<40=downtrend，其余=fluctuating。",
        "why_it_matters": "把论文核心的 regime switch 压成最小、可复核、完全用当下 bar 可见信息计算的手写状态层。",
        "operator_rule": "禁止用未来收益或事后标签定义状态；阈值只允许在小邻域内做稳健性检查。",
    },
    {
        "section": "component",
        "item": "direction_component",
        "value": "ema_direction = sign(EMA20 - EMA50)",
        "why_it_matters": "继续复用当前 desk 最熟悉、最接近 paper 的 EMA 方向层，避免新 intake 一开始就开新大框架。",
        "operator_rule": "若 EMA20≈EMA50，则该组件记为 no-vote，不允许强行补方向。",
    },
    {
        "section": "component",
        "item": "protection_component",
        "value": "psar_protection = PSAR same-side filter；只在价格位于 PSAR 顺向侧时允许保留仓位",
        "why_it_matters": "对应论文里 PSAR 更像 protection / fast-exit，而不是主 alpha。",
        "operator_rule": "v1 先把 PSAR 限定为保仓/禁入过滤，不单独当开仓触发器。",
    },
    {
        "section": "component",
        "item": "timing_component",
        "value": "rsi_pullback = RSI14 从过热/过冷区回到 45~55 附近后的再转向确认，作为入场 timing 层",
        "why_it_matters": "把 RSI 收窄成 timing/filter，而不是让它单独扛方向判断。",
        "operator_rule": "若 timing 条件未满足，则只允许保持 no-trade，不可因为 regime 正确就直接开仓。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "ema_baseline | regime_gate_only | constrained_no_buy | regime_plus_psar_rsi",
        "why_it_matters": "先回答最核心问题：regime gating 本身是否有增量，还是必须叠加 protection/timing 才有意义。",
        "operator_rule": "所有版本共用同一 data window / cost / exit；差异只来自 gate 与组件堆叠。",
    },
    {
        "section": "variants",
        "item": "ema_baseline_rule",
        "value": "EMA20 > EMA50 做多，EMA20 < EMA50 平仓；不看 regime / PSAR / RSI",
        "why_it_matters": "给当前新 intake 一个最朴素的 15m baseline，对照 regime gate 是否真有增量。",
        "operator_rule": "这是对照组，不额外加 no-trade 逻辑。",
    },
    {
        "section": "variants",
        "item": "regime_gate_only_rule",
        "value": "只有 uptrend 才允许按 ema_baseline 做多；downtrend / fluctuating 一律 flat",
        "why_it_matters": "直接检验论文最值钱的想法：不该交易的时候别交易。",
        "operator_rule": "若只靠 no-trade_ratio 飙升才守住收益，则后续默认直接 park。",
    },
    {
        "section": "variants",
        "item": "constrained_no_buy_rule",
        "value": "uptrend 允许 EMA long；fluctuating 仅在 RSI14 从 <45 回升且 PSAR 顺向时允许更窄 long；downtrend 严格 no-buy",
        "why_it_matters": "对应 MIHCS 精神：在下跌里禁买，在边界状态里抬高入场门槛。",
        "operator_rule": "fluctuating 不直接做反转 alpha；只是更窄的 long confirmation。",
    },
    {
        "section": "variants",
        "item": "regime_plus_psar_rsi_rule",
        "value": "uptrend: EMA long + PSAR 顺向 + RSI 回踩后再转上；fluctuating/downtrend: flat",
        "why_it_matters": "把论文的 indicator stack 压成当前 desk 能快速复现的最小组合版。",
        "operator_rule": "若这个版本 trade_count 过低（例如 no_trade_ratio > 85%），即便收益为正也要优先怀疑是假改善。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与当前 Scout 快筛保持同一执行口径，便于 apples-to-apples 比较。",
        "operator_rule": "第一刀不改出场规则；先看 regime gate 本身是否值得保留。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | cost_survival | regime_bucket_return",
        "why_it_matters": "regime 候选最容易靠少做交易制造错觉，因此必须把 no-trade 与 trades_per_asset 放在一线指标。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset + per-regime。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 regime_gate_only / constrained_no_buy 不能同时改善 post_cost_return 与 drawdown/false-trade proxy，或只是靠 no_trade_ratio>80% 勉强转正，则直接 park；若最优版本在 6bps 下跨资产 positive_asset_ratio < 2/3，也不进 paper candidate。",
        "why_it_matters": "提前写死失败条件，避免后续把‘下跌不交易’误写成天然 alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先实现四档最小回测并补 Light Stability Pack，不再继续补 source-intake 文案。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 Binance 15m cache 与已有 EMA / PSAR / RSI 逻辑。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_regime_switch_stack_15m_v1",
                "source": "Naganjaneyulu et al. (2023)",
                "desk_role": "new Scout intake / paper-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的高边际值动作，是把 regime-switch indicator stack 冻结成 implementation-ready clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 ema_baseline / regime_gate_only / constrained_no_buy / regime_plus_psar_rsi 的最小 clean replication，然后按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · regime-switch indicator stack · clean-room spec</title>
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
  <h1>Scout Seat · regime-switch indicator stack · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把新的 paper-based 15m crypto intake 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“是否值得做最小 clean replication”，不是立刻去争 <code>Live Seat</code>。</li>
      <li>它复用的是当前 desk 已有的 EMA / PSAR / RSI 组件，但把它们收窄成 <code>regime gate + protection + timing</code> 的因果组合。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7 / Rank 8</b> 已完成 clean replication + Light Stability Pack，当前 verdict 都是 <code>park / evidence pool</code>。</li>
      <li>这条线是新的 paper-based 15m crypto intake，而且最值钱的原则是“下跌里别硬买、震荡里提高门槛”，更贴合当前 desk 想尽快筛出下一条 paper candidate 的目标。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_regime_switch_stack_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么不照搬论文日频收益数字？</b> 因为当前 desk 要的是 15m crypto 快筛，而不是复述一组不可直接迁移的 daily headline。</li>
      <li><b>为什么要把 no_trade_ratio 放到 scoreboard？</b> 因为 regime gate 很容易靠“不交易”制造表面改进，必须和 trades_per_asset 一起看。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与已有 EMA / PSAR / RSI 逻辑；不要切到新数据源或更复杂出场规则。</p>
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
    print("[ok] regime-switch stack scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
