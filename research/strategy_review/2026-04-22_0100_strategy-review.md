# 2026-04-22 01:00 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（存在大量历史未跟踪文件；本轮按约束仅更新 `BOT2_BOT3_STATE.md` 与本日志）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-22_0059_spotperp_basisfade_conditional_survivor_prewrite_blocked.md`
  - `research/optimization_loop/2026-04-22_0046_rank60_conditional_freshintake_blocked_absorbed_by_rank378.md`
  - `research/optimization_loop/2026-04-22_0025_spotperp_basisfade_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-22_0011_postevent_volcrush_straddle_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-22_0019_strategy-review.md`
  - `research/strategy_review/2026-04-21_2337_strategy-review.md`
  - `research/strategy_review/2026-04-21_2254_strategy-review.md`
- Current / recent intake sources checked:
  - `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/quant_digests/2026-04-21_2359_spotperp-delta-neutral-basisfade-alpha.md`
  - `research/park_reframe/INDEX.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 否。
- `current_target = none`；`Rank 431` 已完成 dedicated runner + scheduler + first verified run，并已写入 `connected_runner_live`，当前没有待接线对象。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 改为 `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`。
- 理由：最近最新的 queue-facing 新 digest（`2332 intraday mom/reversal regime switch`、`2310 post-event vol crush straddle re-expansion`、`2359 spot↔perp basis fade`）都已在 optimization log 中完成 first verdict 并直接收口 `background/P0`；原 fallback `Rank 60` 也已在 `2026-04-22_0046_rank60_conditional_freshintake_blocked_absorbed_by_rank378.md` 被明确判定为 stale residue、不能再占前排。当前 `P3 / Active P2 / survivor` 全空时，按 policy 应切到仍未被 runtime 消费、且具备明确单轴改写的 park-reframe 候选；最新仍像“活的具体对象”的是 `Rank 62b / fail-fast only in first 2~3 bars, then handoff to slow exit`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-21_2359_spotperp-delta-neutral-basisfade-alpha.md`，已在 `research/optimization_loop/2026-04-22_0025_spotperp_basisfade_freshintake_background_p0.md` 直接收口 `background/P0`。
- 决定性理由已经闭合：这条线只证明了稳定但极薄的 gross basis 回归（约 `1.8~2.1bps/笔`），没有证明存在至少两个非单一币 / 单一窗、能跨过现实四腿摩擦的 after-cost pocket，不值得占用 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 431` 已完成 `P2 -> P3 -> connected_runner_live`；当前没有需要 bot2 兜底裁判、直接改写进 `P3 / Paper launch queue` 的对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前没有达到 `keep_P1 / P2 / P3` 但仍无正式 `Rank` 的前排对象。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- 本轮未发现仍停留在 `Active P2`、但 desk review 已足够支持直接进入 paper trade / paper launch 的对象。
- 因此无需把任何对象直接改写进 `P3 / Paper launch queue`。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.current_target` 切到 `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`
- `Fresh intake slot.source_record` 同步切到该 park-reframe 记录
- `Fresh intake slot.latest_blocked_record` 更新为 `research/optimization_loop/2026-04-22_0046_rank60_conditional_freshintake_blocked_absorbed_by_rank378.md`
- `Paper launch queue` 保持 `none`
- `Surviving candidate slot` 保持 `none`
- `Active P2 slot` 保持 `none`
- `cycle_plan` 重写为 4 条具体 pending：
  1. `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`：当前 fresh intake，先回答 `Rank 62b` 的两段式 exit clock 是否真能修复原 Rank 62 的 `winner truncation`，而不是靠更慢退出拖出纸面改善。
  2. `research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`：仅作为第 1 项若得到 `keep_P1` 时的唯一 survivor blocker 预写，避免 bot3 把它扩成泛化 exit-framework 研究。
  3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`：conditional fresh intake，只在第 1 项未形成 survivor/P2 时执行；只把 `short-side second-touch + candle-quality admission delay` 当作新窄 hypothesis 处理，不把原 shared retest gate 自动拉回前排。
  4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`：仅作为第 3 项若得到 `keep_P1` 时的唯一 survivor blocker 预写，避免 bot3 把它扩成泛泛的 second-chance / failure 研究。

## 本轮结论
- 当前没有待接线 P3、没有 survivor、没有 Active P2；因此本轮预算应继续诚实切回 fresh intake。
- 但最近两轮已经证明：`spot-perp basis` 与 `Rank 60` 都不是还活着的前排对象；继续围着它们写 conditional，只会让 bot3 对着死前置条件打转。
- 因此本轮应把前排切到两个**仍未被 runtime 消费、且具有单轴定义的具体 park-reframe 对象**：
  - 第一优先：`Rank 62b / 前 2~3 根 bar fail-fast + 存活后 handoff 到 slow exit`
  - 第二优先：`Rank 96 / short-side second-touch + candle-quality admission delay`
- 其中 `Rank 62b` 比 `Rank 96` 更优先，因为它的 blocker 更清楚、trade-off 更单轴、且尚未被既有 live family 明确吸收。

## Tail step status
- homepage publish：已按独立命令执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；进程长时间无输出，最终手动终止并记为**非阻断尾部失败**，不回滚本轮 review / state / log
- email notify：已按独立命令成功执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排切到Rank62b与Rank96窄假设" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-22_0100_strategy-review.md`
