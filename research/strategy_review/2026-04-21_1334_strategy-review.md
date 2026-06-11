# 2026-04-21 13:34 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（当前仍有大量历史 untracked 临时文件；本轮只更新 runtime state 与本日志）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_1328_crossvenue_funding_spread_diptolerance_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_1306_rank431_p2_exit_promote_p3_recentslice_overlap.md`
  - `research/optimization_loop/2026-04-21_1158_rank431_p2_exit_rescope_to_p1_nearatom_only.md`
  - `research/optimization_loop/2026-04-21_1148_rank431_p2_admission_round1_keep_p2_single_durable_pair_blocker.md`
  - `research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_1152_strategy-review.md`
  - `research/strategy_review/2026-04-21_1110_strategy-review.md`
  - `research/strategy_review/2026-04-21_0903_strategy-review.md`
- Current intake sources checked / selected:
  - `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
  - `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`
  - `research/quant_digests/2026-04-21_1348_bbrsi-bracket-meanreversion-shell.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- 当前 `current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`。
- 因为 `Rank 431` 还没有 dedicated runner / scheduler / first verified run，所以 queue 不是“只需观察”的状态，而是存在明确 `P3 launch wiring` 动作。

2. 本轮 `fresh intake` 是什么？
- 在 `P3 launch wiring` 之后，本轮 fresh intake 顺位为：
  1. `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`（`BTC impulse × alt own-move confirmation / reentry × BTC-fail exits`）
  2. `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`（`spread z-score fade × zero-cross exit × kill-switch`）
  3. `research/quant_digests/2026-04-21_1348_bbrsi-bracket-meanreversion-shell.md`（`BB20 touch + RSI14 extreme MR × 2%/4% bracket exits`）

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 上一条 fresh intake 是 `cross-exchange funding spread carry × dip-tolerance 持仓门控`。
- 不值得 follow-up；它已在 `research/optimization_loop/2026-04-21_1328_crossvenue_funding_spread_diptolerance_freshintake_background_p0.md` 诚实收口为 `background/P0`。
- decisive blocker 是同源 portability probe 在 `BTC/ETH/SOL`、`15m`、统一 `34bps` roundtrip 成本下 `145` 笔交易 `avg_net_bps≈-32.33`、`win_rate=0`，没有至少两个 symbol / venue-pair 同向 after-cost carry pocket。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 431` 已在 `research/optimization_loop/2026-04-21_1306_rank431_p2_exit_promote_p3_recentslice_overlap.md` 完成 P2 出口并升级为 `P3 / Paper launch queue`。
- 因此当前最近的前排出口不是 P2 的 `P3/P1/P0` 三选一，而是 `P3 launch wiring -> connected_runner_live`。

## Rank 完整性检查
- `Paper launch queue.current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`，已有正式 Rank。
- `Active P2 = none`。
- `Surviving candidate = none`。
- Fresh intake 尚未进入 `keep_P1` 或更高 verdict，无需预先分配 rank。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- `Rank 431` 已由 bot3 正式 `promote_P3`，bot2 无需再兜底升级。
- 但按 policy，进入 P3 但未完成 runner / scheduler / first verified run 的对象仍视作 `launch wiring` 未完成。
- 所以本轮必须把 `Rank 431` 排在 `cycle_plan` 第一项，而不是把 fresh intake 排到它前面。

## State rewrite
已按 policy 默认优先级重写 `docs/BOT2_BOT3_STATE.md` 的当前轮 `cycle_plan`：
1. `Rank 431 / cointegration maker-first + hard time-stop pairs`
   - `P3 launch wiring`
   - 要求 dedicated runner、scheduler、first verified run，并写回 `connected_runner_live` 或同等语义
2. `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
   - fresh intake first verdict
3. `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`
   - fresh intake first verdict
4. `research/quant_digests/2026-04-21_1348_bbrsi-bracket-meanreversion-shell.md`
   - fresh intake first verdict

## 本轮结论
- queue 非空，且 `Rank 431` 的 launch wiring 是当前最高优先级真实动作。
- 上一条 fresh intake 已 `P0`，不享有 survivor follow-up。
- 当前没有 Active P2。
- fresh intake 只作为 P3 接线之后的剩余预算项排入，未覆盖或抢占 `Rank 431` 的 P3 handoff。

## Tail step status
- homepage publish：待本轮尾部独立命令执行。
- email notify：待本轮尾部独立命令执行。
