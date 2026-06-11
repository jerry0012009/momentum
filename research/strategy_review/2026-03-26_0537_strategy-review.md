# Strategy Review (bot2)

Time: 2026-03-26 05:37 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；当前前排已切换为 `Active P2 = Rank 178 / cross-chain-attention-spread-alpha` 与 `Surviving candidate = Rank 179 / basis-xs-cheap-vs-rich-alpha`，因此本轮默认排班必须先处理 `Rank 178` 的 P2 admission / 出口决策，再处理 `Rank 179` 的唯一 survivor follow-up，之后才轮到新的 fresh intake；现有 desk review 证据还不足以触发 bot2 对 `Rank 178` 的 `P2 -> P3` 兜底直推。

## 1) 先读 policy + state 后的结论
- 默认排班顺序仍是：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。
- 当前 `Paper launch queue = none`，不存在已明确达到 paper launch 门槛却被 bot3 漏升的对象，因此 bot2 的 `P2 -> P3` 兜底升级条件本轮**未触发**。
- 当前 `Surviving candidate slot = Rank 179 / basis-xs-cheap-vs-rich-alpha`，`followup_budget_remaining = 1`；按 policy，这个 survivor follow-up 在诚实收口前享有前排锁定权，不能被新的 `keep_P1` 候选覆盖。
- 当前 `Active P2 slot = Rank 178 / cross-chain-attention-spread-alpha`，所以这轮前排第一优先动作已从 survivor 收口切换为 **P2 admission / 出口决策**。
- 前排对象不存在无 rank 情况：`Rank 178`、`Rank 179` 均已有正式 rank，无需补发新的整数 `Rank`。

## 2) 最近 repo / optimization_loop / strategy_review 证据
### Repo 状态
- `git status --short` 仍主要是大量未跟踪 artifacts / reports / scripts。
- 这些只作为最近工作的 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。

### 最近 `research/optimization_loop/`
1. `2026-03-26_0505_rank178_survivor_followup_promote_p2.md`
   - `Rank 178 / cross-chain-attention-spread-alpha` 已从 survivor 升到 `Active P2`。
   - 当前被保留并推进到 P2 的明确对象是：`leader-chain attention shock -> long leader / short equal-weight rival basket` 这条 **5-leg cross-chain relative-value spread baseline**。
   - 关键信号：intake artifact 的强 shock 事件里，平均 spread 约 `+87.01 bps`，扣 `30 bps` 后仍约 `+57.01 bps`；BTC 平静窗口里平均 spread 仍约 `+75.97 bps`。
   - 但同步 replay 版 full 1v4 只剩约 `+9.21 bps`、compressed 3-leg 约 `+10.58 bps`，说明当前最大 blocker 是 **spec lock / replay reconciliation / execution realism**，而不是原始骨架已被证伪。
   - 这份 evidence 还不足以让 bot2 直接兜底升 `P3`：因为 P2 admission 的关键 honesty gap 仍未收口，尤其 `3-leg compression` 不能当成已成立事实。
2. `2026-03-26_0513_rank179_basis_xs_cheap_vs_rich_intake_keep_p1.md`
   - `Rank 179 / basis-xs-cheap-vs-rich-alpha` 已完成 fresh intake 首判并进入 survivor。
   - 当前被保留的明确对象是：`long cheap basis / short rich basis` 这条横截面 basis carry / relative-value 骨架。
   - 本地快检在 Binance perp `premiumIndex` proxy 上给出同号结果：`16-bar signal + 32-bar hold` 的 non-overlap gross 约 `+14.36 bps/trade`，胜率约 `60.9%`。
   - 但证据仍主要停留在 `perp premium proxy`、短样本和粗成本口径，因此它**值得那唯一一次 follow-up**，但还不够直接升 `P2`。
3. `2026-03-26_0401_rank177_survivor_followup_park_to_background.md`
   - `Rank 177` 已诚实收口并退回 background，不再占前排。

### 最近 `research/strategy_review/`
- `2026-03-26_0436_strategy-review.md` 的判断当时仍然正确：那一轮先处理 `Rank 178` 的 survivor follow-up，再切到 basis cheap-vs-rich intake。
- 随后 bot3 已经把这两步都跑完，所以系统认知的关键变化是：
  - `Rank 178` 不再是 survivor，而是明确 `Active P2`；
  - `Rank 179` 成为当前唯一 survivor。
- 这意味着当前 `cycle_plan` 必须按 policy **前移 P2 admission**，不能继续把新 intake 放在最前。

## 3) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
- **否，当前仍为空。**

### Q2. 本轮 `fresh intake` 是什么？
- **当前前排收口之后的下一条 `fresh intake` 是** `research/quant_digests/2026-03-26_0342_cointegrated-basket-ou-hysteresis.md`。
- 因为 `basis cheap-vs-rich` 已经不再是 fresh intake，而已进入 survivor；在它之后，按当前候选顺序应轮到 `cointegrated basket OU`，再之后才是 `HTF BB-RSI exhaustion fade`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 是 `Rank 179 / basis-xs-cheap-vs-rich-alpha`。
- 首判 `keep_P1` 是诚实的，因为它保留的是明确且独立的 basis alpha 本体：`long cheap basis / short rich basis`。
- 但它还没有强到可直接升 `P2`：当前仍缺更诚实 basis 口径、非重叠持有、保守组合成本与 neutralization 后净边的 decisive 收口，所以这唯一一次 follow-up 应该被用掉，并且必须直接回答 `promote_P2` 还是 `park_to_background`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。当前明确 `Active P2 = Rank 178 / cross-chain-attention-spread-alpha`。**
- 就现有 desk review 证据看，它**离 `P3` 最近，但还没近到 bot2 可以直接兜底推进**。
- 原因不是原始骨架太弱，而是 admission 的主 blocker 已经非常聚焦：`5-leg baseline` 的 spec lock / replay reconciliation / honesty realism 还没收口；若这一步能解释 artifact 与 replay 的大幅口径差异且保住厚净边，它就最接近 `P3`，否则更可能落到 `one-time P2->P1 re-scope` 或 `drop_to_background`。

## 4) Rank / front-slot 合规检查
- `Paper launch queue = none`
- `Active P2 slot = Rank 178`
- `Surviving candidate slot = Rank 179`
- 所有前排对象均已有正式 rank；本轮无需补 rank。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的改写
本轮只更新了 `BOT2_BOT3_STATE.md` 的 `cycle_plan`，没有改 policy / brief / operating card / auto loop / cron prompt。

新的 `cycle_plan` 按 policy 默认顺序重写为：
1. **`Rank 178` 的 P2 admission / 出口决策轮**
   - 直接围绕 `effectiveness / cross-asset / time / parameter / honesty` 五项里的 admission 主问题收口：
   - 先把 `5-leg leader-vs-rival attention spread baseline` 的 `spec lock / replay reconciliation` 做诚实收口；
   - 再回答它应当 `promote_P3`、`keep_P2`、`one-time P2->P1 re-scope` 还是 `drop_to_background`。
2. **`Rank 179` 的 survivor follow-up**
   - 用掉唯一一次 follow-up，直接回答 `long cheap basis / short rich basis` 在更诚实 basis 口径、非重叠持有与保守组合成本下，是否足以升 `P2`，否则就退回 background。
3. **`cointegrated basket OU` fresh intake**
   - 仅当前排 `P2 / P1` 都已诚实收口时执行。
4. **`HTF BB-RSI exhaustion fade` fresh intake**
   - 仅当上述链条都已诚实收口且预算仍有余时执行。

所有新 cycle items 均为：`result = none`、`status = pending`。

## 6) 一句话结论
**这轮没有任何需要 bot2 兜底硬推 `P3` 的对象；正确动作是承认前排已切换为 `Rank 178` 的 P2 admission + `Rank 179` 的 survivor follow-up，先把这两条前排链条诚实收口，再切回新的 fresh intake。**
