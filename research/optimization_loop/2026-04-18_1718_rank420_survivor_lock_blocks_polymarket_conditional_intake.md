# 2026-04-18 17:18 UTC — conditional fresh intake blocked by active survivor lock

本轮按 policy + state 读取 `cycle_plan` 后，排在最前的 pending 小点是 item2：
`research/quant_digests/2026-04-18_1240_polymarket-dumphedge-complementary-arb.md`。

结论：该小点本轮必须标记为 `blocked`，不执行研究主体。

原因：
- item1 已在本轮前序状态中诚实收口，并产出 `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion`。
- 当前 runtime 明确存在 `Surviving candidate slot = Rank 420`，且 `followup_budget_remaining: 1`。
- 根据 policy，survivor 是前排锁定对象；只有在 `survivor / P2 / P3` 都没有真实可执行动作时，conditional fresh intake 才能前进。
- 因此前置条件“item1 已诚实收口且仍无 survivor / P2 / P3”已经被 state 明确否定，继续执行 Polymarket complementary-arb 首判会构成非法绕行前排对象。

已回写 runtime：
- cycle_plan item2 `status -> blocked`
- cycle_plan item2 `result -> blocked：item1 已产出 Rank 420 survivor，当前前排不为空，因此该 conditional fresh intake 的前置条件不成立，不能绕过 survivor 锁定继续 intake Polymarket 补体错价。`

本轮无新对象、无层级变化、无 rank 变化；属于 guard 型合法阻断。

尾部执行状态（non-blocking）：
- homepage publish（`bash scripts/publish_homepage_index.sh`）异步结果：进程被 `SIGKILL` 终止；按 policy 视为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- 邮件通知（`send_text_email.py`）异步结果：`code 0` 成功发送。