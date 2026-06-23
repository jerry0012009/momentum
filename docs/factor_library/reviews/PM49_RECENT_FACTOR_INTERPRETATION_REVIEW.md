# PM-49: Recent Intake Factor Interpretation / Research Review

**Date**: 2026-06-23
**Scope**: 7 factors (PM-35 batch01 + Batch02 + Batch03)
**Methodology**: Factor Evaluation Layer v0.1 evidence-based review
**Disclaimer**: 本文件仅为研究诊断，不构成交易建议。所有结论基于历史数据，需进一步 signal-level 验证。

---

## Research Decision Summary

| Factor | Research Decision | Direction Status | Profile Score | Key Issue |
|--------|------------------|-----------------|---------------|-----------|
| rev_2h | LOWER_PRIORITY_REVIEW | DIRECTION_ALIGNED | 49.85 | IC强但LS弱，成本敏感 |
| mom_vol_adjusted_20h | FORMULA_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 44.64 | IC全部为负，与expected相反 |
| range_breakout_vol_confirm_20h | FORMULA_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 37.53 | IC全部为负，BTC beta敏感 |
| volume_pressure_20h | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 47.69 | IC全部为负，可能expected_direction反了 |
| xs_rank_mom_accel | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 47.99 | IC全部为负，加速度方向待确认 |
| up_down_vol_ratio_20h | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 44.64 | IC全部为负，bear dependent |
| clv_20h | CANDIDATE_POOL_WATCHLIST | SHORT_HORIZON_REVERSAL | 51.90 | 短期IC负，长期(72h)转正 |

---

## 最值得保留的因子

**clv_20h** (Close Location Value) — 唯一一个在最佳 horizon 上 empirical direction 与 expected direction 对齐的因子。72h RankIC = +0.018 (t=18.5)，机制清晰（close 在 high-low 区间的位置），distinct singleton（信息独特）。虽然 standalone 质量偏弱，但作为 diagnostic probe 和未来 candidate pool 成员有研究价值。

**rev_2h** (2h Reversal) — IC 方向完全对齐（1h RankIC = +0.036, t=29.8），但 LS 收益很薄且 cost collapsed。机制简单清晰。适合作为 reversal family 的 baseline 对比因子。

## 需要方向/公式复核的因子

- **mom_vol_adjusted_20h**: IC 全部为负（与 expected positive 冲突）。公式本身 `mom_20h / rolling_std` 逻辑合理，但 empirical evidence 表明高波动调整后的动量在 crypto 中是反向信号。需确认 expected_direction 是否应改为 negative。
- **range_breakout_vol_confirm_20h**: IC 全部为负。breakout + volume confirm 的组合在 crypto 中捕捉的是 mean reversion 而非 breakout continuation。BTC beta = 0.008（敏感），需复核公式逻辑。
- **volume_pressure_20h**: IC 全部为负。`sign(delta(close)) * volume` 的方向性成交量指标在 crypto 中可能反映的是 selling pressure（下跌时放量）。expected_direction 可能需要反转。
- **xs_rank_mom_accel**: IC 全部为负。动量加速度（mom_20h - delay(mom_20h,5)）的 cross-sectional rank，empirical 显示 deceleration 才是预测信号。expected_direction 待确认。
- **up_down_vol_ratio_20h**: IC 全部为负。`sum(vol*(ret>0),20)/sum(vol,20)` 本意是捕捉 bullish volume dominance，但 empirical 显示高 ratio 预测负收益。bear dependent，可能反映的是 capitulation dynamics。

## 只是 Diagnostic 的因子

**rev_2h**: 虽然 IC 强，但 profile class = BROAD_WATCHLIST, standalone_quality = REVIEW_REQUIRED, cost_risk = COST_COLLAPSED。在成本约束下不具备独立使用价值，适合作为 reversal family 的 diagnostic baseline。

## 可能进入 Future Candidate Pool 的因子

**clv_20h**: 唯一的 CANDIDATE_POOL_WATCHLIST。Close Location Value 在技术分析中是经典指标，在 crypto 72h horizon 上显示出显著的正向预测力。需要进一步验证在不同 market regime 下的稳定性。

---

## 逐因子详细分析

### 1. rev_2h — 2小时反转

**Factor Mechanism（因子机制）**

捕捉 2 小时内的短期价格反转效应。在 crypto 市场中，短期价格过度反应（overreaction）后倾向于回归。这是经典的 short-term reversal / mean reversion 信号，在传统市场和 crypto 中都有文献支持。

**Formula Semantics（公式语义）**

```
formula: -(close / close_2h_ago - 1)
```

- 符号：公式已做 sign-inverted（取负），higher factor_value = 更强的 prior loser = 更强的反转信号
- expected_direction = positive：因为是反转因子，prior loser 应该后续表现更好，所以 IC 应为正
- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | +0.036 | +29.8 | ✅ ALIGNED |
| 4h | +0.031 | +26.2 | ✅ ALIGNED |
| 24h | +0.015 | +13.1 | ✅ ALIGNED |
| 72h | +0.007 | +6.0 | ✅ ALIGNED |

**Classification: DIRECTION_ALIGNED** — 所有 horizon 的 IC 方向均与 expected_direction 一致。

**Evaluation Evidence**

- Best horizon: 1h（最高 |t-stat| = 29.8）
- RankIC mean: +0.036 (1h)
- RankIC t-stat: +29.8
- LS mean: +7.1e-5 (1h), 衰减至 -2.0e-3 (72h)
- LS Sharpe: 数据不足（canonical LS 无聚合字段）
- Ann Return: 数据不足
- Max Drawdown: 数据不足
- Paper viability: PAPER_MIXED
- Fee sensitivity: COST_COLLAPSED（成本敏感，fee_breakeven 不可用）
- Regime/BTC class: REGIME_ROBUST, LS-BTC Corr = -0.037（低相关）
- Quantile shape: NO_CLEAR_SHAPE
- Decile shape: NONLINEAR_MIXED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: DISTINCT_SINGLETON, cluster_size=1
- Marginal information: DISTINCT_SINGLETON
- Profile score: 49.85/100
- Profile class: BROAD_WATCHLIST
- Evidence completeness: 数据不足（canonical LS 缺聚合字段）

**Research Decision: LOWER_PRIORITY_REVIEW**

IC 方向正确且统计显著，但 LS 收益很薄（1h 仅 +7.1e-5），且 cost_risk = COST_COLLAPSED。在扣除交易成本后不具备独立使用价值。适合作为 reversal family 的 baseline 参考。

---

### 2. mom_vol_adjusted_20h — 波动率调整动量

**Factor Mechanism（因子机制）**

将 20 小时动量除以同期波动率，得到 volatility-adjusted momentum（类似 risk-adjusted momentum / Sharpe-like momentum）。直觉：在同等涨幅下，低波动的资产应该有更强的持续性。

**Formula Semantics（公式语义）**

```
formula: mom_20h / rolling_std(pct_change(close), 20)
notes: safe for zero vol
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅
- 定义清晰 ✅

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.021 | -20.5 | ❌ CONFLICT |
| 4h | -0.026 | -25.0 | ❌ CONFLICT |
| 24h | -0.022 | -20.5 | ❌ CONFLICT |
| 72h | -0.013 | -13.1 | ❌ CONFLICT |

**Classification: EXPECTED_DIRECTION_CONFLICT** — 所有 horizon 的 IC 均为负，与 expected positive 冲突。

**Evaluation Evidence**

- Best horizon: 4h（最高 |t-stat| = 25.0）
- RankIC mean: -0.026 (4h)
- RankIC t-stat: -25.0
- LS mean: +9.5e-5 (1h) → +5.3e-3 (72h)
- LS Sharpe: 数据不足
- Ann Return: 数据不足
- Max Drawdown: 数据不足
- Paper viability: PAPER_MIXED
- Fee sensitivity: COST_COLLAPSED
- Regime/BTC class: REGIME_ROBUST, LS-BTC Corr = +0.007（低相关）
- Quantile shape: NO_CLEAR_SHAPE
- Decile shape: BOTH_TAILS_U_SHAPED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: REDUNDANT_HIGH_QUALITY_ALTERNATIVE（冗余，有高质量替代）
- Marginal information: LOW_MARGINAL_INFO
- Profile score: 44.64/100
- Profile class: BROAD_WATCHLIST
- Evidence completeness: 数据不足

**Research Decision: FORMULA_REVIEW_REQUIRED**

IC 方向与 expected 完全相反。可能原因：
1. 在 crypto 中，低波动调整后的动量实际是反向信号（高波动环境下的 momentum 才有效）
2. expected_direction 设置错误，应为 negative
3. 公式中 `rolling_std` 的窗口（20h）可能与动量窗口（20h）产生 look-ahead bias

建议：复核 expected_direction，或考虑将公式改为 `mom_20h * rolling_std(...)`（高波动动量）。

---

### 3. range_breakout_vol_confirm_20h — 放量突破

**Factor Mechanism（因子机制）**

当价格突破 20 小时价格区间时（breakout），用成交量 z-score 进行确认。直觉：放量突破比缩量突破更有持续性。这是经典的技术分析信号。

**Formula Semantics（公式语义）**

```
formula: breakout_dist_20h * zscore(volume, 20) when breakout_dist_20h > 0
notes: volume-confirmed breakout
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 注意：仅在 `breakout_dist_20h > 0` 时激活（只做上突破），非突破时为 0
- 无符号反向问题 ✅

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.029 | -13.7 | ❌ CONFLICT |
| 4h | -0.035 | -16.4 | ❌ CONFLICT |
| 24h | -0.041 | -18.8 | ❌ CONFLICT |
| 72h | -0.035 | -16.8 | ❌ CONFLICT |

**Classification: EXPECTED_DIRECTION_CONFLICT** — 所有 horizon 的 IC 均为负。

**Evaluation Evidence**

- Best horizon: 24h（最高 |t-stat| = 18.8）
- RankIC mean: -0.041 (24h)
- RankIC t-stat: -18.8
- LS mean: +1.2e-4 (1h), +2.2e-4 (4h), -9.6e-4 (24h), +6.8e-4 (72h)
- LS Sharpe: 数据不足
- Ann Return: 数据不足
- Max Drawdown: 数据不足
- Paper viability: PAPER_MIXED
- Fee sensitivity: COST_COLLAPSED
- Regime/BTC class: BTC_BETA_SENSITIVE, LS-BTC Corr = +0.155（中等相关）, BTC Beta = +0.008
- Quantile shape: NO_CLEAR_SHAPE
- Decile shape: NONLINEAR_MIXED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_BOTH
- Redundancy: REDUNDANT_HIGH_QUALITY_ALTERNATIVE
- Marginal information: LOW_MARGINAL_INFO
- Profile score: 37.53/100
- Profile class: PROMISING_BUT_REGIME_DEPENDENT

**Research Decision: FORMULA_REVIEW_REQUIRED**

IC 方向与 expected 完全相反。在 crypto 中，"放量突破" 实际上可能捕捉的是 breakout exhaustion（突破后的力竭），而非 breakout continuation。BTC beta 敏感（+0.008），说明与市场整体走势高度相关。建议：
1. 复核 breakout 信号在 crypto 中的有效性
2. 考虑是否应做双向突破（包括下突破）
3. 或将 expected_direction 改为 negative（突破后反转）

---

### 4. volume_pressure_20h — 方向性成交量

**Factor Mechanism（因子机制）**

滚动 20 小时的方向性成交量压力。`sign(delta(close)) * volume`：价格上涨时的成交量为正，下跌时为负。直觉：正向成交量压力（买方主导）应该预测未来上涨。

**Formula Semantics（公式语义）**

```
formula: rolling_mean(sign(delta(close, 1)) * volume, 20)
notes: directional volume pressure
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅
- 但 empirical 方向与 expected 相反

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.011 | -11.3 | ❌ CONFLICT |
| 4h | -0.015 | -14.7 | ❌ CONFLICT |
| 24h | -0.016 | -16.3 | ❌ CONFLICT |
| 72h | -0.012 | -12.5 | ❌ CONFLICT |

**Classification: EXPECTED_DIRECTION_CONFLICT**

**Evaluation Evidence**

- Best horizon: 24h（最高 |t-stat| = 16.3）
- RankIC mean: -0.016 (24h)
- RankIC t-stat: -16.3
- LS mean: +7.2e-5 (1h) → +3.6e-3 (72h)
- Paper viability: PAPER_MIXED
- Fee sensitivity: COST_COLLAPSED
- Regime/BTC class: VOL_DEPENDENT, LS-BTC Corr = +0.149（中等相关）
- Quantile shape: WEAK_MONOTONIC
- Decile shape: NONLINEAR_MIXED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: DISTINCT_SINGLETON
- Marginal information: DISTINCT_SINGLETON
- Profile score: 47.69/100
- Profile class: BROAD_WATCHLIST

**Research Decision: DIRECTION_REVIEW_REQUIRED**

IC 方向与 expected 相反。可能原因：
1. 在 crypto 中，下跌放量（selling pressure / capitulation）反而是反转信号的前兆
2. `sign(delta(close)) * volume` 捕捉的可能是 selling panic（下跌时成交量放大），而非 bullish pressure
3. expected_direction 可能需要反转为 negative

建议：复核 expected_direction，或考虑改为 `sign(delta(close)) * volume` 的反向（selling pressure 信号）。

---

### 5. xs_rank_mom_accel — 截面动量加速度

**Factor Mechanism（因子机制）**

动量加速度 = mom_20h - delay(mom_20h, 5)，然后做 cross-sectional rank。直觉：动量正在加速的资产应该有更强的持续性。这是 momentum continuation / acceleration 信号。

**Formula Semantics（公式语义）**

```
formula: xs_rank(mom_20h - delay(mom_20h, 5))
notes: Per-symbol momentum acceleration; cross-sectional rank applied by caller
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅
- 但 empirical 方向与 expected 相反

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.024 | -20.5 | ❌ CONFLICT |
| 4h | -0.024 | -21.0 | ❌ CONFLICT |
| 24h | -0.019 | -15.8 | ❌ CONFLICT |
| 72h | -0.011 | -9.5 | ❌ CONFLICT |

**Classification: EXPECTED_DIRECTION_CONFLICT**

**Evaluation Evidence**

- Best horizon: 4h（最高 |t-stat| = 21.0）
- RankIC mean: -0.024 (4h)
- RankIC t-stat: -21.0
- LS mean: +4.5e-6 (1h) → +1.0e-3 (72h)
- Paper viability: PAPER_REVIEW_REQUIRED
- Fee sensitivity: INSUFFICIENT_DATA
- Regime/BTC class: REGIME_ROBUST, LS-BTC Corr = -0.030（低相关）
- Quantile shape: NO_CLEAR_SHAPE
- Decile shape: NONLINEAR_MIXED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: DISTINCT_SINGLETON
- Marginal information: DISTINCT_SINGLETON
- Profile score: 47.99/100
- Profile class: BROAD_WATCHLIST

**Research Decision: DIRECTION_REVIEW_REQUIRED**

IC 方向与 expected 相反。在 crypto 中，动量 deceleration（加速度为负）可能是 continuation 信号（当前趋势正在减速但尚未反转）。建议复核 expected_direction 是否应为 negative。

---

### 6. up_down_vol_ratio_20h — 上涨成交量占比

**Factor Mechanism（因子机制）**

20 小时内上涨 bar 的成交量占总成交量的比例。直觉：bullish volume dominance（买方主导成交量）应该预测未来上涨。

**Formula Semantics（公式语义）**

```
formula: sum(vol*(ret>0), 20) / sum(vol, 20)
notes: buying pressure ratio; higher = bullish volume dominance
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅
- 但 empirical 方向与 expected 相反

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.016 | -18.5 | ❌ CONFLICT |
| 4h | -0.020 | -23.1 | ❌ CONFLICT |
| 24h | -0.018 | -20.6 | ❌ CONFLICT |
| 72h | -0.014 | -16.8 | ❌ CONFLICT |

**Classification: EXPECTED_DIRECTION_CONFLICT**

**Evaluation Evidence**

- Best horizon: 4h（最高 |t-stat| = 23.1）
- RankIC mean: -0.020 (4h)
- RankIC t-stat: -23.1
- LS mean: +7.7e-5 (1h) → +4.1e-3 (72h)
- Paper viability: PAPER_MIXED
- Fee sensitivity: COST_COLLAPSED
- Regime/BTC class: BEAR_DEPENDENT, LS-BTC Corr = +0.011（低相关）
- Quantile shape: WEAK_MONOTONIC
- Decile shape: BOTH_TAILS_U_SHAPED
- Rolling stability: INSUFFICIENT_HISTORY
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: LOWER_MARGINAL_INFORMATION_MEMBER
- Marginal information: LOW_MARGINAL_INFO
- Profile score: 44.64/100
- Profile class: PROMISING_BUT_REGIME_DEPENDENT

**Research Decision: DIRECTION_REVIEW_REQUIRED**

IC 方向与 expected 完全相反。可能原因：
1. 在 crypto 中，高上涨成交量占比可能反映的是 retail buying frenzy（散户追涨），随后反转
2. 或者下跌时的缩量（low selling volume）反而是 bearish signal（缺乏 buying interest）
3. expected_direction 可能需要反转为 negative

---

### 7. clv_20h — Close Location Value

**Factor Mechanism（因子机制）**

Close Location Value：衡量收盘价在 high-low 区间中的位置。+1 = 收盘在最高价，-1 = 收盘在最低价。这是经典的技术分析指标（类似 Williams %R 的变体），在传统市场中用于衡量 buying/selling pressure。

**Formula Semantics（公式语义）**

```
formula: mean(((close-low)-(high-close))/(high-low+eps), 20)
notes: Close Location Value; +1=close at high, -1=close at low
```

- 公式与命名一致 ✅
- 公式与 intuition 一致 ✅
- 无符号反向问题 ✅
- 定义清晰 ✅

**Expected Direction Review**

| Horizon | RankIC | t-stat | Direction |
|---------|--------|--------|-----------|
| 1h | -0.003 | -3.5 | ❌ CONFLICT (weak) |
| 4h | -0.001 | -0.7 | ⚪ INCONCLUSIVE |
| 24h | +0.012 | +11.6 | ✅ ALIGNED |
| 72h | +0.018 | +18.5 | ✅ ALIGNED |

**Classification: SHORT_HORIZON_REVERSAL** — 短期 IC 为负（weak），长期 IC 转正且统计显著。这是经典的 short-horizon reversal pattern。

**Evaluation Evidence**

- Best horizon: 72h（最高 |t-stat| = 18.5，且方向对齐）
- RankIC mean: +0.018 (72h)
- RankIC t-stat: +18.5
- LS mean: -4.6e-5 (1h), +6.2e-5 (4h), +9.8e-4 (24h), +1.9e-3 (72h)
- LS Sharpe: 数据不足
- Ann Return: 数据不足
- Max Drawdown: 数据不足
- Paper viability: PAPER_REVIEW_REQUIRED
- Fee sensitivity: INSUFFICIENT_DATA
- Regime/BTC class: BEAR_DEPENDENT, LS-BTC Corr = +0.037（低相关）
- Quantile shape: NO_CLEAR_SHAPE
- Decile shape: NONLINEAR_MIXED
- Rolling stability: STABLE_WEAK（弱稳定）
- Capacity/liquidity: WATCH_LIQUIDITY
- Redundancy: DISTINCT_SINGLETON
- Marginal information: DISTINCT_SINGLETON
- Profile score: 51.90/100（7 因子中最高）
- Profile class: UNIQUE_BUT_WEAK

**Research Decision: CANDIDATE_POOL_WATCHLIST**

这是 7 个因子中唯一一个在最佳 horizon（72h）上 empirical direction 与 expected direction 对齐的因子。Close Location Value 是经典技术指标，机制清晰，信息独特（distinct singleton）。虽然 standalone 质量偏弱（UNIQUE_BUT_WEAK），但：
1. 72h RankIC = +0.018 (t=18.5) 统计显著
2. 信息独特，不与其他因子冗余
3. 在 bear market 中表现更好（BEAR_DEPENDENT）
4. 短期反转模式（1h IC 为负，72h 转正）值得进一步研究

建议保留作为 future candidate pool 成员，待进一步验证 regime stability 和 capacity。

---

## 附录：方向复核分类定义

| 分类 | 含义 |
|------|------|
| DIRECTION_ALIGNED | 所有 horizon 的 IC 方向与 expected_direction 一致 |
| SHORT_HORIZON_REVERSAL | 短期 IC 与 expected 相反，长期 IC 与 expected 一致 |
| EXPECTED_DIRECTION_CONFLICT | 所有 horizon 的 IC 方向与 expected_direction 冲突 |
| FORMULA_SIGN_REVIEW_REQUIRED | 公式可能存在符号问题 |
| REGIME_CONDITIONAL_DIRECTION | IC 方向取决于市场状态 |
| INCONCLUSIVE | 证据不足，无法判断 |

---

## 附录：Research Decision 分类定义

| 分类 | 含义 |
|------|------|
| KEEP_FOR_RESEARCH_REVIEW | 保留用于研究复核 |
| CANDIDATE_POOL_WATCHLIST | 进入候选池观察名单 |
| DIRECTION_REVIEW_REQUIRED | 需要复核 expected_direction |
| FORMULA_REVIEW_REQUIRED | 需要复核公式逻辑 |
| COST_SENSITIVE_DIAGNOSTIC | 成本敏感，仅作诊断用途 |
| REGIME_DEPENDENT_DIAGNOSTIC | 依赖市场状态，仅作诊断用途 |
| LOW_PRIORITY_REVIEW | 低优先级复核 |
| DIAGNOSTIC_ONLY | 仅作诊断用途 |
| DROP_NOT_RECOMMENDED_FOR_NOW | 暂不推荐使用 |

---

*PM-49 | 2026-06-23 | Factor Evaluation Layer v0.1 evidence-based review*
