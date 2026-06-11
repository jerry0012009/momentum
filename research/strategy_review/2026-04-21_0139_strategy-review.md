# 2026-04-21 01:39 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-20_2312_kalman_dynhedge_pairspread_freshintake_background_p0_singlepair.md`
  - `research/optimization_loop/2026-04-20_2058_rank430_survivor_followup_background_p0_dayconcentration.md`
  - `research/optimization_loop/2026-04-20_1950_cycle_item2_blocked_survivor_already_locked.md`
  - `research/optimization_loop/2026-04-20_1841_rank430_liquidity_sweep_rejection_bounce_freshintake_keep_p1.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-20_1954_strategy-review.md`
- Recent candidate sources checked:
  - `research/quant_digests/2026-04-20_1129_dual-momentum-breakout-expansion-alpha.md`
  - `research/quant_digests/2026-04-20_0455_betacorr-gated-betaweighted-futures-pairs-shell.md`
  - `research/quant_digests/2026-04-20_1856_speed-volume-momentum-shell-alpha.md`
  - `research/quant_digests/2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空：`connected_runner_live` 里已有多条已接线对象；但当前 `current_target = none`，没有待补 runner / scheduler / first run 的 active P3 接线项。

2. 本轮 `fresh intake` 是什么？
- 由于 `P3 / Active P2 / Surviving candidate` 已全部收口，本轮切回 fresh intake。
- 按本轮重排后的顺序，fresh intake 依次是：
  - `research/quant_digests/2026-04-20_1129_dual-momentum-breakout-expansion-alpha.md`
  - `research/quant_digests/2026-04-20_0455_betacorr-gated-betaweighted-futures-pairs-shell.md`
  - `research/quant_digests/2026-04-20_1856_speed-volume-momentum-shell-alpha.md`
  - `research/quant_digests/2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得，因为上一条 fresh intake 已经收口，不再占 survivor 槽位。
- 最近一条 fresh intake 是 `Kalman dynamic hedge ratio × rolling z-score spread fade`；它已在 `2026-04-20_2312...` 被诚实判为 `background/P0`，理由是统一双腿 `8bps` 与非单 pair 约束下仅剩 `XRP/DOGE` 单 pair pocket，不符合 survivor 条件。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。`Active P2 = none`。

## Rank 完整性检查
- 当前前排对象检查：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate slot.current_target = none`
  - `Active P2 slot.current_target = none`
- 不存在缺 rank 的前排对象；本轮无需补新 `Rank`。

## State rewrite（按 policy 默认排班顺序）
- 前排 `P3 / P2 / P1` 均无真实可执行动作，因此本轮合法动作全部来自 `fresh intake`。
- 已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，当前轮具体任务为：
  1. `dual-momentum breakout × ATR expansion` first verdict
  2. `beta-corr gated beta-weighted futures pairs shell` first verdict
  3. `speed-volume momentum shell` first verdict
  4. `hawkes LOB excitation × base-imbalance` first verdict
- 所有新项均满足：`result = none`、`status = pending`。

## P2 -> P3 兜底判断
- 当前没有 `Active P2`，也没有待接线 `P3 current_target`。
- 本轮不存在“已够格但 bot3 尚未升级”的对象，因此无需 bot2 直接强推 `P3 / Paper launch queue`。

## Tail step status
- homepage publish（独立命令）已尝试：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，进程最终 `SIGKILL`，按规则记为非阻断尾部失败，不回滚 state/log。
- email notify（独立命令）已完成：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排已收口并切回 fresh intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-21_0139_strategy-review.md`，已发送到默认收件人。
