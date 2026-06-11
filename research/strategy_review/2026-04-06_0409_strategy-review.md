# Strategy Review — 2026-04-06 04:09 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 optimization：
  - `research/optimization_loop/2026-04-06_0337_rank346_macro_impulse_sentiment_gate_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0324_sg_lob_imbalance_fresh_intake_background_p0.md`
  - `research/optimization_loop/2026-04-06_0311_rank345_survivor_followup_drop_background.md`
  - `research/optimization_loop/2026-04-06_0258_rolling_max_intake_blocked_duplicate_rank234.md`
  - `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-06_0300_strategy-review.md`
  - `research/strategy_review/2026-04-06_0155_strategy-review.md`
  - `research/strategy_review/2026-04-06_0053_strategy-review.md`
- 最近新 digest / intake 候选：
  - `research/quant_digests/2026-04-06_0357_adaptive-2sma-walkforward-perp-trend-alpha.md`
  - `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`
  - `research/quant_digests/2026-04-05_2055_deribit-gammawall-regime-router.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Paper launch queue.current_target = none`。
- 最近 `Rank 342` 已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成 dedicated runner、scheduler 与首跑验证，并正式写回 `connected_runner_live`。
- 因此当前没有待 handoff 的 `P3` 对象，本轮也不存在 bot2 需要兜底补推到 `P3` 的漏项。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 应切到** `research/quant_digests/2026-04-06_0357_adaptive-2sma-walkforward-perp-trend-alpha.md`。
- 原因：
  1. `Rank 346` 已完成上一条 fresh intake 的 first verdict，并已依法进入唯一 `Surviving candidate slot`，不能继续被误写成当前 intake 位；
  2. `SG-smoothed LOB imbalance` 已在 `2026-04-06_0324` 收口为 `background / P0`，不能回前排；
  3. `rolling-MAX` 已在 `2026-04-06_0258` 被确认是旧对象 `Rank 234` 的 duplicate，不得再当 fresh intake；
  4. 在当前未首判的新对象里，`adaptive 2-SMA walk-forward perp trend` 是最新且具备完整 raw-alpha 骨架的具体候选，因此应接管 fresh intake 槽位。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且它现在就是前排第一优先级。**
- 上一条 fresh intake 是 `Rank 346 / scheduled-macro impulse × pre-event sentiment gate`。
- `research/optimization_loop/2026-04-06_0337_rank346_macro_impulse_sentiment_gate_first_verdict_keep_p1.md` 已明确说明：
  - 这条线的对象主语已经独立于旧的 `FOMC/CPI blackout` 与 `macro vol gate`；
  - 但 admission 所需的关键缺口仍在于 `BTC/ETH × FOMC/CPI/NFP/PCE × 1m/3m/5m/15m` 的 taker / delay after-cost follow-through 是否存在；
  - 所以下一轮唯一 survivor follow-up 必须直接收口这个问题，不能再重复 distinctness 论证。
- 因此答案是：**值得，而且 survivor budget 仍剩 1 次，必须先把这次用掉并给出 `promote_P2` 或 `drop_to_background` 的终局结论。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 active P2 是 `Rank 342`，但它已在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后又在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成 `P3 launch wiring -> connected_runner_live`。
- 因此当前没有需要 bot2 兜底裁判 `P3 / P1 / P0` 出口方向的滞留 `P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 346`
- `Active P2 slot.current_target = none`
- 当前所有前排对象均已带 rank；不存在达到 `keep_P1 / P2 / P3` 但无 rank 的违规状态，因此本轮无需补发 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- desk review 未发现任何“已经足够进入 paper trade、但 bot3 尚未升级”的漏判对象。
- 因此本轮不需要执行 `P2 -> P3` 的强制写回；当前重点是把 `Rank 346` 的 survivor follow-up 收口，并把新的 fresh intake 正确切到最新对象。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前合法前排链条为：
- `P3`: none
- `P2`: none
- `P1 survivor`: `Rank 346`

因此本轮排班必须先收口 `Rank 346`，然后才轮到新的 fresh intake。已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Rank 346 / scheduled-macro impulse × pre-event sentiment gate` survivor follow-up
2. `research/quant_digests/2026-04-06_0357_adaptive-2sma-walkforward-perp-trend-alpha.md`
3. `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`
4. `research/quant_digests/2026-04-05_2055_deribit-gammawall-regime-router.md`

### 为什么这么排
- `Rank 346` 作为当前唯一 survivor，依法享有前排锁定权；在它那唯一一次 follow-up 收口前，不能让新的 `keep_P1` 候选覆盖 survivor 槽位。
- `adaptive 2-SMA` 是当前最新且未首判的具体 raw-alpha 候选，应接 fresh intake 位；但它必须排在 survivor 后面。
- `SaR overlay` 仍是未首判、且可直接服务当前 alpha 池的具体 overlay 对象，保留为后续 fresh intake。
- `Deribit gammawall router` 虽是 regime/router 而非裸方向 alpha，但属于可明确验证、能服务 breakout 与 fade 的共享前排候选，适合作为 conditional 第四项。
- `SG-smoothed LOB imbalance`、`AdaptiveTrend basket`、`rolling-MAX duplicate` 都已收口或被 guard 拦下，不能再拿来占本轮前排。

## 对 repo 状态的最小备注
- repo 当前存在若干未跟踪临时文件与历史产物，但本轮 policy 明确规定调度只以 `BOT2_BOT3_STATE.md` 与最近 research evidence 为准；这些临时文件不构成 reopen 旧对象或改变前排顺序的理由。

## 本轮一句话
当前没有 `P3`、也没有 `Active P2`；唯一必须先做的是把 `Rank 346` 的 survivor follow-up 诚实收口，然后把 fresh intake 切到最新的 `adaptive 2-SMA walk-forward perp trend`，再依次处理 `SaR` 与 `Deribit gammawall` 这两个具体候选。