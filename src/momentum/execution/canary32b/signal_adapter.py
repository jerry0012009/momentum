from __future__ import annotations

import hashlib
import importlib.util
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import requests

from momentum.domain.canary32b_models import AlphaSignal, Side

ROOT = Path(__file__).resolve().parents[4]
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
EXT_SCRIPT = ROOT / "scripts" / "build_rank32b_extended_history_probe.py"
PERP_SCRIPT = ROOT / "scripts" / "build_rank32b_perp_funding_probe.py"
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
DEFAULT_ASSET_TO_SYMBOL = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
}
RECENT_1M_URL = "https://fapi.binance.com/fapi/v1/klines"
REQ_TIMEOUT = 15
ATR_PERIOD = 14


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base_mod = load_module(BASE_SCRIPT, "rank32_base_mod_canary")
ext_mod = load_module(EXT_SCRIPT, "rank32_ext_mod_canary")
perp_mod = load_module(PERP_SCRIPT, "rank32_perp_mod_canary")


@dataclass(slots=True)
class SignalSnapshot:
    signals: list[AlphaSignal]
    latest_bar_utc: str | None
    latest_signal_utc: str | None
    latest_observed_signal_utc: str | None


def compute_atr14(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    high = pd.to_numeric(frame.get("high"), errors="coerce")
    low = pd.to_numeric(frame.get("low"), errors="coerce")
    close = pd.to_numeric(frame.get("close"), errors="coerce")
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _build_completed_hours_from_15m(bars: pd.DataFrame) -> pd.DataFrame:
    work = bars.copy().sort_values("timestamp").reset_index(drop=True)
    work["hour_start"] = pd.to_datetime(work["timestamp"], utc=True).dt.floor("1h")
    hours = (
        work.groupby("hour_start", sort=True)
        .agg(hour_close=("close", "last"))
        .reset_index()
        .sort_values("hour_start")
        .reset_index(drop=True)
    )
    fast_vals: list[float] = []
    slow_vals: list[float] = []
    prev_fast = math.nan
    prev_slow = math.nan
    for close in hours["hour_close"].astype(float):
        if not math.isfinite(prev_fast):
            prev_fast = close
            prev_slow = close
        else:
            prev_fast = (2.0 / (base_mod.EMA_FAST_1H + 1.0)) * close + (1.0 - 2.0 / (base_mod.EMA_FAST_1H + 1.0)) * prev_fast
            prev_slow = (2.0 / (base_mod.EMA_SLOW_1H + 1.0)) * close + (1.0 - 2.0 / (base_mod.EMA_SLOW_1H + 1.0)) * prev_slow
        fast_vals.append(prev_fast)
        slow_vals.append(prev_slow)
    hours["ema_fast_hour"] = fast_vals
    hours["ema_slow_hour"] = slow_vals
    return hours


def _build_completed_15m_reference(bars: pd.DataFrame, hour_df: pd.DataFrame) -> pd.DataFrame:
    work = bars.copy().sort_values("timestamp").reset_index(drop=True)
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True)
    work["signal_confirmed_at"] = work["timestamp"] + pd.Timedelta(minutes=15)
    work["hour_start"] = work["signal_confirmed_at"].dt.floor("1h")

    hour_map = hour_df[["hour_start", "ema_fast_hour", "ema_slow_hour"]].copy()
    hour_map["prev_hour_start"] = hour_map["hour_start"] + pd.Timedelta(hours=1)
    hour_map = hour_map[["prev_hour_start", "ema_fast_hour", "ema_slow_hour"]].rename(
        columns={"prev_hour_start": "hour_start", "ema_fast_hour": "prev_hour_fast", "ema_slow_hour": "prev_hour_slow"}
    )
    work = work.merge(hour_map, on="hour_start", how="left")

    alpha_fast = 2.0 / (base_mod.EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (base_mod.EMA_SLOW_1H + 1.0)
    work["ema_fast_1h"] = alpha_fast * work["close"] + (1.0 - alpha_fast) * work["prev_hour_fast"]
    work["ema_slow_1h"] = alpha_slow * work["close"] + (1.0 - alpha_slow) * work["prev_hour_slow"]
    work["fast_slope"] = work["ema_fast_1h"] / work["prev_hour_fast"] - 1.0
    work["slow_slope"] = work["ema_slow_1h"] / work["prev_hour_slow"] - 1.0
    work["long_structure"] = (work["ema_fast_1h"] > work["ema_slow_1h"]).fillna(False)
    work["short_structure"] = (work["ema_fast_1h"] < work["ema_slow_1h"]).fillna(False)
    work["slope_floor_long"] = ((work["fast_slope"] > base_mod.SLOPE_FLOOR) & (work["slow_slope"] > 0)).fillna(False)
    work["slope_floor_short"] = ((work["fast_slope"] < -base_mod.SLOPE_FLOOR) & (work["slow_slope"] < 0)).fillna(False)
    work["slope_strength"] = work["fast_slope"].abs().fillna(0.0) + work["slow_slope"].abs().fillna(0.0)

    prev_close_15 = work["close"].shift(1)
    tr = pd.concat(
        [
            (work["high"] - work["low"]).abs(),
            (work["high"] - prev_close_15).abs(),
            (work["low"] - prev_close_15).abs(),
        ],
        axis=1,
    ).max(axis=1)
    work["tr15"] = tr
    work["atr14"] = tr.rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()
    return work


def _build_preview_candidates_for_bucket(
    *,
    bars: pd.DataFrame,
    bucket_rows: pd.DataFrame,
    current_bucket: pd.Timestamp,
    hour_df: pd.DataFrame | None = None,
    bars15: pd.DataFrame | None = None,
) -> pd.DataFrame:
    bars_base: pd.DataFrame | None = None
    if hour_df is None or bars15 is None:
        bars_base = bars.copy()
        bars_base["timestamp"] = pd.to_datetime(bars_base["timestamp"], utc=True)
        bars_base = bars_base[bars_base["timestamp"] < current_bucket].copy().sort_values("timestamp").reset_index(drop=True)
        if bars_base.empty:
            return pd.DataFrame()

    work = bucket_rows.copy().sort_values("open_ts").reset_index(drop=True)
    if work.empty:
        return pd.DataFrame()
    work["open_ts"] = pd.to_datetime(work["open_ts"], utc=True)
    work["close_ts"] = pd.to_datetime(work["close_ts"], utc=True)
    work["bucket_start"] = current_bucket
    work["hour_start"] = work["close_ts"].dt.floor("1h")
    work["cum_high"] = work["high"].cummax()
    work["cum_low"] = work["low"].cummin()

    if hour_df is None or bars15 is None:
        assert bars_base is not None
        hour_df = _build_completed_hours_from_15m(bars_base)
        bars15 = _build_completed_15m_reference(bars_base, hour_df)
    else:
        hour_df = hour_df.copy()
        bars15 = bars15.copy()
        hour_df["hour_start"] = pd.to_datetime(hour_df["hour_start"], utc=True)
        bars15["timestamp"] = pd.to_datetime(bars15["timestamp"], utc=True)
        bars15 = bars15[bars15["timestamp"] < current_bucket].copy().sort_values("timestamp").reset_index(drop=True)
    if bars15.empty:
        return pd.DataFrame()

    hour_map = hour_df[["hour_start", "ema_fast_hour", "ema_slow_hour"]].copy()
    hour_map["next_hour_start"] = hour_map["hour_start"] + pd.Timedelta(hours=1)
    hour_map = hour_map[["next_hour_start", "ema_fast_hour", "ema_slow_hour"]].rename(
        columns={"next_hour_start": "hour_start", "ema_fast_hour": "prev_hour_fast", "ema_slow_hour": "prev_hour_slow"}
    )
    work = work.merge(hour_map, on="hour_start", how="left")

    alpha_fast = 2.0 / (base_mod.EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (base_mod.EMA_SLOW_1H + 1.0)
    work["ema_fast_1h"] = alpha_fast * work["close"] + (1.0 - alpha_fast) * work["prev_hour_fast"]
    work["ema_slow_1h"] = alpha_slow * work["close"] + (1.0 - alpha_slow) * work["prev_hour_slow"]
    work["fast_slope"] = work["ema_fast_1h"] / work["prev_hour_fast"] - 1.0
    work["slow_slope"] = work["ema_slow_1h"] / work["prev_hour_slow"] - 1.0
    work["long_structure"] = (work["ema_fast_1h"] > work["ema_slow_1h"]).fillna(False)
    work["short_structure"] = (work["ema_fast_1h"] < work["ema_slow_1h"]).fillna(False)
    work["slope_floor_long"] = ((work["fast_slope"] > base_mod.SLOPE_FLOOR) & (work["slow_slope"] > 0)).fillna(False)
    work["slope_floor_short"] = ((work["fast_slope"] < -base_mod.SLOPE_FLOOR) & (work["slow_slope"] < 0)).fillna(False)
    work["slope_strength"] = work["fast_slope"].abs().fillna(0.0) + work["slow_slope"].abs().fillna(0.0)

    prev_bucket = current_bucket - pd.Timedelta(minutes=15)
    prev15 = bars15[bars15["timestamp"] == prev_bucket].tail(1)
    if prev15.empty:
        return pd.DataFrame()
    prev15_row = prev15.iloc[0]
    work["prev15_close"] = float(prev15_row["close"])
    work["prev15_fast"] = float(prev15_row["ema_fast_1h"])
    work["prev15_tr"] = float(prev15_row["tr15"])

    hist_tr = list(bars15[bars15["timestamp"] < current_bucket]["tr15"].tail(ATR_PERIOD - 1).astype(float))
    hist_count = len(hist_tr)
    hist_sum = float(sum(hist_tr)) if hist_tr else 0.0
    partial_prev_close = work["prev15_close"]
    partial_tr = pd.concat(
        [
            (work["cum_high"] - work["cum_low"]).abs(),
            (work["cum_high"] - partial_prev_close).abs(),
            (work["cum_low"] - partial_prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    work["partial_tr15"] = partial_tr
    work["atr14_partial"] = np.where(
        hist_count >= (ATR_PERIOD - 1),
        (hist_sum + work["partial_tr15"]) / ATR_PERIOD,
        np.nan,
    )

    work["preview_long"] = (
        work["long_structure"]
        & work["slope_floor_long"]
        & (work["prev15_close"] <= work["prev15_fast"])
        & (work["close"] > work["ema_fast_1h"])
    )
    work["preview_short"] = (
        work["short_structure"]
        & work["slope_floor_short"]
        & (work["prev15_close"] >= work["prev15_fast"])
        & (work["close"] < work["ema_fast_1h"])
    )
    work["preview_dir"] = np.where(work["preview_long"], 1, np.where(work["preview_short"], -1, 0))
    work["spread_mid"] = (work["ema_fast_1h"] + work["ema_slow_1h"]) / 2.0
    return work


def build_preview_signal_from_bucket_rows(
    *,
    asset: str,
    symbol: str,
    bars: pd.DataFrame,
    bucket_rows: pd.DataFrame,
    cutoff: pd.Timestamp,
    current_bucket: pd.Timestamp | None = None,
    now_utc: pd.Timestamp | None = None,
    official_signal_ttl_minutes: int | None = None,
    signal_id_builder=None,
    alpha_version: str = "canary_preview_v2",
    hour_df: pd.DataFrame | None = None,
    bars15: pd.DataFrame | None = None,
) -> AlphaSignal | None:
    if bucket_rows.empty:
        return None
    work = bucket_rows.copy()
    work["open_ts"] = pd.to_datetime(work["open_ts"], utc=True)
    work["close_ts"] = pd.to_datetime(work["close_ts"], utc=True)
    if current_bucket is None:
        current_bucket = pd.to_datetime(work.iloc[0]["open_ts"], utc=True).floor("15min")
    current_bucket = pd.to_datetime(current_bucket, utc=True)
    if now_utc is None:
        now_utc = pd.Timestamp.now(tz="UTC")
    else:
        now_utc = pd.to_datetime(now_utc, utc=True)

    candidates = _build_preview_candidates_for_bucket(
        bars=bars,
        bucket_rows=work,
        current_bucket=current_bucket,
        hour_df=hour_df,
        bars15=bars15,
    )
    if candidates.empty:
        return None

    scoped = candidates[candidates["preview_dir"] != 0].copy()
    if scoped.empty:
        return None
    for _, row in scoped.iterrows():
        signal_ts = pd.to_datetime(row["close_ts"], utc=True)
        if signal_ts < cutoff or signal_ts > now_utc:
            continue
        direction = int(row["preview_dir"])
        side = Side.LONG if direction > 0 else Side.SHORT
        atr_val = row.get("atr14_partial")
        atr_ready = pd.notna(atr_val) and float(atr_val) > 0
        expires_at = (
            signal_ts + pd.Timedelta(minutes=official_signal_ttl_minutes)
            if official_signal_ttl_minutes is not None
            else None
        )
        signal_id = (
            signal_id_builder(symbol=symbol, ts=signal_ts, side=side, mode="preview")
            if signal_id_builder is not None
            else f"preview-{symbol.lower()}-{signal_ts.strftime('%Y%m%d%H%M%S')}"
        )
        return AlphaSignal(
            signal_id=signal_id,
            timestamp=signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            symbol=symbol,
            side=side,
            signal_price=float(row["close"]),
            alpha_name="rank32b_slope_floor_continuation",
            alpha_version=alpha_version,
            metadata={
                "asset": asset,
                "variant": PRIMARY_VARIANT,
                "signal_mode": "preview_unclosed15m",
                "bucket_start": current_bucket.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "bucket_close_at": (current_bucket + pd.Timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "first_seen_at": signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "expired_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") if expires_at is not None else None,
                "confirmed_at_close": None,
                "official_confirmed_at": None,
                "entry_reference": "immediate_market",
                "signal_confirmed_at_override": signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_delay_minutes": 0,
                "fast_slope": float(row["fast_slope"]) if pd.notna(row["fast_slope"]) else None,
                "slow_slope": float(row["slow_slope"]) if pd.notna(row["slow_slope"]) else None,
                "spread_mid": float(row["spread_mid"]) if pd.notna(row["spread_mid"]) else None,
                "slope_strength": float(row["slope_strength"]) if pd.notna(row["slope_strength"]) else None,
                "atr_ready": bool(atr_ready),
                "atr14": float(atr_val) if atr_ready else None,
                "bar_close_price": float(row["close"]),
                "prev15_close": float(row["prev15_close"]) if pd.notna(row["prev15_close"]) else None,
                "prev15_fast": float(row["prev15_fast"]) if pd.notna(row["prev15_fast"]) else None,
            },
        )
    return None


class Rank32BPerpSignalAdapter:
    def __init__(
        self,
        *,
        asset_to_symbol: dict[str, str] | None = None,
        days: int = 30,
        recent_hours: int = 72,
        variant: str = PRIMARY_VARIANT,
        refresh_bars: bool = True,
        refresh_tail_days: int | None = 2,
        preview_unclosed_15m: bool = False,
        preview_fetch_limit: int = 30,
        entry_delay_minutes: int = 1,
        official_signal_ttl_minutes: int | None = None,
    ) -> None:
        self.asset_to_symbol = asset_to_symbol or DEFAULT_ASSET_TO_SYMBOL
        self.days = int(days)
        self.recent_hours = int(recent_hours)
        self.variant = variant
        self.refresh_bars = bool(refresh_bars)
        self.refresh_tail_days = None if refresh_tail_days is None else max(1, int(refresh_tail_days))
        self.preview_unclosed_15m = bool(preview_unclosed_15m)
        self.preview_fetch_limit = max(5, int(preview_fetch_limit))
        self.entry_delay_minutes = max(0, int(entry_delay_minutes))
        self.official_signal_ttl_minutes = (
            None if official_signal_ttl_minutes is None else max(0, int(official_signal_ttl_minutes))
        )

    def _signal_id(self, *, symbol: str, ts: pd.Timestamp, side: Side, mode: str = "official") -> str:
        if mode == "official":
            raw = f"rank32b_canary|{symbol}|{ts.strftime('%Y-%m-%dT%H:%M:%SZ')}|{side.value}"
        else:
            raw = f"rank32b_canary|{mode}|{symbol}|{ts.strftime('%Y-%m-%dT%H:%M:%SZ')}|{side.value}"
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
        return f"rank32b-{symbol.lower()}-{digest}"

    def _fetch_recent_1m_bars(self, symbol: str) -> pd.DataFrame:
        resp = requests.get(
            RECENT_1M_URL,
            params={"symbol": symbol, "interval": "1m", "limit": self.preview_fetch_limit},
            timeout=REQ_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close"])
        cols = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "num_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ]
        raw = pd.DataFrame(data, columns=cols)
        out = pd.DataFrame(
            {
                "open_ts": pd.to_datetime(raw["open_time"], unit="ms", utc=True),
                "open": pd.to_numeric(raw["open"], errors="coerce"),
                "high": pd.to_numeric(raw["high"], errors="coerce"),
                "low": pd.to_numeric(raw["low"], errors="coerce"),
                "close": pd.to_numeric(raw["close"], errors="coerce"),
            }
        )
        out["close_ts"] = out["open_ts"] + pd.Timedelta(minutes=1)
        return out.dropna().sort_values("open_ts").drop_duplicates("open_ts").reset_index(drop=True)

    def _build_preview_signal(
        self,
        *,
        asset: str,
        symbol: str,
        bars: pd.DataFrame,
        cutoff: pd.Timestamp,
        now_utc: pd.Timestamp | None = None,
    ) -> AlphaSignal | None:
        if not self.preview_unclosed_15m or bars.empty or len(bars) < 2:
            return None
        try:
            recent_1m = self._fetch_recent_1m_bars(symbol)
        except Exception:
            return None
        if recent_1m.empty:
            return None

        if now_utc is None:
            now_utc = pd.Timestamp.now(tz="UTC")
        else:
            now_utc = pd.to_datetime(now_utc, utc=True)
        current_bucket = now_utc.floor("15min")
        bucket_rows = recent_1m[recent_1m["open_ts"].dt.floor("15min") == current_bucket].copy()
        if bucket_rows.empty:
            return None

        return build_preview_signal_from_bucket_rows(
            asset=asset,
            symbol=symbol,
            bars=bars,
            bucket_rows=bucket_rows,
            cutoff=cutoff,
            current_bucket=current_bucket,
            now_utc=now_utc,
            official_signal_ttl_minutes=self.official_signal_ttl_minutes,
            signal_id_builder=self._signal_id,
            alpha_version="canary_preview_v2",
        )

    def _build_historical_preview_signals(
        self,
        *,
        asset: str,
        symbol: str,
        bars: pd.DataFrame,
        minute_df: pd.DataFrame,
        cutoff: pd.Timestamp,
        now_utc: pd.Timestamp,
    ) -> list[AlphaSignal]:
        if not self.preview_unclosed_15m or bars.empty or len(bars) < 2 or minute_df.empty:
            return []

        work = minute_df.copy()
        work["open_ts"] = pd.to_datetime(work["open_ts"], utc=True)
        work["close_ts"] = pd.to_datetime(work["close_ts"], utc=True)
        work = work[(work["close_ts"] >= cutoff) & (work["open_ts"] <= now_utc)].copy()
        if work.empty:
            return []

        hour_df = _build_completed_hours_from_15m(bars)
        bars15 = _build_completed_15m_reference(bars, hour_df)
        out: list[AlphaSignal] = []

        for bucket_start, bucket_rows in work.groupby(work["open_ts"].dt.floor("15min"), sort=True):
            bucket_ts = pd.to_datetime(bucket_start, utc=True)
            scoped = bucket_rows[bucket_rows["close_ts"] <= now_utc].copy()
            if scoped.empty:
                continue
            signal = build_preview_signal_from_bucket_rows(
                asset=asset,
                symbol=symbol,
                bars=bars,
                bucket_rows=scoped,
                cutoff=cutoff,
                current_bucket=bucket_ts,
                now_utc=min(now_utc, pd.to_datetime(scoped["close_ts"].max(), utc=True)),
                official_signal_ttl_minutes=None,
                signal_id_builder=self._signal_id,
                alpha_version="canary_preview_v2",
                hour_df=hour_df,
                bars15=bars15,
            )
            if signal is not None:
                out.append(signal)
        return out

    def load_recent_signals(
        self,
        *,
        now_utc: pd.Timestamp | None = None,
        preview_history_minute_loader: Callable[[str, pd.Timestamp, pd.Timestamp], pd.DataFrame] | None = None,
    ) -> SignalSnapshot:
        rows: list[AlphaSignal] = []
        latest_bar: pd.Timestamp | None = None
        latest_observed_signal: pd.Timestamp | None = None
        if now_utc is None:
            now_utc = pd.Timestamp.now(tz="UTC")
        else:
            now_utc = pd.to_datetime(now_utc, utc=True)
        cutoff = now_utc - pd.Timedelta(hours=self.recent_hours)
        current_bucket = now_utc.floor("15min")
        official_ready_cutoff = (
            None
            if self.official_signal_ttl_minutes is None
            else now_utc - pd.Timedelta(minutes=self.official_signal_ttl_minutes)
        )
        for asset, symbol in self.asset_to_symbol.items():
            try:
                bars = perp_mod.load_or_fetch_perp_bars(
                    symbol,
                    days=self.days,
                    refresh=self.refresh_bars,
                    incremental_refresh_days=self.refresh_tail_days if self.refresh_bars else None,
                )
                if bars.empty:
                    continue
                bars = bars.copy()
                bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
                latest_ts = pd.to_datetime(bars.iloc[-1]["timestamp"], utc=True)
                latest_bar = latest_ts if latest_bar is None else max(latest_bar, latest_ts)

                closed_bars = bars.loc[bars["timestamp"] < current_bucket].copy()
                frame = ext_mod.build_rank32b_frame_from_bars(asset, closed_bars)
                if not frame.empty:
                    frame = frame.copy()
                    frame["atr14"] = compute_atr14(frame)

                    for idx in range(1, len(frame)):
                        signal = base_mod.get_signal(frame, idx, self.variant)
                        if signal is None:
                            continue
                        direction, trigger_name = signal
                        ts = pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True)
                        if ts < cutoff:
                            continue
                        latest_observed_signal = ts if latest_observed_signal is None else max(latest_observed_signal, ts)
                        ready_at = ts + pd.Timedelta(minutes=15)
                        if ready_at > now_utc:
                            continue
                        if official_ready_cutoff is not None and ready_at < official_ready_cutoff:
                            continue
                        side = Side.LONG if direction > 0 else Side.SHORT
                        price = float(frame.iloc[idx]["close"])
                        atr_val = frame.iloc[idx].get("atr14")
                        atr_ready = pd.notna(atr_val) and float(atr_val) > 0
                        expires_at = (
                            ready_at + pd.Timedelta(minutes=self.official_signal_ttl_minutes)
                            if self.official_signal_ttl_minutes is not None
                            else None
                        )
                        rows.append(
                            AlphaSignal(
                                signal_id=self._signal_id(symbol=symbol, ts=ts, side=side, mode="official"),
                                timestamp=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                symbol=symbol,
                                side=side,
                                signal_price=price,
                                alpha_name="rank32b_slope_floor_continuation",
                                alpha_version="canary_phase1_v1",
                                metadata={
                                    "asset": asset,
                                    "variant": trigger_name,
                                    "signal_mode": "official_close",
                                    "bucket_start": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "bucket_close_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "first_seen_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "expired_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") if expires_at is not None else None,
                                    "confirmed_at_close": True,
                                    "official_confirmed_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "entry_reference": "immediate_market",
                                    "signal_confirmed_at_override": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "entry_delay_minutes": 0,
                                    "fast_slope": float(frame.iloc[idx]["fast_slope"]) if pd.notna(frame.iloc[idx]["fast_slope"]) else None,
                                    "slow_slope": float(frame.iloc[idx]["slow_slope"]) if pd.notna(frame.iloc[idx]["slow_slope"]) else None,
                                    "spread_mid": float(frame.iloc[idx]["spread_mid"]) if pd.notna(frame.iloc[idx]["spread_mid"]) else None,
                                    "slope_strength": (
                                        abs(float(frame.iloc[idx]["fast_slope"])) + abs(float(frame.iloc[idx]["slow_slope"]))
                                        if pd.notna(frame.iloc[idx]["fast_slope"]) and pd.notna(frame.iloc[idx]["slow_slope"])
                                        else None
                                    ),
                                    "atr_ready": bool(atr_ready),
                                    "atr14": float(atr_val) if atr_ready else None,
                                    "bar_close_price": float(frame.iloc[idx]["close"]),
                                },
                            )
                        )

                if preview_history_minute_loader is not None and self.preview_unclosed_15m:
                    try:
                        minute_df = preview_history_minute_loader(symbol, cutoff, now_utc)
                    except Exception:
                        minute_df = pd.DataFrame()
                    preview_signals = self._build_historical_preview_signals(
                        asset=asset,
                        symbol=symbol,
                        bars=bars,
                        minute_df=minute_df,
                        cutoff=cutoff,
                        now_utc=now_utc,
                    )
                    for preview_signal in preview_signals:
                        preview_ts = pd.to_datetime(preview_signal.timestamp, utc=True)
                        latest_observed_signal = preview_ts if latest_observed_signal is None else max(latest_observed_signal, preview_ts)
                        rows.append(preview_signal)
                else:
                    preview_signal = self._build_preview_signal(asset=asset, symbol=symbol, bars=bars, cutoff=cutoff, now_utc=now_utc)
                    if preview_signal is not None:
                        preview_ts = pd.to_datetime(preview_signal.timestamp, utc=True)
                        latest_observed_signal = preview_ts if latest_observed_signal is None else max(latest_observed_signal, preview_ts)
                        rows.append(preview_signal)
            except Exception as exc:
                print(
                    {
                        "level": "WARN",
                        "component": "rank32b_signal_adapter",
                        "asset": asset,
                        "symbol": symbol,
                        "message": "load_recent_signals_symbol_failed",
                        "error": str(exc),
                    },
                    flush=True,
                )
                continue

        rows.sort(key=lambda x: x.timestamp)
        latest_signal_utc = rows[-1].timestamp if rows else None
        latest_bar_utc = latest_bar.strftime("%Y-%m-%dT%H:%M:%SZ") if latest_bar is not None else None
        latest_observed_signal_utc = latest_observed_signal.strftime("%Y-%m-%dT%H:%M:%SZ") if latest_observed_signal is not None else None
        return SignalSnapshot(
            signals=rows,
            latest_bar_utc=latest_bar_utc,
            latest_signal_utc=latest_signal_utc,
            latest_observed_signal_utc=latest_observed_signal_utc,
        )
