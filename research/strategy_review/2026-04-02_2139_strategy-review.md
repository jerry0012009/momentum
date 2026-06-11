# Strategy Review — 2026-04-02 21:39 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_2059_rank297_multiquote_bucket_rv_keep_p1.md`
  - `research/optimization_loop/2026-04-02_2135_dynamic_scaling_pairs_overlay_background_p0.md`
  - `research/optimization_loop/2026-04-02_2040_rank296_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_1823_rank295_public_inflow_proxy_blocked.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_2028_strategy-review.md`
- 新近 intake 候选：
  - `research/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`
  - `research/quant_digests/2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
  - `research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- 当前 `Paper launch queue.current_target = none`。
- 运行态已接好的仍是 `Rank 200 / 201 / 213 / 229`；本轮没有需要 bot2 兜底直接推进到 `P3 / Paper launch queue` 的 `Active P2`。

2) 本轮 `fresh intake` 是什么？
- 运行态最近一条**已完成首判**的 fresh intake 仍是 `research/quant_digests/2026-04-02_1946_dynamic-scaling-pairs-alpha.md`。
- 它的 first verdict 已明确写成 `background/P0`，没有进入 survivor。
- 但按本轮重排后的 `cycle_plan`，当前最靠前、等待进入的**下一条 fresh intake** 已切到 `research/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，但这里“上一条值得 follow-up 的 fresh intake”不是刚被打回 `P0` 的 `dynamic scaling pairs`，而是当前 survivor：`Rank 297 / same-underlier multiquote bucket RV`。
- 它已经完成 fresh intake first verdict 并拿到正式 rank，且保留理由具体：
  - 不是旧两腿 pairs 的换壳；
  - 主语是同一底层、多报价腿的 relative-value；
  - 关键增量在于多 spread 同时触发时的统一 allocator；
  - `BTC/ETH × (USDT, USDC, FDUSD)` 的 public-data clean-room 路径已成立。
- 但它还没到 admission 级，唯一还值得做的 follow-up 就是：**比较 `bucket allocator` 相对 `independent pairs` baseline 的 after-cost 增益是否真实存在。**
- 因此它值得、也只值得这唯一一次 follow-up；这条前排锁在本轮必须优先收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 active P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`，本轮没有仍应继续 admission 的对象。
- 所以本轮最近的前排出口不是 `P2 -> P3`，而是 `Rank 297` 这个 `P1 survivor` 的 `P2 / P0` 二选一收口。

## Rank 完整性检查
- `Surviving candidate slot = Rank 297`
- `Active P2 = none`
- `Paper launch queue.current_target = none`
- 当前前排不存在无 rank 对象，因此本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近证据里也没有出现“desk review 已明显足够 paper launch，但 bot3 没升”的漏升对象。
- 因此本轮**不触发** bot2 直接写入 `P3 / Paper launch queue`。

## 本轮排班结论
本轮继续严格按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

由于当前：
- `P3` 无待接线对象；
- `Active P2 = none`；
- 但 `Rank 297` 是唯一合法 survivor，且 follow-up 预算还剩 `1`；

所以本轮 `cycle_plan` 必须写成：
1. **先收口 `Rank 297` 的唯一 survivor follow-up**，直接回答 `promote_P2` 还是 `background/P0`；
2. 然后才排新的 fresh intake；
3. 新 fresh intake 依次填入：
   - `2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`
   - `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
   - `2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
当前最该做的不是继续撒新的 intake，而是把 `Rank 297` 那唯一一次 survivor follow-up 用掉；只有它诚实收口后，`dynamic-factor multi-pair stat-arb` 才该接过 fresh intake 头位。