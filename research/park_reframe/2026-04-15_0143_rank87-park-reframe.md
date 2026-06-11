# Rank 87 park reframe review

- 时间：2026-04-15 01:43 UTC
- 对象：`Rank 87 / volume-clock + CS spread interaction gate`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮先读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-19_1102_rank87-volume-clock-intake.md`
- `research/optimization_loop/2026-03-19_1126_rank87-clean-replication-park.md`
- `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
- `research/quant_digests/2026-04-12_0924_nyse-open-betaspread-continuation-alpha.md`
- `research/quant_digests/2026-04-13_1220_pseudoopen-pseudoclose-tsmom-alpha.md`

## 1. 原 rank 为什么 park？
原始 clean replication 已把 blocker 说清楚：`Rank 87` 不是完全没改善，而是改善几乎全部来自**极端砍样本**，没有证明自己能作为 queue-facing 的 shared continuation gate 站住。

关键结果（6bps/side）是：
- `baseline`：`mean_total_return ≈ -28.85%`，`positive_asset_ratio=1/3`，`retention≈86.96%`
- `fixed_clock_gate`：`mean_total_return ≈ -5.73%`，`positive_asset_ratio=1/3`，`retention≈8.22%`
- `volume_clock_gate`：`mean_total_return ≈ -0.67%`，`positive_asset_ratio=1/3`，`retention≈3.42%`

所以原 park 不是因为“volume clock / liquidity state 完全没信息”，而是因为：
**这条 shared gate 只是在极少数窗口里少亏，但没有证明自己具备可迁移、可共用、可 queue-facing 的 admission 增量。**

## 2. 它更像 hard park 还是 soft park？
本轮判断：**soft park，但已经比 4 月 3 日那轮更接近 hard。**

理由：
- 仍能看到一点 residual：固定 funding 时钟确实太粗，真实交易时钟更像成交峰值附近；
- 但这点 residual 没有救活 `shared gate` 写法本身；
- 4 月 12~13 的新增证据继续说明，时钟信息更像应写成**独立的 session-pocket raw alpha / spread book**，而不是继续塞回 `Rank 87` 这种三条 base setup 共用的 allow/deny gate。

## 3. 现有证据里有没有“可救信号”？
**有，但只剩主题级可救信号，不再属于旧 Rank 87 本体。**

当前还能保留的信号主要有两类：
1. **真实成交时钟比固定 funding / 整点时钟更有信息**；
2. **session pocket 本身可能成立**，例如最近新增的：
   - `NYSE open 正向 pulse -> beta-spread continuation`
   - `pseudo-open overnight sign -> pseudo-close last-30m continuation`

但这些新证据的共同点是：
- 它们救活的是**新的 session-clock raw-alpha family**；
- 主语已经变成 `NYSE open beta-spread`、`pseudo-session first-to-last continuation` 这种独立 alpha；
- 而不是 `Rank 87` 原本那种“volume-clock + CS spread 作为 shared continuation gate，去共用放行 EMA/PSAR / Fib retest / breakout_short”。

## 4. 最值得改的唯一一刀是什么？
如果只谈“最值得改的唯一一刀”，本轮唯一诚实的表述是：

> **放弃 shared gate 身份，把“volume-clock / pseudo-session clock”从 continuation admission 层迁移成独立的 session-pocket raw alpha 宿主。**

但这刀**不值得写成 `Rank 87b`**，因为：
- 它已经不是在救 `Rank 87` 的单轴实现；
- 它相当于承认原 rank 的 gate 壳不成立，只保留“时钟主题还活着”；
- 新宿主的 entry / holding / exit / book 结构都变了，已经更像 fresh intake，而不是诚实的旧 rank 派生。

## 5. 是否值得形成新的 derived hypothesis？
**不值得。结论仍是 `keep_park`。**

原因：
- 最近新证据没有推翻原 blocker：`shared gate` 改善仍主要依赖极端 retention 压缩；
- 新证据反而把主题进一步上移到更完整的 session-clock raw-alpha 宿主；
- 若现在硬写 `Rank 87b`，大概率只是把新 family 借旧 rank 名义回灌到 queue，审计上不诚实。

## 6. trade on / trade off（why-not-draft）
本轮不 draft 新假设，但可以记录 why-not-draft：
- trade on：承认 clock information 仍有价值，且真实交易时钟优于固定 funding 锚；
- trade off：这份价值不再保留在 `Rank 87` 的 shared gate 角色里，而应外流到新的 session-pocket / clock-spread raw-alpha 宿主。

## 7. 本轮结论摘要
- 原 rank 为什么 park：`volume_clock_gate` 主要靠 `retention≈3.42%` 的极端砍样本把亏损压小，没证明 shared gate 成立。
- 更像 hard 还是 soft：`soft park`，但比 4 月 3 日那轮更接近 hard。
- 有没有可救信号：有，主要是“真实时钟 / session pocket 仍有信息”，但已不属于旧 Rank 87 gate 壳。
- 最值得改的唯一一刀：把 clock 主题从 shared gate 迁移到独立 session-pocket raw alpha 宿主。
- 是否值得形成新的 derived hypothesis：**否**。

## Final verdict
**`keep_park`**

## 对 queue 的更新口径
仅在 `docs/PARK_REFRAME_QUEUE.md` 与 `research/park_reframe/INDEX.md` 追加本轮记录；
不改 `docs/TODO.md` 顶部排班；
不新增 `Rank 87b`。

## Git / 提交
- 本轮只做最小必要文档更新。
- 未做 commit；默认避免把共享工作区其他脏文件混入。
