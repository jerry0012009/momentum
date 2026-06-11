# Strategy Review — 2026-04-04 18:03 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1758_rank332_pancakeswap_latelock_ev_prediction_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1714_rank331_canonical_sign_audit_promote_p2.md`
  - `research/optimization_loop/2026-04-04_1534_rank330_p2_admission_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1646_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **当前 runtime 中已完成的 fresh intake 是**：`research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`。
- 它已经在运行态中写成 `Rank 332`，first verdict 为 `keep_P1`，并进入 `Surviving candidate slot`；因此本轮真正尚待执行的新 fresh intake 已顺延为后面的 `2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md` 与 `2026-04-04_1335_deribit-iv-calendar-spread-alpha.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- `Rank 332` 不是粗糙的跟 crowd / 反 crowd 脚本，而是完整的 `late-lock pool imbalance × payout-aware EV switch` raw alpha 壳：公开赔率、最小 `p_hat`、fee/gas/tie risk、固定到期结算都已成形。
- 当前唯一 decisive blocker 也很清楚：`lock 前 60s/30s/20s/15s/10s` 的 visible pool state 相对最终 locked pool 是否足够稳定、足够可下注。
- 这正符合 survivor 的“唯一一次便宜但决定性的诚实检查”，因此它应继续占据 survivor 前排锁定位，直到这次 follow-up 诚实收口。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。** 当前明确 `Active P2 = Rank 331 / spot-perp basis state × funding-pressure × delta-neutral flip`。
- 结合 `2026-04-04_1714` 的 sign audit，`Rank 331` 已经跨过“是不是伪 edge / 方向写反”的 survivor blocker，保留了独立的 basis drift raw-alpha 主语和清楚的 `15m discovery + 5m execution` 壳。
- 因此在三种出口里，它现在**离 `P3` 最近**：剩下要补的是 admission 轴上的 effectiveness / cross-asset / honesty 收口，而不是回退到 `P1` 的 re-scope，也不是已有 fatal flaw 直落 `P0`。
- 但当前证据还**没有**到达 bot2 必须直接兜底升 `P3` 的程度；因为含成本后 effectiveness、跨资产迁移性、funding cashflow 记账 realism 仍未被写实地回答。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`
- `Surviving candidate slot.current_target = Rank 332 / late-lock pool imbalance × payout-aware EV switch`
- `Active P2 slot.current_target = Rank 331 / spot-perp basis state × funding-pressure × delta-neutral flip`
- 当前所有前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮明确 `Active P2 = Rank 331`，但 desk review 尚未清楚表明它已经“足够值得进入 paper trade / paper launch”。
- 目前最强的新证据只是 canonical sign audit 通过；这说明它值得进入正式 admission，不说明它已经跨过 `P3` 门槛。
- 因此本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级；但已在新的 `cycle_plan` 第 1 项里明确写死：若本轮 admission 结果已经足够支持 paper trade，bot3 必须直接写成 `promote_P3`，不得继续开放式研究。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一 follow-up > fresh intake > P0`，本轮合法前排动作应为：

1. `Rank 331`：`Active P2` admission 第 1 轮，先答 `effectiveness / cross-asset`，必要时直接 `promote_P3` 或 `drop_to_background`
2. `Rank 332`：survivor 唯一一次 snapshot 稳定性审计，并直接 `promote_P2` 或 `background/P0`
3. `research/quant_digests/2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md`
4. `research/quant_digests/2026-04-04_1335_deribit-iv-calendar-spread-alpha.md`

这样排的理由：
- `P3` 为空，当前没有待接线对象；
- `P2` 不为空，且 `Rank 331` 是当前最接近出口决策的对象，因此必须排在最前；
- `P1` 也不为空，`Rank 332` 的唯一一次 follow-up 享有 survivor 锁定权，必须排在所有新 fresh intake 之前；
- 只有在 `P2/P1` 都已被诚实排入前部后，剩余预算才给新的具体 intake。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 项：
- 第 1 项改为 `Rank 331` 的 `Active P2` admission 第 1 轮
- 第 2 项改为 `Rank 332` 的 survivor 唯一 follow-up
- 第 3/4 项保留为两条具体 fresh intake
- 新生成项均满足 `result = none`、`status = pending`

## 本轮结论一句话
当前前排主线已经从“survivor sign audit”切到“`Rank 331` 的 P2 admission + `Rank 332` 的 survivor 收口”；bot2 已按 policy 把运行态重排为先收口已有前排对象，再吃新的 intake。