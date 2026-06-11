"""Regime Triplet signal implementation.

Signals (at day t):
- up_regime:
  1) t-3 bullish candle (close > open)
  2) close at t-3..t all above MA(ma_period)
  3) volume at t-3..t all above vol_multiplier * MA(volume, vol_ma_period)

- side_regime:
  1) price part meets up-regime rule (1)+(2)
  2) but volume part (3) does NOT hold for all 4 days

- down_regime:
  1) close at t-3..t all below MA(ma_period)
  2) no volume condition required

Compatibility columns:
- upwave := up_regime
- downwave := down_regime
"""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


REQUIRED_COLUMNS = ["open", "close", "volume"]


@dataclass(frozen=True)
class RegimeTripletConfig:
    ma_period: int = 20
    vol_ma_period: int = 120
    vol_multiplier: float = 1.0


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def compute_regime_triplet_signals(
    bars: pd.DataFrame,
    *,
    config: RegimeTripletConfig = RegimeTripletConfig(),
) -> pd.DataFrame:
    _validate_df(bars)

    out = bars.copy()
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
        out = out.sort_values("timestamp").reset_index(drop=True)

    ma_col = f"ma_{config.ma_period}"
    vol_ma_col = f"vol_ma_{config.vol_ma_period}"

    out[ma_col] = out["close"].rolling(config.ma_period, min_periods=config.ma_period).mean()
    out[vol_ma_col] = out["volume"].rolling(config.vol_ma_period, min_periods=config.vol_ma_period).mean()

    above = out["close"] > out[ma_col]
    below = out["close"] < out[ma_col]
    bullish_t3 = out["close"].shift(3) > out["open"].shift(3)

    all4_above = above & above.shift(1) & above.shift(2) & above.shift(3)
    all4_below = below & below.shift(1) & below.shift(2) & below.shift(3)

    vol_ok = out["volume"] > (config.vol_multiplier * out[vol_ma_col])
    vol_ok4 = vol_ok & vol_ok.shift(1) & vol_ok.shift(2) & vol_ok.shift(3)

    price_up_core = bullish_t3 & all4_above

    out["up_regime"] = (price_up_core & vol_ok4).fillna(False).astype(int)
    out["side_regime"] = (price_up_core & (~vol_ok4)).fillna(False).astype(int)
    out["down_regime"] = all4_below.fillna(False).astype(int)

    out["upwave"] = out["up_regime"]
    out["downwave"] = out["down_regime"]

    return out


__all__ = [
    "RegimeTripletConfig",
    "compute_regime_triplet_signals",
]
