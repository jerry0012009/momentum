# 2026-03-31 09:55 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排；只读取 runtime state、repo 状态、最近 `research/optimization_loop/` 与最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 仍写明 `Paper launch queue.current_target: none`；当前只有 `Rank 200 / 201 / 213 / 229` 在 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮最近一条已正式写回 runtime 的 fresh intake 仍是 **`Rank 267 / crypto factor momentum × size/vol rotation`**。
   - 证据：`research/optimization_loop/2026-03-31_0919_rank267_crypto_factor_momentum_sizevol_rotation_intake_keep_p1.md` 完成首判，随后 `2026-03-31_0946_rank267_survivor_followup_promote_p2.md` 用掉 survivor follow-up 并把它升入 `Active P2`；因此“本轮 fresh intake 是什么”仍应回答 Rank 267，而不是把尚未正式 intake 的别的 digest 硬写成当前 intake。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且已经值得完。**
   - 证据：`Rank 267` 的唯一 survivor follow-up 已执行完成；在 Binance perp 当前高流动 universe、4h 换仓、单边 10bps 成本下，`short-horizon momentum` 与 `size` sleeves 已给出成本后净边，`low-vol` 未见 fatal flaw，`winner rotation` 最佳组合约 `+174.82 bps/period`，因此不是“follow-up 后仍停 P1”，而是已经诚实收口成 `promote_P2`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**存在。当前明确 `Active P2` 是 `Rank 267`，它离的最近出口是 `P3`。**
   - 证据：`research/optimization_loop/2026-03-31_0946_rank267_survivor_followup_promote_p2.md` 已把对象升入 `P2`；从现有证据看，当前缺口不再是“它是不是只有 paper story”，而是 `cross-asset / time / parameter / honesty` 这四类 admission blocker 是否能补齐。换句话说，它目前更像“偏 promote_P3 的 admission 链”，而不是接近 `P1` re-scope 或 `P0` drop。

## rank / 前排合法性检查

- `Paper launch queue`: `none`
- `Fresh intake slot`: `Rank 267`，已有正式 rank
- `Surviving candidate slot`: `none`
- `Active P2 slot`: `Rank 267`，已有正式 rank
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short` 显示大量未跟踪产物；本轮只把它视为 repo 活动背景，不据此改 policy 或拉旧对象回前排。
- 最近 optimization 里最关键的三条证据：
  - `2026-03-31_0919_rank267_crypto_factor_momentum_sizevol_rotation_intake_keep_p1.md`
  - `2026-03-31_0946_rank267_survivor_followup_promote_p2.md`
  - `2026-03-31_0910_rank266_survivor_followup_background_p0_majors_sparse_breach_fail.md`
- 最近 strategy review 最新文件是 `2026-03-31_0828_strategy-review.md`；其中当时前排还是 `Rank 266` survivor。现在 runtime 已前进到 `Rank 267` Active P2，所以本轮必须重写 state 与 `cycle_plan`，不能继续沿用旧 survivor 排班。

## 为什么本轮不直接把 Rank 267 兜底推到 P3

policy 允许 bot2 在“已经足够值得进入 paper trade / paper launch”时直接兜底推进 `P3`。本轮我专门检查了这一点：

- **偏向 P3 的证据已经存在：** 静态 `momentum + size` sleeves 有成本后净边，rotation 也不是装饰；因此它确实不是弱 P2。
- **但还没到 desk review 可以直接越过 admission 剩余 blocker 的程度：** 目前仍缺 `cross-asset / time / parameter / honesty` 的最小 decisive write-up，尤其需要确认收益不是少数币 pocket、不是单一近期窗口、不是孤点参数、也不是被 universe / neutrality / turnover 假设放大。

所以本轮结论是：**不应拖回开放研究，更不应回 P1；但也暂不由 bot2 直接写入 `P3 / Paper launch queue`。** 最诚实的排法是把 `Rank 267` 当前轮完整压到偏 `promote_P3` 的 admission 链最前面。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：有，而且唯一合法对象就是 `Rank 267`
3. `P1 survivor`：无
4. `fresh intake`：只能排在 `Rank 267` admission 链之后

因此本轮把 `cycle_plan` 重写为：
1. `Rank 267`：`cross-asset stability`
2. `Rank 267`：`time stability`
3. `Rank 267`：`parameter + honesty` 合并 admission，并直接准备出口决策
4. `anchor-low reversal gate`：作为唯一具体 fresh intake 补位

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 把 `Fresh intake slot` 与当前 runtime 进度对齐
  - 明确 `Active P2 = Rank 267`，并写清它当前最近出口是 `P3`
  - 把旧的已完成项从当前轮 `cycle_plan` 移除，重写为 4 个具体 `pending` 小点
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮未触发 bot2 的 `P2 -> P3` 兜底直推，因为 admission 还差最小但关键的 blocker 审计
