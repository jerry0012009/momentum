# Rank 163 survivor slot 纠偏 — 写回唯一合法 survivor

- 时间：2026-03-25 11:31 UTC
- 轮次角色：bot3 cycle_plan 第 2 小点执行
- 对象：`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha`
- 相关旧对象：`Rank 162 / Kalman β-gap cross-sectional raw alpha`
- 本轮动作：按 policy 把上一条 fresh intake 写成新的唯一合法 survivor，并把唯一一次 follow-up 收口成单一 decisive blocker

## 触发原因
当前 runtime state 与 policy 冲突：
- policy 明确规定 **Surviving candidate 只能是上一条 fresh intake**；
- 当前 fresh intake 已是 `Rank 163` 且 verdict 为 `keep_P1`；
- 但 survivor 仍停留在 `Rank 162`，因此 bot3 本轮必须先回退到合法动作，而不是继续沿旧 survivor 歪路径推进。

## 本轮依据
- `docs/BOT2_BOT3_POLICY.md`：Surviving candidate 只能是上一条 fresh intake，且只能保留 1 次最小 decisive follow-up。
- `docs/BOT2_BOT3_STATE.md`：fresh intake 已在 `2026-03-25_1126_rank163-itsm-pocket-intake.md` 中得到 `keep_P1` 且已分配正式 `Rank 163`。
- `research/optimization_loop/2026-03-25_1126_rank163-itsm-pocket-intake.md`：已经明确写出 survivor 唯一合法 follow-up 的单一 blocker。

## 写回后的 runtime 变化
1. `Surviving candidate slot` 改写为 `Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha`。
2. `followup_budget_remaining` 维持为 `1`，不额外扩表、不开放式补研究。
3. 唯一 allowed blocker 明确收口为：
   - **把 pocket 触发收缩成 `|ret_lb|` threshold，并按 `15m signal / 5m execution` + `4/8/12bps` round-trip 成本阶梯计价后，`post-cost avg bps/trigger` 是否仍稳定为正。**
4. `Rank 162` 不再占用 survivor 前排，按 policy 返回 `Background pool`，除非后续被用户明确 reopen。

## 一句话结果
`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha` 已写成新的唯一合法 survivor；唯一 follow-up blocker 被收口为“threshold 稀疏化 + 15m signal/5m execution 后，在 4/8/12bps 成本阶梯下 `post-cost avg bps/trigger` 是否仍稳定为正”。
