# 2026-03-31 14:34 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；只读取 fixed policy、runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`dynamic boundary RL pairs`。**
   - 证据：runtime 的 `Fresh intake slot.current_target` 仍是 `dynamic boundary RL pairs`，且 `latest_result` 已明确写成：它不是新的独立 crypto raw alpha，而是旧 `pairs/stat-arb` 家族外再包一层 `dynamic band / RL action` 治理壳，因此本轮首判为 `不进入前排，回 background/P0`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得。**
   - 对象：`Rank 268 / moving-band basket stat-arb × 线性 inventory shell`。
   - 证据：
     - `2026-03-31_1339_rank268_moving_band_basket_statarb_intake_keep_p1.md` 已把它正式记为 fresh intake，并分配 `Rank 268`；
     - intake 结论不是“论文表现很好”，而是它已经具备独立可审计的 `moving-band basket + linear inventory shell` raw alpha 骨架；
     - 当前缺口只剩受控 crypto universe 下的最小 after-cost replication 是否成立，因此它正好符合 policy 允许的那唯一一次 survivor follow-up。
   - desk review 判断：这一次 follow-up 应直接回答 transfer 是否成立，以及 `Rank 268` 的真实出口是 `P2` 还是 `background/P1/P0`；不应继续把新的 fresh intake 拉到它前面。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`Rank 267` 已在 `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 完成 `P2 -> P1` 一次性 re-scope，并在 `2026-03-31_1308_rank267_rescoped_survivor_followup_keep_p1.md` 用掉该窄版对象唯一的 survivor follow-up；runtime 也已明确写成 `Active P2 slot.current_target: none`。
   - 因而当前不存在离 `P3 / P1 / P0` 最近的 active P2；最近一次离开 `P2` 的对象 `Rank 267`，真实出口是 **`P1`**，且该出口动作已完成，不应再占本轮前排资源。

## rank / 前排合法性检查

- `Paper launch queue`: `none`
- `Fresh intake slot`: `dynamic boundary RL pairs`，已判 `background/P0`，无需 rank
- `Surviving candidate slot`: `Rank 268`，已有正式 rank
- `Active P2 slot`: `none`
- 结论：**当前前排合法对象不存在缺失 rank 的情况，无需补号。**

## 为什么本轮不触发 `P2 -> P3` 兜底直推

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 `paper trade / paper launch`，而 bot3 没升，bot2 必须直接把它写入 `P3 / Paper launch queue` 或 handoff 路径。

本轮复核后，**不存在这样的对象**：
- 当前 `Active P2 = none`；
- 最近一个 `P2` 对象 `Rank 267` 已经诚实收口为一次性 `P2 -> P1 re-scope`，不是该被兜底直推 `P3` 的对象；
- 当前真正需要收口的前排对象是 `Rank 268` 的 survivor follow-up，而不是某个遗漏升级的 `Active P2`。

因此本轮 bot2 不应伪造 `P3`，而应把 survivor follow-up 放回当前轮第一优先级。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor`：有，`Rank 268` 仍保留 1 次合法 follow-up，且这一步必须先收口；
4. 只有在上面的 survivor 已于当前轮前部被诚实排入后，才允许继续补新的 `fresh intake`。

因此本轮把 `cycle_plan` 重写为：
1. `Rank 268` survivor follow-up（受控 crypto universe 的 after-cost replication / transfer 决策）
2. `asynchronous funding clock × net-hour hurdle`
3. `cointegration pair + graduation + daily throttle`
4. `front/back annualized basis calendar spread`

这满足 policy：已有前排对象先收口；后续 fresh intake 都是具体对象，不是抽象占位。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue.current_target = none`、`Active P2 slot = none`；
  - 保持 `Surviving candidate slot = Rank 268`，不让新的 fresh intake 覆盖 survivor 锁；
  - 把当前轮 `cycle_plan` 按 policy 默认顺序重写为：`Rank 268 survivor follow-up > async funding carry intake > cointegration graduation intake > front/back basis intake`；
  - 所有新生成 cycle item 都按要求写成 `result: none`、`status: pending`。
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
