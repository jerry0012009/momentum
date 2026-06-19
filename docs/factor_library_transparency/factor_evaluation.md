# 因子评价

> Phase 12D-H7 · 研究解释页

## 声明

本页展示"单因子层"的注册与评价状态。当前已完成的是 signal-level evaluation。factor-level IC 如未计算则标记 NOT_COMPUTED。本页不是实盘，不是交易建议。

## 概览

- 注册因子总数：53
- 进入当前信号：10（6 negative + 3 overlay + 1 cross-sectional）
- 候选因子：37
- 诊断探针：6（taker imbalance + funding rate，需 crypto-native cache）
- factor-level IC：NOT_COMPUTED
- signal-level RankIC：COMPUTED

## 数据来源

- 因子注册：`scripts/factor_formula_registry.py`（804 行，53 个 FactorSpec）
- 信号构建：`scripts/build_phase9b_signal_panel.py`（10 个因子进入当前信号）
- 信号评价：`scripts/evaluate_signals.py` + `src/momentum/signal_evaluation/`

## 信号使用

当前信号 `signal_v0_core_only__1h__original_no_guard` 使用 10 个因子：

### Negative list（6 个，信号中取负方向）
- vol_5h, vol_40h
- downside_vol_20h, vol_of_vol_20h
- rsi_7h, rsi_28h

### Overlay（4 个，横截面标准化后叠加）
- range_1h, range_4h, price_pos_24h
- xs_rank_vol

## 因子级 IC 状态

factor-level IC 尚未计算。当前只有 signal-level RankIC（即 10 个因子组合后的信号 vs forward return 的横截面排序相关性）。

如果需要评估单个因子的独立贡献，需要新增 factor-level IC evaluator。

## 状态枚举

| 状态 | 含义 |
|------|------|
| ACTIVE_IN_SIGNAL | 已进入当前 signal panel |
| CANDIDATE | 已注册、已计算 factor values，但未进入当前信号 |
| DIAGNOSTIC_PROBE | 需要额外数据源（crypto-native cache），当前仅作诊断探针 |

## 关联页面

- [代码结构](actual-script-map.html) — 因子库主链路、目录结构、脚本顺序
- [信号评价](signal-evaluation-summary.html) — 信号级 RankIC、Spread、Consistency
