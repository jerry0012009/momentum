# 2026-04-06 09:35 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `Rank 342` 已经不在 queue 待接线，而是正式写进 `connected_runner_live`；本轮没有新的待接线 `P3` 头对象。

2. **本轮 `fresh intake` 是什么？**
   - 当前 head fresh intake 是：
   - `research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
   - 理由：`Rank 351 / RF threshold-bucket × HF pairs` 已在 08:54 UTC 完成 first verdict 并退回 `background / P0`；前排仍被 `Rank 350` survivor 锁住，但 fresh-intake 头对象应切到最新未执行、且具体可判的 intake。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 是。
   - 上一条 fresh intake 是 `Rank 350 / BTC lead × low-liquidity alt lag`。
   - `research/optimization_loop/2026-04-06_0826_rank350_btc_lead_low_liquidity_alt_lag_first_verdict_keep_p1.md` 已把它压成独立 raw alpha 主语：`BTC 先发现 + 低流动性 alt 慢半拍补价`，并给出 `1m 主半衰期 / 3m 仅 child aggregation` 的边界。
   - 因此它值得且必须享有那唯一一次 survivor follow-up；本轮 follow-up 应直接回答 `tradable alt bucket × explicit after-cost` 下是否还能保留可迁移净增量，决定其是升 `P2` 还是退回 `background / P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - 最近的 `Active P2` 是 `Rank 342`，它已经完成 `P2 -> P3`，随后完成 dedicated runner / scheduler / 首跑验证，并写回 `connected_runner_live`，所以当前既不留在 `Active P2`，也不留在 `Paper launch queue`。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = Rank 350`
  - `Active P2 = none`
  - `Fresh intake head = research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
- 前排不存在 `keep_P1 / P2 / P3` 但无正式 rank 的对象。
- 本轮**无需补 rank**。

## 排班判断

按 policy 的 authoritative 顺序扫描：

1. **P3 handoff**：无待接线对象。
2. **P2 admission / promote / park**：`Active P2 = none`。
3. **P1 survivor follow-up**：`Rank 350` 仍有且只剩 1 次 follow-up 预算，这一步必须排第一，不能被新的 intake 覆盖。
4. **fresh intake**：只有在 survivor 已诚实排入前部后，才用剩余预算补具体 intake 对象。

因此本轮 `cycle_plan` 必须重写为：

1. `Rank 350 / BTC lead × low-liquidity alt lag` survivor exit decision
2. `2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
3. `2026-04-06_0843_binance-l2-feeaware-as-maker-alpha.md`
4. `2026-04-06_0718_coint-shell-signbug-costcliff.md`

这样写的原因：
- 当前存在真实可执行的前排 survivor 收口动作，优先级高于任何新的发现；
- 没有 `P3` 与 `Active P2`，所以剩余预算可以诚实切回 fresh intake；
- fresh intake 部分只写具体对象，不写抽象模板，也不把 background pool 旧候选重新拉回前排。

## 对 `BOT2_BOT3_STATE.md` 的具体改写

- 保持：
  - `Paper launch queue.current_target = none`
  - `Active P2.current_target = none`
- 更新：
  - `Fresh intake slot.current_target -> research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
  - `Surviving candidate slot` 继续锁定 `Rank 350`，并把 follow-up 描述改成明确出口决策句式
  - `cycle_plan` 重写为 `1 个 survivor follow-up + 3 个具体 fresh intake`
- 新计划项全部保持：`result = none`、`status = pending`。

## P2 -> P3 兜底检查

- 本轮没有明确 `Active P2`。
- 因此不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 执行补记

- `docs/BOT2_BOT3_STATE.md` 已按本轮 review 写回。
- repo 状态显示大量历史未跟踪文件，但本轮仅将其作为环境证据，不反向改 policy，也不据此重排 background pool。
- 最近有效证据主要来自：
  - `research/optimization_loop/2026-04-06_0826_rank350_btc_lead_low_liquidity_alt_lag_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0854_rank351_rf_threshold_bucket_hf_pairs_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-06_0812_rank349_survivor_followup_funding_basis_persistence_background_p0.md`

## 一句话结论

本轮前排真实动作只有 `Rank 350` 的 survivor 出口决策；`P3` 为空、`Active P2` 为空，因此正确排班不是开放式重读，而是把 `Rank 350` 放在第一位收口，再用剩余预算按具体对象切回新的 `fresh intake`。