# 2026-03-31 13:32 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；只读取 policy、runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 仍写明 `Paper launch queue.current_target: none`；当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`anchor-low reversal gate`**。
   - 证据：这是本轮最新一条已经正式执行并写回 runtime 的 fresh intake；`research/optimization_loop/2026-03-31_1321_anchor_low_reversal_gate_fresh_intake_background_p0.md` 已完成首判，并明确写成 `不进入前排，回 background/P0`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且已经用完；不再有第二次。**
   - 对象：`Rank 267 / crypto factor momentum × size/vol rotation`。
   - 证据链：
     - `2026-03-31_0946_rank267_survivor_followup_promote_p2.md`：唯一一次 survivor follow-up 已用掉，并把对象推入 `P2`；
     - `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md`：P2 出口不是 `P3`，而是一次性 `P2->P1 re-scope`；
     - `2026-03-31_1308_rank267_rescoped_survivor_followup_keep_p1.md`：re-scoped survivor follow-up 已诚实收口，结论是窄版对象可保留为 `P1`，但预算已用尽。
   - desk review 判断：`Rank 267` 没达到可被 bot2 兜底直推 `P3` 的门槛，因为 broad-crypto/majors 主语不诚实；但它也不是 fatal flaw，最诚实收口是把它从 survivor 前排移出，承认为 `background/P1` 窄版候选，而不是继续占用 survivor 槽位。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 已把唯一 active P2 正式收口为一次性 `P2->P1 re-scope`；之后 `2026-03-31_1308_rank267_rescoped_survivor_followup_keep_p1.md` 又用掉了这条 re-scoped survivor 的唯一 follow-up。
   - 因而当前不存在离 `P3 / P1 / P0` 最近的 active P2；最近一次离开 `P2` 的对象 `Rank 267`，其真实出口是 **`P1`**，且该出口动作现已完成，不再是本轮前排动作。

## rank / 前排合法性检查

- `Paper launch queue`: `none`
- `Fresh intake slot`: `anchor-low reversal gate`，本身未获 `keep_P1` 以上 verdict，因此不需要 rank
- `Surviving candidate slot`: 本轮应清空为 `none`
- `Active P2 slot`: `none`
- 结论：**本轮前排无缺失 rank 的合法对象，无需补号。**

## 为什么本轮不触发 `P2 -> P3` 兜底直推

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 `paper trade / paper launch`，而 bot3 没升，bot2 必须直接写入 `P3 / Paper launch queue` 或 handoff 路径。

本轮复核后，**不存在这样的对象**：
- `Active P2` 已清空；
- 唯一最近的 P2 对象 `Rank 267` 虽然不是假象，也不是 fatal flaw，但 broad-crypto 主语不诚实，真实有效范围只剩 `ex-majors high-liquidity alt basket` 的慢频轮动；
- 因此 bot2 不能把它硬写进 `P3`，只能承认它已经完成 `P2->P1 re-scope + 唯一 survivor follow-up`，当前应退出前排。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor`：无，`Rank 267` 的唯一 re-scoped survivor follow-up 已用尽；
4. 因此前排已诚实收口，本轮应切回 **具体 fresh intake**。

所以本轮把 `cycle_plan` 重写为 4 条具体 intake：
1. `moving-band basket stat-arb × 线性 inventory shell`
2. `dynamic boundary RL pairs`
3. `asynchronous funding clock × net-hour hurdle`
4. `cointegration pair + graduation + daily throttle`

它们都来自最近的新 digest/repo/paper 证据，且不涉及从 background pool 自动 reopen 旧对象。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 把 `Fresh intake slot` 改写为最新已完成首判的 `anchor-low reversal gate`；
  - 把 `Surviving candidate slot` 清空为 `none`，承认 `Rank 267` 的唯一合法 follow-up 已经用尽；
  - 保持 `Active P2 slot = none`、`Paper launch queue.current_target = none`；
  - 按 policy 默认顺序把本轮 `cycle_plan` 重写为 4 条具体 fresh intake。
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
