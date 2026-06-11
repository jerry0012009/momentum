# Strategy Review — 2026-04-04 06:53 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md`
  - `research/optimization_loop/2026-04-04_0510_rank324_volume_router_dualbook_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0539_obi_microprice_pairs_first_verdict_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0544_strategy-review.md`
- 最新 fresh-intake 候选 digest：
  - `research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
  - `research/quant_digests/2026-04-04_0620_par-prediction-line-cross-alpha.md`
  - `research/quant_digests/2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前仅有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- 当前前排仍有真实动作：
  - `Surviving candidate = Rank 324`
  - `Active P2 = none`
- 因此新的 fresh intake 仍不能越过 survivor 收口；只能老实排在其后。
- 结合最新 digest 时间顺序与“最近新 repo/paper/alpha 报告优先”，**本轮 fresh intake 头**改为：
  - `research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
- 若预算仍有余，补位顺序为：
  - `research/quant_digests/2026-04-04_0620_par-prediction-line-cross-alpha.md`
  - `research/quant_digests/2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 上一条 fresh intake 是 `Rank 325 / OBI-microprice pairs shell`。
- 05:39 UTC 的 first verdict 已明确写成 `background/P0`：它虽然给出了 `cointegrated spread fade + microprice/OBI veto` 的完整 repo 壳，但新增信息主要仍是对现有 pairs 主线的工程化复述，没有给出一条比当前前排更独特、且不依赖脏 universe / 高频执行假设的新 short-cycle lane。
- 因此它不进入 survivor，也不存在 follow-up 预算；当前唯一 survivor 仍然只能是上一条 `keep_P1` fresh intake——`Rank 324`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 322` 的 P2 exit 已在 06:30 UTC 收口：原先 `BTC-XRP / SOL-XRP × 15m` 双 lane 在更长样本与 honesty 重检后只剩 `SOL-XRP` 单 lane 勉强存活，因此对象不升 `P3`，也不直接打回 `P0`，而是一次性 `P2->P1 re-scope` 到 `SOL-XRP-only × 15m`，并释放 `Active P2 slot`。
- 所以当前不再有需要 bot2 兜底升级到 `P3` 的活跃 P2；离出口最近的对象已经完成出口，且落点是 **`P1`**。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = Rank 324 / vol-z router × TSMOM / XS reversal dual-book`
- `Active P2 slot.current_target = none`
- 当前前排对象均已有正式 `Rank`；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮 desk review 后，当前**不存在明确 `Active P2`**，因此也不存在一个“已足够值得 paper trade 但 bot3 尚未升级”的在位对象需要 bot2 直接推进到 `P3 / Paper launch queue`。
- `Rank 322` 的出口已被最新 evidence 诚实收口为一次性 `P2->P1 re-scope`，所以本轮不得再把它按开放式 P2 admission 续写，也不得越证据改写成 `P3`。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：无明确 `Active P2`
3. `P1`：有且只有一个 survivor —— `Rank 324`
4. `fresh intake`：只有在 survivor 已诚实排入当前轮前部后，才能补新的具体对象

因此本轮将 `cycle_plan` 重写为 4 项：
1. `Rank 324`：做唯一一次 survivor follow-up，结论只能是 `promote_P2` 或 `background/P0`
2. `2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`：作为当前轮 fresh intake 头
3. `2026-04-04_0620_par-prediction-line-cross-alpha.md`：作为第二条具体 fresh intake
4. `2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`：作为预算仍有余时的补位 intake

改写理由：
- 当前不存在 `P3` 与 `Active P2` 真实动作，唯一必须优先收口的是 `Rank 324` 的 survivor follow-up；
- `Rank 324` 仍持有 survivor 锁定权，不能被新的 `keep_P1` 覆盖；
- 在 survivor 已排入当前轮首位后，本轮 fresh intake 应优先来自**最新**的新 repo/paper/alpha 报告，因此 06:41 的 walk-forward pairs repo 和 06:20 的 PAR paper 都应先于更早的 04:48 MFI exhaustion digest；
- `Rank 325` 已在 first verdict 收口到 `background/P0`，不应再占用 follow-up 或 survivor 槽位。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮只改写 runtime state；未改动 policy / brief / operating card / auto loop / cron prompt。
