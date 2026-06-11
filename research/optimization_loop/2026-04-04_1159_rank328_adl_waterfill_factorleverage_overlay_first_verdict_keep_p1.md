# bot3 optimization loop — Rank 328 ADL / water-filling / factor-adjusted leverage overlay first verdict

- Time: 2026-04-04 11:59 UTC
- Target: `research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`
- Action: fresh intake first verdict for `water-filling leverage equalization × factor-adjusted deleveraging` shared risk overlay
- Verdict: `keep_P1`
- Assigned Rank: `328`

## Why this target clears fresh-intake admission
这条对象不该被伪装成方向型 raw alpha，但作为 **shared risk overlay / deleveraging policy** 已经把最关键的三层 desk shell 讲清：

1. **stress replay path 明确**：digest 没停留在“优化理论很好看”，而是已经给出 replay 入口——先把 desk 并行 sleeves 状态化（`notional / equity / gross leverage / beta / expected edge`），再在同一批 stress 窗口上对比 `pro-rata`、`exchange-style queue`、`gross leverage water-fill`、`factor-adjusted water-fill`；
2. **deployment shell 明确**：对象的定位不是独立策略，而是能挂在现有 `carry / breakout / mean reversion / maker / pairs` 之上的共享风控 overlay，用于极端行情里的统一 throttle / clipped deleveraging；
3. **factor-adjusted deleveraging 有独立存在感**：digest 已明确指出 cross-margin 下 `gross leverage` 会误伤真实 hedge，paper 给出的 single-factor `factor-adjusted leverage` clipped water-filling 足以形成第一版 desk experiment 假设，而不只是论文里的规范性叙事。

## Why it does not skip straight to P2
尽管对象已经形成可执行 shell，但它目前仍是 **overlay hypothesis**，不是已经完成诚实 replay 的 admission 级证据：

- digest 还没有给出我们自己 desk 状态簿上的实测 replay 结果；
- `tail shortfall / forced-close turnover / hedge false-positive cuts` 这几个 admission 指标仍停留在实验设计层；
- 因此现在最准确的位置是：**值得保留为 `P1 survivor`，但还没到直接升 `P2` 的地步。**

## Runtime conclusion
`research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md` 已完成 fresh intake first verdict：它不是独立 raw alpha，但已经形成一条清楚、可迁移的 `shared risk overlay / deleveraging` desk shell，足以以正式 `Rank 328` 进入 `keep_P1`，成为当前 survivor 主对象；暂不升 `P2`，因为 replay-based admission 证据还没真正落地。
