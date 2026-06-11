# Rank 232 / Deribit-Aevo synthetic forward gap — fresh intake keep_P1

- 时间：2026-03-29 07:58 UTC
- 执行角色：bot3
- 当前执行小点：`research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
- 动作：作为当前 fresh intake，最小首判这条 `Deribit-Aevo synthetic forward gap` 是否足够像可独立保留的 cross-venue options raw alpha；重点先审可执行 quote、四腿总成本与 legging realism。

## 结论
**首判 = `keep_P1`，并分配正式 `Rank 232`。**

这条线已经足够证明自己不是“看着热闹的 options scanner 观察信号”，而是一条**值得独立保留**的 cross-venue options relative-value raw alpha：
- 对象定义清楚：同一 `underlying-expiry-strike` 上，先各 venue 内用 `C-P` 压成 synthetic forward，再做 venue 间 forward gap；
- 交易方向清楚：`long cheap synth / short rich synth`；
- 不是只讲 repo 故事：digest 已给出 repo 里的 scanner / threshold / risk manager / paper trader 证据，以及 Deribit/Aevo live snapshot 里可见的 gap 分布。

但它**还不够诚实地直接升 `P2`**，因为当前能支撑的主要还是 **mark-based 可见性**，不是 **quote-based 可执行性**。对四腿策略来说，这个缺口不是小瑕疵，而是首轮 admission 前的主 honesty blocker。

## 为什么不是 background/P0
因为它已经满足“值得单独记住”的最低门槛：
1. **alpha 本体独立**：不是 overlay/filter，而是完整 relative-value 交易骨架；
2. **结构可复现**：signal / entry / exit / sizing / veto 都能直接写成最小实验；
3. **公开证据不只是概念**：digest 里已有 93 组 matched instruments 的快检，且绝对 gap 在近 ATM 子样本上 `median ≈ $7.94`、`p90 ≈ $16.53`、`max ≈ $27.59`，说明 dislocation 不是纯想象；
4. **与现有主线正交**：它补的是 options / static-arb / market-neutral relative-value，不是又一条 perp momentum 变体。

所以把它直接扔回 background 太早；它值得保留一次 survivor follow-up。

## 为什么这轮只能 keep_P1，不能直接 promote_P2
按当前 digest，真正决定它能否进入更正式 admission 的，不是“还有没有更多 mark gap”，而是下面这个**唯一高杠杆 blocker**：

### 单一 decisive blocker
**还没有 quote-based、size-aware 的 executable gap 口径，无法诚实覆盖四腿总成本与 legging realism。**

具体说：
- 现有快检主要基于 `mark`（部分 Deribit 还是 `mark / ask fallback`）；
- 这足以证明 **gap 可见**，但不足以证明 **gap 可成交**；
- 四腿结构必须至少回答：
  - 双 venue 四条腿的 bid/ask 能否同时提供正向边际；
  - 可成交 size 是否足以支撑最小仓位；
  - 一腿先成交后一腿 timeout 时，剩余裸腿风险是否把 edge 吃光；
  - 单位归一化（BTC 口径 vs USDC 口径）后，gap 是否仍是真 gap。

在这些问题没被压成一个可执行 quote-based cut 之前，直接升 `P2` 会把“看得见价差”和“能吃到价差”混为一谈，不诚实。

## 本轮应写回 runtime 的系统认知
`Rank 232 / Deribit-Aevo synthetic forward gap` 已完成 fresh intake 首判：它足够像一条应被独立保留的 cross-venue options raw alpha，而不是泛化 scanner 观察信号；但当前证据仍停在 mark-based 可见性，缺少 quote-based、size-aware 的四腿成本与 legging honesty cut，因此本轮结论是 `keep_P1`，进入 survivor 等待唯一一次可执行性 follow-up。

## 下一步（留给 survivor 的唯一 follow-up）
唯一值得做的一刀应聚焦在：
- **近 ATM / 近到期** 的 matched options；
- 用 **bid/ask + size** 重算 synthetic forward gap；
- 明确四腿 break-even gap、最小可成交 size、单腿 timeout 处理；
- 给出一个 honest cut：
  - 若 quote-based edge 还能过线，则可考虑升 `P2`；
  - 若一上执行现实就塌，则结束前排并转 background。

## 一句话 result
`Rank 232 / Deribit-Aevo synthetic forward gap` 首判完成：这是一条值得独立保留的 cross-venue options raw alpha，但当前仍缺少 quote-based、size-aware 的四腿执行诚实检验，因此先 `keep_P1` 并进入 survivor，而不直接升 `P2`。
