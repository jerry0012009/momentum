# Strategy Review (bot2)

Time: 2026-03-27 18:37 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 fresh intake 仍是 `Rank 200 / BTC weekday-hour sparse short schedule`；它值得并且必须先消耗那唯一一次 survivor follow-up；当前存在明确 `Active P2 = Rank 199 / US cash-session downside cross-asset lead-lag`，但它刚从 survivor 升上来，离最近的出口不是继续拖着 `keep_P2`，而是尽快做一次 admission，直接回答更接近 `P3` 还是 `P1/P0`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：repo 里仍有大量未跟踪产物与历史噪音，但这不构成把 background pool 旧候选重新拉回前排的理由。
- 最近 `optimization_loop/`：
  - `2026-03-27_1831_liquidity_provision_fresh_intake_blocked_front_chain.md`
  - `2026-03-27_1825_rank200_weekday_hour_btc_eventclock_intake_keep_p1.md`
  - `2026-03-27_1757_rank199_survivor_followup_promote_p2.md`
  - `2026-03-27_1718_rank199_us_tech_crypto_intake_keep_p1.md`
  - `2026-03-27_1609_rank198_survivor_param_stability_park.md`
- 最近 `strategy_review/`：
  - `2026-03-27_1750_strategy-review.md`
  - `2026-03-27_1658_strategy-review.md`
  - `2026-03-27_1606_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当作本轮排班依据
- 已检查前排 rank 合规：当前所有达到 `keep_P1` 或更高、且位于前排槽位的对象都已带正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
`Rank 183 / cbeth-eth-rolling-fair-basis-mr`、`Rank 186 / CME expiry postfix short BTC`、`Rank 187 / BTCUSDT 15m late-session path-shape swing` 已在 `2026-03-27_1328_rank183_186_187_paper_runner_wiring_complete.md` 完成 `runner + scheduler + first verified run`，按 policy 已退出 queue。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 200 / BTC weekday-hour sparse short schedule`。**
原因：
- `research/quant_digests/2026-03-27_1555_weekday-hour-bitcoin-eventclock-alpha.md` 已在 `2026-03-27_1825_rank200_weekday_hour_btc_eventclock_intake_keep_p1.md` 完成首轮 intake；
- 它是当前最新一个已经真正进入前排、并拿到正式 rank 的 fresh intake；
- 之后虽然出现了 `2026-03-27_1822_utc-clock-seasonality-alpha.md` 等更新对象，但它们尚未合法进入前排，只能作为后续候选 intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且按 policy 现在必须优先执行。**
`Rank 200` 的首轮结论不是“直接上 P2”，而是：
- 现有论文页 + Binance `1h` quick check 说明“少数固定弱 weekday-hour 后做 BTC 4h short”确实像可复验的 raw alpha pocket；
- 但当前证据仍主要停留在单资产、单 venue、单持有窗的稀疏时钟袋；
- 因此它值得那唯一一次 follow-up，用来直接回答：这到底是可独立 paper 的 sparse scheduler，还是只配降级成其他策略的 event-clock overlay / veto。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2 = Rank 199 / US cash-session downside cross-asset lead-lag`。**
更具体地说，它现在离最近的出口是：
- **先做 admission，再在 `P3 / P1 / P0` 里二选一或三选一；**
- 从已有 desk review 证据看，它还没有被清楚证明足够直接升 `P3`，因为目前只补到了 `source_cost_event_strip` 这一轴；
- 但它也不像应立即掉回 `P0` 的对象，因为 `QQQ+NVDA` 联合 downside shock -> `short ETH 1h` 在更贴近原 digest 的 global decile + Binance perp + 剔除大事件口径下仍保留正净值空间。

所以当前最诚实的描述是：
> `Rank 199` 离 **`P2 exit decision`** 最近；在三个正式出口里，目前**相对更靠近 `P3`**，但还没到 bot2 必须兜底直升的程度，仍应先完成一次 admission 主检查。

## 3) 前排 rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 200`，已有正式 rank
- `Surviving candidate slot`: `Rank 200`，已有正式 rank
- `Active P2 slot`: `Rank 199`，已有正式 rank

结论：本轮不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；无需补发新整数 `Rank`。

## 4) 基于 policy 的当前轮排班重写
按 authoritative priority ladder 扫描当前所有合法动作：
1. `P3 handoff`：无，queue 为空
2. `P2 / Active P2`：有，而且这是当前最高优先级动作——`Rank 199` admission / promote / park
3. `P1 / Surviving candidate`：有——`Rank 200` 的唯一一次便宜但诚实 follow-up
4. `fresh intake`：只能在前两者已经被诚实排进前部后，再用剩余预算补具体对象

因此本轮 `cycle_plan` 已重写为：
1. `Rank 199 / US cash-session downside cross-asset lead-lag`
   - 先做 `P2 admission` 主检查
   - 重点围绕 `effectiveness / cross-asset / time / parameter / honesty`
   - 要求直接回答它是否够格升 `P3 / Paper launch queue`
2. `Rank 200 / BTC weekday-hour sparse short schedule`
   - 用掉 survivor 唯一 follow-up
   - 重点核验 `4/8/12 bps`、rolling refresh、spot/perp 口径与轻微持有窗扰动
   - 直接回答升 `P2` 还是移回 `Background pool`
3. `research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md`
   - 仅在前排 `P2/P1` 已诚实排进前部后，才作为 fresh intake 进入
4. `research/quant_digests/2026-03-27_1748_graph-matching-pairbook-meanreversion.md`
   - 若预算仍有余，再作为第二个 fresh intake 进入

这次重排比上一版更符合 policy，原因有三点：
- `Rank 199` 已进入 `Active P2`，因此必须前置到 `Rank 200` 之前；
- `Rank 200` 仍拥有 survivor 的唯一 follow-up 锁，不能被新的 intake 覆盖；
- 新的 intake 必须是具体对象，且只能在前排链条已被诚实摆在前部后补入。

## 5) bot2 兜底裁判结论
- 当前没有漏升 `P3` 的对象需要 bot2 直接强推；
- 也没有待补接线的 `P3 handoff`；
- `Rank 199` 目前还不满足“desk review 已清楚表明足够值得直接 paper trade”的强兜底条件；
- 所以本轮 bot2 的职责不是硬升 `P3`，而是把当前前排顺序校正回：**先 `Rank 199` admission，再 `Rank 200` follow-up，然后才是新的 intake。**

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
- 删除已完成/已失效的旧排班表述；
- 重写为当前合法顺序：
  1. `Rank 199` admission
  2. `Rank 200` survivor follow-up
  3. `utc-clock seasonality` fresh intake
  4. `graph-matching pairbook meanreversion` fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 7) 一句话结论
这轮最重要的不是再找新故事，而是把前排顺序摆正：`Rank 199` 先做 admission，`Rank 200` 再做唯一 follow-up；只有这两件事已经诚实排在前面时，新的 intake 才能合法补进来。