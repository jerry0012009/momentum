# 2026-04-01 02:30 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；先读 policy + state，再看 repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已接线对象仍只有 `Rank 200 / 201 / 213 / 229`，没有新的 queue 头需要接线。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**当前运行态中的 `Fresh intake slot` 为空；若前排收口后切回新的 intake，第一条应是 `research/quant_digests/2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`。**
   - 证据：`Rank 276` 已在 `2026-04-01_0157_rank276_survivor_followup_promote_p2.md` 从 `fresh intake -> keep_P1 -> survivor follow-up` 正式推进到 `Active P2`，因此当前 `Fresh intake slot.current_target = none`。同时最近 `quant_digests/` 目录里，尚未执行且时间最新的具体对象是 `2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`，其次才是 `2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且已经用完并成功升入 `P2`。**
   - 证据：上一条 fresh intake 是 `Rank 276 / BTC 15m Donchian overshoot fade × 10bps breach threshold`。它在 `2026-04-01_0144_rank276_donchian_overshoot_fade_keep_p1.md` 被诚实首判为 `keep_P1`，随后唯一一次 follow-up `2026-04-01_0157_rank276_survivor_followup_promote_p2.md` 已用 repo 原始公开 raw CSV 与同源规则完成 source-faithful reproduction：`5bps` 与 source 表格逐项对齐，且 OOS 在 `8/10bps` 下仍保留正 pocket，因此 survivor 预算用尽后的诚实出口是 `promote_P2`，不是回 `background/P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**存在：`Active P2 = Rank 276`，而且当前离 `P3` 最近。**
   - 证据：`BOT2_BOT3_STATE.md` 当前明确写明 `Active P2 slot.current_target = Rank 276 / BTC 15m Donchian overshoot fade × 10bps breach threshold`。最近日志还表明它不是脆弱的 repo headline：`5bps` 已 source-faithful 对齐，OOS 在 `8/10bps` 下仍为正；这说明对象已经越过“有没有 pocket”这道门槛，当前最近的合法出口不再是 `P1` 或 `P0`，而是先完成 `time stability` 与 `honesty / execution realism` 两个 admission blocker，然后优先回答是否直接 `promote_P3`。

## 前排 / rank 合法性检查

- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = Rank 276`
- 当前前排对象都已有正式 `Rank`；不存在 `keep_P1 / P2 / P3` 级别却无正式 rank 的对象。
- 结论：**本轮无需补 rank。**

## `P2 -> P3` 兜底检查

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接改写 state 进入 `P3 / handoff` 路径。

本轮复核结果：**暂不直接触发该兜底，但 `Rank 276` 已明显更靠近 `P3`，不应再被排成开放式重复研究。**
- 当前 `Active P2 = Rank 276`；
- 已有证据足以证明这不是 coursework 幻觉，且 source-faithful pocket 在 OOS 与更厚成本壳下仍存在；
- 但当前仍缺两道会直接改变 `paper trade` 判断的 admission blocker：
  1. `time stability`：edge 是否集中在极少数窗口；
  2. `honesty / execution realism`：`spot vs perp / maker-taker / funding-slippage` 下是否仍足够诚实；
- 因而本轮最诚实的 bot2 动作不是假装已到 P3，也不是继续空转新 intake，而是把这两个最接近出口的问题直接排到 `cycle_plan` 最前，并把第二项 success criterion 写成：若 realism 过关，则直接 `promote_P3`。

## repo / recent evidence 摘要

- 最近 `optimization_loop` 头部顺序显示：
  1. `2026-04-01_0230_rank276_p2_admission_blocked_by_empty_cycle_plan.md`
  2. `2026-04-01_0157_rank276_survivor_followup_promote_p2.md`
  3. `2026-04-01_0144_rank276_donchian_overshoot_fade_keep_p1.md`
  4. `2026-04-01_0118_rank275_survivor_followup_background_p0.md`
- 这说明当前真正的运行问题不是 `Rank 276` 证据不足，而是 **`Active P2` 已存在，但上一轮 `cycle_plan` 被耗尽后没有被 bot2 及时重写，导致 bot3 合法动作断档**。
- 最近 `quant_digests/` 里，尚未执行且最新的具体 intake 顺序是：
  1. `research/quant_digests/2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`
  2. `research/quant_digests/2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`
  3. `research/quant_digests/2026-04-01_0034_cex-dex-priority-fee-delay-arb-alpha.md`
- 因为当前确实存在合法 `Active P2` 收口动作，所以这些新对象都不能排到 `Rank 276` 前面。

## cycle_plan 重排逻辑

按 policy 默认顺序从高到低扫描：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：**有，而且就是当前最优先的 `Rank 276`**；
3. `P1 survivor follow-up`：无，`Surviving candidate = none`；
4. 因此前两项必须先围绕 `Rank 276` 的 admission blocker 排满前部；
5. 只有在 `P2` 收口动作已经诚实排在当前轮前部后，剩余预算才能补新的 `fresh intake`；
6. 新 intake 来源优先使用最近新的 repo/paper/alpha 报告，因此依次补 `0226 us-session cross-sectional reversal` 与 `0138 l1 imbalance × vwap spread direction`。

因此本轮把 `cycle_plan` 重写为：
1. `Rank 276` — `time stability` admission
2. `Rank 276` — `honesty / execution realism` admission（过关则直接 `promote_P3`）
3. `2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`
4. `2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`

这样写符合 policy：
- 没有把新的 fresh intake 排到现存 `Active P2` 前面；
- 没有伪造空槽确认动作去占轮次；
- 没有继续沿用已经耗尽的旧 `cycle_plan`；
- 也没有把 background pool 旧候选拉回前排。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue = none`；
  - 保持 `Active P2 = Rank 276`；
  - 保持 `Fresh intake slot = none`、`Surviving candidate slot = none`；
  - 将当前轮 `cycle_plan` 重写为：`Rank 276 time stability admission -> Rank 276 honesty/execution realism admission -> 0226 US session cross-sectional reversal intake -> 0138 L1 imbalance × VWAP spread intake`；
  - 新生成项全部满足 `result = none`、`status = pending`。
- 未改写 policy / brief / operating card / auto loop / cron prompt。
- 未自动把 background pool 旧候选拉回前排。
