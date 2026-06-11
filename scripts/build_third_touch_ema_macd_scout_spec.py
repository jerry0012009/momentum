#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_third_touch_ema_macd_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_third_touch_ema_macd_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "spec_meta.csv"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


SPEC_ROWS = [
    {
        "section": "run_context",
        "item": "desk_fallback_reason",
        "value": "Paper Seat waiting_not_due；breakout 已 bench；Scout Rank 1 仍停在 03:53 UTC，Rank 2 已有 first verdict + friction recheck",
        "why_it_matters": "当前最诚实的 Run 3 动作不是重复无新证据的 recheck，而是把 Rank 3 压成 implementation-ready spec。",
        "operator_rule": "本轮默认切到 Rank 3 clean-room spec；不伪造 Rank 1 新 bar，也不重复 Rank 2 同样本切片。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_third_touch_ema_macd_15m_v1",
        "why_it_matters": "给 Scout Seat Rank 3 一个稳定、可复用的实现句柄。",
        "operator_rule": "后续实验、日志、网页统一用这个 candidate_id，避免与其它 breakout/confirmation guard 混名。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Wiśniewski (2024) / third-touch confirmation + EMA/MACD confluence",
        "why_it_matters": "明确这条线是 confirmation/filter reference，不是把周频案例论文直接搬成 alpha。",
        "operator_rule": "只迁移可客观规则化的结构确认链：third-touch -> breakout persistence -> EMA/MACD 共识。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持和 Rank 1 / Rank 2 同级别可比，不新开重型下载路径。",
        "operator_rule": "优先复用现有 Binance 15m cache；第一刀不要切到更多币种或更长窗口。",
    },
    {
        "section": "scope",
        "item": "direction_layer",
        "value": "EMA20 > EMA50 只做多 breakout；EMA20 < EMA50 只做空 breakout",
        "why_it_matters": "把结构确认和大方向背景拆开，避免第三次触碰本身被误读成独立方向信号。",
        "operator_rule": "与 Rank 1 / Rank 2 保持同一 EMA20/50 方向层，方便 apples-to-apples 对照。",
    },
    {
        "section": "structure",
        "item": "candidate_boundary",
        "value": "用 2-left/2-right swing highs/lows 构造水平/轻斜率边界；同侧连续两次触碰后形成 candidate boundary，触碰缓冲带=±0.05 ATR",
        "why_it_matters": "把论文里的手工趋势线翻成因果可实现的 swing-boundary 近似版，先避免主观画线。",
        "operator_rule": "v1 先限制为 swing-boundary；若未来要上 full diagonal trendline，必须另立变体，不回写 v1。",
    },
    {
        "section": "gate",
        "item": "third_touch_confirmation",
        "value": "candidate boundary 成立后，后续 4~24 根内再次触碰同一缓冲带，且反向反应幅度 >= 0.2 ATR，才记为 confirmed third-touch",
        "why_it_matters": "核心要回答的是：第三次结构确认，是否比 first-cross 更能压低假突破。",
        "operator_rule": "third_touch_only 版本只有在 confirmed third-touch 之后，才允许寻找 breakout；若 24 根内没等到第三触碰，则该边界作废。",
    },
    {
        "section": "gate",
        "item": "breakout_persistence",
        "value": "confirmed third-touch 后的 1~12 根内，收盘越过边界 ±0.05 ATR；并要求 2-of-3 closes 保持在线外，才算 persistence 成立",
        "why_it_matters": "避免 wick/瞬时穿越把第三触碰逻辑重新变回噪声追单。",
        "operator_rule": "若 first-cross 发生但 2-of-3 persistence 未成立，则该次 breakout 记为 failed break，不入场。",
    },
    {
        "section": "gate",
        "item": "ema_confluence",
        "value": "breakout 触发时，EMA20 与 EMA50 顺向排列，且 EMA20 slope 连续 3 根同向",
        "why_it_matters": "EMA 在这条线里只负责方向共识，不负责定义边界本身。",
        "operator_rule": "third_touch_plus_ema 版本必须同时满足 third-touch + persistence + EMA slope；缺一项即不入场。",
    },
    {
        "section": "gate",
        "item": "macd_confluence",
        "value": "做多时 MACD line > signal 且 histogram >= 0；做空时 MACD line < signal 且 histogram <= 0",
        "why_it_matters": "把论文里“EMA/MACD 共识”再压一层，检验是否真能继续收窄假突破。",
        "operator_rule": "third_touch_plus_ema_macd 版本必须在 breakout 确认同一根 bar 上满足 MACD 共识，不允许事后补确认。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "raw_breakout | third_touch_only | third_touch_plus_ema | third_touch_plus_ema_macd",
        "why_it_matters": "一次把最小对照矩阵冻住，避免实现阶段又临时改题。",
        "operator_rule": "所有版本共用同一 data window / exit / cost；差异只来自结构确认与共识过滤。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与 Rank 1 / Rank 2 保持同一执行口径，便于比较结构确认链的真实增量。",
        "operator_rule": "第一刀不要同时改 SL/TP；先看 third-touch + confluence 本身是否有用。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | false_break_ratio | persistence_pass_rate | time_to_failure | max_drawdown | positive_asset_ratio | trades_per_asset",
        "why_it_matters": "防止只盯 headline return，不看第三触碰是否只是把交易压到太少。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset；必须同时看 trade compression。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 third_touch_plus_ema_macd 相对 raw_breakout 不能同时改善 post_cost_return 与 false_break_ratio，或 trade count 压缩 >75% 且 positive_asset_ratio 仍不升，则直接 bench；若只有 third_touch_only 有增量，则保留为更窄 structure gate",
        "why_it_matters": "提前写死失败条件，避免这条线后续以“更严格所以看起来更稳”无限续命。",
        "operator_rule": "下一轮 first slice 跑完后，必须给 keep / narrow / bench 之一，不留 spec-only 漂浮状态。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入本地 first slice；下一步应优先实现 raw_breakout + third_touch_only + third_touch_plus_ema_macd 三档，而不是继续补解释页",
        "why_it_matters": "确保 Run 3 fallback 产物真能缩短下一轮 time-to-first-verdict。",
        "operator_rule": "优先复用现有 15m cache 和 Rank 1 / Rank 2 同口径执行框架；不要再开新样本或新出场支线。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_third_touch_ema_macd_15m_v1",
                "source": "Wiśniewski (2024)",
                "rank": "Run 3 fallback / Scout Rank 3",
                "hard_verdict": "当前最诚实的 Run 3 推进，不是继续对无新 bar 的 Rank 1 近义重读，也不是重复 Rank 2 friction，而是把 Rank 3 的 third-touch + EMA/MACD confluence 冻结成 implementation-ready clean-room spec。",
                "next_step": "实现 raw_breakout + third_touch_only + third_touch_plus_ema_macd 的本地 first slice，并沿用既有 Binance 120d 15m cache / exit / cost 口径。",
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
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout Rank 3 · third-touch + EMA/MACD confluence · clean-room spec</title>
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
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Scout Seat · Rank 3：third-touch + EMA/MACD confluence · clean-room spec</h1>
  <p class=\"muted\">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是结果宣判页，而是把 Scout Rank 3 压成可直接实现的本地最小实验 spec。</p>

  <div class=\"card\">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这一步的价值不是继续复述周频案例研究，而是把下一轮实验该怎么实现、怎么比较、怎么判输赢冻结下来。</li>
      <li>因此当前更诚实的 desk call 是：<b>Rank 3 已 implementation-ready，但还没有 performance verdict</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>本轮冻结的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是下一轮实验的输入，不是输出。</b> 目的是缩短 <code>time-to-first-verdict</code>，避免下一轮又从论文摘要重讲一遍。</li>
      <li><b>为什么 v1 先用 swing-boundary 而不直接做主观趋势线？</b> 因为当前要的是最小因果实现；先把 third-touch 规则冻结，再考虑更复杂的斜线版本。</li>
      <li><b>为什么要同时看 trade compression？</b> 因为 third-touch + EMA/MACD 很容易“看起来更干净”，但代价是几乎不交易；所以必须把 trades_per_asset 一起放上 scoreboard。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class=\"muted\">优先复用既有 Binance 15m cache / exit / cost；不要再开一条重型下载与新出场规则支线。</p>
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    spec_df, meta_df = build_tables()
    spec_df.to_csv(SPEC_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    write_report(spec_df, meta_df)
    print("[ok] scout third-touch EMA/MACD spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
