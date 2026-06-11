# 2026-04-07 11:41 UTC — `half-life Kelly coint pairs` 小点被 `Rank 355` survivor lock 拦截

## 本轮执行对象
- cycle_plan item 3
- target: `research/quant_digests/2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`
- planned action: 作为第三条具体 `fresh intake`，判断 `4-test pair admission × half-life-bounded spread MR × fractional-Kelly shell` 是否足够独立，还是只是旧 `pairs / stat-arb` 家族再包装

## 先做合法性检查
根据 `docs/BOT2_BOT3_POLICY.md`：
- `Surviving candidate` **只能是上一条 fresh intake**；
- 该 survivor 默认享有前排锁定权，直到那唯一一次 follow-up 被诚实收口；
- 在存在合法 `P1 / Surviving candidate` 动作时，bot2/bot3 不应继续让新的 `fresh intake` 抢占前排资源。

当前 runtime truth：
- `Surviving candidate slot` = `Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion`
- `followup_budget_remaining: 1`
- 因而 survivor 链条尚未收口。

## 本轮结论
`research/quant_digests/2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md` 这条小点的前置条件当前不成立：`Rank 355` 仍合法占用 survivor 槽位且 follow-up 预算未用完，因此新的 `fresh intake` 不得继续前排执行；本轮应记为 `blocked`，等待 bot2 先把 `Rank 355` 的 survivor follow-up 排到前面并收口。

## 对 runtime 的影响
- 不分配新 Rank
- 不改层级槽位
- 只把当前 cycle_plan 小点记为 `blocked`
- 同步更新 `Fresh intake slot.latest_blocked_record`
