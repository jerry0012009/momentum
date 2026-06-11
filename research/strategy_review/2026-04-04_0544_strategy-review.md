# Strategy Review — 2026-04-04 05:44 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0457_rank322_survivor_followup_promote_p2_major_pairs_15m_cost_admission.md`
  - `research/optimization_loop/2026-04-04_0510_rank324_volume_router_dualbook_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0539_obi_microprice_pairs_first_verdict_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0437_strategy-review.md`
- 本轮可用 fresh-intake 候选 digest：
  - `research/quant_digests/2026-04-04_0527_xsm-goldilocks-btcvol-scaling-alpha.md`
  - `research/quant_digests/2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- 当前前排仍有真实动作：
  - `Active P2 = Rank 322`
  - `Surviving candidate = Rank 324`
- 因此新的 fresh intake 不能越过前排收口；只能老实排在其后。
- 结合最近新 digest，**本轮 fresh intake 头**应改为：
  - `research/quant_digests/2026-04-04_0527_xsm-goldilocks-btcvol-scaling-alpha.md`
- 若预算仍有余，补位顺序为：
  - `research/quant_digests/2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在必须先做。**
- 上一条 fresh intake 是 `Rank 324 / vol-z router × TSMOM / XS reversal dual-book`。
- 05:10 UTC 的 first verdict 已明确写成 `keep_P1`：该对象不是把 volume confirmation 换壳重讲，而是把 `TSMOM continuation`、`XS reversal` 与 `volume regime router` 三层拆开的 dual-book raw alpha 壳。
- 按 policy，survivor 只能是上一条 fresh intake，且只允许 **1 次** decisive follow-up；在这一次诚实收口之前，不能让别的新 `keep_P1` 覆盖 survivor 槽位。
- 因此本轮必须直接回答：在 `15m` 优先、`4/8/12 bps` 成本阶梯下，`vol-z router` 是否真的能在 `continuation / reversal` 之间留下至少一条诚实、可迁移的 short-cycle lane；有则 `promote_P2`，没有则收口到 `background/P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。**
- 当前明确 `Active P2 = Rank 322 / cointegrated spread z-score × stop-loss/time-exit`。
- 从 04:57 UTC 的最新证据看，它已经不只是 pairs 教材壳，而是锁定了 `BTC-XRP / SOL-XRP × 15m` 这条经过 `pair-quality / half-life / 2/4/8 bps cost ladder / horizon narrowing` 后仍保留正净边的诚实 lane。
- 目前看，**它离 `P3` 最近**，不是离 `P1` 或 `P0` 最近：
  - 没有看到唯一明确的 re-scope 需求，因此不满足默认 `P2->P1` 条件；
  - 也没有看到明显 fatal flaw，暂不该先写 `P0`；
  - 下一步正确问题是：更长样本、更真实 execution/honesty 口径后，这条 lane 是否已经足够值得 paper trade。若答案是肯定，bot2 作为兜底裁判必须直接把它推进 `P3 / Paper launch queue`，不能继续拖成开放式研究。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = Rank 324 / vol-z router × TSMOM / XS reversal dual-book`
- `Active P2 slot.current_target = Rank 322 / cointegrated spread z-score × stop-loss/time-exit`
- 当前所有前排对象均已有正式 `Rank`；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 当前存在明确 `Active P2 = Rank 322`，且最新 desk evidence 指向的默认近端出口是 `P3`，不是 `P1/P0`。
- 但截至本轮 review，证据仍停在 survivor-follow-up 刚升 `P2` 的阶段；尚未看到 bot3 已完成覆盖 `effectiveness / time stability / parameter stability / honesty` 的 admission 收口页，因此**现在还不能越证据直接写入 `P3`**。
- 相应地，本轮正确动作不是继续泛化研究，而是把 `Rank 322` 明确排成 **出口导向 admission 轮**：要么补足证据后直接 `promote_P3`，要么发现唯一明确 re-scope / fatal flaw 后转向 `P1/P0`。不得让它在 `keep_P2` 上空转。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：有且只有一个明确 `Active P2` —— `Rank 322`
3. `P1`：有且只有一个 survivor —— `Rank 324`
4. `fresh intake`：只有在前两类动作已诚实排入后，才能补新的具体对象

因此本轮将 `cycle_plan` 重写为 4 项：
1. `Rank 322`：做 P2 admission 收口轮，直接回答更长样本、更真实 cost/execution 后是否已够格 `promote_P3`
2. `Rank 324`：做唯一一次 survivor follow-up，结论只能是 `promote_P2` 或 `background/P0`
3. `2026-04-04_0527_xsm-goldilocks-btcvol-scaling-alpha.md`：作为当前轮 fresh intake 头
4. `2026-04-04_0448_mfi-overbought-firstred-fade-alpha.md`：作为补位 fresh intake

改写理由：
- 当前存在合法 `P2` 与 `P1` 前排动作，收口优先级必须高于新的发现；
- `Rank 324` 仍持有 survivor 锁定权，不能被新的 `keep_P1` 覆盖；
- 最新 05:27 / 04:48 digest 都比更早的 00:20 digest 更新、更适合作为当前轮 intake 来源；
- `Rank 322` 既然已进入 `Active P2`，就必须按 policy 优先回答 admission 出口，不能继续拿新的 pairs 补件替代本体决策。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮只改写 runtime state；未改动 policy / brief / operating card / auto loop / cron prompt。

## 发布与通知
- 中文邮件摘要已发送成功。
- 首页刷新脚本 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 在本 cron 运行态下卡在 `sudo` 步骤；随后尝试以提升权限重跑，但当前 runtime 不提供 `elevated`，因此**首页发布本轮未完成**。这不影响 `BOT2_BOT3_STATE.md` 与 review 日志已落库，但公网首页可能暂未同步到最新 review。
