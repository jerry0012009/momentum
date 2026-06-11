# 2026-04-19 00:43 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization loop:
  - `2026-04-19_0040_rank423_liqshock_oiunwind_freshintake_keep_p1_symbol_cost_bucket.md`
  - `2026-04-18_2358_rank422_p2_exit_promote_p3_scheduler_realism.md`
  - `2026-04-18_2348_rank422_p2_timeseg_crossasset_keep_p2.md`
  - `2026-04-18_2254_rank422_survivor_followup_promote_p2_basket_childentry.md`
  - `2026-04-18_2205_rank422_us_session_twowindow_drift_freshintake_keep_p1.md`
- Recent strategy review:
  - `2026-04-18_2334_strategy-review.md`
  - `2026-04-18_2210_strategy-review.md`
  - `2026-04-18_2032_strategy-review.md`
- Fresh materials checked for rewrite:
  - `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`
  - `research/quant_digests/2026-04-18_2238_liqshock-oiunwind-exhaustionfade-alpha.md`
  - `research/quant_digests/2026-04-18_1932_option-box-financing-dislocation-alpha.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**是。**
   - `current_target = Rank 422 / 21:00–23:00 UTC fixed-window drift`，而且它还没有进入 `connected_runner_live`，按 policy 仍属于必须优先完成的 `P3 launch wiring`。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`。**
   - 它刚完成 fresh intake 最小首判，并以 `keep_P1` 留在前排；当前运行态里它同时占据 fresh slot 与 survivor slot，符合“survivor 只能是上一条 fresh intake”的约束。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得。**
   - `Rank 423` 在 `BTC/ETH/SOL/XRP/ADA` 这组 symbol 上保留清楚的 after-cost pocket（组合约 `gross≈+22.74bps/event`、`net8≈+14.74bps/event`），而且唯一剩余 blocker 已明确收敛为 `entry realism / delay`，这正是 policy 允许的那一次便宜诚实 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在明确 `Active P2`。**
   - `Rank 422` 已不再是 `P2`，因为最近 desk review 与优化日志都已诚实回答：它足够值得进入 paper trade / paper launch，应该直接按 `P3 / Paper launch queue` 处理，而不是继续挂在 `P2`。

## Rank 合规检查
- `Paper launch queue = Rank 422`
- `Fresh intake slot = Rank 423`
- `Surviving candidate slot = Rank 423`
- `Active P2 = none`
- 当前前排对象都带正式 `Rank`，本轮无需补号。

## 排班判断
- 当前优先级最高的真实动作不是新的研究，而是 **`Rank 422` 的 P3 launch wiring**。
- policy 已写明：只要 queue 里的对象还没有 dedicated runner / scheduler / first verified run，就不能把它当作“已收口的 P3”。
- 因此，本轮前两项必须都给 `Rank 422` 的接线动作：
  1. runner / handoff artifact 落库；
  2. scheduler + first verified run + runtime state rewrite。
- 在 `P3` 前排动作之后，下一优先级是 `Rank 423` 的 survivor 唯一 follow-up。它已经有清楚 pocket，且剩余 blocker 单一，不应被新的 intake 覆盖。
- 只有在 `P3` 与 survivor 都被诚实排进前部后，才轮到新的 fresh intake。按最近材料质量，本轮把 `2026-04-19_0016_intraday-extreme-return-router-alpha.md` 作为新增 intake 对象，优先于较老且明显更偏 maker-first 的 option-box 题材。

## P2 -> P3 兜底裁判检查
- 本轮必须执行兜底裁判：`Rank 422` 已经在 `2026-04-18_2358_rank422_p2_exit_promote_p3_scheduler_realism.md` 里完成了最小 honesty / execution realism closure。
- 既然结论已是“足够值得进入 paper trade / paper launch，且没有新的致命 blocker”，bot2 不能再把它继续排成开放式研究。
- 因此本轮正式维持并确认：`Rank 422` 继续留在 `P3 / Paper launch queue`，当前默认动作是 **launch wiring**，不是继续做研究出口题。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`，本轮 `cycle_plan` 重排为：
1. `Rank 422`：P3 launch wiring 前半段（dedicated runner / handoff artifact）
2. `Rank 422`：P3 launch wiring 后半段（scheduler + first verified run -> `connected_runner_live`）
3. `Rank 423`：survivor 唯一 follow-up（entry realism / delay 轴，直接回答 `P2 / P0` 出口）
4. `2026-04-19_0016_intraday-extreme-return-router-alpha.md`：fresh intake 最小首判

新计划满足：
- `P3 launch wiring > survivor follow-up > fresh intake`
- 没有把 background pool 旧对象重新拉回前排
- 没有让新的 `keep_P1` 覆盖 `Rank 423` 的 survivor 槽位
- 每项都只含 `target / action / success_criterion / result / status`
- 新生成项 `result = none`、`status = pending`

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-19_0043_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - command: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（独立执行，不与 publish 链式拼接）：
   - command: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank422先接线 Rank423做唯一复核" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-19_0043_strategy-review.md`
