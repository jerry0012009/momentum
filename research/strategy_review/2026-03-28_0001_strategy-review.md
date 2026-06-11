# Strategy Review (bot2)

Time: 2026-03-28 00:01 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮 `fresh intake` 仍是 `Rank 206 / CTTrend 横截面技术复合信号`；上一条 fresh intake `Rank 205 / par-local-drift crossover` 值得拿到那唯一一次 follow-up；当前存在明确 `Active P2 = Rank 203 / graph-matching pairbook mean-reversion`，而且它离 `P3 / Paper launch queue` 最近，但还需要一次不重复上一轮 axis 的 admission 出口决策。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact，但这些只能当作最近运行证据，不得反向改 policy，也不得据此把 background pool 旧候选拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-27_2344_rank206_cttrend_xs_technical_composite_intake_keep_p1.md`
  - `2026-03-27_2329_rank205_par_local_drift_crossover_intake_keep_p1.md`
  - `2026-03-27_2307_rank203_survivor_followup_promote_p2.md`
  - `2026-03-27_2254_rank204_liquidity_provision_xs_short_reversal_intake_keep_p1.md`
  - `2026-03-27_2233_rank203_graph_matching_pairbook_intake_keep_p1.md`
  - `2026-03-27_2216_rank201_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-27_2303_strategy-review.md`
  - `2026-03-27_2206_strategy-review.md`
  - `2026-03-27_2127_strategy-review.md`
- 额外读取了最近新 digest：
  - `research/quant_digests/2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`
  - `research/quant_digests/2026-03-27_2344_extreme-return-shock-percentile-alpha.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 已核对前排对象 rank：`Rank 203 / 205 / 206 / 200 / 201` 均已有正式整数 rank，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
原因：
- `Rank 200` 已完成 runner + scheduler + 首跑验证；
- `Rank 201` 已在 `2026-03-27_2216_rank201_p3_launch_wiring_connected_runner_live.md` 完成最小 launch wiring；
- 当前 queue-side 没有等待接线的头部对象。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 仍是 `Rank 206 / CTTrend 横截面技术复合信号`。**
依据：
- `Fresh intake slot` 当前仍指向 `research/quant_digests/2026-03-27_1352_cttrend-xs-technical-composite-alpha.md`；
- 它的最新正式结果是 `2026-03-27_2344_rank206_cttrend_xs_technical_composite_intake_keep_p1.md`；
- 后面 23:22 / 23:44 的两个新 digest 目前还只是可选下一轮 intake 来源，尚未完成首判，因此还不能替换当前 runtime 的 `fresh intake` truth。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在就该由它占据 survivor 槽位。**
上一条 fresh intake 是 `Rank 205 / par-local-drift crossover`：
- 它已在 `2026-03-27_2329_rank205_par_local_drift_crossover_intake_keep_p1.md` 获得正式 `keep_P1`；
- 唯一高杠杆问题非常明确：这条 `rolling local drift / prediction line + buffered crossover + opposite flip` 是否真的比 `EMA / Donchian / N-bar continuation` 这类简单 trend baseline 多出新增 alpha；
- 这正符合 policy 里 survivor 只能做一次便宜而 decisive 的 follow-up 的定义。

所以答案不是“可做可不做”，而是：**值得，而且应优先于任何新的 fresh intake。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2 = Rank 203 / graph-matching pairbook mean-reversion`，而且它离 `P3` 最近。**
理由：
- 最新 admission 结论已经说明：在更强 pair admission 下，`max-degree<=2` 的 capped-overlap hybrid 是当前唯一略为净正、且优于 `full non-overlap` 与 overlap baseline 的形态；
- 这说明它不再像一个等待重写 spec 的 `P1`，也没有出现明显 fatal flaw 迫使它靠近 `P0`；
- 当前最诚实的下一问不是“要不要继续开放研究”，而是 **在更现实 friction / execution 口径下，它是否已经足够值得进入 paper trade**。

因此，按 policy 的出口优先级，它当前更接近 `P3`，不是 `P1` 或 `P0`。

## 3) 前排 rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 206`，已有正式 rank
- `Surviving candidate slot`: `Rank 205`，已有正式 rank
- `Active P2 slot`: `Rank 203`，已有正式 rank

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；
- 本轮无需补新的整数 `Rank`；
- 需要调整的是本轮排班顺序与具体对象，不是 rank identity。

## 4) 本轮排班判断
按 policy 默认顺序扫描：

1. **P3 / Paper launch queue**
   - 当前无待接线对象；无真实可执行动作。
2. **P2 / Active P2**
   - 有，而且这是当前最高优先级动作：`Rank 203` 必须进入 admission 出口决策轮。
3. **P1 / Surviving candidate**
   - 有，而且必须紧随其后：`Rank 205` 的 survivor 唯一 follow-up 不能被新的 intake 覆盖。
4. **fresh intake**
   - 只有在上面两类动作已诚实排在前部后，才用剩余预算补新对象。

本轮 fresh intake 具体对象优先选了最近两个新 digest：
- `2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`
- `2026-03-27_2344_extreme-return-shock-percentile-alpha.md`

原因：
- 都是最近新增；
- 都是和当前前排不同的单资产短周期 raw alpha skeleton；
- 相比继续保留更旧的抽象占位，它们更符合 policy 要求的“具体值得做的任务”。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**本轮还不到必须直接写入 `P3 / Paper launch queue` 的程度。**

我对 `Rank 203` 的判断是：
- 它已经明显不该退回开放式 `keep_P2` 拖延；
- 但当前手头证据还只是“略为净正 + capped-overlap 优于其他 pair-book 结构”的 admission 起点；
- 在没有把现实 friction / execution realism 明确收口前，还不能替 bot3 直接把它写成 `P3` runtime truth。

所以 bot2 本轮做的兜底不是“强推到 P3”，而是：
> **把 `Rank 203` 明确排成一次 admission 出口决策轮，而且 success criterion 直接写到 `P3 / P2->P1 / P0` 三选一，不再允许第三种开放式拖延。**

这符合 policy：
- 不把够格的 P3 继续拖研究；
- 也不在证据还差最后一层 execution/honesty 收口时，提前伪装成已过线。

## 6) 对 state 的实际写回
本轮仅更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Rank 203 / graph-matching pairbook mean-reversion`
   - `Active P2` admission 出口决策轮
   - 明确要求在统一成本/执行口径下回答 `P3 / P2->P1 / P0`
2. `Rank 205 / par-local-drift crossover`
   - survivor 唯一 follow-up
   - 与简单 trend baseline 同框诚实对照
3. `research/quant_digests/2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`
   - 具体 fresh intake
4. `research/quant_digests/2026-03-27_2344_extreme-return-shock-percentile-alpha.md`
   - 具体 fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- 新排项 `result = none`
- 新排项 `status = pending`

## 7) 一句话结论
这轮最重要的不是再翻旧候选，而是把前排链条诚实收口：**先让 `Rank 203` 做 `P2` 出口决策，再让 `Rank 205` 用掉 survivor 唯一预算，最后才切到两个最新、最具体的新 intake。**