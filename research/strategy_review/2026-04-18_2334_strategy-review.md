# 2026-04-18 23:34 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`
- Recent optimization loop:
  - `2026-04-18_2254_rank422_survivor_followup_promote_p2_basket_childentry.md`
  - `2026-04-18_2205_rank422_us_session_twowindow_drift_freshintake_keep_p1.md`
  - `2026-04-18_2120_stablecoin_crossvenue_gap_freshintake_background_p0_fee_size_duration.md`
  - `2026-04-18_1955_rank421_survivor_followup_background_p0_depth_fee_lifetime.md`
  - `2026-04-18_1900_rank421_triangular_crossrate_freshintake_keep_p1_lowfee_execution_axis.md`
- Recent strategy review:
  - `2026-04-18_2210_strategy-review.md`
  - `2026-04-18_2032_strategy-review.md`
  - `2026-04-18_1904_strategy-review.md`
- Fresh materials checked for rewrite:
  - `research/quant_digests/2026-04-18_2238_liqshock-oiunwind-exhaustionfade-alpha.md`
  - `research/quant_digests/2026-04-18_1932_option-box-financing-dislocation-alpha.md`
  - `research/quant_digests/2026-04-18_2150_sar-slippage-risk-overlay.md`
  - `research/quant_digests/2026-04-18_1845_intraday-max-lottery-fade-alpha.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否。**
   - `current_target = none`；`connected_runner_live` 里的对象都已经是已接线完成的 live runner，不存在待补 wiring 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**当前运行态 fresh slot 为空；上一条完成的 fresh intake 是 `Rank 422 / 21:00–23:00 UTC fixed-window drift`，且它已不再停留在 fresh slot。**
   - 它已经走完 `fresh intake -> survivor -> promote_P2`，所以本轮不能再把它按 fresh 对待。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，而且已经用掉并产生层级变化。**
   - `2026-04-18_2254_rank422_survivor_followup_promote_p2_basket_childentry.md` 已明确给出：剔除弱币 `XRP` 后的 `EW5(BTC/ETH/SOL/BNB/DOGE)` 在 `21:15 delay-one-bar` 下仍有 `gross≈+13.55bps/day / net8≈+5.55bps/day`，因此 survivor 唯一 follow-up 不是浪费，而是直接把对象推进到了 `P2`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**有，`Active P2 = Rank 422 / 21:00–23:00 UTC fixed-window drift`，而且它当前离 `P3` 最近。**
   - 原因不是“研究已经完美”，而是它已经跨过了 fresh/survivor 便宜检查，留下来的主要问题只剩 `time stability / cross-asset stability / honesty-execution realism` 的正式 admission 收口；从当前证据看，更像在确认是否有单一 decisive blocker，而不是更像要退回 `P1/P0`。

## Rank 合规检查
- `Paper launch queue = none`
- `Fresh intake slot = none`
- `Surviving candidate slot = none`
- `Active P2 = Rank 422`
- 当前前排对象均带正式 `Rank`，本轮无需补号。

## 排班判断
- 当前存在真实且优先级最高的前排动作：`Rank 422` 的 `Active P2` admission / exit 决策。
- 按 policy，已有前排对象的收口优先级高于新 intake，因此本轮必须先把 `Rank 422` 放到 `cycle_plan` 前两项，且都围绕出口决策而不是继续抽象“再补一点证据”。
- 同时，`Rank 422` 上一轮 evidence axis 是 `basket admission + delay-one-bar child entry`；本轮不能沿同一 axis 低杠杆重复，因此改切到：
  1. `time stability / cross-asset stability`
  2. `honesty / execution realism` 的唯一 decisive blocker
- 在前排动作被诚实排入后，剩余预算再补具体 fresh intake：
  1. `liqshock-oiunwind-exhaustionfade-alpha`（更新、更像 raw alpha、且有完整事件驱动壳）
  2. `option-box-financing-dislocation-alpha`（清楚的 relative-value 主语，但高度怀疑 maker-first / contract-spec realism 是唯一 blocker）
- 之前还挂在旧 plan 里的 `SaR overlay` 与 `intraday MAX fade` 不再比 `Rank 422` 的 P2 出口和更新的 `liqshock` 更优先，因此本轮先退出前四项。

## P2 -> P3 兜底裁判检查
- 本轮存在明确 `Active P2`：`Rank 422`。
- 但当前证据尚不足以让我在 desk review 这一步就直接把它写入 `P3 / Paper launch queue`：
  - 已知强项：`EW5` + `21:15 delay-one-bar` 仍保留正 after-cost 边际，说明不是单一 timestamp 幻觉。
  - 仍未闭合项：`time stability / cross-asset stability / fixed scheduler honesty` 还没被写成正式 admission 结论。
- 因此本轮**不直接越级写 P3**；但已经明确把它排成 **P2 出口决策优先轮**，而不是继续开放式研究。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`，本轮 `cycle_plan` 重排为：
1. `Rank 422 / 21:00–23:00 UTC fixed-window drift`：P2 admission 主结论轮（`time stability / cross-asset stability`）
2. `Rank 422 / 21:00–23:00 UTC fixed-window drift`：P2 出口最小 honesty / execution realism blocker
3. `research/quant_digests/2026-04-18_2238_liqshock-oiunwind-exhaustionfade-alpha.md`
4. `research/quant_digests/2026-04-18_1932_option-box-financing-dislocation-alpha.md`

新计划满足：
- 前排 `Active P2` 收口优先于新的 fresh intake
- 前两项都是真推进动作，且直接面向 `P3 / P1 / P0` 出口
- 新生成项只含 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_2334_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
   - outcome: non-blocking tail failure，进程以 `SIGKILL` 结束；未回滚本轮 state / log。
2. 中文邮件摘要（与 publish 独立执行，无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank422 进入 P2 出口决策轮" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_2334_strategy-review.md`
   - outcome: sent to default recipient `18810813576@163.com`。
