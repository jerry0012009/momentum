# Rank 336 / liquidity-split last-day return cross-sectional — first verdict keep_P1
- 时间：2026-04-04 23:59 UTC
- 对象：`research/quant_digests/2026-04-04_2355_liquidity-split-lastday-return-xs-alpha.md`
- 执行动作：fresh intake first verdict
- 结论：`keep_P1`
- 正式 Rank：`Rank 336`

## 为什么这条线成立为 distinct raw alpha
这条 intake 不是把已有的 generic cross-sectional momentum / reversal 换个 liquidity 包装名词，而是把**同一个 `ret_24h` feature 的交易符号交给 liquidity split 决定**：

- 在 `liquid majors` 里，主命题是 **continuation**；
- 在 `illiquid tail` 里，论文/背景证据才更像 **reversal**；
- 对 desk 真正值得继续推进的，是前者这条 **可交易大币横截面 continuation 壳**，而不是把全市场混成一个统一方向。

这会改变系统认知，因为它给出的不是“再来一条 24h rank alpha”，而是：
1. `liquidity split definition` 已被提升为 alpha 定义的一部分，而不是回测后解释；
2. 可执行主战场明确落在 `liquid-major continuation`，不是默认追尾部 loser reversal；
3. 后续验证路径已经是 desk 可执行壳：`24h rank signal -> 5m/15m rebalance -> top/bottom bucket spread -> cost + beta neutral check`。

## 为什么现在先停在 P1，而不是直接升 P2
虽然 distinctness 和 executable shell 都够清楚，但 admission 还没完成，至少还缺最小实证来确认：
- `sign-router necessity` 在 perp / liquid-major 口径下是否真的稳定；
- `liquid-major continuation` 在 cost 后是否仍保留；
- `beta-neutral / market-leader projection` 会不会吃掉大部分表面收益。

所以 first verdict 合法收口为 `keep_P1`，进入 survivor 唯一一次 follow-up，而不是直接 admission。

## 下一次 survivor follow-up 应该盯什么
唯一高杠杆 follow-up 应该是：
- 只在 `liquid majors` 上做最小 desk 化检查；
- 验证 `24h rank continuation` 在 `5m/15m` 执行层、含成本与 BTC beta 控制后，是否仍然是可 admission 的主体；
- 若只剩论文解释层、或者 edge 主要来自 tail / beta 投影，就应诚实收口而不是拖长。

## 本轮 verdict
`Rank 336`：这条 `liquidity-split last-day return cross-sectional` 已经足以作为 distinct 的 `liquid-major continuation / illiquid-tail reversal` raw alpha 进入研究前排；first verdict 记为 `keep_P1`，并占用新的 survivor 槽位等待唯一一次 follow-up。
