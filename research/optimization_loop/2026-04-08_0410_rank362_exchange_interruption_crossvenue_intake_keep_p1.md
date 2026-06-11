# Rank 362 — venue-freeze price gap × re-link close — fresh intake first verdict (`keep_P1`)

- Time: 2026-04-08 04:10 UTC
- Target: `research/quant_digests/2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md`
- Slot before action: `Fresh intake`
- Decision: `keep_P1`
- Assigned Rank: `362`

## Why this changed system belief
这条对象已经不是泛化的“交易所 outage 会带来机会”评论，而是一个主语、异常代理、入场/出场壳都已压清的独立 raw alpha intake：
- 主语明确：`stale venue quote / heartbeat gap` 相对 `healthy reference` 的异常偏离；
- 异常代理明确：`quote_age_sec` / `heartbeat_gap_sec` / `stale_flag`；
- 收益机制明确：异常解除后的 `re-link close`；
- 最小执行壳明确：同标的跨所、以高流动性 majors 为先、按深度约束定仓，并显式纳入 fee/slippage/orphan-leg 风险。

因此它已经足够作为一个独立 front-slot 问题保留到 `P1`，而不该直接扔回泛 cross-venue arbitrage 背景池。

## Why not `P2` yet
当前证据仍主要来自论文事件统计与 clean-room 假设，尚未完成：
1. 现代主流 venue（Binance/OKX/Bybit）上的 proxy 事件提取；
2. after-cost `post-cost spread capture` 与 `orphan-leg ratio` 的最小现实检验；
3. 区分“冻结失真”与“健康 venue 价格领先”的简化 veto。

所以本轮最诚实的位置是 `keep_P1`，进入唯一一次 survivor follow-up，而不是直接升 `P2`。

## Suggested single decisive follow-up
下一步唯一高杠杆检查应是：
- 用 `quote staleness / heartbeat gap` 代理在现代 majors 跨所数据上做一次 cheap decisive quickcheck；
- 直接回答异常解除后是否仍存在可复述的 `after-cost spread capture`，以及 orphan-leg 是否把纸面 edge 吃掉。

## Result sentence
`Rank 362` 已完成 fresh first verdict：`venue-freeze price gap × re-link close` 已把 stale-side 主语、异常代理、回补机制与最小执行壳压清，足以作为独立事件驱动 cross-venue raw alpha 保留到 `P1`，但因缺少现代多-venue after-cost quickcheck，当前先不升 `P2`。
