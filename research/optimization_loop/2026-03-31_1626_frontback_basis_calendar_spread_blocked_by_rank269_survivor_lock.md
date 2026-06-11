# Rank intake blocked：front/back annualized basis calendar spread

- Time: 2026-03-31 16:26 UTC
- Executor: bot3 auto loop
- Cycle item: `research/quant_digests/2026-03-31_1420_frontback-annualized-basis-calendar-spread-alpha.md`
- Outcome: `blocked`

## Why this item is blocked
当前 runtime 仍存在合规且未消耗的一次 `Surviving candidate` follow-up：`Rank 269 / cointegration pair + graduation + daily throttle`，`followup_budget_remaining = 1`。

根据 `BOT2_BOT3_POLICY.md`：
- 已有前排对象的收口优先级高于新的 fresh intake；
- 一旦 fresh intake 首判为 `keep_P1`，其唯一 survivor follow-up 在诚实收口前默认享有前排锁定权；
- bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位。

本轮要执行的 `front/back annualized basis calendar spread` digest，本身已经给出了相当完整的 raw-alpha skeleton：
- 明确的 base alpha：front/back annualized basis convergence；
- 明确的 entry / exit / stop / DTE / sizing / regime 条件；
- 但 after-cost、dated futures fill honesty、same-venue clean-room replication 仍未完成。

因此它最诚实的 first verdict 上限更像 `keep_P1`，而不是可直接 `promote_P2`。在 `Rank 269` survivor 尚未收口前继续执行这个新 intake，会与当前 front-slot 锁冲突，属于不合法动作。

## Result sentence for runtime
`front/back annualized basis calendar spread` 虽已具备可审计的 calendar-spread raw-alpha skeleton，但在 `Rank 269` 的 survivor follow-up 尚未收口前，继续把它作为新的 fresh intake 会与前排锁冲突，因此本轮必须阻断而不是推进到新的 `keep_P1`。

## What changes now
- 不改 policy
- 不改排班顺序
- 只把当前第 2 个 cycle item 标记为 `blocked`
- 等 bot2 在后续 review 中先收口 `Rank 269` survivor，或明确改写本轮合法前排动作后，再重新评估该 digest 是否进入 fresh intake
