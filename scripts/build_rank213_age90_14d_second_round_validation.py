#!/usr/bin/env python3
from __future__ import annotations

import json
import io
import zipfile
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_14d_second_round_validation.html"

DAILY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_daily.csv"
PRICE_DIR = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "daily_1d"
RAW_1D_DIR = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "raw_1d"

SUMMARY_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_summary.json"
COST_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_cost_sensitivity.csv"
FOLD_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_time_folds.csv"
MONTHLY_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_monthly.csv"
ROLLING_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_rolling_windows.csv"
LEG_DAILY_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_leg_daily.csv"
SYMBOL_ATTR_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_symbol_attribution.csv"
RISK_GATE_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_simple_risk_gates.csv"
EXECUTION_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_execution_timing.csv"
EXECUTION_DAILY_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_execution_timing_daily.csv"

STRATEGY = "age90_14d_skip1d_voladj"
BASE_COST_BPS = 4.0
COST_GRID_BPS = [0, 4, 8, 12, 16, 20]


def fmt_pct(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}%"
    except (TypeError, ValueError):
        return ""


def fmt_bps(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f} bps"
    except (TypeError, ValueError):
        return ""


def compound(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    return float((1.0 + ret).prod() - 1.0) if len(ret) else np.nan


def max_drawdown(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def stats(df: pd.DataFrame, ret_col: str = "net_ret") -> dict:
    ret = pd.to_numeric(df[ret_col], errors="coerce").fillna(0.0)
    active = (
        pd.to_numeric(df["active"], errors="coerce").fillna(0).astype(bool)
        if "active" in df.columns
        else pd.Series(True, index=df.index)
    )
    return {
        "rows": int(len(df)),
        "trading_baskets": int(active.sum()),
        "net_mean_bps": float(ret.mean() * 10000.0) if len(df) else np.nan,
        "net_cum_pct": float(compound(ret) * 100.0) if len(df) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(df) else np.nan,
        "win_rate_pct": float((ret > 0).mean() * 100.0) if len(df) else np.nan,
    }


def read_daily() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PATH)
    df = df[df["strategy"] == STRATEGY].copy()
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True, format="mixed")
    df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True, format="mixed")
    df["gross_ret"] = pd.to_numeric(df["gross_ret"], errors="coerce")
    df["net_ret"] = pd.to_numeric(df["net_ret"], errors="coerce")
    df["active"] = df["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    df = df.dropna(subset=["timestamp_ts", "exit_ts", "gross_ret", "net_ret"])
    return df.sort_values("timestamp_ts").reset_index(drop=True)


def read_price(symbol: str) -> pd.Series | None:
    path = PRICE_DIR / f"{symbol}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, usecols=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce", format="mixed")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
    if df.empty:
        return None
    return df.set_index("timestamp")["close"]


def read_raw_ohlc(symbol: str) -> pd.DataFrame | None:
    paths = []
    for bucket in ["monthly", "daily"]:
        base = RAW_1D_DIR / bucket / symbol
        if base.exists():
            paths.extend(sorted(base.glob(f"{symbol}-1d-*.zip")))
    if not paths:
        return None

    frames = []
    names = [
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trade_count", "taker_base", "taker_quote", "ignore",
    ]
    for path in paths:
        try:
            with zipfile.ZipFile(path) as zf:
                members = zf.namelist()
                if not members:
                    continue
                data = zf.read(members[0])
            part = pd.read_csv(io.BytesIO(data), header=None, names=names)
        except Exception:
            continue
        part["open_time"] = pd.to_numeric(part["open_time"], errors="coerce")
        for col in ["open", "high", "low", "close"]:
            part[col] = pd.to_numeric(part[col], errors="coerce")
        part = part.dropna(subset=["open_time", "open", "close"])
        if part.empty:
            continue
        frames.append(pd.DataFrame({
            "timestamp": pd.to_datetime(part["open_time"].astype("int64"), unit="ms", utc=True),
            "open": part["open"].astype(float),
            "high": part["high"].astype(float),
            "low": part["low"].astype(float),
            "close": part["close"].astype(float),
        }))
    if not frames:
        return None
    out = pd.concat(frames, ignore_index=True).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    return out.set_index("timestamp")


def build_leg_attribution(daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    cache: dict[str, pd.Series | None] = {}
    daily_rows: list[dict] = []
    sym_rows: list[dict] = []
    missing = 0
    total_legs = 0

    for _, row in daily.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        longs = [x for x in str(row["longs"]).split(",") if x]
        shorts = [x for x in str(row["shorts"]).split(",") if x]
        long_rets: list[float] = []
        short_rets: list[float] = []
        for side, symbols in [("long", longs), ("short", shorts)]:
            for symbol in symbols:
                total_legs += 1
                if symbol not in cache:
                    cache[symbol] = read_price(symbol)
                ser = cache[symbol]
                if ser is None or ts not in ser.index or exit_ts not in ser.index:
                    missing += 1
                    continue
                raw = float(ser.loc[exit_ts] / ser.loc[ts] - 1.0)
                contrib = raw if side == "long" else -raw
                weighted = contrib / 6.0
                if side == "long":
                    long_rets.append(raw)
                else:
                    short_rets.append(-raw)
                sym_rows.append({
                    "timestamp_ts": ts,
                    "symbol": symbol,
                    "side": side,
                    "raw_ret": raw,
                    "contrib_ret": contrib,
                    "weighted_contrib_ret": weighted,
                })
        long_leg = float(np.mean(long_rets)) if long_rets else np.nan
        short_leg = float(np.mean(short_rets)) if short_rets else np.nan
        gross_rebuilt = 0.5 * long_leg + 0.5 * short_leg if np.isfinite(long_leg) and np.isfinite(short_leg) else np.nan
        daily_rows.append({
            "timestamp_ts": ts,
            "long_leg_ret": long_leg,
            "short_leg_ret": short_leg,
            "gross_rebuilt": gross_rebuilt,
            "gross_original": float(row["gross_ret"]),
            "gross_diff": gross_rebuilt - float(row["gross_ret"]) if np.isfinite(gross_rebuilt) else np.nan,
        })

    leg_daily = pd.DataFrame(daily_rows)
    sym = pd.DataFrame(sym_rows)
    if sym.empty:
        symbol_attr = pd.DataFrame(columns=["symbol", "side", "legs", "avg_weighted_contrib_bps", "sum_weighted_contrib_pct", "win_rate_pct"])
    else:
        symbol_attr = (
            sym.groupby(["symbol", "side"], as_index=False)
            .agg(
                legs=("weighted_contrib_ret", "size"),
                avg_weighted_contrib_bps=("weighted_contrib_ret", lambda s: float(s.mean() * 10000.0)),
                sum_weighted_contrib_pct=("weighted_contrib_ret", lambda s: float(s.sum() * 100.0)),
                win_rate_pct=("contrib_ret", lambda s: float((s > 0).mean() * 100.0)),
            )
            .sort_values("sum_weighted_contrib_pct", ascending=False)
        )
    meta = {
        "total_legs": int(total_legs),
        "missing_price_legs": int(missing),
        "leg_price_coverage_pct": float((total_legs - missing) / total_legs * 100.0) if total_legs else np.nan,
    }
    return leg_daily, symbol_attr, meta


def build_cost_sensitivity(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost in COST_GRID_BPS:
        work = daily.copy()
        work["net_ret_scenario"] = work["gross_ret"] - cost / 10000.0
        rows.append({"cost_bps_per_basket": cost, **stats(work, "net_ret_scenario")})
    return pd.DataFrame(rows)


def build_folds(daily: pd.DataFrame) -> pd.DataFrame:
    folds = [
        ("2020-2021", "2020-01-01", "2021-12-31"),
        ("2022-2023", "2022-01-01", "2023-12-31"),
        ("2024-2026", "2024-01-01", "2026-12-31"),
        ("2024", "2024-01-01", "2024-12-31"),
        ("2025", "2025-01-01", "2025-12-31"),
        ("2026 YTD", "2026-01-01", "2026-12-31"),
    ]
    rows = []
    ts = daily["timestamp_ts"]
    for label, start, end in folds:
        mask = (ts >= pd.Timestamp(start, tz="UTC")) & (ts <= pd.Timestamp(end, tz="UTC"))
        sub = daily[mask].copy()
        rows.append({"fold": label, **stats(sub)})
    return pd.DataFrame(rows)


def build_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month, sub in daily.groupby("month"):
        st = stats(sub)
        rows.append({"month": str(month), **st})
    out = pd.DataFrame(rows).sort_values("month").reset_index(drop=True)
    total_log = float(np.log1p(pd.to_numeric(daily["net_ret"], errors="coerce").fillna(0.0)).sum())
    out["month_log_ret"] = out["net_cum_pct"].apply(lambda x: float(np.log1p(float(x) / 100.0)) if pd.notna(x) else np.nan)
    out["share_of_total_log_return_pct"] = out["month_log_ret"] / total_log * 100.0 if total_log else np.nan
    return out


def build_rolling(monthly: pd.DataFrame) -> pd.DataFrame:
    rows = []
    monthly = monthly.copy()
    monthly["month_ret"] = monthly["net_cum_pct"] / 100.0
    for window in [6, 12, 24]:
        for i in range(window - 1, len(monthly)):
            sub = monthly.iloc[i - window + 1:i + 1]
            ret = sub["month_ret"]
            rows.append({
                "window_months": window,
                "end_month": sub.iloc[-1]["month"],
                "net_cum_pct": float(compound(ret) * 100.0),
                "positive_month_rate_pct": float((ret > 0).mean() * 100.0),
                "worst_month_net_pct": float(sub["net_cum_pct"].min()),
                "avg_monthly_net_pct": float(sub["net_cum_pct"].mean()),
            })
    return pd.DataFrame(rows)


def build_simple_risk_gates(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.sort_values("timestamp_ts").copy()
    ret = work["net_ret"].reset_index(drop=True)

    def trailing_comp(window: int) -> pd.Series:
        vals = []
        for i in range(len(ret)):
            hist = ret.iloc[max(0, i - window):i]
            vals.append(compound(hist) if len(hist) == window else np.nan)
        return pd.Series(vals, index=work.index)

    gates = {
        "trade_all_reference": pd.Series(True, index=work.index),
        "prior_30d_return_positive": trailing_comp(30) > 0,
        "prior_60d_return_positive": trailing_comp(60) > 0,
        "prior_30d_return_above_minus5pct": trailing_comp(30) > -0.05,
    }
    rows = []
    for name, mask in gates.items():
        sub = work[mask.fillna(False)].copy()
        skipped = int((~mask.fillna(False)).sum())
        rows.append({
            "gate": name,
            "skipped_days": skipped,
            "active_rate_pct": float(mask.fillna(False).mean() * 100.0),
            **stats(sub),
        })
    return pd.DataFrame(rows)


def build_execution_timing(daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cache: dict[str, pd.DataFrame | None] = {}
    scenarios = {
        "paper_raw_close_to_close": ("timestamp_ts", "exit_ts", "close"),
        "same_day_open_to_next_open": ("timestamp_ts", "exit_ts", "open"),
        "delayed_next_open_to_following_open": ("exit_ts", "next_next_ts", "open"),
    }
    rows: list[dict] = []

    for _, row in daily.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        next_next_ts = exit_ts + pd.Timedelta(days=1)
        longs = [x for x in str(row["longs"]).split(",") if x]
        shorts = [x for x in str(row["shorts"]).split(",") if x]
        for scenario, (entry_key, exit_key, px_col) in scenarios.items():
            entry_ts = row[entry_key] if entry_key in row else locals()[entry_key]
            out_ts = row[exit_key] if exit_key in row else locals()[exit_key]
            long_rets: list[float] = []
            short_rets: list[float] = []
            missing = 0
            total = 0
            for side, symbols in [("long", longs), ("short", shorts)]:
                for symbol in symbols:
                    total += 1
                    if symbol not in cache:
                        cache[symbol] = read_raw_ohlc(symbol)
                    ohlc = cache[symbol]
                    if ohlc is None or entry_ts not in ohlc.index or out_ts not in ohlc.index:
                        missing += 1
                        continue
                    entry = float(ohlc.at[entry_ts, px_col])
                    out = float(ohlc.at[out_ts, px_col])
                    if not np.isfinite(entry) or not np.isfinite(out) or entry <= 0:
                        missing += 1
                        continue
                    raw = out / entry - 1.0
                    if side == "long":
                        long_rets.append(raw)
                    else:
                        short_rets.append(-raw)
            long_leg = float(np.mean(long_rets)) if long_rets else np.nan
            short_leg = float(np.mean(short_rets)) if short_rets else np.nan
            gross = 0.5 * long_leg + 0.5 * short_leg if np.isfinite(long_leg) and np.isfinite(short_leg) else np.nan
            rows.append({
                "timestamp_ts": ts,
                "scenario": scenario,
                "entry_ts": entry_ts,
                "exit_ts": out_ts,
                "price_col": px_col,
                "total_legs": total,
                "missing_legs": missing,
                "coverage_pct": float((total - missing) / total * 100.0) if total else np.nan,
                "long_leg_ret": long_leg,
                "short_leg_ret": short_leg,
                "gross_ret": gross,
                "net_ret": gross - BASE_COST_BPS / 10000.0 if np.isfinite(gross) else np.nan,
            })

    detail = pd.DataFrame(rows)
    summary_rows = []
    for scenario, sub in detail.groupby("scenario"):
        valid = sub.dropna(subset=["net_ret"]).copy()
        summary_rows.append({
            "scenario": scenario,
            "valid_days": int(len(valid)),
            "avg_coverage_pct": float(sub["coverage_pct"].mean()) if len(sub) else np.nan,
            **stats(valid),
        })
    order = {
        "paper_raw_close_to_close": 0,
        "same_day_open_to_next_open": 1,
        "delayed_next_open_to_following_open": 2,
    }
    summary = pd.DataFrame(summary_rows)
    summary["_order"] = summary["scenario"].map(order).fillna(99)
    summary = summary.sort_values(["_order", "scenario"]).drop(columns=["_order"]).reset_index(drop=True)
    return summary, detail


def table_html(df: pd.DataFrame, cols: list[str]) -> str:
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row.get(c, "")
            if c.endswith("_pct"):
                txt = fmt_pct(v)
            elif c.endswith("_bps"):
                txt = fmt_bps(v)
            elif isinstance(v, float):
                txt = f"{v:.4f}"
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def equity_svg(daily: pd.DataFrame) -> str:
    work = daily.sort_values("timestamp_ts").copy()
    work["equity"] = (1.0 + work["net_ret"]).cumprod()
    width, height = 1100, 360
    left, right, top, bottom = 70, 25, 30, 54
    plot_w = width - left - right
    plot_h = height - top - bottom
    ts_min = work["timestamp_ts"].min()
    ts_max = work["timestamp_ts"].max()
    x_span = max((ts_max - ts_min).total_seconds(), 1.0)
    y = np.log(work["equity"].clip(lower=1e-6))
    y_min, y_max = float(y.min()), float(y.max())
    if y_max <= y_min:
        y_max = y_min + 1.0

    def xy(ts: pd.Timestamp, eq: float) -> tuple[float, float]:
        x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
        yy = top + (1.0 - ((np.log(max(eq, 1e-6)) - y_min) / (y_max - y_min))) * plot_h
        return x, yy

    pts = [xy(r["timestamp_ts"], float(r["equity"])) for _, r in work.iterrows()]
    path = " ".join(("M" if i == 0 else "L") + f"{x:.2f},{yy:.2f}" for i, (x, yy) in enumerate(pts))
    grid = []
    for eq in [0.5, 1, 2, 5]:
        yy = top + (1.0 - ((np.log(eq) - y_min) / (y_max - y_min))) * plot_h
        if top <= yy <= top + plot_h:
            grid.append(f"<line x1='{left}' y1='{yy:.1f}' x2='{width-right}' y2='{yy:.1f}' stroke='#e2e8f0'/><text x='{left-8}' y='{yy+4:.1f}' text-anchor='end'>{eq:.1f}x</text>")
    years = []
    for year in range(ts_min.year, ts_max.year + 1):
        ts = pd.Timestamp(f"{year}-01-01T00:00:00Z")
        if ts_min <= ts <= ts_max:
            x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
            years.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{top+plot_h}' stroke='#f1f5f9'/><text x='{x:.1f}' y='{height-30}' text-anchor='middle'>{year}</text>")
    return f"""
<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="age90 14d equity curve">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="13" fill="#475569">
    {''.join(grid)}
    {''.join(years)}
    <line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <path d="{path}" fill="none" stroke="#2563eb" stroke-width="2.6"/>
    <text x="{left}" y="20" font-size="15" font-weight="700" fill="#172033">age90_14d_skip1d_voladj equity（log scale）</text>
  </g>
</svg>
"""


def monthly_bar_svg(monthly: pd.DataFrame) -> str:
    width, height = 1100, 360
    left, right, top, bottom = 55, 20, 28, 68
    plot_w = width - left - right
    plot_h = height - top - bottom
    vals = pd.to_numeric(monthly["net_cum_pct"], errors="coerce").fillna(0.0)
    vmin = min(float(vals.min()), 0.0)
    vmax = max(float(vals.max()), 0.0)
    span = max(vmax - vmin, 1.0)
    zero_y = top + (vmax / span) * plot_h
    bw = plot_w / max(len(monthly), 1)
    bars = []
    labels = []
    for i, (_, r) in enumerate(monthly.iterrows()):
        val = float(r["net_cum_pct"])
        x = left + i * bw + 1
        y = top + ((vmax - max(val, 0)) / span) * plot_h
        h = abs(val) / span * plot_h
        if val < 0:
            y = zero_y
        color = "#16a34a" if val >= 0 else "#ea580c"
        bars.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{max(bw-2,1):.1f}' height='{max(h,1):.1f}' fill='{color}' opacity='0.82'/>")
        if str(r["month"]).endswith("-01"):
            labels.append(f"<text x='{x:.1f}' y='{height-34}' transform='rotate(45 {x:.1f},{height-34})'>{escape(str(r['month'])[:4])}</text>")
    return f"""
<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="monthly returns">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="12" fill="#475569">
    <line x1="{left}" y1="{zero_y:.1f}" x2="{width-right}" y2="{zero_y:.1f}" stroke="#0f172a" stroke-width="1"/>
    {''.join(bars)}
    {''.join(labels)}
    <text x="{left}" y="20" font-size="15" font-weight="700" fill="#172033">逐月净收益（绿色正、橙色负）</text>
  </g>
</svg>
"""


def build_report(
    daily: pd.DataFrame,
    cost: pd.DataFrame,
    folds: pd.DataFrame,
    monthly: pd.DataFrame,
    rolling: pd.DataFrame,
    leg_daily: pd.DataFrame,
    symbol_attr: pd.DataFrame,
    risk_gates: pd.DataFrame,
    execution: pd.DataFrame,
    leg_meta: dict,
) -> str:
    base = stats(daily)
    positive_month_rate = float((monthly["net_cum_pct"] > 0).mean() * 100.0)
    top_months = monthly.sort_values("month_log_ret", ascending=False).head(6)
    worst_months = monthly.sort_values("month_log_ret", ascending=True).head(6)
    long_mean = float(leg_daily["long_leg_ret"].mean() * 10000.0)
    short_mean = float(leg_daily["short_leg_ret"].mean() * 10000.0)
    long_cum = float(compound(0.5 * leg_daily["long_leg_ret"]) * 100.0)
    short_cum = float(compound(0.5 * leg_daily["short_leg_ret"]) * 100.0)
    top_symbols = symbol_attr.head(12)
    bad_symbols = symbol_attr.tail(12).sort_values("sum_weighted_contrib_pct", ascending=True)
    exec_notes = {
        "paper_raw_close_to_close": "用 raw zip 的 close 重建原始 close-to-close，主要验证缓存口径。",
        "same_day_open_to_next_open": "假设信号在当天开盘前已可用，按 open-to-open 成交。",
        "delayed_next_open_to_following_open": "信号延迟一天后再按 open-to-open 成交，测试 alpha 衰减。",
    }
    generated = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 age90 14d 二轮验证</title>
  <style>
    body {{ margin:0; background:#f5f1e8; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.65; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 16px 52px; }}
    .card {{ background:#fff; border:1px solid #e6dccb; border-radius:16px; padding:18px 20px; margin:14px 0; box-shadow:0 1px 2px rgba(20,24,31,.04); }}
    .hero {{ background:linear-gradient(135deg,#fff7ed,#fff 58%,#e0f2fe); border-color:#fdba74; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#bbf7d0; }}
    .muted {{ color:#64748b; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:900px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:14px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2) {{ text-align:left; }}
    .chart {{ width:100%; height:auto; border:1px solid #e2e8f0; border-radius:18px; background:#fff; margin:8px 0; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>age90_14d_skip1d_voladj 二轮验证</h1>
    <p>验证对象：<code>{STRATEGY}</code>。本页只做二轮研究验证，不表示可以直接上线。</p>
    <p class="muted">生成时间：{escape(generated)} · 数据：现有 monthly-volume causal daily backtest artifacts。</p>
    <p><a href="/momentum/paper/rank213_age90_14d_phase3_validation.html">Phase 3 严肃验证包</a> · <a href="/momentum/paper/rank213_baseline_v2_four_direction_review.html">返回 Baseline V2 主报告</a> · <a href="/momentum/paper/rank213_evidence_map.html">Evidence Map</a></p>
  </section>

  <section class="card warn">
    <h2>结论</h2>
    <p><b>它确实有 alpha 候选价值，但风险还不过关。</b> 全样本累计 {fmt_pct(base['net_cum_pct'])}，均值 {fmt_bps(base['net_mean_bps'])}，但最大回撤 {fmt_pct(base['max_drawdown_pct'])}，正收益月占比 {fmt_pct(positive_month_rate)}。</p>
    <p><b>最大坑：</b>收益集中在部分月份，且 close-to-close 成交仍偏理想。已用本地 Binance raw 1d zip 补做 open-to-open 压力测试；结果没有推翻策略，但同样是日线开盘价理想成交，不能替代真实执行回测。</p>
  </section>

  <section class="card">
    <h2>核心指标</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_pct(base['net_cum_pct'])}</b><span>累计净收益</span></div>
      <div class="metric"><b>{fmt_pct(base['max_drawdown_pct'])}</b><span>最大回撤</span></div>
      <div class="metric"><b>{fmt_bps(base['net_mean_bps'])}</b><span>日均 basket 收益</span></div>
      <div class="metric"><b>{fmt_pct(positive_month_rate)}</b><span>正收益月占比</span></div>
    </div>
  </section>

  <section class="card">
    <h2>收益曲线与逐月波动</h2>
    {equity_svg(daily)}
    {monthly_bar_svg(monthly)}
  </section>

  <section class="card">
    <h2>成本敏感性</h2>
    <p class="muted">这里把 daily gross_ret 直接扣不同 per-basket 成本。原研究口径为 4bps；如果真实执行接近 12-20bps，收益/回撤会明显恶化。</p>
    <div class="table-wrap">{table_html(cost, ["cost_bps_per_basket", "trading_baskets", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>执行时点压力测试</h2>
    <p class="muted">同一批 daily 持仓，不重新选币，只改变成交价时点。这里仍按 4bps per-basket 成本扣减。</p>
    <div class="table-wrap">{table_html(execution, ["scenario", "valid_days", "avg_coverage_pct", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
    <ul>
      {''.join(f"<li><code>{escape(k)}</code>：{escape(v)}</li>" for k, v in exec_notes.items())}
    </ul>
  </section>

  <section class="card">
    <h2>时间分段 / Walk-forward 风险</h2>
    <p class="muted">没有重新调参，只按时间切片看同一 frozen rule 是否跨阶段稳定。</p>
    <div class="table-wrap">{table_html(folds, ["fold", "rows", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>逐月贡献集中度</h2>
    <p class="muted">如果总收益主要靠少数月份，策略稳定性就要打折。</p>
    <div class="grid">
      <div class="metric"><b>{fmt_pct(positive_month_rate)}</b><span>正收益月占比</span></div>
      <div class="metric"><b>{escape(str(monthly.loc[monthly['net_cum_pct'].idxmax(), 'month']))}</b><span>最佳月 {fmt_pct(monthly['net_cum_pct'].max())}</span></div>
      <div class="metric"><b>{escape(str(monthly.loc[monthly['net_cum_pct'].idxmin(), 'month']))}</b><span>最差月 {fmt_pct(monthly['net_cum_pct'].min())}</span></div>
      <div class="metric"><b>{fmt_pct(float(top_months['share_of_total_log_return_pct'].sum()))}</b><span>前 6 盈利月贡献</span></div>
    </div>
    <h3>贡献最高月份</h3>
    <div class="table-wrap">{table_html(top_months, ["month", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "trading_baskets", "share_of_total_log_return_pct"])}</div>
    <h3>拖累最大月份</h3>
    <div class="table-wrap">{table_html(worst_months, ["month", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "trading_baskets", "share_of_total_log_return_pct"])}</div>
  </section>

  <section class="card">
    <h2>滚动 6/12/24 月稳定性</h2>
    <p class="muted">重点看 12/24 个月窗口是否频繁转负。</p>
    <div class="table-wrap">{table_html(rolling.tail(36), ["window_months", "end_month", "net_cum_pct", "positive_month_rate_pct", "worst_month_net_pct", "avg_monthly_net_pct"])}</div>
  </section>

  <section class="card">
    <h2>Long / Short 归因</h2>
    <p>重建 leg 级收益覆盖率：{fmt_pct(leg_meta['leg_price_coverage_pct'])}。Long leg 日均 {fmt_bps(long_mean)}，Short leg 日均 {fmt_bps(short_mean)}。如果一侧明显弱，后续可以考虑单边化或侧别 gate。</p>
    <div class="grid">
      <div class="metric"><b>{fmt_bps(long_mean)}</b><span>long leg 日均</span></div>
      <div class="metric"><b>{fmt_bps(short_mean)}</b><span>short leg 日均</span></div>
      <div class="metric"><b>{fmt_pct(long_cum)}</b><span>0.5 long-only 复利</span></div>
      <div class="metric"><b>{fmt_pct(short_cum)}</b><span>0.5 short-only 复利</span></div>
    </div>
    <h3>贡献最大的 symbol/side</h3>
    <div class="table-wrap">{table_html(top_symbols, ["symbol", "side", "legs", "avg_weighted_contrib_bps", "sum_weighted_contrib_pct", "win_rate_pct"])}</div>
    <h3>拖累最大的 symbol/side</h3>
    <div class="table-wrap">{table_html(bad_symbols, ["symbol", "side", "legs", "avg_weighted_contrib_bps", "sum_weighted_contrib_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>简单风险 Gate 快检</h2>
    <p class="muted">这些 gate 只用过去策略自身收益，避免未来函数；它们是风险诊断，不是最终参数优化。</p>
    <div class="table-wrap">{table_html(risk_gates, ["gate", "active_rate_pct", "skipped_days", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card warn">
    <h2>未完成验证项</h2>
    <ul>
      <li><b>TWAP / 滑点：</b>本轮已补 raw 1d open/close 压力测试，但没有分钟线和 orderbook，不能严谨估计真实冲击成本。</li>
      <li><b>真实资金费率：</b>第四条 perp overlay 已暂时搁置，本策略本轮没有加入 funding/basis/OI。</li>
      <li><b>参数样本外：</b>这里没有重新优化参数，但也还没做正式 walk-forward 参数冻结实验。</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    daily = read_daily()
    cost = build_cost_sensitivity(daily)
    folds = build_folds(daily)
    monthly = build_monthly(daily)
    rolling = build_rolling(monthly)
    leg_daily, symbol_attr, leg_meta = build_leg_attribution(daily)
    risk_gates = build_simple_risk_gates(daily)
    execution, execution_detail = build_execution_timing(daily)

    cost.to_csv(COST_PATH, index=False)
    folds.to_csv(FOLD_PATH, index=False)
    monthly.to_csv(MONTHLY_PATH, index=False)
    rolling.to_csv(ROLLING_PATH, index=False)
    leg_daily.to_csv(LEG_DAILY_PATH, index=False)
    symbol_attr.to_csv(SYMBOL_ATTR_PATH, index=False)
    risk_gates.to_csv(RISK_GATE_PATH, index=False)
    execution.to_csv(EXECUTION_PATH, index=False)
    execution_detail.to_csv(EXECUTION_DAILY_PATH, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strategy": STRATEGY,
        "objective": "second-round validation for age90_14d_skip1d_voladj baseline candidate",
        "main_stats": stats(daily),
        "positive_month_rate_pct": float((monthly["net_cum_pct"] > 0).mean() * 100.0),
        "leg_attribution_meta": leg_meta,
        "data_limitations": [
            "Binance raw 1d open/close timing stress is included where cached raw zips exist.",
            "Minute TWAP/orderbook slippage cannot be validated here.",
            "Funding/basis/OI overlay is not included.",
            "This remains daily-bar research, not execution-grade live validation.",
        ],
        "artifacts": {
            "cost_sensitivity": str(COST_PATH.relative_to(ROOT)),
            "time_folds": str(FOLD_PATH.relative_to(ROOT)),
            "monthly": str(MONTHLY_PATH.relative_to(ROOT)),
            "rolling": str(ROLLING_PATH.relative_to(ROOT)),
            "leg_daily": str(LEG_DAILY_PATH.relative_to(ROOT)),
            "symbol_attribution": str(SYMBOL_ATTR_PATH.relative_to(ROOT)),
            "risk_gates": str(RISK_GATE_PATH.relative_to(ROOT)),
            "execution_timing": str(EXECUTION_PATH.relative_to(ROOT)),
            "execution_timing_daily": str(EXECUTION_DAILY_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_PATH.write_text(build_report(daily, cost, folds, monthly, rolling, leg_daily, symbol_attr, risk_gates, execution, leg_meta), encoding="utf-8")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
