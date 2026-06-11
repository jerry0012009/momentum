# 2026-04-17 18:08 UTC｜bot6 park-reframe｜Rank 55

## 0) 本轮选择
- 选定：`Rank 55 / order-imbalance crash-risk overlay`
- 轮转说明：继续按 `50+` 优先低频复盘；`Rank 55` 上次 bot6 复盘是 `2026-04-04 18:46 UTC`，已超过 `7` 天窗口，且 4 月上旬又新增了 `adverse-selection` 与 `venue liquidity fragility` 两组旁证，足够做一次“是否还值得再诚实派生”的复核。

## 1) 原 rank 为什么 park？
原 `park` verdict 保留，不推翻。

根据：
- `research/optimization_loop/2026-03-18_1142_rank55-crash-risk-intake.md`
- `research/optimization_loop/2026-03-18_1249_rank55-clean-replication.md`
- `research/optimization_loop/2026-03-18_1348_rank55-time-stability-park.md`

原线失败点一直很清楚：
- 它想把 `order-imbalance / flow shock / downside move` 写成服务 `ema_psar_long / fib_retest_long / breakout_short` 的 **15m shared crash-risk overlay**；
- clean replication 里只有 `ema_psar_long` 留下少量改善：`base≈+1.63% -> binary_crash_gate≈+3.15%`；
- `fib_retest_long` 基本无增量，`breakout_short` 虽少亏但仍为负；
- 随后的 time-stability 又把问题钉死：唯一三段都为正的只剩 `ema_psar_long + binary_crash_gate`，而且每桶平均 trades 只有约 `1.7~2.7`。

翻成人话：
- 主动成交失衡 / crash-pressure 不是完全没信息；
- 但它没有证明自己能作为 **跨 setup 可迁移的 shared crash overlay** 存活。

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 4 月 4 日那轮更接近 `hard with consumed residual`。**

原因：
- 软的一面：`ema_psar_long` 上仍留有一点“极端卖压环境下少做 / 缩做 long”式 residual；
- 硬的一面：4 月新增证据继续说明，真正有信息的主语不是旧 Rank 55 这种 `15m shared overlay`，而是更快的 microstructure raw alpha 或更上位的 venue-quality router。

## 3) 有没有“可救信号”？
- **有，但可救信号继续远离旧 Rank 55 本体。**

这次最相关的新旁证：
- `research/quant_digests/2026-04-06_1224_adverse-selection-cost-continuation-alpha.md`
  - 新证据保留下来的主语，不是“先给 15m base setup 做 crash veto”；
  - 而是 **`signed adverse-selection share shock × next-bar continuation`** 这条 `1m/3m/5m` 的 microstructure directional raw alpha。
- `research/quant_digests/2026-04-10_1758_binance-liquidity-fragility-router-gate.md`
  - 另一条新证据也没有回头支持旧 Rank 55；
  - 它更像把市场脆弱度写成 **breakout vs fade 的 shared router / regime layer**，而不是某个既有 setup 前的一层通用 crash gate。

所以，`Rank 55` 还剩下的那点“可救信号”更像两类外流：
1. **更快时钟的 signed-flow / adverse-selection raw alpha**；
2. **更上位的 venue liquidity / fragility router**。

它们都说明主题没死，但都不再诚实地属于旧 `Rank 55 / shared crash-risk overlay`。

## 4) 最值得改的唯一一刀是什么？
**如果只保留唯一一刀，最诚实的改法仍然是：把 `15m shared crash-risk overlay` 彻底降级/迁出为“更快时钟的 microstructure raw alpha 或更上位的 market-quality router”。**

也就是：
- 不再让它继续服务 `ema_psar_long / fib_retest_long / breakout_short` 这套 shared overlay 角色；
- 若保留主动成交失衡主题，优先把它写成 `1m/3m` 的 `signed-flow / adverse-selection continuation`；
- 若保留 crash-prone / fragility 主题，优先把它写成 continuation-vs-fade 的 router / regime 层。

但关键是：
- 这已经不是旧 Rank 55 的诚实窄 reframe；
- 而是在承认旧主题应该换宿主。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 审计对象——`15m shared crash-risk overlay`——其失败没有被推翻；
2. 4 月新增证据没有把它拉回旧职责层，反而继续把 residual 外流到新的 `microstructure raw-alpha / venue-quality router` 宿主；
3. 若现在硬写 `Rank 55b`，大概率只是把“主题迁移”误包装成“旧 rank 的单轴 reframe”；
4. bot6 这轮最诚实的动作，仍是保留原 `park` 的审计意义，而不是给旧 overlay 续一个名义上的窄派生。

## 6) 小结
- 原 rank 为什么 park：因为 shared crash overlay 只在单一 archetype 留下薄 pocket，跨 setup / 时间稳定都没站住。
- 更像 hard 还是 soft：`soft park`，但比 4 月 4 日那轮更接近 `hard with consumed residual`。
- 有没有可救信号：有，但都在外流到 `1m/3m adverse-selection raw alpha` 或 `market-quality router`。
- 最值得改的一刀：把旧 overlay 角色迁出，而不是继续微调 shared crash gate。
- 是否值得形成新的 derived hypothesis：**现在不值得**。
- `trade on`：保留“极端失衡/脆弱状态确实影响短窗路径”的信息价值。
- `trade off`：一旦继续沿旧 Rank 55 命名派生，就会模糊原 `park` 对 shared overlay 失败的审计意义。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park，但比 4 月 4 日那轮更接近 hard with consumed residual；4 月新增的 adverse-selection / venue liquidity fragility 证据继续说明，Rank 55 若还有 residual value，也更像新的 1m/3m microstructure raw-alpha 或 market-quality router 宿主，而不是足以再诚实派生旧 Rank 55 的 Rank 55b。`

## 8) 文件动作
- 新增：`research/park_reframe/2026-04-17_1808_rank55-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 9) commit
- 默认不做 commit。
- 原因：工作区存在大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做最小必要文档改动。