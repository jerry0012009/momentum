# bot3 guard — Rank 286 survivor front-lock blocks copula fresh intake

- 时间：2026-04-02 00:40 UTC
- 本轮执行对象：`research/quant_digests/2026-04-01_2218_btc-reference-copula-pairs-mispricing-alpha.md`
- 执行类型：`cycle_plan` 第一个 pending 小点合法性检查

## 本轮结论

本小点未进入实质首判，直接记为 `blocked`。

原因不是对象本身有 fatal flaw，而是当前 runtime 与 fixed policy 冲突：

1. `Fresh intake slot` 刚在上一小点完成 `Rank 286` 首判并写成 `keep_P1`；
2. 按 policy，`Surviving candidate` 只能是**上一条 fresh intake**，且其唯一一次 follow-up 在诚实收口前默认享有前排锁定权；
3. 当前 state 已明确 `Surviving candidate slot = Rank 286`，且 `followup_budget_remaining = 1`；
4. 在这种情况下，把新的 copula pairs digest 继续作为默认 fresh intake 排到前面，会越过现存 survivor 的合法优先级。

因此，bot3 本轮按兜底规则拒绝执行这条歪路径，不对该 copula 对象做新 rank / 新 verdict / 新层级写回，只把当前小点标记为：

> `blocked: Rank 286 survivor follow-up still owns the front slot; new fresh intake cannot preempt it.`

## 对 runtime 的影响

- `cycle_plan` 第 3 项状态已改为 `blocked`
- `result` 已写明：阻塞原因为 `Rank 286` survivor 前排锁定权尚未收口
- 其他槽位与层级保持不变：
  - `Active P2 slot` 仍为 `Rank 285`
  - `Surviving candidate slot` 仍为 `Rank 286`
  - 未分配新 `Rank`
  - 未产生新 fresh-intake first verdict

## 为什么这里不能偷跑

这不是 desk review，也不是重排轮次。当前指令要求 bot3：

- 只执行最前面的合法小点；
- 若 `state` 与 `policy` 冲突，直接回退到合法动作；
- 不得因为 backlog 里还有新 digest 就绕开现有 survivor。

所以本轮最诚实的执行就是：把这条 pending fresh-intake 小点当场拦下，而不是假装它在当前轮仍然合法。
