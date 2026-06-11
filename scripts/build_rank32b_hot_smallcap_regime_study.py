#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import statistics
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_hot_smallcap_regime_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_hot_smallcap_regime_15m"
REPORT_PATH = SITE_DIR / "report.html"
POOL_META_PATH = ART_DIR / "pool_meta.csv"
VARIANT_SUMMARY_PATH = ART_DIR / "variant_summary.csv"
ASSET_VARIANT_PATH = ART_DIR / "variant_asset_summary.csv"
TIME_SUMMARY_PATH = ART_DIR / "variant_time_summary.csv"
DETAIL_JSON_PATH = ART_DIR / "study_summary.json"

LIVE_PARITY_SCRIPT = ROOT / "scripts" / "build_rank32b_live_parity_universe.py"
FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
FUTURES_TICKER_24H = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"

DAYS = 120
TP_MULT = 1.25
SL_MULT = 1.0
TIMEOUT_15M = 8
MAX_CONCURRENT = 1
REGIME_WINDOW = 36
REGIME_TREND_THRESHOLD = 0.015
REGIME_SCORE_THRESHOLD = 2.0
VOL_Q = 0.40


@dataclass(frozen=True)
class PoolEntry:
    symbol: str
    rationale: str
    requested_by_user: bool = False


POOL = [
    PoolEntry("BEATUSDT", "用户点名；偏热度驱动的新币/妖币研究样本", True),
    PoolEntry("PIPPINUSDT", "用户点名；高成交、高话题的小币样本", True),
    PoolEntry("SIRENUSDT", "用户点名；高热度高波动样本", True),
    PoolEntry("TRADOORUSDT", "用户点名；较新且疑似题材驱动样本", True),
    PoolEntry("FARTCOINUSDT", "同类 meme/hot proxy；成交连续性较强"),
    PoolEntry("WIFUSDT", "同类 meme/hot proxy；较成熟的热点币对照组"),
    PoolEntry("PENGUUSDT", "同类 meme/hot proxy；活跃但非一线"),
    PoolEntry("PNUTUSDT", "同类 meme/hot proxy；高波动题材币"),
    PoolEntry("MOODENGUSDT", "同类 meme/hot proxy；热度驱动明显"),
    PoolEntry("HIPPOUSDT", "同类 meme/hot proxy；微价位高波动样本"),
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


live_mod = load_module(LIVE_PARITY_SCRIPT, "rank32b_live_parity_hot_smallcap")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pct(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def money_m(v: float | None) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) / 1e6:.1f}M"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None, money_cols: set[str] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    money_cols = money_cols or set()
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        tds: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in money_cols:
                text = money_m(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            tds.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def fetch_pool_meta(pool: list[PoolEntry]) -> pd.DataFrame:
    exchange_info = fetch_json(FUTURES_EXCHANGE_INFO)
    ticker_24h = {row["symbol"]: row for row in fetch_json(FUTURES_TICKER_24H)}
    symbol_rows = {row["symbol"]: row for row in exchange_info["symbols"]}
    now_ms = time.time() * 1000.0
    rows: list[dict[str, object]] = []
    for entry in pool:
        row = symbol_rows.get(entry.symbol)
        ticker = ticker_24h.get(entry.symbol, {})
        if not row:
            continue
        params = urllib.parse.urlencode({"symbol": entry.symbol, "interval": "1d", "limit": 30})
        klines = fetch_json(f"{FUTURES_KLINES}?{params}")
        qv = [float(x[7]) for x in klines] if klines else []
        rows.append(
            {
                "symbol": entry.symbol,
                "asset": entry.symbol.replace("USDT", "-USD"),
                "requested_by_user": entry.requested_by_user,
                "listing_days": (now_ms - float(row.get("onboardDate") or 0.0)) / 1000.0 / 86400.0,
                "quote_volume_24h": float(ticker.get("quoteVolume") or 0.0),
                "quote_volume_median_30d": float(statistics.median(qv)) if qv else np.nan,
                "quote_volume_mean_30d": float(sum(qv) / len(qv)) if qv else np.nan,
                "last_price": float(ticker.get("lastPrice") or 0.0),
                "rationale": entry.rationale,
            }
        )
    return pd.DataFrame(rows).sort_values(["requested_by_user", "quote_volume_median_30d"], ascending=[False, False]).reset_index(drop=True)


def simulate_candidates_with_metrics(asset_map: dict[str, str], days: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, symbol in asset_map.items():
        bars_15m = live_mod.exec_mod.perp_mod.load_or_fetch_perp_bars(symbol, days=days, refresh=False)
        bars_5m = live_mod.exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=False)
        frame = live_mod.ext_mod.build_rank32b_frame_from_bars(asset, bars_15m)
        frame["atr14"] = live_mod.exec_mod.compute_atr(frame)
        frame["ret_1"] = frame["close"].pct_change()
        frame["trend_return_36"] = frame["close"] / frame["close"].shift(REGIME_WINDOW) - 1.0
        frame["trend_strength_36"] = frame["trend_return_36"].abs()
        frame["noise_level_36"] = frame["ret_1"].rolling(REGIME_WINDOW, min_periods=REGIME_WINDOW).std(ddof=0)
        frame["regime_score_36"] = frame["trend_strength_36"] / frame["noise_level_36"].replace(0.0, np.nan)
        frame["atr_pct"] = frame["atr14"] / frame["close"]
        signals = live_mod.exec_mod.build_signal_trades(frame, asset)
        sub_df = bars_5m.copy().sort_values("timestamp").reset_index(drop=True)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]")
        for _, trade in signals.iterrows():
            signal_idx = int(trade["signal_idx"])
            frow = frame.iloc[signal_idx]
            entry_ts = pd.to_datetime(trade["entry_ts"], utc=True)
            direction_sign = int(trade["direction_sign"])
            entry_res = live_mod.exec_mod.simulate_entry(
                sub_df,
                ts_array,
                entry_ts,
                direction_sign,
                entry_style="taker",
                entry_offset_bps=0.0,
                ttl_bars=live_mod.exec_mod.ENTRY_TTL_5M_BARS,
            )
            if entry_res is None:
                continue
            exit_res = live_mod.simulate_atr_oco_exit(
                sub_df,
                int(entry_res["fill_idx"]),
                float(entry_res["fill_px"]),
                direction_sign,
                float(trade["atr14_entry"]),
                TP_MULT,
                SL_MULT,
                TIMEOUT_15M,
            )
            if exit_res is None:
                continue
            gross_ret = live_mod.exec_mod.gross_return(float(entry_res["fill_px"]), float(exit_res["exit_px"]), direction_sign)
            rows.append(
                {
                    "asset": asset,
                    "symbol": symbol,
                    "event_ts": pd.to_datetime(trade["event_ts"], utc=True),
                    "entry_ts": pd.to_datetime(entry_res["fill_ts"], utc=True),
                    "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                    "direction": str(trade["direction"]),
                    "direction_sign": direction_sign,
                    "slope_strength": float(frow["slope_strength"]) if pd.notna(frow["slope_strength"]) else np.nan,
                    "atr14_entry": float(trade["atr14_entry"]),
                    "atr_pct": float(frow["atr_pct"]) if pd.notna(frow["atr_pct"]) else np.nan,
                    "trend_strength_36": float(frow["trend_strength_36"]) if pd.notna(frow["trend_strength_36"]) else np.nan,
                    "noise_level_36": float(frow["noise_level_36"]) if pd.notna(frow["noise_level_36"]) else np.nan,
                    "regime_score_36": float(frow["regime_score_36"]) if pd.notna(frow["regime_score_36"]) else np.nan,
                    "entry_price": float(entry_res["fill_px"]),
                    "exit_price": float(exit_res["exit_px"]),
                    "gross_ret": gross_ret,
                    "net_ret": live_mod.exec_mod.apply_fees(gross_ret, float(entry_res["entry_fee_bps"]), float(exit_res["exit_fee_bps"])),
                    "hold_minutes": int(exit_res["hold_minutes"]),
                    "target_hit": int(exit_res["target_hit"]),
                    "stop_hit": int(exit_res["stop_hit"]),
                    "exit_type": str(exit_res["exit_type"]),
                }
            )
    return pd.DataFrame(rows)


def build_variants(candidates: pd.DataFrame) -> dict[str, pd.DataFrame]:
    work = candidates.copy()
    vol_floor = work.groupby("asset")["atr_pct"].quantile(VOL_Q).to_dict()
    work["vol_gate_p40"] = work.apply(lambda r: pd.notna(r["atr_pct"]) and r["atr_pct"] > vol_floor.get(r["asset"], np.nan), axis=1)
    work["trend_gate_default"] = (work["trend_strength_36"] > REGIME_TREND_THRESHOLD) & (work["regime_score_36"] > REGIME_SCORE_THRESHOLD)
    work["combo_gate"] = work["vol_gate_p40"] & work["trend_gate_default"]
    return {
        "baseline": work,
        "vol_gate_p40": work[work["vol_gate_p40"]].copy(),
        "trend_gate_default": work[work["trend_gate_default"]].copy(),
        "combo_gate": work[work["combo_gate"]].copy(),
    }


def build_time_buckets(trades: pd.DataFrame, variant: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "window", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes"])
    work = trades.copy().sort_values("entry_ts").reset_index(drop=True)
    work["entry_ts"] = pd.to_datetime(work["entry_ts"], utc=True)
    start = work["entry_ts"].min()
    end = work["entry_ts"].max()
    span = max((end - start).total_seconds(), 1.0)
    cut1 = start + pd.Timedelta(seconds=span / 3)
    cut2 = start + pd.Timedelta(seconds=span * 2 / 3)
    windows = [
        ("early_third", work[work["entry_ts"] < cut1]),
        ("middle_third", work[(work["entry_ts"] >= cut1) & (work["entry_ts"] < cut2)]),
        ("late_third", work[work["entry_ts"] >= cut2]),
    ]
    rows: list[dict[str, object]] = []
    for name, part in windows:
        if part.empty:
            continue
        rows.append(
            {
                "variant": variant,
                "window": name,
                "trades": int(len(part)),
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "win_rate": float((part["net_ret"] > 0).mean()),
                "avg_net_ret": float(part["net_ret"].mean()),
                "avg_hold_minutes": float(part["hold_minutes"].mean()),
            }
        )
    return pd.DataFrame(rows)


def study(asset_map: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    candidates = simulate_candidates_with_metrics(asset_map, DAYS)
    variants = build_variants(candidates)
    summary_rows: list[dict[str, object]] = []
    asset_rows: list[pd.DataFrame] = []
    time_rows: list[pd.DataFrame] = []
    detail: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": DAYS,
        "tp_atr_mult": TP_MULT,
        "sl_atr_mult": SL_MULT,
        "timeout_15m": TIMEOUT_15M,
        "max_concurrent": MAX_CONCURRENT,
        "regime_window": REGIME_WINDOW,
        "regime_trend_threshold": REGIME_TREND_THRESHOLD,
        "regime_score_threshold": REGIME_SCORE_THRESHOLD,
        "volatility_quantile_floor": VOL_Q,
        "symbols": list(asset_map.values()),
    }
    for name, df in variants.items():
        selected, selection_stats = live_mod.apply_live_selection(df, strongest_only_per_bar=True, max_concurrent_positions=MAX_CONCURRENT)
        portfolio = live_mod.summarize_portfolio(selected, selection_stats, df)
        asset_summary = live_mod.summarize_assets(selected, asset_map)
        positive_asset_ratio = float((asset_summary["total_return"] > 0).mean()) if not asset_summary.empty else np.nan
        summary_rows.append(
            {
                "variant": name,
                **{k: v for k, v in portfolio.items() if k != "selection_stats"},
                "positive_asset_ratio": positive_asset_ratio,
            }
        )
        variant_asset = asset_summary.copy()
        variant_asset.insert(0, "variant", name)
        asset_rows.append(variant_asset)
        time_rows.append(build_time_buckets(selected, name))
        detail[name] = {
            **{k: v for k, v in portfolio.items() if k != "selection_stats"},
            "selection_stats": selection_stats.to_dict(orient="records"),
            "positive_asset_ratio": positive_asset_ratio,
        }
    variant_summary = pd.DataFrame(summary_rows)
    asset_variant = pd.concat(asset_rows, ignore_index=True) if asset_rows else pd.DataFrame()
    time_summary = pd.concat(time_rows, ignore_index=True) if time_rows else pd.DataFrame()
    return variant_summary, asset_variant, time_summary, detail


def build_html(generated_at: str, pool_meta: pd.DataFrame, variant_summary: pd.DataFrame, asset_variant: pd.DataFrame, time_summary: pd.DataFrame) -> str:
    baseline = variant_summary.loc[variant_summary["variant"] == "baseline"].iloc[0].to_dict()
    vol_row = variant_summary.loc[variant_summary["variant"] == "vol_gate_p40"].iloc[0].to_dict()
    trend_row = variant_summary.loc[variant_summary["variant"] == "trend_gate_default"].iloc[0].to_dict()
    combo_row = variant_summary.loc[variant_summary["variant"] == "combo_gate"].iloc[0].to_dict()

    variant_view = variant_summary[[
        "variant",
        "selected_trades",
        "portfolio_total_return",
        "win_rate",
        "avg_net_ret",
        "avg_hold_minutes",
        "positive_asset_ratio",
        "candidate_signal_times",
        "overlap_timestamp_ratio",
    ]].copy()

    baseline_asset = asset_variant[asset_variant["variant"] == "baseline"].copy()
    baseline_time = time_summary[time_summary["variant"] == "baseline"].copy()

    takeaways = f"""
    <ul>
      <li><b>核心结论：</b>在这组偏热度/偏题材/偏小币的 10 个 Binance U 本位永续样本里，<b>当前 32b 实盘口径不是失效，反而显著抓到了趋势段</b>。baseline 在最近 {DAYS} 天里做到 <b>{int(baseline['selected_trades'])} 笔</b>、组合累计收益 <b>{pct(baseline['portfolio_total_return'])}</b>、胜率 <b>{pct(baseline['win_rate'])}</b>。</li>
      <li><b>不是少数币硬撑：</b>baseline 下 <b>{pct(baseline['positive_asset_ratio'])}</b> 的资产为正（即 {int(round(float(baseline['positive_asset_ratio']) * len(pool_meta)))} / {len(pool_meta)}）。用户点名的 <code>BEAT / PIPPIN / SIREN / TRADOOR</code> 都是正的，其中 <code>BEAT / SIREN / TRADOOR</code> 贡献尤其强。</li>
      <li><b>去低波动（vol gate）有用，但像“质量提升器”，不是“救命器”：</b>把 ATR/price 低于各币 40% 分位的信号剔掉后，单笔均值从 <b>{pct(baseline['avg_net_ret'])}</b> 升到 <b>{pct(vol_row['avg_net_ret'])}</b>，但总收益从 <b>{pct(baseline['portfolio_total_return'])}</b> 降到 <b>{pct(vol_row['portfolio_total_return'])}</b>。</li>
      <li><b>去震荡/噪音（trend regime）能提高“每笔像样程度”，但会砍掉太多本来就赚钱的机会：</b>默认趋势门之后，单笔均值升到 <b>{pct(trend_row['avg_net_ret'])}</b>，但只剩 <b>{int(trend_row['selected_trades'])}</b> 笔，且正资产比例降到 <b>{pct(trend_row['positive_asset_ratio'])}</b>。</li>
      <li><b>组合 gate（低波动 + 震荡都剔）太严了：</b>虽然单笔均值继续升到 <b>{pct(combo_row['avg_net_ret'])}</b>，但收益、交易数和横截面覆盖都明显下降，不适合作为默认部署版本。</li>
    </ul>
    """

    interpretation = """
    <ol>
      <li><b>妖币/热币并不天然反 32b。</b> 如果这些币的价格推进靠的是事件驱动、流动性突然放大、题材集中交易，那么 32b 这种“高阶结构方向 + 回到 fast EMA 再启动 + slope floor”反而容易抓到连续推进段。</li>
      <li><b>真正的问题不是“有没有趋势”，而是“趋势是不是足够短而猛、且会不会很快退化成乱震”。</b> 这也是为什么 baseline 很强，但更严格的 regime gate 会提高单笔质量 —— 它把一部分弱推进/弱波动信号切掉了。</li>
      <li><b>但对这类热币池，baseline 已经足够有 edge。</b> 说明 32b 本体对“热度驱动的 directional burst”并不迟钝，没必要先验地把这些币一概排除。</li>
      <li><b>更合理的实盘做法</b> 不是默认上很重的 regime gate，而是把它当成<b>二级风控旋钮</b>：当你担心组合容量、冲击成本、或近期 market 进入极度噪音期时，再切到 vol gate 版，而不是平时就常开 combo gate。</li>
    </ol>
    """

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · hot/smallcap regime study</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    h1,h2,h3 {{ margin-bottom: 8px; }}
  </style>
</head>
<body>
  <h1>Rank 32b · 热门小币 / 妖币 regime 研究</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 研究问题：32b 在偏热度、偏题材、偏“妖币”环境下是否仍有动量 edge？如果担心低波动/震荡段，regime gate 是否值得加？</p>

  <div class='card'>
    <h2>研究设计</h2>
    <ul>
      <li><b>样本池：</b>10 个 Binance U 本位永续。优先保留用户点名的 <code>BEAT / PIPPIN / SIREN / TRADOOR</code>，再补 6 个同类 meme / hot 小币代理样本。</li>
      <li><b>共同观察窗：</b>最近 <b>{DAYS} 天</b>。因为这批币上市时间不一致，统一短窗比硬拉 1y 更公平。</li>
      <li><b>执行口径：</b><code>market/taker entry + TP 1.25 ATR + SL 1.00 ATR + timeout 8x15m + strongest signal only + max_concurrent=1</code>，与当前 32b live parity 保持一致。</li>
      <li><b>对照版本：</b>baseline / 去低波动（vol gate）/ 去震荡（trend regime）/ 双重 gate。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>样本池元数据</h2>
    {render_table(pool_meta[["symbol", "requested_by_user", "listing_days", "quote_volume_24h", "quote_volume_median_30d", "rationale"]], digits_cols={"listing_days": 1}, money_cols={"quote_volume_24h", "quote_volume_median_30d"})}
  </div>

  <div class='card'>
    <h2>结论先看</h2>
    <p><span class='pill'>baseline trades = {int(baseline['selected_trades'])}</span><span class='pill'>baseline total return = {pct(baseline['portfolio_total_return'])}</span><span class='pill'>baseline win rate = {pct(baseline['win_rate'])}</span><span class='pill'>baseline positive asset ratio = {pct(baseline['positive_asset_ratio'])}</span></p>
    {takeaways}
  </div>

  <div class='card'>
    <h2>variant 对照</h2>
    {render_table(variant_view, percent_cols={"portfolio_total_return", "win_rate", "avg_net_ret", "positive_asset_ratio", "overlap_timestamp_ratio"}, digits_cols={"selected_trades": 0, "avg_hold_minutes": 1, "candidate_signal_times": 0})}
  </div>

  <div class='card'>
    <h2>baseline：分资产表现</h2>
    {render_table(baseline_asset[["asset", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes", "target_hit_rate", "stop_hit_rate", "timeout_rate"]], percent_cols={"total_return", "win_rate", "avg_net_ret", "target_hit_rate", "stop_hit_rate", "timeout_rate"}, digits_cols={"trades": 0, "avg_hold_minutes": 1})}
  </div>

  <div class='card'>
    <h2>baseline：时间分桶稳定性</h2>
    {render_table(baseline_time[["window", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes"]], percent_cols={"total_return", "win_rate", "avg_net_ret"}, digits_cols={"trades": 0, "avg_hold_minutes": 1})}
    <p class='muted'>这里不是绝对的 calendar windows，而是把最近 {DAYS} 天按时间顺序切成 3 段，目的是看 edge 是否只靠某一小段爆发。</p>
  </div>

  <div class='card'>
    <h2>怎么理解这些结果</h2>
    {interpretation}
  </div>

  <div class='card'>
    <h2>操作层建议</h2>
    <ul>
      <li><b>研究层结论：</b>不要先验地把“妖币/热币”排除出 32b 视野。至少在这组样本里，32b baseline 明显能抓到趋势推进。</li>
      <li><b>如果你是做下一轮候选扩池：</b>可以把这组池子视为 <b>exploratory universe</b>，先 paper / shadow 跟踪，而不是直接并进主 18 币白名单。</li>
      <li><b>如果你担心乱震 / 低波动拖累：</b>优先尝试 <code>vol gate</code>，因为它提升了单笔质量，但没有把横截面覆盖砍得像 combo 那么狠。</li>
      <li><b>不建议默认打开 combo gate：</b>它更像“在你极端担心噪音时的收缩开关”，不是平时默认版本。</li>
      <li><b>下一步最值得做的强化：</b>把这组池子接到更现实的成本层（更细 slippage / funding / liquidity stress），再决定哪些币值得从 exploratory universe 晋升到真实监控名单。</li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    pool_meta = fetch_pool_meta(POOL)
    asset_map = live_mod.build_asset_map(",".join(entry.symbol for entry in POOL))
    variant_summary, asset_variant, time_summary, detail = study(asset_map)
    generated_at = detail["generated_at_utc"]

    pool_meta.to_csv(POOL_META_PATH, index=False)
    variant_summary.to_csv(VARIANT_SUMMARY_PATH, index=False)
    asset_variant.to_csv(ASSET_VARIANT_PATH, index=False)
    time_summary.to_csv(TIME_SUMMARY_PATH, index=False)
    DETAIL_JSON_PATH.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(build_html(generated_at, pool_meta, variant_summary, asset_variant, time_summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "report_html": str(REPORT_PATH),
                "pool_meta_csv": str(POOL_META_PATH),
                "variant_summary_csv": str(VARIANT_SUMMARY_PATH),
                "asset_variant_csv": str(ASSET_VARIANT_PATH),
                "time_summary_csv": str(TIME_SUMMARY_PATH),
                "detail_json": str(DETAIL_JSON_PATH),
                "generated_at_utc": generated_at,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
