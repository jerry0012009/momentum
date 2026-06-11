# Strategy Review — 2026-04-04 22:50 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_2245_rank335_dual_momentum_breakout_expansion_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_2207_rank334_survivor_followup_ga_pair_label_veto_background_p0.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_2141_strategy-review.md`
  - `research/strategy_review/2026-04-04_2037_strategy-review.md`
- 新近 digest 候选：
  - `research/quant_digests/2026-04-04_2057_deribit-putcall-perp-parity-alpha.md`
  - `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
  - `research/quant_digests/2026-04-04_2203_extreme-funding-tail-carry-alpha.md`

## repo 状态摘录
- `jerry/momentum` 工作树仍有大量未跟踪 research / tmp / artifact 文件；这些只作环境 evidence，不改变本轮排班。
- 本轮遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮最新完成 first verdict 的 fresh intake 是 `Rank 335 / dual momentum breakout expansion`。**
- 依据：`research/optimization_loop/2026-04-04_2245_rank335_dual_momentum_breakout_expansion_first_verdict_keep_p1.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在正占用那唯一一次 follow-up。**
- `Rank 335` 的 first verdict 已经把对象收口成清楚的 raw alpha 主语：`20-bar breakout + 20/60-bar dual momentum + ATR expansion + bull-regime gate`。
- 当前唯一该回答的 decisive question 也很明确：在固定 `1h regime -> 15m execution` 架构、限定 `BTC/ETH` 或最小 top-N ranking discipline 后，它是否仍保留可辩护 raw alpha 主体，并足以升到 `P2`；若不能，就应直接收口到 `background/P0`。
- 因此这条对象依法享有 survivor 前排锁定权，新的 fresh intake 不得排到它前面。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 是 `Rank 331`，已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 中被明确收口到 `P0`；因此当前没有需要继续判 `P3 / P1 / P0` 出口的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 335`
- `Active P2 slot.current_target = none`
- 当前前排对象全部带正式 `Rank`，不存在需要补 rank 的前排对象。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 升级。
- 原因：当前没有 `Active P2`；最近 P2（`Rank 331`）已被 admission 证据明确否决，不存在“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且只有 `Rank 335` 的 survivor 唯一一次 follow-up

因此本轮 `cycle_plan` 必须先把 `Rank 335` 的 survivor follow-up 放回首位，再把新的 fresh intake 诚实排在后面。重写后的 4 项为：

1. `Rank 335 / dual momentum breakout expansion` survivor follow-up
2. `research/quant_digests/2026-04-04_2057_deribit-putcall-perp-parity-alpha.md`
3. `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
4. `research/quant_digests/2026-04-04_2203_extreme-funding-tail-carry-alpha.md`

这样排的理由：
- 前排 `P1` 仍有合法且必须优先执行的收口动作；
- `Paper launch queue` 与 `Active P2` 当前都为空，不存在更高优先级的 handoff / admission 出口动作；
- 新的 fresh intake 只能在 survivor follow-up 已被诚实排入之后占据后续槽位；
- fresh intake 来源优先采用最近新的 alpha 报告，且都是真实、具体、可执行对象，不含抽象模板或空占位。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Fresh intake slot = Rank 335`
- 保持 `Surviving candidate slot = Rank 335`，`followup_budget_remaining = 1`
- 保持 `Active P2 slot = none`
- 重写 `cycle_plan`，把 `Rank 335` survivor 唯一 follow-up 放回第 1 位；其余 3 项改为最近、具体的新 fresh intake 对象

## 本轮结论一句话
当前没有 `P3` 也没有 `Active P2`，唯一必须优先收口的是 `Rank 335`；所以 bot2 已把 runtime 改成合法顺序：先做 `Rank 335` 的 survivor follow-up，再轮到最新三条 fresh intake。
