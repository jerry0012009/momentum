# 2026-04-02 07:12 UTC — Rank 30 park reframe review

## 结论
- `source_rank`: `Rank 30`
- `verdict`: `keep_park`
- `original verdict kept`: `park`
- 一句话：**Rank 30 仍是 soft park（偏硬）：新增的 MA/breakout × bubble-state 证据更像新的 family-level trend raw-alpha intake，不足以在既有 Rank 30b 之外再诚实派生 Rank 30c。**

## 为什么本轮看它
- 本轮按低频轮转从已 park 条目里只处理 1 条。
- `Rank 30` 上次 park-reframe 复盘是 `2026-03-22 09:03 UTC`，已超过 7 天。
- 最近确有新证据（`2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`），具备复盘条件。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_1029_rank30-clean-replication-park.md`：
- `raw_corridor_breach @ 6bps/side`：`mean_total_return≈-10.73%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈86.11%`
- `breach_plus_reclaim_hold @ 6bps/side`：`mean_total_return≈-7.33%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈82.39%`
- 结论：突破主题并非全无信息，但确认层不足以把假突破和可交易突破分开；成本后跨资产仍全负，所以 park。

## 它更像 hard park 还是 soft park
- **soft park（偏硬）**。
- 软：`breach_plus_reclaim_hold` 相比 raw breach 有一致的“少亏”改善。
- 偏硬：改善仍停在减亏层，尚未出现可 admission 的正向 after-cost 资产覆盖。

## 有没有“可救信号”
有，但不足以再开新派生：
1. 新论文证据确认 `MA / breakout` 主题在加上 regime/cost 骨架时可作为独立 raw-alpha family。
2. 这说明 breakout 主题“未死”，但它支持的是**更完整的新 family**，不是对旧 `Rank 30` 的窄修补。
3. 对 Rank 30 本体而言，核心 blocker 仍是 post-breach 假突破率过高；该 blocker 与既有 `Rank 30b`（event-anchored VWAP hold/reclaim）仍更直接匹配。

## 最值得改的唯一一刀是什么
- 本轮仍维持：**唯一值得保留的一刀是既有 `Rank 30b`（breach-event anchored VWAP hold/reclaim）**。
- 不建议把这轮新证据再改写成 `Rank 30c`，否则会从“窄 reframe”滑向“换题到新 family-level trend raw alpha”。

## 是否值得形成新的 derived hypothesis
- **不值得。**
- 本轮结论：`keep_park`。

## 最终判断（固定问答）
- 原 rank 为什么 park？
  - 因为 clean replication 下假突破率高、成本后跨资产全负，确认层不足。
- 更像 hard 还是 soft？
  - soft park（偏硬）。
- 有可救信号吗？
  - 有，但更支持新 family，不支持再派生 Rank 30c。
- 唯一一刀是什么？
  - 继续只保留既有 Rank 30b（event-anchored VWAP hold/reclaim）。
- 是否形成新的 derived hypothesis？
  - 否，`keep_park`。

## 本轮文件改动
- 新增本日志：`research/park_reframe/2026-04-02_0712_rank30-park-reframe.md`
- 更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`

## git / 提交
- 本轮仅做最小必要文档改动。
- 未做 commit（工作区存在大量无关脏文件，避免混提）。
