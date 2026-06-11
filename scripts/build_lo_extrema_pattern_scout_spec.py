#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_lo_extrema_pattern_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_lo_extrema_pattern_15m"
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
        "value": "EMA 当前 waiting_not_due；Rank 7/8/9/10 均已 park；Rank 2 已 narrow paper pilot approved 且只有 append/review need 时再继续。",
        "why_it_matters": "当前 Scout Seat 最该补的是新的 paper/repo based 15m crypto intake，而不是继续磨旧候选 wiring。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication 或 paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_lo_extrema_pattern_15m_v1",
        "why_it_matters": "给新的 repo-based Scout intake 一个稳定句柄，方便后续 clean replication / Light Stability Pack / TODO / site 统一追踪。",
        "operator_rule": "后续所有 clean replication 与 verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Lo et al. (2000) + SITONGRUC/FOUNDATIONS_OF_TECHNICAL_ANALYSIS third-party replication repo",
        "why_it_matters": "最值钱的不是照搬 notebook，而是把 kernel smoothing -> extrema -> pattern rule 的工程分层翻译成当前 desk 可因果执行的 15m crypto clean-room spec。",
        "operator_rule": "v1 禁止照搬 repo 中任何非因果 kernel 回看实现；只迁移可因果实现的分层流程。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 2/5/7/8/9/10 同级样本，继续复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不切新数据源、不追最新 bar。",
    },
    {
        "section": "pipeline",
        "item": "causal_smoothing",
        "value": "用 one-sided EMA9(hlc3) 作为 v1 causal smoothing proxy；每根 bar 只允许使用当下及过去数据。",
        "why_it_matters": "repo 里的 kernel regression 更像教学实现，当前 desk 需要先把 smoothing 层压成无 lookahead 的最小可实现版本。",
        "operator_rule": "禁止 centered window、禁止 future bars、禁止回填式平滑。",
    },
    {
        "section": "pipeline",
        "item": "confirmed_extrema",
        "value": "在平滑序列上找 confirmed local highs/lows：候选 extrema 必须在后续 2 根 bar 仍未被突破，确认延迟固定为 2 bars。",
        "why_it_matters": "把 repo 的 extrema 流程改写成明确有延迟、但无 repaint 的因果事件层。",
        "operator_rule": "只能在 extrema 被确认后才允许进入 pattern rule；不得用未确认 swing。",
    },
    {
        "section": "pipeline",
        "item": "zone_construction",
        "value": "最近 2~3 个同侧 confirmed extrema 若价差 <= 0.35 ATR，则聚合为一个 swing zone；否则只保留最新确认位。",
        "why_it_matters": "把 pattern rule 建在 zone 上，而不是像素级单点；也更贴近当前 desk 已接受的 retest/zone 读法。",
        "operator_rule": "zone 只能由已确认 extrema 聚合，不得用未来最优对齐。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "swing_break_only | double_bottom_reclaim | pullback_recovery_gate | pattern_vote_guard",
        "why_it_matters": "先回答核心问题：结构 pattern 本身是否有最小增量，而不是一开始就把整个图形库都搬进来。",
        "operator_rule": "四档共用同一 data window / cost / exit；差异只来自 pattern gate。",
    },
    {
        "section": "variants",
        "item": "swing_break_only_rule",
        "value": "close 突破最近 confirmed swing-high zone 上沿 + 0.05 ATR 做多；跌破最近 swing-low zone 下沿 - 0.05 ATR 平仓。",
        "why_it_matters": "给 pattern 类候选一个最朴素的 structure baseline，先看单纯 swing-zone breakout 是否比现有 fast-lane 更有味道。",
        "operator_rule": "v1 不做做空；只允许 long-or-flat。",
    },
    {
        "section": "variants",
        "item": "double_bottom_reclaim_rule",
        "value": "上升背景下，若最近两次 confirmed lows 落在同一 support zone（差距 <= 0.35 ATR），且第二个 low 后收盘重回 zone 上方并突破中间 swing high，则做多。",
        "why_it_matters": "把 repo/paper 里最常见、最容易写成因果规则的双底重夺压成最小 long-only 模式。",
        "operator_rule": "若第二个 low 形成前已有 breakout，则该模式作废，防止事后拼图。",
    },
    {
        "section": "variants",
        "item": "pullback_recovery_gate_rule",
        "value": "EMA20 > EMA50 背景下，价格先突破 resistance zone，再在 3 bars 内回踩 zone 但未失守，随后再次收在 zone 上方 + 0.03 ATR 才做多。",
        "why_it_matters": "把 pattern 候选收窄成顺趋势 pullback recovery，而不是重新大开 breakout 分支。",
        "operator_rule": "若回踩期间收破 zone 中枢，则直接取消该 setup。",
    },
    {
        "section": "variants",
        "item": "pattern_vote_guard_rule",
        "value": "double_bottom_reclaim 与 pullback_recovery_gate 各 1 票，再加 ema_direction 1 票；同向票数 >= 2 才做多，否则 flat。",
        "why_it_matters": "先检验简单 pattern vote 是否比单一结构条件更稳，而不是马上扩成大而全图形框架。",
        "operator_rule": "如果 no_trade_ratio > 80% 才勉强转正，clean replication 后默认直接 park。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与当前 Scout 快筛保持同一执行口径，避免把改进误归因于不同 exit 设计。",
        "operator_rule": "第一刀不引入更复杂的 trailing stop 或动态仓位。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | false_break_proxy | cost_survival",
        "why_it_matters": "pattern 候选很容易靠少做交易看起来更稳，因此必须同时盯交易数与 false-break proxy。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若最优 pattern 版本在 6bps 下 positive_asset_ratio < 2/3，或 post_cost_return 不优于 swing_break_only，或只是靠 no_trade_ratio>80% 才守住收益，则直接 park；若 clean replication 暴露 extrema/zone 逻辑需要大量主观补丁，也直接 park。",
        "why_it_matters": "提前写死失败条件，避免后续把‘结构更复杂’误写成 alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补 causal smoothing + confirmed extrema + 4 档 pattern gate 的最小回测，再按 Light Stability Pack 给出 park 或继续。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 Binance 15m cache 与已有 EMA / ATR helper；不要切到更长样本或更复杂 pattern 库。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_lo_extrema_pattern_15m_v1",
                "source": "Lo et al. (2000) + SITONGRUC repo",
                "desk_role": "new Scout intake / repo-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的新 fresh intake 是把 Lo 风格的 smoothing -> extrema -> pattern 流程压成因果、可复核的 15m crypto clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 swing_break_only / double_bottom_reclaim / pullback_recovery_gate / pattern_vote_guard 四档最小 clean replication，再用时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · Lo extrema pattern · clean-room spec</title>
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
  <h1>Scout Seat · Lo extrema pattern · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把 repo-based pattern candidate 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“是否值得做最小 clean replication”，不是去争 <code>Live Seat</code>。</li>
      <li>它借的是 repo 里的流程分层，不是把 notebook 里的非因果实现原样搬进 desk。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7 / 8 / 9 / 10</b> 已完成 clean replication + Light Stability Pack，并都压回 <code>park / evidence pool</code>。</li>
      <li>Lo 风格 candidate 是新的 <b>repo-based 15m crypto intake</b>：既复用当前 desk 已经熟悉的结构/zone 语义，又不要求新数据源或更花的模型。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_lo_extrema_pattern_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么不用 kernel regression 原实现？</b> 因为 repo 更像教学代码；当前 desk 先要无 lookahead、可延迟确认的最小版本。</li>
      <li><b>为什么只做 long-or-flat？</b> 因为当前项目默认不再强调 breakout short；先验证结构 pattern 是否能为 long 侧提供更诚实的 gate。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与已有 EMA / ATR helper；不要切到更长样本或更复杂 pattern 库。</p>
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
    print("[ok] lo extrema pattern scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
