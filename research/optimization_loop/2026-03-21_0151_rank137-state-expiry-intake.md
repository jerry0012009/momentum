# 2026-03-21 01:51 UTC — Rank 137 / state expiry latency budget gate intake

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，所以本轮主动作切去 **Scout Seat fresh intake**。比较当前 active Scout 的边际价值后，正式认领 **`Rank 137 / state expiry latency budget gate`**，并把它放进下一轮最小 clean replication 队列。

## 先检查了什么
- `git status --short`：repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：当前没有 `due-now / overdue` lane
  - 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 `22.1h` 后到点
  - 说明：`require-due` 下 `exit code 2` 代表“还没到点，不做伪 refresh”，不是故障。

## 为什么这轮认领 fresh intake，而不是回旧 P1
当前 authoritative 顶板写的是：
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，则执行 fresh intake next`
3. `Run 3 = 若新的 fresh intake guard-pass：只给它 1 次最小 clean replication`

因此先比较当前 active Scout：
- `Rank 127 / signal→confirm ATR delta phase gate`
  - 已是 `P1 / budget used / evidence_pool`；继续磨它的边际价值不高。
- `Rank 125 / range location veto gate`
  - 已完成 1 次真正会改变 verdict 的最小检查，当前继续追加的优先级低于 fresh intake。
- `Rank 112 / basis dislocation short veto`
  - 同样是 `budget used / evidence_pool`，更像旧证据池，不是本轮最优主资源位。
- `Rank 111 / abnormal-return event clock`
  - 也是旧 `P1`，继续磨它不如认领一条新的、明确贴三条主线的候选。
- `fixed partial -> R/ATR partial`
  - 有价值，但角色更像 `tiny-live plumbing / path-management fallback`，按当前 desk 不该抢 Scout 主位。

**结论：** 本轮最该认领的是新的 repo-based 15m 候选，而 01:45 这条 `state expiry latency budget gate` 比继续磨旧 P1 更能直接改变 desk judgment。

## 本轮主点：认领 Rank 137 / state expiry latency budget gate
来源：
- `research/quant_digests/INDEX.md`
- 对应 digest：`2026-03-21_0145_state-expiry-latency-budget-gate.md`

翻成人话：
这条线值钱，不是因为它又发明了一个指标，而是因为它把当前三条主线共同的一个漏洞讲清楚了：
**确认层如果可以无限等，就会把已经过期的 follow-up 也混进同一类 continuation 样本。**

它直接服务三条主线：
- `breakout_short`：把“破位后拖很久才确认”的 stale continuation 剔出去；
- `Fib retest_hold`：把“回踩永不过期”的偷懒口径改成有时间预算的诚实口径；
- `EMA / PSAR`：先不改 trigger，本轮只补一个更便宜、更可审计的 post-trigger honesty gate。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on：** 冻结既有 `breakout_short / fib_retest_hold / ema_psar_long` 触发，只给 post-trigger 链路增加双时窗 expiry：
  - `confirmWindow` 到期即作废
  - `confirm -> entryWindow` 再到期也作废
- **trade off：** 它不是新主策略，不是 tiny-live path-management，也不是为了“解释更漂亮”；如果 clean replication 只是靠大砍交易数，或只在单一 pocket 有效，就直接 `park`。

### 2) no lookahead / repaint / data leakage
- 所有时窗只允许使用 signal / confirm 时点之前已经完成的 bar 状态；
- 执行统一 `next-bar open + no-overlap`；
- 不允许用 future path、最终 outcome、或事后最优 window 去回填 expiry 逻辑。

**本轮 hard verdict：`guard-passed / admit_to_clean_replication_queue`。**

## 本轮新增产物
- `reports/artifacts/literature/scout_rank137_state_expiry_latency_budget_source_intake_card.csv`
- `research/optimization_loop/2026-03-21_0151_rank137-state-expiry-intake.md`

## 对 desk board 的最小 write-back
- `Scout Seat 当前主点`：改成 **`Rank 137 / state expiry latency budget gate`**。
- `Active Scout 排序`：将 `Rank 137` 置顶为 `P1 / source intake done / guard-passed`。
- `Next 3 runs`：
  - `Run 2` 改为：若 EMA 仍 `waiting_not_due`，执行 `Rank 137` 的 1 次最小 clean replication；
  - `Run 3` 改为：若 `Rank 137` hard-fail / exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback。
- `最近关键 evidence`：补入本轮 `EMA waiting_not_due` 守门与 `Rank 137 fresh intake` 结论。

## 下一轮最小动作建议
若下一轮 `EMA` 仍非 due-now：
- 只给 `Rank 137` **1 次最小 clean replication**；
- 对照三臂：
  - `A = 无 expiry`
  - `B = 仅 confirmWindow`
  - `C = confirmWindow + entryWindow`
- 固定 `BTC/ETH/SOL perpetual`、`15m`、`next-bar open`、`no-overlap`、成本 `6/10/15 bps`；
- 主看：`post_cost_expectancy`、`failure_rate`、`trade_count_retention`、`time-to-confirm/time-to-entry` 分布。

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

## 风险 / 边界
- 这轮还只是 intake，不是假装已经完成 replication；
- 但它已经足够作为新的 Scout 主点，因为当前缺的不是又一个更花的过滤器，而是**确认层的时间预算 honesty**；
- 如果下一轮 replication 证明它只是靠极端砍单变好，就应该很快 `park`，不要继续磨文案。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部 intake card、run log 与顶板 write-back，不适合混提。
