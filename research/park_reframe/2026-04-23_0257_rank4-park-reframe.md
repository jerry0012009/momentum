# 2026-04-23 02:57 UTC · Rank 4 park reframe

## Selected rank
- `Rank 4`
- selection note: 本轮按用户限定只看 `Rank 1~37` 的 parked rank。最近 7 天里该号段大多已被复盘；`Rank 4` 上次 park-reframe 为 `2026-04-16 04:18 UTC`，已超出 7 天窗口，同时 4 月 21~23 又新增多条 pairs / stat-arb 证据，适合复核这些新材料到底是在救旧 `Rank 4`，还是继续把主题外推到新的 stat-arb full shell。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-16_0418_rank4-park-reframe.md`
- `research/park_reframe/2026-04-12_2350_rank4-park-reframe.md`
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/optimization_loop/2026-03-16_1838_rank4b-clean-replication.md`
- `research/optimization_loop/2026-04-08_1245_rank4_fresh_intake_first_verdict_background_sync.md`
- `research/optimization_loop/2026-04-11_0622_rank4_freshintake_first_verdict_background_p0.md`
- `research/quant_digests/2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md`
- `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`
- `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`
- `research/quant_digests/2026-04-23_0248_walkforward-cointegration-basket-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 4` 被 park 的审计结论没变：把少数 major pair 的 frozen-beta spread z-score 直接写成 queue-facing standalone alpha 时，clean replication 已在主要 pairs 上一起失败。

最早 hard audit（`2026-03-16_1508_rank4-pairs-clean-replication-park.md`）关键结果仍然是：
- `BTC/ETH`: `trade_count=83`, `cumulative_net_return≈-12.42%`
- `BTC/SOL`: `trade_count=117`, `cumulative_net_return≈-22.91%`
- `ETH/SOL`: `trade_count=127`, `cumulative_net_return≈-27.77%`

后续虽然有 `Rank 4b` 把局部 pair 拉回轻微正 pocket，但它没有推翻原结论；随后又被 time-stability 与 runtime first verdict 收口到 `background / P0`。所以旧 `Rank 4` 被否掉的核心不是“参数还差一点”，而是：

> **旧 Rank 4 这层 direct pair-spread entry 宿主，不足以诚实承载 relative-value 主题。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但已比 4 月 16 日那轮更接近 hard park with consumed residual。**

原因：
- `soft` 的部分：4 月 21~23 新证据继续说明 pairs / stat-arb 主题本身没死，甚至还很活跃；
- `更接近 hard` 的部分：这些新证据几乎一致地要求 `walk-forward admission / cointegration筛选 / threshold治理 / maker-first / basket / regime veto / risk-parity sizing` 这种更完整的新壳，而不是给旧 `Rank 4` 再补一个小补丁。

一句话：
> 主题活着，但旧 `Rank 4` 这具壳子越来越不像值得继续派生 `Rank 4d` 的宿主。

## 3) 有没有“可救信号”？
**有，但仍然是主题级可救信号，不是旧 rank 级可救信号。**

### A. maker-first + half-life time-stop pair shell
`2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md` 留下的信号是：
- cointegration spread fade 还能活；
- 但真正重要的是 `rolling pair admission + maker-first + half-life time-stop` 这套完整执行骨架。

这已经不是旧 `Rank 4` 的“固定 pair + direct spread z-score”小修小补。

### B. zero-cross exit + kill-switch pair shell
`2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md` 进一步说明：
- spread fade 在 short-cycle 上仍可见 gross edge；
- 但真实可迁移价值更像 `thicker threshold + zero-cross exit + account-level kill-switch` 的完整策略骨架。

这同样是在重写 exit / risk shell，而不是旧 `Rank 4` 自己的新单轴残余。

### C. fixed / dynamic threshold 是 pair shell 的核心，而不是旧 residual
`2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md` 最关键的启示不是“dynamic 或 fixed 谁一定更好”，而是：
- threshold 机制本身决定 edge 厚度；
- pair pocket 与周期（`15m` vs `5m`）一起决定哪种 threshold 更合适。

这继续把主题推向 `selected pair + threshold shell`，而不是旧 `Rank 4` 还能诚实切出一条新 residual。

### D. walk-forward basket / regime veto / risk parity
`2026-04-23_0248_walkforward-cointegration-basket-alpha.md` 又把主题进一步上移到：
- walk-forward cointegrated basket
- regime veto
- risk-parity sizing

这已经明显是新的 stat-arb full shell / basket family，不再属于旧 `Rank 4` 的窄 reframe。

## 4) 最值得改的唯一一刀是什么？
**对旧 `Rank 4` 来说，本轮最值得保留的唯一一刀仍然只是既有 `Rank 4c`；没有出现新的唯一主修改轴。**

也就是：
- 保留 `BTC-ETH spread z-score` 这类 residual 信息；
- 但只把它当 `shared risk overlay / position-sizing gate`；
- 不再把它当 direct pair-entry alpha。

为什么本轮不能诚实写 `Rank 4d`：
- 若改成 `maker-first + time-stop`，已经重写 execution shell；
- 若改成 `fixed/dynamic threshold pair shell`，已经重写 admission + threshold 主语；
- 若改成 `walk-forward basket + regime veto`，更是新的 full-shell / basket family。

这些都不是旧 `Rank 4` 的单轴窄补丁。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 新证据没有给出还属于旧 `Rank 4` 的新的单一修改轴；
3. 所有新增证据都在把 residual value 从 `old Rank 4` 外推到新的 pairs/stat-arb full shell；
4. 对旧 rank 而言，唯一仍诚实的 residual 仍只到既有 `Rank 4c`，没有必要再 draft `Rank 4d`。

## 6) 单轮模板回答
### 原 rank 为什么 park？
因为最小 clean replication 在主要 pairs 上一起偏负，而后续 rolling-beta / residual 窄重开也没能跨过时间稳定性与独立 alpha 主语这两个门槛。

### 它更像 hard park 还是 soft park？
`soft park`，但已比 4 月 16 日那轮更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但只是主题级：cointegration、threshold、maker-first、walk-forward basket 这些都说明 pairs / stat-arb 还值得追；只是它们已经属于新的 full shell，而不是旧 `Rank 4` 本体可救。

### 最值得改的唯一一刀是什么？
仍只是既有 `Rank 4c`：把 spread z-score 残余收缩成 shared risk overlay / sizing gate，而不再当 direct pair alpha。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但已比 2026-04-16 那轮更接近 hard park with consumed residual`
- short note: `4 月 21~23 的 maker-first/time-stop、zero-cross/kill-switch、fixed-vs-dynamic threshold 与 walk-forward basket 新证据继续说明：pairs / stat-arb 主题还活，但真正可救的是新的 admission / threshold / basket / full-shell 宿主，而不是旧 Rank 4 的 direct spread-entry residual；旧 rank 的唯一诚实残余仍只到既有 Rank 4c。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改写 `TODO`。只是进一步确认：
- `pairs / stat-arb` 值得继续研究；
- 但应作为新的 shell / basket / admission family 去追，而不是继续在旧 `Rank 4` 名下硬切 `Rank 4d`。

## Git
- 未做 commit。
- 原因：工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档更新与邮件交付，避免混提。
