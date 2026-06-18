# Crypto-Native Factor Formulas

> Phase 12D-D · NOT_IN_CURRENT_SIGNAL · Authority: build_crypto_native_factor_values.py
> Crypto-native 因子当前未进入 当前信号库 v0 或 当前核心纸面信号。

## Funding Rate 因子 (3个)

| 因子 | 公式 | Lookback | 数据源 |
|------|------|----------|--------|
| funding_rate_change_24h | funding_rate - delay(funding_rate, 24) | 24h | funding_aligned/ |
| funding_rate_level_20h | rolling_mean(funding_rate, 20) | 20h | funding_aligned/ |
| funding_rate_zscore_80h | (funding_rate - SMA80) / STD80 | 80h | funding_aligned/ |

**风险:** Funding rate 8h 更新一次，rolling window 内有效样本少。

## Taker Imbalance 因子 (3个)

| 因子 | 公式 | Lookback | 数据源 |
|------|------|----------|--------|
| taker_buy_delta_5h | ratio - delay(ratio, 5) | 5h | taker-enriched bars |
| taker_buy_ratio_20h | rolling_mean(taker_qvol/qvol, 20) | 20h | taker-enriched bars |
| taker_buy_zscore_20h | zscore(taker_qvol/qvol, 20) | 20h | taker-enriched bars |

**优势:** 数据连续，无稀疏性问题。

## 未确认数据类型

以下数据当前未下载或未确认：OI、basis、long-short ratio、liquidations、orderbook depth。

## 后续使用

若要把 crypto-native 因子加入信号，应另起 Phase 9C/9D signal design，不能改写 Phase 9B 历史结果。

---

Phase 12D-D · Phase 13 NOT STARTED · No real execution
