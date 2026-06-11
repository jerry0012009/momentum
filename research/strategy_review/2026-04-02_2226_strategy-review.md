# Strategy Review — 2026-04-02 22:26 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_2221_rank298_dynamic_factor_multipair_keep_p1.md`
  - `research/optimization_loop/2026-04-02_2148_rank297_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_2135_dynamic_scaling_pairs_overlay_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_2139_strategy-review.md`
- 新近 intake 候选：
  - `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`
  - `research/quant_digests/2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
  - `research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 已接线 live 的仍是 `Rank 200 / 201 / 213 / 229`；本轮没有待 bot2 兜底推进到 `P3 / Paper launch queue` 的对象。

2) 本轮 `fresh intake` 是什么？
- 运行态最近一条已完成首判的 fresh intake 是 `research/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`，其结果已写成 `Rank 298 / keep_P1`。
- 但按本轮重排后的 `cycle_plan`，当前真正排在最前、等待进入的**下一条 fresh intake** 已切到 `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- `Rank 298` 已具备独立 raw-alpha 主语：先剥离共同市场因子，再以 stationary 第二因子驱动 ranked long-short rotation，并自带 `ADF/corr` honesty gate 与 public-data clean-room 路径。
- 但它还停在 `P1`，尚未回答最关键 admission 前问题：高流动 perp universe 上这种两因子结构是否稳定、`top-half/bottom-half` 与 `top-2/bottom-2 sparse` 哪个能活过成本、以及 `15m/5m` 的 short-cycle 持有是否仍保留净边。
- 所以它值得、也只值得这唯一一次 survivor follow-up；这条前排锁必须先收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；本轮没有仍应继续 admission 的对象。
- 因而当前最近的前排出口不是 `P2 -> P3`，而是 `Rank 298` 这个 survivor 的 `P2 / P0` 二选一收口。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot = Rank 298`
- `Active P2 slot = none`
- 当前前排对象均已有正式 `Rank`；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近 evidence 中也没有出现“已足够 paper launch，但 bot3 尚未升级”的漏升对象。
- 因此本轮**不触发** bot2 直接改写到 `P3 / handoff` 路径。

## 本轮排班结论
继续严格按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

由于当前：
- `P3` 无待接线对象；
- `Active P2 = none`；
- 但 `Rank 298` 是唯一合法 survivor，且 follow-up budget 还剩 `1`；

所以本轮 `cycle_plan` 重写为：
1. **先收口 `Rank 298` 的唯一 survivor follow-up**，直接回答 `promote_P2` 还是 `background/P0`；
2. 然后才排新的 fresh intake；
3. 新 fresh intake 依次填入：
   - `2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`
   - `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
   - `2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
当前最该做的不是继续开新的 admission 或回捞旧候选，而是把 `Rank 298` 那唯一一次 survivor follow-up 用掉；只有它诚实收口后，新的 intake 才应按 `EMA(RSI) regime hierarchy -> best-venue funding z-score carry -> liquidity-provision short-term reversal` 的顺序进入前排。
