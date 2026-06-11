# Strategy Review — 2026-04-03 11:12 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；仅作状态参考，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_1106_rank309_crypto_spike_reversion_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1042_rank307_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_1029_rank308_dlsa_latent_residual_policy_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-03_1009_rank307_kalshi_strikegap_binary_mispricing_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_1032_strategy-review.md`
  - `research/strategy_review/2026-04-03_0937_strategy-review.md`
  - `research/strategy_review/2026-04-03_0824_strategy-review.md`
- 最近新 digest：
  - `research/quant_digests/2026-04-03_1108_deltaneutral-eth-funding-carry-gate-alpha.md`
  - `research/quant_digests/2026-04-03_1020_adaptive-regime-switch-trend-mr-alpha.md`
  - `research/quant_digests/2026-04-03_0948_crypto-spike-reversion-binary-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有等待 bot2 兜底推进的 `P3 / Paper launch queue` 头部对象。

2) 本轮 `fresh intake` 是什么？
- 当前最新已完成的 fresh intake 仍是：
  - `research/quant_digests/2026-04-03_0948_crypto-spike-reversion-binary-alpha.md`
- 它已在 `research/optimization_loop/2026-04-03_1106_rank309_crypto_spike_reversion_first_verdict_keep_p1.md` 中获得正式 `Rank 309`，first verdict = `keep_P1`。
- 因此当前前排真正需要优先收口的是 `Rank 309` 的 survivor-only follow-up，而不是抢先切到新的 intake。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `Rank 309 / crypto spike reversion × binary wrapper`。
- 这条对象已经具备清楚的 `5m impulse overshoot -> short-cycle reversion` 主语、明确阈值、明确 time-box 与最小成本/流动性壳；它通过 `keep_P1` 不是因为 repo 很大，而是因为 raw alpha skeleton 已经足够具体。
- 因此它依法占据当前唯一 survivor 槽位，并默认享有那唯一一次 follow-up 的前排锁定权；`1108` 和 `1020` 这些新 intake 只能排在它之后。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次明确 P2 出口仍是 `Rank 285` 在 `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md` 中完成的 `one-time P2->P1 re-scope`。
- 因而本轮不触发 bot2 的 `P2 -> P3` 兜底升级责任，也不存在必须立即手动写入 `P3 / handoff` 的漏升对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 309`
- `Surviving candidate slot.current_target = Rank 309`
- `Active P2 slot.current_target = none`
- 当前所有前排对象都有正式 `Rank`；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- desk review 没有看到“已经足够值得 paper trade，但 bot3 仍未升级”的漏升对象。
- 因此本轮不直接写入新的 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班改写
按 policy 默认顺序，当前合法动作排序为：
1. `Rank 309` 的唯一 survivor follow-up
2. 在 survivor 已诚实排入后，补新的具体 fresh intake

因此本轮把 `cycle_plan` 改写为：
1. `Rank 309 / crypto spike reversion × binary wrapper`
2. `research/quant_digests/2026-04-03_1108_deltaneutral-eth-funding-carry-gate-alpha.md`
3. `research/quant_digests/2026-04-03_1020_adaptive-regime-switch-trend-mr-alpha.md`
4. `research/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`

改写理由：
- `Rank 309` 已明确是当前 survivor，且 `followup_budget_remaining = 1`；它依法享有前排锁定权。
- 当前没有 `P3` 待接线，也没有 `Active P2` 待出口，因此 survivor-only follow-up 继续是最前。
- `1108` 是本轮最新的新 repo/raw-alpha 报告，应优先于更早的 `1020` 与更旧 pending 的 `1007`。
- `1020` 仍然是具体且近期的新 repo/raw-alpha 候选，排在 `1108` 后面合理。
- `1007` 只作为预算补位；前排链条没有收口前，不得把它抢到更近的新对象前面。
- 本轮没有把 background pool 旧候选拉回前排，也没有把 guard/空槽确认单独写成 bot3 任务。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_1112_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前没有 P3，也没有 Active P2；前排唯一必须优先收口的是 `Rank 309` 的 survivor follow-up，而新的 intake 只应按 `1108 -> 1020 -> 1007` 的顺序排在它后面。
