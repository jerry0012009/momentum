# Rank 231 / ETH whale balance imbalance — survivor 唯一 follow-up 收口：keep_P1 后转 background

- 时间：2026-03-29 06:48 UTC
- 对象：`Rank 231 / ETH whale balance imbalance`
- 本轮角色：survivor 唯一一次 follow-up
- 结论：`keep_P1 后转 background`

## 一句话结论
`Rank 231 / ETH whale balance imbalance` 留下的仍是一条像样的 ETH holder-imbalance 结构，但它在 survivor 阶段唯一该补的 decisive bridge —— **可公开重建、可短周期更新、且能诚实剔除交易所/桥/合约污染的大户 vs 小户 cohort proxy** —— 依然不存在一个足够便宜、足够干净、足以直接做 admission 的公开桥；因此这轮不升 `P2`，按 `keep_P1 后转 background` 收口。

## 这轮为什么足以改变系统认知
这轮不是重复讲日频论文结论，而是直接回答 survivor 唯一该回答的问题：

> 能不能用公开可得、无需先做一整套重标签工程的方式，把 `Δlarge - Δsmall` 迁到 ETH 的 `15m/30m/60m/240m` 事件漂移检验，并在现实成本/延迟口径下诚实进入 admission？

答案仍然是否定的，且是否定得足够具体：

1. **原论文依赖的是 vendor 级 cohort 分层，不是顺手可得的分钟信号**
   - Philadelphia Fed 这篇 paper 的核心证据来自 Coin Metrics 的 holder cohorts。
   - `large vs small` 不是链上账本原生字段，而是建立在地址聚类、分层、标签清洗上的 vendor 层构造。

2. **公开链上入口能给原始地址/余额/转账，但不能免费直接给出干净的交易型 cohort proxy**
   - 公开 API 或原始账本最多能拿到 holder / balance / transfer 层信息。
   - 但要把它变成论文里的对象，仍需自己处理：
     - 地址聚类与实体归并
     - 交易所、桥、合约金库、托管地址剔除
     - cohort 边界随 ETH 价格漂移的重定义
     - 分钟级更新延迟与快照一致性
   - 这意味着“有公开数据”不等于“有 cheap-but-decisive 的 admission bridge”。

3. **这条线当前真正卡住的是数据工程诚实度，不是 alpha 故事本身**
   - base alpha 结构依旧成立：`large accumulation - small distribution`。
   - 但若没有足够干净、足够及时的 cohort proxy，分钟级 drift 检验很容易变成假 admission：
     - 看似能做，实则标签污染严重；
     - 看似分钟化，实则观测时点已经过度滞后。

4. **因此这次 follow-up 的答案已经足够收口，而不是继续拖第二次 P1 follow-up**
   - policy 明确 survivor 只允许 1 次 cheap-but-decisive follow-up。
   - 对 Rank 231 来说，这个唯一 blocker 就是：
     - 有没有现实可得、低污染、足够及时的 cohort proxy，让它能进入 after-cost intraday admission。
   - 这轮已经把答案写清：**没有 ready 的便宜桥**。

## 为什么不是 promote_P2
因为当前并没有新的证据证明：
- `Δlarge - Δsmall` 的分钟化事件阈值在 `15m/30m/60m/240m` 上留下了方向一致、成本前后仍有意义的 ETH 漂移；
- 且该检验所依赖的 cohort 构造在延迟/标签污染上足够诚实。

没有这座桥，升 `P2` 只会把对象继续拖在 admission 阶段，而不是形成真正可判的前排候选。

## 为什么不是直接 drop
因为它不是伪 alpha，只是当前不适合继续占前排资源：

1. 它明确暴露了一种可能真实存在的 ETH 知情资金结构：`large accumulation - small distribution`。
2. 如果未来获得可用的 holder cohort vendor feed、可信地址标签资产，或用户明确要求投入链上地址工程，它仍可合法 reopen。
3. 它也适合保留为未来 ETH 策略的 regime / context / veto 素材，而不必现在硬做成独立 intraday admission。

## 正式 verdict
- `Rank 231 / ETH whale balance imbalance`：**keep_P1 后转 background**
- 本轮不升 `P2`
- 本轮不进入 `Paper launch queue`

## 对 runtime 的直接影响
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 应归零
- `Background pool.latest_parked` 应更新为本条收口结论
- `cycle_plan` 第 1 项应写成 `done`

## runtime sentence
> `Rank 231 / ETH whale balance imbalance` 的唯一 survivor follow-up 已收口：方向结构仍像一条值得记住的 ETH holder-imbalance alpha，但当前并不存在一个足够便宜、足够干净、足以把 `Δlarge - Δsmall` 诚实迁到 `15m/30m/60m/240m` admission 的公开 cohort proxy 桥；因此本轮不升 `P2`，按 `keep_P1 后转 background` 退出前排。
