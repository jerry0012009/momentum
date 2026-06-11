# 2026-04-07 06:24 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只允许更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已写入 `connected_runner_live`，表示它们已完成最小 `P3 launch wiring`，不是当前待接线队列成员；因此当前没有需要继续排在 `P3 handoff` 前排的对象。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-07_0551_basis-funding-gap-convergence-alpha.md`。**

原因：当前 `P3 / Active P2 / Surviving candidate` 都为空，前排链条已经诚实收口；按 policy，新的 `fresh intake` 应优先从最近新 repo / paper / alpha 报告里挑。最新一条具体且未处理的对象就是 `basis-funding gap convergence`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`。它已在 `research/optimization_loop/2026-04-07_0621_volume_anomaly_bandfade_hmm_veto_intake_background_p0.md` 收口为 `background / P0`：对象本质上仍是旧 `Bollinger / oversold mean-reversion` 家族叠加 `volume confirmation + HMM crash veto` 的实现壳，没有压出足以独立保留前排的新 alpha 主语，因此不应占用 survivor 唯一 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近一条 `Active P2` 是 `Rank 342`，已在 `2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小 wiring；当前没有任何需要 bot2 兜底裁决的漏升 `P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 但无正式 rank”的情况，因此本轮无需补 rank。

## 最近证据与排班结论
最近有效新增证据只有两条：
1. `Rank 354` 的 survivor 唯一 follow-up 已在 `2026-04-07_0510_rank354_survivor_followup_background_p0_readme_only_no_auditable_edge.md` 收口为 `background / P0`；
2. `volume anomaly band-fade × HMM veto` 已在 `2026-04-07_0621_volume_anomaly_bandfade_hmm_veto_intake_background_p0.md` 收口为 `background / P0`。

因此当前前排链条已经清空，不存在 `P3 handoff`、`P2 admission`、`P1 follow-up` 的真实可执行动作。本轮必须切回 `fresh intake`，且应直接指定最新、最具体的对象，而不是继续沿用已经相对陈旧的 pending intake。

## 本轮 runtime 调整
仅重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，新的当前轮顺序为：
1. `2026-04-07_0551_basis-funding-gap-convergence-alpha.md`
2. `2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md`
3. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`
4. `2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`

这样排的原因：
- 没有任何 `P3 / P2 / P1` 前排动作需要优先于新 intake；
- `0551` 与 `0530` 是最新两条、且都属于明确可落地的 relative-value / carry / calendar-spread 家族新对象；
- `0333` 与 `0241` 保留在后两位，作为当前轮预算内的继续 intake；
- 不需要显式写 `Background pool guard` 或空槽确认小点，因为当前没有 reopen / 槽位污染迹象。

## 为什么这轮不需要 bot2 兜底升 P3
没有任何 `Active P2` 留在前排，更不存在“desk review 已清楚表明足够 paper trade、但 bot3 尚未升级”的对象。`Rank 342` 的升级与 wiring 已完成，其余对象最近都在 `P0` 收口，没有漏判成 `P3` 的情况。

## 一句话总结
当前运行态已从 `Rank 354 survivor + volume-anomaly intake` 全部收口回到空前排；因此 bot3 下一轮应直接从最新两条 fresh intake（`basis-funding gap convergence`、`bestBid-bestAsk calendar netting`）开始，而不是回头重复已结束的前排对象。
