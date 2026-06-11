#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_hot_fee_vip0_compare_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_hot_fee_vip0_compare_15m"
REPORT_PATH = SITE_DIR / "report.html"
SUMMARY_JSON_PATH = ART_DIR / "study_summary.json"
SMALL_COMPARE_PATH = ART_DIR / "smallcap_compare.csv"
UNIVERSE_COMPARE_PATH = ART_DIR / "hot_universe_compare.csv"
STRICT_SMALL_VARIANT_PATH = ART_DIR / "strict_smallcap_variant_summary.csv"
STRICT_SMALL_ASSET_PATH = ART_DIR / "strict_smallcap_asset_summary.csv"
STRICT_SMALL_TIME_PATH = ART_DIR / "strict_smallcap_time_summary.csv"
STRICT_SMALL_DETAIL_PATH = ART_DIR / "strict_smallcap_detail.json"
STRICT_UNIV_VARIANT_PATH = ART_DIR / "strict_universe_variant_summary.csv"
STRICT_UNIV_ASSET_PATH = ART_DIR / "strict_universe_asset_summary.csv"
STRICT_UNIV_PHASE_PATH = ART_DIR / "strict_universe_phase_summary.csv"
STRICT_UNIV_TIME_PATH = ART_DIR / "strict_universe_time_summary.csv"
STRICT_UNIV_DETAIL_PATH = ART_DIR / "strict_universe_detail.json"

PREV_SMALL_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_hot_smallcap_regime_15m"
PREV_UNIV_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_hot_universe_volume_phase_15m"
PREV_SMALL_REPORT = ROOT / "reports" / "site" / "factors" / "scout_rank32b_hot_smallcap_regime_15m" / "report.html"
PREV_UNIV_REPORT = ROOT / "reports" / "site" / "factors" / "scout_rank32b_hot_universe_volume_phase_15m" / "report.html"

SMALL_SCRIPT = ROOT / "scripts" / "build_rank32b_hot_smallcap_regime_study.py"
UNIV_SCRIPT = ROOT / "scripts" / "build_rank32b_hot_universe_volume_phase_study.py"

VIP0_SIDE_FEE_BPS = 5.0


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def apply_fee_override(study_mod, taker_fee_bps: float, maker_fee_bps: float) -> None:
    study_mod.live_mod.exec_mod.TAKER_FEE_BPS = taker_fee_bps
    study_mod.live_mod.exec_mod.MAKER_FEE_BPS = maker_fee_bps


def run_strict_smallcap() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    mod = load_module(SMALL_SCRIPT, "rank32b_hot_smallcap_vip0_compare")
    apply_fee_override(mod, VIP0_SIDE_FEE_BPS, VIP0_SIDE_FEE_BPS)
    asset_map = mod.live_mod.build_asset_map(",".join(entry.symbol for entry in mod.POOL))
    variant_summary, asset_variant, time_summary, detail = mod.study(asset_map)
    detail["fee_assumption"] = {
        "entry_fee_bps": VIP0_SIDE_FEE_BPS,
        "exit_fee_bps": VIP0_SIDE_FEE_BPS,
        "note": "统一按 Binance VIP0 双边万5/万5 计算，不再区分 TP maker 0bps / SL timeout taker 6bps。",
    }
    return variant_summary, asset_variant, time_summary, detail


def run_strict_universe() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    mod = load_module(UNIV_SCRIPT, "rank32b_hot_universe_vip0_compare")
    apply_fee_override(mod, VIP0_SIDE_FEE_BPS, VIP0_SIDE_FEE_BPS)
    variant_summary, asset_variant, time_summary, phase_summary, detail = mod.study(mod.POOL)
    detail["fee_assumption"] = {
        "entry_fee_bps": VIP0_SIDE_FEE_BPS,
        "exit_fee_bps": VIP0_SIDE_FEE_BPS,
        "note": "统一按 Binance VIP0 双边万5/万5 计算，不再区分 TP maker 0bps / SL timeout taker 6bps。",
    }
    return variant_summary, asset_variant, time_summary, phase_summary, detail


def load_previous_frames() -> dict[str, pd.DataFrame]:
    return {
        "small_variant": pd.read_csv(PREV_SMALL_DIR / "variant_summary.csv"),
        "small_asset": pd.read_csv(PREV_SMALL_DIR / "variant_asset_summary.csv"),
        "small_time": pd.read_csv(PREV_SMALL_DIR / "variant_time_summary.csv"),
        "univ_variant": pd.read_csv(PREV_UNIV_DIR / "variant_summary.csv"),
        "univ_asset": pd.read_csv(PREV_UNIV_DIR / "variant_asset_summary.csv"),
        "univ_phase": pd.read_csv(PREV_UNIV_DIR / "selected_trade_phase_summary.csv"),
        "univ_time": pd.read_csv(PREV_UNIV_DIR / "variant_time_summary.csv"),
    }


def compare_frames(prev_df: pd.DataFrame, strict_df: pd.DataFrame, key: str) -> pd.DataFrame:
    metric_cols = [c for c in [
        "selected_trades",
        "portfolio_total_return",
        "win_rate",
        "avg_net_ret",
        "avg_hold_minutes",
        "positive_asset_ratio",
        "candidate_signal_times",
        "overlap_timestamp_ratio",
        "target_hit_rate",
        "stop_hit_rate",
        "timeout_rate",
    ] if c in prev_df.columns and c in strict_df.columns]
    merged = prev_df[[key, *metric_cols]].merge(
        strict_df[[key, *metric_cols]],
        on=key,
        suffixes=("_prev", "_vip0"),
    )
    for col in metric_cols:
        merged[f"{col}_delta"] = merged[f"{col}_vip0"] - merged[f"{col}_prev"]
    return merged


def render_compare_table(compare_df: pd.DataFrame, key: str) -> str:
    display = compare_df.copy()
    cols = [key]
    for base in ["portfolio_total_return", "win_rate", "avg_net_ret", "positive_asset_ratio"]:
        if f"{base}_prev" in display.columns:
            cols.extend([f"{base}_prev", f"{base}_vip0", f"{base}_delta"])
    if "selected_trades_prev" in display.columns:
        cols[1:1] = ["selected_trades_prev", "selected_trades_vip0", "selected_trades_delta"]
    display = display[cols]
    percent_cols = {c for c in display.columns if c.endswith(("_prev", "_vip0", "_delta")) and any(x in c for x in ["return", "rate", "avg_net_ret"])}
    digits_cols = {c: 0 for c in display.columns if "selected_trades" in c}
    return render_table(display, percent_cols=percent_cols, digits_cols=digits_cols)


def build_summary_payload(prev: dict[str, pd.DataFrame], strict_small: tuple, strict_univ: tuple) -> dict[str, object]:
    strict_small_variant, strict_small_asset, strict_small_time, strict_small_detail = strict_small
    strict_univ_variant, strict_univ_asset, strict_univ_time, strict_univ_phase, strict_univ_detail = strict_univ

    small_compare = compare_frames(prev["small_variant"], strict_small_variant, "variant")
    univ_compare = compare_frames(prev["univ_variant"], strict_univ_variant, "variant")

    small_baseline_prev = prev["small_variant"].loc[prev["small_variant"]["variant"] == "baseline"].iloc[0].to_dict()
    small_baseline_vip0 = strict_small_variant.loc[strict_small_variant["variant"] == "baseline"].iloc[0].to_dict()
    univ_baseline_prev = prev["univ_variant"].loc[prev["univ_variant"]["variant"] == "baseline_all"].iloc[0].to_dict()
    univ_baseline_vip0 = strict_univ_variant.loc[strict_univ_variant["variant"] == "baseline_all"].iloc[0].to_dict()
    univ_hot_prev = prev["univ_variant"].loc[prev["univ_variant"]["variant"] == "hot_phase_only"].iloc[0].to_dict()
    univ_hot_vip0 = strict_univ_variant.loc[strict_univ_variant["variant"] == "hot_phase_only"].iloc[0].to_dict()
    univ_cold_prev = prev["univ_variant"].loc[prev["univ_variant"]["variant"] == "cold_phase_only"].iloc[0].to_dict()
    univ_cold_vip0 = strict_univ_variant.loc[strict_univ_variant["variant"] == "cold_phase_only"].iloc[0].to_dict()

    strict_univ_phase_baseline = strict_univ_phase.loc[strict_univ_phase["variant"] == "baseline_all"].copy()
    strict_small_top = strict_small_asset.loc[strict_small_asset["variant"] == "baseline"].sort_values("total_return", ascending=False).head(10)
    strict_univ_top = strict_univ_asset.loc[strict_univ_asset["variant"] == "baseline_all"].sort_values("total_return", ascending=False).head(12)

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fee_assumption": {
            "previous": "旧研究：entry taker 6bps；TP exit maker 0bps；SL/timeout exit taker 6bps。",
            "vip0": "新研究：买卖双边统一 5bps / 5bps（Binance VIP0 万5/万5）。",
        },
        "small_compare": small_compare,
        "univ_compare": univ_compare,
        "small_baseline_prev": small_baseline_prev,
        "small_baseline_vip0": small_baseline_vip0,
        "univ_baseline_prev": univ_baseline_prev,
        "univ_baseline_vip0": univ_baseline_vip0,
        "univ_hot_prev": univ_hot_prev,
        "univ_hot_vip0": univ_hot_vip0,
        "univ_cold_prev": univ_cold_prev,
        "univ_cold_vip0": univ_cold_vip0,
        "strict_univ_phase_baseline": strict_univ_phase_baseline,
        "strict_small_top": strict_small_top,
        "strict_univ_top": strict_univ_top,
    }


def build_html(payload: dict[str, object]) -> str:
    small_compare: pd.DataFrame = payload["small_compare"]
    univ_compare: pd.DataFrame = payload["univ_compare"]
    strict_univ_phase_baseline: pd.DataFrame = payload["strict_univ_phase_baseline"]
    strict_small_top: pd.DataFrame = payload["strict_small_top"]
    strict_univ_top: pd.DataFrame = payload["strict_univ_top"]
    small_prev = payload["small_baseline_prev"]
    small_vip0 = payload["small_baseline_vip0"]
    univ_prev = payload["univ_baseline_prev"]
    univ_vip0 = payload["univ_baseline_vip0"]
    hot_prev = payload["univ_hot_prev"]
    hot_vip0 = payload["univ_hot_vip0"]
    cold_prev = payload["univ_cold_prev"]
    cold_vip0 = payload["univ_cold_vip0"]

    small_ret_delta = float(small_vip0["portfolio_total_return"] - small_prev["portfolio_total_return"])
    univ_ret_delta = float(univ_vip0["portfolio_total_return"] - univ_prev["portfolio_total_return"])
    hot_ret_delta = float(hot_vip0["portfolio_total_return"] - hot_prev["portfolio_total_return"])
    cold_ret_delta = float(cold_vip0["portfolio_total_return"] - cold_prev["portfolio_total_return"])

    intro = f"""
    <ul>
      <li><b>这次不是简单重跑，而是统一费用口径：</b>旧研究按 <code>entry taker 6bps / TP maker 0bps / SL-timeout taker 6bps</code>；新研究按 <code>buy 5bps + sell 5bps</code> 的 Binance VIP0 双边费用统一计算。</li>
      <li><b>这个新口径并非对所有交易都单向更苛刻：</b>对 <b>TP 出场</b> 的单子，旧口径总费约 6bps，新口径变成 10bps；对 <b>SL / timeout</b> 的单子，旧口径总费约 12bps，新口径变成 10bps。</li>
      <li><b>因此你现在看到的结果更适合作为“统一保守费率口径”</b>：同一套研究里，所有买卖都按万5/万5 算，便于横向比较。</li>
    </ul>
    """

    takeaways = f"""
    <ul>
      <li><b>10 币小池结论没有被推翻：</b>baseline 从 <b>{pct(small_prev['portfolio_total_return'])}</b> 变到 <b>{pct(small_vip0['portfolio_total_return'])}</b>，变化 <b>{pct(small_ret_delta)}</b>；胜率和交易数不变，主要变化只来自手续费重算。</li>
      <li><b>23 币扩大池结论也还站得住：</b>baseline 从 <b>{pct(univ_prev['portfolio_total_return'])}</b> 变到 <b>{pct(univ_vip0['portfolio_total_return'])}</b>，变化 <b>{pct(univ_ret_delta)}</b>；即便用统一双边 5bps 口径，热门币池仍然是明显为正。</li>
      <li><b>“热期更强、冷期变薄”的主结论没有变：</b>hot phase 从 <b>{pct(hot_prev['portfolio_total_return'])}</b> 变到 <b>{pct(hot_vip0['portfolio_total_return'])}</b>；cold phase 从 <b>{pct(cold_prev['portfolio_total_return'])}</b> 变到 <b>{pct(cold_vip0['portfolio_total_return'])}</b>。冷期仍然有 edge，但更薄。</li>
      <li><b>所以新的研究结论不是“原结论失效”，而是：</b>在更统一的 VIP0 双边费率下，32b 在热门小币上的优势仍然存在，只是收益数值更接近实盘保守估计。</li>
    </ul>
    """

    interpretation = """
    <ol>
      <li><b>这轮重算主要影响的是收益幅度，不太影响排序和结构判断。</b> 因为交易筛选逻辑、TP/SL/timeout、以及 strongest-only 约束都没变，变的是每笔交易净值的扣费方式。</li>
      <li><b>热门币依然不是“只在一瞬间有效”。</b> 更统一的费用后，热期依然最强，冷期依然更薄，但并没有一退潮就完全归零。</li>
      <li><b>如果你未来要把这些币纳入真正的动态观察池，VIP0 双边费率版更值得拿来做阈值和优先级判断。</b> 因为它避免了“TP 单成本太乐观、SL 单成本太悲观”的路径差异。</li>
    </ol>
    """

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · hot-coin fee compare (VIP0 5/5)</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1220px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <h1>Rank 32b · 热门小币研究费用口径对比</h1>
  <p class='muted'>生成时间：{escape(payload['generated_at_utc'])} ｜ 目标：把之前两轮热门币研究与新的 Binance VIP0 双边万5/万5 重算结果放到同一页比较，并解释结论是否变化。</p>

  <div class='card'>
    <h2>费用口径说明</h2>
    {intro}
    <p>
      <span class='pill'>旧口径：6 / 0 or 6</span>
      <span class='pill'>新口径：5 / 5</span>
      <span class='pill'>旧 10 币报告：<a href='{escape(str(PREV_SMALL_REPORT.relative_to(ROOT / 'reports' / 'site')))}'>smallcap regime study</a></span>
      <span class='pill'>旧 23 币报告：<a href='{escape(str(PREV_UNIV_REPORT.relative_to(ROOT / 'reports' / 'site')))}'>hot universe volume-phase study</a></span>
    </p>
  </div>

  <div class='card'>
    <h2>先看结论</h2>
    {takeaways}
  </div>

  <div class='card'>
    <h2>10 币小池：旧口径 vs VIP0 双边万5</h2>
    {render_compare_table(small_compare, 'variant')}
  </div>

  <div class='card'>
    <h2>23 币扩大池：旧口径 vs VIP0 双边万5</h2>
    {render_compare_table(univ_compare, 'variant')}
  </div>

  <div class='card'>
    <h2>VIP0 双边万5下：23 币扩大池 baseline 按热度阶段拆分</h2>
    {render_table(strict_univ_phase_baseline[['phase', 'trades', 'portfolio_total_return', 'win_rate', 'avg_net_ret', 'avg_hold_minutes', 'positive_assets', 'active_assets', 'positive_asset_ratio']], percent_cols={'portfolio_total_return', 'win_rate', 'avg_net_ret', 'positive_asset_ratio'}, digits_cols={'trades': 0, 'avg_hold_minutes': 1, 'positive_assets': 0, 'active_assets': 0})}
  </div>

  <div class='card'>
    <h2>VIP0 双边万5下：10 币小池 baseline 强势资产</h2>
    {render_table(strict_small_top[['asset', 'trades', 'total_return', 'win_rate', 'avg_net_ret']], percent_cols={'total_return', 'win_rate', 'avg_net_ret'}, digits_cols={'trades': 0})}
  </div>

  <div class='card'>
    <h2>VIP0 双边万5下：23 币扩大池 baseline 强势资产</h2>
    {render_table(strict_univ_top[['asset', 'trades', 'total_return', 'win_rate', 'avg_net_ret']], percent_cols={'total_return', 'win_rate', 'avg_net_ret'}, digits_cols={'trades': 0})}
  </div>

  <div class='card'>
    <h2>怎么理解这些数据</h2>
    {interpretation}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    prev = load_previous_frames()
    strict_small = run_strict_smallcap()
    strict_univ = run_strict_universe()

    strict_small_variant, strict_small_asset, strict_small_time, strict_small_detail = strict_small
    strict_univ_variant, strict_univ_asset, strict_univ_time, strict_univ_phase, strict_univ_detail = strict_univ

    strict_small_variant.to_csv(STRICT_SMALL_VARIANT_PATH, index=False)
    strict_small_asset.to_csv(STRICT_SMALL_ASSET_PATH, index=False)
    strict_small_time.to_csv(STRICT_SMALL_TIME_PATH, index=False)
    STRICT_SMALL_DETAIL_PATH.write_text(json.dumps(strict_small_detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    strict_univ_variant.to_csv(STRICT_UNIV_VARIANT_PATH, index=False)
    strict_univ_asset.to_csv(STRICT_UNIV_ASSET_PATH, index=False)
    strict_univ_phase.to_csv(STRICT_UNIV_PHASE_PATH, index=False)
    strict_univ_time.to_csv(STRICT_UNIV_TIME_PATH, index=False)
    STRICT_UNIV_DETAIL_PATH.write_text(json.dumps(strict_univ_detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = build_summary_payload(prev, strict_small, strict_univ)
    payload['small_compare'].to_csv(SMALL_COMPARE_PATH, index=False)
    payload['univ_compare'].to_csv(UNIVERSE_COMPARE_PATH, index=False)

    summary_json = {
        'generated_at_utc': payload['generated_at_utc'],
        'fee_assumption': payload['fee_assumption'],
        'small_baseline_prev': payload['small_baseline_prev'],
        'small_baseline_vip0': payload['small_baseline_vip0'],
        'univ_baseline_prev': payload['univ_baseline_prev'],
        'univ_baseline_vip0': payload['univ_baseline_vip0'],
        'univ_hot_prev': payload['univ_hot_prev'],
        'univ_hot_vip0': payload['univ_hot_vip0'],
        'univ_cold_prev': payload['univ_cold_prev'],
        'univ_cold_vip0': payload['univ_cold_vip0'],
    }
    SUMMARY_JSON_PATH.write_text(json.dumps(summary_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(build_html(payload), encoding='utf-8')

    print(json.dumps({
        'report_html': str(REPORT_PATH),
        'summary_json': str(SUMMARY_JSON_PATH),
        'small_compare_csv': str(SMALL_COMPARE_PATH),
        'hot_universe_compare_csv': str(UNIVERSE_COMPARE_PATH),
        'strict_small_variant_csv': str(STRICT_SMALL_VARIANT_PATH),
        'strict_universe_variant_csv': str(STRICT_UNIV_VARIANT_PATH),
        'generated_at_utc': payload['generated_at_utc'],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
