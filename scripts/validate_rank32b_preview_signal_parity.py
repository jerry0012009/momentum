#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import importlib.util

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ART_ROOT = ROOT / "reports" / "artifacts" / "rank32b_preview_signal_parity"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


preview_mod = load_module(ROOT / "scripts" / "build_rank32b_unclosed15m_preview_backtest.py", "rank32b_preview_bt_mod")
perp_mod = load_module(ROOT / "scripts" / "build_rank32b_perp_funding_probe.py", "rank32b_perp_probe_mod")
signal_adapter_mod = load_module(ROOT / "src" / "momentum" / "execution" / "canary32b" / "signal_adapter.py", "rank32b_signal_adapter_mod")


DEFAULT_ASSET_TO_SYMBOL = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "ADA-USD": "ADAUSDT",
    "LINK-USD": "LINKUSDT",
    "AVAX-USD": "AVAXUSDT",
    "DOT-USD": "DOTUSDT",
    "LTC-USD": "LTCUSDT",
    "BCH-USD": "BCHUSDT",
    "UNI-USD": "UNIUSDT",
    "AAVE-USD": "AAVEUSDT",
    "MKR-USD": "MKRUSDT",
    "COMP-USD": "COMPUSDT",
    "SNX-USD": "SNXUSDT",
    "CRV-USD": "CRVUSDT",
    "BEAT-USD": "BEATUSDT",
}


def invert_map(asset_to_symbol: dict[str, str]) -> dict[str, str]:
    return {symbol: asset for asset, symbol in asset_to_symbol.items()}


def first_offline_preview_rows(asset: str, symbol: str, minute_df: pd.DataFrame) -> pd.DataFrame:
    hour_df = preview_mod.build_completed_hours(minute_df)
    bars15 = preview_mod.build_completed_15m(minute_df, hour_df)
    preview_df = preview_mod.build_preview_minutes(minute_df, hour_df, bars15)
    return preview_mod.first_preview_rows(asset, symbol, preview_df)


def build_live_like_preview_rows(asset: str, symbol: str, minute_df: pd.DataFrame, bars: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    hour_df = signal_adapter_mod._build_completed_hours_from_15m(bars)
    bars15 = signal_adapter_mod._build_completed_15m_reference(bars, hour_df)
    for bucket_start, bucket_rows in minute_df.groupby(minute_df["open_ts"].dt.floor("15min"), sort=True):
        signal = signal_adapter_mod.build_preview_signal_from_bucket_rows(
            asset=asset,
            symbol=symbol,
            bars=bars,
            bucket_rows=bucket_rows.copy(),
            cutoff=pd.Timestamp.min.tz_localize("UTC"),
            current_bucket=pd.to_datetime(bucket_start, utc=True),
            now_utc=pd.to_datetime(bucket_rows["close_ts"].max(), utc=True),
            official_signal_ttl_minutes=None,
            alpha_version="parity_check_preview_v2",
            hour_df=hour_df,
            bars15=bars15,
        )
        if signal is None:
            continue
        meta = signal.metadata or {}
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bucket_start": meta.get("bucket_start"),
                "live_preview_ts": signal.timestamp,
                "live_preview_dir": signal.side.value,
                "live_signal_price": signal.signal_price,
                "live_fast_slope": meta.get("fast_slope"),
                "live_slow_slope": meta.get("slow_slope"),
                "live_prev15_close": meta.get("prev15_close"),
                "live_prev15_fast": meta.get("prev15_fast"),
            }
        )
    return pd.DataFrame(rows)


def compare_symbol(asset: str, symbol: str, days: int, refresh: bool) -> tuple[pd.DataFrame, dict[str, object]]:
    minute_df = preview_mod.load_or_fetch_1m(symbol, days=days, refresh=refresh)
    minute_df = minute_df.sort_values("open_ts").reset_index(drop=True)
    bars = perp_mod.load_or_fetch_perp_bars(symbol, days=days, refresh=refresh, incremental_refresh_days=(2 if refresh else None))
    bars = bars.copy()
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)

    offline = first_offline_preview_rows(asset, symbol, minute_df)
    live_like = build_live_like_preview_rows(asset, symbol, minute_df, bars)

    if offline.empty:
        offline_cmp = pd.DataFrame(columns=["bucket_start", "offline_preview_ts", "offline_preview_dir", "offline_signal_price", "offline_fast_slope", "offline_slow_slope"])
    else:
        offline_cmp = offline.rename(
            columns={
                "preview_ts": "offline_preview_ts",
                "preview_dir": "offline_preview_dir",
                "preview_price": "offline_signal_price",
                "preview_fast_slope": "offline_fast_slope",
                "preview_slow_slope": "offline_slow_slope",
            }
        ).copy()
        offline_cmp["offline_preview_dir"] = offline_cmp["offline_preview_dir"].map({1: "long", -1: "short"})
        offline_cmp["bucket_start"] = pd.to_datetime(offline_cmp["bucket_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        offline_cmp["offline_preview_ts"] = pd.to_datetime(offline_cmp["offline_preview_ts"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    if live_like.empty:
        live_cmp = pd.DataFrame(columns=["bucket_start", "live_preview_ts", "live_preview_dir", "live_signal_price", "live_fast_slope", "live_slow_slope", "live_prev15_close", "live_prev15_fast"])
    else:
        live_cmp = live_like.copy()

    merged = live_cmp.merge(offline_cmp, on=["asset", "symbol", "bucket_start"], how="outer")

    def classify(row: pd.Series) -> str:
        live_dir = row.get("live_preview_dir")
        offline_dir = row.get("offline_preview_dir")
        if pd.isna(live_dir) and pd.isna(offline_dir):
            return "none"
        if pd.isna(live_dir):
            return "offline_only"
        if pd.isna(offline_dir):
            return "live_only"
        if str(live_dir) != str(offline_dir):
            return "direction_mismatch"
        if str(row.get("live_preview_ts")) != str(row.get("offline_preview_ts")):
            return "timestamp_mismatch"
        return "match"

    if merged.empty:
        merged = pd.DataFrame(columns=["asset", "symbol", "bucket_start", "status"])
    else:
        merged["status"] = merged.apply(classify, axis=1)
        merged = merged.sort_values("bucket_start").reset_index(drop=True)

    summary = {
        "asset": asset,
        "symbol": symbol,
        "rows": int(len(merged)),
        "match": int((merged.get("status") == "match").sum()) if "status" in merged else 0,
        "live_only": int((merged.get("status") == "live_only").sum()) if "status" in merged else 0,
        "offline_only": int((merged.get("status") == "offline_only").sum()) if "status" in merged else 0,
        "direction_mismatch": int((merged.get("status") == "direction_mismatch").sum()) if "status" in merged else 0,
        "timestamp_mismatch": int((merged.get("status") == "timestamp_mismatch").sum()) if "status" in merged else 0,
    }
    return merged, summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare rank32b live-like preview signals vs offline preview replay.")
    ap.add_argument("--symbols", default="BEATUSDT", help="Comma-separated symbols, e.g. BEATUSDT,BTCUSDT")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--tag", default="latest")
    args = ap.parse_args()

    symbol_to_asset = invert_map(DEFAULT_ASSET_TO_SYMBOL)
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    out_dir = ART_ROOT / args.tag
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    for symbol in symbols:
        asset = symbol_to_asset.get(symbol, symbol.replace("USDT", "-USD"))
        merged, summary = compare_symbol(asset=asset, symbol=symbol, days=args.days, refresh=args.refresh)
        merged.to_csv(out_dir / f"{symbol.lower()}_parity.csv", index=False)
        summary_rows.append(summary)
        print(json.dumps(summary, ensure_ascii=False))

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out_dir / "summary.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"artifacts: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
