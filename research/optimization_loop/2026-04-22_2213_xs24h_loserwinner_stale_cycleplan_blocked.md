# stale cycle_plan blocker — xs24h loser→winner voltarget shell

- 时间：2026-04-22 22:13 UTC
- 对象：`research/quant_digests/2026-04-22_0622_xs24h-loserwinner-voltarget-shell.md`
- 关联旧 Rank：`Rank 433 / 24h loser→winner majors8 RV fade`
- 本轮动作类型：`cycle_plan pending item legality check`
- 结论：`blocked`

## 本轮只回答的一个问题
当前 `cycle_plan` 第 2 项把 `24h loser→winner fade × inverse-vol dollar-neutral sizing` 重新写成了 fresh intake pending；但这个对象今天早些时候已经完成过正式 front-slot 流转：
1. `2026-04-22_0701_rank433_xs24h_loserwinner_freshintake_keep_p1.md` 已给它分配正式 `Rank 433`，并完成 fresh intake first verdict `keep_P1`；
2. `2026-04-22_0714_rank433_survivor_followup_background_p0.md` 又完成了它唯一允许的 survivor follow-up，并把它诚实收口到 `background/P0`；
3. 当前 runtime 的 `Background pool.latest_parked` 里也已明确记录 `Rank 433` 已因 child-execution realism 不成立而回到 background。

因此，这个 pending 小点已经不再具备合法前置条件：
- 它不是新的 fresh intake；
- 它也不是当前前排槽位里的 survivor / active P2 / P3；
- policy 明确禁止把已回到 `Background pool` 的旧候选自动拉回前排。

## 为什么本轮不能继续执行它
如果继续把它当 fresh intake 再做一遍，等于绕过：
- `Rank identity` 的 durable identity 约束；
- `Surviving candidate` 只允许 1 次 follow-up 的硬预算；
- `Background pool` 不得自动 reopen 的 policy。

所以本轮合法动作不是重做研究，而是把这个 stale pending 小点标记为 `blocked`。

## 本轮会改变系统认知的一句话
`24h loser→winner fade × inverse-vol dollar-neutral sizing` 不是新的 fresh intake；它已经以 `Rank 433` 完成 `keep_P1 -> survivor follow-up -> background/P0` 全流程，因此当前这个 cycle_plan pending 属于 stale 重排，按 policy 必须阻断而不是重做。

## 尾部执行状态（异步回执补记）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步回执为 `signal SIGKILL`（2026-04-22 22:22:35 UTC），按 policy 视为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`send_text_email.py` 已成功发送（`[momentum-bot3-auto] stale pending 阻断`）。
