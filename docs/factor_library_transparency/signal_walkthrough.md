# Signal Walkthrough — 当前核心纸面信号穿透

> Phase 12D-E · 研究解释页，不是实盘，不是交易建议。

## 概述

本页用真实数据展示 signal_v0_core_only__1h__original_no_guard 的形成过程。

**Walkthrough Timestamp:** 2026-06-13 08:00:00 UTC
**Signal Snapshot Timestamp:** 2026-06-13 00:00:00 UTC
**数据来源:** phase12a_latest_signal_snapshot.csv + factor_values.parquet

## 信号构成

```
risk_pressure = mean(flipped(vol_5h), flipped(vol_40h), flipped(downside_vol_20h), flipped(vol_of_vol_20h))
oscillator_exhaustion = mean(flipped(rsi_7h), rsi_28h)
raw_core_score = 0.60 × risk_pressure + 0.40 × oscillator_exhaustion
signal_v0_core_only = xs_zscore(raw_core_score)
```

## 样例 1: BCHUSDT (LONG, Rank #1)

| 因子 | 原始值 | 方向 | 解释 |
|------|--------|------|------|
| vol_5h | 0.00631 | NEG → flip | 低波动 → 正贡献 |
| vol_40h | 0.00738 | NEG → flip | 低波动 → 正贡献 |
| downside_vol_20h | 0.00314 | NEG → flip | 下行波动率低 → 正贡献 |
| vol_of_vol_20h | 0.00274 | NEG → flip | 波动率稳定 → 正贡献 |
| rsi_7h | 73.04 | NEG → flip | 超买 → flip 后为负 |
| rsi_28h | 56.56 | POS | 中性偏多 → 正贡献 |

**signal_value = +1.087 (z-score), weight = +0.0625**

## 样例 2: HUSDT (SHORT, Rank #43)

| 因子 | 原始值 | 方向 | 解释 |
|------|--------|------|------|
| vol_5h | 0.08308 | NEG → flip | 极高波动 → 强烈负贡献 |
| vol_40h | 0.05767 | NEG → flip | 极高波动 → 强烈负贡献 |
| downside_vol_20h | 0.03199 | NEG → flip | 下行波动率极高 → 强烈负贡献 |
| vol_of_vol_20h | 0.01736 | NEG → flip | 波动率不稳定 → 负贡献 |
| rsi_7h | 41.25 | NEG → flip | 偏超卖 → flip 后为正 |
| rsi_28h | 51.87 | POS | 接近中性 |

**signal_value = -4.695 (z-score), weight = -0.0625**

## 样例 3: DOGEUSDT (NEUTRAL, Rank #21)

所有因子值处于截面中等水平。signal_value = +0.387，不在 top-8 也不在 bottom-8，不进入纸面信号。

## 截面总览

- 可用符号：43
- Long side：8 个，每个权重 +0.0625
- Short side：8 个，每个权重 -0.0625
- Neutral：27 个
- Gross/Net Exposure：1.0 / 0.0

## 声明

- Phase 13 NOT STARTED
- No real execution, no alpha claim, no production claim
- Forward return 在最新 timestamp 不可用
