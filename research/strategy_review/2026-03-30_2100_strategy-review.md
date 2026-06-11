# 2026-03-30 21:00 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已 live 的只有 `connected_runner_live`（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮 fresh intake 是 **`Rank 260 / perp-perp funding diff × net-EV hurdle`**。
   - 证据：最新已完成 fresh intake 结果为 `research/optimization_loop/2026-03-30_2028_rank260_perp_perp_funding_diff_netev_intake_keep_p1.md`；对象主语已锁定为 `same-underlier cross-venue 双 perp` 只在 `funding spread` 同时过 `z-score / net-EV / quote-depth` 门后才开仓的事件型 relative-value carry，首判为 `keep_P1`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且已经被诚实用完。**
   - 证据：上一条 fresh intake 是 **`Rank 259 / bear-shock short-alt lag pocket`**。其唯一 survivor follow-up 已在 `research/optimization_loop/2026-03-30_2015_rank259_survivor_followup_background_p0.md` 完成；把 `Spot proxy` 切到冻结 top5 的 Binance USDⓈ-M perp + `next-bar open` 后，满足条件的事件只剩 7 个，且在 `6/10/14/18 bps` 成本下 event mean / median 均为负、收益主要由单一 crash window 支撑，因此这次 follow-up 的诚实结论不是升 `P2`，而是**用尽预算后回 `background/P0`**。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。最近的 `Rank 235` 已在 `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`，不再属于当前 active P2。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头
- `Fresh intake`: `Rank 260`，已有正式 rank
- `Surviving candidate`: `Rank 260`，已有正式 rank
- `Active P2`: `none`
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short --branch` 显示 repo 有大量未跟踪产物；本轮只把它当环境噪音，不据此反推 policy 或改排班。
- 最近 optimization 里真正改变前排链条的新增结果是：
  - `2026-03-30_2015_rank259_survivor_followup_background_p0.md`：`Rank 259` 的唯一 survivor follow-up 已完成并回 `background/P0`
  - `2026-03-30_2028_rank260_perp_perp_funding_diff_netev_intake_keep_p1.md`：`Rank 260` fresh intake 首判完成，直接成为当前 latest fresh 与 survivor
  - `2026-03-30_2058_percentile_cointegration_intake_blocked_survivor_lock.md`：`percentile-entry cointegration spread mean reversion` 并非证据否决，而是因为 `Rank 260` survivor lock 仍未收口，本轮不具备合法执行前置条件
- 最近 strategy review 到 `2026-03-30_1947_strategy-review.md` 为止，前排仍停在“`Rank 260` 刚成为 survivor，后续新 intake 被锁”的状态；本轮要做的是把这个顺序写得更诚实：先收口 `Rank 260`，再继续新的具体 intake。
- 最近值得排进 fresh intake 队列的具体新对象，按“最近新 repo/paper/alpha 报告”优先级看，当前最合适的是：
  1. `research/quant_digests/2026-03-30_1858_percentile-entry-cointegration-pairs-alpha.md`
  2. `research/quant_digests/2026-03-30_2055_skip-lastbar-xs-momentum-alpha.md`
  3. `research/quant_digests/2026-03-30_1827_tau-reset-band-liquidity-harvest-alpha.md`
- `research/quant_digests/2026-03-30_2005_btceth-spread-mr-momentum-veto.md` 当前快检结论是 gross 微正、轻微成本即转负，更像 control-card / reject-for-now，不如上面三条适合作为 survivor 收口之后的新一轮 fresh intake。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：有，而且当前唯一 survivor 是 `Rank 260`
4. 因此前排链条未完全收口前，第 1 优先级必须先排 `Rank 260` 的唯一 follow-up；其后才能用剩余预算补新的具体 intake

因此本轮把 `cycle_plan` 重写为：
1. `Rank 260 / perp-perp funding diff × net-EV hurdle` survivor follow-up
2. `percentile-entry cointegration spread mean reversion` fresh intake
3. `skip-last-bar 的 8h~16h XS momentum` fresh intake
4. `symmetric τ-band liquidity harvest × band-exit reset` fresh intake

## 为什么这样改 state

- `Rank 259` 已经完成唯一 follow-up 并回 `background/P0`，不能继续占前排。
- `Rank 260` 是当前最新 fresh intake，且它的唯一值得继续的一刀非常明确——直接统计 `BTC / ETH / SOL × Binance / Bybit / OKX` 在统一 `z-score + net_ev > 0 + quote/depth veto` 下的历史过线率，判断它到底是 admission 候选还是极低频事件 pocket——所以必须占据 survivor 槽位与 `cycle_plan` 第 1 项。
- 当前没有 `P3` 待接线对象，也没有 `Active P2`，所以后 3 个预算位可以诚实回到新的具体 intake。
- 新 intake 只从最近 digest 中挑选具体对象，没有把 background pool 旧候选自动拉回前排。
- `percentile-entry cointegration spread mean reversion` 先前被 bot3 以 survivor lock 拦下，并不是对象本身被否；因此它理应保留在 survivor 收口之后的 fresh intake 第一顺位。
- `skip-last-bar 的 8h~16h XS momentum` 比 `BTC/ETH spread MR × momentum veto` 更适合作为下一个新 intake：前者是结构清楚、可 desk 化迁移的完整 XS raw alpha；后者当前仍停留在 gross 微正、轻微成本即翻负的 control-card 状态。

## P2 -> P3 兜底裁判是否触发

**不触发。**

因为：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 最近 desk review 没有出现“对象已明显足够进入 paper trade / paper launch，但 bot3 尚未升级”的 active P2

因此本轮不新增 `P3 / Paper launch queue` 写回，也不伪造 handoff 路径。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：只重写 `cycle_plan`，使其与最新前排链条同步（`Rank 260` survivor 优先，后续补 3 条新的具体 intake）
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3` 的门槛，因此无新增 P3 handoff 写回
