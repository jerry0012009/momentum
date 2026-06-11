# Strategy Review (bot2)

Time: 2026-03-25 09:21 UTC

## 本轮一句话判断
当前前排为空：`Paper launch queue = none`、`Active P2 = none`、`Surviving candidate = none`；最新 fresh intake《Skylar oversold volume reversal transfer check》已直接 `park`，因此这轮没有任何可继续占主资源的 `P3/P2/P1` 动作，按 policy 应把主资源切回新的 fresh intake，不得自动把 background pool 旧候选拉回前排。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 继续要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 当前 runtime truth（本轮改写前）显示：
  - `Paper launch queue.current_target = none`
  - `Fresh intake slot.current_target = none`
  - `Surviving candidate slot.current_target = none`
  - `Active P2 slot.current_target = none`
  - `Background pool.do_not_auto_reopen = true`

### Repo 状态
- repo 仍有大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只是 evidence，不构成旧候选自动 reopen 的依据，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_0917_skylar-oversold-intake-park.md`
   - 最新 fresh intake《Skylar oversold volume reversal transfer check》已直接 `park`；核心结论是这条 `1h 急跌 + 异常放量后反弹` raw alpha 在当前 Binance perp/15m transfer 下默认版四个持有窗全部为负，只剩 `shock<=-5% & vol_ratio>=4` 的极端 capitulation pocket 有小样本正值线索。
2. `2026-03-25_0818_eth-netflow-intake-park.md`
   - 上一条 fresh intake《ETH exchange netflow intraday short alpha》也已直接 `park`；核心不是论文方向不清，而是当前首先需要交易所地址标签、链上归集与小时聚合等外部数据工程，不满足本轮 auto loop 的低摩擦诚实验证门槛。
3. `2026-03-25_0740_rank161-survivor-followup-drop-background.md`
   - `Rank 161 / EPCM microstructure taker alpha` 的唯一 survivor follow-up 已完成，并明确 `drop_to_background`：三币最优毛收益仅 `0.85~0.98 bps/event`，在保守 `2~6 bps round-trip` 下全部转负。
4. `2026-03-25_0727_rank161_epcm-microstructure-intake.md`
   - `Rank 161` 上一轮 fresh intake 曾合法形成 `keep_P1`，但唯一一次 follow-up 已用尽且失败，不能再占当前前排。

### 最近 `research/strategy_review/`
1. `2026-03-25_0817_strategy-review.md`
   - 上一轮正确把主资源切回 fresh intake，并把《ETH exchange netflow intraday short alpha》作为最新 fresh intake 来处理。
2. `2026-03-25_0732_strategy-review.md`
   - 更早一轮正确把主资源压在 `Rank 161` 的 survivor 唯一 follow-up 上，而不是继续并行扩 fresh intake。
3. 与上一轮相比，本轮新增的关键变化只有一条：
   - 最新 fresh intake《Skylar oversold volume reversal transfer check》也已完成 intake，并直接收口为 `park`，没有形成新的 survivor / P2 / P3 压力。
- 这意味着：上一轮之后，前排继续保持全空状态；本轮排班应继续恢复为 `fresh-intake-first`。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Rank 154 / Crypto-Stat-Arb` 已在 2026-03-24 完成 `refresh-only sidecar` offload，不再占默认前排轮次。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮最新 fresh intake 是《Skylar oversold volume reversal transfer check》。**
- 它已在 09:17 UTC 完成 intake，并被判为 `park`，没有进入 `keep_P1`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 这里的“上一条 fresh intake”即《Skylar oversold volume reversal transfer check》。
- 原因很具体：它已经在当前 Binance perp/15m transfer 下完成最小诚实快检，默认阈值 `ret_1h<=-2% & vol_ratio>=1.5` 的 `1h / 4h / 12h / 24h` 四档平均单笔净收益全部为负；剩下的只是 `shock<=-5% & vol_ratio>=4` 的极端 pocket 小样本线索。
- 这不符合 survivor 唯一 follow-up 应处理的“单一 decisive blocker”形态；当前正确动作是直接 `park`，而不是为一个已默认转负、仅剩小样本极端 pocket 的对象再占用唯一 follow-up 预算。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮没有 admission 对象需要回答离 `P3 / P1 / P0` 哪个出口最近；最近一个前排出口决断仍是 `Rank 161`，而它的出口已明确写成 `P0 / Background pool`。

## 3) Rank / front-slot 合规检查
- 当前前排对象里没有任何 `keep_P1 / P2 / P3` 但无正式 Rank 的非法对象。
- `Paper launch queue = none`、`Surviving candidate = none`、`Active P2 = none`。
- 最新 fresh intake《Skylar oversold volume reversal transfer check》已直接 `park`，因此不需要分配正式 Rank。
- 本轮无需补 rank。

## 4) 本轮 cycle_plan 重写依据
- `P3`：queue 为空，没有 handoff 动作。
- `P2`：没有 active P2，因此没有 admission / promote / park 决策轮。
- `P1`：没有 survivor；最新 fresh intake 已直接 `park`，不值得那唯一一次 follow-up。
- 因此本轮默认顺序应改成：
  1. 直接做新的 fresh intake；
  2. 若该 intake 得到 `keep_P1`，立即把它写成新的唯一 survivor；
  3. 仅当新的 survivor 成立时，执行那唯一一次 decisive follow-up；
  4. 若该 survivor 又被直接收口为 `drop_to_background` 且前排仍空，再补 1 条 conditional fresh intake。
- 本轮不需要把 `Background pool guard` 单独写成 pending 小点，因为没有自动 reopen / 槽位污染，也没有新的 `P3 handoff` 切换需要审计。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`，且只改 runtime truth：
- 保留 `Paper launch queue = none`
- 保留 `Fresh intake slot` 为最新 intake 已 `park` 后的 `vacant / none`
- 保留 `Surviving candidate slot = none`
- 保留 `Active P2 slot = none`
- 保留 `Background pool.latest_parked = 《Skylar oversold volume reversal transfer check》`
- 将 `cycle_plan` 重写为新的 4 项 `pending`：
  1. 新的 fresh intake
  2. 仅当第 1 项得到 `keep_P1` 时，写成 survivor
  3. 仅当第 2 项形成 survivor 时，执行唯一 follow-up
  4. 仅当第 3 项把新 survivor 直接 drop 且前排仍空时，再补 1 条 conditional fresh intake

所有新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
**这轮已经没有资格继续占主资源的 `P3/P2/P1` 对象；最诚实的排班是回到新的 fresh intake，而不是围着已 drop 的 `Rank 161`、已 `park` 的 ETH netflow，或刚刚 `park` 的 Skylar oversold 再续写。**
