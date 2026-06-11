# 2026-04-10 00:30 UTC · Rank 68 park reframe review

## Scope
- source rank: `Rank 68 / block-mitigation retest score`
- source status kept: `park`
- this round verdict: `keep_park`
- original `park` verdict: **kept for audit**

## Why this rank now
- 本轮按 `bot6` 轮转仍优先补 `50~79` 号段。
- `docs/PARK_REFRAME_QUEUE.md` 最近 `7` 天没有复盘过 `Rank 68`。
- `Rank 68` 属于典型“原命题留下了一点 hold-quality 残余，但很可能已被邻近 family 吸收”的 parked 条目，适合做一次低频收口。

## Original park reason
原始 intake 与 clean replication（`2026-03-18_2148_rank68-source-intake.md`、`2026-03-18_2207_rank68-clean-replication-park.md`）要做的事是：
- 不改 base trigger；
- 给 `ema_psar_long / fib_retest_long / breakout_short` 三条 lane 都加一层 shared `block-mitigation retest score`；
- 问题不是有没有 block，而是“这次 breakout / retest 是否来自更扎实的 consolidation block”。

它被 park 的核心原因很清楚：
1. `plus_block_length` 和 `plus_block_length_and_range` 几乎没有带来结构性改善；
2. 真正少亏的是 `full` gate，但主要靠极重砍样本：
   - `ema_psar_long` retention 约只剩 `8.57%`
   - `fib_retest_long` retention 约只剩 `9.09%`
   - `breakout_short` retention 约只剩 `21.45%`
3. 最伤的是：`fib_retest_long` 从 `base≈+1.20%` 被筛到 `full≈-0.02%`，说明这套 shared block-quality 语言不但没跨 lane 站住，反而把原本还活着的一条线筛坏了。

一句人话：
> 原 Rank 68 不是“看不见干净回踩”，而是“只有把样本砍到很薄时才显得更干净”，这还不够构成诚实的 shared gate。

## Hard park or soft park?
- **结论：`soft park`，但对原 `Rank 68` 本体已经明显往 `hard park` 靠。**

为什么不是纯 hard：
- `full` gate 确实让 `ema_psar_long` / `breakout_short` 的 `failure-before-target` 降了一些；
- 说明“回踩质量 / hold-quality”主题不是完全没信息。

为什么又不该乐观：
- 这些改善主要靠 retention 崩塌换来；
- 且 shared 设定直接伤到了 `fib_retest_long`；
- 所以被证伪的不是“block / retest quality 完全没信息”，而是 **“把它写成 breakout_short / Fib / EMA 三线共用的 block-mitigation score gate” 这件事本身**。

## Salvage signal check
有可救信号，但已经很窄，而且更像被别的宿主吸收了：
- 原 Rank 68 留下的唯一残余，不再是 `block length / range / vol / depth` 这套 shared score 本身；
- 真正留下的只是更泛化的 `long-side pullback honesty / hold-quality` 语义。

问题在于，这条残余现在已经和现有 family 高度重叠：
- `Rank 64b` 已经把“shared pullback-quality gate”收窄成 `long-side-only hold-quality / admission score`；
- `Rank 101` 也长期保留为 `long-side hold-quality residual note`；
- 近期 digest 继续把同主题往更明确的 long-side trend shell / session shell 宿主推，而不是支持再回头救原 Rank 68 的 shared gate 写法。

所以本轮判断是：
- **可救信号有；**
- **但它更像旧 residual 已被 `Rank 64b / Rank 101` 一类邻近对象消费，而不是还能从原 Rank 68 再诚实切出一条新的独立主轴。**

## Single best modification axis
- **本轮判断：没有新的唯一主修改轴。**

如果硬要总结原线唯一还剩的方向，那也只是：
- 把 `shared block-mitigation retest score`
- 继续降级成更普通的 `long-side hold-quality / pullback honesty gate`

但这已经不是新的轴了，而是已被既有 `Rank 64b` 基本吸收的旧 residual。

## Should this become a new derived hypothesis?
- **No. 不值得形成新的 derived hypothesis。**
- 本轮最终 verdict：`keep_park`

### Why not draft `Rank 68b`
因为现在若硬写 `Rank 68b`，大概率只会落入下面几种不诚实路径：
1. 把 `block` 语言换个名字，实质上重复 `Rank 64b` 的 long-side hold-quality 叙事；
2. 顺手删掉 `breakout_short`、删成 long-only，再把旧 residual 重新包装成新 rank；
3. 再叠第二轴（session / HTF / trend shell / regime）去制造“新故事”。

这三条都不符合本任务纪律：
- 会稀释原 `park` 的审计意义；
- 会把 bot6 变成重复改写 parked 条目的机器；
- 也不满足“每轮最多只提 1 条唯一主修改轴”的边界。

## Final verdict
- `source_rank`: `Rank 68`
- `verdict`: `keep_park`
- `park_type_now`: `soft park -> near hard for the original shared-gate reading`
- `salvage_signal`: `有，但已收缩成 long-side hold-quality residual，且基本被 Rank 64b / Rank 101 family 吸收`
- `single modification axis`: `none new`
- `derived_hypothesis`: `no`

## Files checked
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2148_rank68-source-intake.md`
- `research/optimization_loop/2026-03-18_2207_rank68-clean-replication-park.md`
- `research/park_reframe/2026-04-09_2214_rank30-park-reframe.md`
- `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
- `research/park_reframe/2026-04-09_0024_rank10-park-reframe.md`

## Commit note
- 未提交。
- 原因：git 工作区存在无关脏文件；本轮仅做最小必要文档改动，避免混提。
