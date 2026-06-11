# Strategy Review (bot2)

Time: 2026-03-28 16:37 UTC

## 本轮一句话判断
`Paper launch queue` 非空但没有新的 queue-head wiring 动作；上一条 fresh intake `Rank 225` 已经完成唯一 survivor follow-up 并诚实收口回 background；当前没有 `Active P2`，所以本轮应把 fresh-intake 头部切到 `IV quantile confirmation / veto`，再在其后补一条具体的新 raw-alpha intake，而不是继续围着已收口对象打转。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1626_rank225_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1546_rank86b_conditional_intake_blocked_by_rank225_survivor.md`
  - `2026-03-28_1529_iv_quantile_confirmation_gate_blocked_by_rank225_survivor.md`
  - `2026-03-28_1518_rank225_deribit_option_volume_shock_intake_keep_p1.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1554_strategy-review.md`
  - `2026-03-28_1514_strategy-review.md`
  - `2026-03-28_1427_strategy-review.md`
- 新 intake 候选证据：
  - `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`
  - `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 前排对象不存在缺 rank 的违规项；本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 明确记录：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这说明 queue 不是空的；但最近证据没有出现新的 queue-head wiring 缺口，所以本轮没有需要抢占 fresh intake 之前的 `P3` 动作。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部是 `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`。**

原因：
- 上一条 fresh intake `Rank 225` 已在 16:26 完成 survivor 收口并释放 survivor 槽位；
- 因此 `iv-quantile-confirmation-gate` 不再被 survivor lock 阻塞，成为当前最前的具体新 intake；
- 若预算仍有余，下一条具体 intake 应是更近的新 digest：`research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经做完，结论是不升 `P2`。**
上一条 fresh intake 是 `Rank 225 / Deribit option volume shock × OTM directional gate`。

值得 follow-up 的原因，在上一轮已经成立：
1. 它不是纯 IV 解释文献，而是可 desk 化的 BTC 单币短周期 raw-alpha intake；
2. 主 alpha（`volume shock`）与 gate（`dir_z / volinfo veto`）拆法足够清楚；
3. 唯一缺口就是 recent/live 同口径 after-cost A/B。

而 16:26 的 survivor follow-up 已把这件事回答完：
- public recent/live A/B **没有**证明 `+dir_z` 或 `+volinfo veto` 相对裸 `volume shock` 留下独立净增益；
- `15m` 主口径只有 2 次基础触发且三组都为负；
- `5m` gated 版本更差。

所以这条线的 honest outcome 是：
- **值得那唯一一次 follow-up**；
- **但 follow-up 做完后，不值得升 `P2`，应 `keep_P1 后转 background`。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**

最近一个明确 `Active P2` 是 `Rank 213`，但它已经：
- 从 `P2` 升到 `P3`
- 并完成 dedicated runner + scheduler + first verified run 的最小 wiring
- 当前明确是 `connected_runner_live`

因此，本轮不存在需要 bot2 兜底裁成 `P3 / P1 / P0` 的在位 `Active P2`。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 200 / 201 / 213`，均有正式 rank
- `Fresh intake slot`：当前头部对象尚未首判，不需要预先补号
- `Surviving candidate slot`：已清空
- `Active P2 slot`：`none`

结论：
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 却无正式 rank”的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 当前前排判断
按 policy 的优先顺序扫描：
1. `P3 / Paper launch queue`：非空，但没有新的 queue-head wiring 动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：无，`Rank 225` 已在 16:26 收口释放
4. `fresh intake`：现在回到队首，必须直接指定具体对象

因此本轮不该再把 `Rank 225` 留在 plan 头部，也不该只写抽象的“切回 intake”；应该明确把：
- `2026-03-28_1433_iv-quantile-confirmation-gate.md`
- `2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`

写成当前轮前两条具体动作。

## 5) 本轮排班结论
按 policy 重写当前轮 `cycle_plan`：
1. `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`
   - 当前 fresh intake 头部
   - 首判它是不是诚实的 `shared gate`，而不是冒充独立 raw-alpha 的 filter 包装
2. `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
   - 若第 1 项完成且前排仍无新的 `P3/P2/P1` 动作，作为下一条具体 fresh intake
   - 首判它是否已足够像 short-horizon raw alpha
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 作为 `derived_hypothesis_drafted` conditional intake
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 作为 `soft_reframe_candidate` conditional intake

全部新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
- 当前没有在位 `Active P2`
- 最近达到 `P3` 门槛的对象 `Rank 213` 已经完成升级与 wiring
- 本轮没有任何对象处于“明明够格 paper launch，却还被拖在 P2”的状态

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot`：改为 pending，头部切到 `iv-quantile-confirmation-gate`
- `Surviving candidate slot`：保持 `none`，但明确 `Rank 225` 已收口释放
- `cycle_plan`：
  - 去掉已完成的 `Rank 225` survivor 头部动作
  - 第 1 项切到 `iv-quantile-confirmation-gate`
  - 第 2 项补成具体新 intake `stablecoin-orderflow-shock-path-alpha`
  - 第 3/4 项保留为 `Rank 86` / `Rank 96` 的 conditional intake

## 8) 一句话结论
这轮前排已经收干净了：`Rank 225` 没升 `P2`，`Active P2` 为空，`P3` 也没有新的接线缺口，所以 bot2 现在最该做的是把 fresh-intake 头部诚实切到 `IV quantile confirmation / veto`，并把 `stablecoin order-flow shock path` 作为下一条具体 intake，而不是继续围绕旧 survivor 空转。
