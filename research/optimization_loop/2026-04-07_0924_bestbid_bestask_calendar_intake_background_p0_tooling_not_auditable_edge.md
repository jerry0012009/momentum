# 2026-04-07 09:24 UTC — fresh intake first verdict：bestBid > -bestAsk calendar-spread gap × shared-leg netting

- target: `research/quant_digests/2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md`
- action: 对 `mikehyland-quant/crypto-options-relative-value` 中 `bestBid > -bestAsk` 的 futures calendar-spread 可成交倒挂叙事做 fresh intake first verdict
- verdict: `background / P0`

## Why it does not earn keep_P1
1. **独立主语不够新**：这条线的核心仍是经典 `relative-value / calendar spread executable mispricing`，新意主要在“用图搜索求最优可成交 bid/ask 路径”和 `shared-leg netting` 工程实现，而不是提出一个独立于既有期限结构/跨 venue spread 家族的新 raw alpha 主语。
2. **公开证据停留在 source-asserted README 层**：当前 digest 主要依据 repo README 与作者自报指标；没有公开 trade blotter、bar-level 事件样本、逐腿成交与撤单统计、也没有独立 after-cost pocket 复核，无法证明 `bestBid > -bestAsk + hurdle` 在公开 crypto venue 上稳定保留净边。
3. **execution realism 仍是主 blocker**：这类机会最容易被时间戳错位、腿间部分成交、保证金切换、盘口 stale 和 fee tier 假设吃掉。现有公开材料虽然承认这些风险，但没有把它们压成可审计的现实成交留存证据。
4. **更像工具链/扫描框架，不是已压实的可迁移 alpha**：repo 同时覆盖多 venue、多合约路径与 options RV 语境；对我们当前短周期素材池而言，它更像值得记住的执行扫描思路，而不是已经足以占据 survivor 槽位的一条独立候选。

## System-changing result
`bestBid > -bestAsk calendar-spread gap × shared-leg netting` 当前更像 options RV 工具链里的可成交 spread 扫描叙事；公开材料尚未把独立 raw alpha 主语、公开 venue 的 after-cost pocket 与逐腿执行诚实性压成可审计证据，因此 fresh intake first verdict 直接收口为 `background / P0`。

## Files checked
- `research/quant_digests/2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md`
- `research/quant_digests/INDEX.md`
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`
