# 2026-04-20 11:18 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-20_0726_hyperliquid_funding_signflip_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-20_0713_ctos_beta_pairs_pending_stale_closed.md`
  - `research/optimization_loop/2026-04-20_0659_negative_funding_5davg_carry_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-20_0619_cycle_plan_no_pending_guard.md`
  - `research/optimization_loop/2026-04-20_0116_rank427_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-19_2354_rank427_p2_exit_promote_p3_exeth_corebounce.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-20_0912_strategy-review.md`
  - `research/strategy_review/2026-04-20_0229_strategy-review.md`
  - `research/strategy_review/2026-04-20_0145_strategy-review.md`
- Recent candidate sources scanned:
  - `research/quant_digests/2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`
  - `research/quant_digests/2026-04-19_1602_crosschain-negative-spillover-rv-alpha.md`
  - `research/quant_digests/2026-04-19_1636_xs-reversal-horizon-transition-portability.md`
  - `research/quant_digests/2026-04-19_1712_emacross-volume-bracket-pocket-alpha.md`
  - `research/park_reframe/INDEX.md`

## Repo snapshot
- `Paper launch queue` 非空，且所有已入队对象都写在 `connected_runner_live`；当前 `current_target = none`，没有待接线的 P3。
- `Fresh intake slot` 当前指向 `research/quant_digests/2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`，仍未完成 first verdict。
- `Surviving candidate slot = none`；上一条 survivor `Rank 428` 已在 `2026-04-20_0128` 用完唯一 follow-up 并收口 `background/P0`。
- `Active P2 slot = none`；最近唯一 P2 出口是 `Rank 427` 已在 `2026-04-19_2354` 升到 `P3`，并在 `2026-04-20_0116` 完成 launch wiring。
- 当前没有需要 bot2 兜底直推 `P2 -> P3` 的对象，也没有前排无 rank 的违规对象。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是。`connected_runner_live` 非空，但 `current_target = none`，本轮没有待接线的 `P3` 对象。

2. 本轮 `fresh intake` 是什么？
- `research/quant_digests/2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。上一条 fresh intake 是 `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`；它已在 `2026-04-20_0726` 直接收口 `background/P0`，没有 survivor 资格，也不应再给 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在，`Active P2 = none`。

## Rank 完整性检查
- 当前前排对象检查结果：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate slot = none`
  - `Active P2 slot = none`
- 现有前排不存在缺 rank 对象，本轮无需补新 `Rank`。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot` 锁定到当前唯一前排对象 `2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`，明确写成 pending，避免被后续 intake 覆盖。
- 不改写 policy / brief / cron prompt，只重排 runtime state 与当前轮 `cycle_plan`。
- 因当前不存在真实 `P3 / P2 / P1` pending 动作，本轮预算全部用于具体 fresh intake；同时遵守“当前 fresh intake 先做完，再排 conditional intake”的顺序。

## 当前轮 cycle_plan
1. `research/quant_digests/2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`
   - action: fresh intake first verdict，先回答 `EMA200 顺势外轨触碰回归 × opposite-band maker exit` 在 maker fill realism、TIME exit 集中度、band-width 过窄与 trend-day 接飞刀风险下，是否仍保留独立 after-cost pocket。
   - success_criterion: 只能输出 `keep_P1` 或 `background/P0`；若没有跨币且统一成本后的可复制 pocket，就直接收口。
2. `research/quant_digests/2026-04-19_1602_crosschain-negative-spillover-rv-alpha.md`
   - action: conditional fresh intake，检查跨链 spillover relative-value 在 `t+2` 延迟确认、双腿成本与窗口现实化后，是否仍保留可复制 after-cost pocket。
   - success_criterion: 必须直接 `keep_P1` 或 `background/P0`。
3. `research/quant_digests/2026-04-19_1636_xs-reversal-horizon-transition-portability.md`
   - action: conditional fresh intake，检查 XS reversal → continuation horizon transition 在 turnover cap、统一 `8bps` 成本与资产分层后是否仍成立。
   - success_criterion: 必须直接 `keep_P1` 或 `background/P0`。
4. `research/quant_digests/2026-04-19_1712_emacross-volume-bracket-pocket-alpha.md`
   - action: conditional fresh intake，检查 `EMA cross × volume confirmation × bracket exit pocket` 在 next-bar entry、固定 TP/SL 与 TIME exit realism 下是否仍保留独立 after-cost pocket。
   - success_criterion: 必须直接 `keep_P1` 或 `background/P0`。

## Review verdict
- 本轮不存在需要 bot2 兜底裁决的 `Active P2 -> P3` 个案；`Rank 427` 已完成 promote 与 launch wiring，不需要重复处理。
- `Paper launch queue` 虽非空，但目前没有未接线对象，因此默认优先级自然切回 fresh intake。
- 当前唯一必须先推进的前排对象是 `bbtouch-oppositeband-maker-shell`；只有它被诚实首判后，后面的 conditional fresh intake 才应依次执行。
- 未从 `Background pool` 自动拉回任何旧候选；`park_reframe` 仅作后备导航，本轮并未动用。
