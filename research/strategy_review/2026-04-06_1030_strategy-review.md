# 2026-04-06 10:30 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `Rank 342` 已完成最小 `P3 launch wiring`，正式写回 `connected_runner_live`；当前没有新的 queue 头对象等待接线。

2. **本轮 `fresh intake` 是什么？**
   - 当前 head fresh intake 是：
   - `research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
   - 理由：`Rank 350` 的 survivor 已在 10:02 UTC 诚实收口并退回 `background / P0`，当前前排已无 `P3 / Active P2 / Surviving candidate` 动作，所以排班切回最前面的未执行具体 intake；之后再补更近的 `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`、`2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 是。
   - 上一条 fresh intake 是 `Rank 350 / BTC lead × low-liquidity alt lag`。
   - 它在 `research/optimization_loop/2026-04-06_0826_rank350_btc_lead_low_liquidity_alt_lag_first_verdict_keep_p1.md` 已把主语压成独立 raw alpha：`BTC 先发现 + 低流动性 alt 慢半拍补价`，因此确实值得且必须享有那唯一一次 survivor follow-up。
   - follow-up 已在 `research/optimization_loop/2026-04-06_1002_rank350_survivor_followup_tradable_alt_bucket_after_cost_background_p0.md` 收口；结论是优势只清楚活在超薄 `1m` 小币桶，未证明在可成交 alt bucket 与明确 after-cost 下保留可迁移净增量，所以不升 `P2`，退回 `background / P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - 最近的 `Active P2` 是 `Rank 342`，它已经完成 `P2 -> P3`，随后 runner / scheduler / 首跑验证都落地并写回 `connected_runner_live`；因此当前不存在仍需 bot2 兜底裁决的 `P2`。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = none`
  - `Active P2 = none`
  - `Fresh intake head = research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
- 前排不存在 `keep_P1 / P2 / P3` 但无正式 rank 的对象。
- 本轮**无需补 rank**。

## 最近证据与排班判断

本轮先看 fixed policy/state，再看 repo 状态、最近 optimization_loop 与最近 strategy_review：

- `research/optimization_loop/2026-04-06_1002_rank350_survivor_followup_tradable_alt_bucket_after_cost_background_p0.md`
  - 说明上一条 survivor 已经诚实收口，不再占前排。
- `research/optimization_loop/2026-04-06_0854_rank351_rf_threshold_bucket_hf_pairs_first_verdict_background_p0.md`
  - 说明 `RF threshold-bucket × HF pairs` 已被判定为更像旧 pairs alpha 的参数分层，不值得保留前排。
- repo 最近新增 digest 显示 fresh intake 供应充足，且有更近的新对象：
  - `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
  - `2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
  - `2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
  - `2026-04-06_0843_binance-l2-feeaware-as-maker-alpha.md`

按 policy 的 authoritative 顺序扫描：

1. **P3 handoff**：无待接线对象。
2. **P2 admission / promote / park**：`Active P2 = none`。
3. **P1 survivor follow-up**：`Rank 350` 已在本轮前完成并收口，当前 survivor 槽为空。
4. **fresh intake**：因此本轮预算应全部切回新的具体 intake，对象必须具体、不能写抽象模板。

## 对 `BOT2_BOT3_STATE.md` 的具体改写

已写回：

- 保持：
  - `Paper launch queue.current_target = none`
  - `Active P2.current_target = none`
- 确认：
  - `Surviving candidate slot.current_target = none`
  - `followup_budget_remaining = 0`
  - `latest_result` 继续记载 `Rank 350` 已收口退回 `background / P0`
- 重写本轮 `cycle_plan` 为 4 条具体 `fresh intake`：
  1. `2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
  2. `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
  3. `2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
  4. `2026-04-06_0843_binance-l2-feeaware-as-maker-alpha.md`
- 新计划项全部保持：`result = none`、`status = pending`。

## P2 -> P3 兜底检查

- 本轮没有明确 `Active P2`。
- 因此不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 一句话结论

本轮前排链条已经诚实收口：`Paper launch queue` 为空、`Active P2` 为空、`Rank 350` survivor 已退回 `background / P0`；因此正确排班不是再拖旧对象，而是把当前轮全部预算切回具体的新 `fresh intake`，从 `btc-perp-conditional-drift` 开始，随后依次检查 `volume-anomaly-bandfade-hmm-veto`、`quality-weighted-squeeze-release`、`binance-l2-feeaware-as-maker`。
