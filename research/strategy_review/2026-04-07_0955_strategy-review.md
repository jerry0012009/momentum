# 2026-04-07 09:55 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成，因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-07_0740_polymarket-term-structure-kalman-ou-alpha.md`。**

原因不是它最新，而是当前更近的两条 `fresh intake` 已经完成 first verdict：
- `research/quant_digests/2026-04-07_0852_ofi-ewma-reservation-maker-alpha.md` 已在 `research/optimization_loop/2026-04-07_0938_ofi_ewma_reservation_fresh_intake_background_p0_old_microstructure_family.md` 收口为 `background / P0`；
- `research/quant_digests/2026-04-07_0828_avax-icp-rollslippage-pairs-alpha.md` 已在 `research/optimization_loop/2026-04-07_0944_avax_icp_fresh_intake_background_p0_old_pairs_family.md` 收口为 `background / P0`。

在 `P3 / P2 / P1` 都为空的前提下，按默认排班顺序，当前轮新的队首 fresh intake 就顺延到 `07:40` 这条 `Polymarket term-structure × Kalman-OU spread`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_0828_avax-icp-rollslippage-pairs-alpha.md`，并且已经直接首判为 `background / P0`，不进入 survivor：
- 它本质上仍是已知 `pairs / stat-arb / spread mean reversion + cost governance` 家族的窄化实现；
- 新增证据主要只是把对象压缩到单一 `AVAX/ICP` alt pair，并补了 `roll slippage` 表；
- 公开材料没有压出跨 pair / 跨资产 / 跨时期的独立 after-cost pocket。

既然首判就是 `P0`，就不占那唯一一次 follow-up 预算。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。本轮没有任何需要 bot2 兜底裁判并强行推向 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
本轮最关键的新证据，不是出现了需要 bot2 兜底直升 `P3` 的对象，而是前排继续清空：
1. `research/optimization_loop/2026-04-07_0938_ofi_ewma_reservation_fresh_intake_background_p0_old_microstructure_family.md`
   - 证明 `OFI × EWMA reservation-price maker skew` 只是旧 microstructure / maker inventory skew 家族的工程化重述，直接 `background / P0`。
2. `research/optimization_loop/2026-04-07_0944_avax_icp_fresh_intake_background_p0_old_pairs_family.md`
   - 证明 `AVAX/ICP roll-slippage pairs` 只是旧 pairs / stat-arb 家族的窄化单 pair 实现，直接 `background / P0`。
3. 当前 `P3 / Surviving candidate / Active P2` 继续全空。

这意味着：
- 本轮没有任何合法的 `P3 handoff` 动作；
- 没有任何合法的 `P2 admission / promote / park` 动作；
- 也没有 survivor follow-up 锁住前排；
- 所以必须诚实切回 fresh intake，并从仍未首判的具体对象里继续向前推进。

## 本轮 runtime 调整
本轮只重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`。新的当前轮顺序为：
1. `research/quant_digests/2026-04-07_0740_polymarket-term-structure-kalman-ou-alpha.md`
2. `research/quant_digests/2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`
3. `research/quant_digests/2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`

这样排的原因：
- 当前没有任何 `P3 / P2 / P1` 前排对象需要抢占预算；
- `07:40` 的 Polymarket、`03:33` 的 crash-trim、`02:41` 的 multi-test coint pairs 都是仍未形成 first verdict 的具体 intake；
- `07:20 / 06:40 / 05:51 / 05:30 / 08:52 / 08:28` 等更近对象要么已收口为 `P0`，要么已经在 optimization loop 里被明确处理，不能重复排；
- 没有把 background pool 旧候选自动拉回前排，也没有把 guard / 空槽确认单独塞成 cycle item。

## 为什么这轮不需要 bot2 兜底升 P3
这轮没有任何 `Active P2` 在前排，更没有“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的漏升对象：
- `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 354` 的 survivor follow-up 已耗尽并回到 background；
- 近两条 fresh intake（OFI / AVAX-ICP）都直接收口为 `P0`。

所以本轮 bot2 的正确动作不是硬造一个 `P3`，而是诚实地把 bot3 的前排重新切回仍未首判的 fresh intake 队列。

## 一句话总结
当前前排仍是全空；最新两条 fresh intake（OFI、AVAX/ICP）都已直接收口为 `background / P0`。因此 bot3 下一轮应从 `Polymarket term-structure × Kalman-OU spread` 开始，再看 `crash-trim + vol-managed XS momentum`，最后看 `4-test pair admission × half-life-bounded spread MR`。