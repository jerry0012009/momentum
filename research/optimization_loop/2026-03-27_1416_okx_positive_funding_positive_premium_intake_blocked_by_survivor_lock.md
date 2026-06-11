# 2026-03-27 14:16 UTC — OKX 正 funding × 正 premium carry intake blocked by survivor lock

## 本轮执行小点
- target: `research/quant_digests/2026-03-27_1050_okx-positive-funding-positive-premium-carry.md`
- action: 在前两项未留下更高优先级前排对象时，对 `正 funding × 正 premium` spot-perp carry pocket 做 fresh intake

## policy / state 约束核对
- 当前 `Surviving candidate slot` 已被 `Rank 198 / dynamic cointegration pair-basket spread convergence` 占用，且 `followup_budget_remaining: 1`
- 按 policy 的 authoritative priority，`P1 / Surviving candidate` 的唯一一次便宜诚实检查优先于新的 `fresh intake`
- 本轮 state 第 1 项已经把 `Rank 198` 留在 survivor 槽，因此第 3 项 action 里“若前两项没有留下更高优先级前排对象”的前置条件不成立

## 结论
本轮不允许对 `okx-positive-funding-positive-premium-carry` 执行 fresh intake；当前前排仍由 `Rank 198` 的 survivor follow-up 锁定，因此该小点按 policy 收口为 `blocked`，避免在 survivor 未收口时继续插入新的 intake。

## runtime writeback
- cycle_plan item 3 -> `status: blocked`
- cycle_plan item 3 -> `result: 正 funding × 正 premium carry` 本轮未被合法执行：`Rank 198` 仍占用 survivor 槽，导致“前两项没有留下更高优先级前排对象”的前置条件不成立，因此该小点按 policy 收口为 blocked。

## reader-facing impact
- 无新 intake
- 无新 rank
- 无层级变化
- 无 homepage 刷新必要
