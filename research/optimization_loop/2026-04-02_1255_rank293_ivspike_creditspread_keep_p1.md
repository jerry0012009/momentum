# Rank 293 / near-expiry IV spike × 1m liquidity sweep → short vertical credit spread — fresh intake first verdict

- Time: 2026-04-02 12:55 UTC
- Executor: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.md`
- Object assigned: `Rank 293 / near-expiry IV spike × 1m liquidity sweep → short vertical credit spread`
- Verdict: `keep_P1`
- Level change: fresh intake -> surviving candidate slot

## Why this is not a straight P0
这条对象已经具备独立可审计的 raw-alpha 主语，不只是期权 UI / 执行脚本包装：
1. 主语明确：`near-expiry implied vol overshoot mean reversion + 0DTE theta decay`。
2. 触发与交易壳明确：`IV spike` + `1m liquidity sweep`，卖出同到期窄宽度 vertical credit spread。
3. entry / exit / sizing / max-hold / protection width 都已给出最小策略骨架。
4. 最小 clean-room path 明确：Delta Exchange 公共 `products / tickers / candles` 即可做 7~14 天链路记录与 paper validation。

## Why this is not promoted to P2 yet
当前证据还不足以把它直接抬成 `P2`：
1. 现阶段主证据仍以 repo source audit + 单次 live snapshot 为主，尚未给出连续样本下的净期望。
2. options 双腿成交质量、half-spread、taker fee、撤单重挂惩罚很可能决定这条 edge 是否还能存活；这不是边角问题，而是 admission 前的 decisive blocker。
3. 当前还没证明 `IV spike + sweep` 的触发在真实 near-expiry chain 上，扣掉双腿成本与滑点后仍有稳定正期望。

## System-changing conclusion
`Rank 293` 已通过 fresh intake 首判：它不是泛泛的 options automation 包装，而是一条具备独立 options raw-alpha 主语、明确 vertical spread 风险壳与公开数据 clean-room path 的候选，因此进入 `keep_P1`；但在连续链路样本证明成本后净期望之前，不升 `P2`。

## Next decisive follow-up for survivor slot
唯一值得做的 survivor follow-up 应收口到一个问题：

> 在 Delta 公共链路下，`IV spike + 1m sweep -> same-expiry short vertical credit spread` 扣除双腿 half-spread + taker fee + 现实成交惩罚后，是否仍有正的净期望？

若答案是否定或不清楚，则应诚实回 `background/P0`；若答案为肯定，再考虑升 `P2`。
