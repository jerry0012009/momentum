# Phase 2D Review — Prior Shortlist

> Date: 2026-06-13
>
> Previous: Phase 2D draft COMPLETE (56 priors collected)
>
> Human decision: Phase 2D Review REQUIRED; Phase 2E NOT ALLOWED YET

---

## 1. Phase 2D 初稿评价

Phase 2D 初稿成功建立了 56 条外部因子先验记录，覆盖 5 个来源家族。

**总体评价：**
- ✅ 5 个主要来源家族均已覆盖
- ✅ 每条 prior 有 10 个结构化字段
- ✅ crypto 可用性 bucket 分类合理
- ⚠️ 部分 WQ101 的 adaptation mode 过于简化（默认写为 "rolling zscore"）
- ⚠️ 未区分 V0 已覆盖的 prior 与新增 prior
- ⚠️ 未形成 Phase 2E 实施候选清单

---

## 2. V0 已覆盖的 Prior（应 Skip）

以下 5 个 V0 DIAGNOSTIC_PROBE 已经覆盖了部分 prior 的核心逻辑：

| V0 Probe | 覆盖的 Prior | 处理方式 |
|----------|-------------|---------|
| `mom_20h` | `gtja_mom_01` | `skip_existing` — 完全重复 |
| `reversal_5h` | `gtja_rev_01` | `skip_existing` — 完全重复 |
| `volatility_20h` | `gtja_vol_01`, `q158_std_20d` | `skip_existing` — 完全重复 |
| `rsi_14h` | `gtja_tech_01` | `skip_existing` — 完全重复 |
| `bb_zscore_20h` | `gtja_tech_02` | `skip_existing` — 完全重复 |

**额外跳过的近似重复：**
- `gtja_mom_02` (60-day momentum) — 与 `mom_20h` 同族，仅窗口不同
- `gtja_vol_02` (60-day volatility) — 与 `volatility_20h` 同族
- `q158_ret_1d` (1-bar return) — 过短，噪音为主
- `q158_ret_20d` (20-bar return) — 与 `mom_20h` 近似
- `q158_ma_ratio_20d` (Price/MA20) — 与 `bb_zscore_20h` 高度相关

**跳过总数：10 条**

---

## 3. Park 的 Prior（需要额外数据）

以下 prior 需要当前 OHLCV 数据之外的数据源，暂不进入 Phase 2E：

| Prior ID | 原因 | 所需数据 |
|----------|------|---------|
| `crypto_funding` | `requires_derivatives` | Binance fundingRate API |
| `crypto_funding_ma` | `requires_derivatives` | Binance fundingRate API |
| `crypto_oi_change` | `requires_derivatives` | Binance openInterestHist API |
| `crypto_oi_vol_ratio` | `requires_derivatives` | Binance openInterestHist API |
| `crypto_basis` | `requires_derivatives` | Spot + Perp 对齐 |
| `crypto_ls_ratio` | `requires_derivatives` | Binance LS ratio API |
| `crypto_taker_imbalance` | `requires_microstructure` | aggTrades 分类 |
| `crypto_liq_volume` | `requires_external` | Coinglass 等第三方 |
| `crypto_exchange_flow` | `requires_external` | Glassnode/CryptoQuant |
| `q158_vwap_corr_20d` | `requires_vwap` | VWAP 可派生但需额外处理 |
| `gtja_turn_01` | 需要 total_volume（不可得） | 不适用 |
| `gtja_liq_02` | 需要 volume_share | 不适用 |

**Park 总数：12 条**

---

## 4. Phase 2E 候选 Shortlist

从剩余 prior 中筛选 16 条进入 shortlist。筛选标准：
- OHLCV-only 或 VWAP 可派生
- 公式简单，可独立实现
- 不重复 V0 已有因子
- 能在 `crypto_top50_usdt_perp_1h` 数据上直接实现

### Shortlist 概览

| # | candidate_id | 来源 | 因子名 | factor_family | adaptation_mode |
|---|-------------|------|--------|--------------|----------------|
| 1 | `wq101_alpha101` | WQ101 | Alpha#101 | intraday_position | direct_formula |
| 2 | `wq101_alpha06` | WQ101 | Alpha#6 | volume_price_corr | cross_sectional_rank |
| 3 | `wq101_alpha12` | WQ101 | Alpha#12 | volume_price_momentum | direct_formula |
| 4 | `wq101_alpha53` | WQ101 | Alpha#53 | intraday_position_delta | direct_formula |
| 5 | `wq101_alpha01` | WQ101 | Alpha#1 | conditional_momentum | cross_sectional_rank |
| 6 | `wq101_alpha34` | WQ101 | Alpha#34 | return_momentum | direct_formula |
| 7 | `wq101_alpha21` | WQ101 | Alpha#21 | mean_reversion | direct_formula |
| 8 | `wq101_alpha54` | WQ101 | Alpha#54 | intraday_return | direct_formula |
| 9 | `q158_ret_5d` | Alpha158 | Return 5-bar | momentum | direct_formula |
| 10 | `q158_ma_ratio_5d` | Alpha158 | Price/MA5 ratio | mean_reversion | direct_formula |
| 11 | `q158_vol_ratio_5d` | Alpha158 | Volume ratio 5-bar | volume_surge | direct_formula |
| 12 | `q158_high_low_range` | Alpha158 | High-Low Range | volatility | direct_formula |
| 13 | `tech_macd` | Technical | MACD Signal | trend | direct_formula |
| 14 | `tech_atr` | Technical | ATR 14 | volatility | direct_formula |
| 15 | `tech_stochastic` | Technical | Stochastic %K | oscillator | direct_formula |
| 16 | `tech_williams_r` | Technical | Williams %R | oscillator | direct_formula |

---

## 5. Cross-Sectional Rank Adaptation Policy

当前 `crypto_top50_usdt_perp_1h` universe 有 50 个 symbol，每个 timestamp 有足够样本做横截面排名。

**Adaptation 规则：**

| 场景 | adaptation_mode | 说明 |
|------|----------------|------|
| 原公式使用 `rank(x)`，且有 50+ symbols | `cross_sectional_rank` | 保留 timestamp-level 横截面 rank |
| 原公式使用 `rank(x)`，但样本不稳定 | `time_series_zscore` | 改用 rolling zscore |
| 需要百分位而非排名 | `rolling_percentile` | 使用 rolling percentile rank |
| 公式无 rank 运算 | `direct_formula` | 直接实现 |
| 复杂度过高或不适用 | `skip_or_park` | 暂不实现 |

**当前 shortlist 中的分配：**
- `cross_sectional_rank`: 2 条（Alpha#6, Alpha#1）— 保留横截面 rank
- `direct_formula`: 14 条 — 无 rank 运算，直接实现

---

## 6. Phase 2E 进入评估

**Phase 2E 进入条件：**
1. ✅ Phase 2D 交付物完成
2. ✅ Shortlist 已筛选（16 条候选）
3. ⏳ Human review of shortlist
4. ⏳ Human 批准进入 Phase 2E

**当前状态：** Phase 2D Review 完成，等 human 批准后可进入 Phase 2E。

**Phase 2E 第一批实施范围（建议）：**
- 优先 HIGH priority: `wq101_alpha101`, `tech_macd`, `tech_atr`, `tech_stochastic`, `tech_williams_r`, `q158_high_low_range`
- 次优先 MEDIUM priority: 其余 10 条

**预计 Phase 2E 交付物：**
- 新增 ~16 个 factor implementation in `scripts/build_factor_values.py`
- 新增 ~16 个 `factor_values.parquet`
- 更新 `evaluate_factors.py` 以支持批量评价
- 更新 `FACTOR_REGISTRY.md` 新增 factor 条目

**Status 升级规则：**
- 新实现的 factor 在首次跑通 evaluation 后，只能设为 `DIAGNOSTIC_PROBE`
- `CANDIDATE_REVIEW` 必须等 Phase 2E 结果出来，并经 human review 后才允许
- No factor may enter `CANDIDATE_REVIEW` during Phase 2E implementation automatically
- Human review required before any status upgrade beyond `DIAGNOSTIC_PROBE`
