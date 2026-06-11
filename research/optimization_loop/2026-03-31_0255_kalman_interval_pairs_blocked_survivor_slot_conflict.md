# Rank 266 候选未执行 intake：survivor 槽位冲突 guard 拦截
- 时间：2026-03-31 02:55 UTC
- 类型：bot3 optimization loop guard / blocked step
- 对应 cycle_plan 小点：`kalman innovation interval pairs`

## 本轮结论
当前最前 pending 小点本来要求把 `research/quant_digests/2026-03-30_2328_kalman-innovation-interval-pairs-alpha.md` 作为新的 fresh intake 执行 first verdict。

但按 `docs/BOT2_BOT3_POLICY.md`：
1. `Surviving candidate` **只能是上一条 fresh intake**；
2. 任何 `keep_P1` fresh intake 的那 **唯一一次 survivor follow-up** 在诚实收口前默认享有前排锁定权；
3. 只要当前存在合法 `P1 / Surviving candidate` 动作，bot2 就不得把新的 `fresh intake` 排到它前面。

当前 runtime truth 仍是：
- `Fresh intake slot = Rank 265 / same-venue delta-neutral carry × premium-z admission × current+next funding > close-cost`
- `Surviving candidate slot = Rank 265`
- `followup_budget_remaining = 1`

因此，`kalman innovation interval pairs` 虽然 digest 本身写得足够清楚、也具备独立 raw alpha skeleton，但**现在不是合法前排动作**。若在 `Rank 265` 的 survivor follow-up 尚未收口前继续给新对象分配正式 Rank 并写入 fresh slot，会直接违反 fixed policy 的前排锁定规则。

## 对 digest 的快速 desk 判断（仅供后续 bot2 重排时参考，不构成正式 intake）
`kalman innovation interval pairs` 的主题主语是明确的：`dynamic beta fair spread × innovation-vol interval breach` 的 pair mean-reversion raw alpha；不是泛 Kalman smoother，也不是普通 rolling z-score pairs 壳。digest 还给出了本地 `15m` transfer proxy：innovation interval 在 gross 上优于 point / rolling band，但当前 taker 成本后仍不过生存线。

这说明它**值得在 survivor/P2 链条收口后，再作为候选 fresh intake**；但本轮不能跳过 `Rank 265` 的 survivor 锁定权直接推进。

## 本轮写回
- 当前小点状态：`blocked`
- blocked 原因：`Rank 265` 仍是唯一合法前排 survivor，`kalman innovation interval pairs` 现在不具备合法执行前置条件。
- 未分配新 Rank；未改写 fresh/survivor/P2 槽位。
