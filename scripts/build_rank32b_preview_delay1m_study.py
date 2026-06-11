#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_preview_delay1m_study"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_preview_delay1m_study"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


corrected = load_module(ROOT / "scripts" / "build_rank32b_corrected_preview_extended_validation.py", "rank32b_corrected_preview_extended_validation")


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
    cols = list(df.columns)
    rows = []
    for _, row in df.iterrows():
        tds = []
        for col in cols:
            val = row[col]
            if col in percent_cols and pd.notna(val):
                text = pct(val)
            elif isinstance(val, (int, float, np.floating)) and pd.notna(val):
                text = num(float(val), digits_cols.get(col, 2))
            else:
                text = escape(str(val))
            tds.append(f"<td>{text}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    thead = "<tr>" + "".join(f"<th>{escape(str(c))}</th>" for c in cols) + "</tr>"
    return "<table><thead>" + thead + "</thead><tbody>" + "".join(rows) + "</tbody></table>"


def direction_bps(side: int, start_price: float, end_price: float) -> float:
    if side > 0:
        return (float(end_price) / float(start_price) - 1.0) * 10000.0
    return (float(start_price) / float(end_price) - 1.0) * 10000.0


def build_preview_delay_table(m1: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    preview = corrected.build_preview_table(m1, frame).copy()
    if preview.empty:
        return preview
    open_map = m1.set_index("open_ts")["open"]
    delayed_rows = []
    for row in preview.itertuples(index=False):
        delayed_entry_ts = pd.to_datetime(row.entry_ts, utc=True) + pd.Timedelta(minutes=1)
        if delayed_entry_ts not in open_map.index:
            continue
        baseline_entry_ts = pd.to_datetime(row.entry_ts, utc=True)
        if baseline_entry_ts not in open_map.index:
            continue
        baseline_entry_px = float(open_map.loc[baseline_entry_ts])
        delayed_entry_px = float(open_map.loc[delayed_entry_ts])
        side = int(row.preview_dir)
        delay_penalty_bps = direction_bps(side, baseline_entry_px, delayed_entry_px)
        atr14 = float(row.atr14_partial) if pd.notna(row.atr14_partial) else np.nan
        tp175_bps_from_delay = np.nan
        tp175_bps_from_signal = np.nan
        if np.isfinite(atr14) and delayed_entry_px > 0:
            tp175_bps_from_delay = (1.75 * atr14 / delayed_entry_px) * 10000.0
        signal_px = float(row.close) if hasattr(row, "close") else baseline_entry_px
        if np.isfinite(atr14) and signal_px > 0:
            tp175_bps_from_signal = (1.75 * atr14 / signal_px) * 10000.0
        delay_pct_of_tp175 = delay_penalty_bps / tp175_bps_from_delay * 100.0 if np.isfinite(tp175_bps_from_delay) and tp175_bps_from_delay > 0 else np.nan
        delayed_rows.append({
            **row._asdict(),
            "entry_ts": delayed_entry_ts,
            "baseline_entry_ts": baseline_entry_ts,
            "baseline_entry_price": baseline_entry_px,
            "delayed_entry_price": delayed_entry_px,
            "delay_penalty_bps": delay_penalty_bps,
            "tp175_bps_from_delay": tp175_bps_from_delay,
            "tp175_bps_from_signal": tp175_bps_from_signal,
            "delay_pct_of_tp175": delay_pct_of_tp175,
            "mode_entry": "preview_unclosed15m_delay1m",
        })
    return pd.DataFrame(delayed_rows)


def run_delay_study(days: int = 90, refresh: bool = False, universe_key: str = "core18", costs: list[float] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    costs = costs or [10.0]
    universe = corrected.UNIVERSES[universe_key]
    trades: list[dict] = []
    signal_rows: list[dict] = []

    for idx, (asset, symbol) in enumerate(universe.items(), start=1):
        print(f"[{idx}/{len(universe)}] {asset} {symbol}", flush=True)
        m1 = corrected.load_or_fetch_1m(symbol, days=days, refresh=refresh)
        m1["open_ts"] = pd.to_datetime(m1["open_ts"], utc=True)
        m1["close_ts"] = pd.to_datetime(m1["close_ts"], utc=True)
        for c in ["open", "high", "low", "close"]:
            m1[c] = pd.to_numeric(m1[c], errors="coerce")
        bars = corrected.build_15m_from_1m(m1)
        frame = corrected.build_frame(bars)
        preview = corrected.build_preview_table(m1, frame)
        delay_preview = build_preview_delay_table(m1, frame)
        open_map = m1.set_index("open_ts")["open"]
        close_map = m1.set_index("close_ts")["close"]

        if not delay_preview.empty:
            for row in delay_preview.itertuples(index=False):
                signal_rows.append({
                    "asset": asset,
                    "symbol": symbol,
                    "signal_timestamp": pd.to_datetime(row.timestamp, utc=True).isoformat().replace("+00:00", "Z"),
                    "baseline_entry_ts": pd.to_datetime(row.baseline_entry_ts, utc=True).isoformat().replace("+00:00", "Z"),
                    "delayed_entry_ts": pd.to_datetime(row.entry_ts, utc=True).isoformat().replace("+00:00", "Z"),
                    "delay_penalty_bps": float(row.delay_penalty_bps),
                    "tp175_bps_from_delay": float(row.tp175_bps_from_delay) if pd.notna(row.tp175_bps_from_delay) else None,
                    "delay_pct_of_tp175": float(row.delay_pct_of_tp175) if pd.notna(row.delay_pct_of_tp175) else None,
                    "confirmed_at_close": int(row.confirmed_at_close),
                    "preview_only": int(row.preview_only),
                    "lead_minutes": float(row.lead_minutes),
                })

        official = frame[frame["official_dir"] != 0][["timestamp", "official_dir", "atr14"]].copy()
        official["entry_ts"] = official["timestamp"] + pd.Timedelta(minutes=15)
        official["confirmed_at_close"] = 1
        official["preview_only"] = 0
        official["lead_minutes"] = 0.0

        pre_first = corrected.build_preview_table(m1, frame)

        for cfg in corrected.EXIT_CONFIGS:
            for cost in costs:
                # official_close
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                for row in official.sort_values("entry_ts").itertuples(index=False):
                    if row.entry_ts <= last_exit:
                        continue
                    if cfg["kind"] == "fixed_hold":
                        ex = corrected.simulate_fixed_hold(open_map, close_map, row.entry_ts, int(row.official_dir), cost)
                    else:
                        ex = corrected.simulate_atr(open_map, m1, row.entry_ts, int(row.official_dir), float(row.atr14) if pd.notna(row.atr14) else np.nan, cost, cfg["tp_atr"], cfg["sl_atr"], cfg["timeout_min"])
                    if ex is None:
                        continue
                    trades.append({
                        "asset": asset,
                        "symbol": symbol,
                        "entry_mode": "official_close",
                        "exit_config": cfg["name"],
                        "market_cost_bps": float(cost),
                        "net_ret": ex.net_ret,
                        "gross_ret": ex.gross_ret,
                        "exit_reason": ex.exit_reason,
                        "confirmed_at_close": 1,
                        "preview_only": 0,
                        "lead_minutes": 0.0,
                        "delay_penalty_bps": 0.0,
                        "delay_pct_of_tp175": 0.0,
                    })
                    last_exit = ex.exit_ts

                # baseline preview
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                for row in pre_first.sort_values("entry_ts").itertuples(index=False):
                    if row.entry_ts <= last_exit:
                        continue
                    atr14 = float(row.atr14_partial) if pd.notna(row.atr14_partial) else np.nan
                    if cfg["kind"] == "fixed_hold":
                        ex = corrected.simulate_fixed_hold(open_map, close_map, row.entry_ts, int(row.preview_dir), cost)
                    else:
                        ex = corrected.simulate_atr(open_map, m1, row.entry_ts, int(row.preview_dir), atr14, cost, cfg["tp_atr"], cfg["sl_atr"], cfg["timeout_min"])
                    if ex is None:
                        continue
                    trades.append({
                        "asset": asset,
                        "symbol": symbol,
                        "entry_mode": "preview_unclosed15m",
                        "exit_config": cfg["name"],
                        "market_cost_bps": float(cost),
                        "net_ret": ex.net_ret,
                        "gross_ret": ex.gross_ret,
                        "exit_reason": ex.exit_reason,
                        "confirmed_at_close": int(row.confirmed_at_close),
                        "preview_only": int(row.preview_only),
                        "lead_minutes": float(row.lead_minutes),
                        "delay_penalty_bps": 0.0,
                        "delay_pct_of_tp175": 0.0,
                    })
                    last_exit = ex.exit_ts

                # preview + 1m delay
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                for row in delay_preview.sort_values("entry_ts").itertuples(index=False):
                    if row.entry_ts <= last_exit:
                        continue
                    atr14 = float(row.atr14_partial) if pd.notna(row.atr14_partial) else np.nan
                    if cfg["kind"] == "fixed_hold":
                        ex = corrected.simulate_fixed_hold(open_map, close_map, row.entry_ts, int(row.preview_dir), cost)
                    else:
                        ex = corrected.simulate_atr(open_map, m1, row.entry_ts, int(row.preview_dir), atr14, cost, cfg["tp_atr"], cfg["sl_atr"], cfg["timeout_min"])
                    if ex is None:
                        continue
                    trades.append({
                        "asset": asset,
                        "symbol": symbol,
                        "entry_mode": "preview_unclosed15m_delay1m",
                        "exit_config": cfg["name"],
                        "market_cost_bps": float(cost),
                        "net_ret": ex.net_ret,
                        "gross_ret": ex.gross_ret,
                        "exit_reason": ex.exit_reason,
                        "confirmed_at_close": int(row.confirmed_at_close),
                        "preview_only": int(row.preview_only),
                        "lead_minutes": float(row.lead_minutes),
                        "delay_penalty_bps": float(row.delay_penalty_bps),
                        "delay_pct_of_tp175": float(row.delay_pct_of_tp175) if pd.notna(row.delay_pct_of_tp175) else np.nan,
                    })
                    last_exit = ex.exit_ts

    trades_df = pd.DataFrame(trades)
    signal_df = pd.DataFrame(signal_rows)

    summary_rows = []
    for (entry_mode, exit_config, cost), grp in trades_df.groupby(["entry_mode", "exit_config", "market_cost_bps"], sort=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        summary_rows.append({
            "entry_mode": entry_mode,
            "exit_config": exit_config,
            "market_cost_bps": float(cost),
            "mean_total_return": float(asset_total.mean()),
            "median_total_return": float(asset_total.median()),
            "positive_asset_ratio": float((asset_total > 0).mean()),
            "mean_trades": float(grp.groupby("asset").size().mean()),
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()),
            "confirmed_at_close_ratio": float(grp["confirmed_at_close"].mean()) if "preview" in entry_mode else 1.0,
            "preview_only_ratio": float(grp["preview_only"].mean()) if "preview" in entry_mode else 0.0,
            "mean_lead_minutes": float(grp["lead_minutes"].dropna().mean()) if grp["lead_minutes"].notna().any() else 0.0,
            "mean_delay_penalty_bps": float(grp["delay_penalty_bps"].dropna().mean()) if grp["delay_penalty_bps"].notna().any() else 0.0,
            "median_delay_penalty_bps": float(grp["delay_penalty_bps"].dropna().median()) if grp["delay_penalty_bps"].notna().any() else 0.0,
            "mean_delay_pct_of_tp175": float(grp["delay_pct_of_tp175"].dropna().mean()) if grp["delay_pct_of_tp175"].notna().any() else 0.0,
            "max_delay_pct_of_tp175": float(grp["delay_pct_of_tp175"].dropna().max()) if grp["delay_pct_of_tp175"].notna().any() else 0.0,
        })
    return trades_df, pd.DataFrame(summary_rows).sort_values(["exit_config", "market_cost_bps", "entry_mode"]).reset_index(drop=True), signal_df


def build_asset_summary(trades_df: pd.DataFrame, target_exit: str, target_cost: float = 10.0) -> pd.DataFrame:
    rows = []
    subset = trades_df[(trades_df["exit_config"] == target_exit) & (trades_df["market_cost_bps"] == target_cost)]
    for (entry_mode, asset), grp in subset.groupby(["entry_mode", "asset"], sort=False):
        rows.append({
            "entry_mode": entry_mode,
            "asset": asset,
            "trades": int(len(grp)),
            "win_rate": float((grp["net_ret"] > 0).mean()),
            "total_return": float((1.0 + grp["net_ret"]).prod() - 1.0),
            "mean_net_ret": float(grp["net_ret"].mean()),
            "mean_delay_penalty_bps": float(grp["delay_penalty_bps"].mean()) if grp["delay_penalty_bps"].notna().any() else 0.0,
            "mean_delay_pct_of_tp175": float(grp["delay_pct_of_tp175"].mean()) if grp["delay_pct_of_tp175"].notna().any() else 0.0,
        })
    return pd.DataFrame(rows)


def write_report(summary_df: pd.DataFrame, signal_df: pd.DataFrame, asset_df: pd.DataFrame, out_dir: Path, universe_key: str, days: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    focus = summary_df[(summary_df["exit_config"] == "atr_tp1.75_sl1.00_to120") & (summary_df["market_cost_bps"] == 10.0)].copy()
    focus = focus[[
        "entry_mode", "mean_total_return", "median_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate",
        "confirmed_at_close_ratio", "preview_only_ratio", "mean_lead_minutes", "mean_delay_penalty_bps", "median_delay_penalty_bps",
        "mean_delay_pct_of_tp175", "max_delay_pct_of_tp175",
    ]]
    delay_signals = signal_df.copy()
    if not delay_signals.empty:
        delay_signals = delay_signals[[
            "asset", "symbol", "signal_timestamp", "baseline_entry_ts", "delayed_entry_ts", "delay_penalty_bps",
            "tp175_bps_from_delay", "delay_pct_of_tp175", "confirmed_at_close", "preview_only", "lead_minutes",
        ]].sort_values("delay_penalty_bps", ascending=False).head(20)
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b corrected preview +1m delay study</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1200px; margin: 24px auto; padding: 0 16px; line-height: 1.6; color: #111827; }}
    .muted {{ color: #6b7280; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 12px; margin: 16px 0; }}
    .card {{ border:1px solid #e5e7eb; border-radius: 14px; padding: 14px 16px; background: #fff; }}
    .k {{ color:#6b7280; font-size: 12px; text-transform: uppercase; }}
    .v {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
    table {{ width:100%; border-collapse: collapse; margin: 14px 0 24px; }}
    th, td {{ border:1px solid #e5e7eb; padding: 8px 10px; text-align: left; font-size: 13px; }}
    th {{ background:#f8fafc; }}
  </style>
</head>
<body>
  <h1>Rank32b corrected preview：+1 根 1m 延迟入场研究</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ universe={escape(universe_key)} ｜ lookback={days}d ｜ 口径：在 corrected preview 的基础上，将 preview 入场时间从 <code>signal minute close</code> 再向后推 1 根 1m K 线，用于模拟实盘检测/执行延迟。</p>

  <div class='grid'>
    <div class='card'><div class='k'>研究重点</div><div class='v'>atr_tp1.75</div><div class='s'>重点观察 1.75 ATR 止盈下，1m 延迟是否显著侵蚀 edge</div></div>
    <div class='card'><div class='k'>baseline</div><div class='v'>preview_unclosed15m</div><div class='s'>corrected preview 原始口径</div></div>
    <div class='card'><div class='k'>delay mode</div><div class='v'>preview +1m</div><div class='s'>额外延迟一根 1m 后再入场</div></div>
    <div class='card'><div class='k'>交易成本</div><div class='v'>10 bps</div><div class='s'>与 corrected preview validation 主口径对齐</div></div>
  </div>

  <h2>1.75 ATR 止盈：模式对比</h2>
  <p class='muted'>看三种模式：official_close、baseline preview、preview+1m delay。重点看总收益、胜率，以及 delay penalty 侵蚀了多少 TP 空间。</p>
  {render_table(focus, percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'mean_trades':1,'mean_lead_minutes':2,'mean_delay_penalty_bps':2,'median_delay_penalty_bps':2,'mean_delay_pct_of_tp175':2,'max_delay_pct_of_tp175':2})}

  <h2>1m 延迟最敏感的 preview 信号（Top 20）</h2>
  <p class='muted'>这里的 <strong>delay_penalty_bps</strong> 是：如果比 corrected preview 晚 1 根 1m K 线入场，方向上会多吃掉多少 bps；<strong>delay_pct_of_tp175</strong> 是这部分损耗占 1.75 ATR TP 空间的比例。</p>
  {render_table(delay_signals, digits_cols={'delay_penalty_bps':2,'tp175_bps_from_delay':2,'delay_pct_of_tp175':2,'confirmed_at_close':0,'preview_only':0,'lead_minutes':2})}

  <h2>资产层表现（1.75 ATR / 10bps）</h2>
  <p class='muted'>可直接看哪些资产对 +1m delay 更敏感；如果某个资产 delay penalty 偏大且总收益明显转弱，就值得重点排查/临时剔除。</p>
  {render_table(asset_df.sort_values(['entry_mode','total_return'], ascending=[True, False]), percent_cols={'win_rate','total_return','mean_net_ret'}, digits_cols={'trades':0,'mean_delay_penalty_bps':2,'mean_delay_pct_of_tp175':2})}
</body>
</html>
"""
    (out_dir / "report.html").write_text(html, encoding="utf-8")


def main() -> None:
    universe_key = "core18"
    days = 90
    refresh = False
    costs = [10.0]
    out_art = ART_DIR / f"{universe_key}_{days}d_cost10"
    out_site = SITE_DIR / f"{universe_key}_{days}d_cost10"
    out_art.mkdir(parents=True, exist_ok=True)
    out_site.mkdir(parents=True, exist_ok=True)

    trades_df, summary_df, signal_df = run_delay_study(days=days, refresh=refresh, universe_key=universe_key, costs=costs)
    asset_df = build_asset_summary(trades_df, target_exit="atr_tp1.75_sl1.00_to120", target_cost=10.0)

    trades_df.to_csv(out_art / "trades.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    summary_df.to_csv(out_art / "summary.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    signal_df.to_csv(out_art / "delay_signal_stats.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    asset_df.to_csv(out_art / "asset_summary.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "universe_key": universe_key,
        "days": days,
        "refresh": refresh,
        "costs": costs,
        "source": "rank32b_corrected_preview_extended_validation",
        "study": "preview entry delayed by +1 additional 1m bar",
        "focus_exit": "atr_tp1.75_sl1.00_to120",
    }
    (out_art / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(summary_df, signal_df, asset_df, out_site, universe_key=universe_key, days=days)
    print(f"[ok] wrote {out_art}")
    print(f"[ok] wrote {out_site / 'report.html'}")


if __name__ == "__main__":
    main()
