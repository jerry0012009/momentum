# Strategy Review (bot2)

Time: 2026-03-26 22:30 UTC

## 本轮一句话判断
`Paper launch queue` 明确非空；本轮新的 fresh intake 已是 `Rank 189`，它值得那唯一一次 survivor follow-up；当前存在明确 `Active P2 = Rank 188`，且它离 `P3` 最近，因此本轮默认排班应先把 `Rank 188` 做成 admission 收口链，再兑现 `Rank 189` 的唯一 follow-up，最后才允许补 conditional fresh intake。

## 1) 先读 policy + state
已先读取：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

硬约束保持：
- 只更新 `BOT2_BOT3_STATE.md`
- 不改写 policy / brief / operating card / auto loop / cron prompt
- 不自动把 background pool 旧候选拉回前排
- 最近日志只作 evidence，不反向改 policy

前排 rank 合规检查：
- `Paper launch queue`: `Rank 183`; `Rank 186`; `Rank 187`
- `Surviving candidate`: `Rank 189`
- `Active P2`: `Rank 188`
- 结论：**当前前排对象全部已有正式整数 Rank，无需补号。**

## 2) 再读 repo 状态、最近 optimization_loop、最近 strategy_review
### Repo 状态
- `git status --short --branch` 显示 repo 里仍有大量未跟踪 `reports / artifacts / scripts`。
- 这些只算近期研究 evidence，不构成排班依据，更不能反向把旧对象从 background pool 拉回前排。

### 最近 `research/optimization_loop/`
本轮采纳的关键 evidence：
1. `2026-03-26_2153_rank188_survivor_followup_promote_p2.md`
   - `Rank 188` 已通过 survivor 唯一 cheap follow-up，确认 `top-k=2~4 + 16-bar sparse rebalance + BTC gate` 相对 dense 版本出现了真实 turnover compression 与小幅正 gross pocket。
   - 这说明它不该继续停在 `P1`，而应进入正式 `P2 admission`。
2. `2026-03-26_2219_rank189_hyperliquid_funding_rich_4h_intake_keep_p1.md`
   - 新 fresh intake 已明确收口为 `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`。
   - 按 policy，既然它首判是 `keep_P1`，就依法拥有且只拥有那一次 survivor follow-up。
3. `2026-03-26_2022_rank183_p3_handoff_reconfirm.md`
   - `Rank 183` queue-head handoff 仍闭环，没有新的 launch-facing 缺口。
4. `2026-03-26_1900_rank186_honesty_exit_promote_p3.md`
   - `Rank 186` 已完成 `P2 -> P3`，当前处于 queue-side handoff-ready，而不是待 admission 的 `P2`。
5. `2026-03-26_2010_rank187_p2_exit_promote_p3_execution_realism.md`
   - `Rank 187` 也已完成 `P2 -> P3`，当前同样属于 queue-side handoff-ready，而不是待 admission 的 `P2`。

### 最近 `research/strategy_review/`
- 最近一篇 review：`2026-03-26_2150_strategy-review.md`
- 相比上一轮，本轮变化非常明确：
  - 上一轮时 `Rank 188` 的 survivor 唯一 follow-up 还没落地；
  - 现在它已正式进入 `Active P2`；
  - 同时 `Rank 189` 刚完成 fresh intake 并锁定 survivor 槽位。
- 因此这轮的前排收口顺序不再是“先 survivor 再 intake”，而是**先 `P2 admission`，再 survivor，最后才是 conditional fresh intake**。

## 3) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
- `current_target`: `Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- `queued_handoff_ready`: `Rank 186 / CME expiry postfix short BTC`; `Rank 187 / BTCUSDT 15m late-session path-shape swing`

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 已经是 `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`。**
- 它来自 `research/quant_digests/2026-03-26_2146_hyperliquid-funding-rich-4h-crowding-alpha.md`
- 当前值得保留的是这条单轴对象，而不是整个 funding carry screener / dashboard。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
- 上一条 fresh intake 正是当前 `Rank 189`；
- intake 已经证明：在近一个月 Hyperliquid 公共样本里，`current funding richest-vs-cheapest 4h` 在扣未来 funding cashflow 与 `8bps` 成本后仍留有正 net pocket；
- 当前唯一尚未回答的问题也足够便宜且 decisive：**这是不是只是高-beta / 热门赛道 / 上新币暴露的替身。**
- 因此它依法应该拿到那唯一一次 survivor follow-up，而不是被新的 intake 覆盖掉。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在：`Active P2 = Rank 188 / extreme-only sparse top-k shock reversal skeleton`。它目前离 `P3` 最近。**
- 理由不是它已经够格直接升 `P3`，而是：
  - dense 版本早已被否；
  - 唯一保留的窄 re-scope 在更低换手下已恢复成小幅正 gross；
  - 这使它当前更像一个**值得继续 admission、可能向 paperable pocket 收口** 的对象，而不是更接近 `P1/P0` 的失败边缘。
- 当然，这个“更接近 `P3`”仍需 admission 把 `effectiveness / cross-asset / time / parameter / honesty` 这五类问题补齐；若 admission 发现 edge 只是少数币或短窗巧合，再落回 `P1/P0` 也完全允许。

## 4) 前排 rank 合规检查
- `Paper launch queue`：`Rank 183 / Rank 186 / Rank 187`
- `Surviving candidate slot`：`Rank 189`
- `Active P2 slot`：`Rank 188`
- **全部已有正式整数 Rank，无需补发。**

## 5) bot2 兜底裁判检查
本轮 bot2 兜底裁判结论：
- 当前没有“bot3 明明该升 P3 却没升”的滞留 `Active P2`；
- `Rank 186` 与 `Rank 187` 已经诚实升级到 `P3`，`Rank 183` 继续是 queue head；
- 所以本轮不需要 bot2 代替 bot3 做强制 `P2 -> P3` 改写；
- 真正该做的是：**别让 `Rank 188` 在 `P2` 里开放式漂着，也别让 `Rank 189` 的 survivor 锁定权被新的 intake 抢掉。**

## 6) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序：
1. `P3 handoff`
2. `P2 admission/promote/park`
3. `P1 survivor 唯一一次诚实检查`
4. `fresh intake`

本轮诚实判断：
- `P3` 当前没有新的真实动作，只是 queue 继续保持闭环；
- `P2` 当前有明确真实动作：`Rank 188` admission；
- `P1` 当前也有明确真实动作：`Rank 189` survivor 唯一 follow-up；
- 所以新的 intake 只能放在这些前排动作之后，不能插队。

## 7) 本轮重写后的 `cycle_plan`
### 1. `Rank 188` P2 admission 第一刀
- `target`: `Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- `action`: 先做 `P2 admission` 第一刀，只回答 `effectiveness / expected return` 与 `cross-asset stability`：在更完整主流 perp universe 与统一成本口径下，`top-k=2~4 + 16-bar sparse rebalance + BTC gate` 的 net edge 是否仍保留、还是主要靠少数币种硬撑
- `success_criterion`: 必须对 `Rank 188` 产出单一 admission 结论句（允许 `keep_P2` 或直接出口），且必须明确回答这条 pocket 是 broad enough 值得继续 admission，还是已接近 `P1/P0`；不得回头重开已判负的 dense 版本
- `result`: `none`
- `status`: `pending`

### 2. `Rank 188` P2 admission 第二刀
- `target`: `Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- `action`: 若第 1 项未直接给出出口，再做同一对象的第二刀 admission，只回答 `time stability / parameter stability / honesty-execution realism`：确认 `16-bar sparse + top-k` 是否只是短窗巧合、参数脆点，还是已足以支持继续朝 `P3 / P1 / P0` 出口收口
- `success_criterion`: 必须基于与上一轮不同的 axis 给出单一 admission 结果句（`keep_P2`、`promote_P3`、`one-time P2->P1 re-scope`、或 `drop_to_background` 之一）；若仍为 `keep_P2`，必须明确剩下的唯一 blocker，不能写第三次开放式 admission 模板
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
**这轮不该再盯 queue 做空转确认；真正该推进的是：先把 `Rank 188` 做成 admission 收口链，再兑现 `Rank 189` 那唯一一次 survivor follow-up，最后才轮到 conditional fresh intake。**
