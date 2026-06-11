# Strategy Review — 2026-04-03 09:37 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；仅作状态参考，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0931_rank306_kalshi_macro_vol_regime_gate_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0854_rank305_hip3_oracle_premium_fade_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
  - `research/optimization_loop/2026-04-03_0818_fundingstable_spotbasis_profitlock_first_verdict_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0824_strategy-review.md`
  - `research/strategy_review/2026-04-03_0738_strategy-review.md`
  - `research/strategy_review/2026-04-03_0640_strategy-review.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`，没有待 bot2 直接推进的 `P3 / Paper launch queue` 头部对象。

2) 本轮 `fresh intake` 是什么？
- 当前已完成的 fresh intake 是：
  - `research/quant_digests/2026-04-03_0228_kalshi-macro-vol-regime-gate.md`
- 它在 `2026-04-03_0931_rank306_kalshi_macro_vol_regime_gate_first_verdict_keep_p1.md` 中已获得正式 `Rank 306`，first verdict = `keep_P1`。
- 但按 policy，当前前排真正优先收口的不是继续开新坑，而是上一条 fresh intake 留下的 survivor 动作。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 是 `Rank 305 / HIP-3 oracle-premium percentile fade × time-boxed exit`。
- 它已经在 `2026-04-03_0854_*` 中被诚实判为 `keep_P1`，并且主语与既有 funding / basis carry 家族有清楚区分：核心是 `mark-vs-oracle premium` 的分钟级极端偏离回归。
- 因此它依法占据当前唯一 survivor 槽位，且那唯一一次 follow-up 应优先执行，不能被新的 intake 覆盖。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次明确 P2 出口仍是 `Rank 285` 在 `2026-04-02_0159_*` 中完成的 `one-time P2->P1 re-scope`。
- 因而本轮不触发 bot2 的 `P2 -> P3` 兜底升级责任。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 306`
- `Surviving candidate slot.current_target = Rank 305`
- `Active P2 slot.current_target = none`
- 当前前排对象都有正式 `Rank`；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不存在“desk review 已清楚表明够格 paper trade 但 bot3 尚未升级”的漏升对象。
- `Paper launch queue` 也为空，无需直接写入新的 `P3 / handoff`。

## 本轮排班改写
按 policy 默认顺序，当前最前面的真实动作应是：
1. `Rank 305` 的唯一 survivor follow-up
2. 只有把这个前排动作诚实排入后，才允许补新的具体 fresh intake

因此本轮把 `cycle_plan` 改写为：
1. `Rank 305 / HIP-3 oracle-premium percentile fade × time-boxed exit`
2. `research/quant_digests/2026-04-03_0908_kalshi-strikegap-binary-mispricing-alpha.md`
3. `research/quant_digests/2026-04-03_0848_dlsa-latent-residual-policy-alpha.md`
4. `research/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`

改写理由：
- `Rank 305` 已明确是 survivor，且 follow-up budget 仍为 1；它依法享有前排锁定权。
- `Rank 306` 虽然也是 `keep_P1`，但当前并没有合法理由让它跳过 `Rank 305` 直接占用 survivor 动作，因此这轮不能把新对象排在 `Rank 305` 前面。
- 在第 1 条已诚实排入的前提下，剩余预算才用来补具体、最近、尚未首判的新 intake；最新两条是 `0908` 与 `0848`，再往后补 `1007`。
- 本轮不把 `park_reframe` 提前到最新新 digest 前面，也不把 background pool 旧候选自动拉回前排。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_0937_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前没有 P3、也没有 Active P2；真正该优先收口的是 `Rank 305` 的唯一 survivor follow-up，而不是继续让后续 `keep_P1` 或新 intake 抢在它前面。