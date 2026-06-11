# 2026-04-08 12:45 UTC · Rank 4 pairs threshold-governance / dynamic-sizing first verdict background sync

## 本轮执行对象
- target: `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
- action: 作为当前首个 `pending` fresh intake，判断 `pairs threshold-governance / dynamic-sizing` 这条旧 `Rank 4` residual 是否已足够从 park 语义收敛成新的正式 raw alpha intake。

## 判定口径
本轮不是重做原始 `Rank 4 / crypto pairs trading / stat-arb` 的 clean replication，也不是替 pairs 主题直接开一条新 family。

本轮只回答一件事：

> 把旧 `spread z-score overlay` 读法进一步收窄成 `pairs threshold-governance / dynamic-sizing` 后，它有没有形成一条单一、queue-facing、可 clean-room 描述的新 raw alpha 宿主？

## 本轮复核到的关键事实
1. 原 `Rank 4` 被 park 的主因没有改变：直接把 frozen-beta spread z-score 写成 pairs alpha 时，主要 pair 在成本后整体为负；这条 direct-entry 主线已被审计关闭。
2. `2026-03-24` 新增的两条证据确实说明 pairs 主题没有“彻底没信息”，但它们共同指向的是一条 **full-stack family**：
   - `threshold / basket governance` 决定 pairs 是否还能留下 pocket；
   - `dynamic sizing` 更像风险预算与执行骨架，而不是 raw alpha 主体本身。
3. 这两条新增证据都不是“旧 Rank 4 上唯一的一刀”——它们要求同时重写 entry/exit、pair basket、成本治理、sizing 与执行语义，已经超出旧 rank residual 的单轴 clean-room 收敛边界。
4. 现有 residual 仍没有压出新的独立宿主：
   - 没有独立 pocket 已经被新对象唯一占有；
   - 没有独立执行边界能把它和既有 pairs / overlay family 分开；
   - 没有独立 clean-room 主语，能把它从“需要完整治理的新 family”压缩成单一 raw alpha intake。
5. 因此更诚实的读法仍是：`Rank 4` 的残余价值主要证明 **pairs 主题若要重开，应另起完整新 family**；但这不等于当前这个 residual 已经形成新的正式 intake。

## first verdict
**`Rank 4` 的 `pairs threshold-governance / dynamic-sizing` residual 虽说明 pairs 主题更像需要完整治理的新 family，但仍未压出单一 queue-facing 主语、独立 clean-room 宿主与独立 raw alpha pocket，因此本轮 first verdict 收口为 `background / P0`。**

## 对 runtime 的直接写回
- `Fresh intake slot.latest_result` 更新为本轮 `background / P0` 结论。
- `Fresh intake slot.current_target` 顺延到 `research/park_reframe/2026-04-08_0820_rank84-park-reframe.md`。
- `Background pool.latest_parked` 同步写回本轮结论。
- `cycle_plan` 第 1 条写成 `done`，并填入正式 `result`。

## 为什么这次不分配新 Rank
因为 verdict 不是 `keep_P1 / promote_P2 / promote_P3`，而是直接收口到 `background / P0`；它没有形成新的正式 raw alpha intake，所以不应新开号码。

## 本轮结果（供 state 引用）
- result: `Rank 4：pairs threshold-governance / dynamic-sizing` residual 虽说明 pairs 主题更像需要完整治理的新 family，但仍未形成单一 queue-facing 主语与独立 raw alpha intake，因此本轮 first verdict 收口为 `background / P0`
- status: `done`
