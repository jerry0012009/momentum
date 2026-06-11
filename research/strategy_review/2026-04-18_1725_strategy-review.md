# 2026-04-18 17:25 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仅见既有未跟踪临时/研究文件噪声；未发现需要按 policy 先补 rank 的前排对象）
- Recent optimization loop:
  - `2026-04-18_1718_rank420_survivor_lock_blocks_polymarket_conditional_intake.md`
  - `2026-04-18_1705_rank420_deribit_atmiv_straddle_first_verdict_keep_p1.md`
  - `2026-04-18_1641_rank57_conditional_freshintake_stale_replay_blocked.md`
  - `2026-04-18_1628_rank27_conditional_freshintake_blocked_stale_replay.md`
  - `2026-04-18_1612_rank60_freshintake_blocked_stale_absorbed_by_rank378.md`
- Recent strategy review:
  - `2026-04-18_1645_strategy-review.md`
  - `2026-04-18_1357_strategy-review.md`
  - `2026-04-18_1304_strategy-review.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 列表中的对象都已完成 dedicated runner + scheduler + first verified run，当前没有待补 wiring 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**本轮 fresh intake 已经被消费为 `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion`。**
   - 当前 `Fresh intake slot.status = promoted_to_survivor`、`current_target = none`，说明本轮新的 intake 已完成首判并升入 survivor，而不是仍停留在未决 intake 状态。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得。**
   - 决定性依据来自 `2026-04-18_1705_rank420_deribit_atmiv_straddle_first_verdict_keep_p1.md`：
     - `cheap-IV long-vol` 半边当前不成立；
     - 但 `BTC-first rich-IV short delta-neutral ATM straddle` 的 proxy 证据已经足够清楚；
     - 且唯一剩余 blocker 已经收敛为单轴：`真实 option-chain fill / hedge PnL realism`。
   - 这正符合 policy 对 survivor 唯一 follow-up 的使用条件，因此本轮前排应继续给 `Rank 420`，而不是绕过去开新的 intake。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 仍是 `Rank 417`，但它已在 `2026-04-16_0309_rank417_p2_exit_rescope_to_p1_noeth_pairs.md` 完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前 `Paper launch queue / Surviving candidate / Active P2` 前排对象均已有正式 rank。
- `Surviving candidate = Rank 420`，合规。
- 本轮无需补新 `Rank`。

## 排班判断
- 当前没有 `P3 launch wiring`，没有 `Active P2`；但明确存在 `Surviving candidate = Rank 420`，且 `followup_budget_remaining = 1`。
- 根据 policy，已有前排对象的收口优先级高于任何新的 `fresh intake`；因此上一版 cycle plan 中把 Polymarket / tri-arb / session drift 放在继续 intake 的位置已经过时，必须把 `Rank 420` survivor follow-up 放回队首。
- 本轮最诚实的排班顺序应是：
  1. `Rank 420` survivor 唯一 follow-up（回答 `promote_P2` 还是 `background/P0`）
  2. 若 item1 收口后前排重新为空，再回到 `Polymarket YES+NO < 1` 补体错价
  3. 再看 `triangular cross-rate loop`
  4. 再看 `21:00–23:00 UTC fixed-window drift`

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`，因此不存在 bot2 必须兜底直升 `P3 / Paper launch queue` 的对象。
- `Paper launch queue.current_target = none`，也不存在 queue 内待补 runner / scheduler / first verified run 的接线对象。
- 结论：**本轮无需**直接把任何对象写入 `P3 / Paper launch queue` 或 handoff 路径。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot` / `Surviving candidate slot` 当前 runtime 事实不变；
- 仅重写 `cycle_plan`，把 `Rank 420` survivor follow-up 提到 item1；
- `Polymarket complement / tri-arb cross-rate / session drift` 全部后移为 conditional fresh intake。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_1725_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank420 survivor锁前排，先做唯一期权真实回放" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_1725_strategy-review.md`

## Tail execution result
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 最终以 `signal SIGKILL` 结束；按 policy 记为**非阻断尾部失败**，不回滚本轮已写出的 state / review / cycle_plan。
- email notify：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送到默认收件人。
