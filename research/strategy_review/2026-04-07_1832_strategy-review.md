# 2026-04-07 18:32 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只重写 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`。**

原因：
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 旧 `cycle_plan` 里前两条 `1711` 与 `1640` 已分别在 `research/optimization_loop/2026-04-07_1756_xgboost_spread_inventory_ladder_first_verdict_background.md` 与 `research/optimization_loop/2026-04-07_1809_btc_tick_impulse_ada_catchup_first_verdict_background.md` 完成 first verdict 并收口为 `background / P0`

前排已经诚实清空，因此当前 fresh 队头顺延到仍未判决、且已在上一轮 pending 的 `14:36 UTC` 这条 `major-lead first-slot return × follower close-slot continuation`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_1640_btc-ticklead-ada-catchup-alpha.md`。它已在 `research/optimization_loop/2026-04-07_1809_btc_tick_impulse_ada_catchup_first_verdict_background.md` 明确写成：
- 只是把既有 `BTC-first alt-lag / leader-follower / cross-market ITSM` 家族压到更短秒级窗口与更窄单币对；
- 主语仍是 `BTC 先动、follower 后补`；
- 没有形成独立新 raw alpha pocket。

因此它首判即 `background / P0`，不进 `keep_P1`，自然不配 survivor 那唯一一次 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的 `Active P2` 仍是 `Rank 342`，但它已在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后又在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮没有 bot2 需要兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与判断
本轮先读 fixed policy / runtime state，再看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-07_1756_xgboost_spread_inventory_ladder_first_verdict_background.md`
   - `1711 xgboost-spread-adaptive-maker` 已完成 first verdict，并被诚实记为 `background / P0`；说明它不再占 fresh queue 的第一位。
2. `research/optimization_loop/2026-04-07_1809_btc_tick_impulse_ada_catchup_first_verdict_background.md`
   - `1640 btc-ticklead-ada-catchup` 也已完成 first verdict，并收口为 `background / P0`；说明旧 `cycle_plan` 的前两条 pending 已经都结束。
3. `research/optimization_loop/2026-04-07_1612_rank356_survivor_followup_background_router_loses_to_plain_xs.md`
   - `Rank 356` 的 survivor follow-up 已经用完并收口为 `background / P0`；当前没有 survivor 锁位。
4. `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` + `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
   - 最近的 `P2/P3` 主线已经完成升级与最小接线，不再占用 `Paper launch queue` 或 `Active P2`。
5. 最新 digest 顺序显示当前尚未判决、且值得排入预算的 fresh 对象包括：
   - `2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
   - `2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
   - `2026-04-07_1830_volume-routed-xs-reversal-tsmom-dualbook-alpha.md`
   - `2026-04-07_1748_binance-okx-spot-leadlag-catchup-alpha.md`

因此，按 policy 的默认排班顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

本轮实际扫描结果是：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：无 survivor 锁位；
- 所以只能也应该切回具体 fresh intake。

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看见某个**在场 `Active P2`** 已经足够值得进入 paper trade，而 bot3 尚未升级时，直接把它写入 `P3 / Paper launch queue` 或 handoff 路径。

本轮不满足这个前提：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 356` 已在 survivor follow-up 中诚实收口回 `background/P0`；
- 当前待做对象都只是 fresh intake。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的漏升对象。

## Runtime writeback
本轮已按 policy 只改 `docs/BOT2_BOT3_STATE.md` 的 runtime 部分：

### 1) Fresh intake slot
- `status` 切回 `pending`
- `current_target` 从已完成 first verdict 的 `2026-04-07_1640_btc-ticklead-ada-catchup-alpha.md` 顺延到 `2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
- `source_record` 同步切到 `1436` digest
- `latest_result` / `latest_result_record` 保留最近刚落地的 `1640 -> background / P0`

### 2) cycle_plan
按当前合法动作重写为 4 条具体 fresh intake：
1. `1436 majorlead-closeslot-crossmarket-itsm`
2. `1129 polymarket-pairsum-shield-maker`
3. `1830 volume-routed-xs-reversal-tsmom-dualbook`
4. `1748 binance-okx-spot-leadlag-catchup`

重排原则：
- 先保留并收口上一轮已在前排等待的 `1436` 与 `1129`；
- 前排 `P3/P2/P1` 已清空后，再用剩余预算补更近的新 intake `1830` 与 `1748`；
- 新生成项统一保持 `result: none`、`status: pending`。

## 一句话总结
这轮没有漏升的 `P2`、没有遗留的 `P1`、也没有待接线的 `P3`；旧 fresh 队头 `1711` 和 `1640` 都已完成 first verdict 并收口，因此 runtime 现在应切到 `1436 -> 1129 -> 1830 -> 1748` 这四条具体 intake。