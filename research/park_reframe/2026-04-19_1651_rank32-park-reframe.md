# 2026-04-19 16:51 UTC · Rank 32 park-reframe（bot6）

## 本轮对象
- `Rank 32 / EMA structure vs MA slope direction gate`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 为什么选这条
- 本轮只处理 `Rank 1~37` 的 1 条已 `park` rank。
- `Rank 32` 上次复盘是 `2026-04-12 08:56 UTC`，到本轮已超过 7 天窗口，符合低频复盘约束。

## 1) 原 rank 为什么 park？
原始 clean replication（`2026-03-17_1123_rank32-clean-replication-park.md`）的核心审计结论没变：
- `ema_cross_only` 成本后明显为负；
- `ema_cross_plus_slope_floor` 能留下正 pocket；
- 但原主写法里的 `spread-mid reclaim` 把样本压得过稀（no-trade 比例极高），不够 queue-facing 可交易厚度。

所以 `Rank 32` 被 park 不是因为 EMA slope 主题“完全没信息”，而是因为原命题职责层（尤其 reclaim 约束）与样本密度不诚实。

## 2) 它更像 hard park 还是 soft park？
**结论：`soft park`，但已接近 `hard park with consumed residual`。**

原因：
- soft 的部分：`slope floor` 这条残余信号曾被验证过有信息量；
- 接近 hard 的部分：这条唯一自然 rescue 已被 `Rank 32b` 消费，且 `2026-04-09_1532_rank32b_fresh_intake_background_already_consumed.md` 已把其收口为 `background / P0 / already consumed`。

## 3) 有没有“可救信号”？
**有，但不是新的。**
- 可救信号仍是同一条：`EMA cross + aligned slope floor`。
- 这条信号已经被既有 `Rank 32b` 提炼并消费，不再构成新的派生空间。

## 4) 最值得改的唯一一刀是什么？
若只允许一刀，仍只有：

**去掉 `spread-mid reclaim`，仅保留 `EMA cross + aligned slope floor`。**

但这就是既有 `Rank 32b`，不属于本轮可再派生的新轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮维持 `keep_park`。**

理由：
1. 唯一自然修改轴已被 `Rank 32b` 消费；
2. `Rank 32b` 已被 runtime 收口为 `background / P0`；
3. 4 月 19 日新增的 `EMA walk-forward + double-OOS admission` 证据（`2026-04-19_1135_ema-wfo-double-oos-trend-alpha.md`）继续说明：EMA 主题若要再开，更像新的完整 trend shell / admission protocol 宿主，而不是旧 `Rank 32` 的 `Rank 32c`。

## 单轮模板回答（归档）
- 原 rank 为什么 park：原写法把可交易密度压得过稀，职责层不诚实。
- hard/soft：soft park（接近 hard with consumed residual）。
- 可救信号：有，且仅有 `slope floor`，但已被 32b 消费。
- 唯一一刀：移除 reclaim，保留 slope floor。
- 是否派生新假设：否，本轮 `keep_park`。

## Final verdict
- `keep_park`
- note：`原 park 保留；Rank 32 的唯一自然残余已被既有 Rank 32b 消费并在 runtime 收口为 background/P0；新增 EMA double-OOS 证据指向新的完整 trend-shell admission 宿主，而非旧 Rank 32 再派生。`

## 文件动作
- 新增：本日志
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 提交
- 本轮未提交（工作区存在无关脏文件，按最小改动原则仅做文档增量）。
