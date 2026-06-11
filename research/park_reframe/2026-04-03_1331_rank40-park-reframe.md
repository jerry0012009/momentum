# 2026-04-03 13:31 UTC · Rank 40 park reframe

## Selected rank
- `Rank 40`
- selection note: 本轮按 `50~79 -> 80~110 -> 1~24 -> 25~49` 低频轮转，前几轮已连续覆盖 `50+ / 80~110 / 1~24`，因此这轮切到 `25~49` 段。`Rank 40` 近 7 天内尚未被 bot6 单独复盘；同时它属于典型的 `EMA pullback` 旧 parked 线，而最近新增的 pullback-quality / post-trigger verdict / EMA role-split 证据，正好可以再判断一次：这些新旁证是在救旧 `Rank 40`，还是只是在把主题推向更共享、也更诚实的新骨架。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-17_1806_rank40-ema-pullback-intake.md`
- `research/optimization_loop/2026-03-17_1827_rank40-clean-replication-park.md`

原 `Rank 40` 被 park 的原因没有变：它把 **three-EMA trend continuation + pullback swing stop + 2.06R target** 当成可直接 queue-facing 的 standalone continuation alpha，但最小 clean replication 没把这条线救活。

冻结版最关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`, `6bps/side`）：
- 主变体 `33/165/365`：`mean_total_return ≈ -13.32%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 59.0`
- `mean_no_trade_ratio ≈ 83.79%`
- 时间桶：`bucket_1 ≈ -11.47%`, `bucket_2 ≈ +6.64%`, `bucket_3 ≈ -8.00%`
- 邻近参数也没把它救回来：
  - `20/100/200 @ 6bps ≈ -0.19%`, `positive_asset_ratio = 1/3`
  - `40/200/440 @ 6bps ≈ -8.51%`, `positive_asset_ratio = 1/3`

翻成人话：
- 原问题不是“只差一组更对的 EMA 参数”；
- 而是这条 **direct three-EMA pullback entry** 在成本后、跨资产、跨时间口袋上都不够厚；
- 甚至相对最宽松邻近参数，也只做到“少亏”，没形成可继续推的诚实主体。

所以原 `park` 的审计意义必须保留：**失败对象是“让三 EMA 回踩自己承担 standalone 触发器角色”这件事，不是 pullback / trend-continuation 主题整体死亡。**

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 pure hard park：
1. 原 clean replication 并非所有邻近口径都同样灾难；`20/100/200` 至少把亏损压到接近打平；
2. 说明“顺势回踩”这个大主题本身还有信息，不像完全没有任何 residual value；
3. 原 source 也比更粗糙的 intake 多了一点 execution honesty：至少把 `swing stop + fixed R target` 讲清了。

为什么又已明显偏硬：
1. 真正留下的信息越来越不像“再调一组 EMA 参数”，而像 **把 EMA 降级成 context / score / verdict layer**；
2. 最近新增的旁证更像在吸收 `Rank 40` 的主题残余，而不是支持一个新的、仍属于它自己的 direct-entry 派生；
3. 若继续把它写成 `EMA pullback 自己下单`，大概率只是在重复审计过的失败对象。

## Any salvage signal?
有，但更像“主题外流”，不是“旧 rank 还能再诚实窄救一刀”。

本轮最 relevant 的新增旁证：
- `research/quant_digests/2026-03-18_1151_pullback-quality-score-gate.md`
- `research/quant_digests/2026-03-20_0742_pullback-two-sided-window-verdict.md`
- `research/quant_digests/2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`

这些新证据共同在说：
1. **EMA / pullback 主题没死**；
2. 但更诚实的写法不是“再给三 EMA pullback 一次 direct-entry 预算”；
3. 更像：
   - 把回踩写成 `trend + depth + volume + reclaim` 的 **pullback-quality score**；
   - 或把 raw trigger 改成 `scan-only`，让真正入场交给 **pullback → success/failure/timeout** 的短窗口 verdict；
   - 或把 EMA 明确拆成 **macro gate + momentum confirm + fast exit**，让主触发回到 breakout / other base event。

换句话说：
- 可救信号存在；
- 但它在救的是“pullback confirmation / EMA role assignment”这个更共享的骨架；
- 不是在救旧 `Rank 40` 这条 `three-EMA continuation direct entry`。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向是：

> **demote direct three-EMA pullback entry into a shared pullback-quality / post-trigger verdict layer**

也就是：
- 不再让 `EMA fast/trend/limit + reclaim` 自己直接触发下单；
- 改成把 EMA 只保留在 `trend context / momentum confirm / fast exit`，而真正的 entry 交给更窄的 pullback-quality score 或 post-trigger verdict。

但这刀本轮**不够诚实地属于 `Rank 40`**，原因有三：
1. 它已经把主语从“three-EMA pullback alpha”改成“shared confirmation skeleton”；
2. 它和近期 digest 里的共享 pullback / breakout / EMA role-split 主题高度重合；
3. 若硬写成 `Rank 40b`，会模糊原失败对象边界——看起来像在救旧 rank，实际是在借更共享的新骨架换壳续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次仍不值得 draft `Rank 40b`：
1. 原 `park` verdict 没被推翻；
2. 最近新增的最强旁证都在把主题推向 **shared pullback-quality / post-trigger verdict / EMA role-split**，而不是支持原 `three-EMA direct-entry` 的 residual pocket；
3. 这条唯一看起来像样的修改轴，实际上已经超出旧 rank 的诚实边界；
4. bot2 若未来要认领，更诚实的做法应是直接认领新的 shared pullback / breakout confirmation intake，而不是把它挂回 `Rank 40` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；最近新增的 pullback-quality / two-sided verdict / EMA role-split 证据说明，Rank 40 的残余价值更像 shared confirmation skeleton，而不是旧 three-EMA pullback direct-entry 的诚实窄派生，不足以 draft Rank 40b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动；且仓库长期存在共享脏文件风险，避免混提。
