# Rank intake log — asymmetric shock horizon router -> background / P0

- Time: 2026-04-08 20:49 UTC
- Target: `research/quant_digests/2026-04-08_1729_asymmetric-shock-horizon-router-alpha.md`
- Slot: `Fresh intake`
- Action: first verdict
- Verdict: `background / P0`

## What changed system truth
`shock-sign × fast-bounce / slow-follow router` 说明负冲击短促回补、正冲击慢一点才兑现的 horizon asymmetry 可能存在，但当前新增信息主要仍是“按 sign/horizon 区分既有 shock fade / continuation family 的 admission discipline”，还不足以形成新的独立 queue-facing raw alpha。

## Why not keep_P1
1. **独立主语不够硬**：当前最强结论是 `5m downside fade` 与 `15m delayed upside follow` 要分开看，本质更像对既有 single-asset shock family 的 router 细化，而不是一个新的统一 alpha 主语。
2. **论文与可交易频率错层明显**：论文证据是周频非对称与跨币相关；落到 `5m/15m` 时已经被作者自己降成 portability probe，faithful transfer 还没建立。
3. **执行现实感还不够**：digest 里已经承认 `15m` 正冲击 next-bar 先回撤，真正 verdict 会显著依赖 `close-entry vs pullback-entry`；在这件事没补齐前，不适合升成独立前排对象。
4. **与现有家族重叠高**：仓库里已经有 `common-shock / peer-shock / imbalance / jump continuation` 等多条 shock-family intake；这条线当前更像 family 内的 sign-router 经验，而不是独立新书。

## Minimal evidence used
- 目标 digest 的论文摘要与本地 Binance USDⓈ-M `5m/15m` probe 结论。
- 现有 digest 池的 family overlap 快速核对：已存在 `common shock`、`peer shock`、`imbalance/OFI continuation`、`jump continuation` 等相邻主语。

## Runtime writeback
- `Fresh intake slot` 更新为本对象的 `background / P0` 收口结果。
- `Background pool.latest_parked` 更新为本对象。
- `cycle_plan` 第 3 项状态更新为 `done`。

## Reader-facing implication
后续若要重开，这条线更合适的姿势不是“继续证明 shock asymmetry 存在”，而是只挑一个单独子书重开：
- 要么只做 `5m downside snapback`；
- 要么只做 `15m positive-shock delayed follow`，并把 `pullback-entry vs close-entry` 作为唯一 decisive blocker。
