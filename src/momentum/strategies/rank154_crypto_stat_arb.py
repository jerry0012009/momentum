from __future__ import annotations

import numpy as np
import pandas as pd


STRATEGY_ID = "rank154_crypto_stat_arb_v1"
CANDIDATE_ID = "rank154_crypto_stat_arb"
CANDIDATE_RANK = 154

UNIVERSE_SIZE = 30
MIN_LISTING_DAYS = 180
MAX_ABS_WEIGHT = 0.10
MIN_EFFECTIVE_WEIGHT = 0.005

STABLE_BASES = {
    "USDT",
    "USDC",
    "FDUSD",
    "BUSD",
    "USDP",
    "TUSD",
    "USDE",
    "USDS",
    "DAI",
}


def is_plain_alpha_base(base: str) -> bool:
    return bool(base) and base.isalpha() and base.upper() == base and base not in STABLE_BASES


def days_since_high_rolling(close: pd.Series, window: int = 20) -> pd.Series:
    def _fn(values: np.ndarray) -> float:
        arr = np.asarray(values, dtype=float)
        if len(arr) == 0 or np.all(np.isnan(arr)):
            return np.nan
        idx = int(np.nanargmax(arr))
        return float(len(arr) - 1 - idx)

    return close.rolling(window, min_periods=window).apply(_fn, raw=True)


def add_signal_features(frame: pd.DataFrame, min_listing_days: int = MIN_LISTING_DAYS) -> pd.DataFrame:
    out = frame.copy()
    out["trail_quote_volume_30d"] = out["quote_volume"].rolling(30, min_periods=30).mean()
    out["momo_10d"] = out["close"].pct_change(10)
    out["days_since_20d_high"] = days_since_high_rolling(out["close"], 20)
    out["breakout_raw"] = 19.0 - out["days_since_20d_high"]
    out["carry_raw"] = out["funding_rate_last"] if "funding_rate_last" in out.columns else out.get("funding_rate", 0.0)
    out["decision_ready"] = (
        out["trail_quote_volume_30d"].notna()
        & out["momo_10d"].notna()
        & out["breakout_raw"].notna()
    )
    out["guard_pass"] = (
        out["decision_ready"]
        & out["plain_alpha_base"]
        & (out["listing_days"] >= min_listing_days)
    )
    out["guard_reason"] = np.where(
        ~out["plain_alpha_base"],
        "filtered_non_alpha_or_stable_base",
        np.where(
            out["listing_days"] < min_listing_days,
            "listing_too_short",
            np.where(~out["decision_ready"], "insufficient_history", "eligible"),
        ),
    )
    return out


def centered_deciles(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    if series.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    ranks = series.rank(method="first")
    q = max(2, min(10, int(len(series))))
    dec = pd.qcut(ranks, q=q, labels=False, duplicates="drop")
    dec = pd.Series(dec, index=series.index, dtype=float) + 1.0
    centered = dec - dec.mean()
    return dec, centered


def build_reason_text(row: pd.Series) -> str:
    pieces: list[str] = []
    if pd.notna(row.get("carry_decile")):
        pieces.append(f"carry D{int(row['carry_decile'])}")
    if pd.notna(row.get("momo_decile")):
        pieces.append(f"momo D{int(row['momo_decile'])}")
    if pd.notna(row.get("breakout_decile")):
        pieces.append(f"breakout D{int(row['breakout_decile'])}")
    side = "做多" if float(row.get("target_weight", 0.0)) > 0 else ("做空" if float(row.get("target_weight", 0.0)) < 0 else "观望")
    dominant = str(row.get("dominant_driver") or "composite")
    return f"{side}；主因={dominant}；" + " / ".join(pieces)


def build_panel_for_date(
    frames: dict[str, pd.DataFrame],
    decision_date: pd.Timestamp,
    universe_size: int = UNIVERSE_SIZE,
    max_abs_weight: float = MAX_ABS_WEIGHT,
    min_effective_weight: float = MIN_EFFECTIVE_WEIGHT,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    for symbol, frame in frames.items():
        row = frame[frame["date"] == decision_date]
        if row.empty:
            continue
        rows.append(row.iloc[0].to_dict())
    panel = pd.DataFrame(rows)
    if panel.empty:
        return panel, panel

    eligible = panel[panel["guard_pass"]].copy()
    eligible = eligible.sort_values(["trail_quote_volume_30d", "quote_volume_24h"], ascending=False).reset_index(drop=True)
    eligible["volume_rank_30d"] = np.arange(1, len(eligible) + 1)
    universe = eligible.head(universe_size).copy().reset_index(drop=True)

    if universe.empty:
        return universe, panel

    carry_dec, carry_centered = centered_deciles(universe["carry_raw"])
    momo_dec, momo_centered = centered_deciles(universe["momo_10d"])
    breakout_dec, breakout_centered = centered_deciles(universe["breakout_raw"])

    universe["carry_decile"] = carry_dec
    universe["momo_decile"] = momo_dec
    universe["breakout_decile"] = breakout_dec
    universe["carry_centered"] = carry_centered
    universe["momo_centered"] = momo_centered
    universe["breakout_centered"] = breakout_centered
    universe["carry_contrib"] = 0.5 * universe["carry_centered"]
    universe["momo_contrib"] = 0.2 * universe["momo_centered"]
    universe["breakout_contrib"] = 0.3 * universe["breakout_centered"]
    universe["combined_score_raw"] = universe["carry_contrib"] + universe["momo_contrib"] + universe["breakout_contrib"]
    universe["combined_score"] = universe["combined_score_raw"] - universe["combined_score_raw"].mean()
    denom = float(universe["combined_score"].abs().sum())
    universe["target_weight_raw"] = universe["combined_score"] / denom if denom > 0 else 0.0
    universe["target_weight_capped"] = universe["target_weight_raw"].clip(-max_abs_weight, max_abs_weight)
    universe["target_weight"] = np.where(universe["target_weight_capped"].abs() >= min_effective_weight, universe["target_weight_capped"], 0.0)
    universe["side"] = np.where(universe["target_weight"] > 0, "long", np.where(universe["target_weight"] < 0, "short", "flat"))
    universe["dominant_driver"] = universe[["carry_contrib", "momo_contrib", "breakout_contrib"]].abs().idxmax(axis=1).str.replace("_contrib", "", regex=False)
    universe["decision_reason"] = universe.apply(build_reason_text, axis=1)
    universe = universe.sort_values("target_weight", ascending=False).reset_index(drop=True)
    return universe, panel
