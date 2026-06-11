#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_orb_protective_closing_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_orb_protective_closing_15m"
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
        "value": "EMA 当前 waiting_not_due；Rank 7~15 均已完成 clean replication + Light Stability Pack 并 park；Rank 2 已 narrow paper pilot approved 且当前没有真实 append/review need。",
        "why_it_matters": "当前 Scout Seat 的更高边际值动作，是补一条新的 paper-based 15m crypto fast intake，而不是继续磨旧候选 wiring。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication 或 paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_orb_protective_closing_15m_v1",
        "why_it_matters": "给新的 Scout intake 一个稳定句柄，方便后续 clean replication / Light Stability Pack / TODO / site 统一追踪。",
        "operator_rule": "后续所有 replication 与 verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Wu, Syu, Lin, Ho (2021) ORB with protective closing + Syu et al. (2020)",
        "why_it_matters": "最值钱的不是 GA 搜参，而是把 intraday breakout 拆成 event threshold / confirmation / protective closing 三层，适合做当前 desk 的最小 clean-room。",
        "operator_rule": "v1 不引入 GA；只迁移 clean-room 可执行规则层。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "继续复用现有 15m crypto cache，与当前 Scout fast lane 口径一致。",
        "operator_rule": "第一刀不扩币种、不追最新 bar、不切新数据源。",
    },
    {
        "section": "pipeline",
        "item": "pseudo_session_ranges",
        "value": "固定 3 个 pseudo opens：00:00 UTC、08:00 UTC、13:30 UTC；每个 session 用前 2 根或 3 根 15m K 的高低点形成 opening range。",
        "why_it_matters": "把股票 ORB 的开盘概念压成 crypto 24/7 可执行的最小 session proxy。",
        "operator_rule": "range 只能由 session 启动后的已完成 bars 生成；不得用未来波动压缩窗口回填。",
    },
    {
        "section": "pipeline",
        "item": "threshold_definition",
        "value": "breakout threshold τ ∈ {0, 0.10 ATR, 0.20 ATR}；long 触发为 close > range_high + τ。",
        "why_it_matters": "当前核心问题不是再找更花的信号，而是先回答阈值带能否减少假突破。",
        "operator_rule": "v1 只做 long-or-flat；不把 breakout-short 拉回默认主舞台。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "raw_orb | confirm1_outside | confirm2of3_outside | retest_hold | protective_close_overlay",
        "why_it_matters": "先回答阈值、确认层、保护性出场三者里，哪一层真的提供了最小增量。",
        "operator_rule": "所有变体共用同一 data window / friction；差异只来自 gate 或 exit。",
    },
    {
        "section": "variants",
        "item": "raw_orb_rule",
        "value": "close > range_high + τ 直接在 next-bar open 做多；跌回 range_mid 以下平仓。",
        "why_it_matters": "给 ORB 候选一个最朴素 baseline，方便检查确认层是否真有增量。",
        "operator_rule": "baseline 只服务比较，不得拿来直接争 Live Seat。",
    },
    {
        "section": "variants",
        "item": "confirm1_outside_rule",
        "value": "首次越过 range_high + τ 后，下一根 bar 仍收在区间外才做多。",
        "why_it_matters": "这是最轻量、最易执行的确认层。",
        "operator_rule": "若下一根收回区间内，则该次 breakout 失效，不得回填成已确认。",
    },
    {
        "section": "variants",
        "item": "confirm2of3_outside_rule",
        "value": "首次越过 range_high + τ 后，后续 3 根里至少 2 根仍收在区间外才做多。",
        "why_it_matters": "检验多等一点，是否真的能减少假突破而不是只是让交易数塌掉。",
        "operator_rule": "若 3 根窗口内跌回 range_mid 下方，则该次 breakout 作废。",
    },
    {
        "section": "variants",
        "item": "retest_hold_rule",
        "value": "首次越过 range_high + τ 后，价格在 3 根内回踩 range_high 但未失守，随后再次收在 range_high + 0.03 ATR 上方才做多。",
        "why_it_matters": "把当前 desk 更熟悉的 retest-hold 语义接到 ORB 上。",
        "operator_rule": "若回踩期间收破 range_mid，则 setup 取消。",
    },
    {
        "section": "variants",
        "item": "protective_close_overlay_rule",
        "value": "在 raw_orb / confirm1 / confirm2of3 / retest_hold 之上统一测试 protective close：1 ATR 初始止损，浮盈达到 +1R 后抬到 break-even，持仓超过 8 bars 仍未扩张则 time stop。",
        "why_it_matters": "把论文里真正有辨识度的 protective closing 明确压成当前 desk 可比较的 exit overlay。",
        "operator_rule": "第一轮先固定 protective close，不和更多动态仓位/追踪止损混合。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | +1R break-even lift | 8-bar time stop | 6/10/15/20 bps per side",
        "why_it_matters": "同时检查 ORB 候选对 frictions 的脆弱度，避免只看单一成本档。",
        "operator_rule": "first pass 默认先在 6bps 看 alpha-candidate 味道，再用 10/15/20bps 做 cost survival。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | false_break_ratio | max_drawdown | cost_survival",
        "why_it_matters": "ORB 候选很容易靠少做交易或把 exit 收太紧制造错觉，必须把收益、交易数、假突破、回撤一起看。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若确认层或 protective close 不能同时改善 false_break_ratio 与 post_cost_return，或只是靠 no_trade_ratio>80% 才看起来更稳，或 6bps 下 positive_asset_ratio<2/3，则 clean replication 后默认直接 park。",
        "why_it_matters": "提前写死失败条件，避免后续把“多等几根/多收紧出场”误写成天然 alpha。",
        "operator_rule": "clean replication 后必须诚实给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补 pseudo-session range + 5 档对照回测，再按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 hard verdict。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 Binance 15m cache 与已有 ATR helper；不要切到新大框架。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_orb_protective_closing_15m_v1",
                "source": "Wu et al. (2021) / Syu et al. (2020)",
                "desk_role": "new Scout intake / paper-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的高边际值动作，是把 ORB 的 threshold / confirmation / protective closing 三层压成 implementation-ready clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 raw_orb / confirm1_outside / confirm2of3_outside / retest_hold / protective_close_overlay 的最小 clean replication，再按时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · ORB protective closing · clean-room spec</title>
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
  <h1>Scout Seat · ORB protective closing · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把新的 paper-based 15m crypto intake 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答 ORB 的阈值 / 确认层 / protective closing 值不值得做最小 clean replication，而不是直接去争 <code>Live Seat</code>。</li>
      <li>虽然它仍属于 breakout 家族，但当前 desk 读法不是“重开 breakout 主线”，而是把它当作 <b>session-threshold + protective-exit</b> 的新 fast-lane 候选来快筛。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么它现在边际价值更高</h2>
    <ul>
      <li><b>Rank 2</b> 已进入 <code>narrow paper pilot approved</code>，当前若无真实 append/review need，再补 wiring 边际价值很低。</li>
      <li><b>Rank 7~15</b> 已完成 clean replication + Light Stability Pack，并都压回 <code>park / evidence pool</code>。</li>
      <li>相比 Rank 5/6 这类暂时不够贴当前 <code>paper/repo based 15m crypto</code> fast lane 的候选，ORB 这条线更容易直接复用现有 15m cache 给出 clean replication verdict。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_orb_protective_closing_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么不照搬论文的 GA？</b> 因为当前 desk 要的是 fast-lane 快筛，不是搜一套高自由度参数口袋。</li>
      <li><b>为什么当前仍可看它？</b> 因为这里要验证的不是“重新押 breakout 主叙事”，而是 <b>threshold + confirmation + protective closing</b> 是否能形成新的可因果候选。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与 ATR helper；不要切到新数据源或更大框架。</p>
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
    print("[ok] orb protective-closing scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
