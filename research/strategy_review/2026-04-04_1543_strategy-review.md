# Strategy Review — 2026-04-04 15:43 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1534_rank330_p2_admission_cross_asset_failed_drop_to_background.md`
  - `research/optimization_loop/2026-04-04_1428_rank330_survivor_followup_canonical_supertrend_promote_p2.md`
  - `research/optimization_loop/2026-04-04_1347_rank328_p2_rescope_to_p1_missing_unified_overlay_replay_board.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1430_strategy-review.md`
- 最近新的 digest / alpha 报告：
  - `research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
  - `research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`
  - `research/quant_digests/2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md`
  - `research/quant_digests/2026-04-04_1335_deribit-iv-calendar-spread-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 头是**：`research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`。
- 原因：`Rank 330` 已经完成从 fresh intake → survivor → `Active P2` → `background/P0` 的完整前排链条；当前没有残留的 `P3 / P2 / P1` 前排动作，因此按 policy 默认顺序，fresh intake 头应顺延到最近新的 alpha 报告，而不是继续停在已收口对象或回头拉旧候选。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且那唯一一次 follow-up 已经用完。**
- 上一条 fresh intake 是 `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`，已被分配为 `Rank 330`。
- 在 `research/optimization_loop/2026-04-04_1428_rank330_survivor_followup_canonical_supertrend_promote_p2.md` 中，这次唯一 follow-up 明确回答了关键 blocker：repo 当前实现几乎冻结了 SuperTrend flip，但 canonical 口径在 `BTCUSDT 15m recent 90d` 上恢复到 `bull_flip=146 / bear_flip=146`，并重新产生 `69` 个 long 与 `87` 个 short 壳信号。
- 这次 follow-up 因此是值得的：它把 `Rank 330` 从 `P1` 推进到 `Active P2`。但随后在 `research/optimization_loop/2026-04-04_1534_rank330_p2_admission_cross_asset_failed_drop_to_background.md` 中，`effectiveness / cross-asset` admission 已明确失败，故该对象现在已诚实收口到 `background/P0`，不能再占 survivor 槽位。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最新证据已经把 `Rank 330` 从 `Active P2` 直接收口到 `background/P0`：canonical 化后虽恢复 firing density，但 `BTC/ETH/SOL/BNB 15m recent 90d` 上 aggregate `gross_return=+6.23%`、`net_return=-48.62%`（每币 `10k` 口径），且成本后四币全负，因此不存在仍应留在前排的明确 P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排对象不存在无 rank 的 `P1 / P2 / P3` 槽位对象；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有明确 `Active P2`。
- 最近唯一需要检查的前排对象是 `Rank 330`；desk review 并未表明它已足够进入 paper trade，反而已清楚表明它应直接 `drop_to_background`。
- 因此本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级，也不应继续把任何已收口对象伪装成开放式研究。

## 本轮排班结论
当前 `P3 / P2 / P1` 全为空，合法默认顺序已经自然切回 fresh intake；因此本轮 `cycle_plan` 应全部由**具体 fresh intake** 组成，且按最近新的 strategy repo / paper / alpha 报告排序：

1. `research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
2. `research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`
3. `research/quant_digests/2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md`
4. `research/quant_digests/2026-04-04_1335_deribit-iv-calendar-spread-alpha.md`

这样排的理由：
- `Paper launch queue` 为空，不能凭空制造接线动作；
- `Active P2` 为空，不能把已掉回 background 的对象继续前排化；
- `Surviving candidate` 为空，说明不存在锁定唯一 follow-up 的对象；
- 因此前排链条已诚实收口，当前预算应该直接切到新的具体 intake，而不是继续停留在旧的 12:26 / 13:14 候选。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 改为新的 pending 头：`research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
- 保留 `Rank 330` 已完成前排链条并已回 `background/P0` 的最新 runtime truth
- 将 `cycle_plan` 改写为 4 条具体 fresh intake：1525 → 1455 → 1406 → 1335

## 本轮结论一句话
`Rank 330` 已被诚实收口到 `background/P0`，当前没有任何合法 `P3 / P2 / P1` 前排动作；所以本轮 bot2 应直接把运行态切回最近四条新 alpha 的 fresh-intake 轮，而不是继续拖旧对象。