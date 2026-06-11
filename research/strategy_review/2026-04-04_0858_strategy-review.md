# Strategy Review — 2026-04-04 08:58 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0855_btc_spotperp_funding_threshold_carry_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-04_0700_rank324_survivor_followup_background_p0_volume_router_no_postcost_lane.md`
  - `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0733_strategy-review.md`
- 最新 fresh-intake 候选 digest：
  - `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`
  - `research/quant_digests/2026-04-04_0756_signed-hourpair-lagmap-alpha.md`
  - `research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
  - `research/quant_digests/2026-04-04_0620_par-prediction-line-cross-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物、脚本与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 头是：** `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`。
- 原因：
  - 当前 `Paper launch queue = none`
  - 当前 `Surviving candidate slot = none`
  - 当前 `Active P2 slot = none`
  - 上一条 fresh intake 已经诚实收口为 `background/P0`
- 因此前排没有仍需优先收口的 `P3 / P2 / survivor` 动作，本轮可按 policy 切回**最近新的 strategy repo / paper / alpha report**；08:49 这条 signed-flow / maker-conviction digest 是当前时间上最新、对象具体、且尚未进入前排评判的合法 fresh intake。
- 若预算仍有余，补位顺序为：
  1. `research/quant_digests/2026-04-04_0756_signed-hourpair-lagmap-alpha.md`
  2. `research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
  3. `research/quant_digests/2026-04-04_0620_par-prediction-line-cross-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 上一条 fresh intake 是 `BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry`。
- 08:55 UTC 的 first verdict 已明确写成 `background/P0`：它没有形成独立于 `Rank 265 / Rank 310` 的新前排 raw alpha，新增值主要属于 same-venue delta-neutral carry 家族的 `negative-funding veto / re-entry / cost-budget` 诚实化 baseline，而不是新的 front-slot 对象。
- 因此它不进入 survivor，也不存在 follow-up 预算；当前 survivor 槽位应保持 `none`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 322` 的 P2 exit 已在 06:30 UTC 收口：原先 `BTC-XRP / SOL-XRP × 15m` 双 lane 在更长样本与 honesty 重检后，只剩 `SOL-XRP` 单 lane 勉强保留，因此对象不升 `P3`，也不直接打回 `P0`，而是一次性 `P2->P1 re-scope` 到 `SOL-XRP-only × 15m`，并释放 `Active P2 slot`。
- 所以当前不再有需要 bot2 兜底升级到 `P3` 的活跃 P2；离出口最近的对象已经完成出口，且落点是 **`P1`**。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排没有无 rank 对象；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮 desk review 后，当前**不存在明确 `Active P2`**，因此也不存在一个“已足够值得 paper trade 但 bot3 尚未升级”的在位对象需要 bot2 直接推进到 `P3 / Paper launch queue`。
- `Rank 322` 的出口已被最新 evidence 诚实收口为一次性 `P2->P1 re-scope`，所以本轮不得越证据把它改写成 `P3`。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：无明确 `Active P2`
3. `P1`：无 survivor follow-up 待做
4. `fresh intake`：成为本轮主线

因此本轮将 `cycle_plan` 重写为 4 项：
1. `2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`
2. `2026-04-04_0756_signed-hourpair-lagmap-alpha.md`
3. `2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
4. `2026-04-04_0620_par-prediction-line-cross-alpha.md`

改写理由：
- `BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry` 已在 08:55 UTC 诚实收口到 `background/P0`，因此不享有 survivor follow-up；
- `Rank 324` survivor 已在 07:00 UTC 诚实收口到 `background/P0`，survivor 槽位已释放；
- `Rank 322` 的 `P2->P1 re-scope` 只是已定义的新 scope，不在当前 survivor / active P2 合法槽位，policy 不允许把它自动拉回前排默认主线；
- 因此前排收口已完成，本轮应直接回到最新合法 fresh intake；
- 最新对象里，08:49 的 `1m signed trade imbalance × 5m forward return × maker-only conviction gate` 比 07:56 / 06:41 / 06:20 的候选更新，故成为本轮 intake 头。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮只改写 runtime state；未改动 policy / brief / operating card / auto loop / cron prompt。
