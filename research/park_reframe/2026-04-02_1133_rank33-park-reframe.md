# 2026-04-02 11:33 UTC｜bot6 park-reframe｜Rank 33

## 0) 本轮选择
- 选定：`Rank 33 / NW + confirmed HL reclaim`。
- 原因：
  - 它属于 `Rank 1~37` 里的已 `park` 条目；
  - 最近 `7` 天未被复盘；
  - 上次 bot6 复盘停在 `soft_reframe_candidate / keep_park` 之间，本轮适合用最近新增的 `turning-point confirmed continuation` 证据再做一次低频判断。
- 本轮目标不是推翻原 `park`，而是判断：**最近新证据够不够把它诚实地压成一条新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：`research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`。

原 rank 被 `park` 的核心原因：
- `endpoint NW` 平滑 + `confirmed HL/LH reclaim` 确实能把部分假 reclaim 压低；
- 但它**没有把收益结构一起救活**；
- 再往上叠 `highbreak` 之后，反而变成高 `no-trade` + 中段口袋型结果，不够诚实地继续当 queue-facing 候选。

关键原始数值（`6bps/side`）：
- `raw_extrema_reclaim`：`mean_total_return≈-1.72%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈49.13%`
- `nw_hl_reclaim`：`mean_total_return≈-1.39%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈47.20%`
- `nw_hl_plus_highbreak`：`mean_total_return≈-8.51%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈20.07%`，`mean_no_trade_ratio≈98.71%`
- 主变体 time-pocket：`bucket_1≈-9.24% / bucket_2≈+5.03% / bucket_3≈-3.95%`

所以原 verdict 不能改写：**它被 park 不是因为“主题完全没信息”，而是因为“过滤更干净了，但还没形成可推进 alpha”。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 3 月下旬时更偏硬。**

为什么还不是 pure hard park：
- 原 rank 至少留下了一点稳定语义：它更像在识别 `bad reclaim / false reclaim`，而不是在提供一个能独立开仓的 reclaim alpha。

为什么又更偏硬：
- 这条残余信息已经很窄；
- 且过去两轮 bot6 已基本把唯一诚实改写轴收敛到 `shared false-reclaim veto / failure-routing hint`；
- 最近新增证据并没有再给出第二条同样干净、且不和既有判断重复的单轴切法。

## 3) 有没有“可救信号”？
- **有，但仍然只有一条：`false reclaim / reclaim-failure` 识别能力。**

也就是说，Rank 33 真正还留下来的不是：
- “NW + reclaim 可以直接做 continuation entry”；

而更像是：
- “若某次 reclaim 质量差，Rank 33 可能更适合帮主 setup 识别它像是假 reclaim / failure path”。

这条可救信号没有消失，但也没有明显变厚。

## 4) 最近新证据有没有改变判断？
本轮主要参考的新证据：
- `research/quant_digests/2026-03-31_2248_turning-point-confirmed-tsmom-alpha.md`

它给出的核心信息是：
- 更值得先测的是 **confirmed turning-point continuation raw alpha**；
- 也就是：先确认结构完成，再把它当作一条新的 trend continuation 主线去测。

这条新证据对 Rank 33 的意义不是“把 Rank 33 救活”，而更像：
- 它把同主题往 **structure-aware trend raw alpha family** 推了一步；
- 但这个 family 的主语已经不再是 Rank 33 那种 `NW + reclaim` 的 shared filter 写法；
- 它更像一条新的 `confirmed turning-point continuation` intake 方向。

所以它**没有推翻**原 `park`，反而进一步说明：
- Rank 33 的 residual value 还是偏 `failure-veto / routing hint`；
- 真正值得新开的是另一条更完整、以 turning-point continuation 为主语的 raw-alpha family，而不是把旧的 Rank 33 再硬包成 `Rank 33b`。

## 5) 最值得改的唯一一刀是什么？
**唯一主修改轴仍然只有一条：把 standalone `NW + confirmed reclaim` entry，降级成 `shared false-reclaim veto / failure-routing hint`。**

更具体地说：
- 不再让 Rank 33 自己触发新单；
- 只在现有 setup 已触发时，额外判断这次 reclaim 更像 `clean continuation` 还是 `false reclaim / failure path`；
- 第一刀若以后真重开，也只能做 `baseline vs veto-only / failure-routing hint`，不能顺手叠第二轴。

## 6) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` audit 意义仍然成立，不能改写；
2. 最近新证据虽然说明“结构确认后的 continuation 主题未死”，但它更像**新的 raw-alpha family**，不是旧 Rank 33 的自然窄派生；
3. Rank 33 唯一诚实残余，仍只是 `false-reclaim veto / failure-routing` 这一条，而这点在过去几轮已经被充分收敛；
4. 现在硬写 `Rank 33b`，很容易只是把既有 `soft_reframe_candidate` 重述一遍，而不是新增真正可审计的新假设。

## 7) trade on / trade off（仅作为 why-not-draft 说明）
若未来真要重开，仍只能按下面这条唯一轴来理解：
- `trade on`：把它迁移成 shared false-reclaim veto / failure-routing 提示，减少把坏 reclaim 误读成 continuation 的次数；
- `trade off`：trade density 会下降，而且极容易退化成“砍单美化”；若没有严格冻结的 baseline A/B，这条线就不该重开。

但今天的新证据还不足以把这段 why-notion 升级成新的 queue-facing draft。

## 8) 本轮结论
- `keep_park`
- 补充口径：`soft park，但更偏硬；最近新增的 turning-point confirmed continuation 证据更像新的 structure-aware trend raw-alpha family，不足以把旧的 Rank 33 / NW+reclaim 诚实派生成新的窄修改轴`

## 9) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动，且仓库长期存在与本轮无关的共享脏文件风险，避免混提。
