# Rank 408 survivor follow-up（BTC+BNB 成本稳定性）
- 时间：2026-04-15 02:40 UTC
- 执行对象：`Rank 408 / BB expansion breakout × pullback reversal continuation shell`
- cycle_plan 小点：#2（survivor 唯一 follow-up）

## 本轮执行
按 state 指定动作，仅对 `BTC+BNB` 资产域执行 4/6 bps 成本核验，并补最小 honesty 子检查（trigger->entry 是否严格 next-bar、无 delayed confirmation）。

数据源：
- 交易明细：`reports/artifacts/quant_digests/bbexpansion_pullback_probe_trades_2026-04-14.csv`

本轮产物：
- `reports/artifacts/optimization_loop/rank408_survivor_btc_bnb_cost46_summary_2026-04-15.csv`
- `reports/artifacts/optimization_loop/rank408_survivor_btc_bnb_weekly_netbps_2026-04-15.csv`
- `reports/artifacts/optimization_loop/rank408_survivor_btc_bnb_honesty_2026-04-15.csv`

## 结果
### 1) 成本后稳定性（BTC+BNB）
- 样本交易数：`77`
- `4 bps`：
  - `avg net bps = +5.538`
  - `positive week ratio = 0.625`（16 周中 10 周为正）
- `6 bps`：
  - `avg net bps = +3.538`
  - `positive week ratio = 0.625`（16 周中 10 周为正）

结论：在 survivor 约束资产域下，`positive week ratio` 与 `avg net bps` 在 4/6 bps 下均同时为正。

### 2) honesty / execution realism 最小子检查
- `min_entry_lag_min = 5.0`
- `max_entry_lag_min = 5.0`
- `strict_next_bar_ratio = 1.0`
- `non_next_bar_count = 0`

结论：触发到入场为严格 next-bar，无 delayed confirmation / 同 bar / 负延迟成交迹象。

## 本轮verdict（单步收口）
`Rank 408` survivor 唯一 follow-up 通过，满足 `promote_P2` 条件：
- 成本后周度与均值双指标同向为正；
- 最小 honesty 检查通过；
- 不存在单一 decisive execution blocker。

因此本轮将对象从 `Surviving candidate slot` 升级至 `Active P2 slot`，并用尽 survivor follow-up 预算。