# Rank 130 / cross-market leader impulse nonlinear gate · scorecard backfill

## 为什么这次补这一步
- 这不是重跑 clean replication，也不是改 verdict；只是把已经完成并被压回 `park` 的 `Rank 130`，按新的 **Scout Promotion Scorecard** 格式真实落一次。
- 这样可以验证：新格式不只适用于“看起来像赢家”的候选，也能诚实描述一个已经 `park` 的候选为什么该 `park`。

## 本次新增产物
- `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/promotion_scorecard.csv`
- `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/promotion_scorecard.json`
- `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/summary.json`（补写 `promotion_scorecard` 字段）
- `reports/site/factors/scout_rank130_crossmarket_leader_impulse_15m/report.html`（补 scorecard 区块）
- `reports/site/reading/repo_scout/rank130_crossmarket_leader_impulse_clean_replication.html`（补 scorecard 区块）

## Scorecard（0~3）
- `usefulness = 1/3`
  - `low_z_only` 在测试段相对 baseline 改善约 `+5.22 bps`，failure 改善约 `-7.75 pct`，但 retention 只剩 `18.89%`；而 `high_z_veto` 反而恶化约 `-1.86 bps`。
- `time_stability = 1/3`
  - `low_z_only` 在 train/test 都呈现“少亏一点”的方向，但都依赖大幅缩样本，不足以说明 shared gate 稳定成立。
- `cross_asset_stability = 0/3`
  - `BTC/SOL` 有局部 low-z uplift，`ETH` 反而更差；`high_z_veto` 在三资产上都不成形。
- `cost_trade_stability = 1/3`
  - `low_z_only` 在 `6/10/15bps` 下的 return delta 没有立刻塌掉，但经济改善仍建立在明显缩样本上。
- `deployability = 2/3`
  - 规则清楚、数据稳定、无明显 leakage；但当前还不值得进入 paper candidate。

**总分：`5/15`**

## Hard-fail flags
- `rule_unclear = false`
- `leakage_risk = false`
- `post_cost_collapse = false`
- `too_sparse = true`
- `single_pocket_dependency = true`

## 推荐动作
- `recommended_action = park`
- `why_now = 用一个已经完成 clean replication 且已被压回 park 的真实候选，验证新 scorecard 格式是否能稳定落地。`
- `main_weakness = 改善主要来自把样本压到 18.9%；真正更该值钱的 high_z_veto 没有站住，且跨资产不一致。`

## 结论
这张卡没有改变原 verdict，反而把原 verdict 讲得更清楚：
**`Rank 130` 不是“完全没信息”，而是“有一点点 low-z 线索，但不够 shared、不够稳、也不够值得继续占 fast lane”。**

## Commit hash
- 待本轮一并提交。
