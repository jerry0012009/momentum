# 2026-04-08 19:26 UTC — normalized cluster deviation × next-bar snapback fresh intake 收口为 background / P0

## 本轮对象
- target: `research/quant_digests/2026-04-08_1358_normalized-cluster-deviation-snapback-alpha.md`
- 类型: fresh intake first verdict

## 执行结论
**结论：`normalized cluster deviation × next-bar snapback` 不进入 survivor，也不升 P2；本轮 fresh intake 直接收口为 `background / P0`。**

## 为什么不是 `keep_P1`
这条线虽然有一个清楚的 desk 读法——“把同簇资产先放到同一条归一化路径上，再抓单腿偏离后的 1~2 bar snapback”——但当前新增价值主要仍停留在**归一化实现与快收口持有期提示**，还没有形成一个独立于既有 family 的 queue-facing 主语。

### 1) 它没有脱离既有 cluster-relative MR 家族
仓库内已经存在更强、更宽的同家族宿主：
- `2026-04-01_1525_pca-cluster-deviation-statarb-alpha.md` 已把主语压成 **PCA residualized cluster deviation-to-mean**，核心也是“簇内相对偏离均值回归”；
- `2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md` 进一步把 cluster 结构 desk 化到 pair / cluster-neutral book 的 admission 层。

和这些已有宿主相比，`2026-04-08 13:58` 这条 digest 的新增点更像：
- 用更朴素的 `normalized path deviation` 替代 price-level spread；
- 明确提示 alpha half-life 很短，更像 `1 bar / 2 bar snapback`；
- 提醒不要把量纲不可比的币直接做 cluster mean。

这些都是真信息，但更像**同一家族的实现收紧/诚实边界修正**，而不是新的独立 raw alpha 主语。

### 2) 当前 portability probe 还不足以支撑独立前排身份
本地 probe 的 strongest claim 只有：
- `15m`、`24/48` 窗口、next-bar 口径大约 `+0.611 / +0.698 bps per trade`；
- 持有到 `4` 根后转负，说明更像快收口而不是可抱的 swing MR。

这能支持“**如果做，就做 very-short-horizon cluster snapback**”的 desk 方向判断，
但还不能回答它作为独立 intake 最关键的问题：
- 这种 edge 是否只是 generic cross-sectional reversal / cluster-neutral MR 在更短持有期下的自然表现；
- 成本后是否还有独立增量；
- cluster 定义变化后，新增贡献究竟来自 `normalized path`，还是只是已有 cluster MR 主体本来就存在。

也就是说，当前单一 decisive blocker 不是“完全没有信号”，而是**独立主语边界没有建立**：它更像旧 family 的一版 honest narrowing，而不是值得单独占 survivor 配额的新 rank 主体。

### 3) 它更适合作为已有家族的实现提示，而不是新 queue-facing 对象
这轮最值钱的一句话不是“发现了新 alpha”，而是：
> 对 cluster-relative mean reversion 家族，crypto 里不要直接拿原始价格做 cluster mean；若做短周期，优先把它读成 normalized path deviation 的 1~2 bar 快收口 snapback。

这句话应该服务于已有 cluster/pairs/stat-arb 宿主的 future refinement，
而不是再单独拉一条新的前排对象。

## 对 runtime 的直接影响
- `Fresh intake slot` 当前对象完成 first verdict，收口为 `background / P0`
- 不分配新 `Rank`（因为不是 `keep_P1` 或更高）
- 不占用 `Surviving candidate slot`
- `cycle_plan[1]` 标记为 `done`
- 前排 fresh intake 自然顺延到下一条 pending：`2026-04-08_1828_toxicflow-jump-continuation-alpha.md`

## 一句话 result
`normalized cluster deviation × next-bar snapback` 证明了“cluster-relative MR 在 crypto 更该做归一化路径 + 快收口”，但这仍是既有 cluster-deviation / cluster-neutral stat-arb family 的实现收紧，不足以形成新的独立 queue-facing raw alpha，因此本轮 first verdict 收口为 `background / P0`。
