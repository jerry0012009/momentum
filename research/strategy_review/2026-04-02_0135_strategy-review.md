# Strategy Review — 2026-04-02 01:35 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核最近运行证据：
- `research/optimization_loop/2026-04-02_0007_rank285_survivor_followup_promote_p2.md`
- `research/optimization_loop/2026-04-02_0026_rank286_calendar_spread_keep_p1.md`
- `research/optimization_loop/2026-04-02_0040_rank286_survivor_guard_blocks_copula_fresh_intake.md`
- `research/optimization_loop/2026-04-02_0107_guard_blocked_microprice_obi_fresh_intake.md`
- 上一轮 review：`research/strategy_review/2026-04-02_0004_strategy-review.md`

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，仍为空。
- `current_target = none`。
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`，最新 queue 结果仍是 `Rank 229` 已完成 wiring 并清空 queue 头，没有新的待接线对象。

### 2) 本轮 `fresh intake` 是什么？
- 本轮 runtime 中最新完成首判的 fresh intake 是：
  - `research/quant_digests/2026-04-01_2252_adjacent-maturity-calendar-spread-alpha.md`
  - 已写成 `Rank 286 / adjacent-maturity calendar-spread ratio dislocation × carry normalization`
- 最近证据表明它已经具备可独立审计的 `futures-curve relative-value raw alpha skeleton`，所以首判是 `keep_P1`，而不是 `P0`。
- 但它还没有公开 dated futures 上的 clean-room after-cost replication，因此还不能诚实直升 `P2`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且按 policy 现在就该占住 survivor 前排锁。
- 上一条 fresh intake 就是 `Rank 286` 本身；它刚完成首判并进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 这唯一一次 follow-up 应直接回答一个决定性问题：
  - 在公开可拿的 BTC / ETH dated futures 上，`days-normalized adjacent-maturity spread ratio` 的回归，在 `realistic fee / roll / legging friction` 后是否仍保留净 pocket。
- 最近两条 blocked 日志也证明了这一点：后续 copula / microprice 两条新 intake 都因为 `Rank 286` survivor front-lock 尚未收口而被 policy 正常拦下。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 有，当前明确 `Active P2 = Rank 285 / 24h losers-vs-winners XS reversal × dispersion / turnover`。
- 从最近证据看，它已经跨过了最关键的 `survivor` 问题：
  - 原始 daily spot shell 虽不可交易；
  - 但 liquid perp 的 mature tail / high-RV lower-turnover 子口袋里，已经出现现实 after-cost 生存证据。
- 因此它当前**离 `P3` 最近**，不是离 `P1` 或 `P0` 最近。
- 但这还不是 bot2 兜底直推 `P3` 的时点，因为当前只明确回答了 `pocket existence / transfer viability`，还没有把 `effectiveness / cross-asset / time / parameter / honesty` 五轴 admission 诚实补齐。
- 所以本轮最正确的动作不是开放式继续研究，也不是草率升级，而是把 `Rank 285` 明确排成 `P2 admission + exit framing`，优先验证它是否已经足够进入 `P3 / Paper launch queue`。

## Rank 完整性检查
- `Paper launch queue`: 无当前 target，无 rank 冲突。
- `Active P2 slot`: `Rank 285`，已有正式 rank。
- `Surviving candidate slot`: `Rank 286`，已有正式 rank。
- 当前前排对象不存在“已到 keep_P1/P2/P3 但无 rank”的问题，因此本轮无需补新 rank。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一 follow-up > fresh intake > P0`。

当前合法前排链条非常清楚：
1. 没有 `P3` queue 头要接线；
2. 有一个明确 `Active P2 = Rank 285`，而且它离 `P3` 最近；
3. 有一个明确 `Surviving candidate = Rank 286`，其唯一 follow-up 尚未执行；
4. 因此前两优先级必须都排给 `Rank 285` 的 admission/exit，第三优先级给 `Rank 286` 的 survivor follow-up；
5. 只有把这些真实前排动作诚实排进本轮前部后，才允许补 1 条 conditional fresh intake。

## 已写回 `BOT2_BOT3_STATE.md` 的新 `cycle_plan`
1. `Rank 285`：先做 `effectiveness / cross-asset stability` admission
2. `Rank 285`：再做 `time / parameter / honesty-execution realism` admission，并明确出口是否已足够 `P3`
3. `Rank 286`：执行唯一 survivor follow-up，直接回答 dated futures clean-room after-cost 是否还能存活
4. `research/quant_digests/2026-04-02_0117_binance-polymarket-lagged-binary-mispricing-alpha.md`：仅作为当前前排链条已诚实排入后的 conditional fresh intake

## 结论
- `Paper launch queue`：空
- 本轮 fresh intake：`Rank 286 / adjacent-maturity calendar-spread ratio dislocation × carry normalization`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且现在必须执行
- 当前明确 `Active P2`：有，`Rank 285`
- `Rank 285` 目前离 `P3` 最近，但尚未达到 bot2 必须直接兜底推进到 `P3` 的门槛；本轮应先把 admission 五轴补成出口决策，而不是继续散写开放式研究
