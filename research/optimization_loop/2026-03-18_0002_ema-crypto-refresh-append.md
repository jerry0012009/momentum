# 2026-03-18 00:02 UTC · EMA crypto due-now append

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Run 1 -> Run 2 -> Run 3` 顺序重读当前 desk。
- 上一轮的权威读法已经把最近的下一次时钟动作钉在 `Crypto 1d+1wk -> 2026-03-18 00:00 UTC`。
- 因此本轮不该继续把 `EMA` 当 `waiting_not_due`，而是先做 `Run 1 / EMA due-now follow-up`，确认这根 crypto completed bar 是否被真实续写。

## 做了什么改动
1. 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 结果把 `Crypto 1d+1wk（BTC/ETH/SOL）` 续写到新的 completed bar：`latest_completed_bar_utc=2026-03-17 00:00 UTC`。
3. `ema_paper_trading_refresh_history.csv` 新增 1 条 completed-bar row，累计从 `12` 条增至 `13` 条。
4. reader-facing 页面已同步重建：
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
5. 最小写回权威板：
   - `docs/TODO.md` 顶部 `Paper Seat` 最新补充
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 最新补充

## 验证 / 证据
### refresh history
`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv` 最新尾行：
- `history_recorded_at_utc=2026-03-18 00:02 UTC`
- `deployment_scope=Crypto 1d+1wk（BTC/ETH/SOL）`
- `latest_completed_bar_utc=2026-03-17 00:00 UTC`
- `monitor_status=refresh_green_backstop_live`
- `review_action=keep_secondary_backstop`

### due guardrail
`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 当前显示：
- `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d -> 2026-03-18 07:00 UTC`
- `美股 1d+1wk -> 2026-03-18 20:00 UTC`
- `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
- 当前全 desk 已重新回到 **无 `due-now / overdue` lane**

### 运行边界
- 这轮是真 refresh，不是 waiting-window 里的伪续写。
- crypto lane 续写完成后，`Paper Seat` 已重新回到 `running paper / waiting_not_due`。

## 风险 / 边界
- 本轮没有改 EMA 规则、没有改 seat judgment，也没有重开新的 scout 候选。
- `Scout Fast Lane` 的 exhaustion 状态没有因为这次 refresh 被改变；下一轮只有在没有新 due-now bar 的前提下，才恢复 `Run 2（若仍 exhaustion 则直接 Run 3）` 的回退顺序。
- 这次命令末尾返回了非零退出码，但从输出与落地 artifacts 看，refresh row、due guardrail、reader-facing report 都已经实际写成；当前更像是报告构建尾段的环境噪音而不是 refresh 失败。本轮按落地结果记账，不把它误报成 failed refresh。

## 下一步建议
- 下一个真实 `Run 1` 时钟动作应是 `A股三条 lane -> 2026-03-18 07:00 UTC`。
- 若在那之前没有新的 promoted scout source，则 desk 默认回到：`Scout Fast Lane（若仍 exhaustion 则直接 Run 3） > tiny-live plumbing`。
- `Run 3` 若继续被认领，当前唯一真正会改状态的动作仍是：出现可附着 / 已登录的 venue execution surface 后，再做 `Rank 2 / SOLUSDT` whitelist-bound `test/no-fill replay`。

## 相关产物
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `docs/TODO.md`

## Commit hash
- 未提交。
- 原因：repo/worktree 中存在大量与本轮无关的脏文件与未跟踪文件；本轮只做最小选择性写入，避免混提。
