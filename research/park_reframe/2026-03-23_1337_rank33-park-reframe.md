# 2026-03-23 13:37 UTC｜bot6 park-reframe｜Rank 33

## 0) 本轮选择
- 当前 `Rank 1~37` 的 parked rank 近 7 天已被大面积轮过；本轮不重复看“纯无新证据”的旧案。
- 选定：`Rank 33 / NW + confirmed HL reclaim`。
- 原因：虽然它在 `2026-03-22 00:28 UTC` 已被 bot6 复盘过，但今天出现了两条与它**同主题、且足够窄**的新旁证：
  1. `2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`：新证据继续反对把 retest / reclaim 写成独立硬门或独立 alpha，更像 phase-score / veto 层；
  2. `2026-03-23_0312_ft-nft-killzone-postbreak-router.md`：新证据把 post-break path 明确写成双路由 verdict 骨架，强化“failure / false reclaim 更像 verdict/filter，不像 standalone entry”。
- 因此本轮不是推翻原 `park`，而是低频判断：**这些新证据够不够把 Rank 33 从 soft candidate 推进成新的 derived hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：`research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`。

原 rank 被 park 的核心原因：
- `NW` 平滑与 `confirmed HL/LH reclaim` 的确能降低假 reclaim；
- 但它**没有把收益结构一起救活**，而且典型地呈现 `中段亮、前后两端不站住` 的 time-pocket。

关键原始数值（6bps/side）：
- `raw_extrema_reclaim`：mean_total_return≈`-1.72%`，positive_asset_ratio=`1/3`，false_reclaim_ratio≈`49.13%`
- `nw_hl_reclaim`：mean_total_return≈`-1.39%`，positive_asset_ratio=`1/3`，false_reclaim_ratio≈`47.20%`
- `nw_hl_plus_highbreak`：mean_total_return≈`-8.51%`，positive_asset_ratio=`1/3`，mean_no_trade_ratio≈`98.71%`，false_reclaim_ratio≈`20.07%`
- 主变体 time-pocket：`bucket_1≈-9.24% / bucket_2≈+5.03% / bucket_3≈-3.95%`

所以原 verdict 必须保留：`park / evidence pool`。

## 2) 它更像 hard park 还是 soft park？
- **仍然更像 soft park。**

理由：
- 它不是“主题彻底没信息”；
- 真正留下来的信息是：**Rank 33 更擅长识别 false reclaim / bad reclaim，而不是提供可独立部署的 reclaim alpha**。
- 但这点信息目前仍偏弱，离“值得立一个 queue-facing 新 rank”还有距离。

## 3) 有没有“可救信号”？
有，但仍然只有一条：
- **可救信号 = 它对 `false reclaim` 的过滤价值。**

今天的新旁证并没有把它救成 standalone：
- `ORB phase-state / retest→bounce + score` 说明：回踩/重夺更像 phase score，不像独立硬门；
- `FT/NFT 双路由` 说明：post-break 之后更该先分“延续 vs 失败”两条路，而不是默认把 reclaim 直接当 continuation entry。

这两条旁证都在强化同一个方向：
- Rank 33 最自然的职责不是自己开仓；
- 它更像**给现有 setup 做 false-reclaim veto / failure routing 提示**。

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把 Rank 33 从 standalone `NW + reclaim` entry，降级成 `shared false-reclaim veto / failure-routing hint`。**

更具体地说：
- 不再让 `NW + confirmed HL/LH reclaim` 自己直接触发新单；
- 只在现有 setup 已经触发时，额外判断这次 reclaim 更像 `clean reclaim` 还是 `false reclaim / failure path`；
- 第一刀若将来真要验证，也只能做：`baseline vs veto-only`，不偷带第二轴。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 这轮新证据虽然继续支持“Rank 33 应降级成 failure/filter 角色”，但这件事在 `2026-03-22` 的 `soft_reframe_candidate` 里已经基本成立；
2. 今天的新证据主要是在**收紧角色边界**，不是给出新的、足够独立的一刀；
3. 若现在硬写成 `Rank 33b`，很容易只是把已有 `soft_reframe_candidate` 重新包装一遍，而不是新增真正可审计的单轴假设。

因此更诚实的判断是：
- 保留原 `park` verdict；
- 保留 `Rank 33` 的 `soft_reframe_candidate` 性质；
- 但**本轮不升级为 `derived_hypothesis_drafted`**。

## 6) trade on / trade off（仅作为 why-not-draft 说明）
如果未来真要重开，唯一允许的读法仍应是：
- `trade on`：把 false-reclaim 识别能力迁移成 shared veto / failure-routing 层，减少把坏 reclaim 误当 continuation；
- `trade off`：trade density 下降，而且极容易变成“砍单美化”；若不能对冻结 setup 做 strict A/B，这条线就不应重开。

但今天的新证据还不足以把这段 why-notion 压成新的 queue-facing draft。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park；今天的新证据只够把 Rank 33 的 residual value 继续收紧成 false-reclaim veto / failure-routing hint，不足以把既有 soft_reframe_candidate 升级成新的 derived hypothesis`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：该仓库长期存在与本轮无关的共享脏文件风险；本轮只做最小文档改动，避免混提。