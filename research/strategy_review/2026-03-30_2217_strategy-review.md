# 2026-03-30 22:17 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已 live 的仍是 `connected_runner_live`（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮 fresh intake 是 **`Rank 262 / percentile-entry cointegration spread mean reversion`**。
   - 证据：最新 optimization 结果是 `research/optimization_loop/2026-03-30_2211_rank262_percentile_cointegration_intake_keep_p1.md`；对象主语已经锁定为 `cointegration pair selection + percentile-entry + mean-cross exit` 的 crypto pairs spread MR，fresh intake 首判已完成并给出 `keep_P1`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且当前就该占据 survivor 锁。**
   - 证据：上一条 fresh intake 是 **`Rank 262 / percentile-entry cointegration spread mean reversion`** 本身；其首判刚完成，blocker 也足够集中——现在唯一需要诚实回答的是：当 universe 从论文式广泛小币样本收缩到 `Binance / OKX / Bybit` 可承载的 liquid-major / desk-feasible pair，并补上 friction / max-hold / next-bar 执行后，这条 alpha 是否仍保留足够的成本后 MR 边际。这正符合 policy 所说“上一条 fresh intake 的唯一一次诚实 follow-up”。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。最近没有新的 active P2 入场；因此也不存在本轮需要 bot2 兜底直推 `P3` 的对象。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头
- `Fresh intake`: `Rank 262`，已有正式 rank
- `Surviving candidate`: `Rank 262`，已有正式 rank
- `Active P2`: `none`
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short --branch` 显示 repo 有大量未跟踪产物；本轮只把它当环境噪音，不据此反推 policy 或改排班。
- 最近真正改变前排链条的 optimization 结果是：
  - `2026-03-30_2135_rank260_survivor_followup_background_p0.md`：`Rank 260` 的唯一 survivor follow-up 已诚实收口回 `background/P0`
  - `2026-03-30_2211_rank262_percentile_cointegration_intake_keep_p1.md`：`Rank 262` 完成 fresh intake 首判，成为当前最新 fresh intake 与 survivor
- `2026-03-30_2058_percentile_cointegration_intake_blocked_survivor_lock.md` 说明该对象之前不是被否，而只是被 `Rank 260` 的 survivor lock 挡住；现在 `Rank 260` 已收口，它自然成为当前最合法的前排对象。
- 最近 strategy review 到 `2026-03-30_2100_strategy-review.md` 仍停留在“先收口 Rank 260，再把 percentile-entry cointegration 作为下一条 fresh intake”的状态；本轮需要把 state 正式同步到 **`Rank 262` 已经成为当前 survivor** 这一 runtime truth。
- 当前 survivor 收口之后，最适合作为后续具体 intake 的最近对象是：
  1. `research/quant_digests/2026-03-30_2055_skip-lastbar-xs-momentum-alpha.md`
  2. `research/quant_digests/2026-03-30_2204_qqq-nvda-crypto-15m-leadlag-alpha.md`
  3. `research/quant_digests/2026-03-30_1827_tau-reset-band-liquidity-harvest-alpha.md`
- 之所以不再把 `percentile-entry cointegration` 留在 fresh intake 槽里，是因为它已经完成首判并取得 survivor 锁；当前更诚实的动作是先执行它唯一一次 follow-up，再把预算让给新的具体 intake。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：有，而且当前唯一 survivor 是 `Rank 262`
4. 因此前排链条未完全收口前，第 1 优先级必须先排 `Rank 262` 的唯一 follow-up；其后才能用剩余预算补新的具体 intake

因此本轮把 `cycle_plan` 重写为：
1. `Rank 262 / percentile-entry cointegration spread mean reversion` survivor follow-up
2. `skip-last-bar 的 8h~16h XS momentum` fresh intake
3. `QQQ / NVDA lead-lag × crypto 15m spillover` fresh intake
4. `symmetric τ-band liquidity harvest × band-exit reset` fresh intake

## 为什么这样改 state

- `Rank 260` 已经完成唯一 follow-up 并回 `background/P0`，不能继续占前排。
- `Rank 262` 是当前最新 fresh intake，且其唯一值得继续的一刀非常明确——直接回答 liquid-major / desk-feasible pair 下的可承载性，所以必须占据 survivor 槽位与 `cycle_plan` 第 1 项。
- 当前没有 `P3` 待接线对象，也没有 `Active P2`，所以后 3 个预算位可以诚实回到新的具体 intake。
- 新 intake 只从最近 digest 中挑选具体对象，没有把 background pool 旧候选自动拉回前排。
- `skip-last-bar 的 8h~16h XS momentum` 与 `QQQ / NVDA -> crypto 15m spillover` 都是最近新增且边界清楚的对象；把它们排在 survivor 收口之后，符合“已有前排对象的收口优先级永远高于新的发现”。
- `τ-band liquidity harvest × reset` 保留在第 4 位，作为预算仍有余时的具体补位 intake，而不是抽象占位符。

## P2 -> P3 兜底裁判是否触发

**不触发。**

因为：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 最近 desk review 没有出现“对象已明显足够进入 paper trade / paper launch，但 bot3 尚未升级”的 active P2

因此本轮不新增 `P3 / Paper launch queue` 写回，也不伪造 handoff 路径。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：只重写 `cycle_plan`，使其与最新前排链条同步（`Rank 262` survivor 优先，后续补 3 条新的具体 intake）
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3` 的门槛，因此无新增 P3 handoff 写回
