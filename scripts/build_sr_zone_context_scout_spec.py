#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_sr_zone_context_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_sr_zone_context_15m"
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
        "value": "EMA 当前 waiting_not_due；Rank 7/8/9/10/11 均已 park；Rank 2 已 narrow paper pilot approved 且只有 append/review need 时再继续；shortlist 剩余 rank5/6 偏 prediction-market 或跨资产 proxy，不如新的 paper-based 15m crypto zone candidate 贴 desk。",
        "why_it_matters": "当前 Scout Seat 最该补的是新的 paper/repo based 15m crypto intake，而不是继续磨旧候选 wiring，或切去偏离主线的执行型假说。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication 或 paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_sr_zone_context_15m_v1",
        "why_it_matters": "给 averaged support/resistance zone 候选一个稳定句柄，方便后续 clean replication / Light Stability Pack / TODO / site 统一追踪。",
        "operator_rule": "后续所有 clean replication 与 verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Zhang & Zhou (2024) What are Effective Support and Resistance Levels? Evidence from High and Low Prices",
        "why_it_matters": "论文最值钱的不是再喊一次 breakout，而是把『longer-window averaged resistance zone + context』压成更诚实的确认层。",
        "operator_rule": "v1 只迁移 long-side resistance-zone 读法；不把 short breakout 当镜像主角。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 2/7/8/9/10/11 同级样本，继续复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不切新数据源、不追最新 bar。",
    },
    {
        "section": "pipeline",
        "item": "zone_construction",
        "value": "用过去 80 bars 的 confirmed swing highs 构造 resistance 候选；若相邻 highs 落在 0.30 ATR 内，则取其均值做 averaged resistance zone 中枢，并记录 zone_high/zone_low。",
        "why_it_matters": "把论文里的 averaged nearby levels 翻译成当前 desk 可因果执行的 15m zone 构造，而不是死守单一像素线。",
        "operator_rule": "zone 只能由已确认 swing highs 构造；禁止 future alignment、禁止用后见之明补线。",
    },
    {
        "section": "pipeline",
        "item": "context_filters",
        "value": "只在 EMA20 > EMA50 且 zone_width <= 1.2 ATR 的顺趋势/不过宽 channel 背景里允许 long setup；若 zone 过宽则视为 context_fail。",
        "why_it_matters": "论文明确提示 breakout effectiveness 依赖历史 price channel 与趋势背景；desk 需要先把这个 context 约束写死。",
        "operator_rule": "v1 不引入更多 regime 分类器；只允许 EMA trend + zone width 两个最小 context 过滤。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "single_line_break | averaged_zone_break | averaged_zone_retest | averaged_zone_context_gate",
        "why_it_matters": "先回答核心问题：zone averaging 与 context gate 是否真比 single-line 更诚实，而不是一开始扩写成大而全 SR 框架。",
        "operator_rule": "四档共用同一 data window / cost / exit；差异只来自 zone 与 context gate。",
    },
    {
        "section": "variants",
        "item": "single_line_break_rule",
        "value": "close 突破最近 confirmed swing high + 0.05 ATR 做多；跌回该 swing high 下方则 flat。",
        "why_it_matters": "给 zone 类候选一个朴素 baseline，先看 averaged zone 是否比单线更值钱。",
        "operator_rule": "v1 不做做空；只允许 long-or-flat。",
    },
    {
        "section": "variants",
        "item": "averaged_zone_break_rule",
        "value": "close 突破 averaged resistance zone 上沿 + 0.05 ATR 做多；若后续收回 zone 中枢下方则退出。",
        "why_it_matters": "直接测试论文主张：averaged nearby levels 是否优于 single-line breakout。",
        "operator_rule": "zone 必须来自过去 confirmed highs；禁止用突破后新高回写 zone。",
    },
    {
        "section": "variants",
        "item": "averaged_zone_retest_rule",
        "value": "先突破 averaged resistance zone，再在 3 bars 内回踩 zone 但不失守，随后再次收在 zone_high + 0.03 ATR 上方才做多。",
        "why_it_matters": "把『zone』真正变成 retest confirmation，而不是只把单线换个名字。",
        "operator_rule": "若回踩期间 close 跌破 zone_mid，则 setup 取消。",
    },
    {
        "section": "variants",
        "item": "averaged_zone_context_gate_rule",
        "value": "在 averaged_zone_retest 基础上，再要求 EMA20 > EMA50 且 zone_width <= 1.2 ATR；否则 no-trade。",
        "why_it_matters": "先检验 context gate 是否能把 zone candidate 压成更诚实的 long-side confirmation。",
        "operator_rule": "若候选只是靠 no_trade_ratio > 80% 才勉强转正，clean replication 后默认直接 park。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与当前 Scout 快筛保持同一执行口径，避免把改善误归因于不同 exit 设计。",
        "operator_rule": "第一刀不引入 trailing stop、动态仓位、更多 channel 层。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | false_break_ratio | cost_survival",
        "why_it_matters": "zone candidate 很容易靠少做交易看起来更稳，因此必须同时盯交易数与假突破率。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若最优 zone 版本在 6bps 下 positive_asset_ratio < 2/3，或 post_cost_return 不优于 single_line_break，或只是靠 no_trade_ratio > 80% 才守住收益，则直接 park；若 zone 构造需要大量主观补丁，也直接 park。",
        "why_it_matters": "提前写死失败条件，避免把『线换成带』误写成 alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补 single_line vs averaged_zone vs retest vs context_gate 四档最小回测，再按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 Binance 15m cache 与已有 EMA / ATR / swing helper；不要切到更长样本或新框架。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_sr_zone_context_15m_v1",
                "source": "Zhang & Zhou (2024)",
                "desk_role": "new Scout intake / paper-based 15m crypto zone candidate",
                "hard_verdict": "当前最诚实的新 fresh intake，是把 averaged support/resistance zone + context gate 压成因果、可复核的 15m crypto clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 single_line_break / averaged_zone_break / averaged_zone_retest / averaged_zone_context_gate 四档最小 clean replication，再用时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · averaged SR zone + context · clean-room spec</title>
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
  <h1>Scout Seat · averaged support/resistance zone + context · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把 paper-based zone candidate 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“是否值得做最小 clean replication”，不是去争 <code>Live Seat</code>。</li>
      <li>它服务的是当前 desk 更偏 long-side / zone / context 的确认层，不是重新炒作 breakout short。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7 / 8 / 9 / 10 / 11</b> 已完成 clean replication + Light Stability Pack，并都压回 <code>park / evidence pool</code>。</li>
      <li><b>shortlist 剩余 rank5 / rank6</b> 分别偏 prediction market 与跨资产 proxy，不如这条 <b>paper-based 15m crypto zone candidate</b> 贴当前 desk 口径。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_sr_zone_context_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么先做 resistance zone？</b> 因为论文里更强的是 averaged long-term resistance，而当前 desk 也默认不再强调 short breakout。</li>
      <li><b>为什么只保留两个 context 条件？</b> 因为当前 desk 要的是最小可因果、可复核版本，不是新开大而全 regime 框架。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与已有 EMA / ATR / swing helper；不要切到更长样本或更多 filter。</p>
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
    print("[ok] sr zone context scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
