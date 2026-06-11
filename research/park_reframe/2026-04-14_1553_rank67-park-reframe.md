# Rank 67 park reframe review

- 时间：2026-04-14 15:53 UTC
- 对象：`Rank 67 / regime-matrix shared-state gate`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮先读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2130_rank67-regime-matrix-park.md`
- `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/overall_summary.csv`
- `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/setup_compare.csv`
- `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/regime_summary_30m.csv`
- `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/time_pockets.csv`
- `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md`

## 1. 原 rank 为什么 park？
原始 clean replication 已把 blocker 说得很清楚：`Rank 67` 的四态 regime matrix 作为**三条 setup 共用的 shared state language**并没有站住。

关键问题不是“完全没改善”，而是“改善方式不诚实”：
- `ema_psar_long`：6bps 下 `base=-3.79%`，`no_mr=-1.47%`，`trend_expansion_only=-1.26%`；但 retention 只剩 `20.95%` / `16.19%`
- `fib_retest_long`：6bps 下 `base=+1.20%`，`no_mr=+2.04%`，`trend_expansion_only=+2.04%`；但 retention 只剩 `15.15%`
- `breakout_short`：6bps 下 `base=-3.54%`，`no_mr=-1.04%`，`trend_expansion_only=-0.49%`；但 retention 只剩 `26.10%` / `17.05%`
- `breakout_short` 在 `trend_expansion_only` 下的 `false_break_or_hold_4bars_rate` 还从 `61.70%` 升到 `72.22%`
- `compression_to_expansion_breakout` 这一臂直接没有形成可比样本

所以原 park 不是因为“regime 主题彻底没信息”，而是因为：
**这套 shared 4-state gate 主要靠大幅砍样本减亏，没证明自己足以成为 queue-facing 的共用 admission language。**

## 2. 它更像 hard park 还是 soft park？
本轮仍判断：**soft park，但已明显向 hard park 靠。**

理由：
- 它确实留下过一点 residual，尤其是 `fib_retest_long` 的 `no_MR / trend+exp` pocket；
- 但这些 residual 从 3 月到现在都没有长成“属于 Rank 67 自己”的独立单轴；
- 相反，残余信息越来越像：只能作为某个更完整趋势壳/continuation 壳里的**局部 context veto**，而不是一条独立的 shared-state rank。

## 3. 现有证据里有没有“可救信号”？
有，但很弱，而且已高度宿主化。

唯一还算可救的信号是：
- `fib_retest_long` 在排除 `Mean Reversion` 后，结果从 `+1.20%` 提到 `+2.04%`；
- 同时 dispersion 下降到 `0.00522`，`false_4bars=0`。

但这个 pocket 的问题也很明确：
- retention 只有 `15.15%`，高度依赖砍样本；
- 它没有证明“四态 regime matrix”本身有普适增量；
- 它更像“某个 continuation / pullback 宿主需要一个更窄的 HTF or daily veto”，而不是 `Rank 67` 这层 shared language 本体复活。

## 4. 最值得改的唯一一刀是什么？
如果只谈“最值得改的一刀”，唯一还算诚实的表述是：

> **把 `shared 4-state regime matrix` 继续降级成 `单一 setup-local 的 HTF / daily veto`，而不是三条 setup 共用的 regime language。**

但这刀本轮**不值得正式 draft 成 Rank 67b**，原因有两点：
1. 这已经不再像 `Rank 67` 本体的窄重开，而是把 residual 迁移到别的完整壳里；
2. 2026-04-14 新 digest（`daily-trend veto × 15m technical-vote continuation`）给出的更强信息是：**regime filter 更适合作为完整 raw-alpha shell 的局部 veto，而不是抽象成跨 setup 的 shared matrix。**

也就是说，这条“唯一一刀”更像一个**迁移方向判断**，而不是值得挂到 queue 里的新派生 rank。

## 5. 是否值得形成新的 derived hypothesis？
**不值得。结论仍是 `keep_park`。**

原因：
- 最近新证据没有推翻原 blocker；
- 新证据反而进一步说明：regime / daily filter 的价值存在于**完整壳里的 local veto**，不在 `Rank 67` 这种 shared-state gate 写法里；
- `Rank 67` 的唯一残余，在 desk 语言里早已被 `Rank 25b / 21b / 9b` 一类更窄提案以及最新 daily-veto shell 继续吸收；
- 现在若硬写 `Rank 67b`，大概率只是换宿主重讲，不是诚实的单轴派生。

## 6. trade on / trade off（仅做 why-not-draft 说明）
本轮不 draft 新假设；但可以记录 why-not-draft：
- trade on：放弃“shared regime matrix 适合三条线共用”的大叙事，承认 regime 信息只在局部壳里有价值；
- trade off：`Rank 67` 失去 queue-facing 独立性，残余价值被并入别的 raw-alpha / shell admission，而不是保留为独立 reframe 候选。

## 7. 本轮结论摘要
- 原 rank 为什么 park：shared 4-state gate 的改善主要靠大幅砍样本；`compression->expansion` 臂几乎不成立；并未形成可信的三线共用语言。
- 更像 hard 还是 soft：`soft park`，但比 4 月 1 日那轮更接近 hard。
- 有没有可救信号：只有 `fib_retest_long` 上的“排除 MR”局部 pocket，但 retention 过低且已宿主化。
- 最值得改的唯一一刀：继续把 shared regime language 降级为 setup-local HTF/daily veto。
- 是否值得形成新的 derived hypothesis：**否**。

## Final verdict
**`keep_park`**

## 对 queue 的更新口径
仅在 `docs/PARK_REFRAME_QUEUE.md` 与 `research/park_reframe/INDEX.md` 追加本轮记录；
不改 `docs/TODO.md` 顶部排班；
不新增 `Rank 67b`。

## Git / 提交
- 本轮只做最小必要文档更新。
- 未做 commit；默认避免把共享工作区其他脏文件混入。