# Rank 196 intake首判：same-asset multi-quote spread mean reversion 保留为 P1

- 时间：2026-03-27 06:46 UTC
- 对象：`Rank 196 / same-asset multi-quote spread mean reversion with |z|-scaled sizing`
- 来源：`research/quant_digests/2026-03-27_0608_dynamic-scaling-quote-spread-meanreversion.md`
- 类型：fresh intake 首判

## 本轮只回答一个问题
`同币多报价 spread mean reversion + |z| 分层 sizing` 是否值得保留成一个单一 same-asset multi-quote spread raw alpha，而不是直接扩写成 RL / pair-trading 工程？

## 结论
值得保留，首判给 `keep_P1`，并分配正式 `Rank 196`。

## 为什么这次不是直接 park
1. **对象已经足够收缩**：可直接压缩为一个 clean-room 定义——在同一底层币种的多个稳定币/报价交易对之间，rolling spread z-score 极端偏离后，未来短窗内倾向向均值回归，且 `|z|` 更大时可用更高确定性仓位梯度。
2. **不是空泛论文转述**：digest 已附带最小快检，覆盖 `BTCUSDT/BTCUSDC`、`BTCUSDT/BTCFDUSD`、`ETHUSDT/ETHUSDC`、`ETHUSDT/ETHFDUSD` 的 45 天 `5m` 公共数据；在 `|z|>2` 事件上，1 小时 spread 回归幅度随 `|z|` 桶位升高而提升，简单 `1x/1.5x/2x` ladder 相比固定 `1x` 的 gross convergence-unit 提升约 `+31% ~ +38%`。
3. **desk 化后有明确最小下一步**：不需要先碰 RL；唯一 survivor follow-up 可以直接检查这个 raw alpha 在更诚实口径下是否还能站住，例如换到更细频率/净成本/成交方式后，固定 1x 与 ladder sizing 的增益是否仍成立。

## 仍然保留的诚实保留意见
- 当前证据仍偏 `gross / public klines / quote-spread` 口径，离真实可交易性还有距离；maker/taker、四腿成交、盘口深度、稳定币偏离风险都可能显著吃掉 edge。
- 因而本轮只配得上 `keep_P1`，还不够直接升 `P2`。

## 写回 runtime 的最小对象定义
`Rank 196 / same-asset multi-quote spread mean reversion with |z|-scaled sizing`：在同一底层币种的多报价交易对（优先稳定币报价）之间，若 rolling spread z-score 绝对值超过开仓阈值，则做均值回归；基础 raw alpha 不是 RL，而是“更极端的 spread 偏离对应更大的后续收敛幅度，因此仓位按 |z| 分层放大”。

## 本轮 verdict
- fresh intake：`keep_P1`
- 层级去向：进入 `Surviving candidate slot`
- 下一轮允许动作：仅 1 次最小 decisive follow-up；若该次检查后仍不足以升级，则按 policy 诚实收口，不继续拖成长研究。
