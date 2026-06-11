# 2026-03-16 17:57 UTC · Desk Board Review

## 本轮一句话判断

**这轮仍是无换席巡检：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 维持四档阶段表，且最新证据继续把 `Rank 2 combo_all` 锁在 `paper_candidate_only / blocked`（不是升格），`Rank 1 / Rank 3 / Rank 4` 继续 `park`。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - 最新几轮 runbook（含 `17:39`、`17:47`）都复核了 `EMA require-due`，结论仍是没有 `due-now / overdue` lane。
   - 因此当前 `EMA` 应维持 `running paper` 的 waiting 状态管理，不应伪造 refresh，也不应占用默认 bot3 主资源。

2. **Live Seat 继续保持暂空**
   - 没有任何候选在本轮被推进到可争夺 `Live Seat` 的级别；
   - `breakout` 仍是历史 bench 证据池，且无新的 blocker reduction；
   - 因此当前最诚实结论不变：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 继续是唯一仍保留前推价值的候选，但被进一步锁成 blocked closeout**
   - `17:28`：新增 `small_live_rank2_closeout_snapshot_v1.csv`，并同步到 `alpha_closure_board`；
   - `17:39`：首页 `Deployment Watch` 也直接读取该快照，明确 `dry_run_only / paper_candidate_only / blocked`；
   - `17:47`：新增 `small_live_rank2_receipt_chain_audit_v1.csv`，审计三条 whitelist leg（BTC/ETH/SOL）均为 `real_refs_landed = 0/3`；
   - 当前唯一允许动作依旧是：**在 whitelist 上补一条真实 `test/no-fill` receipt chain（intent_ref + ack_ref + cancel_or_close_ref 同链）**。

4. **Rank 1 / Rank 3 / Rank 4 继续维持 park**
   - `Rank 1 τ-band`：历史 verdict 仍弱，继续 `park`；
   - `Rank 3 third-touch+EMA/MACD`：trade-count / time / parameter 稳定性已有 fail 证据，继续 `park`；
   - `Rank 4 pairs stat-arb`：clean replication first pass 整体偏负，继续 `park`。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 把 Rank 2 的 closeout artifact 误读成 tiny-live 放行：必须禁止。
- 继续把 Rank 3/4 作为默认主资源位：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续暂空。**
- **Scout Seat（paper/repo 候选 + 当前阶段）**：
  1. `Rank 1 τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `Rank 2 volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ `paper candidate`（窄范围 / **paper_candidate_only / blocked**）
  3. `Rank 3 third-touch + EMA/MACD`（Wiśniewski 2024）→ `park`
  4. `Rank 4 crypto pairs stat-arb`（paper + repo seed）→ `park`

## 接下来优先级 Top 1~3

1. **Rank 2 仅允许 receipt-chain 真回执闭环，不再扩同类说明页**
   - 目标：同一 whitelist-bound replay 上补齐 `intent_ref + ack_ref + cancel_or_close_ref`；
   - 未补齐前继续保持 `paper_candidate_only / blocked`。

2. **若 Scout 没有合格主点，直接回退 tiny-live plumbing**
   - 继续 `handoff / registry / writeback / reconciliation` 链路；
   - 不回头做低杠杆重复叙述。

3. **Rank 1/3/4 默认停在 evidence pool，等待 bot2 明确重开**
   - 不作为默认主资源位。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1757_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 `docs/TODO.md`：本轮需要表达的核心（Rank 2 blocked closeout + receipt audit 0/3）已在顶板由最新 bot3 产物同步到位。
- 不改 cron 频率：`bot3` 频率暂可维持。

### 额外观察（cron 健康）
- `bot2-strategy-review-40m` 当前在 `cron list` 中显示 `error`。
- 最近 3 条 run 记录均为 `cron: job execution timed out`（约 `600s` 超时）。
- 这不改变当前席位判断，但建议下一轮优先做一次执行时长收敛（缩短单轮动作/输出），避免 bot2 持续 timeout。

## 风险与不确定性

1. `Rank 2` 仍未落地真实 receipt chain，所以离 `shadow_parity` 仍有硬距离。
2. 当前候选池里只有 `Rank 2` 处于可前推态，若它长期 blocked，会放大 scout 主线集中度风险。
3. bot2 cron 连续 timeout 会影响 desk 例行可见性；建议尽快压缩单轮执行路径。

## 本轮一句话结论（给 Jerry）

**这轮没有新的 seat-level 改判：EMA 继续 running paper 且 waiting_not_due，Live Seat 继续暂空；Scout 方面仍是 Rank 2 单点前推，但它现在被更明确锁在 `paper_candidate_only / blocked`，receipt audit 显示 BTC/ETH/SOL 三条腿都还是 `0/3` 真实 refs，下一步只能是 whitelist receipt-chain 真回执闭环。**
