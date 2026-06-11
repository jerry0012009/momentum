# Rank 220 / ETH whale balance imbalance alpha — survivor 唯一 follow-up 收口：keep_P1 后转 background

- 时间：2026-03-28 12:03 UTC
- 对象：`Rank 220 / ETH whale balance imbalance alpha`
- 本轮角色：survivor 唯一一次 follow-up
- 结论：`keep_P1 后转 background`

## 一句话结论
`Rank 220 / ETH whale balance imbalance alpha` 留下的确实还是一条像样的 ETH holder-imbalance 结构，但它在 survivor 阶段唯一该补的 decisive bridge —— **可公开重建、可短周期更新、且能诚实剔除交易所/桥/合约污染的大户 vs 小户 cohort proxy** —— 并不存在一个足够便宜、足够干净、足以直接做 admission 的公开桥，所以这轮不升 `P2`，按 `keep_P1 后转 background` 收口。

## 这轮实际补了什么
这次不再重复日频论文结论，而是直接问唯一该问的问题：

> 能不能用公开可得、无需重 vendor/标签工程的方式，把 `large-holder accumulation minus small-holder distribution` 迁到 ETH 的短周期事件漂移检验？

快速检查后，答案更接近：**没有便宜且诚实的桥**。

### 1) 原论文依赖的是 vendor 级 cohort 分层，不是顺手可得的公开分钟信号
原 intake 已经确认，Philadelphia Fed 这篇 paper 的核心证据来自 Coin Metrics 的 holder cohorts；而 cohort 本身不是“链上原始账本直接自带”的字段，而是建立在地址聚类、分层、标签清洗之上的 vendor 层构造。

### 2) 公开链上 API 能给原始地址/余额/持有人数据，但不能免费把它变成干净的 `large vs small` 交易信号
这轮补查里，公开可见的数据入口更多像 Bitquery 这类“原始/结构化链上数据 API”：能拿 token holders、balance history、transfers、traces，但**不等于**已经有可直接交易的 `large cohort` / `small cohort`。要把它变成论文里的对象，仍要自己处理：
- 地址聚类与实体归并
- 交易所、桥、合约金库、托管地址剔除
- cohort 边界定义随 ETH 价格变化的漂移
- 分钟级更新延迟与快照一致性

也就是说，公开数据层是有的，但 admission 需要的不是“有数据”，而是“有一条 cheap-but-decisive 的 clean proxy 桥”；这条桥并没有现成出现。

### 3) 市场上现成的 holder behavior 产品本身也说明这更像付费/重工程数据问题，不像 cheap follow-up
Glassnode 一类产品确实主打 on-chain participant behavior / clustering / capital-flow intelligence，但这恰恰说明：
- 真正可用的 holder cohort 不是免费公共面板顺手拿来就能跑；
- 它更像 vendor 数据产品或重标签工程资产；
- survivor 这一步若继续推进，本质上就会滑向“先做一套地址标签/聚类工程”，而不是一次便宜、决定性的前排 follow-up。

## 为什么这足以收口，而不是再留第二次 follow-up
按照 policy，survivor 只允许一次 cheap-but-decisive follow-up。对这条对象来说，唯一能决定它是否值得升 `P2` 的 blocker 不是“再补一点论文”“再换个 holding horizon”，而是：

> **有没有现实可得、低污染、足够及时的 cohort proxy，让这条线能进入 after-cost intraday admission？**

这轮已经把答案补清楚：
- **方向结构值得保留**；
- **但 bridge 不 cheap，也不 ready**；
- 因而它不适合继续占前排 survivor / P2 资源。

## 为什么不是直接 drop
因为它不是假的，只是当前不适合走默认前排链条。

保留价值仍然存在：
1. 它明确指出了一种可能真实存在的 ETH 知情资金结构：`large accumulation - small distribution`。
2. 如果未来明确获得可用的 cohort feed、可靠地址标签资产，或用户明确要求做链上重工程，这条线仍可 reopen。
3. 它也可作为未来别的 ETH 策略的 regime / veto / context card，而不一定非得先做独立 raw alpha admission。

## 正式 verdict
- `Rank 220 / ETH whale balance imbalance alpha`：**keep_P1 后转 background**
- 本轮不升 `P2`
- 本轮不进入 `Paper launch queue`

## 对 runtime 的直接影响
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 应归零
- `Background pool.latest_parked` 应更新为本条收口结论
- `cycle_plan` 第 1 项应写成 `done`

## 供后续 reopen 的唯一合法前提
只有在以下条件之一成立时，才值得把这条线从 background 重新拉回前排：
1. 获得可用的 holder cohort vendor feed；
2. 已有现成、可信的地址标签/聚类资产可直接复用；
3. 用户明确要求投入链上地址工程，接受这不再是 cheap follow-up。
