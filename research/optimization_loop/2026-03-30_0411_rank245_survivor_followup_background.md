# Rank 245 / Donchian breakout × EMA HTF context gate survivor follow-up → background

- Time: 2026-03-30 04:11 UTC
- Target: `Rank 245 / Donchian breakout × EMA HTF context gate`
- Action: 唯一一次 survivor 最小诚实 A/B（`baseline confirmed breakout` vs `breakout + EMA HTF context-only gate`）
- Verdict: `不升 P2，回 background/P0`

## What was tested
本轮严格只做 policy 允许的那一刀：
- 固定同一批本地样本：`reports/artifacts/scout_tau_band_breakout_15m/cache/*__120d__15m.csv`
- 固定同一执行口径：`Donchian breakout confirmed-close / next-bar open`
- 固定同一成本：`6 bps / side`
- 固定同一 exit：沿用既有 `ATR 1.5x + reverse/flat`
- 只比较两个版本：
  1. `baseline_confirmed_breakout`：只保留 Donchian confirmed breakout，本体不加 EMA bias
  2. `ema_htf_context_gate`：EMA 只做 1h 闭合 bar 的 HTF 顺风 context gate，不再与 breakout 同层共触发

## Core result
结果非常直接：**把 EMA 从 co-trigger 降成 HTF context gate，并没有修复原 Rank 25 的时间塌陷；它只是在 aggregate 上留下几乎可忽略的微小抬升，但三桶结构完全不变。**

### Aggregate summary (BTC / ETH / SOL, 120d 15m cache)
- `baseline_confirmed_breakout`
  - `positive_assets = 3/3`
  - `mean_total_return = +16.6741%`
  - `median_total_return = +23.8216%`
  - `mean_max_drawdown = -13.5743%`
  - `mean_trades = 34.0`
- `ema_htf_context_gate`
  - `positive_assets = 3/3`
  - `mean_total_return = +16.8318%`
  - `median_total_return = +24.2898%`
  - `mean_max_drawdown = -13.4626%`
  - `mean_trades = 33.67`

这点差异太小，而且主要只是少掉极少数交易；它不足以说明“EMA 岗位重写”本身创造了新的、可升级的诚实优势。

### Time-bucket summary
两组结果的时间桶形状完全一样：
- `baseline_confirmed_breakout`
  - `bucket_1 mean_total_return = -11.0351%`
  - `bucket_2 mean_total_return = +33.0164%`
  - `bucket_3 mean_total_return = -12.0611%`
- `ema_htf_context_gate`
  - `bucket_1 mean_total_return = -11.0351%`
  - `bucket_2 mean_total_return = +33.1917%`
  - `bucket_3 mean_total_return = -12.0611%`

也就是说，这条 survivor 最关键要回答的问题——**能不能把 `bucket_1负 / bucket_2正 / bucket_3负` 的塌陷拉平**——答案是不能。EMA context-only gate 没有把前后段从负 pocket 拉回来，连 bucket pattern 都没有任何实质变化。

## Why this closes the survivor honestly
1. 这轮没有偷偷引入第二轴：没有加 regime、没有换 exit、没有加 strength、没有改 sizing。
2. 它直接比较了 `Donchian breakout` 单触发与 `Donchian breakout + EMA context gate` 的唯一差别。
3. 如果这条角色改写真的能救原对象，最起码应在时间桶结构上留下可见改善；现在没有。
4. 因为 survivor 预算只有这 1 次，所以本轮必须收口，不能再继续把 Rank 245 拖成新的开放式 P1/P2。

## Runtime implication
- `Rank 245` 的唯一 survivor follow-up 预算已用尽。
- 结论是：**不升 `P2`，回 `background/P0`。**
- 这也说明原 `Rank 25` 的主要问题并不只是“EMA 放错岗位”；至少在当前固定 breakout/成本/exit 口径下，EMA 退居 HTF context gate 不能单独修复它的时间不稳。

## Artifacts
- `reports/artifacts/rank245_donchian_ema_context_ab/aggregate_summary.csv`
- `reports/artifacts/rank245_donchian_ema_context_ab/asset_summary.csv`
- `reports/artifacts/rank245_donchian_ema_context_ab/time_bucket_aggregate.csv`
- `reports/artifacts/rank245_donchian_ema_context_ab/time_bucket_asset_summary.csv`
- `reports/artifacts/rank245_donchian_ema_context_ab/trades.csv`

## Result sentence
`Rank 245 / Donchian breakout × EMA HTF context gate` 的唯一 survivor A/B 已确认：把 EMA 从 co-trigger 降为 HTF context gate 并没有修复原 `Rank 25` 的 `bucket_1负 / bucket_2正 / bucket_3负` 时间塌陷，aggregate 仅有可忽略微升、三桶结构不变，因此 survivor 预算用尽后不升 `P2`，回 `background/P0`.
