# Strategy Review — 2026-04-06 03:00 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 optimization：
  - `research/optimization_loop/2026-04-06_0258_rolling_max_intake_blocked_duplicate_rank234.md`
  - `research/optimization_loop/2026-04-06_0224_rank345_ghe_pairs_fresh_intake_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0158_adaptivetrend_fresh_intake_background_p0.md`
  - `research/optimization_loop/2026-04-06_0124_rank344_survivor_followup_beta_wrap_not_distinct_xs_alpha_background_p0.md`
  - `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-06_0155_strategy-review.md`
  - `research/strategy_review/2026-04-06_0053_strategy-review.md`
  - `research/strategy_review/2026-04-06_0006_strategy-review.md`
- 最近新 digest / intake 候选：
  - `research/quant_digests/2026-04-06_0040_sg-lob-imbalance-continuation-alpha.md`
  - `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`
  - `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Paper launch queue.current_target = none`。
- 最近 `Rank 342` 已在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成 dedicated runner、scheduler 与首跑验证，并正式写回 `connected_runner_live`。
- 因此当前没有待 handoff 的 `P3` 对象，也不存在 bot2 需要兜底补推到 `P3` 的漏项。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 应切到** `research/quant_digests/2026-04-06_0040_sg-lob-imbalance-continuation-alpha.md`。
- 原因：
  1. 当前前排里唯一还没收口的是 `Rank 345` 的 survivor follow-up；它占用的是 `P1` 槽位，不是 fresh intake 槽位。
  2. `AdaptiveTrend` 已在 `2026-04-06_0158` 收口为 `background/P0`，不能再继续占当前 intake 位。
  3. `rolling-MAX` 已在 `2026-04-06_0258` 被确认是旧对象 `Rank 234` 的重复表述，按 duplicate-object guard 不能再当成合法 fresh intake。
  4. 在剩余尚未首判的最近新对象里，`2026-04-06_0040` 是最新、且是 raw alpha 本体而非纯 overlay 的具体候选，因此应作为当前第一条新的 fresh intake。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在这唯一一次 follow-up 正是最该优先执行的前排动作。**
- 上一条 fresh intake 是 `Rank 345 / GHE-Hurst pair selection × spread mean reversion`。
- `2026-04-06_0224_rank345_ghe_pairs_fresh_intake_keep_p1.md` 已明确写出：
  - 它的 distinctness 不在普通 pairs baseline 的 ranking embellishment，而在 `low-H top-K pairbook -> beta-hedged z-score MR` 这一前移的 pair formation shell；
  - 现有证据足够支持 `keep_P1`；
  - 但 desk portability 主体目前更明确落在 `5m-first`，因此还需要那唯一一次便宜且决定性的 follow-up，去回答它相对 plain corr/cointegration baseline 是否还有独立的 after-cost 增量。
- 所以答案是：**值得，而且 survivor budget 仍剩 1 次，必须先把这次用掉并给出终局结论。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 active P2 是 `Rank 342`，但它已经在 `2026-04-05_2300` 完成 `P2 -> P3`，随后又在 `2026-04-06_0016` 完成 `P3 launch wiring -> connected_runner_live`。
- 因此当前没有需要 bot2 兜底裁判 `P3 / P1 / P0` 出口方向的滞留 `P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 345`
- `Active P2 slot.current_target = none`
- 当前唯一前排对象 `Rank 345` 已有正式 rank；不存在达到 `keep_P1 / P2 / P3` 但无 rank 的违规状态，因此本轮无需补发 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- desk review 未发现任何“已经足够进入 paper trade、但 bot3 尚未升级”的漏判对象。
- 因此本轮不需要执行 `P2 -> P3` 的强制写回，只需要把前排 survivor 收口，并把新的 fresh intake 顺序排正确。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前合法前排链条为：
- `P3`: none
- `P2`: none
- `P1 survivor`: `Rank 345`

因此本轮排班必须先收口 `Rank 345`，然后才轮到新的 fresh intake。已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Rank 345 / GHE-Hurst pair selection × spread mean reversion` survivor follow-up
2. `research/quant_digests/2026-04-06_0040_sg-lob-imbalance-continuation-alpha.md`
3. `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`
4. `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`

### 为什么这么排
- `Rank 345` 作为当前唯一 survivor，依法享有前排锁定权；在它那唯一一次 follow-up 收口之前，不能让新的 `keep_P1` 候选覆盖 survivor 槽位。
- `rolling-MAX` 已被明确拦截为 `Rank 234` 的 duplicate-object，不得再继续占 fresh intake 位。
- `AdaptiveTrend` 已收口为 `background/P0`，不能再重复排进本轮主序列。
- 在新的合法 intake 候选里，`SG-smoothed LOB imbalance` 是最新且更贴近 raw alpha 的对象，因此排在 macro-event 与 SaR overlay 前面。
- `macro impulse × sentiment gate` 仍是合法的新 raw alpha 候选，优先级高于纯 overlay。
- `SaR` 虽不是方向性 alpha，但作为共享 execution overlay 仍有独立部署价值，因此保留为 conditional 第四项，而不是拿旧 background 对象来凑数。

## 对 repo 状态的最小备注
- repo 当前存在若干未跟踪临时文件与历史产物，但本轮 policy 明确规定调度只以 `BOT2_BOT3_STATE.md` 与最近 research evidence 为准；这些临时文件不构成 reopen 旧对象或改写排班优先级的理由。

## 本轮一句话
当前没有 `P3`、没有 `Active P2`；唯一必须先做的是把 `Rank 345` 的 survivor follow-up 诚实收口，然后把新的 fresh intake 切到 `SG-smoothed LOB imbalance`，而不是继续拿已收口或重复对象占前排。