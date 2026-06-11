# Strategy Review — 2026-04-03 04:51 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；仅作状态参考，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0450_rank303_realized_skewness_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0403_rank302_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_0328_realized_skewness_fresh_intake_blocked_by_rank302_survivor_lock.md`
  - `research/optimization_loop/2026-04-03_0310_rank302_basket_rebalance_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0341_strategy-review.md`
  - `research/strategy_review/2026-04-03_0302_strategy-review.md`
  - `research/strategy_review/2026-04-03_0149_strategy-review.md`
- 最近新 repo/paper/alpha 报告：
  - `research/quant_digests/2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`
  - `research/quant_digests/2026-04-03_0355_same-underlier-multispread-optimizer-statarb.md`
  - `research/quant_digests/2026-04-03_0320_fundingstable-spotbasis-profitlock-alpha.md`
  - `research/quant_digests/2026-04-03_0228_kalshi-macro-vol-regime-gate.md`

## Repo 状态摘要
- `## master...origin/master`
- `jerry/momentum` 本轮按权限边界只更新 `docs/BOT2_BOT3_STATE.md`，并新增本条 strategy review 日志。
- 其他工作区临时变更只作背景状态参考，本轮不据此改 policy。

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有待 bot2 兜底推进的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 本轮在前排 survivor 诚实收口之后，第一条 fresh intake 应切到 `research/quant_digests/2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`。
- 原因：`2026-04-03_0254_realized-skewness-xs-reversal-alpha.md` 已完成 first verdict 并升为 `Rank 303` 占用 survivor 槽位，不再属于 fresh intake；在不跳过当前前排对象的前提下，剩余预算应按最近且主语清楚的新 repo/paper/alpha 报告继续补位，而 `0445` 是当前最新、可直接 desk 化的完整 raw-alpha 壳。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `2026-04-03_0254_realized-skewness-xs-reversal-alpha.md`，现已成为 `Rank 303 / realized-skewness cross-section fade`。
- `2026-04-03_0450_rank303_realized_skewness_first_verdict_keep_p1.md` 已明确给出 `keep_P1`：它不是旧 `MAX` 或普通 `lagged-return reversal` 的简单换皮，而是以“整段收益分布右偏 / 彩票化”作为横截面回吐主语。
- 因此它依法值得那唯一一次 survivor follow-up；而且 follow-up 方向已经足够收敛：只需回答它在 `ret_24h` 与 `MAX` 控制后是否仍有独立增量，若没有就直接收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新对象进入 `Active P2`。
- 因而当前不触发 bot2 作为 `P2 -> P3` 兜底裁判的强制升级动作。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 303`
- `Active P2 slot.current_target = none`
- 当前前排对象都有正式 `Rank`；本轮无需补发新的整数编号。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不触发 bot2 直接把对象改写进 `P3 / Paper launch queue` 或 handoff 路径。
- 最近证据中也没有出现“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的漏升案例。

## 本轮排班改写
按 policy 默认顺序，当前真实可执行动作应为：
1. `P1 / Surviving candidate`：先执行 `Rank 303` 的唯一一次 decisive follow-up。
2. `fresh intake`：只有在 `Rank 303` 已诚实收口后，才允许继续推进新的 intake。

据此，已将 `cycle_plan` 重写为：
1. `Rank 303 / realized-skewness cross-section fade`
2. `2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`
3. `2026-04-03_0355_same-underlier-multispread-optimizer-statarb.md`
4. `2026-04-03_0320_fundingstable-spotbasis-profitlock-alpha.md`

重写理由：
- 当前前排唯一真实动作是 `Rank 303` survivor 收口，不得让新的发现越过它。
- `Rank 303` 已出现 `keep_P1`，因此其唯一 survivor follow-up 依法享有前排锁定权。
- 在 survivor follow-up 被诚实排到首位后，剩余预算应回到最近且主语清楚的具体 fresh intake，而不是继续保留已完成的旧项或抽象占位。
- 本轮未把 background pool 旧候选自动拉回前排。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_0451_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排唯一必须先做完的动作是 `Rank 303` 对 `ret_24h` 与 `MAX` 的 survivor 去重收口；只有它诚实出清后，新的 `EMA+OBV caution trend shell` 才应成为本轮 fresh intake 头。