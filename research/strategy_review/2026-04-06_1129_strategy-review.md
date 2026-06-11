# 2026-04-06 11:29 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - 已连线落地的只有 `connected_runner_live` 列表（`Rank 200 / 201 / 213 / 229 / 342`），没有新的 queue 头对象等待 handoff / wiring。

2. **本轮 `fresh intake` 是什么？**
   - 本轮刚完成的 fresh intake 是 `Rank 352 / BTC perp conditional drift`，来源：
   - `research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
   - 它已在 `research/optimization_loop/2026-04-06_1113_rank352_btc_perp_conditional_drift_intake_keep_p1.md` 被首判为 `keep_P1`，因此不再停留在 fresh intake，而是正式进入 survivor slot。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 值得。
   - 这里的“上一条 fresh intake”现在就是刚刚首判完成的 `Rank 352 / BTC perp conditional drift`。
   - 11:13 UTC 的 intake 结论已经把它压成独立主语：`vol-normalized expected-price slope -> short-cycle directional drift`，并给出了最小可验证骨架（`BTCUSDT perp`、`5m/15m`、`H=1/2/3`、threshold entry、time/sign-flip exit、显式成本壳）。
   - 但它还没完成 after-cost transfer，所以正好符合 policy 对 survivor 的定义：**值得且只值得做 1 次便宜、诚实、能直接收口的 follow-up**。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Active P2 slot.current_target = none`。
   - 最近收口的 P2 是 `Rank 342`，已经完成 `P2 -> P3 -> connected_runner_live`，所以本轮不存在需要 bot2 兜底裁判的活跃 P2。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = Rank 352 / BTC perp conditional drift`
  - `Active P2 = none`
- `Rank 352` 已具正式 rank；前排不存在 `keep_P1 / P2 / P3` 但无 rank 的对象。
- 本轮**无需补 rank**。

## 最近证据与排班判断

本轮按要求先看 fixed policy/state，再看 repo 状态、最近 optimization_loop 与最近 strategy_review。

### 最近会改变排班的证据

1. `research/optimization_loop/2026-04-06_1113_rank352_btc_perp_conditional_drift_intake_keep_p1.md`
   - 说明 fresh intake 已完成 first verdict，且对象进入 survivor slot。
   - 因此本轮默认优先级不再是继续开新的 intake，而是**先完成 Rank 352 的唯一一次 survivor follow-up**。

2. `research/optimization_loop/2026-04-06_1002_rank350_survivor_followup_tradable_alt_bucket_after_cost_background_p0.md`
   - 说明上一条 survivor (`Rank 350`) 已经诚实收口退回 `background / P0`，前排 survivor 槽位已经合法让给更新的 `Rank 352`。

3. `research/optimization_loop/2026-04-06_0854_rank351_rf_threshold_bucket_hf_pairs_first_verdict_background_p0.md`
   - 说明 `Rank 351` 没有形成独立 raw alpha，不会挤占 survivor / P2 / P3 前排资源。

4. repo 最近新增 digest 中，`Rank 352` 收口之后最靠前、最值得作为 fresh intake 的候选是：
   - `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`

### 按 authoritative 顺序扫描当前所有合法动作

1. **P3 / Paper launch queue handoff**
   - 无待接线对象；`current_target = none`。

2. **P2 / Active P2 admission / promote / park**
   - 无明确 `Active P2`；`current_target = none`。

3. **P1 / Surviving candidate 唯一一次诚实检查**
   - 有，而且必须优先：`Rank 352 / BTC perp conditional drift`。
   - 这一步如果不先排，就违反了 “已有前排对象的收口优先级永远高于新的发现” 与 survivor lock 规则。

4. **fresh intake**
   - 只有在把 `Rank 352` survivor 诚实排到前部后，才可以用剩余预算补新的具体 intake。
   - 最靠前的具体对象应先用最近新 digest：`synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`、`quality-weighted-squeeze-release`。

## 对 `BOT2_BOT3_STATE.md` 的具体改写

本轮已写回 `cycle_plan`，遵循 `P1 survivor > fresh intake` 的默认顺序：

1. `Rank 352 / BTC perp conditional drift`
   - action: 做唯一一次便宜但 decisive 的 survivor follow-up
   - goal: 回答 `5m/15m` 的 `EWMA mean / EWMA vol` proxy 在显式 taker 成本后是否仍有单调性与净边
   - exit: 只能是 `升 P2` 或 `background / P0`

2. `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - action: fresh intake first verdict

3. `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - action: fresh intake first verdict

4. `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
   - action: fresh intake first verdict

新计划项全部保持：`result = none`、`status = pending`。

## P2 -> P3 兜底检查

- 当前没有 `Active P2`。
- 因此本轮不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 执行备注

- `BOT2_BOT3_STATE.md` 已按本轮 review 写回。
- 中文邮件摘要已通过 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py` 正常发出。
- 首页刷新脚本已尝试执行，但脚本内固定依赖 `sudo mkdir/install/chown` 发布到 `/var/www/momentum-report`；当前 cron runtime 无可用提权能力，因此停在发布权限门槛，未能完成外层站点落盘。

## 一句话结论

本轮 runtime truth 很简单：`Paper launch queue` 为空，`Active P2` 为空，但 `Rank 352 / BTC perp conditional drift` 已经刚刚成为新的合法 survivor，所以正确排班不是继续把新 intake 顶到前面，而是先用它那唯一一次 follow-up 诚实收口；只有把这一步排在首位之后，才轮到 `synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`、`quality-weighted-squeeze-release` 这些新的具体 intake。