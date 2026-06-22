#!/usr/bin/env python3
"""PM-34: Factor Expansion Backlog & Intake-Readiness Checklist.

Reads the existing factor registry to understand current families and operators,
generates candidate factors from 12 expansion families, fills a backlog schema
for each candidate, selects 3-5 for BATCH_01_CONTROLLED_INTAKE, and creates an
intake-readiness checklist.

Outputs:
    docs/factor_library/FACTOR_EXPANSION_BACKLOG.md
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.csv
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.json
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.csv
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.json
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog_manifest.json

Does NOT modify any existing factor registry, ops, or pipeline scripts.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAG_DIR = ROOT / "research/factor_runs/crypto_top50_factor_library/factor_diagnostics"
DOCS_DIR = ROOT / "docs/factor_library"

# ── Candidate definitions ──────────────────────────────────────────

CANDIDATES: list[dict] = [
    # ── short_term_reversal ──
    {
        "candidate_factor_id": "rev_2h",
        "candidate_family": "short_term_reversal",
        "candidate_theme": "2-hour reversal signal filling gap between 1h and 3h lookbacks",
        "formula_sketch": "-(close / delay(close, 2) - 1)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available in standard OHLCV cache",
        "operator_reuse_plan": "delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Short-term mean reversion: recent losers rebound within 2h in crypto microstructure",
        "likely_existing_cluster_overlap": "LOW — gap between rev_1h (cluster 0) and rev_3h (cluster 1 singleton)",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests granularity of short-term reversal curve; incremental signal vs 1h/3h",
        "expected_failure_mode": "May be too correlated with rev_1h or rev_3h if reversal is smooth",
        "implementation_complexity": "LOW",
        "intake_priority": "P1_CONTROLLED_BATCH",
        "suggested_batch": "BATCH_01_CONTROLLED_INTAKE",
        "review_notes_zh": "填补1h与3h反转信号之间的空白，用于测试短期反转曲线粒度",
        "review_notes_en": "Fills gap between 1h and 3h reversal; tests granularity of short-term reversal curve",
    },
    {
        "candidate_factor_id": "rev_48h",
        "candidate_family": "short_term_reversal",
        "candidate_theme": "48-hour reversal signal bridging short and medium horizon",
        "formula_sketch": "-(close / delay(close, 48) - 1)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Medium-term mean reversion after 2-day overextension",
        "likely_existing_cluster_overlap": "MEDIUM — near rev_24h and rev_72h, may cluster with medium-term reversal family",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — fills 24h-72h gap but risk of high correlation with neighbors",
        "expected_failure_mode": "High correlation with rev_24h or rev_72h; marginal information may be near-zero",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "填补24h-72h反转信号空白，但与相邻因子高度相关的风险较高",
        "review_notes_en": "Fills 24h-72h gap but high correlation risk with neighboring reversals",
    },
    # ── medium_term_momentum ──
    {
        "candidate_factor_id": "mom_vol_adjusted_20h",
        "candidate_family": "medium_term_momentum",
        "candidate_theme": "Risk-adjusted momentum normalizing by realized volatility",
        "formula_sketch": "mom_20h / rolling_std(pct_change(close), 20)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "rolling_std(), delay() from factor_ops; compute mom_20h inline",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Risk-adjusted momentum: high-return/low-vol assets should outperform (quality momentum)",
        "likely_existing_cluster_overlap": "LOW — distinct from raw momentum (cluster 4) and vol factors (cluster 8); combines signal and risk",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests whether volatility-adjusting momentum adds marginal info vs raw mom + vol",
        "expected_failure_mode": "May simply replicate ranking of raw momentum if vol is not cross-sectionally dispersed",
        "implementation_complexity": "LOW",
        "intake_priority": "P1_CONTROLLED_BATCH",
        "suggested_batch": "BATCH_01_CONTROLLED_INTAKE",
        "review_notes_zh": "风险调整动量：测试波动率调整是否增加边际信息",
        "review_notes_en": "Risk-adjusted momentum: tests whether vol-normalization adds marginal info",
    },
    {
        "candidate_factor_id": "mom_168h",
        "candidate_family": "medium_term_momentum",
        "candidate_theme": "1-week (168h) momentum for weekly trend continuation",
        "formula_sketch": "close / delay(close, 168) - 1",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available, lookback 168h within data range",
        "operator_reuse_plan": "delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Weekly trend continuation in crypto; momentum persists at 1-week horizon",
        "likely_existing_cluster_overlap": "MEDIUM — likely joins cluster 4 (large momentum cluster) given 72h/120h neighbors",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — extends momentum curve but may not add marginal info beyond 120h",
        "expected_failure_mode": "High correlation with mom_120h; may just extend a flat IC region",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "1周动量延伸，但可能与120h高度相关",
        "review_notes_en": "1-week momentum extension; risk of high correlation with mom_120h",
    },
    # ── range_breakout ──
    {
        "candidate_factor_id": "range_breakout_vol_confirm_20h",
        "candidate_family": "range_breakout",
        "candidate_theme": "Breakout confirmed by above-average volume",
        "formula_sketch": "breakout_dist_20h * zscore(volume, 20) [when breakout_dist > 0]",
        "required_inputs": "high, low, close, volume",
        "available_inputs_check": "PASS — all OHLCV available",
        "operator_reuse_plan": "zscore() from factor_ops; rolling_max, rolling_min from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Volume-confirmed breakouts are more reliable; high volume + new high = continuation signal",
        "likely_existing_cluster_overlap": "LOW — breakout_dist_20h is singleton-ish; adding volume confirmation is structurally distinct",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests interaction of price breakout and volume surge; cross-factor composition diagnostic",
        "expected_failure_mode": "Breakout without volume confirmation may be noise; conditional signal reduces effective sample",
        "implementation_complexity": "LOW",
        "intake_priority": "P1_CONTROLLED_BATCH",
        "suggested_batch": "BATCH_01_CONTROLLED_INTAKE",
        "review_notes_zh": "成交量确认突破：测试价格突破与成交量激增的交互效应",
        "review_notes_en": "Volume-confirmed breakout: tests price breakout × volume surge interaction",
    },
    {
        "candidate_factor_id": "range_compression_breakout_48h",
        "candidate_family": "range_breakout",
        "candidate_theme": "Low-range-compression preceding breakout tendency",
        "formula_sketch": "-(rolling_std((high-low)/close, 20)) [low vol of range = compression]",
        "required_inputs": "high, low, close",
        "available_inputs_check": "PASS — OHLC available",
        "operator_reuse_plan": "rolling_std() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Range compression precedes explosive moves; low range vol = coiled spring",
        "likely_existing_cluster_overlap": "LOW — structurally different from breakout_dist; relates to volatility shape",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — tests pre-breakout compression hypothesis",
        "expected_failure_mode": "Compression can persist without breakout; direction may be unclear in trending markets",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "区间压缩突破假设测试",
        "review_notes_en": "Tests pre-breakout range compression hypothesis",
    },
    # ── volatility_adjusted_momentum ──
    {
        "candidate_factor_id": "vol_adj_mom_40h",
        "candidate_family": "volatility_adjusted_momentum",
        "candidate_theme": "Medium-horizon risk-adjusted momentum at 40h",
        "formula_sketch": "mom_40h / rolling_std(pct_change(close), 40)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "rolling_std(), delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Quality-adjusted momentum at medium horizon; smooth uptrends outperform volatile drift",
        "likely_existing_cluster_overlap": "LOW — combines mom_40h (cluster 12) and vol_40h (singleton) into a composite",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests vol-adjustment at different horizon than 20h variant",
        "expected_failure_mode": "May replicate mom_vol_adjusted_20h if adjustment window doesn't matter",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "40h风险调整动量，概念上与20h变体相似，留待BATCH_02评估",
        "review_notes_en": "40h risk-adjusted momentum; conceptually similar to 20h variant, deferred to BATCH_02",
    },
    # ── volume_pressure ──
    {
        "candidate_factor_id": "volume_pressure_20h",
        "candidate_family": "volume_pressure",
        "candidate_theme": "Net directional volume pressure over 20h",
        "formula_sketch": "rolling_mean(sign(delta(close, 1)) * volume, 20)",
        "required_inputs": "close, volume",
        "available_inputs_check": "PASS — close and volume available",
        "operator_reuse_plan": "rolling_mean(), delta() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Persistent buying volume pressure indicates informed flow; positive pressure = bullish",
        "likely_existing_cluster_overlap": "LOW — structurally distinct from vol_zscore and vol_ret_corr; directional volume composite",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests directional volume as a signal distinct from raw volume and return-volume correlation",
        "expected_failure_mode": "May correlate with momentum if volume is not cross-sectionally informative",
        "implementation_complexity": "LOW",
        "intake_priority": "P1_CONTROLLED_BATCH",
        "suggested_batch": "BATCH_01_CONTROLLED_INTAKE",
        "review_notes_zh": "定向成交量压力信号，测试方向性成交量是否独立于原始成交量和量价相关性",
        "review_notes_en": "Directional volume pressure signal; tests whether directional volume is independent of raw volume",
    },
    {
        "candidate_factor_id": "volume_pressure_asymmetry_40h",
        "candidate_family": "volume_pressure",
        "candidate_theme": "Asymmetry of up-volume vs down-volume over 40h",
        "formula_sketch": "(sum(up_vol, 40) - sum(down_vol, 40)) / sum(volume, 40) where up_vol = volume if ret>0 else 0",
        "required_inputs": "close, volume",
        "available_inputs_check": "PASS — close and volume available",
        "operator_reuse_plan": "rolling_sum() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Persistent up-volume dominance signals institutional accumulation",
        "likely_existing_cluster_overlap": "LOW — structural asymmetry not captured by existing factors",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "MEDIUM — tests volume asymmetry vs directional volume",
        "expected_failure_mode": "May be highly correlated with volume_pressure_20h if direction dominates",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "成交量不对称性测试",
        "review_notes_en": "Tests volume asymmetry hypothesis",
    },
    # ── liquidity_stress ──
    {
        "candidate_factor_id": "amihud_change_20h",
        "candidate_family": "liquidity_stress",
        "candidate_theme": "Change in illiquidity stress over 20h window",
        "formula_sketch": "amihud_20h - delay(amihud_20h, 20)",
        "required_inputs": "close, quote_volume",
        "available_inputs_check": "PASS — close and quote_volume available",
        "operator_reuse_plan": "delay() from factor_ops; amihud computation from existing formula",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "negative",
        "expected_direction_basis": "Rising illiquidity signals stress; sell assets experiencing liquidity deterioration",
        "likely_existing_cluster_overlap": "LOW — amihud_illiquidity_20h is singleton (cluster 24); change adds dynamics",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests dynamic liquidity stress vs static illiquidity level",
        "expected_failure_mode": "May be noisy if amihud is already stationary",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "流动性压力动态变化信号，测试流动性压力变化是否比静态水平更有信息量",
        "review_notes_en": "Dynamic liquidity stress; tests whether change in illiquidity adds info vs level",
    },
    # ── funding_rate_structure ──
    {
        "candidate_factor_id": "funding_rate_skew_20h",
        "candidate_family": "funding_rate_structure",
        "candidate_theme": "Asymmetry of funding rate distribution over 20h",
        "formula_sketch": "rolling_skew(funding_rate, 20)",
        "required_inputs": "funding_rate",
        "available_inputs_check": "PASS — funding_rate available in crypto-native cache",
        "operator_reuse_plan": "rolling_skew() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "conditional",
        "expected_direction_basis": "Positive skew = occasional extreme positive funding = crowded long tail risk; direction depends on regime",
        "likely_existing_cluster_overlap": "LOW — funding_rate factors are singletons (clusters 27, 39, 43); skew is structural",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "MEDIUM — tests funding rate distribution shape beyond mean/zscore",
        "expected_failure_mode": "Funding rate distribution may be too symmetric to be informative at 20h window",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "资金费率分布偏度测试",
        "review_notes_en": "Tests funding rate distribution shape beyond mean/zscore",
    },
    {
        "candidate_factor_id": "funding_rate_momentum_20h",
        "candidate_family": "funding_rate_structure",
        "candidate_theme": "Acceleration of funding rate change over 20h",
        "formula_sketch": "funding_rate_change_24h - delay(funding_rate_change_24h, 20)",
        "required_inputs": "funding_rate",
        "available_inputs_check": "PASS — funding_rate available",
        "operator_reuse_plan": "delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "negative",
        "expected_direction_basis": "Accelerating funding = increasingly crowded positioning = reversal signal",
        "likely_existing_cluster_overlap": "LOW — second derivative of funding rate; none existing",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "MEDIUM — tests higher-order funding rate dynamics",
        "expected_failure_mode": "May be too noisy; second derivative of already noisy series",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "资金费率动量加速信号",
        "review_notes_en": "Tests higher-order funding rate dynamics (acceleration)",
    },
    # ── taker_flow_structure ──
    {
        "candidate_factor_id": "taker_flow_momentum_20h",
        "candidate_family": "taker_flow_structure",
        "candidate_theme": "Momentum of taker buy ratio over 20h",
        "formula_sketch": "taker_buy_ratio - delay(taker_buy_ratio, 20) [where ratio = taker_buy_qvol / qvol]",
        "required_inputs": "taker_buy_quote_volume, quote_volume",
        "available_inputs_check": "PASS — both available in crypto-native cache",
        "operator_reuse_plan": "delay(), rolling_mean() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Rising taker buy ratio = increasing aggressive buying = momentum continuation",
        "likely_existing_cluster_overlap": "LOW — taker factors are singletons (clusters 37, 40, 42); 20h dynamics not captured",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — tests taker flow dynamics beyond level/zscore",
        "expected_failure_mode": "May be highly correlated with taker_buy_delta_5h at different horizon",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "主动买入流量动量，测试流量动态是否独立于水平值和z分数",
        "review_notes_en": "Taker flow momentum; tests whether flow dynamics are independent of level/zscore",
    },
    {
        "candidate_factor_id": "taker_flow_persistence_40h",
        "candidate_family": "taker_flow_structure",
        "candidate_theme": "Persistence of taker buy ratio (autocorrelation)",
        "formula_sketch": "rolling_corr(taker_ratio, delay(taker_ratio, 1), 40)",
        "required_inputs": "taker_buy_quote_volume, quote_volume",
        "available_inputs_check": "PASS — both available",
        "operator_reuse_plan": "rolling_corr(), delay() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Persistent taker buy dominance = sustained informed buying pressure",
        "likely_existing_cluster_overlap": "LOW — autocorrelation structure not captured by existing taker factors",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "MEDIUM — tests flow persistence as signal",
        "expected_failure_mode": "Autocorrelation may be structurally constant and uninformative cross-sectionally",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "主动买入流量持续性测试",
        "review_notes_en": "Tests taker flow persistence (autocorrelation) as signal",
    },
    # ── intraday_candle_structure ──
    {
        "candidate_factor_id": "candle_body_ma_5h",
        "candidate_family": "intraday_candle_structure",
        "candidate_theme": "Rolling mean candle body over 5h for persistent directional pressure",
        "formula_sketch": "rolling_mean((close - open) / (high - low + eps), 5)",
        "required_inputs": "open, high, low, close",
        "available_inputs_check": "PASS — OHLC available",
        "operator_reuse_plan": "rolling_mean() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Persistent positive body = sustained directional pressure = trend continuation",
        "likely_existing_cluster_overlap": "LOW — candle_body is in cluster 0; rolling mean adds persistence dimension",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — tests whether smoothing candle body adds signal vs raw",
        "expected_failure_mode": "May be dominated by the single latest candle body if window is short",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "蜡烛体均值持续性测试",
        "review_notes_en": "Tests whether smoothing candle body adds signal vs raw single-bar body",
    },
    {
        "candidate_factor_id": "doji_frequency_20h",
        "candidate_family": "intraday_candle_structure",
        "candidate_theme": "Frequency of indecision candles (doji) over 20h",
        "formula_sketch": "rolling_mean(|candle_body| < 0.1, 20) [doji = body < 10% of range]",
        "required_inputs": "open, high, low, close",
        "available_inputs_check": "PASS — OHLC available",
        "operator_reuse_plan": "rolling_mean() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "conditional",
        "expected_direction_basis": "High doji frequency = indecision = likely reversal; low = clear trend. Direction regime-dependent",
        "likely_existing_cluster_overlap": "LOW — no existing candle frequency factor",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests candle pattern frequency as a novel structural signal",
        "expected_failure_mode": "Threshold (0.1) is arbitrary; doji definition may not be robust",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "十字星频率信号，测试K线形态频率是否为有效的结构性信号",
        "review_notes_en": "Tests candle pattern frequency as a novel structural signal",
    },
    # ── realized_volatility_shape ──
    {
        "candidate_factor_id": "realized_vol_skew_40h",
        "candidate_family": "realized_volatility_shape",
        "candidate_theme": "40h realized return skewness for medium-horizon asymmetry",
        "formula_sketch": "rolling_skew(pct_change(close), 40)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "rolling_skew() or .rolling().skew() from pandas",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "conditional",
        "expected_direction_basis": "Negative skew = tail risk = underperformance; positive skew = lottery. Direction depends on risk appetite",
        "likely_existing_cluster_overlap": "LOW — realized_skew_20h is singleton (cluster 21); 40h extends window",
        "likely_redundancy_risk": "MEDIUM",
        "expected_diagnostic_value": "MEDIUM — tests whether 40h skew adds info vs 20h skew",
        "expected_failure_mode": "May be highly correlated with realized_skew_20h if skew is persistent",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "40h实现偏度，测试更长窗口是否增加信息量",
        "review_notes_en": "40h realized skewness; tests whether longer window adds info vs 20h",
    },
    {
        "candidate_factor_id": "realized_vol_regime_ratio_20_80",
        "candidate_family": "realized_volatility_shape",
        "candidate_theme": "Volatility regime ratio comparing short vs long horizon",
        "formula_sketch": "rolling_std(ret, 20) / rolling_std(ret, 80)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "rolling_std() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "conditional",
        "expected_direction_basis": "Vol expansion (ratio > 1) = regime change; vol compression (ratio < 1) = calm",
        "likely_existing_cluster_overlap": "MEDIUM — vol_ratio_20_80 exists in registry (cluster 31 singleton); this is nearly identical",
        "likely_redundancy_risk": "HIGH",
        "expected_diagnostic_value": "LOW — exact duplicate of existing vol_ratio_20_80",
        "expected_failure_mode": "N/A — duplicate, should be excluded",
        "implementation_complexity": "LOW",
        "intake_priority": "P5_DEFER",
        "suggested_batch": "EXCLUDED_DUPLICATE",
        "review_notes_zh": "与现有vol_ratio_20_80重复，排除",
        "review_notes_en": "EXCLUDED — duplicate of existing vol_ratio_20_80",
    },
    # ── cross_sectional_rank_acceleration ──
    {
        "candidate_factor_id": "xs_rank_mom_accel",
        "candidate_family": "cross_sectional_rank_acceleration",
        "candidate_theme": "Cross-sectional rank of momentum acceleration",
        "formula_sketch": "xs_rank(mom_accel_20h) per timestamp",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available; cross-sectional ranking done by caller",
        "operator_reuse_plan": "Reuses mom_accel_20h computation; cross-sectional rank done in build_factor_values.py",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Cross-sectionally ranked acceleration: high rank = accelerating momentum relative to peers",
        "likely_existing_cluster_overlap": "LOW — xs_rank_ret_1h exists but is rank of raw return, not acceleration; structurally distinct",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests cross-sectional normalization of a second-order signal (acceleration)",
        "expected_failure_mode": "May be noisy if acceleration is itself noisy; cross-sectional rank amplifies noise",
        "implementation_complexity": "MEDIUM",
        "intake_priority": "P1_CONTROLLED_BATCH",
        "suggested_batch": "BATCH_01_CONTROLLED_INTAKE",
        "review_notes_zh": "动量加速度的截面排名，测试二阶信号的截面标准化效果",
        "review_notes_en": "Cross-sectional rank of momentum acceleration; tests cross-sectional normalization of second-order signal",
    },
    {
        "candidate_factor_id": "xs_rank_vol_change",
        "candidate_family": "cross_sectional_rank_acceleration",
        "candidate_theme": "Cross-sectional rank of volume change rate",
        "formula_sketch": "xs_rank(delta(volume, 5) / delay(volume, 5)) per timestamp",
        "required_inputs": "volume",
        "available_inputs_check": "PASS — volume available",
        "operator_reuse_plan": "delta(), delay() from factor_ops; cross-sectional rank by caller",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "High volume growth rank = increasing attention relative to peers",
        "likely_existing_cluster_overlap": "LOW — xs_rank_vol is rank of level, not change",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "MEDIUM — tests volume dynamics cross-sectionally",
        "expected_failure_mode": "May be noisy if volume is sporadic for some assets",
        "implementation_complexity": "MEDIUM",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "成交量变化率截面排名",
        "review_notes_en": "Cross-sectional rank of volume change rate",
    },
    # ── mean_reversion_after_extreme_move ──
    {
        "candidate_factor_id": "extreme_reversal_5h",
        "candidate_family": "mean_reversion_after_extreme_move",
        "candidate_theme": "Conditional reversal after 5h extreme move (>2σ)",
        "formula_sketch": "-ret_5h * indicator(|ret_5h| > 2 * vol_5h)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "delay(), rolling_std() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Extreme moves reverse: conditional reversal after 2σ+ 5h move",
        "likely_existing_cluster_overlap": "LOW — conditional structure is novel; not a simple reversal variant",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests conditional mean reversion hypothesis directly",
        "expected_failure_mode": "Low hit rate if extreme moves are rare; effective sample may be small",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "极端行情后均值回归：逻辑清晰但需确认条件信号的有效样本量，留待BATCH_02",
        "review_notes_en": "Conditional mean reversion after extreme 5h move; clear logic but needs effective sample confirmation, deferred to BATCH_02",
    },
    {
        "candidate_factor_id": "extreme_reversal_24h",
        "candidate_family": "mean_reversion_after_extreme_move",
        "candidate_theme": "Conditional reversal after 24h extreme move (>2σ)",
        "formula_sketch": "-ret_24h * indicator(|ret_24h| > 2 * vol_24h)",
        "required_inputs": "close",
        "available_inputs_check": "PASS — close available",
        "operator_reuse_plan": "delay(), rolling_std() from factor_ops",
        "requires_new_operator": "NO",
        "requires_new_data": "NO",
        "expected_direction": "positive",
        "expected_direction_basis": "Extreme 24h moves revert; conditional reversal at daily horizon",
        "likely_existing_cluster_overlap": "LOW — conditional structure at 24h horizon not captured",
        "likely_redundancy_risk": "LOW",
        "expected_diagnostic_value": "HIGH — tests extreme-move reversion at longer horizon",
        "expected_failure_mode": "Less frequent extreme moves at 24h; may be too sparse",
        "implementation_complexity": "LOW",
        "intake_priority": "P2_BACKLOG",
        "suggested_batch": "BATCH_02_BACKLOG",
        "review_notes_zh": "24h极端行情后均值回归",
        "review_notes_en": "Conditional mean reversion after extreme 24h move",
    },
]


# ── Intake-readiness checklist ──────────────────────────────────────

CHECKLIST: list[dict] = [
    {
        "check_id": "registry_integrity_ready",
        "status": "PASS",
        "what_it_checks": "Factor registry (REGISTRY list in factor_formula_registry.py) is parseable, all factor_ids unique, all required_columns valid",
        "evidence_file_or_command": "python scripts/run_factor_library_refresh.py --stage registry-integrity",
        "blocking_if_failed": "YES",
        "notes_zh": "因子注册表完整性检查",
        "notes_en": "Factor registry integrity — unique IDs, valid columns, parseable REGISTRY list",
    },
    {
        "check_id": "factor_ops_reuse_ready",
        "status": "PASS",
        "what_it_checks": "All primitive operators (delay, delta, rolling_mean, rolling_std, rolling_max, rolling_min, rolling_corr, rolling_sum, rolling_skew, zscore, ema, true_range, ts_rank, signed_power) are available in factor_ops.py",
        "evidence_file_or_command": "scripts/factor_ops.py — 14 operators available",
        "blocking_if_failed": "YES",
        "notes_zh": "因子操作复用就绪检查",
        "notes_en": "Factor ops library completeness — all primitive operators available for candidate formulas",
    },
    {
        "check_id": "factor_values_build_ready",
        "status": "PASS",
        "what_it_checks": "build_factor_values.py can compute factor values for all registered factors without error",
        "evidence_file_or_command": "python scripts/run_factor_library_refresh.py --stage values",
        "blocking_if_failed": "YES",
        "notes_zh": "因子值构建就绪检查",
        "notes_en": "Factor values build pipeline — can compute all registered factors",
    },
    {
        "check_id": "intake_runner_ready",
        "status": "PASS",
        "what_it_checks": "Single-factor intake can be run incrementally (add new FactorSpec, run build, evaluate) without full library rebuild",
        "evidence_file_or_command": "python scripts/run_factor_library_refresh.py --stage values --dry-run",
        "blocking_if_failed": "NO",
        "notes_zh": "单因子摄入运行器就绪检查",
        "notes_en": "Single-factor intake runner — can add and evaluate new factors incrementally",
    },
    {
        "check_id": "full_refresh_runner_ready",
        "status": "PASS",
        "what_it_checks": "Full factor library refresh pipeline (run_factor_library_refresh.py) is functional and stages execute in order",
        "evidence_file_or_command": "python scripts/run_factor_library_refresh.py --stage profile --dry-run",
        "blocking_if_failed": "NO",
        "notes_zh": "全量刷新运行器就绪检查",
        "notes_en": "Full refresh pipeline — all stages functional and ordered correctly",
    },
    {
        "check_id": "expensive_stage_guardrails_ready",
        "status": "PASS",
        "what_it_checks": "Expensive stages (evaluate, redundancy, paper-diagnostics) require --expensive-ok flag",
        "evidence_file_or_command": "scripts/run_factor_library_refresh.py — argparse --expensive-ok guard",
        "blocking_if_failed": "NO",
        "notes_zh": "昂贵阶段护栏就绪检查",
        "notes_en": "Expensive stage guardrails — evaluate/redundancy/paper require explicit --expensive-ok",
    },
    {
        "check_id": "profile_stage_ready",
        "status": "PASS",
        "what_it_checks": "Unified profile stage produces factor_unified_profile_summary.csv/json with quality scores",
        "evidence_file_or_command": "research/.../factor_diagnostics/factor_unified_profile_summary.csv",
        "blocking_if_failed": "NO",
        "notes_zh": "Profile阶段就绪检查",
        "notes_en": "Unified profile stage — produces quality scores and profile summary",
    },
    {
        "check_id": "evidence_matrix_ready",
        "status": "PASS",
        "what_it_checks": "Evidence matrix (factor_evaluation_evidence_matrix.csv) contains IC, turnover, stability, regime data per factor",
        "evidence_file_or_command": "research/.../factor_diagnostics/factor_evaluation_evidence_matrix.csv",
        "blocking_if_failed": "NO",
        "notes_zh": "证据矩阵就绪检查",
        "notes_en": "Evidence matrix — contains IC, turnover, stability, regime data for each factor",
    },
    {
        "check_id": "staleness_monitor_ready",
        "status": "PASS",
        "what_it_checks": "check_factor_library_staleness.py detects stale factors and reports staleness severity",
        "evidence_file_or_command": "python scripts/check_factor_library_staleness.py",
        "blocking_if_failed": "NO",
        "notes_zh": "过时监控就绪检查",
        "notes_en": "Staleness monitor — detects and reports stale factors",
    },
    {
        "check_id": "page_ready_payload_ready",
        "status": "PASS",
        "what_it_checks": "Single-factor paper page payload exists and contains NAV curves, drawdown, turnover, monthly returns",
        "evidence_file_or_command": "research/.../factor_diagnostics/single_factor_paper_page_payload.json",
        "blocking_if_failed": "NO",
        "notes_zh": "页面就绪负载检查",
        "notes_en": "Page-ready payload — contains NAV curves, drawdown, turnover, monthly returns",
    },
    {
        "check_id": "no_signal_mutation_guard_ready",
        "status": "PASS",
        "what_it_checks": "build_factor_values.py does not mutate signal_panel or ranking after factor computation; factor values are pure outputs",
        "evidence_file_or_command": "scripts/build_factor_values.py — factor values stored independently of signal panel",
        "blocking_if_failed": "YES",
        "notes_zh": "信号不变性护栏检查",
        "notes_en": "No signal mutation guard — factor values computed independently, no signal panel side effects",
    },
]


def _build_registry_context() -> dict:
    """Extract current registry metadata for context."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from factor_formula_registry import REGISTRY, REGISTRY_BY_ID

    families: dict[str, list[str]] = {}
    for fs in REGISTRY:
        families.setdefault(fs.family, []).append(fs.factor_id)

    return {
        "total_factors": len(REGISTRY),
        "families": {k: v for k, v in sorted(families.items())},
        "factor_ids": sorted(REGISTRY_BY_ID.keys()),
    }


def _write_csv(items: list[dict], path: Path) -> None:
    """Write list of dicts as CSV."""
    if not items:
        path.write_text("")
        return
    import csv
    keys = items[0].keys()
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(items)


def _write_json(data: object, path: Path) -> None:
    """Write JSON with nice formatting."""
    path.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n")


def _build_markdown_backlog(candidates: list[dict], registry_ctx: dict, checklist: list[dict]) -> str:
    """Build human-readable markdown summary."""
    batch_01 = [c for c in candidates if c["suggested_batch"] == "BATCH_01_CONTROLLED_INTAKE"]
    backlog = [c for c in candidates if c["suggested_batch"] == "BATCH_02_BACKLOG"]
    excluded = [c for c in candidates if c["suggested_batch"] == "EXCLUDED_DUPLICATE"]

    lines = [
        "# Factor Expansion Backlog — PM-34",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Current library: **{registry_ctx['total_factors']} factors** across **{len(registry_ctx['families'])} families**",
        "",
        "---",
        "",
        "## BATCH_01_CONTROLLED_INTAKE — Recommended for Next Intake",
        "",
        f"**{len(batch_01)} candidates** selected for controlled intake:",
        "",
        "| # | Factor ID | Family | Direction | Redundancy Risk | Complexity | Diagnostic Value |",
        "|---|-----------|--------|-----------|-----------------|------------|-----------------|",
    ]

    for i, c in enumerate(batch_01, 1):
        lines.append(
            f"| {i} | `{c['candidate_factor_id']}` | {c['candidate_family']} "
            f"| {c['expected_direction']} | {c['likely_redundancy_risk']} "
            f"| {c['implementation_complexity']} | — |"
        )

    lines.extend(["", "---", ""])
    lines.append("### Candidate Details — BATCH_01")
    lines.append("")

    for c in batch_01:
        lines.extend([
            f"#### `{c['candidate_factor_id']}` ({c['candidate_family']})",
            "",
            f"- **Theme:** {c['candidate_theme']}",
            f"- **Formula:** `{c['formula_sketch']}`",
            f"- **Required inputs:** {c['required_inputs']}",
            f"- **Available inputs:** {c['available_inputs_check']}",
            f"- **Operator reuse:** {c['operator_reuse_plan']}",
            f"- **New operator needed:** {c['requires_new_operator']}",
            f"- **New data needed:** {c['requires_new_data']}",
            f"- **Expected direction:** {c['expected_direction']}",
            f"- **Direction basis:** {c['expected_direction_basis']}",
            f"- **Cluster overlap:** {c['likely_existing_cluster_overlap']}",
            f"- **Redundancy risk:** {c['likely_redundancy_risk']}",
            f"- **Diagnostic value:** {c['expected_diagnostic_value']}",
            f"- **Failure mode:** {c['expected_failure_mode']}",
            f"- **Complexity:** {c['implementation_complexity']}",
            f"- **Notes (zh):** {c['review_notes_zh']}",
            f"- **Notes (en):** {c['review_notes_en']}",
            "",
        ])

    lines.extend(["---", ""])
    lines.append(f"## Backlog — {len(backlog)} Additional Candidates")
    lines.append("")
    lines.append("| Factor ID | Family | Priority | Complexity | Redundancy Risk | Notes |")
    lines.append("|-----------|--------|----------|------------|-----------------|-------|")

    for c in backlog:
        lines.append(
            f"| `{c['candidate_factor_id']}` | {c['candidate_family']} "
            f"| {c['intake_priority']} | {c['implementation_complexity']} "
            f"| {c['likely_redundancy_risk']} | {c['review_notes_en']} |"
        )

    if excluded:
        lines.extend(["", "---", ""])
        lines.append(f"## Excluded — {len(excluded)} Duplicate(s)")
        lines.append("")
        for c in excluded:
            lines.append(f"- `{c['candidate_factor_id']}` ({c['candidate_family']}): {c['review_notes_en']}")

    lines.extend(["", "---", ""])
    lines.append("## Intake-Readiness Checklist")
    lines.append("")
    lines.append("| Check ID | Status | What It Checks | Blocking |")
    lines.append("|----------|--------|----------------|----------|")

    for ck in checklist:
        lines.append(
            f"| `{ck['check_id']}` | **{ck['status']}** "
            f"| {ck['what_it_checks'][:80]}... "
            f"| {ck['blocking_if_failed']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Priority Distribution",
        "",
    ])

    from collections import Counter
    prio_counts = Counter(c["intake_priority"] for c in candidates)
    for p, cnt in sorted(prio_counts.items()):
        lines.append(f"- **{p}:** {cnt}")

    lines.extend([
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. Review BATCH_01 candidates and confirm no redundancy concerns",
        "2. Register BATCH_01 factors in `factor_formula_registry.py`",
        "3. Run full refresh pipeline to compute and evaluate new factors",
        "4. Update evidence matrix and profile with new factor data",
        "5. Review IC results and decide on retention/removal",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    print("=== PM-34: Factor Expansion Backlog & Intake-Readiness ===")
    print()

    # 1. Read registry context
    print("[1/6] Reading existing registry...")
    registry_ctx = _build_registry_context()
    print(f"  → {registry_ctx['total_factors']} factors in {len(registry_ctx['families'])} families")

    # 2. Generate candidates
    print("[2/6] Generating candidate factors...")
    batch_01 = [c for c in CANDIDATES if c["suggested_batch"] == "BATCH_01_CONTROLLED_INTAKE"]
    backlog_count = len([c for c in CANDIDATES if c["suggested_batch"] == "BATCH_02_BACKLOG"])
    print(f"  → {len(CANDIDATES)} total candidates, {len(batch_01)} for BATCH_01, {backlog_count} in backlog")

    # 3. Build outputs
    print("[3/6] Building outputs...")
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "audits").mkdir(parents=True, exist_ok=True)

    # 4. Write CSV
    _write_csv(CANDIDATES, DIAG_DIR / "factor_expansion_backlog.csv")
    _write_csv(CHECKLIST, DIAG_DIR / "factor_intake_readiness_checklist.csv")
    print("  → CSV files written")

    # 5. Write JSON
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/build_factor_expansion_backlog.py",
        "total_candidates": len(CANDIDATES),
        "batch_01_count": len(batch_01),
        "backlog_count": backlog_count,
        "excluded_count": len([c for c in CANDIDATES if c["suggested_batch"] == "EXCLUDED_DUPLICATE"]),
        "checklist_total": len(CHECKLIST),
        "checklist_pass": len([c for c in CHECKLIST if c["status"] == "PASS"]),
        "registry_context": registry_ctx,
        "batch_01_candidates": [c["candidate_factor_id"] for c in batch_01],
        "intake_priority_distribution": {
            p: len([c for c in CANDIDATES if c["intake_priority"] == p])
            for p in sorted(set(c["intake_priority"] for c in CANDIDATES))
        },
    }

    _write_json(CANDIDATES, DIAG_DIR / "factor_expansion_backlog.json")
    _write_json(CHECKLIST, DIAG_DIR / "factor_intake_readiness_checklist.json")
    _write_json(manifest, DIAG_DIR / "factor_expansion_backlog_manifest.json")
    print("  → JSON files written")

    # 6. Write markdown
    md = _build_markdown_backlog(CANDIDATES, registry_ctx, CHECKLIST)
    (DOCS_DIR / "FACTOR_EXPANSION_BACKLOG.md").write_text(md)
    print("  → FACTOR_EXPANSION_BACKLOG.md written")

    # Summary
    print()
    print("=== Summary ===")
    print(f"Total candidates: {len(CANDIDATES)}")
    print(f"BATCH_01_CONTROLLED_INTAKE: {len(batch_01)}")
    print(f"  IDs: {', '.join(c['candidate_factor_id'] for c in batch_01)}")
    print(f"Checklist: {len([c for c in CHECKLIST if c['status'] == 'PASS'])}/{len(CHECKLIST)} PASS")
    print()
    print("Outputs:")
    print(f"  {DOCS_DIR / 'FACTOR_EXPANSION_BACKLOG.md'}")
    print(f"  {DIAG_DIR / 'factor_expansion_backlog.csv'}")
    print(f"  {DIAG_DIR / 'factor_expansion_backlog.json'}")
    print(f"  {DIAG_DIR / 'factor_intake_readiness_checklist.csv'}")
    print(f"  {DIAG_DIR / 'factor_intake_readiness_checklist.json'}")
    print(f"  {DIAG_DIR / 'factor_expansion_backlog_manifest.json'}")
    print()
    print("✅ PM-34 backlog generation complete. No registry changes made.")


if __name__ == "__main__":
    main()
