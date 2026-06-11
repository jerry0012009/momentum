# Strategy Review (bot2)

Time: 2026-03-26 23:10 UTC

## 本轮一句话判断
`Paper launch queue` 明确非空；本轮 fresh intake 仍是 `Rank 189`，而且它依法值得那唯一一次 survivor follow-up；当前存在明确 `Active P2 = Rank 188`，但它在连续两次 `keep_P2` 后已不能再开放式续写，下一轮必须直接做出口决策轮；同时 queue-head `Rank 183` 仍应先按 `P3 handoff` 继续保持接线路径闭环。

## 1) 先读 policy + state
已先读取：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

硬约束保持：
- 只更新 `BOT2_BOT3_STATE.md`
- 不改写 policy / brief / operating card / auto loop / cron prompt
- 不自动把 background pool 旧候选拉回前排
- 最近日志只作 evidence，不反向改 policy
- `docs/TODO.md` 不作为本轮排班依据

前排 rank 合规检查：
- `Paper launch queue`: `Rank 183`; `Rank 186`; `Rank 187`
- `Fresh intake / Surviving candidate`: `Rank 189`
- `Active P2`: `Rank 188`
- 结论：**当前前排对象全部已有正式整数 Rank，无需补号。**

## 2) 再读 repo 状态、最近 optimization_loop、最近 strategy_review
### Repo 状态
- `git status --short` 仍显示大量未跟踪 `reports/artifacts/scripts`。
- 这些只算近期研究 evidence，不构成排班依据，也不能反向把旧对象从 background pool 拉回前排。

### 最近 `research/optimization_loop/`
本轮采纳的关键 evidence：
1. `2026-03-26_2306_rank188_p2_admission_time_parameter_honesty_keep_p2.md`
   - `Rank 188` 第二刀 admission 已完成，结论仍是 `keep_P2`；
   - 但关键变化不是“继续研究”，而是它已经明确触发 policy 红线：**连续 2 次 `keep_P2`**；
   - 当前剩余唯一 blocker 已被压缩到 `time stability`，所以下一轮必须直接做出口决策，不能再写第三次开放式 admission。
2. `2026-03-26_2247_rank188_p2_admission_effectiveness_crossasset_keep_p2.md`
   - 第一刀 admission 已确认这条 sparse pocket 还有薄正 effectiveness，但 cross-asset 仍偏窄。
3. `2026-03-26_2219_rank189_hyperliquid_funding_rich_4h_intake_keep_p1.md`
   - 新 fresh intake 已明确收口为 `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`；
   - 按 policy，既然它首判是 `keep_P1`，就依法拥有且只拥有那一次 survivor follow-up。
4. `2026-03-26_2022_rank183_p3_handoff_reconfirm.md`
   - `Rank 183` 的 queue-head handoff 仍闭环，没有新的 launch-facing 单一缺口；
   - 这说明当前合法动作不是把它拖回 `P2`，而是继续把 `P3 handoff` 放在排班最前。
5. `2026-03-26_2040_rank186_queue_handoff_reconfirm.md` 与 `2026-03-26_2053_rank187_queue_handoff_reconfirm.md`
   - `Rank 186`、`Rank 187` 已是 handoff-ready queue backlog，而不是待 admission 的 `P2`。

### 最近 `research/strategy_review/`
- 最近一篇 review：`2026-03-26_2230_strategy-review.md`
- 相比上一轮，本轮变化非常明确：
  - 上一轮只是把 `Rank 188` 排成 admission 两刀；
  - 现在两刀都已执行完成，且正式形成 `2 次连续 keep_P2`；
  - 因此这轮不能再重复 admission 模板，而必须改成 **出口决策轮**。

## 3) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
- `current_target`: `Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- `queued_handoff_ready`: `Rank 186 / CME expiry postfix short BTC`; `Rank 187 / BTCUSDT 15m late-session path-shape swing`

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 仍是 `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`。**
- 它来自 `research/quant_digests/2026-03-26_2146_hyperliquid-funding-rich-4h-crowding-alpha.md`
- 当前值得保留的是这条单轴对象，而不是整个 funding carry screener / dashboard。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
- 上一条 fresh intake 正是当前 `Rank 189`；
- intake 已经证明：在近一个月 Hyperliquid 公共样本里，`current funding richest-vs-cheapest 4h` 在扣未来 funding cashflow 与 `8bps` 成本后仍留有正 net pocket；
- 当前唯一尚未回答的问题也足够便宜且 decisive：**这是不是只是高-beta / 热门赛道 / 上新币暴露的替身。**
- 因此它依法应该拿到那唯一一次 survivor follow-up，而不是被新的 intake 覆盖掉。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在：`Active P2 = Rank 188 / extreme-only sparse top-k shock reversal skeleton`。它现在离“出口决策”最近，而在三个出口里默认先优先回答 `P3`，不是继续开放式 `keep_P2`。**
- 理由不是它已经稳稳够格 `P3`，而是 policy 明确规定：`P2` 连续两次 `keep_P2` 后，下一轮必须直接做 `promote_P3 / drop_to_background / one-time P2->P1 re-scope` 三选一；
- 当前它的唯一 blocker 只剩 `time stability`，所以最先该回答的是：这条窄 pocket 是否仍**足够值得进入 paper trade / paper launch**；
- 若答案不成立，才分别落到 `P0` 或（仅在出现唯一明确 re-scope 时）一次性 `P2->P1`。

## 4) 前排 rank 合规检查
- `Paper launch queue`：`Rank 183 / Rank 186 / Rank 187`
- `Surviving candidate slot`：`Rank 189`
- `Active P2 slot`：`Rank 188`
- **全部已有正式整数 Rank，无需补发。**

## 5) bot2 兜底裁判检查
本轮 bot2 兜底裁判结论：
- 当前没有新的明显“bot3 明明该升 P3 却还没升”的 queue-side 漏判对象；
- `Rank 183 / 186 / 187` 已在 `P3 / handoff` 路径内；
- `Rank 188` 虽未达到 bot2 必须强制代升 `P3` 的明确门槛，但它也绝不能继续拖成第三次开放式 `keep_P2`；
- 因此本轮的兜底动作不是越权代升，而是**把 `cycle_plan` 强制改写成合规的出口决策轮**。

## 6) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序：
1. `P3 handoff`
2. `P2 admission/promote/park`
3. `P1 survivor 唯一一次诚实检查`
4. `fresh intake`

本轮诚实判断：
- `P3` 当前仍有真实动作：queue-head `Rank 183` 的最小 handoff 接线闭环应继续放在最前；
- `P2` 当前也有真实动作：`Rank 188` 必须改成出口决策轮，不能再写 admission 模板；
- `P1` 当前有真实动作：`Rank 189` survivor 唯一 follow-up；
- 因为 `Rank 188` 已出现 `2 次连续 keep_P2`，policy 默认还应保留 `1 个 conditional fresh intake` 小点；
- 所以新的 intake 只能放在前排动作之后，不能插队。

## 7) 本轮重写后的 `cycle_plan`
### 1. `Rank 183` P3 handoff 最小接线
- `target`: `Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- `action`: 先做 `P3 handoff` 最小接线收口：只确认 queue-head 的 launch-facing 交接包与当前排队顺序仍闭环，且不因 `Rank 186/187` 的 handoff-ready 状态而错误改写 queue head
- `success_criterion`: 必须对 `Rank 183` 产出单一 handoff 结论句（继续保持 queue head / 或发现唯一明确 handoff 缺口）；不得把它拖回 `P2` compare，也不得把 queue-side 空转确认写成泛化 guard
- `result`: `none`
- `status`: `pending`

### 2. `Rank 188` P2 出口决策轮
- `target`: `Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- `action`: 直接做 `P2 exit decision`，只围绕当前已压缩出的唯一 blocker `time stability` 回答三选一：这条 `extreme-only + top-k + 16-bar sparse + BTC veto` 窄 pocket 是否已足够值得进 `P3 / Paper launch queue`，还是应 `drop_to_background`；只有出现唯一明确新 re-scope 时才允许一次性 `P2->P1`
- `success_criterion`: 必须对 `Rank 188` 给出单一出口结论（`promote_P3`、`drop_to_background`、或 `one-time P2->P1 re-scope` 之一）；不得写第三次开放式 `keep_P2`，也不得重复上一轮已回答过的 effectiveness / parameter / honesty 轴
- `result`: `none`
- `status`: `pending`

### 3. `Rank 189` survivor 唯一 follow-up
- `target`: `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`
- `action`: 对 survivor 做唯一一次 cheap decisive follow-up，只回答把 `current funding` 横截面做最小 beta / sector / listing-age 去偏后，`richest-vs-cheapest 4h` 的正 sign 是否仍保留，还是应诚实 `park_to_background`
- `success_criterion`: 必须对 `Rank 189` 产出单一 survivor 结论（`promote_P2` 或 `park_to_background`）；不得继续停在开放式 `keep_P1`，也不得把整个 funding carry screener 搬进前排
- `result`: `none`
- `status`: `pending`

### 4. conditional fresh intake
- `target`: `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
- `action`: 仅在前 3 项已诚实收口后，作为 conditional fresh intake 检查 `Rank 96` 的 `short-side second-touch + candle-quality admission-delay` 窄派生是否足以形成新的单轴 fresh object
- `success_criterion`: 必须对该明确对象产出单一首判 verdict（`park` 或 `keep_P1`）；若为 `keep_P1`，必须明确保留的是 `short-side second-touch + candle-quality admission-delay` 这条唯一窄轴，而不是重开原 Rank 96 全家桶
- `result`: `none`
- `status`: `pending`

## 8) 本轮实际写回
- 已写回 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧对象自动拉回前排

## 9) 一句话结论
**这轮最该防的不是漏掉新 intake，而是让 `Rank 188` 在 `P2` 里第三次开放式漂着；所以正确排班是：先保持 `Rank 183` 的 `P3` 接线，再把 `Rank 188` 直接排成出口决策轮，随后兑现 `Rank 189` 的 survivor 锁定权，最后才补 conditional fresh intake。**
