# 2026-04-18 18:18 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（存在既有 workspace 改动与 artifact 刷新噪声；未发现需要本轮先补 rank 的前排对象）
- Recent optimization loop:
  - `2026-04-18_1805_rank420_survivor_followup_background_p0_option_spread_hedge_realism.md`
  - `2026-04-18_1718_rank420_survivor_lock_blocks_polymarket_conditional_intake.md`
  - `2026-04-18_1705_rank420_deribit_atmiv_straddle_first_verdict_keep_p1.md`
  - `2026-04-18_1641_rank57_conditional_freshintake_stale_replay_blocked.md`
  - `2026-04-18_1628_rank27_conditional_freshintake_blocked_stale_replay.md`
- Recent strategy review:
  - `2026-04-18_1725_strategy-review.md`
  - `2026-04-18_1645_strategy-review.md`
  - `2026-04-18_1357_strategy-review.md`
- Fresh-intake candidates read this round:
  - `research/quant_digests/2026-04-18_1240_polymarket-dumphedge-complementary-arb.md`
  - `research/quant_digests/2026-04-18_1048_triangular-crossrate-loop-alpha.md`
  - `research/quant_digests/2026-04-18_0940_us-session-twowindow-drift-alpha.md`
  - `research/quant_digests/2026-04-18_1655_polymarket-latency-binance-shock-alpha.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否。**
   - `current_target = none`，`connected_runner_live` 里列出的对象都已是已接线完成的运行态，不存在待补 runner / scheduler / first verified run 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Polymarket YES+NO < 1` 补体错价。**
   - `Rank 420` 的 survivor follow-up 已在 `2026-04-18_1805...` 诚实收口到 `background/P0`；当前 `P3 / P2 / survivor` 全空，按默认顺序必须切回新的 fresh intake。已把 `research/quant_digests/2026-04-18_1240_polymarket-dumphedge-complementary-arb.md` 提到本轮 `cycle_plan` item1。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，但已经用完且失败。**
   - 上一条 fresh intake 是 `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion`。上一轮把它升为 survivor 是合理的，因为唯一 blocker 已收敛到 `真实 option-chain fill / hedge PnL realism` 单轴；本轮 follow-up 也已经给过，并在 `2026-04-18_1805...` 明确失败：`5d~9d` BTC ATM straddle 最窄 spread 已约 `20bps underlying`，叠加 hedge turnover / option fee / jump tail 后，真实摩擦基本吃掉 proxy short-vol 边际，因此已收口 `background/P0`，不再保留前排。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`。最近一次 active P2 仍是 `Rank 417`，但它已在 `2026-04-16_0309_rank417_p2_exit_rescope_to_p1_noeth_pairs.md` 完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象：`Paper launch queue.current_target = none`、`Surviving candidate = none`、`Active P2 = none`。
- 不存在无 rank 的前排对象。
- 本轮无需补新 `Rank`。

## 排班判断
- 当前不存在 `P3 launch wiring`、不存在 `Active P2`、不存在 survivor follow-up。
- 因此本轮必须按 policy 切回 fresh intake，并且直接指定具体对象。
- 选择顺序遵循“最近新 repo/paper/alpha 报告优先”，同时避免把已经进 background 的旧对象拉回前排：
  1. `Polymarket YES+NO < 1` 补体错价：结构最闭环，且和刚刚结束的 `Rank 420` 无槽位冲突；优先做 fresh intake。
  2. `triangular cross-rate inconsistency`：仍是干净的 relative-value raw alpha，但公开 BBO 下已显示 fee 极敏感，适合作为第二顺位 conditional intake。
  3. `21:00–23:00 UTC fixed-window drift`：时间窗 pocket 已有较清楚 public-data gross 证据，适合作为第三顺位 conditional intake。
  4. `Binance shock -> Polymarket stale odds`：属于另一条 prediction-market event-driven 新对象，尚未被消费，可放在第四顺位 conditional intake。
- 明确不把已在 `background/P0` 的旧对象（如 `tradeflow imbalance router`）重新拉回前排。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- 当前也没有已达到 `paper trade / paper launch` 门槛但尚未升级的对象。
- 结论：**本轮无需**执行 bot2 的 `P2 -> P3` 兜底直升。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot = empty_after_survivor_followup`、`Surviving candidate = none`、`Active P2 = none` 的 runtime 事实不变；
- 重写 `cycle_plan` 为 4 个具体对象，顺序为：
  1. `Polymarket YES+NO < 1` 补体错价
  2. `triangular cross-rate inconsistency`
  3. `21:00–23:00 UTC fixed-window drift`
  4. `Binance shock -> Polymarket stale odds`
- 新生成项统一写为 `result = none`、`status = pending`。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_1818_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（与 publish 独立执行，无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank420收口后切回Polymarket补体错价" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_1818_strategy-review.md`
