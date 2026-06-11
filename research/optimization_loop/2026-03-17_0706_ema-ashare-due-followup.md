# 2026-03-17 07:06 UTC · EMA A股 due-follow-up 已真实消化并切回 Scout 排班

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 上一轮 authoritative override 明确要求：由于 A 股下一次 close 已到 `2026-03-17 07:00 UTC`，本轮必须先执行 **`Run 1 / EMA due-now-or-just-passed follow-up`**，确认是否出现新的 `ledger / refresh` append need。
- 只有在 `Run 1` 被证明仍是 waiting-window 时，才允许切去 `Scout Seat`；本轮不能跳过这个 due check。

## 本轮主点 + 紧邻子点
- 主点：执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，如实确认 A 股 due-window 是否真的产生新的 completed-bar append。
- 紧邻子点：把最新 seat 状态与 `Next 3 bot3 runs` authoritative override 写回 `docs/TODO.md`，让下一轮自动恢复到正确的 `waiting_not_due -> Scout Seat` 顺序。

## 做了什么
1. 实际执行：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 结果不是空跑：
   - 脚本实际向 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv` **追加了 1 条新 completed-bar row**；
   - 新增行对应：`贵州茅台 1d+1wk | A股-1d | latest_completed_bar_utc=2026-03-16 00:00 UTC`；
   - `ema_paper_trading_refresh_history.csv` 累计从 `8` 条增至 **`9` 条**。
3. 脚本同时刷新了：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
4. 将最新判断最小写回到 `docs/TODO.md`：
   - 在 `Paper Seat` 下新增 `2026-03-17 07:04 UTC` 最新补充；
   - 把 `Next 3 bot3 runs` 顶部 authoritative override 改回：当前 `Paper Seat / EMA = waiting_not_due`，下一轮应先比较 `Rank 17 / Rank 2` 是否存在真实 `P3 append/review need`；若无，则优先推进 `Rank 26（P2）` 的那 1 次 genuinely verdict-changing 最小检查。

## 关键证据 / 最小验证
### 1) refresh history 新尾行
- `history_recorded_at_utc=2026-03-17 07:04 UTC`
- `deployment_scope=贵州茅台 1d+1wk`
- `latest_completed_bar_utc=2026-03-16 00:00 UTC`
- `monitor_status=refresh_yellow_mid_queue_live`
- `review_action=keep_secondary_then_recheck_mid`

### 2) 最新 due guardrail 结论
当前全 desk 已**没有** `due-now / overdue` lane：
- 最靠前的是 `美股 1d+1wk（SPY/QQQ/AAPL） -> 2026-03-17 20:00 UTC`
- 其次是 `Crypto 1d+1wk（BTC/ETH/SOL） -> 2026-03-18 00:00 UTC`
- `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d` 都已推到 `2026-03-18 07:00 UTC`

### 3) 对 desk judgment 的直接影响
- 这轮 `Run 1` 已被**真实消化**，不是 waiting-window 空转，也不是伪 refresh；
- 因此从下一轮起，`Paper Seat` 必须重新按 **`waiting_not_due`** 对待；
- bot3 主资源应恢复到 **`Scout Seat`**，而不是继续重复 A 股 due-follow-up。

## 风险 / 边界
- 本轮没有追新研究线；
- 没有打开第二个 Scout 候选；
- 没有伪造不存在的新 completed bar；
- 只做了 `Run 1` 当前唯一应该做的 due-follow-up，以及紧邻的 board 写回。

## 下一步建议
1. 下一轮先检查 `Rank 17 / Rank 2` 是否出现真实 `P3 append/review need`。
2. 若没有，默认直接推进 `Rank 26（P2）` 的 **1 次 genuinely verdict-changing 最小检查**，回答：
   - 升 `narrow paper pilot`，或
   - 压回 `park`。

## Git
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
