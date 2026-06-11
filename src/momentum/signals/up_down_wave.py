"""UpWave / DownWave signal implementations.

Definitions (at day t):
- UpWave(t):
  1) t-3 is bullish candle (close > open)
  2) close at t-3, t-2, t-1, t are all above MA(period)

- DownWave(t):
  1) close at t-3, t-2, t-1, t are all below MA(period)

Provides:
- Pandas batch computation for offline feature generation.
- Backtrader reusable indicator for strategy integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

try:
    import backtrader as bt
except Exception:  # pragma: no cover
    bt = None


REQUIRED_COLUMNS = ["open", "close"]


@dataclass(frozen=True)
class UpDownWaveConfig:
    ma_period: int = 20


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _compute_single_symbol(df: pd.DataFrame, ma_period: int) -> pd.DataFrame:
    out = df.copy()

    ma_col = f"ma_{ma_period}"
    out[ma_col] = out["close"].rolling(ma_period, min_periods=ma_period).mean()

    above = out["close"] > out[ma_col]
    below = out["close"] < out[ma_col]

    # t-3 bullish
    bullish_t3 = out["close"].shift(3) > out["open"].shift(3)

    all4_above = above & above.shift(1) & above.shift(2) & above.shift(3)
    all4_below = below & below.shift(1) & below.shift(2) & below.shift(3)

    out["upwave"] = (bullish_t3 & all4_above).fillna(False).astype(int)
    out["downwave"] = all4_below.fillna(False).astype(int)

    return out


def compute_up_down_wave_signals(
    bars: pd.DataFrame,
    *,
    config: UpDownWaveConfig = UpDownWaveConfig(),
) -> pd.DataFrame:
    """Compute UpWave/DownWave signals for one or multiple symbols.

    Expected columns:
    - open, close
    Optional:
    - timestamp (for sorting)
    - symbol (for per-symbol grouped computation)
    """

    _validate_df(bars)

    df = bars.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        sort_cols = ["symbol"] + (["timestamp"] if "timestamp" in df.columns else [])
        df = df.sort_values(sort_cols).reset_index(drop=True)

        parts = []
        for _, g in df.groupby("symbol", sort=True):
            parts.append(_compute_single_symbol(g.reset_index(drop=True), config.ma_period))
        out = pd.concat(parts, ignore_index=True)
    else:
        if "timestamp" in df.columns:
            df = df.sort_values(["timestamp"]).reset_index(drop=True)
        out = _compute_single_symbol(df, config.ma_period)

    if "timestamp" in out.columns:
        out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return out


if bt is not None:

    class UpDownWaveIndicator(bt.Indicator):
        """Backtrader indicator for UpWave/DownWave.

        lines:
        - upwave: 1 or 0
        - downwave: 1 or 0
        """

        lines = ("upwave", "downwave")
        params = dict(ma_period=20)

        def __init__(self):
            self.ma = bt.indicators.SMA(self.data.close, period=self.p.ma_period)
            # Need ma at t-3, so min bars = ma_period + 3
            self.addminperiod(self.p.ma_period + 3)

        def next(self):
            idxs: Iterable[int] = (3, 2, 1, 0)

            all4_above = all(self.data.close[-k] > self.ma[-k] for k in idxs)
            all4_below = all(self.data.close[-k] < self.ma[-k] for k in idxs)
            bullish_t3 = self.data.close[-3] > self.data.open[-3]

            self.lines.upwave[0] = 1.0 if (bullish_t3 and all4_above) else 0.0
            self.lines.downwave[0] = 1.0 if all4_below else 0.0


__all__ = [
    "UpDownWaveConfig",
    "compute_up_down_wave_signals",
]

if bt is not None:
    __all__.append("UpDownWaveIndicator")
