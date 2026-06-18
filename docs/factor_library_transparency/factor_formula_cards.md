# Factor Formula Cards — 因子公式卡片

> Phase 12D-D · Authority: scripts/factor_formula_registry.py
> 本页解释的是因子公式，不是信号评估结果。

## 当前核心信号因子 — 当前核心纸面信号 (6个)

| 因子 | 公式 | Lookback | 方向 | 家族 |
|------|------|----------|------|------|
| vol_5h | rolling_std(pct_change(close), 5) | 5h | NEGATIVE | volatility |
| vol_40h | rolling_std(pct_change(close), 40) | 40h | NEGATIVE | volatility |
| downside_vol_20h | rolling_std(clip(ret, upper=0), 20) | 20h | NEGATIVE | volatility |
| vol_of_vol_20h | rolling_std(rolling_std(ret, 5), 20) | 20h (inner=5h) | NEGATIVE | volatility |
| rsi_7h | Wilder RSI, EWM alpha=1/7 | 7h | NEGATIVE | technical |
| rsi_28h | Wilder RSI, EWM alpha=1/28 | 28h | NEGATIVE | technical |

全部经过 cross-sectional winsorize (1st-99th) + z-score。全部 direction-flipped。

## 当前信号库 Overlay (4个)

| 因子 | 公式 | Lookback | 角色 |
|------|------|----------|------|
| xs_rank_vol | xs_rank(rolling_mean(volume, 20)) | 20h | liquidity_gate |
| range_1h | (high - low) / close | 1h | position_timing |
| range_4h | (HH4 - LL4) / close | 4h | position_timing |
| price_pos_24h | (close - LL24) / (HH24 - LL24 + 1e-8) | 24h | position_timing |

Overlay 因子 sign-flipped (mean-reversion hypothesis)。不进入 core_only。

## Historical / Experimental (11个)

| 因子 | 公式 | Lookback |
|------|------|----------|
| mom_20h | close / delay(close, 20) - 1 | 20h |
| reversal_5h | -(close / delay(close, 5) - 1) | 5h |
| volatility_20h | rolling_std(pct_change(close), 20) | 20h |
| rsi_14h | Wilder RSI, EWM alpha=1/14 | 14h |
| bb_zscore_20h | (close - SMA20) / STD20 | 20h |
| wq101_alpha101 | (close - open) / (high - low + 0.001) | 1h |
| wq101_alpha12 | sign(delta(vol, 1)) * (-delta(close, 1)) | 1h |
| wq101_alpha53 | -delta(pos, 9) | 9h |
| q158_high_low_range | (high - low) / close | 1h |
| tech_macd | EMA(12) - EMA(26) - signal | 26h |
| tech_atr | rolling_mean(true_range, 14) | 14h |

全部 NOT_IN_CURRENT_SIGNAL, NOT_SURVIVING_CANDIDATE。

## 数据来源

公式来源: `scripts/factor_formula_registry.py` (804行, 45个注册因子)
构建脚本: `scripts/build_factor_values.py` (11基础+扩展), `scripts/build_crypto_native_factor_values.py` (6 crypto-native)

---

Phase 12D-D · Phase 13 NOT STARTED · No real execution
