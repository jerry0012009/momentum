#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_ema_plateau_consensus_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_ema_plateau_consensus_15m"
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
        "value": "EMA 当前 waiting_not_due；Rank 17 已进入 paper candidate pool 且若没有 genuinely new honest evidence 就不该继续补近义 wiring；Rank 7~16 均已 park。",
        "why_it_matters": "当前 Scout Seat 的最高边际价值是补一条新的 paper-based 15m crypto intake，而不是继续在已 park 候选或 Rank 17 wiring 上打转。",
        "operator_rule": "本轮只做 source intake + clean-room spec；不把 spec 冒充成 clean replication / paper candidate。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_ema_plateau_consensus_15m_v1",
        "why_it_matters": "给新的 Scout intake 一个稳定句柄，方便后续 clean replication / Light Stability Pack / TODO / site 统一追踪。",
        "operator_rule": "后续所有 clean replication 与 verdict 都沿用这个 candidate_id。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Chiu et al. (2023) / Enhancing Crypto Success via Heatmap Visualization of Big Data Analytics for Numerous Variable Moving Average Strategies",
        "why_it_matters": "论文最值钱的启发不是再找单一最优 EMA 参数，而是先判断相邻参数是否形成稳定平台。",
        "operator_rule": "v1 只迁移 plateau / neighborhood stability 思路，不照搬论文里的整套大规模 heatmap 工程。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持与 Rank 17 及前面 Scout 快筛同级样本，继续复用现有 15m crypto cache。",
        "operator_rule": "第一刀不扩币种、不切新数据源、不追最新 bar。",
    },
    {
        "section": "rule_design",
        "item": "grid_definition",
        "value": "邻域固定为 fast ∈ {8, 10, 12}，slow ∈ {34, 40, 50}，只保留 fast < slow 的 9 个 EMA pair。",
        "why_it_matters": "先用一个很小、但真的有邻域概念的局部网格回答‘是不是只有孤立 hot pixel’。",
        "operator_rule": "v1 禁止把网格无限扩成大参数搜索；先看局部邻域是否有一致方向。",
    },
    {
        "section": "rule_design",
        "item": "vote_definition",
        "value": "每个 EMA pair 生成 direction vote：EMA_fast > EMA_slow 记 long_vote=1；EMA_fast < EMA_slow 记 flat_vote=1（v1 不做做空）。",
        "why_it_matters": "把 heatmap 稳定平台翻成当前 desk 可执行的 trade on / trade off 规则，而不是停在研究方法层。",
        "operator_rule": "v1 只允许 long-or-flat；不把 short 侧硬写成镜像。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "anchor_10_40 | row_consensus_2of3 | plateau_vote_5of9 | plateau_vote_5of9_spread_guard",
        "why_it_matters": "先比较‘单点参数’、‘小邻域一致性’、‘全邻域平台一致性’三档最小变体，看 plateau 口径是否真的有增量。",
        "operator_rule": "四档共用同一 data window / cost / exit；差异只来自 consensus 规则。",
    },
    {
        "section": "variants",
        "item": "anchor_10_40_rule",
        "value": "trade on = EMA10 > EMA40；trade off = EMA10 <= EMA40。",
        "why_it_matters": "给 plateau 候选一个最朴素的单点基线，防止后续把任何改善都误归因于共识框架。",
        "operator_rule": "这是单点对照组，不得加入额外过滤层。",
    },
    {
        "section": "variants",
        "item": "row_consensus_2of3_rule",
        "value": "固定 slow=40，若 EMA8/40、EMA10/40、EMA12/40 中至少 2 个为 long，则 trade on；否则 flat。",
        "why_it_matters": "先看最小 fast-side 邻域一致性，是否比单点参数更稳。",
        "operator_rule": "若 3 条里只有 1 条 long，不得勉强持仓。",
    },
    {
        "section": "variants",
        "item": "plateau_vote_5of9_rule",
        "value": "9 个 EMA pair 中 long_votes >= 5 则 trade on；否则 flat。",
        "why_it_matters": "把‘邻近参数形成平台’压成最简单、最可审计的多数票规则。",
        "operator_rule": "若 long_votes 只在 4/9 或以下，则视为方向不够稳定，直接 no-trade。",
    },
    {
        "section": "variants",
        "item": "plateau_vote_5of9_spread_guard_rule",
        "value": "在 plateau_vote_5of9 基础上，再要求 9 个 pair 的 median normalized spread = median((EMA_fast-EMA_slow)/close) >= 0.20%。",
        "why_it_matters": "防止多数票只是均线几乎粘在一起时的弱一致，减少 near-zero whipsaw。",
        "operator_rule": "若票数够但 median spread 不够，则仍视为 flat。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "保持与当前 Scout 快筛相同执行口径，避免把差异误读成出场规则变化。",
        "operator_rule": "第一刀不引入 trailing stop、动态仓位或更多保护层。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | positive_asset_ratio | trades_per_asset | no_trade_ratio | cost_survival | positive_cell_ratio_proxy",
        "why_it_matters": "plateau 候选最容易靠‘少做交易’看起来更稳，因此必须把交易数、成本后存活率和邻域一致性一起看。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 plateau 版本相对 anchor_10_40 不能同时改善 post_cost_return 与 positive_asset_ratio，或只是靠 no_trade_ratio > 80% 才勉强转正，则直接 park；若 clean replication 发现多数票只是稀疏持仓幻觉，也直接 park。",
        "why_it_matters": "提前写死失败条件，避免后续把‘参数更多 / 交易更少’误写成 alpha。",
        "operator_rule": "clean replication 后必须给出 park / paper candidate / narrow paper pilot 三选一。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入 clean replication；下一步应优先补 EMA neighborhood vote signal layer + 4 档最小回测，再按时间 / 参数 / 跨标的 / 成本-交易数四项 Light Stability Pack 给出 park 或继续。",
        "why_it_matters": "确保这轮产物能直接缩短下一轮 time-to-clean-replication。",
        "operator_rule": "优先复用现有 EMA helper、ATR helper 与 Binance 15m cache；不要切到更长样本或更大网格。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_ema_plateau_consensus_15m_v1",
                "source": "Chiu et al. (2023)",
                "desk_role": "new Scout intake / paper-based 15m crypto candidate",
                "hard_verdict": "当前最诚实的新 fresh intake，是把‘EMA 邻域是否形成稳定平台’压成一个可执行的 15m crypto neighborhood-consensus candidate；它已通过 source intake / clean-room spec，但还没有通过 clean replication，因此不能误写成 paper candidate。",
                "next_step": "优先补 anchor_10_40 / row_consensus_2of3 / plateau_vote_5of9 / plateau_vote_5of9_spread_guard 的最小 clean replication，再用时间/参数/跨标的/成本-交易数四项 Light Stability Pack 给出 park 或继续。",
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
  <title>Scout Seat · EMA plateau consensus · clean-room spec</title>
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
  <h1>Scout Seat · EMA plateau consensus · 15m crypto clean-room spec</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是成绩宣判页，而是把 paper-based EMA plateau idea 压成可直接进入 clean replication 的最小 spec。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这条线当前的价值，是回答“EMA 邻域平台感是否值得做最小 clean replication”，不是去抢当前 <code>Paper Seat</code>。</li>
      <li>它也不是继续赌单一神奇参数；v1 只允许小邻域一致性，不允许无限扩网格。</li>
    </ul>
  </div>

  <div class="card">
    <h2>为什么这条 intake 现在有边际价值</h2>
    <ul>
      <li><b>Rank 17</b> 已进入 <code>paper candidate pool</code>；若没有 genuinely new honest evidence，就不该继续补近义 wiring。</li>
      <li><b>Rank 7~16</b> 已完成 clean replication + Light Stability Pack 并压回 <code>park / evidence pool</code>。</li>
      <li>这条线是新的 <b>paper-based 15m crypto intake</b>：能复用现有 EMA / ATR helper 与 15m cache，但回答的是另一个更诚实的问题——结果到底是单点幸运，还是邻域稳定。</li>
    </ul>
  </div>

  <div class="card">
    <h2>冻结下来的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class="muted">artifact：<code>reports/artifacts/scout_ema_plateau_consensus_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是 clean replication 的输入，不是输出。</b> 目的是缩短下一轮 <code>time-to-clean-replication</code>。</li>
      <li><b>为什么不用大 heatmap？</b> 因为当前 Scout Seat 要的是快筛；先看小邻域是否有一致方向，再决定值不值得扩网格。</li>
      <li><b>为什么只做 long-or-flat？</b> 因为当前桌面默认不再把 short 侧当作镜像主线，先验证 long 侧 EMA 邻域一致性是否真的更诚实。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">优先复用现有 Binance 15m cache 与已有 EMA / ATR helper；不要切到更大参数网格或更复杂出场规则。</p>
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
    print("[ok] ema plateau consensus scout spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
