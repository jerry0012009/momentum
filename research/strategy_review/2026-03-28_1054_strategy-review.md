# Strategy Review (bot2)

Time: 2026-03-28 10:54 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空，且 `Rank 213` 还停在 `queued_handoff_ready`；当前唯一合法 survivor 已切到 `Rank 219`，所以本轮排班必须先做 `Rank 213` 的 `P3 launch wiring`，再做 `Rank 219` 的唯一 follow-up，之后才轮到新的 fresh intake。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1052_rank219_liquidity_ranked_ema_trend_intake_keep_p1.md`
  - `2026-03-28_1031_rank218_drift_hyperliquid_basis_intake_keep_p1.md`
  - `2026-03-28_1017_rank216_survivor_followup_close_to_background.md`
  - `2026-03-28_0954_rank213_p3_queue_handoff_packet_done.md`
  - `2026-03-28_0852_rank213_p2_exit_promote_p3_deploy_ready_spec.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0934_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
  - `research/quant_digests/2026-03-28_1010_survivor-universe-momentum-falsification-card.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象都有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，当前非空。**
- `current_target = Rank 213 / large-cap XS momentum × short-leg jump veto`
- `latest_result_record = research/optimization_loop/2026-03-28_0954_rank213_p3_queue_handoff_packet_done.md`
- `Rank 200`、`Rank 201` 继续留在 `connected_runner_live`
- 结论：本轮第一优先级仍然是 `Rank 213` 的 `P3 launch wiring`，不是新的 alpha 研究

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部应切到 `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`。**
原因：
- 当前不存在 `Active P2`
- 当前存在明确 `Paper launch queue = Rank 213`
- 当前存在明确 `Surviving candidate = Rank 219`
- `Rank 218` 与 `Rank 219` 已各自产出首轮正式 verdict，不再是“本轮未处理的 fresh intake”
- 在剩余最近新 repo / paper / alpha report 里，`1033 ETH whale balance imbalance alpha` 是最新且最具体的未处理对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`：
- 首判已明确为 `keep_P1`
- 留下的问题也足够集中：不是“这条趋势线还行不行”，而是 `top-1 liquidity rotation + funding/vol veto + hard exits` 相对朴素单币趋势 baseline 是否真有独立 after-cost 增益
- 这正符合 policy 允许的唯一一次便宜且诚实的 decisive follow-up

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已在 `2026-03-28_0852` 从 `P2` 正式收口并升级到 `P3 / Paper launch queue`
- 当前前排里没有待 admission 的 `Active P2`
- 所以本轮不存在“某个 Active P2 离哪个出口最近”的比较题；离出口最近的前排动作仍是 `Rank 213` 的 launch wiring

## 3) rank 合规检查
- `Paper launch queue`: `Rank 213`，有 rank
- `Fresh intake slot`: `Rank 219`，有 rank
- `Surviving candidate slot`: `Rank 219`，有 rank
- `Active P2 slot`: none

结论：
- 当前不存在前排对象已达 `keep_P1 / P2 / P3` 但无正式 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：有，且必须排第一 —— `Rank 213` 的最小 `launch wiring`
2. `P2 / Active P2`：无，不占位
3. `P1 / Surviving candidate`：有，且必须排第二 —— `Rank 219` 的唯一 survivor follow-up
4. `fresh intake`：前两项诚实排入后，再排最新合法具体对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 213 / large-cap XS momentum × short-leg jump veto`
   - 做最小 `P3 launch wiring`
2. `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
   - 做唯一 survivor follow-up
3. `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
   - 当前 fresh intake 头部
4. `research/quant_digests/2026-03-28_1010_survivor-universe-momentum-falsification-card.md`
   - 条件性下一条 fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 是否需要 bot2 直接兜底推进到 P3？
**本轮不需要新增兜底改判，因为该动作已经在 state 中兑现。**
- `Rank 213` 的 desk evidence 早已足够清楚：对象值得进入 `paper trade / paper launch`
- state 也已把它从 `Active P2` 移入 `Paper launch queue`
- 现在 bot2 的责任不再是“是否升 P3”，而是继续强制把它排成 `P3 launch wiring`，直到接线完成

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 213` 的 `P3 launch wiring`
2. `Rank 219` 的唯一 survivor follow-up
3. `1033 ETH whale balance imbalance alpha` fresh intake
4. `1010 survivor-universe momentum falsification card` fresh intake

## 7) 一句话结论
这轮没有新的 `Active P2` 可拖；真正该做的是先把 `Rank 213` 往 live runner 接线推进，再把 `Rank 219` 那次唯一 follow-up 诚实做完，最后才轮到新的 ETH whale 事件型 alpha intake。