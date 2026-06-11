# Rank 183 / cbeth-eth-rolling-fair-basis-mr — fresh intake keep_P1
- 时间：2026-03-26 09:27 UTC
- 对象：`CBETH-ETH rolling fair-basis mean reversion`
- 来源：`research/quant_digests/2026-03-26_0850_cbeth-eth-rolling-fair-basis-mr.md`
- 本轮角色：bot3 对 fresh intake 做最小首判（只收口这一个对象）

## 结论
**首判 = `keep_P1`，并分配正式 `Rank 183`。**

更直白地说：当前值得保留、进入 survivor 的，不是“LSD basis 解释框架”这种泛叙事，而是 **`CBETH-ETH` 围绕 slow rolling fair basis 的短周期 relative-value mean reversion** 这条 raw alpha 本体；它已经显示出足够强的前排保留价值，但还没诚实到可以直接升 `P2`。

## 为什么这轮不是直接 park
这次 digest 至少给了 3 条会改变系统认知的正面信息：
1. **锚点定义是对的。** 论文与快检共同支持“不能拿 1:1 peg 当锚，而应拿 slow-moving fair basis 当锚”，对象边界清晰，不是概念漂移。
2. **最小 admission proxy 有明显正 pocket。** Coinbase 公共 `15m/5m` proxy 在 rolling-z 口径下，不只是偶发正值；尤其 `15m` 档出现了反复可收的残差形态，说明这条线不只是慢 carry。
3. **落地路径具体。** `CBETH spot + ETH perp`、entry/exit、timeout、成本口径、funding、深度过滤都能写成下一轮 survivor follow-up，不像只剩解释、没有可执行 spec 的文献型条目。

## 为什么这轮也还不能直接升 P2
当前证据还停留在 **close-to-close proxy + 论文旁证**，还缺一轮真正 decisive 的 survivor follow-up：
- 需要把对冲腿切到 **真实可交易口径**（`CBETH spot + ETH perp`）；
- 需要把 **pair round-trip cost ladder** 明确跑到至少 `10/20/30/40 bps`；
- 需要把 **funding + 残余 fair-basis drift + CBETH 深度/冲击** 显式带进来；
- 若这些现实化约束一加，edge 只剩“论文上看着美”，那它就该诚实停在背景池，而不是假装已经够格进入 P2。

## 本轮单一收口 verdict
`Rank 183 / cbeth-eth-rolling-fair-basis-mr` 首判为 `keep_P1`：当前应把它保留为 survivor，并把那唯一一次 follow-up 预算留给 **真实可交易口径下的 cost/funding/depth honesty gate**，而不是继续泛讲 liquid staking basis 故事。

## 对 runtime 的直接影响
- 分配新正式身份：`Rank 183`
- `Fresh intake slot`：本轮 intake 已收口
- `Surviving candidate slot`：切换为 `Rank 183`，并保留 **1 次** survivor follow-up 预算
- 不改动其他前排对象与 policy
