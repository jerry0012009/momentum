# Strategy Review — 2026-04-06 01:55 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 optimization：
  - `research/optimization_loop/2026-04-06_0124_rank344_survivor_followup_beta_wrap_not_distinct_xs_alpha_background_p0.md`
  - `research/optimization_loop/2026-04-06_0052_rolling_max_fresh_intake_blocked_by_survivor_lock.md`
  - `research/optimization_loop/2026-04-06_0026_rank344_winner_only_loser_short_veto_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-06_0053_strategy-review.md`
  - `research/strategy_review/2026-04-06_0006_strategy-review.md`
- 最近新 digest / paper intake 候选：
  - `research/quant_digests/2026-04-06_0144_adaptivetrend-rolling-sharpe-trend-basket-alpha.md`
  - `research/quant_digests/2026-04-06_0115_ghe-pair-selection-spread-meanreversion-alpha.md`
  - `research/quant_digests/2026-04-05_2151_rolling-max-spike-persistence-xs-alpha.md`
  - `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Paper launch queue.current_target = none`。
- 最近唯一需要接线的对象 `Rank 342 / same-chain cross-DEX price-gap close` 已在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 写回 `connected_runner_live`，说明 dedicated runner、scheduler 与首跑验证都已完成。
- 因此当前没有待 handoff 的 `P3` 头对象，也不存在 bot2 需要兜底补推的 queue 任务。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 应切到** `research/quant_digests/2026-04-06_0144_adaptivetrend-rolling-sharpe-trend-basket-alpha.md`。
- 理由不是把旧 pending 模板机械顺延，而是：
  1. `Rank 344` survivor 已在 `2026-04-06_0124` 正式收口并退回 background；
  2. 当前 `P3 / P2 / P1` 均为空，不再有前排收口任务；
  3. policy 明确要求在前排链条收口后，优先从**最近新的 strategy repo / paper / alpha report**里指定具体 intake；
  4. `2026-04-06_0144` 是当前最近、最具体、且仍未进入正式 first verdict 的新 paper alpha 候选。
- 因此它比此前被 survivor lock 拦下的 `rolling-MAX` 更符合“恢复 fresh intake 后，从最近新对象重新开火”的默认顺序。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且那一次 follow-up 已经执行完并收口。**
- 上一条 fresh intake 是 `Rank 344 / winner-only × loser-short veto`。
- `2026-04-06_0124_rank344_survivor_followup_beta_wrap_not_distinct_xs_alpha_background_p0.md` 已明确回答：
  - 这条线足以证明 `loser-short veto` 合理；
  - 但没有证明 `winner-only` 在 desk `high-liquidity perp`、after-cost、beta-adjusted 口径下仍是独立可迁移的 XS alpha；
  - 因此 survivor 预算已经合法耗尽，不能再续写第二次 follow-up，也不能继续占前排。
- 所以本题答案是：**值得过那唯一一次，但那次已经用完，结论是不升 P2，直接回 background。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 active P2 是 `Rank 342`，而它已在上一轮完成 `P2 -> P3`，随后又完成 `P3 launch wiring -> connected_runner_live`；因此当前不存在需要 bot2 兜底裁决出口方向的滞留 P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前不存在前排对象，因此也不存在“达到 `keep_P1 / P2 / P3` 但无正式 rank”的违规状态；本轮无需补 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- 最近 desk review 已把 `Rank 342` 兜底推进到 `P3`，bot3 也已经完成 wiring 写回 runtime；因此当前不存在“已足够值得 paper trade、但 bot3 尚未升级”的漏判对象。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前合法前排链条为：
- `P3`: none
- `P2`: none
- `P1 survivor`: none
- 因此前三层都无真实可执行动作，本轮必须恢复到具体 `fresh intake`。

已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `research/quant_digests/2026-04-06_0144_adaptivetrend-rolling-sharpe-trend-basket-alpha.md`
2. `research/quant_digests/2026-04-06_0115_ghe-pair-selection-spread-meanreversion-alpha.md`
3. `research/quant_digests/2026-04-05_2151_rolling-max-spike-persistence-xs-alpha.md`
4. `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`

### 为什么这么排
- `Rank 342` 已完成 `connected_runner_live`，不再占 `P3` 前排。
- `Rank 344` 的唯一 survivor follow-up 已在 `2026-04-06_0124` 收口并退回 background，survivor lock 已解除。
- 当前没有 `Active P2`，因此不能虚构 `P2` admission 任务。
- 一旦前排为空，policy 要求直接指定新的 fresh intake，且优先选最近新的 repo / paper / alpha 报告；因此把 `2026-04-06_0144` 与 `2026-04-06_0115` 提到前两位，比继续沿用 survivor lock 期间排下的旧顺位更诚实。
- `rolling-MAX` 仍然保留在本轮预算里，但已经降到较后的具体 intake 位次；这不是把 background 拉回前排，而是把此前被锁住的合法新对象继续放回 intake 队列。

## 本轮一句话
`Rank 344` 已合法收口出前排，`Rank 342` 已经彻底连上运行态；所以本轮不该再假装有 P3/P2/P1 主线，默认动作就是切回 fresh intake，并从最新的 `AdaptiveTrend rolling-Sharpe basket` 开始。