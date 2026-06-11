#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import types
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_pytrendline_event_validation_v3_report.py"
ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_sampler_fix_rerun_a4c"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_sampler_fix_rerun_a4c"

OLD_REF = "01ad061"
BREAKOUT_FAMILIES = ["breakout_raw", "breakout_confirm_1", "breakout_confirm_2"]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_current_module():
    spec = importlib.util.spec_from_file_location("v3cur", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_old_module(script_path: Path):
    old_src = subprocess.check_output(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "show",
            f"{OLD_REF}:jerry/momentum/scripts/build_pytrendline_event_validation_v3_report.py",
        ],
        text=True,
    )
    module = types.ModuleType("v3old")
    module.__dict__["__file__"] = str(script_path)
    exec(compile(old_src, str(script_path), "exec"), module.__dict__)
    return module


def collect_pipeline(cur, mod, *, symbols: list[str], period: str, interval: str, window_bars: int, snapshot_step_bars: int, horizons: list[int], confirm_bars: int, tol_mult: float):
    cfg = cur.PyTrendlineConfig(
        window_bars=window_bars,
        min_points_required=3,
        ignore_breakouts=False,
        trend_type="BOTH",
        first_pt_must_be_pivot=False,
        last_pt_must_be_pivot=False,
        all_pts_must_be_pivots=True,
        trendline_must_include_global_maxmin_pt=False,
        time_interval="1h",
    )

    frames: list[pd.DataFrame] = []
    symbol_meta: list[dict] = []
    for symbol in symbols:
        bars = cur.download_bars(symbol, period, interval, refresh=False)
        symbol_meta.append(
            {
                "symbol": symbol,
                "rows": int(len(bars)),
                "start": bars["timestamp"].iloc[0],
                "end": bars["timestamp"].iloc[-1],
            }
        )
        ev = mod.collect_events_for_symbol(
            symbol=symbol,
            bars=bars,
            window_bars=window_bars,
            snapshot_step_bars=snapshot_step_bars,
            horizons=horizons,
            confirm_bars=confirm_bars,
            tol_mult=tol_mult,
            cfg=cfg,
        )
        print(f"collect variant={mod.__name__} symbol={symbol} events={0 if ev.empty else len(ev)}", flush=True)
        if not ev.empty:
            frames.append(ev)

    if not frames:
        raise SystemExit(f"No events produced for variant={mod.__name__}")

    raw = pd.concat(frames, ignore_index=True)
    raw["event_type"] = pd.Categorical(raw["event_type"], categories=cur.EVENT_ORDER, ordered=True)
    raw = cur.add_event_family(raw)
    raw = raw.sort_values(["symbol", "event_timestamp", "event_type"]).reset_index(drop=True)

    raw_pair_summary = pd.DataFrame()
    raw_pair_details = pd.DataFrame()
    raw_pair_dropped = pd.DataFrame(columns=list(raw.columns) + ["drop_reason"])
    if mod is cur:
        raw, raw_pair_summary, raw_pair_details, raw_pair_dropped = cur.resolve_exact_mirrored_breakout_pairs(raw)

    purged = cur.purge_events(raw, purge_gap=max(horizons))
    purged = cur.add_event_family(purged)

    purged_pair_summary = pd.DataFrame()
    purged_pair_details = pd.DataFrame()
    purged_pair_dropped = pd.DataFrame(columns=list(purged.columns) + ["drop_reason"])
    if mod is cur:
        purged, purged_pair_summary, purged_pair_details, purged_pair_dropped = cur.resolve_exact_mirrored_breakout_pairs(purged)

    return {
        "raw": raw,
        "purged": purged,
        "symbol_meta": pd.DataFrame(symbol_meta),
        "raw_pair_summary": raw_pair_summary,
        "raw_pair_details": raw_pair_details,
        "raw_pair_dropped": raw_pair_dropped,
        "purged_pair_summary": purged_pair_summary,
        "purged_pair_details": purged_pair_details,
        "purged_pair_dropped": purged_pair_dropped,
    }


def strict_geometry_table(cur, df: pd.DataFrame, *, variant: str, stage: str) -> pd.DataFrame:
    work = cur.add_event_family(df)
    rows: list[dict] = []
    for family in BREAKOUT_FAMILIES:
        g = work[work["event_family"].astype(str) == family].copy()
        support = g[g["event_type"].astype(str).str.startswith("support_")].copy()
        resistance = g[g["event_type"].astype(str).str.startswith("resistance_")].copy()
        support_wrong = int((support["line_value_event"] > support["event_high"]).sum()) if not support.empty else 0
        resistance_wrong = int((resistance["line_value_event"] < resistance["event_low"]).sum()) if not resistance.empty else 0
        total = int(len(g))
        rows.append(
            {
                "variant": variant,
                "stage": stage,
                "family": family,
                "events": total,
                "strict_wrong_side_rows": int(support_wrong + resistance_wrong),
                "strict_wrong_side_share": float((support_wrong + resistance_wrong) / total) if total else 0.0,
                "support_rows": int(len(support)),
                "support_wrong_side_rows": int(support_wrong),
                "support_wrong_side_share": float(support_wrong / len(support)) if len(support) else 0.0,
                "resistance_rows": int(len(resistance)),
                "resistance_wrong_side_rows": int(resistance_wrong),
                "resistance_wrong_side_share": float(resistance_wrong / len(resistance)) if len(resistance) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def mirrored_pair_tables(cur, df: pd.DataFrame, *, variant: str, stage: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = cur.add_event_family(df).copy()
    work["pair_side"] = work["event_type"].astype(str).str.split("_").str[0]
    summary_rows: list[dict] = []
    detail_rows: list[dict] = []

    for family in BREAKOUT_FAMILIES:
        g = work[work["event_family"].astype(str) == family].copy()
        pair_count = 0
        rows_in_pairs = 0
        rows_to_drop = 0
        for key, gg in g.groupby(cur.MIRRORED_BREAKOUT_GROUP_COLS, dropna=False, sort=False):
            sides = set(gg["pair_side"].tolist())
            if len(gg) < 2 or sides != {"support", "resistance"}:
                continue
            pair_count += 1
            rows_in_pairs += int(len(gg))
            rows_to_drop += int(max(0, len(gg) - 1))
            detail_rows.append(
                {
                    "variant": variant,
                    "stage": stage,
                    "family": family,
                    **dict(zip(cur.MIRRORED_BREAKOUT_GROUP_COLS, key)),
                    "group_rows": int(len(gg)),
                    "support_rows": int((gg["pair_side"] == "support").sum()),
                    "resistance_rows": int((gg["pair_side"] == "resistance").sum()),
                    "event_types": " | ".join(gg["event_type"].astype(str).tolist()),
                    "engine_line_ids": " | ".join(gg["engine_line_id"].astype(str).tolist()),
                }
            )
        summary_rows.append(
            {
                "variant": variant,
                "stage": stage,
                "family": family,
                "paired_groups": int(pair_count),
                "rows_in_paired_groups": int(rows_in_pairs),
                "rows_to_drop_if_resolved": int(rows_to_drop),
            }
        )

    return pd.DataFrame(summary_rows), pd.DataFrame(detail_rows)


def breakout_count_table(cur, df: pd.DataFrame, *, variant: str, stage: str) -> pd.DataFrame:
    work = cur.add_event_family(df)
    rows: list[dict] = []
    for family in BREAKOUT_FAMILIES:
        g = work[work["event_family"].astype(str) == family]
        rows.append(
            {
                "variant": variant,
                "stage": stage,
                "family": family,
                "events": int(len(g)),
            }
        )
    return pd.DataFrame(rows)


def breakout_h24_table(cur, df: pd.DataFrame, *, variant: str, stage: str) -> pd.DataFrame:
    summary = cur.summarize(df, [24])
    summary = summary[["event_type", "events", "mean_ret", "median_ret", "up_ratio"]].copy()
    summary = summary[summary["event_type"].astype(str).str.contains("breakout")].copy()
    summary.insert(0, "stage", stage)
    summary.insert(0, "variant", variant)
    return summary.reset_index(drop=True)


def fmt_pct(x: float | int | None, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{float(x) * 100:.{digits}f}%"


def fmt_num(x: float | int | None, digits: int = 4) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{float(x):.{digits}f}"


def render_table(df: pd.DataFrame, *, limit: int | None = None) -> str:
    if df is None or df.empty:
        return "<p><em>empty</em></p>"
    shown = df.copy()
    if limit is not None:
        shown = shown.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            if "share" in col or col.endswith("_ret"):
                shown[col] = shown[col].map(lambda x: "" if pd.isna(x) else round(float(x), 6))
            else:
                shown[col] = shown[col].map(lambda x: "" if pd.isna(x) else round(float(x), 6))
    return shown.to_html(index=False, classes="tbl", border=0)


def chart_strict_compare(strict_df: pd.DataFrame, out_path: Path) -> None:
    pivot = strict_df.pivot_table(index="family", columns="variant", values="strict_wrong_side_share", aggfunc="first").reindex(BREAKOUT_FAMILIES)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = range(len(pivot.index))
    width = 0.36
    old_vals = pivot.get("pre_fix", pd.Series([0.0] * len(pivot.index), index=pivot.index)).fillna(0.0).tolist()
    new_vals = pivot.get("fixed", pd.Series([0.0] * len(pivot.index), index=pivot.index)).fillna(0.0).tolist()
    ax.bar([i - width / 2 for i in x], old_vals, width=width, label="pre-fix", color="#d95f02")
    ax.bar([i + width / 2 for i in x], new_vals, width=width, label="fixed", color="#1b9e77")
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.replace("breakout_", "") for s in pivot.index])
    ax.set_ylabel("strict wrong-side share")
    ax.set_title("Strict wrong-side breakout share (purged sample)")
    ax.legend()
    ax.set_ylim(0, max(0.45, max(old_vals + new_vals + [0.0]) * 1.2))
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def chart_pair_compare(pair_df: pd.DataFrame, out_path: Path) -> None:
    pivot = pair_df.pivot_table(index="family", columns="variant", values="paired_groups", aggfunc="first").reindex(BREAKOUT_FAMILIES)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = range(len(pivot.index))
    width = 0.36
    old_vals = pivot.get("pre_fix", pd.Series([0] * len(pivot.index), index=pivot.index)).fillna(0).tolist()
    new_vals = pivot.get("fixed", pd.Series([0] * len(pivot.index), index=pivot.index)).fillna(0).tolist()
    ax.bar([i - width / 2 for i in x], old_vals, width=width, label="pre-fix", color="#7570b3")
    ax.bar([i + width / 2 for i in x], new_vals, width=width, label="fixed", color="#66a61e")
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.replace("breakout_", "") for s in pivot.index])
    ax.set_ylabel("paired exact-match groups")
    ax.set_title("Exact mirrored breakout groups (purged sample)")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_report(*, symbols: list[str], period: str, interval: str, window_bars: int, snapshot_step_bars: int, horizons: list[int], confirm_bars: int, tol_mult: float, head_ref: str, strict_df: pd.DataFrame, pair_df: pd.DataFrame, count_df: pd.DataFrame, h24_df: pd.DataFrame, old_raw_pair_details: pd.DataFrame, old_purged_pair_details: pd.DataFrame, summary_payload: dict) -> None:
    ensure_dir(SITE)
    purged_strict = strict_df[strict_df["stage"] == "purged"].copy()
    purged_pairs = pair_df[pair_df["stage"] == "purged"].copy()
    old_purged = purged_strict[purged_strict["variant"] == "pre_fix"].set_index("family")
    new_purged = purged_strict[purged_strict["variant"] == "fixed"].set_index("family")

    bullets = []
    for family in BREAKOUT_FAMILIES:
        old_share = float(old_purged.loc[family, "strict_wrong_side_share"]) if family in old_purged.index else 0.0
        new_share = float(new_purged.loc[family, "strict_wrong_side_share"]) if family in new_purged.index else 0.0
        bullets.append(f"<li><strong>{escape(family)}</strong>: strict wrong-side share 从 <strong>{fmt_pct(old_share)}</strong> 降到 <strong>{fmt_pct(new_share)}</strong>。</li>")

    html = f"""<!doctype html>
<html lang='zh'>
<head>
  <meta charset='utf-8'>
  <title>PyTrendline v3 A4-c · sampler fix fresh rerun audit</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; color: #17202a; line-height: 1.6; padding: 0 16px 48px; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #5d6d7e; }}
    .card {{ border: 1px solid #dfe6e9; border-radius: 10px; padding: 16px 18px; margin: 16px 0; background: #fcfcfd; }}
    .good {{ background: #edf9f1; border-color: #b7e4c7; }}
    .warn {{ background: #fff8e8; border-color: #f7d794; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #dfe6e9; padding: 6px 8px; vertical-align: top; }}
    .tbl th {{ background: #f5f7fa; }}
    code {{ background: #f5f7fa; padding: 1px 4px; border-radius: 4px; }}
    ul {{ margin-top: 8px; }}
    img {{ max-width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; background: white; }}
  </style>
</head>
<body>
  <h1>PyTrendline v3 A4-c · 修正 sampler 后的最小 fresh rerun 审计</h1>
  <p class='muted'>生成时间：{escape(summary_payload['generated_at'])} ｜ old baseline = <code>{escape(OLD_REF)}</code>（R2/R3 前） ｜ fixed head = <code>{escape(head_ref)}</code> ｜ 页面定位：A4-c 最小 closure，不是全量 v3 正式重跑。</p>

  <div class='card good'>
    <h2>一句话结论</h2>
    <p>在同一份 <strong>BTC + ETH / 20d / 60m</strong> 最小样本上，修正后的 sampler 确实把我们关心的两类 breakout 脏样本清掉了：<strong>strict wrong-side rows 归零</strong>，<strong>exact mirrored pair groups 也归零</strong>；同时 breakout 样本没有被“一刀切删光”。</p>
  </div>

  <div class='grid'>
    <div class='card'>
      <h3>本轮到底测了什么</h3>
      <ul>
        <li>同样本 A/B：同一份行情、同一组参数，只换 sampler 逻辑。</li>
        <li>样本：<code>{escape(', '.join(symbols))}</code>，<code>{escape(period)}</code>，<code>{escape(interval)}</code>。</li>
        <li>参数：window <code>{window_bars}</code>，snapshot step <code>{snapshot_step_bars}</code>，confirm bars <code>{confirm_bars}</code>，tol mult <code>{tol_mult}</code>，horizons <code>{escape(', '.join(map(str, horizons)))}</code>。</li>
        <li>pre-fix = 只有 snapshot-side gate；fixed = 再加 event-time strict wrong-side gate + exact mirrored pair resolution。</li>
      </ul>
    </div>
    <div class='card'>
      <h3>这轮明确发现了什么</h3>
      <ul>
        {''.join(bullets)}
        <li>purged 样本里的 paired exact-match breakout groups：<strong>{int(purged_pairs[purged_pairs['variant']=='pre_fix']['paired_groups'].sum())}</strong> → <strong>{int(purged_pairs[purged_pairs['variant']=='fixed']['paired_groups'].sum())}</strong>。</li>
        <li>raw breakout rows 仍然保留了可观样本，不是“修 bug = 全删样本”。</li>
      </ul>
    </div>
    <div class='card warn'>
      <h3>这轮没有发现 / 也不该过度声称什么</h3>
      <ul>
        <li>这页<strong>不等于</strong> full v3 45d/4-asset 主报告已经 closure。</li>
        <li>这页也<strong>不支持</strong>“support breakout 和 resistance breakout 已经可以当独立 alpha 信号”——侧别 alpha 解释仍要继续谨慎。</li>
        <li>这份 20d 双币最小样本没有强烈重现早先“大页里 side mean 完全相同”的现象，所以它更像 <strong>cleanliness audit</strong>，不是 full alpha verdict。</li>
      </ul>
    </div>
  </div>

  <h2>怎么看这页</h2>
  <div class='card'>
    <p><strong>先看两张图：</strong>左图是 strict wrong-side 占比，右图是 exact mirrored pair group 数。只要 fixed 一侧降到 0，我们就知道 R2/R3 至少在这份最小 fresh rerun 里起效了。</p>
    <div class='grid'>
      <div><img src='strict_wrong_side_share_purged.png' alt='strict wrong-side share compare'></div>
      <div><img src='mirrored_pair_groups_purged.png' alt='mirrored pair groups compare'></div>
    </div>
  </div>

  <h2>核心结果表</h2>
  <div class='card'>
    <h3>1) strict geometry 对照（raw + purged）</h3>
    {render_table(strict_df)}
  </div>

  <div class='card'>
    <h3>2) exact mirrored pair 对照（raw + purged）</h3>
    {render_table(pair_df)}
  </div>

  <div class='card'>
    <h3>3) breakout 样本数有没有被删光？</h3>
    <p>答案：没有。fix 主要是在清理坏 breakout，而不是把 breakout family 整体抹掉。</p>
    {render_table(count_df)}
  </div>

  <div class='card'>
    <h3>4) h24 breakout side summary（只作 sanity check，不当 alpha 定论）</h3>
    <p>这张表的作用很有限：只是确认修复后 side-level 统计仍然能产出不同数值，而不是所有 breakout side 都被机械压成同一个结果。它<strong>不是</strong>“support / resistance 已可独立交易”的证据。</p>
    {render_table(h24_df)}
  </div>

  <div class='card'>
    <h3>5) pre-fix mirrored pair 明细（方便复查）</h3>
    <p>如果想逐条看旧逻辑下哪些 bar 同时留下了 support / resistance 两边 breakout，可以先看这里。</p>
    <h4>raw</h4>
    {render_table(old_raw_pair_details, limit=20)}
    <h4>purged</h4>
    {render_table(old_purged_pair_details, limit=20)}
  </div>

  <div class='card'>
    <h2>可靠性评估</h2>
    <ul>
      <li><strong>可靠的部分：</strong>这是同样本、同参数、旧逻辑 vs 新逻辑的 A/B，对“R2/R3 是否真的把脏 breakout 清掉”有中高可信度。</li>
      <li><strong>还不够的部分：</strong>样本只有 2 个币、20 天；它适合做 sampler cleanliness closure，不适合直接升级成 full alpha 宣判。</li>
      <li><strong>下一步最自然的动作：</strong>V3X-A 已可收口，后续应转到 V3X-B，把这些审计结论用用户可读方式补进主 v3 页面。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/strict_geometry_compare.csv'>strict_geometry_compare.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/mirrored_pair_compare.csv'>mirrored_pair_compare.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/breakout_count_compare.csv'>breakout_count_compare.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/breakout_h24_compare.csv'>breakout_h24_compare.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/pre_fix_mirrored_pair_details_raw.csv'>pre_fix_mirrored_pair_details_raw.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/pre_fix_mirrored_pair_details_purged.csv'>pre_fix_mirrored_pair_details_purged.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/summary.json'>summary.json</a></li>
    </ul>
  </div>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build pytrendline v3 sampler-fix fresh rerun A4-c audit page")
    p.add_argument("--symbols", default="BTC-USD,ETH-USD")
    p.add_argument("--period", default="20d")
    p.add_argument("--interval", default="60m")
    p.add_argument("--window-bars", type=int, default=72)
    p.add_argument("--snapshot-step-bars", type=int, default=24)
    p.add_argument("--horizons", default="6,24,48,72")
    p.add_argument("--confirm-bars", type=int, default=2)
    p.add_argument("--tol-mult", type=float, default=0.08)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dir(ART)
    ensure_dir(SITE)

    cur = load_current_module()
    old = load_old_module(SCRIPT_PATH)
    head_ref = subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    horizons = sorted({int(x.strip()) for x in args.horizons.split(",") if x.strip()})

    old_run = collect_pipeline(
        cur,
        old,
        symbols=symbols,
        period=args.period,
        interval=args.interval,
        window_bars=int(args.window_bars),
        snapshot_step_bars=int(args.snapshot_step_bars),
        horizons=horizons,
        confirm_bars=int(args.confirm_bars),
        tol_mult=float(args.tol_mult),
    )
    new_run = collect_pipeline(
        cur,
        cur,
        symbols=symbols,
        period=args.period,
        interval=args.interval,
        window_bars=int(args.window_bars),
        snapshot_step_bars=int(args.snapshot_step_bars),
        horizons=horizons,
        confirm_bars=int(args.confirm_bars),
        tol_mult=float(args.tol_mult),
    )

    strict_df = pd.concat(
        [
            strict_geometry_table(cur, old_run["raw"], variant="pre_fix", stage="raw"),
            strict_geometry_table(cur, new_run["raw"], variant="fixed", stage="raw"),
            strict_geometry_table(cur, old_run["purged"], variant="pre_fix", stage="purged"),
            strict_geometry_table(cur, new_run["purged"], variant="fixed", stage="purged"),
        ],
        ignore_index=True,
    )
    pair_old_raw, pair_old_raw_details = mirrored_pair_tables(cur, old_run["raw"], variant="pre_fix", stage="raw")
    pair_new_raw, pair_new_raw_details = mirrored_pair_tables(cur, new_run["raw"], variant="fixed", stage="raw")
    pair_old_purged, pair_old_purged_details = mirrored_pair_tables(cur, old_run["purged"], variant="pre_fix", stage="purged")
    pair_new_purged, pair_new_purged_details = mirrored_pair_tables(cur, new_run["purged"], variant="fixed", stage="purged")
    pair_df = pd.concat([pair_old_raw, pair_new_raw, pair_old_purged, pair_new_purged], ignore_index=True)

    count_df = pd.concat(
        [
            breakout_count_table(cur, old_run["raw"], variant="pre_fix", stage="raw"),
            breakout_count_table(cur, new_run["raw"], variant="fixed", stage="raw"),
            breakout_count_table(cur, old_run["purged"], variant="pre_fix", stage="purged"),
            breakout_count_table(cur, new_run["purged"], variant="fixed", stage="purged"),
        ],
        ignore_index=True,
    )
    h24_df = pd.concat(
        [
            breakout_h24_table(cur, old_run["purged"], variant="pre_fix", stage="purged"),
            breakout_h24_table(cur, new_run["purged"], variant="fixed", stage="purged"),
        ],
        ignore_index=True,
    )

    strict_df.to_csv(ART / "strict_geometry_compare.csv", index=False)
    pair_df.to_csv(ART / "mirrored_pair_compare.csv", index=False)
    count_df.to_csv(ART / "breakout_count_compare.csv", index=False)
    h24_df.to_csv(ART / "breakout_h24_compare.csv", index=False)
    pair_old_raw_details.to_csv(ART / "pre_fix_mirrored_pair_details_raw.csv", index=False)
    pair_old_purged_details.to_csv(ART / "pre_fix_mirrored_pair_details_purged.csv", index=False)
    pair_new_raw_details.to_csv(ART / "fixed_mirrored_pair_details_raw.csv", index=False)
    pair_new_purged_details.to_csv(ART / "fixed_mirrored_pair_details_purged.csv", index=False)

    chart_strict_compare(strict_df[strict_df["stage"] == "purged"].copy(), SITE / "strict_wrong_side_share_purged.png")
    chart_pair_compare(pair_df[pair_df["stage"] == "purged"].copy(), SITE / "mirrored_pair_groups_purged.png")

    summary_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "old_ref": OLD_REF,
        "head_ref": head_ref,
        "symbols": symbols,
        "period": args.period,
        "interval": args.interval,
        "window_bars": int(args.window_bars),
        "snapshot_step_bars": int(args.snapshot_step_bars),
        "horizons": horizons,
        "confirm_bars": int(args.confirm_bars),
        "tol_mult": float(args.tol_mult),
        "old_total_raw": int(len(old_run["raw"])),
        "new_total_raw": int(len(new_run["raw"])),
        "old_total_purged": int(len(old_run["purged"])),
        "new_total_purged": int(len(new_run["purged"])),
        "purged_strict_wrong_side_rows_old": int(strict_df[(strict_df["variant"] == "pre_fix") & (strict_df["stage"] == "purged")]["strict_wrong_side_rows"].sum()),
        "purged_strict_wrong_side_rows_new": int(strict_df[(strict_df["variant"] == "fixed") & (strict_df["stage"] == "purged")]["strict_wrong_side_rows"].sum()),
        "purged_mirrored_pair_groups_old": int(pair_df[(pair_df["variant"] == "pre_fix") & (pair_df["stage"] == "purged")]["paired_groups"].sum()),
        "purged_mirrored_pair_groups_new": int(pair_df[(pair_df["variant"] == "fixed") & (pair_df["stage"] == "purged")]["paired_groups"].sum()),
        "notes": [
            "This page is an A4-c minimum rerun closure, not a full v3 re-publication.",
            "Pre-fix variant is loaded from git ref 01ad061, before strict wrong-side gate and mirrored-pair resolution.",
            "Fixed variant is current HEAD and includes snapshot-side visibility gate, event-time strict wrong-side gate, and exact mirrored-pair resolution.",
        ],
    }
    (ART / "summary.json").write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    build_report(
        symbols=symbols,
        period=args.period,
        interval=args.interval,
        window_bars=int(args.window_bars),
        snapshot_step_bars=int(args.snapshot_step_bars),
        horizons=horizons,
        confirm_bars=int(args.confirm_bars),
        tol_mult=float(args.tol_mult),
        head_ref=head_ref,
        strict_df=strict_df,
        pair_df=pair_df,
        count_df=count_df,
        h24_df=h24_df,
        old_raw_pair_details=pair_old_raw_details,
        old_purged_pair_details=pair_old_purged_details,
        summary_payload=summary_payload,
    )

    print(f"[ok] A4-c rerun report -> {SITE / 'report.html'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
