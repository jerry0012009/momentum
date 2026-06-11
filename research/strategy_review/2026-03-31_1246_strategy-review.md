# 2026-03-31 12:46 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；只读取 policy、runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 仍写明 `Paper launch queue.current_target: none`；`Rank 200 / 201 / 213 / 229` 都已在 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮最近一条已正式写回 runtime 的 fresh intake 仍是 **`Rank 267 / crypto factor momentum × size/vol rotation`**。
   - 证据：`research/optimization_loop/2026-03-31_0915_rank267_crypto_factor_momentum_sizevol_rotation_intake_keep_p1.md` 完成首判，随后 `2026-03-31_0946_rank267_survivor_followup_promote_p2.md` 用掉上一条 fresh intake 的 survivor follow-up 并升入 `P2`；当前还没有新的对象完成正式 intake 写回，所以 fresh intake 仍应回答 `Rank 267`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得；而且当前最诚实的 follow-up 目标，已经从原 broad-crypto 主语收窄成一次性 `P2->P1 re-scope` 后的窄版 survivor 检查。**
   - 证据：
     - `2026-03-31_1044_rank267_p2_cross_asset_blocker_alt_pocket.md` 证明它不是单一币幻觉，但 `BTC/ETH/SOL majors` 单独并不成立，净边主要来自 `ex-majors` 高流动 alt basket；
     - `2026-03-31_1134_rank267_p2_time_stability_passed_but_cross_asset_blocker_remains.md` 证明时间维度过关；
     - `2026-03-31_1207_rank267_p2_parameter_honesty_passed_enter_final_exit_decision.md` 证明最优结果不是单一点参数，且未见致命 honesty flaw；
     - `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 最终把对象诚实收口为一次性 `P2->P1 re-scope`：只保留 `ex-majors high-liquidity alt basket`、`72h~7d` 排序、`12h~24h` 持有、`1d~5d` rotation 这条慢频主语。
   - 因此，上一条 fresh intake 不是“应该继续开放式研究”，而是**值得那唯一一次 follow-up，并且这次 follow-up 现在应当专门检验 re-scoped 窄版对象本身是否站得住。**

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 已把 `Rank 267` 的 P2 出口正式收口为 `one-time P2->P1 re-scope`，因此 active P2 槽位已清空。
   - 补充判断：如果要问“刚刚离开 P2 的那个对象更接近哪个出口”，答案是 **`P1`**，不是 `P3` 也不是 `P0`；因为 desk review 已清楚表明 broad-crypto / majors 主语不诚实，但收窄到 `ex-majors` 慢频轮动后仍未被判死。

## rank / 前排合法性检查

- `Paper launch queue`: `none`
- `Fresh intake slot`: `Rank 267`，已有正式 rank
- `Surviving candidate slot`: `Rank 267`，已有正式 rank
- `Active P2 slot`: `none`
- 结论：**本轮前排对象都已有正式 `Rank`，无需补号。**

## repo / recent evidence quick notes

- `git status --short --branch` 显示 repo 中有大量未跟踪研究产物；本轮只把它当作最近研究活动背景，不据此改 policy，也不据此把旧对象从 background pool 拉回前排。
- 最近 `optimization_loop` 的关键证据链仍集中在 `Rank 267`：
  - `2026-03-31_1044_rank267_p2_cross_asset_blocker_alt_pocket.md`
  - `2026-03-31_1134_rank267_p2_time_stability_passed_but_cross_asset_blocker_remains.md`
  - `2026-03-31_1207_rank267_p2_parameter_honesty_passed_enter_final_exit_decision.md`
  - `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md`
- 最近 `quant_digests` 里，当前最值得排到 fresh intake 候选的是：
  - `2026-03-30_2256_anchor-low-reversal-gate-alpha.md`
  - `2026-03-31_1234_moving-band-basket-statarb-alpha.md`
  - `2026-03-31_1155_dynamic-boundary-rl-pairs-alpha.md`

## 为什么本轮不触发 `P2 -> P3` 兜底直推

policy 要求：若 desk review 已清楚表明对象足够值得进入 paper trade / paper launch，而 bot3 没升，bot2 必须直接改写到 `P3 / handoff`。本轮专门复核后，结论仍然是：**`Rank 267` 还不够。**

- 支持它继续留在前排、而不是直接掉回背景的证据已经够了：
  - 不是单一币幻觉；
  - 时间稳定性已通过；
  - 参数面不是单一点；
  - honesty 未见致命 flaw。
- 但阻止它被直接升 `P3` 的 blocker 也仍然明确：
  - `majors` 单独不成立；
  - 当前净边主要来自 `ex-majors high-liquidity alt basket`；
  - 因而当前 broad-crypto 主语不诚实，paper-ready 主语还没有在更干净的 scope 上被正式站稳。

所以本轮 bot2 的责任不是把它继续拖成开放式研究，也不是硬推 `P3`，而是**承认它已经从 `P2` 收口回 `P1`，并把唯一合法前排动作改写成 re-scoped survivor follow-up。**

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor`：有，而且唯一合法对象就是 `Rank 267` 的 re-scoped survivor follow-up；
4. `fresh intake`：只能排在该 survivor 之后；
5. 前排诚实收口后，再补新的具体 intake 对象。

因此本轮把 `cycle_plan` 重写为：
1. `Rank 267 / ex-majors high-liquidity alt basket factor momentum × size/vol rotation`：执行唯一一次 re-scoped survivor follow-up；
2. `anchor-low reversal gate`：作为第一条新的 fresh intake；
3. `moving-band basket stat-arb × 线性 inventory shell`：作为第二条条件式 fresh intake；
4. `dynamic boundary RL pairs`：作为第三条条件式 fresh intake。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 删除上一轮已完成的 `Rank 267` P2 admission / exit 决策项；
  - 把当前前排唯一合法动作重写为 `Rank 267` 的 re-scoped survivor follow-up；
  - 按新近 alpha 报告顺序重排剩余 intake 候选为 `anchor-low` → `moving-band basket stat-arb` → `dynamic boundary RL pairs`。
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮未触发 `P2 -> P3` 兜底直推，因为现有 desk review 仍不足以诚实宣称 `Rank 267` 已达 paper launch 门槛
