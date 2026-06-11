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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank96_advancedma_retest_count_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank96_advancedma_retest_count_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank96_advancedma_retest_count_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
VARIANTS = ["baseline", "first_touch_only", "second_touch_only", "second_touch_plus_candle_quality"]
LOOKBACK = 20
HOLD_BARS = 8
MAX_RETEST_WAIT = 16
ZONE_PCT = 0.0015
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "second_touch_plus_candle_quality"
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


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["prev_high_20"] = out["high"].shift(1).rolling(LOOKBACK).max()
    out["prev_low_20"] = out["low"].shift(1).rolling(LOOKBACK).min()
    rng = (out["high"] - out["low"]).replace(0, np.nan)
    body = (out["close"] - out["open"]).abs()
    out["body_ratio"] = (body / rng).fillna(0.0)
    out["close_pos"] = ((out["close"] - out["low"]) / rng).clip(0, 1).fillna(0.5)
    out["volume_sma20"] = out["volume"].rolling(20).mean()
    out["vol_ratio"] = (out["volume"] / out["volume_sma20"]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


def candle_quality(row: pd.Series, side: str) -> bool:
    if side == "long":
        return bool(row["body_ratio"] >= 0.4 and row["close_pos"] >= 0.6 and row["vol_ratio"] >= 1.0)
    return bool(row["body_ratio"] >= 0.4 and row["close_pos"] <= 0.4 and row["vol_ratio"] >= 1.0)


def effective_retest(row: pd.Series, level: float, side: str) -> bool:
    zone = max(level * ZONE_PCT, 1e-9)
    if side == "long":
        touched = row["low"] <= level + zone
        reclaimed = row["close"] >= level
        return bool(touched and reclaimed)
    touched = row["high"] >= level - zone
    reclaimed = row["close"] <= level
    return bool(touched and reclaimed)


def collect_events(df: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(df)
    for i in range(LOOKBACK + 1, n - HOLD_BARS - 2):
        row = df.iloc[i]
        long_level = row["prev_high_20"]
        short_level = row["prev_low_20"]
        breakout_long = pd.notna(long_level) and row["close"] > long_level and row["close"] > row["open"]
        breakout_short = pd.notna(short_level) and row["close"] < short_level and row["close"] < row["open"]
        for side, active, level in (("long", breakout_long, long_level), ("short", breakout_short, short_level)):
            if not active or pd.isna(level):
                continue
            baseline_entry_idx = i + 1
            if baseline_entry_idx + HOLD_BARS >= n:
                continue
            rows.append(
                dict(
                    asset=asset,
                    side=side,
                    variant="baseline",
                    signal_idx=i,
                    signal_time=row["timestamp"],
                    entry_idx=baseline_entry_idx,
                    entry_time=df.iloc[baseline_entry_idx]["timestamp"],
                    entry_price=float(df.iloc[baseline_entry_idx]["open"]),
                    exit_idx=baseline_entry_idx + HOLD_BARS,
                    exit_time=df.iloc[baseline_entry_idx + HOLD_BARS]["timestamp"],
                    exit_price=float(df.iloc[baseline_entry_idx + HOLD_BARS]["close"]),
                    level=float(level),
                    retest_count=0,
                    with_quality=False,
                )
            )
            retest_count = 0
            for j in range(i + 1, min(n - HOLD_BARS - 1, i + 1 + MAX_RETEST_WAIT)):
                probe = df.iloc[j]
                if not effective_retest(probe, float(level), side):
                    continue
                retest_count += 1
                quality = candle_quality(probe, side)
                variant = None
                if retest_count == 1:
                    variant = "first_touch_only"
                elif retest_count >= 2:
                    variant = "second_touch_only"
                    if quality:
                        rows.append(
                            dict(
                                asset=asset,
                                side=side,
                                variant="second_touch_plus_candle_quality",
                                signal_idx=j,
                                signal_time=probe["timestamp"],
                                entry_idx=j + 1,
                                entry_time=df.iloc[j + 1]["timestamp"],
                                entry_price=float(df.iloc[j + 1]["open"]),
                                exit_idx=j + 1 + HOLD_BARS,
                                exit_time=df.iloc[j + 1 + HOLD_BARS]["timestamp"],
                                exit_price=float(df.iloc[j + 1 + HOLD_BARS]["close"]),
                                level=float(level),
                                retest_count=retest_count,
                                with_quality=True,
                            )
                        )
                if variant is not None:
                    rows.append(
                        dict(
                            asset=asset,
                            side=side,
                            variant=variant,
                            signal_idx=j,
                            signal_time=probe["timestamp"],
                            entry_idx=j + 1,
                            entry_time=df.iloc[j + 1]["timestamp"],
                            entry_price=float(df.iloc[j + 1]["open"]),
                            exit_idx=j + 1 + HOLD_BARS,
                            exit_time=df.iloc[j + 1 + HOLD_BARS]["timestamp"],
                            exit_price=float(df.iloc[j + 1 + HOLD_BARS]["close"]),
                            level=float(level),
                            retest_count=retest_count,
                            with_quality=(variant == "second_touch_plus_candle_quality"),
                        )
                    )
                if retest_count >= 2:
                    break
    return pd.DataFrame(rows)


def apply_no_overlap(events: pd.DataFrame) -> pd.DataFrame:
    kept = []
    for (asset, side, variant), grp in events.sort_values(["entry_idx", "signal_idx"]).groupby(["asset", "side", "variant"], sort=False):
        last_exit = -1
        for _, row in grp.iterrows():
            if int(row["entry_idx"]) <= last_exit:
                continue
            kept.append(row.to_dict())
            last_exit = int(row["exit_idx"])
    return pd.DataFrame(kept)


def add_returns(events: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    direction = np.where(out["side"] == "long", 1.0, -1.0)
    gross = direction * (out["exit_price"] / out["entry_price"] - 1.0)
    out["gross_return"] = gross
    out["hold8_success"] = out["gross_return"] > 0
    out["fail_close"] = out["gross_return"] <= 0
    for cost in COSTS:
        out[f"net_return_{int(cost)}bps"] = out["gross_return"] - 2.0 * (cost / 10000.0)
        out[f"expectancy_bps_{int(cost)}"] = out[f"net_return_{int(cost)}bps"] * 10000.0
        out[f"positive_net_{int(cost)}"] = out[f"net_return_{int(cost)}bps"] > 0
    return out


def baseline_counts(events: pd.DataFrame) -> pd.DataFrame:
    base = events[events["variant"] == "baseline"].groupby(["asset", "side"], as_index=False).size().rename(columns={"size": "baseline_trades"})
    return base


def build_summaries(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    primary = int(PRIMARY_COST)
    counts = baseline_counts(events)
    merged = events.merge(counts, on=["asset", "side"], how="left")
    merged["trade_count_retention"] = merged.groupby(["asset", "side", "variant"])["asset"].transform("size") / merged["baseline_trades"].replace(0, np.nan)
    asset_summary = (
        merged.groupby(["variant", "side", "asset"], as_index=False)
        .agg(
            trades=("asset", "size"),
            mean_net_bps=(f"expectancy_bps_{primary}", "mean"),
            total_return=(f"net_return_{primary}bps", "sum"),
            hold8_rate=("hold8_success", "mean"),
            fail_close_ratio=("fail_close", "mean"),
            trade_count_retention=("trade_count_retention", "mean"),
        )
    )
    overall = (
        asset_summary.groupby(["variant", "side"], as_index=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            post_cost_expectancy_bps=("mean_net_bps", "mean"),
            hold8_rate=("hold8_rate", "mean"),
            fail_close_ratio=("fail_close_ratio", "mean"),
            trade_count_retention=("trade_count_retention", "mean"),
        )
    )
    cost_rows = []
    for cost in COSTS:
        col = f"net_return_{int(cost)}bps"
        expect_col = f"expectancy_bps_{int(cost)}"
        tmp = merged.groupby(["variant", "side", "asset"], as_index=False).agg(total_return=(col, "sum"), expectancy_bps=(expect_col, "mean"))
        tmp2 = tmp.groupby(["variant", "side"], as_index=False).agg(
            cost_bps=("variant", lambda _: cost),
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            post_cost_expectancy_bps=("expectancy_bps", "mean"),
        )
        cost_rows.append(tmp2)
    cost_summary = pd.concat(cost_rows, ignore_index=True)
    verdict = {"primary_variant": PRIMARY_VARIANT, "primary_cost_bps": PRIMARY_COST}
    return merged, asset_summary, overall, {"cost_summary": cost_summary.to_dict(orient="records"), **verdict}


def decide_verdict(overall: pd.DataFrame) -> dict:
    short = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["side"] == "short")]
    long = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["side"] == "long")]
    baseline_short = overall[(overall["variant"] == "baseline") & (overall["side"] == "short")]
    if short.empty:
        return {"hard_verdict": "park / evidence pool", "reason": "主变体在 short 侧没有形成可交易样本。"}
    s = short.iloc[0]
    bs = baseline_short.iloc[0] if not baseline_short.empty else None
    long_row = long.iloc[0] if not long.empty else None
    if s["post_cost_expectancy_bps"] > 0 and s["positive_asset_ratio"] >= 2/3 and s["trade_count_retention"] >= 0.25:
        if long_row is not None and long_row["post_cost_expectancy_bps"] > -5:
            return {"hard_verdict": "promote_to_P2 / paper candidate", "reason": "short 侧在成本后转正且跨资产不过分集中，long 侧也没有明显爆雷。"}
        return {"hard_verdict": "keep_P1 / short-side only", "reason": "short 侧改善真实，但 long 侧仍只是减亏，不够升成共享 gate。"}
    if bs is not None and s["post_cost_expectancy_bps"] > bs["post_cost_expectancy_bps"] and s["fail_close_ratio"] < bs["fail_close_ratio"]:
        return {"hard_verdict": "keep_P1 / short-side only", "reason": "short 侧比 baseline 更诚实，但跨资产与成本后力度还不足以升到 P2。"}
    return {"hard_verdict": "park / evidence pool", "reason": "second-touch 变体没有把成本后收益、跨资产一致性和失败率一起改善到值得继续占主资源。"}


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    all_events = []
    for asset, symbol in ASSETS.items():
        df = add_features(load_bars(symbol, asset))
        all_events.append(collect_events(df, asset))
    events = pd.concat(all_events, ignore_index=True)
    events = apply_no_overlap(events)
    events = add_returns(events)
    merged, asset_summary, overall, meta = build_summaries(events)
    cost_summary = pd.DataFrame(meta.pop("cost_summary"))
    verdict = decide_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    events.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary_primary_6bps.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)
    summary_json = {
        "generated_at_utc": generated_at,
        "lookback": LOOKBACK,
        "hold_bars": HOLD_BARS,
        "max_retest_wait": MAX_RETEST_WAIT,
        "zone_pct": ZONE_PCT,
        "primary_variant": PRIMARY_VARIANT,
        **verdict,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    overall_show = overall.copy().sort_values(["side", "variant"])
    asset_show = asset_summary.copy().sort_values(["side", "variant", "asset"])
    cost_show = cost_summary.copy().sort_values(["cost_bps", "side", "variant"])
    percent_cols = {"mean_total_return", "positive_asset_ratio", "hold8_rate", "fail_close_ratio", "trade_count_retention", "total_return"}
    html = f"""
    <p><a href='../../plans/momentum_todo.html'>← 返回 TODO / desk board</a></p>
    <h1>Rank 96 · AdvancedMA retest-count admission layer clean replication</h1>
    <div class='card'>
      <p><b>更新时间：</b>{escape(generated_at)}</p>
      <p><b>测试口径：</b><code>BTC / ETH / SOL | 120d | 15m | next-bar open | no-overlap | hold 8 bars</code></p>
      <p><b>比较四臂：</b><code>baseline / first_touch_only / second_touch_only / second_touch_plus_candle_quality</code></p>
      <p><b>hard verdict：</b><span class='{'good' if 'promote' in verdict['hard_verdict'] or 'keep' in verdict['hard_verdict'] else 'bad'}'>{escape(verdict['hard_verdict'])}</span></p>
      <p><b>一句话：</b>{escape(verdict['reason'])}</p>
    </div>
    <div class='card'>
      <h2>怎么读这轮 replication</h2>
      <ul>
        <li><code>baseline</code> = 20-bar breakout 后，直接 next-bar open 进入，不等 retest。</li>
        <li><code>first_touch_only</code> = breakout 后第一次有效 retest 就放行。</li>
        <li><code>second_touch_only</code> = 至少第二次有效 retest 才放行。</li>
        <li><code>second_touch_plus_candle_quality</code> = 第二次 retest 且当根实体/收盘位置/量能不过分差。</li>
      </ul>
    </div>
    <div class='card'><h2>整体结果（6bps/side）</h2>{render_table(overall_show, percent_cols=percent_cols, digits_cols={'post_cost_expectancy_bps':2, 'mean_trades':1})}</div>
    <div class='card'><h2>分资产结果（6bps/side）</h2>{render_table(asset_show, percent_cols=percent_cols, digits_cols={'mean_net_bps':2, 'trades':0})}</div>
    <div class='card'><h2>成本敏感度</h2>{render_table(cost_show, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'cost_bps':0, 'post_cost_expectancy_bps':2})}</div>
    <div class='card'><h2>Artifact</h2><ul>
      <li><code>reports/artifacts/scout_rank96_advancedma_retest_count_15m/trade_log.csv</code></li>
      <li><code>reports/artifacts/scout_rank96_advancedma_retest_count_15m/asset_summary_primary_6bps.csv</code></li>
      <li><code>reports/artifacts/scout_rank96_advancedma_retest_count_15m/overall_summary.csv</code></li>
      <li><code>reports/artifacts/scout_rank96_advancedma_retest_count_15m/cost_summary.csv</code></li>
      <li><code>reports/artifacts/scout_rank96_advancedma_retest_count_15m/summary.json</code></li>
    </ul></div>
    """
    write_html(SITE_DIR / "report.html", "Rank 96 retest-count clean replication", html)
    write_html(READING_PATH, "Rank 96 retest-count clean replication", html)
    print(json.dumps({"generated_at_utc": generated_at, **verdict}, ensure_ascii=False))


if __name__ == "__main__":
    main()
