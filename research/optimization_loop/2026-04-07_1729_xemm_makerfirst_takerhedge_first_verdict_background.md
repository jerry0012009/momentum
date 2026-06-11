# Rank intake verdict — XEMM maker-first / taker-hedge shell goes to background

- Time: 2026-04-07 17:29 UTC
- Target: `research/quant_digests/2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md`
- Slot: `Fresh intake`
- Action: first verdict
- Status: done

## What changed
`maker-first cross-venue quote gap × taker-hedge profitability buffer` 本轮不成立为新的前排 raw alpha：它描述的是成熟 `same-underlier cross-venue gap / cross-exchange market making` 家族的执行工程壳，把 `min_profitability / slippage / balance / taker hedge` 约束写得更完整，但没有压出独立于既有 cross-venue spread capture 叙事的新 alpha 主语，因此直接记为 `background / P0`，不进入 survivor。

## Why
- 可交易主语仍是老问题：同一标的跨 venue 报价错位，maker 先挂、taker 对冲。
- Hummingbot 的价值主要在工程落地：报价反推、撤单节奏、余额/深度限制、滑点缓冲。
- 这些内容更像把老 pocket 做成可执行 shell，而不是证明出现了新的 raw alpha family。
- 对 short-cycle desk 它有实现参考价值，但不该占用当前前排研究槽位。

## Runtime consequence
- `Fresh intake` 对该对象给出明确 first verdict：`background / P0`
- 不分配新 Rank
- 不进入 `Surviving candidate slot`
- 后续继续按 `cycle_plan` 的下一条 pending 对象推进
