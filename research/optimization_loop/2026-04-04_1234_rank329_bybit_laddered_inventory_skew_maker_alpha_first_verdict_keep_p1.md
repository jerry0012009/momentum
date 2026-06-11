# Rank 329 — Bybit laddered inventory skew × maker execution fresh intake first verdict: keep_P1

- Time: 2026-04-04 12:34 UTC
- Target: `research/quant_digests/2026-04-04_1016_bybit-laddered-inventory-skew-maker-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1` → assign formal `Rank 329` and move into survivor path

## Why it stays alive

这条对象不是“靠最优 maker 假设包装出来的纯 execution demo”那么简单。repo 已经把一条最小可执行的 maker raw alpha 壳拆成了清楚的几层：

1. `inventory skew signal`：净仓偏向一边时收缩偏仓侧、放大去库存侧，不是无脑双边等量挂单。
2. `laddered quoting logic`：围绕 spread floor 做双边多层报价，形成明确的 quote refresh / cancel / TP / gross cap 规则。
3. `maker-only economics`：收益口径本身就围绕 spread capture、fee、funding、stale quote/adverse selection 风险展开，而不是先假定方向优势再顺便用 maker 下单。

因此它已经满足 fresh intake 的最低门槛：

> 这是一个独立可迁移的 maker / liquidity-provision raw alpha 家族壳，而不只是 README 级 execution 样板。

## Why it does not jump to P2 yet

当前证据还没有把最关键的存活问题真正做实：

- `queue position / fill proxy / stale-quote penalty` 仍主要停留在研究口径，没有变成我们自己 desk 上的最小 replay 规范；
- 薄 spread floor（如 `0.2bps`）在保守摩擦下是否还能留下净 capture，还没有形成本地 survival line；
- 还缺一轮诚实 follow-up，把 `BTC/ETH/SUI` 这类 symbol 分层、fill haircut、inventory half-life、adverse-selection 损失收敛成明确 admission 路径。

所以当前最准确的定位是：

> `Rank 329` 值得保留到 `P1 survivor`，但还不能直接宣称已达到 `P2 admission`。

## System-changing result sentence

`Rank 329` 的 fresh intake first verdict 已完成：这条 `Bybit laddered inventory skew × maker execution` 已经把 `inventory skew signal / laddered quoting logic / maker-only economics` 分账成一条独立的 maker raw alpha 壳，因此分配正式 `Rank 329` 并进入 `keep_P1` survivor；但在 `fill realism / stale-quote survival line` 还没被我们自己的 replay 口径做实前，暂不升 `P2`。
