#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "spec_meta.csv"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


SPEC_ROWS = [
    {
        "section": "run_context",
        "item": "rank1_recheck_blocker",
        "value": "tau-band rank1 仅新增 2 根 15m bar（03:45 -> 04:23 UTC）",
        "why_it_matters": "不足以做 honest forward continuation；继续硬跑只会把同一样本近义重读。",
        "operator_rule": "本轮自动切到 Rank 2，先冻结 clean-room spec，而不是伪造新的 recheck verdict。",
    },
    {
        "section": "candidate",
        "item": "candidate_id",
        "value": "scout_volume_supportflip_higherlow_15m_v1",
        "why_it_matters": "给 Scout Seat Rank 2 一个稳定、可复用的实现句柄。",
        "operator_rule": "后续实验、日志、网页统一用这个 candidate_id，避免与其它 breakout guard 混名。",
    },
    {
        "section": "candidate",
        "item": "source_anchor",
        "value": "Yumna et al. (2024) / volume confirmation + resistance-becomes-support + higher low",
        "why_it_matters": "明确这是一条 confirmation/filter 候选，不是直接照搬成独立 alpha。",
        "operator_rule": "只迁移可客观规则化的确认链：volume -> support-flip -> higher-low。",
    },
    {
        "section": "scope",
        "item": "market_timeframe",
        "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m",
        "why_it_matters": "保持和 Rank 1 τ-band 实验同级别可比，不另开重型数据路径。",
        "operator_rule": "优先复用现有 Binance 15m cache；不要在第一刀切到更重的数据下载。",
    },
    {
        "section": "scope",
        "item": "direction_layer",
        "value": "EMA20 > EMA50 只做多；EMA20 < EMA50 只做空",
        "why_it_matters": "把结构确认和方向背景拆开，避免 support/resistance 事件与趋势方向混在一起。",
        "operator_rule": "与 Rank 1 保持同一方向层，方便 apples-to-apples 对照。",
    },
    {
        "section": "baseline",
        "item": "breakout_edge",
        "value": "Donchian(20) 上下沿 + tau = 0.05 ATR",
        "why_it_matters": "先冻结最小边界定义，避免 spec 阶段就在 pivot vs zone 上漂移。",
        "operator_rule": "v1 默认先用 Donchian(20)；若后续再试 pivot 版，应作为独立变体，不回写 v1。",
    },
    {
        "section": "gate",
        "item": "volume_confirmation",
        "value": "breakout 当根 volume > rolling20 volume median × 1.2",
        "why_it_matters": "先回答“放量确认”是否单独就能压低假突破。",
        "operator_rule": "volume_only 版本在 breakout 完成后下一根开盘入场；不等待额外结构确认。",
    },
    {
        "section": "gate",
        "item": "support_flip_confirmation",
        "value": "breakout 后 1~3 根内允许回踩旧边界；若最低/最高触碰边界缓冲带（±0.05 ATR）且收盘未重新回区间内，则记为 support-flip / resistance-flip 成立",
        "why_it_matters": "把“旧阻力变新支撑 / 旧支撑变新阻力”写成可检查的 operator 条件。",
        "operator_rule": "flip_only 版本在满足该条件后的下一根开盘入场；若 3 根内未出现 flip，则该次 breakout 作废。",
    },
    {
        "section": "gate",
        "item": "higher_low_confirmation",
        "value": "breakout 后最多 6 根内，出现一个 2-left/2-right 确认 swing low（做空时为 swing high），且该 swing 仍位于旧边界外；随后价格再穿过 breakout 后的 interim high/low 才确认入场",
        "why_it_matters": "把 higher-low / lower-high 写成因果可实现的结构确认，而不是事后肉眼描述。",
        "operator_rule": "higher_low_only 版本必须等 swing 被右侧 2 根确认后，才允许在后续再突破 interim extreme 时入场。",
    },
    {
        "section": "variants",
        "item": "first_experiment_matrix",
        "value": "raw_breakout | volume_only | support_flip_only | higher_low_only | combo_all",
        "why_it_matters": "一次把最小对照矩阵冻住，避免下一轮实现时临时改题。",
        "operator_rule": "所有版本共用同一 data window / exit / cost；差异只来自确认 gate。",
    },
    {
        "section": "execution",
        "item": "entry_exit_cost",
        "value": "next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side",
        "why_it_matters": "与 Rank 1 τ-band 保持同一执行口径，便于比较 guard 是否真改善而不是换了出场规则。",
        "operator_rule": "第一刀不要同时改止盈止损；先看 confirmation 本身的增量。",
    },
    {
        "section": "evaluation",
        "item": "scoreboard",
        "value": "post_cost_return | false_break_ratio | retest_hold_rate | time_to_failure | max_drawdown | positive_asset_ratio",
        "why_it_matters": "防止只盯收益、不看是否真减少假突破与早死。",
        "operator_rule": "网页与 artifact 默认同时展示 aggregate + per-asset；不只给单个 headline。",
    },
    {
        "section": "falsification",
        "item": "bench_rules",
        "value": "若 combo_all 相对 raw 与 volume_only 同时不能改善 post_cost_return 与 false_break_ratio，或 trade count 压缩 >70% 仍无改善，则直接 bench 组合版；若只有 volume_only 有增量，则保留为更窄 execution guard",
        "why_it_matters": "提前写好失败条件，避免实现后又无限找解释。",
        "operator_rule": "下一轮 first slice 跑完后，必须给 keep / narrow / bench 之一，不留空白。",
    },
    {
        "section": "next_action",
        "item": "implementation_ready_call",
        "value": "spec 已足够进入本地 first slice；下一步应该写实验脚本并复用 Rank 1 cache，而不是继续补 wording",
        "why_it_matters": "确保 Run 2 的 fallback 产物真能缩短下一轮 time-to-first-verdict。",
        "operator_rule": "优先实现 volume_only 与 combo_all；若时间不够，先保证 raw + volume_only + combo_all 三档齐。",
    },
]


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    spec_df = pd.DataFrame(SPEC_ROWS)
    now = datetime.now(timezone.utc)
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_volume_supportflip_higherlow_15m_v1",
                "source": "Yumna et al. (2024)",
                "rank": "Run 2 fallback / Scout Rank 2",
                "hard_verdict": "Rank 1 τ-band recheck 仅新增 2 根 15m bar，不足以做 honest continuation；因此本轮切到 Rank 2，并把 volume + support-flip + higher-low 冻结成可直接实现的 clean-room spec。",
                "next_step": "实现 raw + volume_only + combo_all 的本地 first slice，并沿用 Rank 1 的 Binance 120d 15m cache / exit / cost 口径。",
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
  <title>Scout Rank 2 · volume + support-flip + higher-low · clean-room spec</title>
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
  <h1>Scout Seat · Rank 2：volume + support-flip + higher-low · clean-room spec</h1>
  <p class=\"muted\">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页不是结果宣判页，而是把 Scout Rank 2 压成可直接实现的本地最小实验 spec。</p>

  <div class=\"card\">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>这一步的价值不是再写一张概念说明页，而是把下一轮实验该怎么写、怎么比、怎么判输赢冻结下来。</li>
      <li>因此当前更诚实的 desk call 是：<b>Rank 2 已 implementation-ready，但还没有 performance verdict</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>本轮冻结的 clean-room spec（v1）</h2>
    {render_table(spec_df)}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/clean_room_spec_v1.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>它是下一轮实验的输入，不是输出。</b> 目的是缩短 `time-to-first-verdict`，避免下一轮又从文献摘要重讲一遍。</li>
      <li><b>为什么先冻结 Donchian(20) + EMA20/50 + 6bps/side？</b> 因为 Rank 1 已经在这套口径上跑过，Rank 2 若沿用同框架，就能更快回答“confirmation 链本身有没有增量”。</li>
      <li><b>为什么要先写 bench 规则？</b> 因为这条线最容易掉进“交易更少、看起来更稳、但其实没赚更多”的假改善；先把失败条件写死，后续更容易 honest close-out。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>下一步最自然动作</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class=\"muted\">优先复用 Rank 1 的 Binance 15m cache / exit / cost；不要再开一条重型下载与新出场规则支线。</p>
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
    print("[ok] scout volume/support-flip/higher-low spec generated")
    print("[artifact]", SPEC_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
