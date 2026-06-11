# Rank 244 / direction-aware loss × thresholded BTC directional state machine — survivor follow-up closed to background

- Time: 2026-03-30 00:29 UTC
- Current cycle item: `Rank 244 / direction-aware loss × thresholded BTC directional state machine`
- Source digest: `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
- Input state: `Surviving candidate slot`, `followup_budget_remaining = 1`
- Verdict: `survivor follow-up used; do not promote to P2; move to background/P0`

## 本轮只回答的问题
在**同一 BTC 数据、同一特征、同一状态机、同一成本口径**下，`direction-aware loss` 相对 `MSE` 是否真的留下独立的成本后增量，而不是优势主要来自 `threshold abstain` 的稀疏交易？

## 最小诚实代理实验
因为本轮目标只是 survivor 的唯一一次 cheap decisive follow-up，所以不复现整套 Informer，而是做最小代理 A/B：

- 数据：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/candidate_5y_cache/BTCUSDT__1825d__15m.csv`
- 频率：`BTCUSDT 15m`
- 样本：约 5 年；walk-forward 为 `365d train / 30d test`，共 `49` 个测试折
- 特征：相同的一组价格/波动/成交量/时间特征（lag return、rolling vol、momentum、volume ratio、range/body、hour/dow）
- 模型：
  1. `MSE proxy`：普通 ridge regression
  2. `direction-aware proxy`：同一模型、同一特征，但对大振幅样本加更高 sample weight，逼近“别把尾部样本全缩回 0”这条论文主张
- 状态机：同一 `long / short / flat` 阈值 admission
- 成本：保守 `6 bps/side`（状态切换即付成本）
- 产物目录：`reports/artifacts/rank244_survivor_followup_20260330/`

## 关键结果
### 1) 在固定 5 bps admission threshold 下，`direction-aware` 没有留下独立增量，反而更差
- `MSE proxy`
  - `active_share = 0.95%`
  - `trades = 2102`
  - `gross_bps_per_bar = -0.013`
  - `net_bps_per_bar = -0.105`
  - `avg_trade_bps = -7.01`
- `direction-aware proxy`
  - `active_share = 15.80%`
  - `trades = 27420`
  - `gross_bps_per_bar = -0.045`
  - `net_bps_per_bar = -1.261`
  - `avg_trade_bps = -6.44`

也就是说，在**阈值完全固定**时，所谓 direction-aware 改进并没有留下“同等状态机下更好的成本后 edge”；它主要做的是把预测幅度放大，导致交易显著变多，但方向质量没有同步变好。

### 2) `direction-aware` 的预测确实更不容易缩回 0，但这是“更大声”，不是“更准”
- 平均折内 `|prediction|`
  - `MSE`: `9.17e-05`
  - `direction-aware`: `2.91e-04`
- 平均折内相关性
  - `MSE`: `+0.0041`
  - `direction-aware`: `-0.0053`
- 平均折内 RMSE
  - `MSE`: `0.002629`
  - `direction-aware`: `0.002659`

结论很直白：direction-aware 代理确实让预测分布尾部更厚，但**没有把真实下一 bar 回报的相关性一起抬上来**。这意味着“没缩到 0”本身不等于“留下可交易 edge”。

### 3) 即使允许各自挑一个更适合自己的阈值，结论仍然不变
在要求 `active_share >= 2%` 的前提下：
- `direction-aware` 的最好阈值约在 `10 bps`，但仍只有 `net_bps_per_bar = -0.232`
- `MSE` 的最好阈值约在 `2.5 bps`，也仍是 `net_bps_per_bar = -0.541`

两边都没过线；而且 `direction-aware` 没有展示出“固定同一阈值时独立胜过 MSE、或在自己最优阈值下成本后转正”的 survivor 级证据。

## 本轮系统认知变化
> `Rank 244 / direction-aware loss × thresholded BTC directional state machine` 的唯一 survivor follow-up 已完成：在本地 BTC 15m walk-forward、固定同一特征与 long/short/flat 阈值状态机、保守 friction 下，direction-aware loss 代理没有留下独立于 `threshold abstain` 的成本后增量；它主要把预测幅度放大并显著增加交易，但方向质量未同步改善，因此 survivor 预算用尽后不升 `P2`，回 `background/P0`。

## 为什么不是 keep_P1 或 promote_P2
- 这一步已经直接回答了 survivor 最核心的问题：**loss 本身有没有独立价值**。
- 当前证据不支持“有”。
- 再继续拖一轮只会变成重复补同一维度，不符合 policy 对 survivor 只给一次 follow-up 的硬约束。

因此本轮应诚实收口为：
- `status = done`
- `result = Rank 244 完成唯一 survivor follow-up；direction-aware loss 独立增量未成立，回 background/P0`

## 产物
- `reports/artifacts/rank244_survivor_followup_20260330/threshold_summary.csv`
- `reports/artifacts/rank244_survivor_followup_20260330/walkforward_fold_metrics.csv`
- `reports/artifacts/rank244_survivor_followup_20260330/prediction_panel.csv`
- `reports/artifacts/rank244_survivor_followup_20260330/best_threshold_by_model.csv`
- `reports/artifacts/rank244_survivor_followup_20260330/summary.json`
