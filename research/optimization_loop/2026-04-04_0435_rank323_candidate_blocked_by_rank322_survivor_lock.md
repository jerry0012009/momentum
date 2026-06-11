# bot3 optimization log — conditional fresh intake blocked by survivor lock

- Time: 2026-04-04 04:35 UTC
- Cycle item: `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
- Decision: `blocked`

## Why blocked
当前最前 pending 小点本身有具体对象，也满足“前两项已诚实收口且预算仍有余”的字面条件；但运行态在第 2 项完成后已经把 `Rank 322 / cointegrated spread z-score × stop-loss/time-exit` 写入 `Surviving candidate slot`，且 `followup_budget_remaining = 1`。

按 `docs/BOT2_BOT3_POLICY.md`：
- 已有前排对象的收口优先级高于新的发现；
- fresh intake 一旦首判为 `keep_P1`，其唯一 survivor follow-up 在诚实收口前享有前排锁定权；
- bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位。

因此，这个 conditional fresh intake 虽然可以阅读，但在当前 survivor 未收口前，bot3 不能合法地产出新的 `keep_P1`/前排迁移动作；继续给它 first verdict 会制造前排竞争并与当前 runtime truth 冲突。

## Result sentence
`vol-z router × TSMOM / XS reversal dual-book` 这条 conditional fresh intake 本轮未被正式 intake，不是因为对象本身已被证伪，而是因为 `Rank 322` 仍持有唯一 survivor 锁，当前轮次对新 intake 的前排承接条件不成立。

## Runtime consequence
- 本轮只把 `cycle_plan` 第 3 项改写为 `blocked`
- 不改写 `Fresh intake slot` / `Surviving candidate slot` 的对象归属
- 不分配新 Rank，因为本轮没有形成合法 `keep_P1` 或更高 verdict
