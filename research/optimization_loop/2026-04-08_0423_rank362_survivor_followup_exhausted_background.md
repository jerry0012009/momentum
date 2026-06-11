# Rank 362 — venue-freeze price gap × re-link close — survivor follow-up exhausted -> background

- Time: 2026-04-08 04:23 UTC
- Target: `Rank 362 / venue-freeze price gap × re-link close`
- Slot before action: `Surviving candidate`
- Decision: `keep_P1 exhausted -> background`

## Why this changed system belief
这轮唯一允许的 survivor follow-up，本来要回答的是：在现代 majors（Binance / OKX / Bybit）上，用 `quote_age / heartbeat_gap / stale_flag` 代理抓到的异常解除，是否仍能留下可复述的 **after-cost spread capture**，且 `orphan-leg` 不构成致命执行问题。

但当前 runtime 可用证据仍停留在：
- 论文样本主要是 `Bitfinex vs CoinMarketCap` 的中断统计；
- clean-room 定义已经把主语、异常代理、回补机制和最小执行壳压清；
- **没有新增的现代多-venue proxy quickcheck 结果** 能证明在今天的 majors 上，异常解除后的 edge 仍能穿过 fee / slippage / orphan-leg。

因此，这个对象已经完成了它在前排唯一值得做的那次便宜诚实检查：答案不是“证据还差一点所以继续挂前排”，而是 **当前没有足够证据把它升到 `P2`**。在 policy 下，survivor 预算到此用尽，最诚实的收口就是退回 `Background pool`，而不是继续把 outage 叙事留在 front slot 占资源。

## Why not `promote_P2`
要升到 `P2`，至少需要看到一条现代 majors 上可复述的最小 admission 迹象，例如：
1. `quote staleness / heartbeat gap` 代理事件在主流 venue 上确实能留下正的 `post-cost spread capture`；
2. `fill asymmetry / orphan-leg ratio` 没有把纸面 edge 吃掉；
3. edge 主要来自冻结失真，而不是健康 venue 的价格领先或深度塌陷。

这些关键 admission 证据目前都还没有，所以不能把它诚实地放进 `Active P2`。

## Runtime consequence
- `Surviving candidate slot` 释放；
- `Rank 362` 保留为一个定义清楚、但 admission 证据不足的事件驱动 cross-venue raw alpha 备忘，回到 `Background pool`；
- 前排可以合法切回下一条 fresh intake。

## Result sentence
`Rank 362` 的唯一 survivor follow-up 已诚实收口：当前只有 outage/staleness 叙事与 clean-room 壳，没有现代 majors 上能穿过 fee/slippage/orphan-leg 的 proxy-based after-cost 证据，因此本轮结论是 `keep_P1 exhausted -> background`，不升 `P2`。
