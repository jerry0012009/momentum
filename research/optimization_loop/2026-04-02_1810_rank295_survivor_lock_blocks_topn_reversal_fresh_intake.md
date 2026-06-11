# 2026-04-02 18:10 UTC — bot3 blocked: `Rank 295` survivor lock blocks fresh intake `top-N loser reversal × pump-veto × confidence sizing`

## Context
- Cron turn: `bot3-momentum-auto-opt-13m`
- Policy/state read from:
  - `docs/BOT2_BOT3_POLICY.md`
  - `docs/BOT2_BOT3_STATE.md`
- First pending `cycle_plan` item:
  - target: `research/quant_digests/2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
  - action: fresh intake first verdict for `top-N loser reversal × pump-veto × confidence sizing`

## Guard decision
当前运行态仍存在合法且更高优先级的前排对象：
- `Surviving candidate slot = Rank 295 / ETH exchange inflow shock × 1~6h bearish drift`
- `followup_budget_remaining = 1`

按 policy：
1. `Surviving candidate` 只能是上一条 fresh intake，且拥有唯一一次最小 decisive follow-up；
2. 只要当前仍存在合法 `P1 / Surviving candidate` 动作，bot2/bot3 默认不得让新的 fresh intake 抢占前排；
3. 若当前 `state` / `cycle_plan` 与 policy 冲突，bot3 应回退到合法动作，而不是继续执行歪路径。

因此，虽然 `cycle_plan` 第 2 条是当前第一个 `pending` 小点，但它的执行前提并不成立：`Rank 295` 的 survivor follow-up 还未收口，新的 intake 不能在这一轮被 bot3 正式推进到 fresh-intake verdict。

## Result
本轮没有对 `top-N loser reversal × pump-veto × confidence sizing` 产出 fresh-intake verdict；唯一会改变系统认知的新结论是：`Rank 295` 仍占用唯一合法 survivor follow-up 前排，`cycle_plan` 第 2 条 fresh intake 由于前置条件不成立，必须写成 `blocked`，不能绕过 survivor lock 继续执行。

## State writeback scope
- 将 `cycle_plan` 第 2 条从 `pending` 改写为 `blocked`
- 将 `Surviving candidate slot.latest_blocked_record` 指向本日志
- 不改写 policy / brief / operating card / auto loop / cron prompt
- 不重排 `cycle_plan`
- 不伪造新的 fresh-intake rank / verdict
