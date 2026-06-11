# Rank intake log — BTC tick impulse × ADA delayed catch-up

- Time: 2026-04-07 18:09 UTC
- Target: `research/quant_digests/2026-04-07_1640_btc-ticklead-ada-catchup-alpha.md`
- Slot before action: `Fresh intake`
- Action: first verdict

## What changed
`BTC tick impulse × ADA 60s delayed catch-up` 已完成 first verdict：它把既有 `BTC-first alt-lag / leader-follower / cross-market ITSM` 家族压缩到更短的秒级窗口与更窄的单币对上，但新的主语仍然是 `BTC 先动、follower 后补`，并没有提出独立于现有 lead-lag 家族的新 raw alpha pocket，因此本轮诚实收口为 `background / P0`，不进入 survivor。

## Why this is the right verdict
1. 论文真正新增的是 `16~118s`、均值约 `56~57s` 的 lead duration 量级提示，不是新的收益机制。
2. 交易翻译仍是标准 `leader impulse -> follower catch-up`：BTC 冲击、ADA 滞后、随后补涨/补跌；这和现有 leader-follower 主语一致，只是时钟更短、对象更窄。
3. 文中没有把成本后仍稳健成立的独立 execution pocket、可迁移资产簇或新的过滤逻辑压成一条能单独立项的主线；它更像是旧家族的高频刻度补充，而不是新的 family。
4. 因此它有研究参考价值，但不值得占用 survivor / P1 前排资源。

## Runtime write-back
- `Fresh intake slot.current_target` 切到本对象
- `Fresh intake slot.latest_result` 写为 `background / P0`
- `cycle_plan` 第 2 条标记为 `done`
- `Background pool.latest_parked` 更新为本对象

## Reader-facing consequence
这条 digest 保留为 lead-lag 家族的参考证据，但不升级为独立前排候选，也不分配新 Rank。
