# 2026-04-08 02:59 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 最近 queue 侧完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`

因此当前没有待接线的 `P3 / Paper launch queue` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**严格按当前 runtime truth，本轮 front-slot 上一条 fresh intake 已完成，fresh intake 动作现在应切向 `research/quant_digests/2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md`。**

解释：
- `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md` 已在 `research/optimization_loop/2026-04-08_0212_rank361_spot_perp_openclose_basis_intake_keep_p1.md` 完成 first verdict，并获 `Rank 361`；
- 因为它已拿到 `keep_P1`，它不再属于“待判 first verdict 的 fresh intake”，而已进入 `Surviving candidate slot`；
- 所以前排先做完 `Rank 361` 的唯一一次 survivor follow-up 后，本轮应切回最新、尚未做 first verdict 的新对象，即 `2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的“上一条 fresh intake”就是 `Rank 361 / spot-perp executable basis × open/close hysteresis shell`。

理由已经在 `research/optimization_loop/2026-04-08_0212_rank361_spot_perp_openclose_basis_intake_keep_p1.md` 写清：
- 它已经把主语压清为 **same-underlier executable basis dislocation -> close-spread mean reversion**；
- 有成熟源码级的开/平仓阈值、成本缓冲、状态机、reopen delay 与持仓生命周期定义；
- 当前缺的不是“对象是否存在”，而是**在当前 crypto 可成交 quote 与真实成本口径下，是否真有独立于泛 funding/carry 叙事的 after-cost edge**。

这正好满足 policy 对 survivor 的定义：值得保留且只值得保留 **1 次** 便宜、决定性的 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近一次需要 bot2 兜底裁决的 `P2` 是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`
- 本轮不存在“desk review 已明确够格升 P3、但 bot3 尚未升级”的在场 `Active P2`

因此本轮不存在需要 bot2 直接改写进 `P3 / Paper launch queue` 的漏升对象。

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 工作树：存在大量历史未跟踪研究文件，但这只算 repo hygiene 现状，不构成 background pool 自动 reopen 的理由
4. 最近 optimization 记录：
   - `2026-04-08_0212_rank361_spot_perp_openclose_basis_intake_keep_p1.md`
   - `2026-04-08_0150_rank360_survivor_followup_exhausted_background.md`
   - `2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
5. 最近 strategy review：`2026-04-08_0204_strategy-review.md`
6. 最近新 digest：`2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md`
7. recent park reframe 候选：`Rank 60` 与 `Rank 28`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = Rank 361`，且 `Rank 361` 已有正式 rank，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无 rank 的对象，因此本轮无需补 rank

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：存在明确 survivor，且必须优先于所有新 intake 收口
- survivor 收口后，才允许切回新的 `fresh intake`
- 在没有 `P3/P2` 占位的情况下，剩余预算可补具体 conditional fresh intake

因此原 state 里的 `cycle_plan` 已经不够诚实：它把一个已完成 first verdict 的 `Rank 361` 继续写成 fresh intake 步骤，且没有把 survivor follow-up 放在最高优先级。根据 policy，本轮必须重排。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，改成：

1. `Rank 361 / spot-perp executable basis × open/close hysteresis shell`
   - 先做 survivor 唯一一次决定性 follow-up
2. `research/quant_digests/2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md`
   - 作为切回 fresh intake 后的首条具体对象
3. `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
   - 作为 conditional fresh intake
4. `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
   - 作为剩余预算里的具体 conditional fresh intake

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该条件：
- `Active P2 = none`
- 最近完成的 `Rank 342` 已经在 `connected_runner_live`
- 当前真正需要 bot2 做的是 **把 survivor-first 的运行顺序写回 state**，防止 bot3 跳过 `Rank 361` 的唯一 follow-up 就直接换新 intake

## 一句话总结
本轮没有漏升的 `Active P2`，也没有新的 `P3` 接线对象；唯一需要 bot2 纠偏的是：**先把 `Rank 361` 的 survivor follow-up 提到当前轮最前，再切回 `2026-04-08_0237` fresh intake，其余预算才留给 `Rank 60 / Rank 28` 的 conditional intake 判断。**
