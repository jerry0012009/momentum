"""Market-level risk-on / risk-off gate on top of multi-timeframe momentum.

Idea:
- Base entry still comes from multi-timeframe momentum.
- A higher-timeframe market-state gate decides whether the strategy should be ON.
- This gate does not predict direction; it decides whether the current environment is healthy enough.

Minimal baseline v1 uses 3 simple, computable features on 1h bars:
1) trend_1h = close / close.shift(trend_window_1h) - 1
2) ema_ok_1h = close > EMA(ema_window_1h)
3) vol_ok_1h = realized_vol_1h <= rolling_quantile(realized_vol_1h, q_window, q_max)

Pass condition:
- risk_on_score = trend_ok_1h + ema_ok_1h + vol_ok_1h
- risk_on_pass = risk_on_score >= min_pass_count
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .multi_tf_momentum import MultiTfMomentumConfig, compute_multi_tf_momentum_signals


REQUIRED_COLUMNS = ["timestamp", "close"]


@dataclass(frozen=True)
class MarketRiskOnOffFilterConfig:
    # base trend / baseline momentum
    window_5m: int = 6
    window_15m: int = 6
    threshold_5m: float = 0.003
    threshold_15m: float = 0.006
    resample_rule_15m: str = "15min"

    # market-state gate (1h)
    market_resample_rule: str = "1h"
    trend_window_1h: int = 12
    trend_threshold_1h: float = 0.005
    ema_window_1h: int = 24
    vol_window_1h: int = 12
    vol_quantile_window_1h: int = 72
    vol_quantile_max: float = 0.8
    min_pass_count: int = 2


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")



def _validate_config(config: MarketRiskOnOffFilterConfig) -> None:
    if config.window_5m <= 0 or config.window_15m <= 0:
        raise ValueError("momentum windows must be > 0")
    if config.threshold_5m < 0 or config.threshold_15m < 0:
        raise ValueError("momentum thresholds must be >= 0")
    if config.trend_window_1h <= 1:
        raise ValueError("trend_window_1h must be > 1")
    if config.ema_window_1h <= 1:
        raise ValueError("ema_window_1h must be > 1")
    if config.vol_window_1h <= 1:
        raise ValueError("vol_window_1h must be > 1")
    if config.vol_quantile_window_1h <= 1:
        raise ValueError("vol_quantile_window_1h must be > 1")
    if not (0.0 < config.vol_quantile_max <= 1.0):
        raise ValueError("vol_quantile_max must be in (0, 1]")
    if config.min_pass_count < 1 or config.min_pass_count > 3:
        raise ValueError("min_pass_count must be in [1, 3]")



def _compute_single_symbol(df: pd.DataFrame, config: MarketRiskOnOffFilterConfig) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values(["timestamp"]).reset_index(drop=True)

    base = compute_multi_tf_momentum_signals(
        out,
        config=MultiTfMomentumConfig(
            window_5m=config.window_5m,
            window_15m=config.window_15m,
            threshold_5m=config.threshold_5m,
            threshold_15m=config.threshold_15m,
            resample_rule_15m=config.resample_rule_15m,
        ),
    )
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    out = out.merge(
        base[["timestamp", "mom_5m", "mom_15m", "long_signal", "short_signal"]].rename(
            columns={"long_signal": "base_long_signal", "short_signal": "base_short_signal"}
        ),
        on="timestamp",
        how="left",
    )

    market = out[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market = market.resample(config.market_resample_rule).last().dropna().reset_index()
    market["ret_1h"] = market["close_1h_src"].pct_change()
    market["trend_1h"] = market["close_1h_src"] / market["close_1h_src"].shift(config.trend_window_1h) - 1.0
    market["ema_1h"] = market["close_1h_src"].ewm(span=config.ema_window_1h, adjust=False).mean()
    market["rv_1h"] = market["ret_1h"].rolling(config.vol_window_1h, min_periods=config.vol_window_1h).std(ddof=0)
    min_q = max(config.vol_window_1h, config.vol_quantile_window_1h // 3)
    market["rv_1h_qmax"] = market["rv_1h"].rolling(config.vol_quantile_window_1h, min_periods=min_q).quantile(config.vol_quantile_max)

    market["trend_ok_1h"] = (market["trend_1h"] > config.trend_threshold_1h).fillna(False).astype(int)
    market["ema_ok_1h"] = (market["close_1h_src"] > market["ema_1h"]).fillna(False).astype(int)
    market["vol_ok_1h"] = ((market["rv_1h"] <= market["rv_1h_qmax"]) | market["rv_1h_qmax"].isna()).fillna(False).astype(int)
    market["risk_on_score"] = market[["trend_ok_1h", "ema_ok_1h", "vol_ok_1h"]].sum(axis=1)
    market["risk_on_pass"] = (market["risk_on_score"] >= config.min_pass_count).astype(int)

    out = pd.merge_asof(
        out.sort_values("timestamp"),
        market.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    out["risk_on_pass"] = out["risk_on_pass"].fillna(0).astype(int)
    out["risk_on_score"] = out["risk_on_score"].fillna(0).astype(int)
    for col in ["trend_ok_1h", "ema_ok_1h", "vol_ok_1h"]:
        out[col] = out[col].fillna(0).astype(int)

    out["long_signal"] = ((out["base_long_signal"] == 1) & (out["risk_on_pass"] == 1)).astype(int)
    out["short_signal"] = ((out["base_short_signal"] == 1) & (out["risk_on_pass"] == 1)).astype(int)

    out["long_filtered_out"] = ((out["base_long_signal"] == 1) & (out["long_signal"] == 0)).astype(int)
    out["short_filtered_out"] = ((out["base_short_signal"] == 1) & (out["short_signal"] == 0)).astype(int)

    return out



def compute_market_risk_on_off_filter_signals(
    bars: pd.DataFrame,
    *,
    config: MarketRiskOnOffFilterConfig = MarketRiskOnOffFilterConfig(),
) -> pd.DataFrame:
    _validate_df(bars)
    _validate_config(config)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        parts = []
        for _, g in df.groupby("symbol", sort=True):
            parts.append(_compute_single_symbol(g.reset_index(drop=True), config))
        out = pd.concat(parts, ignore_index=True)
    else:
        out = _compute_single_symbol(df, config)

    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


__all__ = [
    "MarketRiskOnOffFilterConfig",
    "compute_market_risk_on_off_filter_signals",
]
