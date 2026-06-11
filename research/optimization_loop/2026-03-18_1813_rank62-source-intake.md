# 2026-03-18 18:13 UTC · Rank 62 source intake

## 本轮结论
- `Paper Seat / EMA`：继续 `running paper / waiting_not_due`
- `Live Seat`：继续 `暂空`
- `Scout Seat`：按 desk board 顺序，从已 `park` 的 `Rank 61` 切到新的 **`Rank 62 / continuation fail-fast overlay`**
- 本轮 hard verdict：**`Rank 62 / continuation fail-fast overlay = guard-passed / admit_to_clean_replication_queue`**

## 先检查了什么
- `git status --short --branch`：工作区存在大量与本轮无关的脏文件，因此本轮只做 selective write，不混提其他改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：最早到点仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`；crypto `-> 2026-03-19 00:00 UTC`；A 股 `-> 2026-03-19 07:00 UTC`。本轮没有新的 `due-now / overdue` lane。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最新 `run_at_utc=2026-03-18T17:50:41Z`，`new_closed_trades_appended=0`，不构成回头抢占 `P3 continuity` 的理由。
- `docs/TODO.md` 顶板：上一轮 `Rank 61` 已在 `17:59 UTC` 压回 `park / evidence pool`，因此当前允许动作应从 `continuation fail-fast overlay > pullback-quality / CQI` 中选 1 条主资源位。

## 为什么这轮认领 Rank 62
- 依据顶板顺序，`Rank 61` 已失效后，下一个更高边际价值的是 `continuation fail-fast overlay`，优先级高于 `pullback-quality / CQI`。
- 相比 `CQI`：
  - `continuation fail-fast overlay` 更贴当前 desk 真缺的 shared failure protocol；
  - 只补 entry 后的“何时承认走坏”，不是再开第四条 entry 框架；
  - 迁移摩擦低于 `CQI`（后者仍带 `4H/Daily long-only` 语义负担）。
- 因“进入 queue-facing 层必须先拿顺序 Rank”，本轮将其正式冻结为 **`Rank 62`**。

## 两条轻量诚实守门
### trade on / trade off
- `trade on`：base setup 继续负责方向与价位；fail-fast overlay 只回答 entry 后 continuation 是否快速失效。
- 第一轮冻结成：
  - long：`close < EMA9` 或 `close < session_VWAP` 或 `close < entry - 0.75*ATR14` 任一成立即 fail-fast exit；
  - short：完全镜像。
- `trade off`：它只能做 `breakout_short / fib_retest_hold / ema_psar_long` 的 shared failure protocol，不能单独开仓，也不能偷渡 repo 里的 A+/B discretionary 打分体系。

### lookahead / repaint / leakage
- 当前未见一眼可判死刑的 `lookahead / repaint / leakage`。
- 但必须显式冻结：
  - 所有判断都只用 signal 当根及之前可得的 entry / indicator 状态；
  - 统一执行到 `next-bar open + no-overlap`；
  - `session VWAP` 在 24/7 crypto 上只是近似代理，后续 replication 必须把这条保留意见直接写进 verdict，而不是事后忽略。

## 本轮产物
- queue-facing artifact：`reports/artifacts/literature/scout_rank62_continuation_fail_fast_source_intake_card.csv`
- reader-facing page：`reports/site/reading/repo_scout/rank62_continuation_fail_fast_source_intake.html`
- desk board 更新：`docs/TODO.md`

## 更新后的 Next 3
1. `Run 1 = EMA due-check only`
2. `Run 2 = 若 Rank 62 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
3. `Run 3 = 若 Rank 62 clean replication 后仍不能给出更高层 verdict，则转去比较 pullback-quality / CQI > Rank 35b > Rank 16b；只有这一层也 exhausted 时，才回退到 tiny-live plumbing`

## 下一轮最小许可动作
- 仅允许做 **`Rank 62 minimal clean replication`**：
  - 复用 `BTC/ETH/SOL 120d~180d 15m` cache；
  - 只比较 `base exit`、`base+any(ema_fail,atr_fail)`、`base+any(ema_fail,vwap_fail,atr_fail)` 三臂；
  - 先看 `post_cost_return@6bps`、`median_loser_size`、`false_follow_through_4bars/8bars`、`winner_truncation_rate`、`trade_count_retention`。
- 若改善主要靠 retention 崩塌、winner truncation、单一 archetype pocket，或 VWAP flip 纯属 session 任意性，则直接 `park / evidence pool`。
