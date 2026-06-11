# 2026-04-18 22:10 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`
- Recent optimization loop:
  - `2026-04-18_2205_rank422_us_session_twowindow_drift_freshintake_keep_p1.md`
  - `2026-04-18_2120_stablecoin_crossvenue_gap_freshintake_background_p0_fee_size_duration.md`
  - `2026-04-18_1955_rank421_survivor_followup_background_p0_depth_fee_lifetime.md`
  - `2026-04-18_1900_rank421_triangular_crossrate_freshintake_keep_p1_lowfee_execution_axis.md`
- Recent strategy review:
  - `2026-04-18_2032_strategy-review.md`
  - `2026-04-18_1904_strategy-review.md`
  - `2026-04-18_1818_strategy-review.md`
- Fresh materials checked for rewrite:
  - `research/quant_digests/2026-04-18_1845_intraday-max-lottery-fade-alpha.md`
  - `research/quant_digests/2026-04-18_1932_option-box-financing-dislocation-alpha.md`
  - `research/quant_digests/2026-04-18_2150_sar-slippage-risk-overlay.md`
  - `research/quant_digests/2026-04-18_0940_us-session-twowindow-drift-alpha.md`
  - `research/optimization_loop/2026-04-18_2205_rank422_us_session_twowindow_drift_freshintake_keep_p1.md`

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否。**
   - `current_target = none`；`connected_runner_live` 里列出的对象都已完成 runner + scheduler + first verified run，不存在待补 wiring 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 422 / 21:00–23:00 UTC fixed-window drift` 已经完成 fresh intake，当前 fresh 槽位的最新结论仍是 `keep_P1`。**
   - 它已获得正式 `Rank 422`，并且当前 survivor 也必须还是它；不能拿新的 `keep_P1` 覆盖这条唯一 survivor 槽位。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得。**
   - `Rank 422` 的首判已经把对象收敛成一个清楚的 `time-of-day raw alpha`：`21:00–23:00 UTC` 窗口在公开 `15m` majors basket 上，`4/8/12bps` 后仍保留 `+8.90/+4.90/+0.90bps/day`，且相邻窗口形成连续强簇，不是单点巧合。按 policy，这种 `keep_P1` 应优先吃掉 survivor 唯一 follow-up，而不是被新的 fresh intake 顶掉。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 仍是 `Rank 417`，但早已完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象里，`Rank 422` 已有正式 rank。
- `Paper launch queue = none`、`Active P2 = none`。
- 没有前排对象缺 rank，因此本轮无需补新 rank。

## 排班判断
- 当前不存在可执行的 `P3` 或 `Active P2` 动作。
- 但存在一个**明确且优先级更高**的 `P1 survivor` 动作：`Rank 422` 的唯一 follow-up 还没用掉。
- 按 policy，已有前排对象的诚实收口必须排在新的 fresh intake 前面；因此本轮 `cycle_plan` 必须把 `Rank 422` survivor follow-up 放在第 1 位。
- 只有把 survivor 动作诚实排进前部之后，剩余预算才补新的具体 fresh intake。
- 结合最近 digest，可补的三个具体对象是：
  1. `intraday MAX / lottery-demand fade`：raw alpha 清楚，但当前 major-perp portability 很薄，适合做最小 `universe breadth / cost realism` 首判。
  2. `box implied financing dislocation`：relative-value 主语清楚，但当前公开快检已高度暗示 `contract-spec + four-leg execution realism` 是唯一最小 blocker。
  3. `SaR slippage-risk overlay`：很像 shared overlay 而不是独立 front object，适合用一轮最小 distinctness 检查直接判断是否应 `background/P0`。
- 已判完的 `stablecoin cross-venue gap shell` 不应继续留在当前轮 `cycle_plan`，否则会形成“已完成对象占前排”的假 pending。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- 也没有 desk review 已清楚表明“足够值得 paper trade / paper launch，但 bot3 未升”的对象。
- 结论：**本轮无需执行** bot2 的 `P2 -> P3` 兜底直升。

## State rewrite
已写回 `docs/BOT2_BOT3_STATE.md`，本轮 `cycle_plan` 重排为：
1. `Rank 422 / 21:00–23:00 UTC fixed-window drift` survivor follow-up
2. `research/quant_digests/2026-04-18_1845_intraday-max-lottery-fade-alpha.md`
3. `research/quant_digests/2026-04-18_1932_option-box-financing-dislocation-alpha.md`
4. `research/quant_digests/2026-04-18_2150_sar-slippage-risk-overlay.md`

新计划满足：
- survivor 在前，新 fresh intake 在后
- 每项只保留 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_2210_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（与 publish 独立执行，无论 publish 成败都继续尝试）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank422 survivor 置顶并补三条 fresh intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_2210_strategy-review.md`
