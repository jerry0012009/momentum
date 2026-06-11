# 2026-04-02 23:28 UTC · Rank 4 park reframe

## Selected rank
- `Rank 4`
- selection note: 本轮按 `Rank 1~37` 的 parked 条目继续低频轮转；`Rank 4` 上次 bot6 复盘为 `2026-03-24 14:30 UTC`，已超过 `7` 天。最近 `2026-04-02` 又集中新增多条 pairs / stat-arb digest，适合再判断一次：这些新证据到底是在救旧 `Rank 4`，还是把主题继续推向新的 full-stack family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/optimization_loop/2026-03-30_0143_rank4_threshold_governed_pairs_residual_stays_park_reframe.md`

原 `Rank 4` 被 park 的原因没有变：它作为 **direct pairs-trade / spread z-score entry** 时，clean replication 在主要 pairs 上一起为负。

冻结版 first-pass 结果：
- `BTC/ETH`: `trade_count=83`, `cumulative_net_return≈-12.42%`
- `BTC/SOL`: `trade_count=117`, `cumulative_net_return≈-22.91%`
- `ETH/SOL`: `trade_count=127`, `cumulative_net_return≈-27.77%`

后来虽然一度出现过 rolling / threshold / pair-scope 的轻微 pocket，但它们没有把原 rank 重新变成可诚实推进的 direct-entry alpha。原审计意义必须保留：

> 失败对象是“把少数 pair 的 frozen-beta / spread z-score 直接写成可 queue 的 standalone alpha”这件事，
> 不是“pairs / stat-arb 主题永远无效”。

## Hard park or soft park?
- 本轮判断：`soft park，但比 3 月下旬时更偏硬`

为什么不是 pure hard park：
- pairs / stat-arb 主题最近明显没死，甚至证据在变多；
- 说明“relative-value / spread / factor-stripping / bucket governance”这一大类仍值得研究。

为什么又更偏硬：
- 这些新增价值越来越像**另一条完整 raw-alpha family**；
- 而不是原 `Rank 4` 还能再诚实切出一个新的单轴 `Rank 4d`。

翻成人话：
- 主题活着；
- 但旧 `Rank 4` 这具壳子越来越不适合继续装新东西。

## Any salvage signal?
有，但主要是“主题未死”的信号，不是“旧 rank 还能再窄救一刀”的信号。

本轮最 relevant 的新增证据来自 `research/quant_digests/INDEX.md` 中近期 pairs / stat-arb 条目，例如：
- `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
- `2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`
- `2026-04-02_2018_multiquote-bucket-rv-alpha.md`
- `2026-04-02_1946_dynamic-scaling-pairs-alpha.md`
- `2026-04-02_0405_coint-lookback-volfilter-trailingstop-pairs-alpha.md`
- `2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`

这些新证据共同说明：
1. pairs 现在更值得写成 **threshold-governed / basket-governed / factor-stripped / dynamically-sized** 的完整 family；
2. 它们的 alpha 语言已经从“单 pair z-score 偏离”扩展到：
   - pair-specific threshold map
   - multi-pair rotation
   - factor stripping / stationary factor
   - dynamic scaling / allocation shell
   - multi-quote bucket routing
3. 这类新增价值不再像旧 `Rank 4` 的唯一主修改轴，而像新的更宽主语。

所以可救信号确实存在，但它在说的是：
- **应该新开更完整的 pairs/stat-arb intake family**；
- 不是继续给旧 `Rank 4` 再挂一个 `4d`。

## Single best cut
如果只保留唯一一刀，当前最诚实的仍然是既有 `Rank 4c`：

> 把 `BTC-ETH spread z-score` 从 direct pairs-trade entry，降级成 shared risk overlay / position-sizing gate。

本轮不建议再写新的唯一主修改轴，原因是：
- 若写成 `threshold governance`，那不是一刀，而是把 entry / exit / basket / cost 一起重写；
- 若写成 `dynamic sizing`，也不是一刀，而是在把完整 risk shell 偷渡进旧 rank；
- 若写成 `factor stripping` 或 `multi-pair rotation`，主语已经彻底变成新的 stat-arb family。

所以本轮最值得改的唯一一刀，**仍然只是旧的 `Rank 4c`，不是新的 `Rank 4d`。**

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

原因：
1. 原 `park` verdict 仍完整成立；
2. 最近新增证据没有给 `Rank 4` 提供一个新的、仍属于它自己的唯一主修改轴；
3. pairs 主题的新增价值正在继续上移到新的 full-stack raw-alpha family；
4. 对旧 rank 来说，唯一还诚实的 residual cut 仍是既有 `Rank 4c`，没有必要再硬造 `Rank 4d`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但更偏硬；最近新增的 RF threshold / dynamic-factor / multiquote bucket / dynamic-scaling / dynamic-coint 证据，继续把 pairs 主题推向新的 full-stack stat-arb raw-alpha family，不足以在既有 Rank 4c 之外再诚实派生 Rank 4d`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。