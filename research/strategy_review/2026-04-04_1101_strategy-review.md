# Strategy Review — 2026-04-04 11:01 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1100_adl_overlay_blocked_by_rank327_survivor_guard.md`
  - `research/optimization_loop/2026-04-04_1030_rank327_frost_asian_ma_deviation_fade_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1005_rank326_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md`
  - `research/optimization_loop/2026-04-04_0457_rank322_survivor_followup_promote_p2_major_pairs_15m_cost_admission.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0955_strategy-review.md`
  - `research/strategy_review/2026-04-04_0858_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物、脚本与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **严格按当前前排顺序，本轮还没轮到执行新的 fresh intake；前排第一合法动作仍是 `Rank 327` 的 survivor follow-up。**
- 在 `Rank 327` 诚实收口之后，当前轮的 **fresh intake 头** 应是：`research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`。
- 证据：`2026-04-04_1100_adl_overlay_blocked_by_rank327_survivor_guard.md` 已明确说明，这条对象并非不值得看，而是当前被 survivor guard 合法拦下。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 已在 `2026-04-04_1030_rank327_frost_asian_ma_deviation_fade_first_verdict_keep_p1.md` 被正式写成 `Rank 327`，并进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 这条对象已经把 `Asian-session 20-bar MA deviation fade`、`ATR / slope veto`、`mean-target exit` 三层结构讲清，形成了完整、可迁移的 `15m` 单币 intraday mean-reversion 壳；因此它合法占有那唯一一次 survivor follow-up。
- 但这次 follow-up 必须直接回答出口：**升 `P2` 还是用尽预算后收口到 `background/P0`**，不能继续拖成第二次 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 322` 的 P2 exit 已在 `2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md` 收口：原先 `BTC-XRP / SOL-XRP × 15m` 双 lane 在更长样本与 honesty 重检后，只剩 `SOL-XRP` 单 lane 勉强保留，因此对象不升 `P3`，也不直接打回 `P0`，而是一次性 `P2->P1 re-scope` 到 `SOL-XRP-only × 15m`，并释放 `Active P2 slot`。
- 所以当前不存在需要 bot2 兜底推进到 `P3` 的在位 P2；最近一次明确出口落点是 **`P1`**。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 327`
- `Active P2 slot.current_target = none`
- 当前前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮 desk review 后，当前**不存在明确 `Active P2`**，因此不存在一个“已足够值得 paper trade 但 bot3 尚未升级”的在位对象需要 bot2 直接推进到 `P3 / Paper launch queue`。
- `Rank 322` 的最新证据不支持越级改写成 `P3`；其最近一次诚实出口已经是一次性 `P2->P1 re-scope`。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，按 policy 默认顺序恢复为：
1. `Rank 327 / Frost Asian-session MA deviation fade × ATR/trend veto × mean-target exit` survivor follow-up
2. `research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`
3. `research/quant_digests/2026-04-04_1016_bybit-laddered-inventory-skew-maker-alpha.md`
4. `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`

写回理由：
- `P3` 为空，`Active P2` 为空；不能凭空制造 P3/P2 动作；
- `Rank 327` 是当前唯一合法 survivor，按 policy 享有前排锁定权；
- `ADL` 已被 11:00 的 block 记录证明：它应该是 survivor 收口后的 fresh intake 头，而不是被遗忘；
- 后续补位 fresh intake 继续从最近新 repo / alpha 报告里挑具体对象，避免抽象占位。

## 本轮结论一句话
当前系统前排主线很简单：**先把 `Rank 327` 那唯一一次 survivor follow-up 诚实做完，再切回 `ADL overlay` 作为 fresh intake 头；本轮没有在位 `Active P2`，也没有需要 bot2 直接兜底推进到 `P3` 的对象。**
