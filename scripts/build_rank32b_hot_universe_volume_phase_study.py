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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_hot_universe_volume_phase_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_hot_universe_volume_phase_15m"
REPORT_PATH = SITE_DIR / "report.html"
POOL_META_PATH = ART_DIR / "pool_meta.csv"
VARIANT_SUMMARY_PATH = ART_DIR / "variant_summary.csv"
ASSET_VARIANT_PATH = ART_DIR / "variant_asset_summary.csv"
PHASE_SUMMARY_PATH = ART_DIR / "selected_trade_phase_summary.csv"
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
HOT_Q = 0.70
COLD_Q = 0.30


@dataclass(frozen=True)
class PoolEntry:
    symbol: str
    rationale: str
    requested_by_user: bool = False


POOL = [
    PoolEntry("BEATUSDT", "用户点名；近几个月高热度/新上市题材币", True),
    PoolEntry("PIPPINUSDT", "用户点名；持续高成交的题材小币", True),
    PoolEntry("SIRENUSDT", "用户点名；热度爆发极强的样本", True),
    PoolEntry("TRADOORUSDT", "用户点名；较新、爆量倍率高", True),
    PoolEntry("WIFUSDT", "过去一年 meme 热门代表"),
    PoolEntry("PNUTUSDT", "过去一年 meme/hot coin 热门代表"),
    PoolEntry("PENGUUSDT", "过去一年高热度 meme 样本"),
    PoolEntry("MOODENGUSDT", "过去一年典型热度驱动样本"),
    PoolEntry("HIPPOUSDT", "高波动、退潮快的小币样本"),
    PoolEntry("FARTCOINUSDT", "过去一年热度非常高的 meme 样本"),
    PoolEntry("GOATUSDT", "较低流动性的热度样本，用来看退潮后是否失效"),
    PoolEntry("ACTUSDT", "AI/题材热币代理样本"),
    PoolEntry("1000PEPEUSDT", "老牌高热度 meme proxy"),
    PoolEntry("1000BONKUSDT", "Solana meme 热门代理样本"),
    PoolEntry("POPCATUSDT", "过去一年热门 meme 代理样本"),
    PoolEntry("BOMEUSDT", "高热度 meme/题材代理样本"),
    PoolEntry("MEMEUSDT", "Memeland 主题高热度样本"),
    PoolEntry("MEWUSDT", "过去一年 meme 热点代理样本"),
    PoolEntry("NEIROUSDT", "过去一年热度较高的狗系/题材样本"),
    PoolEntry("BRETTUSDT", "Base 系热门 meme 样本"),
    PoolEntry("TURBOUSDT", "过去一年热度与成交都较活跃"),
    PoolEntry("CATIUSDT", "热门新叙事但常见退潮场景"),
    PoolEntry("NOTUSDT", "Telegram 叙事高热度样本"),
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


live_mod = load_module(LIVE_PARITY_SCRIPT, "rank32b_live_parity_hot_universe")


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
    body_rows: list[str] = []
    for _, row in df.iterrows():
        cols: list[str] = []
        for c in df.columns:
            v = row[c]
            if c in percent_cols:
                text = pct(v)
            elif c in money_cols:
                text = money_m(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(c, 2))
            else:
                text = str(v)
            cols.append(f"<td>{escape(text)}</td>")
        body_rows.append(f"<tr>{''.join(cols)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def fetch_pool_meta(pool: list[PoolEntry]) -> pd.DataFrame:
    exchange_info = fetch_json(FUTURES_EXCHANGE_INFO)
    ticker_24h = {row["symbol"]: row for row in fetch_json(FUTURES_TICKER_24H)}
    symbol_rows = {row["symbol"]: row for row in exchange_info["symbols"]}
    now_ms = time.time() * 1000.0
    rows: list[dict[str, object]] = []
    for entry in pool:
        row = symbol_rows.get(entry.symbol)
        if not row:
            continue
        params = urllib.parse.urlencode({"symbol": entry.symbol, "interval": "1d", "limit": DAYS})
        klines = fetch_json(f"{FUTURES_KLINES}?{params}")
        quote_volumes = [float(x[7]) for x in klines] if klines else []
        ticker = ticker_24h.get(entry.symbol, {})
        rows.append(
            {
                "symbol": entry.symbol,
                "asset": entry.symbol.replace("USDT", "-USD"),
                "requested_by_user": entry.requested_by_user,
                "listing_days": (now_ms - float(row.get("onboardDate") or 0.0)) / 1000.0 / 86400.0,
                "quote_volume_24h": float(ticker.get("quoteVolume") or 0.0),
                "quote_volume_median_120d": float(statistics.median(quote_volumes)) if quote_volumes else np.nan,
                "quote_volume_top_120d": max(quote_volumes) if quote_volumes else np.nan,
                "heat_ratio_120d": (max(quote_volumes) / max(statistics.median(quote_volumes), 1.0)) if quote_volumes else np.nan,
                "rationale": entry.rationale,
            }
        )
    return pd.DataFrame(rows).sort_values(["requested_by_user", "heat_ratio_120d", "quote_volume_median_120d"], ascending=[False, False, False]).reset_index(drop=True)


def build_daily_phase_map(symbol: str, days: int) -> pd.DataFrame:
    params = urllib.parse.urlencode({"symbol": symbol, "interval": "1d", "limit": days})
    rows = fetch_json(f"{FUTURES_KLINES}?{params}")
    df = pd.DataFrame(
        {
            "date": [pd.to_datetime(int(r[0]), unit="ms", utc=True).normalize() for r in rows],
            "daily_quote_volume": [float(r[7]) for r in rows],
        }
    )
    hot_thr = df["daily_quote_volume"].quantile(HOT_Q)
    cold_thr = df["daily_quote_volume"].quantile(COLD_Q)
    df["volume_phase"] = np.where(
        df["daily_quote_volume"] >= hot_thr,
        "hot_volume",
        np.where(df["daily_quote_volume"] <= cold_thr, "cold_volume", "normal_volume"),
    )
    return df


def summarize_subset(trades: pd.DataFrame) -> dict[str, float | int]:
    if trades.empty:
        return {
            "trades": 0,
            "portfolio_total_return": np.nan,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "avg_hold_minutes": np.nan,
            "positive_assets": 0,
            "active_assets": 0,
            "positive_asset_ratio": np.nan,
        }
    asset_grp = trades.groupby("asset")
    asset_total = asset_grp["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
    active_assets = int(asset_total.shape[0])
    positive_assets = int((asset_total > 0).sum())
    return {
        "trades": int(len(trades)),
        "portfolio_total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "avg_hold_minutes": float(trades["hold_minutes"].mean()),
        "positive_assets": positive_assets,
        "active_assets": active_assets,
        "positive_asset_ratio": float(positive_assets / active_assets) if active_assets else np.nan,
    }


def build_time_buckets(trades: pd.DataFrame, variant: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "window", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes"])
    work = trades.copy().sort_values("entry_ts").reset_index(drop=True)
    start = work["entry_ts"].min()
    end = work["entry_ts"].max()
    span = max((end - start).total_seconds(), 1.0)
    cut1 = start + pd.Timedelta(seconds=span / 3)
    cut2 = start + pd.Timedelta(seconds=span * 2 / 3)
    pieces = [
        ("early_third", work[work["entry_ts"] < cut1]),
        ("middle_third", work[(work["entry_ts"] >= cut1) & (work["entry_ts"] < cut2)]),
        ("late_third", work[work["entry_ts"] >= cut2]),
    ]
    rows: list[dict[str, object]] = []
    for name, part in pieces:
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


def simulate_candidates_with_metrics(pool: list[PoolEntry], days: int) -> pd.DataFrame:
    asset_map = live_mod.build_asset_map(",".join(entry.symbol for entry in pool))
    rows: list[dict[str, object]] = []
    for asset, symbol in asset_map.items():
        phase_map = build_daily_phase_map(symbol, days)
        phase_lookup = dict(zip(phase_map["date"], phase_map["volume_phase"]))
        volume_lookup = dict(zip(phase_map["date"], phase_map["daily_quote_volume"]))

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
            sig_idx = int(trade["signal_idx"])
            frow = frame.iloc[sig_idx]
            entry_ts = pd.to_datetime(trade["entry_ts"], utc=True)
            direction_sign = int(trade["direction_sign"])
            phase_date = entry_ts.normalize()
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
                    "daily_quote_volume": float(volume_lookup.get(phase_date, np.nan)),
                    "volume_phase": phase_lookup.get(phase_date, "normal_volume"),
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
        "baseline_all": work,
        "hot_phase_only": work[work["volume_phase"] == "hot_volume"].copy(),
        "normal_phase_only": work[work["volume_phase"] == "normal_volume"].copy(),
        "cold_phase_only": work[work["volume_phase"] == "cold_volume"].copy(),
        "cold_phase_vol_gate": work[(work["volume_phase"] == "cold_volume") & work["vol_gate_p40"]].copy(),
        "cold_phase_trend_gate": work[(work["volume_phase"] == "cold_volume") & work["trend_gate_default"]].copy(),
        "cold_phase_combo_gate": work[(work["volume_phase"] == "cold_volume") & work["combo_gate"]].copy(),
    }


def study(pool: list[PoolEntry]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    asset_map = live_mod.build_asset_map(",".join(entry.symbol for entry in pool))
    candidates = simulate_candidates_with_metrics(pool, DAYS)
    variants = build_variants(candidates)
    summary_rows: list[dict[str, object]] = []
    asset_rows: list[pd.DataFrame] = []
    time_rows: list[pd.DataFrame] = []
    phase_rows: list[dict[str, object]] = []
    detail: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": DAYS,
        "tp_atr_mult": TP_MULT,
        "sl_atr_mult": SL_MULT,
        "timeout_15m": TIMEOUT_15M,
        "max_concurrent": MAX_CONCURRENT,
        "hot_quantile": HOT_Q,
        "cold_quantile": COLD_Q,
        "volatility_quantile_floor": VOL_Q,
        "symbols": list(asset_map.values()),
    }
    for name, df in variants.items():
        selected, selection_stats = live_mod.apply_live_selection(df, strongest_only_per_bar=True, max_concurrent_positions=MAX_CONCURRENT)
        portfolio = live_mod.summarize_portfolio(selected, selection_stats, df)
        asset_summary = live_mod.summarize_assets(selected, asset_map)
        positive_asset_ratio = float((asset_summary["total_return"] > 0).mean()) if not asset_summary.empty else np.nan
        summary_rows.append({
            "variant": name,
            **{k: v for k, v in portfolio.items() if k != "selection_stats"},
            "positive_asset_ratio": positive_asset_ratio,
        })
        variant_asset = asset_summary.copy()
        variant_asset.insert(0, "variant", name)
        asset_rows.append(variant_asset)
        time_rows.append(build_time_buckets(selected, name))
        if not selected.empty:
            for phase_name, part in selected.groupby("volume_phase"):
                phase_rows.append({"variant": name, "phase": phase_name, **summarize_subset(part)})
        detail[name] = {**{k: v for k, v in portfolio.items() if k != "selection_stats"}, "positive_asset_ratio": positive_asset_ratio}
    return pd.DataFrame(summary_rows), pd.concat(asset_rows, ignore_index=True), pd.concat(time_rows, ignore_index=True), pd.DataFrame(phase_rows), detail


def build_html(generated_at: str, pool_meta: pd.DataFrame, variant_summary: pd.DataFrame, asset_variant: pd.DataFrame, phase_summary: pd.DataFrame, time_summary: pd.DataFrame) -> str:
    baseline = variant_summary.loc[variant_summary["variant"] == "baseline_all"].iloc[0].to_dict()
    hot_only = variant_summary.loc[variant_summary["variant"] == "hot_phase_only"].iloc[0].to_dict()
    cold_only = variant_summary.loc[variant_summary["variant"] == "cold_phase_only"].iloc[0].to_dict()
    cold_vol = variant_summary.loc[variant_summary["variant"] == "cold_phase_vol_gate"].iloc[0].to_dict()
    cold_trend = variant_summary.loc[variant_summary["variant"] == "cold_phase_trend_gate"].iloc[0].to_dict()
    cold_combo = variant_summary.loc[variant_summary["variant"] == "cold_phase_combo_gate"].iloc[0].to_dict()

    baseline_asset = asset_variant[asset_variant["variant"] == "baseline_all"].copy()
    baseline_time = time_summary[time_summary["variant"] == "baseline_all"].copy()
    baseline_phase = phase_summary[phase_summary["variant"] == "baseline_all"].copy()

    takeaway_html = f"""
    <ul>
      <li><b>扩池后结论依然成立：</b>在 23 个过去一年确实“火过”的 Binance 永续热门币池里，32b baseline 在最近 {DAYS} 天内做到 <b>{int(baseline['selected_trades'])} 笔</b>、组合累计收益 <b>{pct(baseline['portfolio_total_return'])}</b>、胜率 <b>{pct(baseline['win_rate'])}</b>，且正资产比例为 <b>{pct(baseline['positive_asset_ratio'])}</b>。</li>
      <li><b>不是只在火爆期有效：</b>如果只看爆量热期，收益确实更强（hot phase only 累计 <b>{pct(hot_only['portfolio_total_return'])}</b>，单笔 <b>{pct(hot_only['avg_net_ret'])}</b>）；但冷期并没有直接归零——cold phase only 仍有 <b>{int(cold_only['selected_trades'])}</b> 笔，累计收益 <b>{pct(cold_only['portfolio_total_return'])}</b>，说明 edge 没有完全消失。</li>
      <li><b>你的担心也是真的：</b>退潮后的低活跃期质量明显变差。和热期相比，cold phase 的单笔收益、胜率、正资产覆盖都更弱，说明“币已经火过了、现在不火了”确实会削弱 32b。</li>
      <li><b>如果专门想处理冷期拖累，regime gate 有帮助：</b>在 cold phase 里，vol gate / trend gate / combo gate 都能提升单笔质量，其中 <b>cold vol gate</b> 是最平衡的折中；combo gate 虽然更纯，但会砍掉太多交易。</li>
      <li><b>实盘启示：</b>这些热门币可以做 32b 的 <b>exploratory universe</b>，但不建议“不分冷热地长期硬监控”。更合理的是：保留一个动态候选池，只有在它们仍处于较高活跃/较高波动/较清晰趋势阶段时才提权。</li>
    </ul>
    """

    interpretation_html = """
    <ol>
      <li><b>妖币/热币的 alpha 来自“注意力冲击 + 流动性加速 + 短期趋势推进”。</b> 这类段落正是 32b 容易抓到的，所以热期表现强并不意外。</li>
      <li><b>退潮期不是完全没机会，但结构从“连续推进”变成“偶发脉冲 + 更多噪音”。</b> 这会直接拉低胜率与单位收益。</li>
      <li><b>因此，研究问题的答案不是“它们是不是 32b 标的”这种二元判断，而是“它们在什么 phase 下是好标的”。</b></li>
      <li><b>最合理的实盘设计</b> 是把热门币放进动态观察池，再用 activity / volatility / trend regime 做晋升与降权，而不是全年无条件常驻。</li>
    </ol>
    """

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

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · hot universe volume-phase study</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1220px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <h1>Rank 32b · 热门币扩大池 + 热度阶段研究</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 目标：把热门币池扩大到过去一年 Binance 永续里真正“火过”的样本，并验证 32b 是否只在火爆期有效，还是在退潮期也仍保留 edge。</p>

  <div class='card'>
    <h2>研究设计</h2>
    <ul>
      <li><b>扩大池：</b>23 个 Binance U 本位永续热门币，兼顾用户点名币与过去一年高热度 meme / 题材币。</li>
      <li><b>共同观察窗：</b>最近 <b>{DAYS} 天</b>。因为 BEAT 等新币上市较晚，统一短窗更公平。</li>
      <li><b>执行口径：</b><code>market/taker entry + TP 1.25 ATR + SL 1.00 ATR + timeout 8x15m + strongest-only + max_concurrent=1</code>。</li>
      <li><b>热度阶段定义：</b>按每个币自己的日度 quote volume 分位数切分：上 30% = <b>hot_volume</b>，下 30% = <b>cold_volume</b>，中间 = <b>normal_volume</b>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>扩大池元数据</h2>
    {render_table(pool_meta[["symbol", "requested_by_user", "listing_days", "quote_volume_24h", "quote_volume_median_120d", "quote_volume_top_120d", "heat_ratio_120d", "rationale"]], digits_cols={"listing_days":1, "heat_ratio_120d":1}, money_cols={"quote_volume_24h", "quote_volume_median_120d", "quote_volume_top_120d"})}
  </div>

  <div class='card'>
    <h2>结论先看</h2>
    <p>
      <span class='pill'>baseline trades = {int(baseline['selected_trades'])}</span>
      <span class='pill'>baseline total return = {pct(baseline['portfolio_total_return'])}</span>
      <span class='pill'>hot-only total return = {pct(hot_only['portfolio_total_return'])}</span>
      <span class='pill'>cold-only total return = {pct(cold_only['portfolio_total_return'])}</span>
      <span class='pill'>cold vol-gate total return = {pct(cold_vol['portfolio_total_return'])}</span>
    </p>
    {takeaway_html}
  </div>

  <div class='card'>
    <h2>variant 对照</h2>
    {render_table(variant_view, percent_cols={"portfolio_total_return", "win_rate", "avg_net_ret", "positive_asset_ratio", "overlap_timestamp_ratio"}, digits_cols={"selected_trades":0, "avg_hold_minutes":1, "candidate_signal_times":0})}
  </div>

  <div class='card'>
    <h2>baseline：选中交易按热度阶段拆分</h2>
    {render_table(baseline_phase[["phase", "trades", "portfolio_total_return", "win_rate", "avg_net_ret", "avg_hold_minutes", "positive_assets", "active_assets", "positive_asset_ratio"]], percent_cols={"portfolio_total_return", "win_rate", "avg_net_ret", "positive_asset_ratio"}, digits_cols={"trades":0, "avg_hold_minutes":1, "positive_assets":0, "active_assets":0})}
  </div>

  <div class='card'>
    <h2>baseline：分资产表现</h2>
    {render_table(baseline_asset[["asset", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes", "target_hit_rate", "stop_hit_rate", "timeout_rate"]], percent_cols={"total_return", "win_rate", "avg_net_ret", "target_hit_rate", "stop_hit_rate", "timeout_rate"}, digits_cols={"trades":0, "avg_hold_minutes":1})}
  </div>

  <div class='card'>
    <h2>baseline：时间分段稳定性</h2>
    {render_table(baseline_time[["window", "trades", "total_return", "win_rate", "avg_net_ret", "avg_hold_minutes"]], percent_cols={"total_return", "win_rate", "avg_net_ret"}, digits_cols={"trades":0, "avg_hold_minutes":1})}
    <p class='muted'>这里是把最近 {DAYS} 天按时间顺序切 3 段，检查 edge 是否只靠某一小段爆发期。</p>
  </div>

  <div class='card'>
    <h2>怎么理解“火的时候有效、冷的时候会不会失效”</h2>
    {interpretation_html}
  </div>

  <div class='card'>
    <h2>操作建议</h2>
    <ul>
      <li><b>这些热门币不是不能做 32b，反而很多是好材料。</b> 但它们更像“阶段性优质标的”，不是全年同权常驻白名单。</li>
      <li><b>实盘上最合理的做法：</b>建立 <code>hot exploratory universe</code>，按最近 activity / volume / trend regime 做晋升与降权。</li>
      <li><b>如果你要做下一轮更贴实盘的版本：</b>建议把热度阶段过滤器真正接进 live ranking（例如：最近 7d quote-volume percentile、ATR/price floor、trend regime score），而不是只在研究里看。</li>
      <li><b>默认不建议全年盲开：</b>对这类币，退潮期会明显拖累，说明“热度仍在”本身就是一个重要条件。</li>
      <li><b>冷期如果一定要做：</b><code>cold_phase_vol_gate</code> 比较像实用版折中；combo gate 太狠，更像风险极高时的收缩开关。</li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    pool_meta = fetch_pool_meta(POOL)
    variant_summary, asset_variant, time_summary, phase_summary, detail = study(POOL)
    generated_at = detail["generated_at_utc"]

    pool_meta.to_csv(POOL_META_PATH, index=False)
    variant_summary.to_csv(VARIANT_SUMMARY_PATH, index=False)
    asset_variant.to_csv(ASSET_VARIANT_PATH, index=False)
    phase_summary.to_csv(PHASE_SUMMARY_PATH, index=False)
    time_summary.to_csv(TIME_SUMMARY_PATH, index=False)
    DETAIL_JSON_PATH.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(build_html(generated_at, pool_meta, variant_summary, asset_variant, phase_summary, time_summary), encoding="utf-8")

    print(json.dumps({
        "report_html": str(REPORT_PATH),
        "pool_meta_csv": str(POOL_META_PATH),
        "variant_summary_csv": str(VARIANT_SUMMARY_PATH),
        "asset_variant_csv": str(ASSET_VARIANT_PATH),
        "phase_summary_csv": str(PHASE_SUMMARY_PATH),
        "time_summary_csv": str(TIME_SUMMARY_PATH),
        "detail_json": str(DETAIL_JSON_PATH),
        "generated_at_utc": generated_at,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
