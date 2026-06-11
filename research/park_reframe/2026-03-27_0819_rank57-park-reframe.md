# 2026-03-27 08:19 UTC — Rank 57 park reframe review

## 本轮对象
- `Rank 57 / TTM squeeze release regime gate`
- 原始 parked rank 保留审计意义；本轮只判断：它现在是否值得再派生一个新的窄 reframe hypothesis。

## 读了什么
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1432_rank57-source-intake.md`
- `research/optimization_loop/2026-03-18_1451_rank57-clean-replication-park.md`

## 1. 原 Rank 为什么 park？
核心原因很简单：**唯一看起来像“有用的一刀”，已经在最小 clean replication 里被审过，但改善主要来自大幅砍样本，不是形成了跨 setup、跨资产都更诚实的 shared regime gate。**

原 clean replication 的关键信号：
- `breakout_short` 上，`release_recent_gate` 确实把均值亏损从约 `-3.55%` 压到接近 `-0.10%`；
- 但代价是 `trade_count_retention≈25.22%`，明显过薄；
- `fib_retest_long` 没有被稳定改善，反而从 `base≈+1.17%` 滑到 `release≈+0.30%`；
- `ema_psar_long` 虽少亏一点，但 retention 只剩约 `11%~13%`，同样更像极端减样本；
- 时间稳定性与 release 窗口 `1~4 bars` 的最小邻域扫描，也没给出“稍微改参数仍站得住”的强证据。

所以原 park 不是“完全没信息”，而是：**信息量不足以支撑 queue-facing 的新 rank。**

## 2. 它更像 hard park 还是 soft park？
我会把它定为：**`soft park，但偏硬`**。

为什么不是纯 hard park：
- `release_recent` 在 `breakout_short` 上至少留下了“压 whipsaw / 少做压缩后假动作”的弱残余；
- 主题本身（compression -> release）并非胡说八道，逻辑上也容易理解。

为什么又偏硬：
- 这点残余几乎只站在一个很窄的 slice 上；
- 一旦要求跨 setup 可迁移、跨资产可复用、或只做最小邻域稳定性，它就站不住；
- 改善形态更像“把大部分交易砍掉后少亏”，而不是“真的筛出更好的交易”。

## 3. 现有证据里有没有“可救信号”？
**有，但很弱。**

最像可救信号的仍然只有这一条：
- `breakout_short` 在 `release_recent_gate` 下，从显著负值收敛到接近打平。

但这条信号目前不够拿来诚实派生，原因有三：
1. retention 只剩约四分之一，太像切样本美化；
2. 这不是 shared gate，而是高度偏 `breakout_short` 的局部 veto / delay 语义；
3. 同主题的“压缩/释放”残余，现在更像应被吸收到更新的 raw-alpha / event-driven breakout family，而不是再从原 Rank 57 继续长出 `Rank 57b`。

## 4. 最值得改的唯一一刀是什么？
如果硬要说唯一还值得记住的一刀，那也只能是：

- **把 `TTM squeeze release` 从多 setup shared regime gate，进一步收窄成 `breakout_short` 专用的 post-compression release veto / delay note。**

但关键是：**这一刀本质上已经被原 clean replication 审过了。**
它留下的是“实现纪律提示”，不是新的 queue-facing hypothesis：
- 只在 breakout-short 上有一点像样残余；
- 对 long-side setup 不统一；
- 再往前推进就会滑成“为单一 pocket 单独起一个 rank”，不够诚实。

## 5. 是否值得形成新的 derived hypothesis？
**结论：不值得。**

本轮 verdict：`keep_park`

原因：
- 原 park 理由没有被新证据推翻；
- 最近 quant digest / paper seed 里也没有出现足够强、且足够贴近 Rank 57 的新旁证，能把它从“薄残余”抬成新的窄 hypothesis；
- 唯一主修改轴（release_recent squeeze gate）已经被最小 replication 审过，且结果更像 sample-thinning，而不是 stable edge。

## 6. 为什么现在不 draft `Rank 57b`？
因为那会违反 bot6 这条线的审计边界：
- 会把“局部少亏”误包装成“值得新开 queue-facing 假设”；
- 会弱化原 park verdict 的审计意义；
- 也会与当前 desk 上更完整的 breakout / event-driven / raw-alpha 家族发生重复叙事。

更诚实的说法是：
- **Rank 57 留下的是一条实现纪律：压缩态/刚释放态的信息若要用，最多只该作为极窄的 breakout follow-up 注释，而不是再单独立项。**

## 本轮结论（唯一允许输出）
- `verdict = keep_park`
- `original verdict kept = park`
- `park flavor = soft park，但偏硬`
- `single modification axis review = release_recent squeeze gate 已被审过，不足以诚实派生新 hypothesis`

## 对 queue 的影响
- 不新增 `Rank 57b`
- 不改 `docs/TODO.md` 顶部排班
- 只在 `docs/PARK_REFRAME_QUEUE.md` 的 `Recently reviewed` 追加一条短记录

## Git / 提交
- 本轮只做 park-reframe 文档最小写回。
- 未做 commit；默认避免把共享工作区的无关脏文件混入。 
