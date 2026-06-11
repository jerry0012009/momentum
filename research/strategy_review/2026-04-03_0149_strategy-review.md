# Strategy Review — 2026-04-03 01:49 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0101_rank300_survivor_exit_background_cutoff_unresolved.md`
  - `research/optimization_loop/2026-04-03_0114_rank301_bb_zscore_rsi_trendveto_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0145_btc_volclock_first30_impulse_first_verdict_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0055_strategy-review.md`
  - `research/strategy_review/2026-04-03_0014_strategy-review.md`
- 最近新 alpha 报告：
  - `research/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`
  - `research/quant_digests/2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
  - `research/quant_digests/2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有等待 bot2 兜底推进的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 头应当切到 `research/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`。
- 原因不是它“更新”这么简单，而是当前前排 `P3 / Active P2` 都为空，`Rank 301` 的 survivor 收口之后，最靠前的新对象应回到最近新 repo/paper/alpha 报告优先级；`0136` 这条 `cointegrated basket equal-weight drift × threshold rebalance` 是最新且主语清楚的 fresh intake。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 已在 `2026-04-03_0114_rank301_bb_zscore_rsi_trendveto_keep_p1.md` 被正式写成 `Rank 301 / BB-zscore overshoot × RSI confirm × trend-veto mean reversion`，并且 first verdict 明确它不是单纯指标拼盘，而是有清楚 raw-alpha 主语的单币 `overshoot snapback` 壳。
- 因此它依法值得那唯一一次 survivor follow-up；下一步必须只回答一个问题：`5m/15m` clean-room 下它能不能形成成本后仍存活、可 admission 的最小 pocket。若不能，就应直接退回 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新对象进入 `Active P2`。
- 因而当前不存在需要 bot2 兜底裁成 `P3 / P1 / P0` 的在役 P2 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot = Rank 301`
- `Active P2 slot = none`
- 当前前排对象均有正式 rank；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不触发 bot2 直接改写到 `P3 / Paper launch queue` 或 handoff 路径。
- 最近 evidence 里也没有出现“对象已足够值得 paper trade，但 bot3 还没升”的漏升案例。

## 本轮排班结论
按 policy 默认顺序，当前轮必须重写为：
`P3 handoff > P2 admission/promote/park > P1 survivor follow-up > fresh intake > P0`

当前实际运行态：
- `P3` 无待接线对象；
- `Active P2 = none`；
- `Surviving candidate = Rank 301`；
- `Fresh intake` 在 survivor 收口后应切到 `2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`。

因此本轮 `cycle_plan` 重写为：
1. `Rank 301` survivor follow-up（唯一一次 decisive follow-up）
2. `2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`
3. `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`
4. `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`

这样排的原因：
- 现有 survivor 的诚实收口优先级高于任何新发现；
- 当前没有 P3/P2 可执行动作，所以 survivor 后应直接切回最新、主语清楚的 fresh intake；
- `2257` 与 `2043` 继续保留为具体、合法的后续 intake，而不是空泛占位。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
当前轮没有任何 `P3` 或 `Active P2` 需要 bot2 兜底，真正的前排动作只剩 `Rank 301` 的唯一 survivor 收口；所以 runtime 必须先把它做完，再切回最新 fresh intake `0136`，而不是继续沿用上一轮已经完成的 `0042/300` 队列。