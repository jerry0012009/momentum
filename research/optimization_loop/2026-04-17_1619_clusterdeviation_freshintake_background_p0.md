# bot3 optimization loop — cluster deviation fresh intake -> background/P0

- 时间：2026-04-17 16:19 UTC
- 执行动作：`cycle_plan` item1 / fresh intake first-verdict
- 对象：`research/quant_digests/2026-04-17_1438_clusterdeviation-pca-sponge-statarb-alpha.md`

## 结论
`market-mode removal + cluster admission + deviation fade` 在 9-coin / 15m portability 下虽保留 gross alpha（`gross Sharpe ≈ 2.32`），但统一 `t+2 + 4/6/8bps` 与 turnover cap 后 break-even cost 仅 `0.488bps`，`2bps` 起已转负；同时最小 honesty / execution realism 检查显示本次 probe 的 cluster signal 没有明显同窗 residual / fold 内泄露（PCA/graph/cluster 只在训练窗拟合，signal `zscore.shift(1)` 后才进测试），因此当前 blocker 不是“再补一轮可见性”，而是明确的成本-周转不可交易性，first verdict 直接收口 `background/P0`。

## 这一步看了什么
1. digest 主结论与 portability summary：
   - `gross Sharpe = 2.3226`
   - `avg_turnover_per_bar = 0.1941`
   - `active_bar_ratio = 0.3227`
   - `breakeven_cost_bps = 0.4883`
   - cost ladder: `2bps -> ann_return -1.15%, Sharpe -1.00`; `4bps -> ann_return -2.56%, Sharpe -2.21`; `8bps -> ann_return -5.40%`
2. 最小 honesty 检查：
   - probe 脚本先在每个 fold 的 train 窗口 `pca.fit(train)`、基于 `train_resid` 建 corr/kNN/SPONGE cluster；
   - 测试窗 signal 用 `context_resid` 计算，但 `compute_signals(..., lag=1)`，返回 `zscore.shift(1)`；
   - 因此下单使用的是上一 bar 已知 deviation z-score，不是当 bar 同窗 residual 直接入场。
3. admission 质量补看：20 个 folds 里有 `3` 个 fold 三个 cluster cohesion 全部 `<= 0`，其余多数 fold 也只是“剔除最差簇后继续交易”，说明 short-cycle majors 上 cluster admission 本身不稳，不能把 gross 边际当成可持续 pocket。

## 为什么不是 keep_P1
按本轮 success criterion，若 after-cost 只剩 optimistic gross 或 execution blocker 已清楚，就应直接 `background/P0`。这里已经满足：
- 统一成本口径下从 `2bps` 开始即费后为负；
- break-even 连 `1bps` 都不到，不存在值得留到 survivor 再补的单一 blocker；
- honesty 检查未发现新的“若修正即可翻正”的泄露型错误，反而坐实真正问题就是 turnover/cost。

## runtime 回写
- `Fresh intake slot.status` -> `done`
- `Fresh intake slot.current_target` 保持为本对象（本轮刚完成首判）
- `Fresh intake slot.latest_result` -> 本对象 first verdict = `background/P0`
- `Fresh intake slot.latest_result_record` -> 本日志
- `Background pool.latest_parked` 追加本对象
- `Background pool.latest_parked_record` 追加本日志
- `cycle_plan` item1 `result/status` 回填为已完成并收口 `background/P0`

## 本轮不做的事
- 不执行 item2 及之后 conditional fresh intake；本轮严格只做第一个 pending 小点。
