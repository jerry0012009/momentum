# 2026-04-16 04:18 UTC · Rank 4 park reframe

## Selected rank
- `Rank 4`
- selection note: 本轮 `Rank 1~37` 的 parked 条目里，最近 `7` 天几乎都已被 `bot6` 复盘；没有更干净的“未复盘 parked rank”可选。按规则改选 **最近确有新证据** 的旧 rank。`Rank 4` 上次 park-reframe 是 `2026-04-12 23:50 UTC`，而 2026-04-15 晚间又新增多条 pairs / stat-arb 证据，足够回答：这些新材料是在救旧 `Rank 4`，还是继续把主题外推到新的 pairs raw-alpha family。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/optimization_loop/2026-03-16_1838_rank4b-clean-replication.md`
- `research/optimization_loop/2026-04-08_1245_rank4_fresh_intake_first_verdict_background_sync.md`
- `research/optimization_loop/2026-04-11_0622_rank4_freshintake_first_verdict_background_p0.md`
- `research/park_reframe/2026-04-10_2002_rank4-park-reframe.md`
- `research/quant_digests/2026-04-15_2057_dynamicfactor-stationarybasket-alpha.md`
- `research/quant_digests/2026-04-15_2133_distancefirst-cryptopairs-baseline-alpha.md`
- `research/quant_digests/2026-04-15_2218_cointegrationfirst-nostop-cryptopairs-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 4` 被 park 的 authoritative blocker 没变：它作为 **direct pairs-trade / spread z-score entry** 时，最小 clean replication 已经把主要 pair 一起打成成本后明显为负。

最早的 hard audit 证据仍是：
- `BTC/ETH`: `trade_count=83`, `cumulative_net_return≈-12.42%`
- `BTC/SOL`: `trade_count=117`, `cumulative_net_return≈-22.91%`
- `ETH/SOL`: `trade_count=127`, `cumulative_net_return≈-27.77%`

随后虽有 `Rank 4b` 把 `ETH/SOL`、`BTC/SOL` 拉回轻微正 pocket，但：
- 它没有推翻原 `Rank 4 park`；
- 后续 runtime 又把 `Rank 4` residual first verdict 收口为 `background / P0`；
- 说明旧 `Rank 4` 真正失败的不是“参数还没调好”，而是 **把 fixed/rolling spread z-score 直接写成 queue-facing standalone alpha 这件事本身不够诚实。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 2026-04-12 那轮更接近 hard。**

原因：
- 软的部分：pairs / stat-arb 主题最近显然仍有强新证据，说明 relative-value 这条大主题没有死；
- 硬的部分：新证据越来越一致地说明，真正值得追的是 **pair admission / basket construction / threshold/no-trade band / regime gate** 这些更完整的壳，而不是旧 `Rank 4` 这种 direct spread-entry residual。

一句话：
> 主题还活，但旧 `Rank 4` 这具壳子更不像能继续承载它。

## 3) 有没有“可救信号”？
**有，但仍然是主题级可救信号，不是旧 rank 级可救信号。**

本轮新增三条最 relevant 证据：

### A. `distance-first pair admission × spread fade`
`2026-04-15_2133_distancefirst-cryptopairs-baseline-alpha.md` 说明：
- pairs 里最值得先保留的，可能是 **distance-first 的 pair admission baseline**；
- 价值主要落在“先挑什么 pair 更诚实”，而不是旧 `Rank 4` 的固定 pair + 固定 spread 直入场。

### B. `cointegration-first × no-stop intraday spread fade`
`2026-04-15_2218_cointegrationfirst-nostop-cryptopairs-alpha.md` 说明：
- 如果要把 pairs 主题重新写成完整壳，更像是 **cointegration-first admission + intraday spread fade + no-stop/time-stop risk shell**；
- 这已经不是旧 `Rank 4` 再补一个小 filter，而是 admission、risk、execution 一起重写。

### C. `stationary factor forecast × basket long-short`
`2026-04-15_2057_dynamicfactor-stationarybasket-alpha.md` 进一步说明：
- relative-value 主题也可能更诚实地迁移到 **basket / stationary-factor** 层；
- 真正有价值的是 `threshold/no-trade band + regime gate` 这套骨架，而不是旧 `Rank 4` 的单 pair spread 读法。

这三条新证据的共同方向不是：
- “给旧 Rank 4 多加一刀就够了”；

而是：
- “pairs 主题若要活，应落在新的 pair-admission / basket-residual / full-shell 宿主上。”

## 4) 最值得改的唯一一刀是什么？
**对旧 `Rank 4` 来说，当前最值得保留的唯一一刀仍然只是既有 `Rank 4c`；本轮没有新的唯一主修改轴。**

也就是：
- 保留 `BTC-ETH spread z-score`；
- 但只把它当 `shared risk overlay / position-sizing gate`；
- 不再把它当 direct pair-entry alpha。

为什么本轮不再新增 `Rank 4d`：
- 若改成 `distance-first admission`，就已换了宿主主语；
- 若改成 `cointegration-first + no-stop spread fade`，就已是完整新壳；
- 若改成 `stationary-factor basket`，更是 basket-level 新 family；
- 这些都不是旧 `Rank 4` 的单轴窄补丁。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 完整成立，且没有被新证据推翻；
2. 新证据没有提供属于旧 `Rank 4` 自己的新的单一修改轴；
3. 新 evidence 继续把 residual value 从 `old Rank 4` 外推到新的 pairs raw-alpha family；
4. 对旧 rank 而言，唯一仍诚实的 residual 仍只到既有 `Rank 4c`，不值得再写 `Rank 4d`。

## 6) Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-12 那轮更接近 hard`
- short note: `4 月 15 日新增的 distance-first、cointegration-first 与 stationary-factor pairs 证据继续说明：pairs 主题并未死亡，但真正可救的是新的 admission/basket/full-shell 宿主，而不是旧 Rank 4 的 direct spread-entry residual；旧 rank 的唯一诚实残余仍只到既有 Rank 4c。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改写 `TODO`。只是把边界再说得更硬一点：
- `pairs` 主题仍值得追；
- 但应该作为新的 full-shell / basket / admission family 去追，**不是**继续在旧 `Rank 4` 名下硬派生 `Rank 4d`。

## Git
- 未做 commit。
- 原因：工作区存在共享脏文件；本轮只做最小必要文档更新与邮件交付，避免混提。
