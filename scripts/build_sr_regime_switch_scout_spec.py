#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_sr_regime_switch_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_sr_regime_switch_15m"
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
        "value": "Paper Seat=EMA 当前 waiting_not_due；Rank 7~14 均已 park；Rank 2 已 narrow paper pilot approved 且无真实 append/review need。",
        "why_it_matters": "当前 Scout Seat 的边际价值更高动作，是补一条新的 paper-based 15m crypto intake，而不是继续磨旧候选 wiring。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication 或 paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_sr_regime_switch_15m_v1",
        "why_it_matters": "给新的 Scout intake 一个稳定句柄，方便后续 clean replication / log / site / TODO 同名追踪。",
        "operator_rule": "后续 clean replication、Light Stability Pack、verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Henderson, Jacka, Liu, Maeda (2021/2025) optimal-stopping support/resistance paper",
        "why_it_matters": "这篇最值得迁移的不是数学推导本身，而是把 support/resistance 交易拆成 provisional break 与 confirmed regime switch 两层。",
        "operator_rule": "v1 不照搬论文连续时间模型；只迁移 path-dependent regime switch 的可因果交易分层。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 11/12/13/14 同级样本，继续复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不切新数据源、不追最新 bar。",
    },
    {
        "section": "pipeline",
        "item": "line_source",
        "value": "用现有 causal zone 读法生成 active support/resistance：优先复用最近 confirmed swing/averaged zone，不允许用未来 extremum 回填线位。",
        "why_it_matters": "让这条线尽量贴近当前 desk 已有的 structure/zone 资产，而不是另起一套难以落地的线位生成器。",
        "operator_rule": "active line 只能来自当下已确认的 zone；禁止事后最优对齐。",
    },
    {
        "section": "pipeline",
        "item": "state_machine",
        "value": "event_state ∈ {touch_or_cross, provisional_break, confirmed_switch}; 第一次收在线外只算 provisional_break，只有额外确认到位才升级为 confirmed_switch。",
        "why_it_matters": "把论文里的 path-dependent regime switch 思想翻成当前最重要的工程问题：不要把第一次越线直接当成新趋势已成立。",
        "operator_rule": "confirmed_switch 只能由当下和过去 bar 触发；禁止用 future return 反标记状态。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "touch_or_cross_baseline | confirm1_outside | confirm2of3_outside | retest_hold_reclaim",
        "why_it_matters": "先回答核心问题：support/resistance 里的状态切换确认，能不能比第一次穿线更诚实，而不是一开始就扩成复杂多因子系统。",
        "operator_rule": "四档共用同一 data window / cost / exit；差异只来自 switch-confirmation gate。",
    },
    {
        "section": "variants",
        "item": "touch_or_cross_baseline_rule",
        "value": "价格首次收盘站上最近 active resistance zone 上沿 + 0.03 ATR 做多；若收回 zone 中枢下方则平仓。",
        "why_it_matters": "给这条候选一个最朴素的 line-cross baseline，方便检验确认层是否真的有增量。",
        "operator_rule": "v1 只做 long-or-flat；不把 breakout short 拉回当前 desk 主舞台。",
    },
    {
        "section": "variants",
        "item": "confirm1_outside_rule",
        "value": "首次 provisional_break 后，下一根 bar 仍收在 resistance zone 上方 + 0.03 ATR，才升级为 confirmed_switch 并做多。",
        "why_it_matters": "这是最轻量、最贴近日常执行的 confirmed switch 定义。",
        "operator_rule": "若下一根收回 zone 内，则 setup 失效，不得回填成当根已确认。",
    },
    {
        "section": "variants",
        "item": "confirm2of3_outside_rule",
        "value": "首次 provisional_break 后，后续 3 根里至少 2 根收在 zone 上方 + 0.03 ATR，才做多。",
        "why_it_matters": "对应更保守的状态切换确认，检验‘多等一点是否真能减少假突破’。",
        "operator_rule": "若 3 根窗口内收回 zone 中枢下方，则该次 switch 直接作废。",
    },
    {
        "section": "variants",
        "item": "retest_hold_reclaim_rule",
        "value": "首次 provisional_break 后，价格在 3 根内回踩 resistance zone 但不跌破 zone 中枢，随后再次收在 zone 上方 + 0.02 ATR 时才做多。",
        "why_it_matters": "把论文的 regime switch 直觉收窄成当前 desk 更熟悉的 retest-hold reclaim 版本。",
        "operator_rule": "若回踩期间跌破 zone 中枢或 EMA20<EMA50，则该 setup 取消。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与当前 Scout 快筛保持同一执行口径，便于 apples-to-apples 比较。",
        "operator_rule": "第一刀不改出场规则；先看 confirmed-switch gate 本身是否值得保留。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | false_break_ratio | cost_survival",
        "why_it_matters": "这条线最容易靠少做交易制造错觉，因此必须把 false_break_ratio 与交易密度一起看。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 confirm1/confirm2of3/retest_hold 都不能同时改善 false_break_ratio 与 post_cost_return，或只是靠 no_trade_ratio>80% 才显得更稳，则直接 park；若 6bps 下跨资产 positive_asset_ratio < 2/3，也不进 paper candidate。",
        "why_it_matters": "提前写死失败条件，避免后续把‘多等几根’误写成天然 alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补四档 switch-confirmation 最小回测，再按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 Binance 15m cache 与现有 zone / EMA / ATR helper；不要切到更长样本或新线位引擎。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_sr_regime_switch_15m_v1",
                "source": "Henderson et al. (2021/2025)",
                "desk_role": "new Scout intake / paper-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的高边际值动作，是把 support/resistance 的 path-dependent regime-switch 思想冻结成 implementation-ready clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 touch_or_cross_baseline / confirm1_outside / confirm2of3_outside / retest_hold_reclaim 的最小 clean replication，然后按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · support/resistance regime-switch · clean-room spec</title>
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
  <h1>Scout Seat · support/resistance regime-switch · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把新的 paper-based 15m crypto intake 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“support/resistance 的 confirmed switch 值不值得做最小 clean replication”，不是立刻去争 <code>Live Seat</code>。</li>
      <li>它复用的是当前 desk 已有的 zone / EMA / ATR 组件，但把它们收窄成 <code>provisional break → confirmed switch</code> 的因果状态机。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7~14</b> 已完成 clean replication + Light Stability Pack，并都压回 <code>park / evidence pool</code>。</li>
      <li>这条线是新的 paper-based 15m crypto intake，而且更贴近当前 desk 想解决的核心问题：<b>第一次越线是不是太早，确认后的状态切换会不会更诚实</b>。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_sr_regime_switch_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么不照搬论文连续时间模型？</b> 因为当前 desk 要的是 15m crypto 快筛，而不是复述一套难以直接运行的理论最优停时结果。</li>
      <li><b>为什么要盯 false_break_ratio？</b> 因为这条线的真正价值不在“线位更多”，而在于确认层能不能减少假状态切换。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与现有 zone / EMA / ATR helper；不要切到新数据源或新线位引擎。</p>
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
    print("[ok] sr regime-switch scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
