# 2026-04-18 19:04 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（存在既有 workspace 未跟踪文件与研究产物噪声；本轮未据此改 policy，也未发现需要先补 rank 的前排对象）
- Recent optimization loop:
  - `2026-04-18_1900_rank421_triangular_crossrate_freshintake_keep_p1_lowfee_execution_axis.md`
  - `2026-04-18_1828_polymarket_complementary_arb_freshintake_background_p0_fee_depth_exit.md`
  - `2026-04-18_1805_rank420_survivor_followup_background_p0_option_spread_hedge_realism.md`
  - `2026-04-18_1718_rank420_survivor_lock_blocks_polymarket_conditional_intake.md`
  - `2026-04-18_1705_rank420_deribit_atmiv_straddle_first_verdict_keep_p1.md`
- Recent strategy review:
  - `2026-04-18_1818_strategy-review.md`
  - `2026-04-18_1725_strategy-review.md`
  - `2026-04-18_1645_strategy-review.md`
- Fresh/conditional materials checked for queue rewrite:
  - `research/quant_digests/2026-04-18_1240_polymarket-dumphedge-complementary-arb.md`
  - `research/quant_digests/2026-04-18_0940_us-session-twowindow-drift-alpha.md`
  - `research/quant_digests/2026-04-18_1655_polymarket-latency-binance-shock-alpha.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否。**
   - `current_target = none`；`connected_runner_live` 列表中的对象都已完成 dedicated runner + scheduler + first verified run，不存在待补 wiring 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 421 / 同所同步报价 cross-rate inconsistency`。**
   - 原因：最新 optimization loop（`2026-04-18_1900...`）已经把它完成首判并给出 `keep_P1`；所以当前 runtime 里的“最近一条 fresh intake”已不是 Polymarket complementary-arb，而是 `Rank 421`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得。**
   - 决定性原因：`Rank 421` 的首判已经把 blocker 收敛为单一 `low-fee/depth-aware execution realism` 轴；这符合 survivor 唯一 follow-up 的使用条件。当前不应继续把它当 fresh intake 重做，也不应让新的 `keep_P1` 候选覆盖这个 survivor 槽位。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 仍是 `Rank 417`，但早已完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象：`Surviving candidate = Rank 421`；`Paper launch queue = none`；`Active P2 = none`。
- 前排对象均已有正式 rank。
- 本轮无需补新 `Rank`。

## 排班判断
- 当前不存在 `P3 launch wiring`，不存在 `Active P2`，但明确存在 `Surviving candidate = Rank 421` 且 `followup_budget_remaining = 1`。
- 根据 policy，survivor 的唯一次 follow-up 拥有前排锁定权；因此上一版把新的 fresh intake 排到队首已经与最新 runtime 不一致，必须改回：
  1. `Rank 421` survivor 唯一 follow-up
  2. 若 item1 诚实收口且前排重新为空，再看 `Polymarket YES+NO < 1`（注意只允许按更窄 spec：深折价 + 深度/fee/early-exit 口径重审）
  3. 再看 `21:00–23:00 UTC fixed-window drift`
  4. 再看 `Binance shock -> Polymarket stale odds`
- 明确不把 `Rank 421` 再次写成 fresh intake，也不让另一条新的 `keep_P1` 候选抢占 survivor 槽位。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- 也没有 desk review 已清楚达到 `paper trade / paper launch` 门槛、但 bot3 尚未升级的对象。
- 结论：**本轮无需**执行 bot2 的 `P2 -> P3` 兜底直升。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot = Rank 421 / keep_P1`、`Surviving candidate = Rank 421` 的最新 runtime 事实；
- 重写 `cycle_plan` 为：
  1. `Rank 421` survivor 唯一 follow-up（P2 / P0 出口轮）
  2. `Polymarket YES+NO < 1` complementary-arb（conditional fresh intake）
  3. `21:00–23:00 UTC fixed-window drift`（conditional fresh intake）
  4. `Binance shock -> Polymarket stale odds`（conditional fresh intake）
- 新生成 pending 项统一写为 `result = none`、`status = pending`。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_1904_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（与 publish 独立执行，无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank421锁定前排，先做唯一次深度费率核验" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_1904_strategy-review.md`

## Tail execution result
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 最终以 `signal SIGKILL` 结束；按 policy 记为**非阻断尾部失败**，不回滚本轮已写出的 state / review / cycle_plan。
- email notify：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送到默认收件人。
