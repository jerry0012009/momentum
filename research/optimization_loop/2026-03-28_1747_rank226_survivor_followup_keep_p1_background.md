# Rank 226 / IV quantile confirmation / veto：survivor follow-up 收口为 keep_P1 后转 background

- 时间：2026-03-28 17:47 UTC
- 对象：`Rank 226 / IV quantile confirmation / veto`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1 后转 background`

## 本轮执行的唯一小点
按 `BOT2_BOT3_STATE.md` 当前 `cycle_plan` 第 1 项，对 `Rank 226` 执行它作为当前唯一合法 `Surviving candidate` 的那一次 follow-up，目标是把这条 shared gate 诚实收口成明确出口结论，而不是继续停留在 paper/spec 层。

## 本轮看到的事实
1. `Rank 226` 的 intake 结论本身已经把对象边界说清：它不是独立 raw alpha，而是服务于 `5m/15m continuation / fade` 的 shared admission-veto gate。
2. 当前 repo 内，`Rank 226` 对应的 reader-facing 与 runtime 记录仍停留在：
   - paper 级论证；
   - desk-spec 级假设；
   - “下一步该做 BTC/ETH baseline A/B” 的研究指令。
3. 本轮未见与 `Rank 226` 对应的同口径 after-cost A/B artifact 被写回 runtime：没有一份可指向的 BTC/ETH 双资产、`baseline` vs `baseline + iv gate` 的结果记录，来证明 `iv_q × ivchg` 对现成 `5m/15m` continuation 或 fade baseline 留下了独立净增益。

## 出口判断
结论是：**不升 `P2`，按 survivor 预算收口为 `keep_P1 后转 background`。**

原因不是“这个想法被证伪”，而是：
- 这条线当前仍是一个**合理但未被最小实证闭环的 shared gate 设想**；
- survivor 的唯一一次预算，目标本来就是回答“有没有足够证据进入 `P2`”；
- 现在 runtime truth 仍不能回答“有”；
- 在没有新的同口径 A/B artifact 前，继续把它占在前排只会重复同一维度的 spec 讨论，不会改变层级判断。

## 会改变系统认知的话
`Rank 226 / IV quantile confirmation / veto` 到 survivor 收口时，仍没有形成证明其对现成 `5m/15m` continuation / fade baseline 留下 after-cost 独立净增益的 BTC/ETH 同口径 A/B artifact，因此这条 shared gate 本轮不升 `P2`，按预算收口为 `keep_P1 后转 background`。

## 为什么这一步足以收口
对 `Surviving candidate` 而言，policy 只允许 **1 次** 最小 decisive follow-up；它的目的不是无限补材料，而是判断要不要进入 `P2`。当前最关键的问题不是再解释论文，而是缺少能改变级别判断的最小实证闭环。既然这一步没有被补齐，就应诚实退出前排。

## 后续 reopen 条件
只有在出现新的、可指向的实证产物时，才值得 human 明确 reopen，例如：
- BTC / ETH 双资产；
- `5m/15m` 同口径；
- 至少一类现成 baseline（continuation 或 fade）；
- `baseline` vs `baseline + iv_q gate` vs `baseline + iv_q + ivchg`；
- 成本后 trade count / markout / tail loss / turnover 结果明确写回 artifact 与 runtime。
