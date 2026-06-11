# 2026-04-19 01:32 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization loop:
  - `2026-04-19_0130_rank422_p3_connected_runner_live.md`
  - `2026-04-19_0040_rank423_liqshock_oiunwind_freshintake_keep_p1_symbol_cost_bucket.md`
  - `2026-04-18_2358_rank422_p2_exit_promote_p3_scheduler_realism.md`
- Recent strategy review:
  - `2026-04-19_0043_strategy-review.md`
  - `2026-04-18_2334_strategy-review.md`
- Fresh materials checked for rewrite:
  - `research/quant_digests/2026-04-19_0112_cointegration-spreadfade-router-alpha.md`
  - `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`
  - `research/quant_digests/2026-04-18_2328_crypto-retail-chasing-continuation-alpha.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**是。**
   - 虽然 `current_target = none`，但 `connected_runner_live` 列表明确非空，且 `Rank 422` 已在 `2026-04-19_0130_rank422_p3_connected_runner_live.md` 中完成 runner + scheduler + 首跑验证；因此 queue 不是空，只是当前没有新的未接线 `P3` 待办。

2. 本轮 `fresh intake` 是什么？
   - 结论：**仍是 `Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`。**
   - 它是当前状态里的最新 fresh intake，而且仍占据 survivor 槽位；在 survivor 预算用完之前，不能让新的 `keep_P1` 覆盖它的前排锁定权。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得。**
   - `Rank 423` 已在 `BTC/ETH/SOL/XRP/ADA` 上保留清楚 pocket（组合约 `gross=+22.74bps/event`、`net8≈+14.74bps/event`），而且唯一剩余 blocker 已收敛为 `entry realism / delay`；这正是 policy 允许且要求消耗掉的那一次 survivor 诚实检查。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在明确 `Active P2`。**
   - `Rank 422` 已不再属于 `P2`：它的 desk review 出口在 `2026-04-18_2358_rank422_p2_exit_promote_p3_scheduler_realism.md` 已明确回答 `promote_P3`，而 `2026-04-19_0130_rank422_p3_connected_runner_live.md` 又确认 wiring 已真正完成，所以当前不存在还需要 bot2 兜底裁判的 active P2。

## Rank 合规检查
- `Paper launch queue` 前排对象都已有正式 Rank；`Rank 422` 已完成接线并写入 `connected_runner_live`
- `Fresh intake slot = Rank 423`
- `Surviving candidate slot = Rank 423`
- `Active P2 = none`
- 当前前排对象不存在无 rank 情况，本轮无需补号。

## 排班判断
- 当前没有新的 `P3 launch wiring` 待办，也没有 `Active P2` 需要出口决策。
- 因此本轮最高优先级的真实动作就是 **`Rank 423` 的 survivor 唯一 follow-up**；它必须先被诚实消费掉，不能让新 intake 插队。
- 在 survivor 之后，才轮到新的 `fresh intake`。
- 结合最近 digest 质量与 policy 的“前排先收口，再补 intake”顺序，本轮采用：
  1. `Rank 423` survivor 唯一 follow-up（entry realism / delay）
  2. `2026-04-19_0112_cointegration-spreadfade-router-alpha.md` fresh intake
  3. `2026-04-19_0016_intraday-extreme-return-router-alpha.md` fresh intake
  4. `2026-04-18_2328_crypto-retail-chasing-continuation-alpha.md` conditional fresh intake

## P2 -> P3 兜底裁判检查
- 本轮无需再触发新的 `P2 -> P3` 兜底改写。
- 原因：最近唯一接近出口的对象 `Rank 422` 已经被 bot2 正式推进并完成到 `connected_runner_live`；当前不存在“明明已够格进入 paper trade，但 bot3 尚未升级”的 active P2 悬案。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`，本轮 `cycle_plan` 重排为：
1. `Rank 423`：survivor 唯一 follow-up（entry realism / delay，直接回答 `P2 / P0` 出口）
2. `2026-04-19_0112_cointegration-spreadfade-router-alpha.md`：fresh intake 最小首判（双腿 friction ladder + pair concentration）
3. `2026-04-19_0016_intraday-extreme-return-router-alpha.md`：fresh intake 最小首判（jump/event veto + 5m child execution）
4. `2026-04-18_2328_crypto-retail-chasing-continuation-alpha.md`：conditional fresh intake（plain momentum horse-race）

新计划满足：
- `P3 / P2` 无真实待办时，先诚实消耗 survivor，再补 fresh intake
- 没有把 background pool 旧对象重新拉回前排
- 没有让新的 `keep_P1` 覆盖 `Rank 423` 的 survivor 锁定槽位
- 每项都只含 `target / action / success_criterion / result / status`
- 新生成项 `result = none`、`status = pending`

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-19_0132_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - command: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（独立执行，不与 publish 链式拼接）：
   - command: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank423先决出口 再切回新intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-19_0132_strategy-review.md`
