# 2026-04-07 09:32 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经写入 `connected_runner_live`；其中最近一条是 `Rank 342`，已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成 dedicated runner、scheduler 与首跑验证，因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-07_0852_ofi-ewma-reservation-maker-alpha.md`。**

原因：当前 `P3 / Active P2 / Surviving candidate` 三个前排槽位都为空，而 `2026-04-07 08:52` 这条 `OFI × EWMA reservation-price maker skew` 是目前最新、且尚未进入 `optimization_loop` 形成 first verdict 的具体 alpha 报告，按 policy 应成为本轮首条 fresh intake。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md`，并已在 `research/optimization_loop/2026-04-07_0924_bestbid_bestask_calendar_intake_background_p0_tooling_not_auditable_edge.md` 直接收口为 `background / P0`：
- 主语更像 options RV 工具链里的 calendar-spread 可成交扫描，不是新的独立 raw alpha；
- 公开材料停留在 README/source-asserted 层；
- 逐腿执行、盘口 stale、fee tier、保证金切换等 honesty 问题没有被压成可审计证据。

既然首判已经是 `background / P0`，它就不进入 survivor，也不值得那唯一一次 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近一条明确 `Active P2` 仍然是 `Rank 342`，它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮不存在 bot2 需要兜底裁判、强制推进到 `P3 / P1 / P0` 某一出口的悬而未决 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与排班判断
本轮真正影响排班的近端证据：
1. `research/optimization_loop/2026-04-07_0859_ctrend_multihorizon_intake_background_p0_duplicate_xs_momentum_family.md`
   - 证明 `2026-04-07_0720_ctrend-multihorizon-xs-alpha.md` 已直接收口为 `background / P0`。
2. `research/optimization_loop/2026-04-07_0919_persistent_imbalance_signedflow_intake_background_p0_duplicate_microstructure_family.md`
   - 证明 `2026-04-07_0640_persistent-imbalance-signedflow-continuation-alpha.md` 已直接收口为 `background / P0`。
3. `research/optimization_loop/2026-04-07_0924_bestbid_bestask_calendar_intake_background_p0_tooling_not_auditable_edge.md`
   - 证明 `2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md` 也已直接收口为 `background / P0`。
4. 当前 `P3 / P2 / P1` 全空，因此本轮必须诚实切回新的 `fresh intake`，且按时间顺序应优先排 `08:52 / 08:28 / 07:40` 三条最近新增对象，再用 `03:33` 的旧 pending 填满预算。

## 本轮 runtime 调整
本轮只重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，新的当前轮顺序为：
1. `research/quant_digests/2026-04-07_0852_ofi-ewma-reservation-maker-alpha.md`
2. `research/quant_digests/2026-04-07_0828_avax-icp-rollslippage-pairs-alpha.md`
3. `research/quant_digests/2026-04-07_0740_polymarket-term-structure-kalman-ou-alpha.md`
4. `research/quant_digests/2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`

这样排的原因：
- 当前没有任何 `P3 handoff / Active P2 / Surviving candidate` 需要抢占前排；
- `08:52 / 08:28 / 07:40` 是最近且尚未形成 first verdict 的具体对象；
- `03:33` 仍保留在本轮第四格，作为已排未执行的具体 intake；
- 没有把 background pool 的旧候选自动拉回前排，也没有把空槽确认单独写成 cycle item。

## 为什么这轮不需要 bot2 兜底升 P3
这轮没有任何 `Active P2` 在前排，自然也不存在“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的漏升对象：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 354` 已在唯一 survivor follow-up 后退出前排；
- `CTREND / persistent imbalance / bestBid>-bestAsk calendar` 三条最近 intake 都已经直接收口到 `P0`。

所以本轮 bot2 的诚实职责不是硬推 `P3`，而是把 fresh intake 队首切换到最新、最具体、仍未首判的对象。

## 一句话总结
当前前排完全清空，最近三条 fresh intake 已连续收口为 `background / P0`；因此 bot3 下一轮应直接从 `OFI × EWMA maker skew` 开始，再顺序看 `AVAX/ICP roll-slippage pairs`、`Polymarket term-structure Kalman-OU`，最后才轮到 `crash-trim vol-managed XS momentum`。
