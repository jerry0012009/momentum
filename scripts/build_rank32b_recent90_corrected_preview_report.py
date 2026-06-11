#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_recent90_corrected_preview"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_recent90_corrected_preview"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "LTC-USD": "LTCUSDT",
    "NEAR-USD": "NEARUSDT",
    "UNI-USD": "UNIUSDT",
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "BNB-USD": "BNBUSDT",
    "ADA-USD": "ADAUSDT",
    "AVAX-USD": "AVAXUSDT",
    "LINK-USD": "LINKUSDT",
    "BCH-USD": "BCHUSDT",
    "DOT-USD": "DOTUSDT",
    "ZEC-USD": "ZECUSDT",
    "AAVE-USD": "AAVEUSDT",
    "SUI-USD": "SUIUSDT",
    "WLD-USD": "WLDUSDT",
}
EMA_FAST_1H = 20
EMA_SLOW_1H = 50
SLOPE_FLOOR = 0.0004
HOLD_MIN = 120
COSTS = [6.0, 10.0, 15.0, 20.0]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v, digits=2):
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v)*100:.{digits}f}%"


def num(v, digits=2):
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_15m_from_1m(m1: pd.DataFrame) -> pd.DataFrame:
    work = m1.copy()
    work["timestamp"] = work["open_ts"].dt.floor("15min")
    return (
        work.groupby("timestamp", sort=True)
        .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
        .reset_index()
    )


def build_frame(bars: pd.DataFrame) -> pd.DataFrame:
    market = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()
    frame = pd.merge_asof(bars.sort_values("timestamp"), market_1h.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False)
    frame["slope_floor_long"] = ((frame["fast_slope"] > SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False)
    frame["prev_close"] = frame["close"].shift(1)
    frame["prev_fast"] = frame["ema_fast_1h"].shift(1)
    frame["official_dir"] = 0
    frame.loc[(frame["long_structure"] & frame["slope_floor_long"] & (frame["prev_close"] <= frame["prev_fast"]) & (frame["close"] > frame["ema_fast_1h"])).fillna(False), "official_dir"] = 1
    frame.loc[(frame["short_structure"] & frame["slope_floor_short"] & (frame["prev_close"] >= frame["prev_fast"]) & (frame["close"] < frame["ema_fast_1h"])).fillna(False), "official_dir"] = -1
    return frame


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = []
    for asset, symbol in ASSETS.items():
        p = ROOT / "reports" / "artifacts" / "rank32b_unclosed15m_preview_backtest" / "cache_1m" / f"{symbol}__90d__1m__perp.csv"
        m1 = pd.read_csv(p)
        m1["open_ts"] = pd.to_datetime(m1["open_ts"], utc=True)
        m1["close_ts"] = pd.to_datetime(m1["close_ts"], utc=True)
        for c in ["open", "high", "low", "close"]:
            m1[c] = pd.to_numeric(m1[c], errors="coerce")
        bars = build_15m_from_1m(m1)
        frame = build_frame(bars)
        open_map = m1.set_index("open_ts")["open"]
        close_map = m1.set_index("close_ts")["close"]

        official = frame[frame["official_dir"] != 0][["timestamp", "official_dir"]].copy()
        official["entry_ts"] = official["timestamp"] + pd.Timedelta(minutes=15)
        official["confirmed_at_close"] = 1
        official["preview_only"] = 0
        official["lead_minutes"] = 0.0
        official["entry_improve_bps"] = 0.0
        official["mode"] = "official_close_fixed_hold_corrected"

        minute = m1[["open_ts", "close_ts", "close"]].copy()
        minute["timestamp"] = minute["open_ts"].dt.floor("15min")
        minute = minute.merge(
            frame[["timestamp", "ema_fast_1h", "long_structure", "short_structure", "slope_floor_long", "slope_floor_short", "prev_close", "prev_fast", "official_dir"]],
            on="timestamp",
            how="left",
        )
        minute["preview_dir"] = 0
        minute.loc[(minute["long_structure"] & minute["slope_floor_long"] & (minute["prev_close"] <= minute["prev_fast"]) & (minute["close"] > minute["ema_fast_1h"])).fillna(False), "preview_dir"] = 1
        minute.loc[(minute["short_structure"] & minute["slope_floor_short"] & (minute["prev_close"] >= minute["prev_fast"]) & (minute["close"] < minute["ema_fast_1h"])).fillna(False), "preview_dir"] = -1
        preview = minute[minute["preview_dir"] != 0].groupby("timestamp", sort=True).head(1).copy()
        preview["entry_ts"] = preview["close_ts"]
        preview["confirmed_at_close"] = (preview["preview_dir"] == preview["official_dir"]).astype(int)
        preview["preview_only"] = (preview["preview_dir"] != preview["official_dir"]).astype(int)
        preview["lead_minutes"] = ((preview["timestamp"] + pd.Timedelta(minutes=15)) - preview["entry_ts"]).dt.total_seconds() / 60.0
        preview["entry_improve_bps"] = np.nan
        off_entry_ts = preview["timestamp"] + pd.Timedelta(minutes=15)
        mask = preview["entry_ts"].isin(open_map.index) & off_entry_ts.isin(open_map.index)
        idx = preview.index[mask]
        preview_open = preview.loc[idx, "entry_ts"].map(open_map)
        official_open = off_entry_ts.loc[idx].map(open_map)
        longmask = preview.loc[idx, "preview_dir"] > 0
        vals = np.where(longmask, (official_open.to_numpy() / preview_open.to_numpy() - 1.0) * 10000.0, (preview_open.to_numpy() / official_open.to_numpy() - 1.0) * 10000.0)
        preview.loc[idx, "entry_improve_bps"] = vals
        preview["mode"] = "preview_unclosed15m_fixed_hold_corrected"

        for mode, dfsig, dircol in [
            ("official_close_fixed_hold_corrected", official, "official_dir"),
            ("preview_unclosed15m_fixed_hold_corrected", preview, "preview_dir"),
        ]:
            dfsig = dfsig[["entry_ts", dircol, "confirmed_at_close", "preview_only", "lead_minutes", "entry_improve_bps"]].rename(columns={dircol: "dir"}).sort_values("entry_ts").reset_index(drop=True)
            for cost in COSTS:
                rate = cost / 10000.0
                last_exit = pd.Timestamp.min.tz_localize("UTC")
                for row in dfsig.itertuples(index=False):
                    entry_ts = row.entry_ts
                    if entry_ts <= last_exit or entry_ts not in open_map.index:
                        continue
                    exit_ts = entry_ts + pd.Timedelta(minutes=HOLD_MIN)
                    if exit_ts not in close_map.index:
                        continue
                    entry = float(open_map.loc[entry_ts])
                    exit_px = float(close_map.loc[exit_ts])
                    gross = (exit_px / entry - 1.0) * int(row.dir)
                    net = (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0
                    trades.append(
                        {
                            "asset": asset,
                            "mode": mode,
                            "market_cost_bps": float(cost),
                            "net_ret": float(net),
                            "confirmed_at_close": int(row.confirmed_at_close),
                            "preview_only": int(row.preview_only),
                            "lead_minutes": float(row.lead_minutes),
                            "entry_improve_bps": float(row.entry_improve_bps) if pd.notna(row.entry_improve_bps) else np.nan,
                        }
                    )
                    last_exit = exit_ts
    trades_df = pd.DataFrame(trades)
    summary_rows = []
    for (mode, cost), grp in trades_df.groupby(["mode", "market_cost_bps"]):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        summary_rows.append(
            {
                "mode": mode,
                "market_cost_bps": float(cost),
                "mean_total_return": float(asset_total.mean()),
                "median_total_return": float(asset_total.median()),
                "positive_asset_ratio": float((asset_total > 0).mean()),
                "mean_trades": float(grp.groupby("asset").size().mean()),
                "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()),
                "confirmed_at_close_ratio": float(grp["confirmed_at_close"].mean()) if "preview" in mode else 1.0,
                "preview_only_ratio": float(grp["preview_only"].mean()) if "preview" in mode else 0.0,
                "mean_lead_minutes": float(grp["lead_minutes"].dropna().mean()) if grp["lead_minutes"].notna().any() else 0.0,
                "mean_entry_improve_bps": float(grp["entry_improve_bps"].dropna().mean()) if grp["entry_improve_bps"].notna().any() else 0.0,
            }
        )
    summary_df = pd.DataFrame(summary_rows).sort_values(["market_cost_bps", "mode"]).reset_index(drop=True)
    return trades_df, summary_df


def build_html(generated_at: str, summary_df: pd.DataFrame, compare10: pd.DataFrame) -> str:
    official10 = summary_df[(summary_df["mode"] == "official_close_fixed_hold_corrected") & (summary_df["market_cost_bps"] == 10.0)].iloc[0]
    preview10 = summary_df[(summary_df["mode"] == "preview_unclosed15m_fixed_hold_corrected") & (summary_df["market_cost_bps"] == 10.0)].iloc[0]
    headline = (
        f"在 recent90、同样 fixed-hold 120m 的 apples-to-apples 对照下，preview 版 mean_total_return≈{pct(preview10['mean_total_return'])}，"
        f"official 版≈{pct(official10['mean_total_return'])}；preview 平均提前 {num(preview10['mean_lead_minutes'],2)} 分钟，"
        f"平均改善入场 {num(preview10['mean_entry_improve_bps'],2)} bps。"
    )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b recent90 corrected preview</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <h1>Rank32b · recent90 corrected preview study</h1>
  <p class='muted'>生成时间：{escape(generated_at)}</p>

  <div class='card'>
    <h2>这次修正了什么</h2>
    <ul>
      <li>不再用旧 preview 脚本里那套“盘中动态更新 1h EMA / slope”的口径。</li>
      <li>corrected preview 只改一件事：<b>当前未收盘 15m bar 的 close 提前可见</b>；高周期 1h 结构仍沿用原始 clean baseline 口径。</li>
      <li>这样才能回答真正的问题：<b>只提前看未收盘 15m，会让策略更有优势还是更没优势？</b></li>
    </ul>
  </div>

  <div class='card'>
    <h2>headline</h2>
    <p><b>{escape(headline)}</b></p>
  </div>

  <div class='card'>
    <h2>总体结果</h2>
    {render_table(summary_df[['mode','market_cost_bps','mean_total_return','median_total_return','positive_asset_ratio','mean_trades','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio','mean_lead_minutes','mean_entry_improve_bps']], percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'market_cost_bps':0,'mean_trades':1,'mean_lead_minutes':2,'mean_entry_improve_bps':2})}
  </div>

  <div class='card'>
    <h2>10bps 分资产对照（preview - official）</h2>
    {render_table(compare10.reset_index()[['asset','official_close_fixed_hold_corrected','preview_unclosed15m_fixed_hold_corrected','delta_preview_minus_official']].sort_values('delta_preview_minus_official', ascending=False), percent_cols={'official_close_fixed_hold_corrected','preview_unclosed15m_fixed_hold_corrected','delta_preview_minus_official'})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    trades_df, summary_df = run()
    compare10 = trades_df[trades_df['market_cost_bps']==10.0].groupby(['asset','mode'])['net_ret'].apply(lambda s: float((1.0+s).prod()-1.0)).unstack()
    compare10['delta_preview_minus_official'] = compare10['preview_unclosed15m_fixed_hold_corrected'] - compare10['official_close_fixed_hold_corrected']
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    run_dir = ensure_dir(ART_DIR / 'recent90')
    trades_df.to_csv(run_dir / 'trades.csv', index=False)
    summary_df.to_csv(run_dir / 'summary.csv', index=False)
    compare10.to_csv(run_dir / 'asset_compare_10bps.csv')
    (run_dir / 'meta.json').write_text(json.dumps({'generated_at': generated_at}, ensure_ascii=False, indent=2), encoding='utf-8')
    site_path = SITE_DIR / 'report.html'
    site_path.write_text(build_html(generated_at, summary_df, compare10), encoding='utf-8')
    print(summary_df.to_string(index=False))
    print(f'\nartifacts: {run_dir}')
    print(f'site: {site_path}')


if __name__ == '__main__':
    main()
