# stablecoin discount → peer-parity reversion — 本轮 blocked（被 Rank 270 survivor lock 拦截）

- 时间：2026-03-31 16:59 UTC
- 对应 cycle_plan 小点：`research/quant_digests/2026-03-31_1617_stablecoin-discount-parity-reversion-alpha.md`
- 执行动作：检查当前最前的 pending 小点是否仍具备合法执行前置条件

## 本轮为什么不能执行这条 intake
按 `BOT2_BOT3_POLICY.md`：
- `Surviving candidate` 只能是上一条 fresh intake；
- 其唯一一次 decisive follow-up 在诚实收口前，默认享有前排锁定权；
- bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位；
- 若当前 `state` 与 policy 冲突，bot3 应拒绝执行歪路径，回退到合法动作。

当前 runtime truth 明确显示：
- `Surviving candidate slot.current_target = Rank 270 / front/back annualized basis calendar spread`
- `followup_budget_remaining = 1`
- `Active P2 slot.current_target = none`
- `Paper launch queue.current_target = none`

这意味着当前仍有一个合法、具体、尚未执行的 survivor follow-up 应优先于任何新的 fresh intake。
因此，`cycle_plan` 第 3 项虽然写成 pending，但它的前置条件其实已经不成立：

> 在 `Rank 270` 的 survivor follow-up 还没收口之前，不能把 `stablecoin discount → peer-parity reversion` 拉进前排做新的 fresh intake。

## 本轮唯一写回的 runtime 结论
`stablecoin discount → peer-parity reversion` 这条 intake 不是被判死，也不是完成首判；它只是因为前排仍被 `Rank 270` 的 survivor lock 合法占用，所以 **本轮前置条件不成立**。

因此本轮把 `cycle_plan` 第 3 项写成：
- `status: blocked`
- `result: 当前仍存在合法且未执行的唯一 survivor Rank 270 follow-up 锁；按 policy 新的 fresh intake 不得覆盖 survivor 前排权，因此这条 stablecoin discount → peer-parity reversion intake 本轮前置条件不成立，先标记为 blocked，等待 Rank 270 诚实收口后再由 bot2 重新排班。`

## 对对象本身的处理边界
本轮 **没有** 对 `stablecoin discount → peer-parity reversion` 给出新的 rank、层级或 fresh verdict，原因不是对象质量不足，而是：
- 这会违反 survivor 前排锁定规则；
- bot3 本轮只允许处理当前这个合法性判断，不得借机重排剩余任务。

## 后续应如何进入前排
只有在以下条件之一成立后，这条对象才应被重新评估是否进入前排：
1. `Rank 270` 的 survivor follow-up 已完成并诚实收口；
2. bot2 基于新的 runtime truth 重写 `cycle_plan`，并把这条对象重新排到合法位置。

本轮无新 verdict、无新 rank、无层级迁移；因此只写内部日志，不额外要求新的 reader-facing 页面刷新。