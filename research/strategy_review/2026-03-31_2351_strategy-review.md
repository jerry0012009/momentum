# 2026-03-31 23:51 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；先读 policy + state，再看 repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已接线对象仍只有 `Rank 200 / 201 / 213 / 229`，没有新的 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`Rank 274 / ETH dual-thrust SMA200 breakout`。**
   - 证据：最近 `optimization_loop` 头部显示 `2026-03-31_2346_rank274_eth_dual_thrust_keep_p1.md` 刚完成 fresh intake 首判，并已写回 state：`Fresh intake slot.status = completed_keep_P1`、`current_target = Rank 274`。因此当前 runtime 里最近一条 fresh intake 已不是 `turning-point confirmed continuation`，而是刚被正式编号并保留 survivor 权的 `Rank 274`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**不值得。**
   - 证据：上一条 fresh intake 是 `turning-point confirmed continuation`；它已在 `research/optimization_loop/2026-03-31_2314_turning_point_confirmed_continuation_intake_background_p0_sparse_nontransferable.md` 被诚实收口为 `background/P0`。关键原因不是“还差最后一点验证”，而是最小 causal transfer 下 5 年 BTC/ETH/SOL perp majors 只触发 4 个事件，跨资产不成立、after-cost 也不稳，因此不该占用 survivor 槽位。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`BOT2_BOT3_STATE.md` 已明确写明 `Active P2 slot.current_target: none`；最近一次 active P2 仍是 `Rank 267`，但已在 `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 正式收口为一次性 `P2 -> P1 re-scope`，当前不再占 active 槽位。

## 前排 / rank 合法性检查

- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 274`
- `Active P2 slot.current_target = none`
- 当前前排对象都已有正式 `Rank`；不存在 `keep_P1 / P2 / P3` 级别却无 rank 的对象。
- 结论：**本轮无需补 rank。**

## `P2 -> P3` 兜底检查

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接改写 state 进入 `P3 / handoff`。

本轮复核结果：**不触发该兜底。**
- 当前 `Active P2 = none`；
- 当前不存在“已经够格进入 paper trade、却仍被 bot3 卡在 P2”的对象；
- 因此前排最高优先级动作不是 `P3 handoff` 或 `P2 exit`，而是先收掉当前唯一合法 survivor `Rank 274`。

## repo / recent evidence 摘要

- repo 当前仍有大量未跟踪文件，但本轮只把它当作环境噪音，不反向改 policy。
- 最近 `optimization_loop` 头部顺序显示：
  1. `2026-03-31_2346_rank274_eth_dual_thrust_keep_p1.md`
  2. `2026-03-31_2314_turning_point_confirmed_continuation_intake_background_p0_sparse_nontransferable.md`
  3. `2026-03-31_2256_liquidity_conditioned_lagged_return_fork_intake_background_p0.md`
  4. `2026-03-31_2230_rank273_survivor_followup_background_p0_lookback_fixed_single_pair_thin_pocket.md`
- 这说明：
  - `turning-point confirmed continuation` 已被诚实打回 `P0`；
  - 最新 front-slot 变化是 `Rank 274` 获得 `keep_P1`；
  - 当前确实存在一个合法 survivor 动作，因此按 policy 不得直接把新的 intake 排到它前面。
- 最近 `quant_digests` 里，当前最靠前、尚未执行的新对象是：
  - `2026-03-31_2320_orderbook-confidence-threshold-direction-alpha.md`
  - `2026-03-31_2156_inverse-options-maker-regime-skew-alpha.md`
  - `2026-03-31_2104_btc-leader-alt-loser-dispersion-alpha.md`

## cycle_plan 重排逻辑

按 policy 默认顺序从高到低扫描：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor follow-up`：**有**，`Surviving candidate = Rank 274`，且 follow-up budget 还剩 1；
4. 因此前两类为空、但 survivor 仍未收口，当前轮必须先把 `Rank 274` 排在最前；
5. 只有把 survivor 诚实排入前部后，才允许用剩余预算补新的 `fresh intake`。

因此本轮把 `cycle_plan` 重写为：
1. `Rank 274 / ETH dual-thrust SMA200 breakout` survivor follow-up
2. `2026-03-31_2320_orderbook-confidence-threshold-direction-alpha.md`
3. `2026-03-31_2156_inverse-options-maker-regime-skew-alpha.md`
4. `2026-03-31_2104_btc-leader-alt-loser-dispersion-alpha.md`

这样写符合 policy：
- 没有把新的 fresh intake 排到未收口的 survivor 前面；
- 没有伪造空槽确认动作去占轮次；
- `Rank 274` 继续享有 survivor 锁定权，不被新的 `keep_P1` 覆盖；
- 剩余预算全部填入具体对象，而不是抽象模板句。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue = none`、`Active P2 = none`；
  - 保持 `Surviving candidate = Rank 274`；
  - 将当前轮 `cycle_plan` 重写为 `Rank 274 survivor follow-up -> 2320 orderbook confidence threshold -> 2156 inverse options maker skew -> 2104 BTC leader × alt loser dispersion`；
  - 新生成项全部满足 `result = none`、`status = pending`。
- 未改写 policy / brief / operating card / auto loop / cron prompt。
- 未自动把 background pool 旧候选拉回前排。

## 执行备注

- 邮件已发送：`[momentum-bot2-review] Rank274 survivor 优先，切回 2320 新 intake`
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 需要 `sudo` 写入 `/var/www/momentum-report/index.html`；本次 cron 运行环境不提供 elevated exec，因此首页发布在 `sudo` 步骤被环境权限阻塞，未在本轮内完成。
