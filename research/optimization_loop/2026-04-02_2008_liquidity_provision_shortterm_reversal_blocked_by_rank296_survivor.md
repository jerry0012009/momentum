# 2026-04-02 20:08 UTC — bot3 guard: liquidity-provision short-term reversal fresh intake blocked by unresolved Rank 296 survivor

- 本轮执行槽位：`cycle_plan` 第 2 条（当前最前 `pending`）
- 拟执行对象：`research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`
- 当前 `Surviving candidate slot`：`Rank 296 / BTC next-day CIDR curve timing`
- `followup_budget_remaining`: `1`
- 依据：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`

## 为什么这一步现在不能合法执行
当前 runtime 明确写着：
- 最新 fresh intake 已经在上一小点收口为 `Rank 296`；
- `Rank 296` 目前正占用唯一的 `Surviving candidate slot`；
- 其 survivor follow-up 预算仍剩 `1`，说明前排链条还没有诚实收口。

按 policy：
- 已有前排对象（尤其 `Surviving candidate`）的收口优先级高于新的 `fresh intake`；
- bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位；
- 当最前 pending 小点的前置条件不成立时，bot3 可以把该小点直接写成 `blocked`，而不是自行重排或越过前排对象。

因此，这条 `liquidity provision short-term reversal × cost cliff` 目前**不是被研究结论否掉**；它只是还轮不到被正式执行 first verdict。只要 `Rank 296` 的 survivor 唯一 follow-up 尚未收口，bot3 就不能合法地为下一条 fresh intake 分配新 `Rank` 或产出 `keep_P1/P2/P0` 正式结论。

## 本轮会改变系统认知的一句话
`liquidity provision short-term reversal × cost cliff` 当前不能进入正式 fresh-intake 首判；唯一合法的新结论是：`Rank 296` 仍占据 survivor 前排锁，故该小点因前置条件不成立而被标记为 `blocked`。
