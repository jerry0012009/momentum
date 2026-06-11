# Strategy Review (bot2)

Time: 2026-03-30 07:22 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 `fresh intake` 仍是 `Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate`，而且它作为上一条 fresh intake 的唯一 survivor **值得做且尚未用掉** 那一次 follow-up；当前没有 `Active P2`，所以本轮默认排班必须先把 `Rank 248` 的 survivor follow-up 放到最前，然后才用剩余预算切回最近的新论文/新 repo intake（`GMADL directional threshold BTC`、`trend continuation × pullback × correlation-budget shell`、`same-expiry box spread implied-rate`）。

## 1) 读取顺序与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0721_rank12_zone_persistence_gate_not_frontslot.md`
  - `2026-03-30_0700_rank13_rs_semivariance_overlay_not_frontslot.md`
  - `2026-03-30_0647_rank248_dynamic_coint_forecast_threshold_intake_keep_p1.md`
  - `2026-03-30_0604_rank247_survivor_followup_background.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-30_0633_strategy-review.md`
- 为本轮 intake 额外核对：
  - `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
  - `research/quant_digests/2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`
  - `research/quant_digests/2026-03-29_2218_coinmargined-boxspread-rate-alpha.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未作为本轮排班依据
- 前排对象中不存在无 rank 的 `keep_P1/P2/P3` 对象，因此本轮无需补 rank

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

runtime 仍是：
- `current_target = none`
- `connected_runner_live = Rank 200 / Rank 201 / Rank 213 / Rank 229`

因此当前没有需要 bot2/bot3 抢占预算的 `P3 launch wiring` 头部对象。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的 `fresh intake` 是 `Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate`。**

原因：
- `BOT2_BOT3_STATE.md` 的 `Fresh intake slot.current_target` 已写成 `Rank 248`
- `2026-03-30_0647_rank248_dynamic_coint_forecast_threshold_intake_keep_p1.md` 已把它正式判成 `keep_P1`
- 因为它是最近一条 fresh intake，且已进入 `Surviving candidate slot`，所以在 survivor 收口前，它仍是当前前排链条的核心对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

而且这一次 follow-up **还没被执行掉**。

证据：
- `Rank 248` 首轮 verdict 是 `keep_P1`，核心新意不是 generic pairs/z-score 换壳，而是：
  - `dynamic cointegration pair selection`
  - `forecasted spread score percentile trigger`
  - `prediction-interval-width uncertainty gate`
- 当前 blocker 也非常具体，不是泛泛“还要再研究”：
  - 还没在同一口径下直接对照 `forecast-score trigger vs plain z-score threshold`
  - 还没证明 `PIW gate` 是否留下独立净增益
- 这正符合 policy 对 survivor 的定义：只做一次最小 decisive follow-up，回答“这两层到底有没有新增净信息，还是只是把普通 pairs MR 包装得更复杂”

所以它值得那唯一一次 follow-up，而且在诚实收口前默认享有 survivor 锁定权，不能被新的 intake 覆盖。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

runtime 明确写着：
- `Active P2 slot.current_target = none`

最近一次活跃 P2 仍是 `Rank 235`，但它已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 被执行成一次性的 `P2 -> P1 re-scope`，不再属于当前 `Active P2`。

## 3) P2 -> P3 兜底裁判是否触发
**不触发。**

因为：
- `Paper launch queue = none`
- `Active P2 = none`
- 最近材料里没有任何当前前排对象已经明显达到 `paper trade / paper launch` 门槛却还被 bot3 卡在 `P2`

所以本轮不能伪造一个 `P3` 或重新打开旧 P2；最诚实的动作是：
1. 先收口 `Rank 248` 的 survivor
2. 再切回新的 `fresh intake`

## 4) rank 合规检查
前排槽位检查：
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 248`
- `Surviving candidate slot.current_target = Rank 248`
- `Active P2 slot.current_target = none`

其中唯一前排对象 `Rank 248` 已有正式 rank，因此：
**本轮不存在“前排对象达到 keep_P1/P2/P3 但无正式 rank”的违规情况，无需补号。**

## 5) 为什么必须重写 `cycle_plan`
上一版 `cycle_plan` 已被最新结果实质性消费：
- `Rank 248` fresh intake 已完成并进入 survivor
- `Rank 13`、`Rank 12` 已被连续确认“不进入前排”
- 旧计划第 4 项 `Rank 64` 还未做，但它现在已经不该排在 survivor 之前

按 policy 的 authoritative priority ladder：
1. `P3 handoff`：无
2. `P2 admission/promote/park`：无
3. `P1 survivor`：有，而且就是 `Rank 248`
4. 只有把 survivor 诚实排在前面后，才能用剩余预算补新的 `fresh intake`

所以本轮必须把 `Rank 248` survivor follow-up 提到第 1 位，再依次排最近的新报告对象。

## 6) 本轮新的 `cycle_plan` 为什么这样排
### 第 1 项：`Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate`
原因：
- 它是唯一合法 survivor
- policy 明确要求 survivor 的唯一 follow-up 在诚实收口前享有前排锁定权
- 当前 blocker 是单轮可证伪的，不是开放式拖延

### 第 2 项：`BTC 单币 direction-aware loss × thresholded long/short state machine`
原因：
- 来自最近新的 paper/repo alpha 报告
- 与已有近邻相比，最值得审的是 `loss function + abstain threshold` 这条具体对象，而不是 Informer 模型名
- 对 short-horizon directional raw alpha 来说，这条对象边界清楚、可做首轮 intake

### 第 3 项：`trend continuation × pullback re-entry × correlation-budget shell`
原因：
- 也是最近新 repo 报告
- 和已有 trend/pullback 近邻相比，它新增的核心不是“趋势继续涨”本身，而是 `correlation-budget shell` 这一层完整组合外壳
- 若这层真能单轮证伪，就值得作为独立 fresh intake 审理

### 第 4 项：`same-expiry box spread implied-rate 偏离`
原因：
- 仍属最近新 repo/新 alpha 报告，优先级高于 park_reframe 残余
- honesty blocker 具体而清楚：coin-margined unit normalization + executable bid/ask
- 很适合做一次 first verdict：要么确认是值得前排的 options RV raw alpha，要么直接判成 mid 幻觉

## 7) 本轮写回的 runtime 变更
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 个新的 pending 小点：
1. `Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate`
2. `BTC 单币 direction-aware loss × thresholded long/short state machine`
3. `trend continuation × pullback re-entry × correlation-budget shell`
4. `same-expiry box spread implied-rate 偏离`

全部新项均满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 8) repo 状态备注
`git status --short` 仍显示多项未跟踪临时文件与产物；本轮只把它当作环境证据读取，没有把“文件很多”误当成排班理由。

## 9) 一句话结论
这轮没有 `P3`、没有 `Active P2`，但有一个必须先诚实收口的 survivor：`Rank 248`。因此 bot3 下一轮最该做的，不是继续翻 park residual，也不是重开旧对象，而是先用掉 `Rank 248` 那唯一一次 decisive follow-up；只有做完这步，才轮到 `GMADL directional threshold BTC`、`trend continuation × pullback × correlation-budget shell`、`same-expiry box spread implied-rate` 这些新的 intake。