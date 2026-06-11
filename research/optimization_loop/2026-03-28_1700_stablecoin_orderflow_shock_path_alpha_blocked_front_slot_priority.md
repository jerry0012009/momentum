# Rank pending / stablecoin signed order-flow shock path alpha — blocked（front-slot priority guard）

- 时间：2026-03-28 17:00 UTC
- 轮次：bot3 13 分钟自动执行
- 对象：`research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
- 动作：按当前 `cycle_plan` 第 2 项尝试执行 fresh intake 首判
- 结论：**blocked**

## 为什么本轮不能执行

根据 `docs/BOT2_BOT3_POLICY.md`：

1. 前排合法动作优先级固定为 `P3 -> Active P2 -> Surviving candidate -> Fresh intake`；
2. 只有当 `P3 / P2 / P1` 都没有真实可执行动作，或它们已经在当前轮前部被诚实排入并等待 bot3 依次执行时，bot2 才能继续补新的 `fresh intake`；
3. `Surviving candidate` 的唯一 follow-up 在诚实收口前，默认享有前排锁定权。

当前 runtime truth 显示：

- `Surviving candidate slot = Rank 226 / IV quantile confirmation / veto`
- `followup_budget_remaining = 1`
- 且该对象的合法下一步已经明确写成：
  - 对现成 `5m/15m` continuation / fade baseline 做一次 BTC/ETH 同口径 after-cost A/B，验证 `iv_q × ivchg` 是否留下独立净增益。

因此，第 2 项里“若第 1 项完成且前排仍无新的 survivor / P2 / P3 动作”这一前置条件 **并未满足**；在 Rank 226 的 survivor follow-up 未被 bot2 诚实排入并收口前，直接继续执行新的 stablecoin order-flow fresh intake 会违反当前固定 priority ladder。

## 本轮写回 runtime 的系统结论

`research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md` 本轮不做首判；原因不是对象本身失效，而是当前前排仍存在 `Rank 226` 的 survivor follow-up，故该 fresh intake 小点按 policy 被收口为 `blocked`。
