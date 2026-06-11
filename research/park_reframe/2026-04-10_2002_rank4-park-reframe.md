# 2026-04-10 20:02 UTC · Rank 4 park reframe

## Selected rank
- `Rank 4`
- selection note: 按 `50~79 -> 80~110 -> 1~24 -> 25~49` 轮转，本轮回到 `1~24`；`Rank 4` 上次 `bot6` 复盘是 `2026-04-02 23:28 UTC`，已超过 `7` 天。近一周又新增多条 pairs / stat-arb digest，足够回答：这些新证据是在救旧 `Rank 4`，还是继续把主题外推到新的 full-stack family。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/optimization_loop/2026-03-30_0143_rank4_threshold_governed_pairs_residual_stays_park_reframe.md`
- `research/park_reframe/2026-03-18_2145_rank4-park-reframe.md`
- `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
- `research/park_reframe/2026-04-02_2328_rank4-park-reframe.md`
- `research/quant_digests/2026-04-10_0127_dynamic-halflife-admission-pairs-alpha.md`
- `research/quant_digests/2026-04-10_1857_local-hurst-fastreversion-pocket-pairs-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 4` 的 authoritative blocker 没变：它作为 **direct pairs-trade / spread z-score entry** 时，最小 clean replication 在主要 pairs 上一起为负。

关键原始证据：
- `BTC/ETH`: `trade_count=83`, `cumulative_net_return≈-12.42%`
- `BTC/SOL`: `trade_count=117`, `cumulative_net_return≈-22.91%`
- `ETH/SOL`: `trade_count=127`, `cumulative_net_return≈-27.77%`

后续已经把最自然的 direct-entry 救法消费过：
- `Rank 4b` 尝试把 frozen beta 改成 rolling beta；
- `Rank 4c` 又把 residual 收窄成 `BTC-ETH spread z-score` shared risk overlay；
- 2026-03-30 也已明确：`threshold governance / basket governance / dynamic sizing` 这些新增价值更像新的 pairs full-stack family，不再是旧 `Rank 4` 的单一窄补丁。

所以原 `park` 结论保留：
> 被否掉的是“把少数 pair 的 spread z-score 直接写成 queue-facing standalone alpha”这件事，
> 不是 `pairs / stat-arb` 主题整体死亡。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：`soft park`，但已继续向 hard 靠。**

原因：
- soft 的部分：pairs / stat-arb 主题近期仍有新证据，说明相对价值本体没死；
- hard 的部分：这些新证据越来越清楚地指向“新的 dynamic-admission / fast-reversion-pocket family”，而不是旧 `Rank 4` 再诚实切一刀就能救活。

换句话说：
- 主题还活；
- 但旧 `Rank 4` 这具壳子已经越来越不适合承载它。

## 3) 有没有“可救信号”？
**有，但更像主题级可救信号，不像旧 rank 级可救信号。**

本轮最 relevant 的新增证据有两类：

### A. dynamic admission 主题更强
`2026-04-10_0127_dynamic-halflife-admission-pairs-alpha.md` 的重点不是“再证明一遍 spread 会均值回归”，而是：
- 哪一对值得做，本身就是 alpha admission 的一部分；
- `half-life` / rolling admission / pair rotation` 比固定 `BTC/ETH + 固定 z-score` 更关键。

### B. local Hurst 更像 fast-reversion pocket rank
`2026-04-10_1857_local-hurst-fastreversion-pocket-pairs-alpha.md` 的 desk 结论也很清楚：
- 不应把 `H<0.5` 直接硬搬成通用 veto；
- 更合理的读法是把 `local Hurst` 当作 pair 内部的 fast-reversion pocket rank / hold-budget feature。

这两条新增 evidence 的共同方向不是：
- “给旧 `Rank 4` 多补一个小 filter 就够了”；

而是：
- “pairs alpha 若要活，更像 `dynamic pair admission × fast-reversion pocket × spread MR shell` 这条新的 full-stack family。”

## 4) 最值得改的唯一一刀是什么？
**对旧 `Rank 4` 来说，当前最值得保留的唯一一刀仍然只是既有 `Rank 4c`；本轮没有新的唯一主修改轴。**

也就是：
- 保留 `BTC-ETH spread z-score`；
- 但只把它当 `shared risk overlay / position-sizing gate`；
- 不再把它当 direct pair-entry alpha。

为什么本轮不再新增一刀：
- 若写成 `dynamic admission`，就不再是一刀，而是把 pair selection / half-life / rotation 一起改写；
- 若写成 `local H pocket rank`，也不是原 Rank 4 的窄补丁，而是在给新的 pairs shell 增加 admission feature；
- 这两条都更像新的 raw-alpha 宿主，而不是旧 `Rank 4` 的 `4d`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 仍完整成立；
2. 本轮新增证据没有提供属于旧 `Rank 4` 自己的新单一修改轴；
3. 新 evidence 继续把 residual value 从 `old Rank 4` 外推到新的 pairs full-stack family；
4. 对旧 rank 而言，唯一仍诚实的 residual cut 仍只是既有 `Rank 4c`。

## 6) Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但继续向 hard 靠`
- short note: `近一周新增的 dynamic admission / local Hurst 证据没有把旧 Rank 4 救回 queue-facing direct-entry 或再诚实切出 Rank 4d；它们继续把 pairs 主题抬升到新的 full-stack raw-alpha family，而旧 rank 的唯一残余仍只到既有 Rank 4c 为止。`

## Minimal audit note
本轮没有推翻原 `park`，也没有重写 `TODO`。只是补充了一条更清楚的边界：
- `pairs` 主题仍值得追；
- 但应该作为新 family 去追，**不是**继续在旧 `Rank 4` 名下硬派生。

## Git
- 未做 commit。
- 原因：工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档更新，避免混提。
