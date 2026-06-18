# Signal Walkthrough — 当前核心纸面信号穿透

> Phase 12D-E-R · 修复版 · 研究解释页，不是实盘，不是交易建议。

## 修复内容

1. **rsi_28h 方向修正**：rsi_28h 是 NEGATIVE，sign-flipped（此前版本错误标记为 POS）
2. **时间戳统一**：signal、factor values、components 均来自 2026-06-13 00:00:00 UTC
3. **组件数值来源**：直接来自 phase9b_signal_panel.parquet，非手工计算

## 统一时间戳

**2026-06-13 00:00:00 UTC** — signal snapshot、factor values、signal panel 三源一致。

## 信号构成

```
risk_pressure = mean(flipped(vol_5h), flipped(vol_40h), flipped(downside_vol_20h), flipped(vol_of_vol_20h))
oscillator_exhaustion = mean(flipped(rsi_7h), flipped(rsi_28h))    ← rsi_28h 也 flip
raw_core_score = 0.60 × risk_pressure + 0.40 × oscillator_exhaustion
signal = xs_zscore(raw_core_score)
```

## 样例 1: BCHUSDT (LONG, Rank #1)

| 因子 | 原始值 | z-score | Flipped z | 方向 |
|------|--------|---------|-----------|------|
| vol_5h | 0.00410 | -0.494 | +0.494 | NEG → flip |
| vol_40h | 0.00698 | -0.649 | +0.649 | NEG → flip |
| downside_vol_20h | 0.00361 | -0.588 | +0.588 | NEG → flip |
| vol_of_vol_20h | 0.00294 | -0.640 | +0.640 | NEG → flip |
| rsi_7h | 35.14 | -0.758 | +0.758 | NEG → flip |
| rsi_28h | 47.87 | -0.279 | +0.279 | NEG → flip |

**Components:** risk_pressure = +0.587, oscillator = +0.900
**raw_core_score = 0.712 → signal = +1.087 (z-score)**

## 样例 2: HUSDT (SHORT, Rank #43)

| 因子 | 原始值 | z-score | Flipped z | 方向 |
|------|--------|---------|-----------|------|
| vol_5h | 0.03127 | +0.716 | -0.716 | NEG → flip |
| vol_40h | 0.06446 | +1.420 | -1.420 | NEG → flip |
| downside_vol_20h | 0.03127 | +0.749 | -0.749 | NEG → flip |
| vol_of_vol_20h | 0.02430 | +1.041 | -1.041 | NEG → flip |
| rsi_7h | 68.31 | +2.153 | -2.153 | NEG → flip |
| rsi_28h | 59.84 | +1.598 | -1.598 | NEG → flip |

**Components:** risk_pressure = -4.000, oscillator = -1.696
**raw_core_score = -3.078 → signal = -4.695 (z-score)**

## 样例 3: DOGEUSDT (NEUTRAL, Rank #21)

因子均处截面中等水平。risk_pressure = -0.047, oscillator = +0.704。
raw_core_score = 0.254 → signal = +0.387，不进入 long/short。

## 截面总览

- 266 total / 43 available / 8 long / 8 short / 27 neutral
- 每个 long +0.0625，每个 short -0.0625
- Gross/Net: 1.0/0.0

## 声明

- Phase 13 NOT STARTED
- No real execution, no alpha claim, no production claim
