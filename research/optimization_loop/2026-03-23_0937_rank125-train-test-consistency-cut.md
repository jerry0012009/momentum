# 2026-03-23 09:37 UTC · Rank 125 / range location veto gate / train-test consistency cut

## 本轮一句话
按 `docs/TODO.md` 顶板，本轮走 **Scout / Run 1 / Rank 125**，目标是补最后这 1 刀真正会改 verdict 的最短 decisive cut：**它到底还能不能回到 `P2` 讨论**。结论：**不能**。本轮 authoritative call 固定为 **`P1 / keep_P1 / reserve冻结 / 不回 P2 讨论`**。

## 本轮路径判断
- `Paper launch queue`：`empty`
- `Interrupt`：未见 paper runner 的 `stale / error / refresh 失步 / ledger 异常 / red-watch`
- 因此本轮路径 = **`Scout`**

## 顶板认领动作
- 主点：`Rank 125 / range location veto gate`
- 紧邻子点：把结论写回 `TRADING DESK BOARD`，让下一轮默认资源位往后轮转到 `Rank 112`

## 为什么选这刀
`Rank 125` 之前已经做过：
1. clean replication；
2. cost / trade-retention stability。

但顶板当前还留着一个未封口的问题：
> 它到底只是旧 reserve，还是还能回到 `P2` 讨论？

最短、最诚实的收口方式不是再扩参数，也不是再补近义说明，而是直接问：
**train/test 两侧有没有一致的 shared uplift。**

如果连 train/test 一致性都没有，它就不该继续占 `Scout` 主位。

## 主点：Rank 125 train-test consistency cut
### 数据来源
复用既有 artifact：
- `reports/artifacts/scout_rank125_range_location_veto_15m/metrics_by_setup_cost_split.csv`
- 已冻结参数仍为：`n=8 / short_veto <= 0.10 / long_confirm >= 0.45`
- 成本继续看：`6 / 10 / 15 bps per side`

### 本轮判定规则
对每个 `setup × cost` 组合，只有同时满足以下条件，才算还能支持 shared/P2 讨论：
1. `train return delta > 0`
2. `test return delta > 0`
3. `train failure 不恶化`
4. `test failure 不恶化`

### 结果
新增文件：
- `reports/artifacts/scout_rank125_range_location_veto_15m/train_test_consistency_cut.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/train_test_consistency_cut.json`
- `reports/site/factors/scout_rank125_range_location_veto_15m/train_test_consistency_cut.html`

关键结果：
- `consistent_positive_count = 0 / 9`
- `shared_candidate = false`

逐项看：
1. `breakout_short`
   - test 侧确实改善：`return delta ≈ +9.5bps`，`failure improve ≈ +2.41pct`
   - 但 train 侧 `failure` 反而恶化：`-1.74pct`
   - 说明它更像 **test-side 局部 no-chase veto**，不是稳定 shared layer
2. `ema_psar_long`
   - train 侧基本 `0 增量`
   - test 侧才有 `+6.7bps` uplift
   - 说明它不是稳定成立的 shared confirm
3. `fib_retest_long`
   - 基本等于 `0 增量`
   - 没有提供额外决策价值

## 硬结论
## authoritative verdict
**`Rank 125 / range location veto gate = P1 / keep_P1 / reserve冻结 / 不回 P2 讨论`**

翻成人话：
- 它不是完全没料；
- 但这点料没有通过 train/test 一致性守门；
- 所以它最多只能留作 **evidence-bearing reserve**；
- 不能再以“也许还能升 `P2`”的名义继续占默认主资源位。

## 紧邻子点：board writeback
已同步更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
- `Active Scout` 里把 `Rank 125` 改成：
  - `P1 / keep_P1 / reserve冻结 / train-test consistency cut done / 不回 P2 讨论`
- `Next 3 bot3 runs` 改成：
  - `Run 1` 默认轮转给 `Rank 112`
  - `Run 2` 默认给 `Rank 111`
  - `Run 3` 才看 fresh intake / reserve 守门
- 最近关键 evidence 顶部新增本轮结论，防止后续循环又把 `Rank 125` 误当成待验证主位

## 简短 scorecard（Scout 要求）
- 主点（Rank 125 decisive cut）：**done**
- 紧邻子点（desk writeback / handoff）：**done**
- 是否升层：**no**
- 层级结论：**`keep_P1 / reserve冻结`**
- 下一默认轮转：**`Rank 112`**

## 验证
本轮实际执行：
```bash
python3 - <<'PY'
# 读取 metrics_by_setup_cost_split.csv，生成 train_test_consistency_cut.*
PY
```

生成结果摘要：
- `reports/artifacts/scout_rank125_range_location_veto_15m/train_test_consistency_cut.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/train_test_consistency_cut.json`
- `reports/site/factors/scout_rank125_range_location_veto_15m/train_test_consistency_cut.html`

## 风险 / 边界
- 这不是在证明 `Rank 125` 完全无效，而是在证明：
  **它当前不值得继续以 shared overlay / P2 候选的身份占主资源。**
- 若未来要 reopen，必须带来新的更强上下文（例如更窄 setup、明确单侧策略归属、或新的共享代理），而不是再重复这套 15m shared 叙事。

## 交付落点
- 日志：本文件
- 网页：`reports/site/factors/scout_rank125_range_location_veto_15m/train_test_consistency_cut.html`
- 顶板：`docs/TODO.md`

## Commit hash
- 未提交。
- 原因：仓库当前存在大量与本轮无关的脏文件；本轮只做了 `Rank 125` 相关 artifact 与 `TODO` 顶板 writeback。