# 2026-03-30 00:19 UTC｜bot6 park-reframe｜Rank 33

## 0) 本轮选择
- 选定：`Rank 33 / NW + confirmed HL reclaim`
- 轮转说明：`50+` 与 `80~110` 号段最近已连续覆盖；`1~24` 近 7 天也已大面积复盘。本轮回到 `25~49`，优先挑一条**虽在 7 天内看过、但新增证据足以重新收紧边界**的 parked rank。
- 为什么是它：`Rank 33` 上次 park-reframe 在 `2026-03-23 13:37 UTC`，当时结论是 `soft_reframe_candidate`，残余价值只够收敛到 `false-reclaim veto / failure-routing hint`。过去 7 天又新增两条更像同主题上位 raw-alpha / verdict family 的证据：
  1. `2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`：把 post-break path 明确抬升为 **event-driven overshoot raw alpha + abnormal-regime veto**，说明真正值得开的更像独立事件时钟 raw alpha，而不是把 `NW reclaim` 再包装成 queue-facing 窄 rank；
  2. `2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`：把短窗方向预测更诚实地写成 **thresholded state machine / abstain**，进一步支持“先做 verdict / abstain 层”，而不是把 reclaim 本身继续当 standalone entry。
- 本轮任务因此不是推翻原 `park`，而是判断：**这些新证据是否足以把 Rank 33 从 parked residual 升成新的窄 derived hypothesis。**

## 1) 原 rank 为什么 park？
原始审计文件：`research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`

原 rank 被 park 的核心原因没变：
- `NW` 平滑与 `confirmed HL/LH reclaim` 的确能把 `false reclaim` 比例压低一点；
- 但它**没有把收益结构一起救活**，而且一旦再叠 `highbreak`，会明显掉进 `中段亮、前后两段都不站住` 的 time-pocket。

关键原始数值（`6bps/side`）：
- `raw_extrema_reclaim`：`mean_total_return≈-1.72%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈49.13%`
- `nw_hl_reclaim`：`mean_total_return≈-1.39%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈47.20%`
- `nw_hl_plus_highbreak`：`mean_total_return≈-8.51%`，`positive_asset_ratio=1/3`，`mean_no_trade_ratio≈98.71%`，`mean_false_reclaim_ratio≈20.07%`
- 主变体 time-pocket：`bucket_1≈-9.24% / bucket_2≈+5.03% / bucket_3≈-3.95%`

所以原结论必须保留：`Rank 33 = park / evidence pool`。

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 2026-03-23 更偏硬。**

为什么不是 hard park：
- 它确实留下了一点信息量——`false reclaim / bad reclaim` 的识别能力比直接裸 reclaim 更有内容。

为什么又更偏硬：
- 新证据没有把这点 residual value 往 `Rank 33b` 推近，反而更明确地说明：真正活下来的应该是**上位的 event-driven path verdict / abstain / raw-alpha family**，不是原 Rank 33 自己再诚实派生一条 queue-facing 窄线。

## 3) 现有证据里有没有“可救信号”？
- **有，但仍然只有一条：`false reclaim / post-break failure` 识别能力。**

具体说：
- 原 clean replication 已说明：`NW` 的贡献更像把 reclaim 判得更“干净”，不是把收益曲线救成可部署 alpha；
- `2026-03-28` 的 DC digest 又把同主题抬高成：**事件触发后去吃 overshoot，本体失败时靠 abnormal regime / reverse confirmation 退出**；
- `2026-03-29` 的 GMADL digest 则强调：短窗方向信号最诚实的写法是 `thresholded long/short/flat`，而不是“有 reclaim 就开单”。

换成人话：
- `Rank 33` 剩下的不是“这套 reclaim 可以救活”；
- 剩下的是“它提醒你，很多 reclaim 更像应被判成 abstain / failure-routing，而不是 continuation entry”。

## 4) 最值得改的唯一一刀是什么？
- **唯一主修改轴仍然只有一条：把 Rank 33 从 standalone `NW + reclaim` entry，降级成 `shared false-reclaim veto / failure-routing hint`。**

也就是：
- 不再让 `NW + confirmed HL/LH reclaim` 自己直接触发新单；
- 只在现有 setup 已触发时，额外判断这次 reclaim 更像 `clean reclaim` 还是 `false reclaim / failure path`；
- 如果未来真要测，第一刀也只能是 `baseline vs veto-only / abstain-only`，不能顺手叠第二轴。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 这轮新增证据虽然是新证据，但它们主要在证明：`Rank 33` 的残余价值应继续上移到 **event-driven verdict / abnormal-regime veto / thresholded abstain** 这类更高层 family；
2. 它们并没有提供一个新的、足够 queue-facing、且仍明显属于 `Rank 33` 的**单一新切口**；
3. 若此时硬写 `Rank 33b`，本质上会是把既有 `soft_reframe_candidate` 换个说法重写一次，而不是新增 genuinely new 的单轴假设。

## 6) 如果勉强重开，trade on / trade off 会是什么？（why-not-draft）
- `trade on`：把 `false reclaim` 的识别能力迁移成 shared veto / abstain / failure-routing 层，尽量少把坏 reclaim 误读成 continuation。
- `trade off`：trade density 会下降，而且极容易只是靠砍单美化；如果不能对冻结 setup 做 strict A/B，它就不配重开。

但这段 today 仍只够当 **why-not-draft** 说明，不够升级成新的 `derived_hypothesis_drafted`。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park，但比 2026-03-23 更偏硬；3/28 的 DC overshoot / abnormal-regime 新证据与 3/29 的 thresholded directional state-machine 新证据都说明，Rank 33 的 residual value 更像应上移到 event-driven verdict / abstain raw-alpha family，而不是继续诚实派生 Rank 33b`

## 8) 文件动作
- 新增：本轮日志（本文件）
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：仓库存在共享脏文件风险；本轮只做最小文档改动，避免混提。
