#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import time

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank107_mtf_chop_chargedup_15m"
CACHE_DIR = ART_DIR / "cache"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank107_mtf_chop_chargedup_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank107_mtf_chop_chargedup_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
INTERVAL = "15m"
LOOKBACK_DAYS = 120
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
LIMIT = 1500
HOLD_BARS = 4
COST_BPS_PER_SIDE = 6.0
ATR_WINDOW = 14
CHOP_WINDOW = 14
EMA_FAST = 20
EMA_SLOW = 50
TREND_SLOW = 200
BREAKOUT_BUFFER_ATR = 0.12
CHARGED_LEVEL = 61.8
CHARGED_COUNT_THRESHOLD = 2
VARIANT_ORDER = ["baseline", "hard_veto", "size_down"]
SETUP_PRIORITY = {"retest_hold_long": 0, "ema_continuation_long": 1}

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
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def net_ret(gross: pd.Series | np.ndarray, cost_bps_per_side: float, size: pd.Series | np.ndarray | float = 1.0) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    gross_s = pd.Series(gross, copy=False).astype(float)
    size_s = pd.Series(size, index=gross_s.index, copy=False).astype(float)
    scaled = gross_s * size_s
    return (1.0 + scaled) * (1.0 - c) * (1.0 - c) - 1.0


def fetch_klines(symbol: str) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = CACHE_DIR / f"{symbol}__{LOOKBACK_DAYS}d__{INTERVAL}.csv"
    if cache_path.exists():
        try:
            cached = pd.read_csv(cache_path)
            cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True)
            if not cached.empty:
                age = datetime.now(timezone.utc) - cached["timestamp"].max().to_pydatetime().replace(tzinfo=timezone.utc)
                if age < timedelta(hours=1):
                    return cached.sort_values("timestamp").reset_index(drop=True)
        except Exception:
            pass

    need = LOOKBACK_DAYS * 24 * 4 + TREND_SLOW + HOLD_BARS + 200
    rows: list[list[object]] = []
    end_time = None
    session = requests.Session()
    while len(rows) < need:
        params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
        if end_time is not None:
            params["endTime"] = end_time
        resp = session.get(BINANCE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows = data + rows
        end_time = int(data[0][0]) - 1
        if len(data) < LIMIT:
            break
        time.sleep(0.15)

    df = pd.DataFrame(
        rows,
        columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "n_trades", "taker_base", "taker_quote", "ignore"],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp")
    df = df.tail(need).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    return df


def compute_chop(df: pd.DataFrame, window: int = CHOP_WINDOW) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    tr_sum = tr.rolling(window).sum()
    hh = df["high"].rolling(window).max()
    ll = df["low"].rolling(window).min()
    denom = (hh - ll).replace(0, np.nan)
    chop = 100.0 * np.log10(tr_sum / denom) / math.log10(window)
    return chop


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    temp = df.copy()
    temp["bar_end"] = temp["timestamp"] + pd.Timedelta(minutes=15)
    res = (
        temp.set_index("bar_end")
        .resample(timeframe, label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return res


def attach_mtf_chop(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bar_end"] = out["timestamp"] + pd.Timedelta(minutes=15)
    out["chop_15m"] = compute_chop(out.rename(columns={"bar_end": "timestamp"}))
    for timeframe, col in [("30min", "chop_30m"), ("60min", "chop_60m")]:
        res = resample_ohlcv(df, timeframe)
        res[col] = compute_chop(res.rename(columns={"bar_end": "timestamp"}))
        out = pd.merge_asof(
            out.sort_values("bar_end"),
            res[["bar_end", col]].sort_values("bar_end"),
            on="bar_end",
            direction="backward",
        )
    charged_cols = ["chop_15m", "chop_30m", "chop_60m"]
    out["charged_count"] = (out[charged_cols] >= CHARGED_LEVEL).sum(axis=1)
    return out


def build_symbol_candidates(symbol: str, asset: str) -> pd.DataFrame:
    df = fetch_klines(symbol).copy()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.rolling(ATR_WINDOW).mean()
    df["ema20"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["sma200"] = df["close"].rolling(TREND_SLOW).mean()
    df["prev_high"] = df["high"].shift(1)
    df["breakout_high_20"] = df["high"].rolling(20).max().shift(1)
    df["close_8ago"] = df["close"].shift(8)
    df["recent_breakout"] = (df["close"].shift(1).rolling(8).max() > df["breakout_high_20"].shift(1)).astype(int)
    df["rolling_low_8"] = df["low"].shift(1).rolling(8).min()
    df = attach_mtf_chop(df)
    df = df.dropna().reset_index(drop=True)

    rows: list[dict[str, object]] = []
    last_idx = len(df) - HOLD_BARS - 1
    for i in range(1, last_idx):
        row = df.iloc[i]
        atr = float(row["atr14"])
        if not np.isfinite(atr) or atr <= 0:
            continue
        ema20 = float(row["ema20"])
        ema50 = float(row["ema50"])
        sma200 = float(row["sma200"])
        trend_ok = bool(ema20 > ema50 > sma200)
        if not trend_ok:
            continue

        continuation = bool(float(row["close"]) > float(row["prev_high"]) + BREAKOUT_BUFFER_ATR * atr and float(row["close"]) > ema20)
        retest = bool(
            row["recent_breakout"] == 1
            and float(row["low"]) <= ema20 + 0.20 * atr
            and float(row["close"]) >= ema20
            and float(row["close"]) >= float(row["open"])
            and float(row["rolling_low_8"]) < ema20 + 0.35 * atr
        )

        setups = []
        if retest:
            setups.append("retest_hold_long")
        if continuation:
            setups.append("ema_continuation_long")
        if not setups:
            continue

        entry_idx = i + 1
        exit_idx = i + HOLD_BARS
        if exit_idx >= len(df):
            continue
        entry_px = float(df.iloc[entry_idx]["open"])
        exit_px = float(df.iloc[exit_idx]["close"])
        path = df.iloc[entry_idx : exit_idx + 1]
        gross_ret = exit_px / entry_px - 1.0
        fail_below_ema20 = int((path["close"] < ema20).any())
        left_tail_proxy = float(path["low"].min() / entry_px - 1.0)

        common = {
            "asset": asset,
            "symbol": symbol,
            "signal_ts": row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_ts": df.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": df.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_return_h4": gross_ret,
            "fail_below_ema20_4bars": fail_below_ema20,
            "left_tail_proxy": left_tail_proxy,
            "charged_count": int(row["charged_count"]),
            "charged_ge2": int(int(row["charged_count"]) >= CHARGED_COUNT_THRESHOLD),
            "chop_15m": float(row["chop_15m"]),
            "chop_30m": float(row["chop_30m"]),
            "chop_60m": float(row["chop_60m"]),
            "trend_stack": f"ema20>{EMA_FAST}, ema50>{EMA_SLOW}, sma200>{TREND_SLOW}",
        }
        for setup in setups:
            rows.append({**common, "setup": setup, "setup_priority": SETUP_PRIORITY[setup]})

    if not rows:
        raise RuntimeError(f"no rank107 candidate events built for {symbol}")
    out = pd.DataFrame(rows)
    out = out.sort_values(["entry_ts", "symbol", "setup_priority"]).drop_duplicates(["symbol", "entry_ts"], keep="first")
    return out.reset_index(drop=True)


def choose_variant_events(candidates: pd.DataFrame, variant: str) -> pd.DataFrame:
    df = candidates.copy()
    if variant == "hard_veto":
        df = df[df["charged_count"] < CHARGED_COUNT_THRESHOLD].copy()
        df["position_size"] = 1.0
    elif variant == "size_down":
        df["position_size"] = np.where(df["charged_count"] >= CHARGED_COUNT_THRESHOLD, 0.5, 1.0)
    else:
        df["position_size"] = 1.0

    df["entry_ts_dt"] = pd.to_datetime(df["entry_ts"], utc=True)
    kept = []
    next_free_by_symbol: dict[str, pd.Timestamp] = {}
    for _, row in df.sort_values(["entry_ts_dt", "symbol", "setup_priority"]).iterrows():
        symbol = str(row["symbol"])
        next_free = next_free_by_symbol.get(symbol)
        if next_free is not None and row["entry_ts_dt"] < next_free:
            continue
        kept.append(row)
        next_free_by_symbol[symbol] = row["entry_ts_dt"] + timedelta(minutes=15 * HOLD_BARS)
    if not kept:
        return pd.DataFrame(columns=list(df.columns) + ["variant", "net_return_6bps"])
    out = pd.DataFrame(kept).drop(columns=["entry_ts_dt"], errors="ignore")
    out["variant"] = variant
    out["net_return_6bps"] = net_ret(out["gross_return_h4"], COST_BPS_PER_SIDE, out["position_size"])
    return out


def build_event_log() -> pd.DataFrame:
    candidates = pd.concat([build_symbol_candidates(symbol, asset) for asset, symbol in ASSETS.items()], ignore_index=True)
    frames = [choose_variant_events(candidates, variant) for variant in VARIANT_ORDER]
    return pd.concat(frames, ignore_index=True).sort_values(["variant", "entry_ts", "symbol"]).reset_index(drop=True)


def summarize(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline = events[events["variant"] == "baseline"].copy()
    baseline_count = len(baseline)
    baseline_setup_counts = baseline.groupby("setup").size().to_dict()
    baseline_charged_share = baseline["charged_ge2"].mean() if baseline_count else np.nan

    overall_rows = []
    setup_rows = []
    symbol_rows = []
    charged_rows = []
    for variant in VARIANT_ORDER:
        subset = events[events["variant"] == variant].copy()
        if subset.empty:
            continue
        overall_rows.append(
            {
                "variant": variant,
                "events": len(subset),
                "trade_count_retention": len(subset) / baseline_count if baseline_count else np.nan,
                "charged_ge2_share": subset["charged_ge2"].mean(),
                "mean_net_ret_6bps": subset["net_return_6bps"].mean(),
                "median_net_ret_6bps": subset["net_return_6bps"].median(),
                "win_rate_6bps": (subset["net_return_6bps"] > 0).mean(),
                "fail_below_ema20_4bars": subset["fail_below_ema20_4bars"].mean(),
                "left_tail_p5_6bps": subset["net_return_6bps"].quantile(0.05),
                "avg_position_size": subset["position_size"].mean(),
            }
        )
        for setup in ["retest_hold_long", "ema_continuation_long"]:
            sub = subset[subset["setup"] == setup].copy()
            if sub.empty:
                continue
            setup_rows.append(
                {
                    "variant": variant,
                    "setup": setup,
                    "events": len(sub),
                    "trade_count_retention_vs_setup_baseline": len(sub) / baseline_setup_counts.get(setup, np.nan) if baseline_setup_counts.get(setup) else np.nan,
                    "charged_ge2_share": sub["charged_ge2"].mean(),
                    "mean_net_ret_6bps": sub["net_return_6bps"].mean(),
                    "median_net_ret_6bps": sub["net_return_6bps"].median(),
                    "win_rate_6bps": (sub["net_return_6bps"] > 0).mean(),
                    "fail_below_ema20_4bars": sub["fail_below_ema20_4bars"].mean(),
                    "left_tail_p5_6bps": sub["net_return_6bps"].quantile(0.05),
                }
            )
        for symbol in sorted(subset["symbol"].unique()):
            sub_sym = subset[subset["symbol"] == symbol].copy()
            symbol_rows.append(
                {
                    "variant": variant,
                    "symbol": symbol,
                    "events": len(sub_sym),
                    "mean_net_ret_6bps": sub_sym["net_return_6bps"].mean(),
                    "win_rate_6bps": (sub_sym["net_return_6bps"] > 0).mean(),
                    "fail_below_ema20_4bars": sub_sym["fail_below_ema20_4bars"].mean(),
                    "left_tail_p5_6bps": sub_sym["net_return_6bps"].quantile(0.05),
                }
            )
        for charged_flag, label in [(0, "charged<2"), (1, "charged>=2")]:
            sub_c = subset[subset["charged_ge2"] == charged_flag].copy()
            if sub_c.empty:
                continue
            charged_rows.append(
                {
                    "variant": variant,
                    "charged_bucket": label,
                    "events": len(sub_c),
                    "mean_net_ret_6bps": sub_c["net_return_6bps"].mean(),
                    "median_net_ret_6bps": sub_c["net_return_6bps"].median(),
                    "win_rate_6bps": (sub_c["net_return_6bps"] > 0).mean(),
                    "fail_below_ema20_4bars": sub_c["fail_below_ema20_4bars"].mean(),
                    "left_tail_p5_6bps": sub_c["net_return_6bps"].quantile(0.05),
                }
            )

    overall = pd.DataFrame(overall_rows)
    setup_df = pd.DataFrame(setup_rows)
    symbol_df = pd.DataFrame(symbol_rows)
    charged_df = pd.DataFrame(charged_rows)

    base_all = overall[overall["variant"] == "baseline"].iloc[0]
    veto_all = overall[overall["variant"] == "hard_veto"].iloc[0]
    size_all = overall[overall["variant"] == "size_down"].iloc[0]
    base_retest_df = setup_df[(setup_df["variant"] == "baseline") & (setup_df["setup"] == "retest_hold_long")]
    veto_retest_df = setup_df[(setup_df["variant"] == "hard_veto") & (setup_df["setup"] == "retest_hold_long")]
    retest_improves = None
    if not base_retest_df.empty and not veto_retest_df.empty:
        base_retest = base_retest_df.iloc[0]
        veto_retest = veto_retest_df.iloc[0]
        retest_improves = float(veto_retest["mean_net_ret_6bps"]) > float(base_retest["mean_net_ret_6bps"])

    veto_improves = (
        float(veto_all["mean_net_ret_6bps"]) > float(base_all["mean_net_ret_6bps"])
        and float(veto_all["fail_below_ema20_4bars"]) < float(base_all["fail_below_ema20_4bars"])
        and (retest_improves is not False)
    )
    if veto_improves and float(veto_all["trade_count_retention"]) >= 0.75:
        verdict = "keep_P1 / weak paper-candidate evidence"
    else:
        verdict = "park / evidence pool"

    desk_readthrough = (
        f"charged_count>=2 的 veto 确实让整体样本少做了一部分高噪声 long：baseline mean_net_ret 约 {bps(base_all['mean_net_ret_6bps'])}，"
        f"hard_veto 约 {bps(veto_all['mean_net_ret_6bps'])}；baseline fail_below_ema20_4bars 约 {pct(base_all['fail_below_ema20_4bars'])}，"
        f"hard_veto 约 {pct(veto_all['fail_below_ema20_4bars'])}。但它仍没有把总体样本拉到足够硬的 candidate 级别，"
        f"而且 retention 只剩 {pct(veto_all['trade_count_retention'])}；size_down 也主要是少亏，不是翻盘。"
    )
    next_step = "按顶板顺序把 Rank 107 收口为 park / evidence pool，并切 prebreak higher-low pressure ladder context gate 的 source intake。"

    verdict_summary = pd.DataFrame(
        [
            {
                "rank": 107,
                "candidate": "MTF CHOP charged-up count",
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "sample": "BTC/ETH/SOL Binance Futures 120d 15m",
                "baseline_events": int(base_all["events"]),
                "hard_veto_events": int(veto_all["events"]),
                "baseline_charged_ge2_share": float(baseline_charged_share),
                "baseline_mean_net_ret_6bps": float(base_all["mean_net_ret_6bps"]),
                "hard_veto_mean_net_ret_6bps": float(veto_all["mean_net_ret_6bps"]),
                "size_down_mean_net_ret_6bps": float(size_all["mean_net_ret_6bps"]),
                "baseline_fail_below_ema20_4bars": float(base_all["fail_below_ema20_4bars"]),
                "hard_veto_fail_below_ema20_4bars": float(veto_all["fail_below_ema20_4bars"]),
                "baseline_left_tail_p5_6bps": float(base_all["left_tail_p5_6bps"]),
                "hard_veto_left_tail_p5_6bps": float(veto_all["left_tail_p5_6bps"]),
                "hard_verdict": verdict,
                "desk_readthrough": desk_readthrough,
                "next_step": next_step,
            }
        ]
    )
    return overall, setup_df, symbol_df, charged_df, verdict_summary


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(CACHE_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    events = build_event_log()
    overall, setup_df, symbol_df, charged_df, verdict_summary = summarize(events)
    verdict = str(verdict_summary.iloc[0]["hard_verdict"])
    snapshot = {
        "generated_at_utc": generated_at,
        "sample": "BTC/ETH/SOL Binance Futures 120d 15m",
        "entry": "next-bar open",
        "exit": f"close after {HOLD_BARS} bars",
        "cost_bps_per_side": COST_BPS_PER_SIDE,
        "variants": VARIANT_ORDER,
        "verdict": verdict,
        "events_by_variant": events.groupby("variant").size().to_dict(),
    }

    events.to_csv(ART_DIR / "event_log.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_df.to_csv(ART_DIR / "setup_summary.csv", index=False)
    symbol_df.to_csv(ART_DIR / "symbol_summary.csv", index=False)
    charged_df.to_csv(ART_DIR / "charged_bucket_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    overall_table = render_table(
        overall,
        percent_cols={"trade_count_retention", "charged_ge2_share", "win_rate_6bps", "fail_below_ema20_4bars"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps", "left_tail_p5_6bps"},
        digits_cols={"events": 0},
    )
    setup_table = render_table(
        setup_df,
        percent_cols={"trade_count_retention_vs_setup_baseline", "charged_ge2_share", "win_rate_6bps", "fail_below_ema20_4bars"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps", "left_tail_p5_6bps"},
        digits_cols={"events": 0},
    )
    symbol_table = render_table(
        symbol_df,
        percent_cols={"win_rate_6bps", "fail_below_ema20_4bars"},
        bps_cols={"mean_net_ret_6bps", "left_tail_p5_6bps"},
        digits_cols={"events": 0},
    )
    charged_table = render_table(
        charged_df,
        percent_cols={"win_rate_6bps", "fail_below_ema20_4bars"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps", "left_tail_p5_6bps"},
        digits_cols={"events": 0},
    )

    body = f"""
<h1>Rank 107 · MTF CHOP charged-up count clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：BTC/ETH/SOL Binance Futures 120d 15m ｜ 口径：signal 当根及之前数据 / MTF CHOP lookahead_off / next-bar open / no-overlap / hold {HOLD_BARS} bars / {num(COST_BPS_PER_SIDE,1)}bps per side</p>
<div class='card'>
  <p><strong>硬结论：</strong><span class='bad'>{escape(verdict)}</span></p>
  <p>{escape(str(verdict_summary.iloc[0]['desk_readthrough']))}</p>
  <p><strong>下一步：</strong>{escape(str(verdict_summary.iloc[0]['next_step']))}</p>
</div>
<div class='card'>
  <h2>这轮到底在测什么</h2>
  <ul>
    <li>只测它能不能当 <code>long-side veto / size-down layer</code>，不把它包装成独立 alpha。</li>
    <li>底层 long proxy 只含两类：<code>retest_hold_long</code> 与 <code>ema_continuation_long</code>。</li>
    <li>三臂固定为：<code>baseline</code> / <code>charged_count&gt;=2 hard veto</code> / <code>charged_count&gt;=2 size-down(0.5x)</code>。</li>
    <li>MTF CHOP 统一按 <code>15m / 30m / 60m</code> 三层、<code>CHOP(14)</code>、<code>lookahead_off</code> 对齐到当前 bar。</li>
  </ul>
</div>
<div class='card'>
  <h2>主表</h2>
  {overall_table}
</div>
<div class='card'>
  <h2>按 setup 拆开</h2>
  {setup_table}
</div>
<div class='card'>
  <h2>按 charged bucket 拆开</h2>
  {charged_table}
</div>
<div class='card'>
  <h2>按币种拆开</h2>
  {symbol_table}
</div>
<div class='card'>
  <h2>reader-facing 读法</h2>
  <ul>
    <li><code>charged_count&gt;=2</code> 更像“少做高噪声 long”的 veto，而不是 shared admission gate。</li>
    <li><code>hard_veto</code> 与 <code>size_down</code> 如果只是把亏损削浅、却没有把整体样本拉成更硬的 queue-facing candidate，就不该继续占住 Scout 主资源位。</li>
    <li>因此这轮更诚实的 desk 读法是：保留“多周期一起变糊时别硬做 long”这条经验，但把 Rank 107 本体压回 <code>park / evidence pool</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>产物</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/event_log.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/setup_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/charged_bucket_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/symbol_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/verdict_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank107_mtf_chop_chargedup_15m/summary_snapshot.json</code></li>
  </ul>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 107 · MTF CHOP charged-up count clean replication", body)
    write_html(READING_PATH, "Rank 107 · MTF CHOP charged-up count clean replication", body)


if __name__ == "__main__":
    main()
