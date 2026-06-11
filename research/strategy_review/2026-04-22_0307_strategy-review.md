# 2026-04-22 03:07 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（共享工作区仍有大量历史未跟踪文件；本轮严格只更新 `docs/BOT2_BOT3_STATE.md` 与本日志）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-22_0214_rank62b_conditional_survivor_blocked.md`
  - `research/optimization_loop/2026-04-22_0126_rank62b_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-22_0059_spotperp_basisfade_conditional_survivor_prewrite_blocked.md`
  - `research/optimization_loop/2026-04-22_0046_rank60_conditional_freshintake_blocked_absorbed_by_rank378.md`
  - `research/optimization_loop/2026-04-22_0025_spotperp_basisfade_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-22_0100_strategy-review.md`
  - `research/strategy_review/2026-04-22_0019_strategy-review.md`
  - `research/strategy_review/2026-04-21_2337_strategy-review.md`
- Current / next intake source evidence:
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`
  - `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`
  - `research/park_reframe/INDEX.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 否。
- `current_target = none`；`Rank 431` 已完成 `P3 launch wiring` 并落入 `connected_runner_live`，当前 queue 没有待接线对象。

2. 本轮 `fresh intake` 是什么？
- 本轮 `fresh intake` 切到 `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`。
- 原因：上一轮前排的 `Rank 62b` 已在 `2026-04-22_0126_rank62b_freshintake_background_p0.md` 里完成 first verdict 并直接收口 `background/P0`，其 conditional survivor 又在 `2026-04-22_0214_rank62b_conditional_survivor_blocked.md` 被明确阻断；当前 `P3 / Active P2 / survivor` 全空，按 policy 应继续切回新的具体 fresh intake。现有最明确、仍未被 runtime 消费的具体对象，是 `Rank 96 / short-side second-touch + candle-quality admission delay` 这条 `soft_reframe_candidate`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `Rank 62b / 前 2~3 根 bar fail-fast 检查后 handoff 到 slow exit`。
- 它已被 first verdict 直接判回 `background/P0`，决定性理由已经闭合：改善主要停留在单一 `SOL` pocket，`ema_psar_long` 的原 quick-failure edge 反而丢失，`breakout_short` 也未修复；所以它不值得 survivor 的唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 431` 已完成 `P2 -> P3 -> connected_runner_live`，当前没有需要 bot2 兜底直接推入 `P3 / Paper launch queue` 的对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排没有 `keep_P1 / P2 / P3` 但缺正式 `Rank` 的对象。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- 本轮未发现仍停留在 `Active P2`、但已足够值得进入 paper trade / paper launch 的对象。
- 因此无需把任何对象直接改写进 `P3 / Paper launch queue` 或 handoff 路径。

## State rewrite
已按 policy 改写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.current_target` 切到 `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
- `Fresh intake slot.source_record` 同步切到 `Rank 96` park-reframe
- `Fresh intake slot.latest_result` 保留刚刚完成的 `Rank 62b -> background/P0` first verdict
- `Fresh intake slot.latest_result_record` 维持 `research/optimization_loop/2026-04-22_0126_rank62b_freshintake_background_p0.md`
- `Fresh intake slot.latest_blocked_record` 更新为 `research/optimization_loop/2026-04-22_0214_rank62b_conditional_survivor_blocked.md`
- `Paper launch queue / Surviving candidate slot / Active P2 slot` 保持无新对象
- `cycle_plan` 重写为当前轮 4 条具体 pending：
  1. `Rank 96` fresh intake first verdict：只回答 `short-side second-touch + candle-quality admission delay` 是否真有区别于既有 failure / second-chance family 的独立新增价值，而不是靠极端砍样本把旧 shared retest gate 换壳重讲。
  2. `Rank 96` conditional survivor prewrite：仅当第 1 项形成 `keep_P1` 时，预写唯一 blocker，避免 bot3 把它扩成泛化结构研究。
  3. `Rank 89` conditional fresh intake：仅当 `Rank 96` 未形成 survivor/P2 时，再回答 `back-inside bar anchored failure-followthrough setup` 是否值得从旧 shared allow-gate 残余里独立出来。
  4. `Rank 89` conditional survivor prewrite：仅当第 3 项形成 `keep_P1` 时，预写唯一 blocker，避免扩成多 horizon / 多 setup 的抽象 failure 研究。

## 本轮结论
- 当前没有待接线 P3，没有 survivor，也没有 Active P2；因此这一轮必须老老实实继续 fresh intake，而不是围着已经收口的 `Rank 62b` 或旧 blocked conditional 打转。
- `Rank 96` 是当前最合理的前排对象：它的残余只剩一条非常窄的 `short-side delayed admission` 线索，适合做一次便宜且诚实的 first verdict。
- 若 `Rank 96` 也不成立，下一条最像“还值得具体回答一次”的对象是 `Rank 89 / back-inside failure-followthrough`，而不是再把背景池旧对象泛化拉回前排。

## Tail step status
- homepage publish：待本日志写完后按独立命令执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入或 preflight 拒绝失败，记为非阻断尾部失败，不回滚本轮 state/log。
- email notify：待 publish 之后按独立命令执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排切到Rank96并预备Rank89" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-22_0307_strategy-review.md`；若失败，只记为尾部通知失败，不回滚本轮 state/log。
