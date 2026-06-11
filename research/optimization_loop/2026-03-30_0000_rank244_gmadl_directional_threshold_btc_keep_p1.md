# Rank 244 / direction-aware loss × thresholded BTC directional state machine — fresh intake keep_P1

- Time: 2026-03-30 00:00 UTC
- Current cycle item: `direction-aware loss × thresholded long/short state machine on BTC`
- Source digest: `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
- Assigned Rank: `Rank 244`
- Verdict: `keep_P1`

## 本轮只回答的问题
`research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md` 里的对象，是否已经足够独立到值得转成新的 queue-facing 对象？

要求是主语必须锁死为：

> `direction-aware loss × thresholded long/short/flat state machine` 这条 BTC 单币短窗 directional raw alpha

而不是泛 `Informer 模型复现`、泛 `BTC 预测仓`、或“复杂模型打败技术指标”的论文摘要。

## 结论
结论是：**值得，且应正式写成 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`。**

本轮 fresh intake verdict 为 **`keep_P1`**，原因不是“论文 headline 很好看”，而是这条对象已经具备：

1. **清楚主语**：它的最小对象不是 Informer 架构，而是
   - `next-bar return forecast`
   - `direction-aware loss`
   - `thresholded long / short / flat admission`
   - `cost-aware abstain`
   这四件东西组成的单币 directional raw alpha。
2. **可独立复现**：同一份 digest 已把最小实验拆成可复现的 desk 版 spec：固定特征集、固定状态机、只改 `MSE vs direction-aware loss`，再做 `loss vs threshold abstain` 拆分。
3. **可单轮证伪**：它不是无限开放的“再调更大模型”，而是能被非常明确地否掉：如果优势只来自阈值稀疏交易、而不是 direction-aware loss 本身，或者一上保守 friction 就失效，那么主语就会被收窄甚至打回背景。
4. **不等同于现有旧对象**：repo 里虽然已有 `Rank 211 / CME BTC futures sign classifier + high-threshold abstain` 这类单币 directional 尝试，但那条线的核心主语是 **sign classifier 在 futures microstructure 上是否站得住**；当前对象的核心主语是 **同一状态机下，direction-aware loss 是否能把预测分布从“缩到 0”拉成可过成本阈值的尾部分布**。两者不重复。

## 为什么它不是泛 Informer 论文复述
如果把它写成“Informer 在 BTC 高频上优于 MACD/RSI”，那只是论文标题党，不能进前排。

但 digest 已经把真正值得保留的本体剥离出来了：

- 论文最强信息不是“Transformer 更强”；
- 而是 **`RMSE -> 预测缩到 0 -> 过不了成本门槛`**；
- 与之相对，**direction-aware loss + thresholded abstain** 这条链路可能才是高频存活的核心。

也就是说，当前保留的对象不是模型名，而是一个清楚可测的 **训练目标 × admission rule** 假设。

## 为什么现在只给 keep_P1，不直接升 P2
虽然对象边界已经清楚，但它目前仍停在 paper/repo/digest 级证据，还没做本地最小 replication。

本轮还没有回答的 decisive follow-up 是：

> 在同一份 BTC 数据、同一特征、同一状态机、同一成本口径下，`direction-aware loss` 相对 `MSE` 是否真的留下了独立的成本后增量，而不是只靠阈值 abstain 假装变好？

在这一步没做之前，直接升 `P2` 会把“可复现对象”误写成“已初步通过 admission 的对象”，不诚实。

因此当前最合适的位置是：

- **fresh intake 成立**
- **正式分配 `Rank 244`**
- **结论 = `keep_P1`**
- **进入 survivor，等待唯一一次最小 decisive follow-up**

## 与现有对象的 distinctness
### 相对 `Rank 211 / CME BTC futures sign classifier + high-threshold abstain`
- `Rank 211`：主语是 `next-bar sign classifier + high-threshold abstain`，更偏 **分类器 + microstructure threshold**。
- `Rank 244`：主语是 `direction-aware loss × thresholded directional state machine`，更偏 **损失函数是否改变可交易预测分布**。

前者在问“分类预测能否留下可交易 sign edge”；
后者在问“同一 directional 任务里，loss 设计是否才是高频穿成本的关键增量”。

### 相对一般 BTC directional / timing family
当前 repo 里当然已经有很多 BTC 单币方向类对象，但这条线仍然独立，因为它的核心 A/B 是：

- `MSE vs direction-aware loss`
- `loss effect vs threshold abstain effect`

这是一条非常具体的实验主语，不是泛 directional family 的换壳。

## 本轮应写回 runtime 的系统认知变化
> `direction-aware loss × thresholded long/short/flat state machine` 已足够独立成 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`：它不是泛 `Informer` 论文复述，而是一条可直接做 `MSE vs direction-aware loss` 与 `loss vs threshold abstain` 拆分对照的 BTC 单币短窗 directional raw alpha，因此本轮 fresh intake 记为 `keep_P1`，进入 survivor，等待唯一一次最小 replication follow-up。

## Runtime updates intended
1. `Fresh intake slot` 切换到 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`
2. `Surviving candidate slot` 切换到 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`
3. `followup_budget_remaining = 1`
4. `cycle_plan` 第 2 项写成 `done`

## Reader-facing note
本轮 reader-facing 变化是：又新增了一条正式前排对象，但还没有进入 P2。真正下一刀要补的是最小 replication：在同一状态机和成本口径下，把 `direction-aware loss` 和 `MSE` 分开诚实对照。 
