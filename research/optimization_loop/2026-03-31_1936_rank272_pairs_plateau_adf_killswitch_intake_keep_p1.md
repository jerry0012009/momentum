# Rank 272 — pairs plateau + ADF kill-switch fresh intake (`keep_P1`)

- Time: 2026-03-31 19:36 UTC
- Source digest: `research/quant_digests/2026-03-31_1846_pairs-plateau-adf-killswitch-cost-cliff.md`
- Slot acted on: `cycle_plan` item 2 (`fresh intake`)
- New rank assigned: `Rank 272`
- Verdict: `keep_P1` (enter survivor slot, no direct `P2` promotion)

## What changed system belief

`plateau-first parameter selection + in-trade ADF kill-switch pairs` 可以诚实收口为一个可审计的 `beta-hedged cointegration spread mean reversion` raw alpha skeleton；真正值得保留的不是 repo 里的单点 best-cell，而是 `plateau-share` 选参、持仓中 `ADF` 失效 kill-switch、以及显式成本生存线三件事的组合。但现有证据仍主要来自 repo audit 加上 `ETH/LINK` 单对 public-data proxy：`10bps` spread-package round-trip 成本下仍有一片正 pocket，`20bps` 下则基本全灭，因此它还不够直升 `P2`。

## Why this is not `P0`

- digest 已把对象清楚收口成独立 raw alpha，而不只是“又一个泛泛 pairs repo”；
- `plateau-first` 回答的是参数面是否真有稳态 pocket，能直接约束 overfit；
- `in-trade ADF kill-switch` 回答的是 pair 关系断裂时如何诚实退出，属于可交易化组件；
- 成本 cliff 结论虽然偏严厉，但没有把对象打成“概念不存在”，而是把它收窄成“只有低成本/高流动候选对才可能存活”的研究方向。

## Why this is not yet `P2`

当前还缺三个 admission 级别的关键补件：

1. **多 pair**：不能只靠 `ETH/LINK` 一对 proxy；
2. **多 venue / 现实执行**：需要把 Binance / Bybit 或至少多个高流动 perp pair 放到统一 clean-room 口径里；
3. **分腿成本 / kill-switch 真实增益**：需要把 `taker/taker`、`maker/taker`、funding/fee tier、以及是否真的减少 tail loss 分开验证。

在这些没补齐前，把它升到 `P2` 会过早把单对 proxy pocket 当成可迁移 admission 结论。

## Single decisive follow-up to queue next

`Rank 272` 进入 survivor 槽后，唯一值得做的一次 follow-up 应该是：

- 选一组同 risk-cluster、高流动 perp 候选对；
- 用统一 rolling clean-room replication 输出 `good_cases / plateau_n / plateau_share`；
- 同时比较 `no kill-switch` vs `ADF kill-switch + half-life timeout`；
- 在 `10/15/20bps` 或分腿成本口径下直接判断是否仍存在成本后存活 pocket。

若该 follow-up 证明多 pair 下仍有成本后 plateau pocket，再升 `P2`；否则应在 survivor 预算用尽后回 `background/P0`。
