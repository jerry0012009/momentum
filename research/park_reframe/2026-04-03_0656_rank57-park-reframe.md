# 2026-04-03 06:56 UTC · Rank 57 park reframe

## Selected rank
- `Rank 57`
- selection note: 本轮按 `50~79` 号段优先，从已 `park` 的 `50+` rank 里低频挑 1 条。`Rank 53` 刚在过去 7 天内复盘过，而 `Rank 57` 自 `2026-03-18` 被压回 `park` 后尚未被 bot6 正式复盘；同时最近新增了 `2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`，值得判断一次：它是在救旧 `Rank 57`，还是只是在把压缩主题推向新的 raw-alpha family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_1432_rank57-source-intake.md`
- `research/optimization_loop/2026-03-18_1451_rank57-clean-replication-park.md`

原 `Rank 57` 被 park 的原因没有变：它把 **TTM squeeze release** 写成一个横跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared regime gate，但最小 clean replication 只证明了“在个别 setup 上砍样本后少亏”，没有证明它能形成稳定、跨 setup 的 queue-facing gate。

冻结版最关键结果（`6bps/side`）：
- `ema_psar_long`: `base≈-3.68% -> release_recent≈-2.94%`，但 `retention≈13.33%`
- `fib_retest_long`: `base≈+1.17% -> release_recent≈+0.30%`
- `breakout_short`: `base≈-3.55% -> release_recent≈-0.10%`，但 `retention≈25.22%`
- 时间稳定性与 `release 1~4 bars` 参数邻域都没给出干净、跨 setup 统一的 pocket

翻成人话：
- squeeze/release 主题不是完全没信息；
- 但把它写成“所有 setup 共用的 shared regime gate”并不成立；
- 原审计意义必须保留：**失败对象是“TTM squeeze release 作为跨 setup shared gate 值得继续占用 scout 预算”这件事，不是压缩→释放主题永远无效。**

## Hard park or soft park?
- 本轮判断：`soft park，但对原 shared-gate 读法已明显偏硬`

为什么不是 pure hard park：
- `breakout_short` 的 `release_recent_gate` 确实比 base 少亏很多；
- 说明“压缩后释放”这件事在 breakout family 里可能还有残余信息。

为什么又已明显偏硬：
- 改善主要集中在单一 setup，而且靠大幅降样本实现；
- `fib_retest_long` 与 `ema_psar_long` 没形成统一增益，shared gate 这层角色基本已经被审计掉了。

## Any salvage signal?
有，而且这次不是纯粹的新 family 漂移；它确实给旧 `Rank 57` 留下了一条更窄、也更诚实的角色改写方向。

本轮最 relevant 的新增证据：
- `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
- `research/optimization_loop/2026-03-18_1451_rank57-clean-replication-park.md`

两者合起来的关键信号是：
1. 原 `Rank 57` 自己已经暴露出明显 **setup asymmetry**：残余主要留在 `breakout_short`，不是 shared；
2. 新 digest 又把同主题收窄成一个更像 **breakout / compression expansion alpha body** 的读法：先有压缩，再看突破，不必强求它横向服务所有 setup；
3. 因而这次新增价值，不只是“另起炉灶做新 raw alpha”，也可以诚实地读成：`Rank 57` 最自然的一刀，是从 **跨 setup shared gate** 降级成 **breakout-family-local admission package**。

## Single best cut
如果只保留唯一一刀，本轮最值得改的是：

> **demote symmetric TTM squeeze release shared gate into a breakout-family-local pre-break compression admission**

也就是：
- 不再让 `Rank 57` 试图给 `ema_psar_long / fib_retest_long / breakout_short` 全部共用；
- 只保留它在 breakout family 里的残余信息：当市场先处于显著压缩，再发生向外突破时，才允许把这次 break 当成更有资格的 continuation / expansion 候选；
- 第一刀优先写成 `breakout_short` 的局部 admission package，而不是再回头救长侧或 shared overlay。

这条一刀仍然保留原 `park` 审计意义，因为它承认：
- 原来的 shared-gate 结论没有被推翻；
- 只是把还活着的残余信息收缩到一个更小、更对题的宿主里。

## Derived hypothesis?
- 结论：`derived_hypothesis_drafted`
- 新提案：`Rank 57b`

为什么这次值得 draft：
1. 原 `Rank 57` 的 failure 已经把“shared across setups”这层错位审计清楚；
2. 残余 pocket 不再是模糊的“可能有点用”，而是集中在 breakout/compression 这一条语义上；
3. `2026-03-30` 的 bottom-quartile BB compression digest 给了同主题、同方向的外部旁证，足以把它收敛成一个单轴窄提案；
4. 这条派生没有推翻原 `park`，只是把主题从“shared gate”改写成“breakout-family-local admission”。

## Drafted derived hypothesis
- `proposed_rank`: `Rank 57b`
- `source_rank`: `Rank 57`
- `single modification axis`: `demote symmetric TTM squeeze release shared gate into a breakout-family-local pre-break compression admission`
- `trade on`: `不再把 squeeze release 同时套到 ema_psar_long / fib_retest_long / breakout_short；保留 breakout family 的原始 break 事件为主语，只在 pre-break 明确处于压缩状态（第一轮优先最小版 trailing BB-width bottom-quartile / squeeze-on）时放行 breakout_short admission；第一轮只测 baseline breakout_short vs compression-admission，不偷带 200SMA / volume spike / funding / 新 exit 第二轴`
- `trade off`: `放弃“一个 squeeze gate 横向服务所有 setup”的原 Rank 57 读法，换取更诚实的 breakout-family-local 角色；代价是 trade density 会下降，而且改善仍可能只是来自砍样本，因此第一轮必须 strict A/B，并报告 trade retention，不允许顺手救 ema/fib 或叠第二层 regime`
- `why now`: `原 clean replication 已经把 Rank 57 的 setup asymmetry 暴露得很清楚：只有 breakout_short 留下接近打平的残余，而 2026-03-30 的 bottom-quartile compression breakout digest 又给出同主题的外部旁证，说明压缩主题更像 breakout-family-local admission，而不是 shared gate`
- `suggested initial state`: `source intake / clean replication next`

## Final verdict
- `derived_hypothesis_drafted`
- original verdict kept: `park`
- short note: `soft park，但对原 shared-gate 读法已明显偏硬；压缩主题的残余主要集中在 breakout family，且有 bottom-quartile compression breakout 新旁证，因此本轮只 draft 一条更窄的 Rank 57b（把 symmetric squeeze-release shared gate 降级成 breakout-family-local pre-break compression admission）`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在大量共享脏文件，且 `docs/PARK_REFRAME_QUEUE.md` 已有并发修改风险；本轮只做最小必要文档改动，避免混提。
