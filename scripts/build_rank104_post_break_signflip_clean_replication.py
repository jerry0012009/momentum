#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank104_post_break_signflip_density_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank104_post_break_signflip_density_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank104_post_break_signflip_density_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
LOOKBACK = 20
ATR_PERIOD = 14
HOLD_BARS = 8
EARLY_BARS = 3
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def bps(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.{digits}f} bps"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in bps_cols:
                text = bps(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding="utf-8")


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def sign_flip_bucket(flips: int) -> str:
    if flips <= 0:
        return "low_flip_0"
    if flips == 1:
        return "mid_flip_1"
    return "high_flip_2"


def cost_net(gross: pd.Series, cost_bps: float) -> pd.Series:
    c = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - c) * (1.0 - c) - 1.0


def build_event_log() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        df = load_bars(symbol, asset)
        df["atr14"] = atr(df)
        df["prev_high_20"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
        df["prev_low_20"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
        body = (df["close"] - df["open"]).abs()
        rng = (df["high"] - df["low"]).replace(0, np.nan)
        df["body_ratio"] = body / rng
        ext_long = (df["close"] - df["prev_high_20"]) / df["atr14"]
        ext_short = (df["prev_low_20"] - df["close"]) / df["atr14"]

        for idx in range(LOOKBACK + 5, len(df) - HOLD_BARS - 1):
            atr14 = float(df.iloc[idx]["atr14"])
            if not np.isfinite(atr14) or atr14 <= 0:
                continue
            side = None
            break_level = np.nan
            if df.iloc[idx]["close"] > df.iloc[idx]["prev_high_20"] and df.iloc[idx]["body_ratio"] >= 0.4 and ext_long.iloc[idx] >= 0.2:
                side = "long"
                break_level = float(df.iloc[idx]["prev_high_20"])
            elif df.iloc[idx]["close"] < df.iloc[idx]["prev_low_20"] and df.iloc[idx]["body_ratio"] >= 0.4 and ext_short.iloc[idx] >= 0.2:
                side = "short"
                break_level = float(df.iloc[idx]["prev_low_20"])
            if side is None or not np.isfinite(break_level):
                continue

            entry_idx = idx + 1
            decision_idx = idx + 1 + EARLY_BARS
            exit_idx = idx + HOLD_BARS
            if exit_idx >= len(df) or decision_idx >= len(df):
                continue
            early = df.iloc[entry_idx:decision_idx].copy()
            later = df.iloc[decision_idx:exit_idx + 1].copy()
            if len(early) < EARLY_BARS or len(later) < (HOLD_BARS - EARLY_BARS):
                continue

            early_signed = ((early["close"] - early["open"]) / early["open"]).to_numpy(dtype=float)
            if side == "short":
                early_signed = -early_signed
            early_sign = np.sign(early_signed)
            for j in range(len(early_sign)):
                if early_sign[j] == 0:
                    early_sign[j] = early_sign[j - 1] if j > 0 else 1
            early_flips = int(np.sum(early_sign[1:] != early_sign[:-1]))
            bucket = sign_flip_bucket(early_flips)

            entry_px = float(df.iloc[entry_idx]["open"])
            decision_px = float(df.iloc[decision_idx]["open"])
            exit_px = float(df.iloc[exit_idx]["close"])
            if not np.isfinite(entry_px) or not np.isfinite(decision_px) or not np.isfinite(exit_px) or entry_px <= 0 or decision_px <= 0 or exit_px <= 0:
                continue

            gross_hold8 = exit_px / entry_px - 1.0
            gross_exit_after_early = decision_px / entry_px - 1.0
            residual_gross = exit_px / decision_px - 1.0
            if side == "short":
                gross_hold8 = -gross_hold8
                gross_exit_after_early = -gross_exit_after_early
                residual_gross = -residual_gross

            later_high = float(later["high"].max())
            later_low = float(later["low"].min())
            fail_back_inside = int(later_low <= break_level) if side == "long" else int(later_high >= break_level)
            cont_hit_0p5atr = int(later_high >= decision_px + 0.5 * atr14) if side == "long" else int(later_low <= decision_px - 0.5 * atr14)
            if side == "long":
                tail_loss = float((later["low"] / decision_px - 1.0).min())
            else:
                tail_loss = float((decision_px / later["high"] - 1.0).min())

            rows.append(
                {
                    "asset": asset,
                    "symbol": symbol,
                    "signal_ts": df.iloc[idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "side": side,
                    "break_level": break_level,
                    "atr14": atr14,
                    "entry_open": entry_px,
                    "decision_open": decision_px,
                    "exit_close_8bars": exit_px,
                    "early_flip_count": early_flips,
                    "early_flip_bucket": bucket,
                    "gross_ret_hold8": gross_hold8,
                    "gross_ret_exit_after_early": gross_exit_after_early,
                    "gross_ret_residual_5bars": residual_gross,
                    "fail_back_inside_after_decision": fail_back_inside,
                    "cont_hit_0p5atr_after_decision": cont_hit_0p5atr,
                    "tail_loss_after_decision": tail_loss,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    events = build_event_log()
    if events.empty:
        raise SystemExit("no events built")

    bucket_summary = (
        events.groupby("early_flip_bucket")
        .agg(
            events=("gross_ret_hold8", "size"),
            share=("gross_ret_hold8", lambda s: len(s) / len(events)),
            mean_gross_ret_hold8=("gross_ret_hold8", "mean"),
            mean_gross_ret_residual_5bars=("gross_ret_residual_5bars", "mean"),
            cont_hit_rate_after_decision=("cont_hit_0p5atr_after_decision", "mean"),
            fail_back_inside_rate_after_decision=("fail_back_inside_after_decision", "mean"),
            tail_loss_p05_after_decision=("tail_loss_after_decision", lambda s: s.quantile(0.05)),
        )
        .reset_index()
    )

    side_summary = (
        events.groupby(["side", "early_flip_bucket"])
        .agg(
            events=("gross_ret_hold8", "size"),
            mean_gross_ret_hold8=("gross_ret_hold8", "mean"),
            mean_gross_ret_residual_5bars=("gross_ret_residual_5bars", "mean"),
            cont_hit_rate_after_decision=("cont_hit_0p5atr_after_decision", "mean"),
            fail_back_inside_rate_after_decision=("fail_back_inside_after_decision", "mean"),
        )
        .reset_index()
    )

    policy_rows: list[dict[str, object]] = []
    for cost in COSTS:
        base = cost_net(events["gross_ret_hold8"], cost)
        early_exit_low = np.where(events["early_flip_bucket"] == "low_flip_0", cost_net(events["gross_ret_exit_after_early"], cost), cost_net(events["gross_ret_hold8"], cost))
        for variant, series in {
            "baseline_hold8": base,
            "overlay_exit_low_after_3bars": pd.Series(early_exit_low),
        }.items():
            policy_rows.append(
                {
                    "variant": variant,
                    "cost_bps_per_side": cost,
                    "events": len(events),
                    "mean_net_ret": float(series.mean()),
                    "tail_loss_p05": float(pd.Series(series).quantile(0.05)),
                    "positive_rate": float((series > 0).mean()),
                }
            )
            for side in ["long", "short"]:
                mask = events["side"] == side
                sub = pd.Series(series[mask.to_numpy()])
                policy_rows.append(
                    {
                        "variant": f"{variant}__{side}",
                        "cost_bps_per_side": cost,
                        "events": int(mask.sum()),
                        "mean_net_ret": float(sub.mean()),
                        "tail_loss_p05": float(sub.quantile(0.05)),
                        "positive_rate": float((sub > 0).mean()),
                    }
                )
    policy_compare = pd.DataFrame(policy_rows)

    base6 = policy_compare[(policy_compare["variant"] == "baseline_hold8") & (policy_compare["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    overlay6 = policy_compare[(policy_compare["variant"] == "overlay_exit_low_after_3bars") & (policy_compare["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    delta_mean = float(overlay6["mean_net_ret"] - base6["mean_net_ret"])
    delta_tail = float(overlay6["tail_loss_p05"] - base6["tail_loss_p05"])

    verdict = "park / evidence pool"
    desk_readthrough = (
        "strict non-leaky early-window 版本只留下很弱的风险管理信号："
        "low-flip 提前退出在 6bps/side 下仅带来约 0.16bps 的均值改善，"
        "主要价值更像轻微削尾而不是能稳定抬升 shared gate expectancy。"
    )
    next_step = "切 body-defined zone re-entry honest failure verdict 的 source intake；只有 fresh source 也 exhausted，才轮到 MTF CHOP > prebreak ladder > 旧 evidence pool。"

    verdict_summary = pd.DataFrame(
        [
            {
                "rank": 104,
                "candidate": "post-break sign-flip density",
                "current_hard_verdict": verdict,
                "desk_readthrough": desk_readthrough,
                "next_step": next_step,
                "events": len(events),
                "low_flip_share": float(bucket_summary.loc[bucket_summary["early_flip_bucket"] == "low_flip_0", "share"].iloc[0]),
                "low_flip_mean_gross_ret_hold8": float(bucket_summary.loc[bucket_summary["early_flip_bucket"] == "low_flip_0", "mean_gross_ret_hold8"].iloc[0]),
                "high_flip_mean_gross_ret_hold8": float(bucket_summary.loc[bucket_summary["early_flip_bucket"] == "high_flip_2", "mean_gross_ret_hold8"].iloc[0]),
                "baseline_mean_net_ret_6bps": float(base6["mean_net_ret"]),
                "overlay_mean_net_ret_6bps": float(overlay6["mean_net_ret"]),
                "overlay_minus_base_mean_net_ret_6bps": delta_mean,
                "overlay_minus_base_tail_loss_p05_6bps": delta_tail,
                "generated_at_utc": generated_at,
            }
        ]
    )

    snapshot = {
        "generated_at_utc": generated_at,
        "events": int(len(events)),
        "early_bars": EARLY_BARS,
        "hold_bars": HOLD_BARS,
        "definition": "20-bar breakout + body_ratio>=0.4 + extension>=0.2 ATR; decision made after first 3 completed post-break bars; evaluate residual next 5 bars",
        "baseline_mean_net_ret_6bps": float(base6["mean_net_ret"]),
        "overlay_mean_net_ret_6bps": float(overlay6["mean_net_ret"]),
        "overlay_minus_base_mean_net_ret_6bps": delta_mean,
        "overlay_minus_base_tail_loss_p05_6bps": delta_tail,
        "verdict": verdict,
    }

    events.to_csv(ART_DIR / "event_log.csv", index=False)
    bucket_summary.to_csv(ART_DIR / "bucket_summary.csv", index=False)
    side_summary.to_csv(ART_DIR / "side_summary.csv", index=False)
    policy_compare.to_csv(ART_DIR / "policy_compare.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    bucket_table = render_table(
        bucket_summary,
        percent_cols={"share", "cont_hit_rate_after_decision", "fail_back_inside_rate_after_decision"},
        bps_cols={"mean_gross_ret_hold8", "mean_gross_ret_residual_5bars", "tail_loss_p05_after_decision"},
        digits_cols={"events": 0},
    )
    side_table = render_table(
        side_summary,
        percent_cols={"cont_hit_rate_after_decision", "fail_back_inside_rate_after_decision"},
        bps_cols={"mean_gross_ret_hold8", "mean_gross_ret_residual_5bars"},
        digits_cols={"events": 0},
    )
    policy_table = render_table(
        policy_compare[policy_compare["cost_bps_per_side"] == PRIMARY_COST],
        percent_cols={"positive_rate"},
        bps_cols={"mean_net_ret", "tail_loss_p05"},
        digits_cols={"events": 0, "cost_bps_per_side": 0},
    )

    body = f"""
<h1>Rank 104 · post-break sign-flip density clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：BTC/ETH/SOL 120d 15m cache ｜ 口径：strict non-leaky early-window（先看前 3 根 post-break bars，再评估后 5 根管理价值）</p>
<div class='card'>
  <p><strong>硬结论：</strong><span class='bad'>{escape(verdict)}</span></p>
  <p>{escape(desk_readthrough)}</p>
  <p><strong>下一步：</strong>{escape(next_step)}</p>
</div>
<div class='card'>
  <h2>这轮到底测了什么</h2>
  <ul>
    <li>breakout 定义沿用 digest：<code>close</code> 突破 <code>prev_high_20 / prev_low_20</code>，且 <code>body_ratio&gt;=0.4</code>、<code>extension&gt;=0.2 ATR</code>。</li>
    <li>只允许使用 breakout 后<strong>前 3 根已完成 bars</strong> 的方向切换数作为决策依据，避免把完整 6 根路径回填进 breakout 当下。</li>
    <li>这不是新 entry gate，而是管理层实验：比较 <code>baseline_hold8</code> 与 <code>low_flip 提前在第 4 根 open 退出</code> 的差别。</li>
  </ul>
</div>
<div class='card'>
  <h2>分桶摘要</h2>
  {bucket_table}
</div>
<div class='card'>
  <h2>分侧摘要</h2>
  {side_table}
</div>
<div class='card'>
  <h2>6 bps/side 管理政策对比</h2>
  {policy_table}
  <p class='muted'>读法：若 low-flip 真的能稳定识别“脆弱延续”，那么 <code>overlay_exit_low_after_3bars</code> 应该明显优于 baseline。实际只看到极小的均值改善与轻微削尾，不足以升到 shared queue-facing gate。</p>
</div>
<div class='card'>
  <h2>产物</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank104_post_break_signflip_density_15m/event_log.csv</code></li>
    <li><code>reports/artifacts/scout_rank104_post_break_signflip_density_15m/bucket_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank104_post_break_signflip_density_15m/side_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank104_post_break_signflip_density_15m/policy_compare.csv</code></li>
    <li><code>reports/artifacts/scout_rank104_post_break_signflip_density_15m/verdict_summary.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 104 · post-break sign-flip density clean replication", body)
    write_html(READING_PATH, "Rank 104 · post-break sign-flip density clean replication", body)


if __name__ == "__main__":
    main()
