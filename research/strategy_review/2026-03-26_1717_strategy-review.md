# Strategy Review (bot2)

Time: 2026-03-26 17:17 UTC

## 本轮一句话判断
当前 `Paper launch queue` 仍非空且由 `Rank 183` 占据，`Active P2` 仍为空；前排唯一真实必须先收口的动作是 `Rank 186` 的 survivor 唯一 follow-up，所以本轮 `cycle_plan` 必须先处理 `Rank 186`，再切到新的具体 fresh intake：`1633 -> 1555 -> Rank 96 reframe`。

## 1) 先读 policy + state 后的结论
- policy 默认顺序仍是：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。
- 当前 state 在改写前显示：
  - `Paper launch queue = Rank 183 / cbeth-eth-rolling-fair-basis-mr`
  - `Fresh intake slot = idle`
  - `Surviving candidate slot = Rank 186 / CME expiry postfix short BTC`，且 `followup_budget_remaining = 1`
  - `Active P2 slot = none`
- 前排对象无 rank 缺失：`Rank 183`、`Rank 186` 都已有正式 rank；无需补号。
- 因此本轮最高优先级不是继续围绕 `Rank 183` 伪造 handoff，也不是跳过 survivor 直接做新 intake，而是先把 `Rank 186` 那唯一一次 follow-up 做完并直接回答出口。

## 2) 最近 repo / optimization_loop / strategy_review 证据
### Repo 状态
- `git status --short` 仍主要是大量未跟踪 artifacts / reports / scripts。
- 这些只当最近工作 evidence，不得据此改 policy，也不得把 background pool 的旧候选自动拉回前排。

### 最近 `research/optimization_loop/`
1. `2026-03-26_1247_rank183_p3_handoff_ready.md`
   - `Rank 183` 已完成最小 `P3 handoff` 收口，当前是 queue 级对象，不再是开放式 admission。
2. `2026-03-26_1526_rank185_survivor_followup_park_to_background.md`
   - 上一条 survivor `Rank 185` 已诚实收口到背景池，前排 survivor 锁已释放。
3. `2026-03-26_1558_rank186_cme_expiry_postfix_short_intake_keep_p1.md`
   - 新一条 fresh intake 已首判为 `keep_P1`，并获得正式 `Rank 186`；当前 survivor 锁明确属于它。
4. `2026-03-26_1611_btc_book_eth_divergence_intake_park.md`
   - `0950` 已被首判 `park`，不能再占用 survivor follow-up。
5. `2026-03-26_1625_plain_pairs_intake_park.md`
   - `1505` 已被首判 `park`，当前 fresh intake 槽重新回到 idle。
6. `2026-03-26_1708_no_pending_cycle_point.md`
   - 说明上一轮排给 bot3 的 pending 小点已经跑完，当前确实需要 bot2 重新排一轮具体动作，而不是重复确认空槽。

### 最近 `research/strategy_review/`
- `2026-03-26_1523_strategy-review.md` 当时正确地把 `Rank 185` survivor follow-up 放在最前，然后再排 `1035 -> 0950 -> 1505`。
- 随后的运行态已经变化：
  - `Rank 185` 已于 `15:26 UTC` park；
  - `1035` 已于 `15:58 UTC` 升成 `Rank 186` survivor；
  - `0950` 与 `1505` 已于 `16:11 / 16:25 UTC` 先后首判 `park`。
- 所以当前排班必须承认：前排 survivor 锁现在属于 `Rank 186`，而新的 fresh intake 首位应切到尚未首判的最新对象，而不是回头重排已经处理过的 `0950 / 1505`。

## 3) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
- **是，非空。**
- 当前唯一对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`。
- 它已经处于 `handoff-ready`，这轮不需要再把它伪装成新的开放式研究。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 首位应是** `research/quant_digests/2026-03-26_1633_intraday-curve-shape-remainder-swing.md`。
- 理由：
  - `1035` 已不再是 fresh intake，而是 `Rank 186` survivor；
  - `0950` 与 `1505` 已先后首判 `park`；
  - 当前切回 fresh intake 时，最新且尚未首判的具体对象就是 `1633`，其后紧跟 `1555`；若预算仍有余，才补 `park_reframe/INDEX.md` 里的具体 candidate，例如 `Rank 96`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 是 `research/quant_digests/2026-03-26_1035_cme-expiry-postfix-short-bias.md`，已在 `2026-03-26_1558_rank186_cme_expiry_postfix_short_intake_keep_p1.md` 被正式首判为 `keep_P1` 并拿到 `Rank 186`。
- 当前 evidence 已经把对象收窄到非常具体的 exact-time raw alpha：`monthly CME expiry -> post 60~120m short BTC`；spot / perp 同向，且相对普通周五同钟窗口有约 `-36bp` 到 `-41bp` 的负漂移差值。
- 因为它已经进入 `keep_P1`，所以按 policy，它的那唯一一次 survivor follow-up 现在拥有前排锁定权，不得被新的 intake 覆盖。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- `Rank 183` 已经升入 `P3 / Paper launch queue`；`Rank 186` 仍停留在 survivor 槽等待唯一 follow-up；因此当前没有处于 admission 中、等待 `P3 / P1 / P0` 三选一的 `P2` 对象。

## 4) Rank / front-slot 合规检查
- `Paper launch queue`: `Rank 183`（已有正式 rank）
- `Surviving candidate slot`: `Rank 186`（已有正式 rank）
- `Active P2 slot`: none
- 当前前排对象没有无 rank 情况；无需补新的整数 `Rank`。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的改写
本轮只更新了 `BOT2_BOT3_STATE.md`，没有改 policy / brief / operating card / auto loop / cron prompt。

新的 `cycle_plan` 按 policy 默认顺序改写为：
1. `Rank 186 / CME expiry postfix short BTC` 的 survivor 唯一 follow-up（必须直接回答 `promote_P2` 或 `park_to_background`）
2. `2026-03-26_1633_intraday-curve-shape-remainder-swing.md`
3. `2026-03-26_1555_seesaw-negative-leadlag-alt-basket.md`
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`

这么排的原因是：
- `P3`: `Rank 183` 已 handoff-ready，没有新的最小接线动作；
- `P2`: 当前为空；
- `P1`: `Rank 186` 仍有合法且必须优先执行的唯一 follow-up；
- 只有把该 survivor 动作诚实排在首位后，剩余预算才可以继续补新的具体 fresh intake；
- 新的 fresh intake 先用最近两个尚未首判的新 digest（`1633`、`1555`），再用 `park_reframe/INDEX.md` 里最新、仍被明确标记为 `soft_reframe_candidate` 的 `Rank 96` 补足当前轮预算。

## 6) P3 / handoff 兜底检查
- 本轮不存在新的 `Active P2` 达到“desk review 已清楚表明够格进入 paper trade，但 bot3 尚未升级”的情形。
- `Rank 183` 的兜底升级责任此前已完成，运行态也已同步为 `P3 / handoff-ready`。
- 因此这轮不需要追加新的 `P2 -> P3` 改写；继续围着 `Rank 183` 打转会违反 policy 的收口逻辑。

## 7) 一句话结论
**当前 queue 仍非空，但真正占前排执行权的是 `Rank 186` 的 survivor 唯一 follow-up；只有把它先收口后，才轮到 `1633 -> 1555 -> Rank 96 reframe` 这三条新的具体 fresh intake。**
