# 2026-03-20 20:16 UTC — EMA 美股 due window 真实续写

## 本轮先核对的东西
- repo：`master`；`git status --short` 仍显示大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：最新已留痕是 `2026-03-20 19:57 UTC / Rank 127 clean replication -> keep_P1 / budget used`。
- `docs/TODO.md` 顶板最新 `Next 3` 明确写死：
  1. `Run 1 = EMA due-check first（美股 lane 即将 due，优先真实 refresh）`
  2. 若 EMA 再次回到 `waiting_not_due`，转去 `Rank 128 / MAX(5m) impulse confirmation tier` 的 source intake + 两条轻量诚实守门
  3. 若 `Rank 128` guard-pass 且 EMA 仍 `waiting_not_due`，才给它 1 次最小 clean replication
- hosted paper lanes：`manual_narrow_paper_last_run_summary.json @ 2026-03-20T19:45:39Z` 为 `new_closed_trades_appended=1`，但本轮仍严格遵守 `Next 3`，**不插队回头认领 P3 continuity**。

## 为什么这轮先做 EMA
这不是一般 scout 轮。
当前时间已经过了 `美股 1d+1wk -> 2026-03-20 20:00 UTC` 的真实 close，所以按 desk 规则必须先跑一次：

`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

如果这根 due-now 没被消化，就不能假装整个 desk 还在等，也不能直接跳去 `Rank 128`。

## 本轮实际执行
实际运行了：

`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

脚本输出的关键结果：
- `ema_paper_trading_refresh_history.csv` **新增 3 条 completed-bar rows**，累计增至 `25` 条；
- 其中明确包含：`美股 1d+1wk（SPY/QQQ/AAPL） -> latest_completed_bar_utc=2026-03-20 00:00 UTC`；
- 同次刷新还把 `贵州茅台 1d+1wk` 与 `沪深300ETF 1d` 一并续写到 `2026-03-20 00:00 UTC`；
- reader-facing 主报告已重建：`reports/site/factors/ema_psar_raw_alpha/report.html`。

虽然脚本最后以 exit code `2` 结束，但从产物看这不是“没跑成”，而是 **due-now 已被真实消化后，`require-due` 再次守门提示当前已回到等待下一根 completed bar**。这轮应按“真实完成 due refresh”处理，而不是按失败处理。

## 刷新后的硬证据
### refresh history 新增尾行
- `2026-03-20 20:16 UTC, 美股 1d+1wk（SPY/QQQ/AAPL）, latest_completed_bar_utc=2026-03-20 00:00 UTC`
- `2026-03-20 20:16 UTC, 贵州茅台 1d+1wk, latest_completed_bar_utc=2026-03-20 00:00 UTC`
- `2026-03-20 20:16 UTC, 沪深300ETF 1d, latest_completed_bar_utc=2026-03-20 00:00 UTC`

### 最新 due guardrail
`ema_paper_trading_due_guardrail_snapshot.csv` 现在最靠前的是：
- `Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 3.7 小时 后到点`
- `创业板ETF 1d -> waiting_not_due / 约 2.4 天 后到点`
- `贵州茅台 1d+1wk -> waiting_not_due / 约 2.4 天 后到点`
- `沪深300ETF 1d -> waiting_not_due / 约 2.4 天 后到点`
- `美股 1d+1wk（SPY/QQQ/AAPL） -> waiting_not_due / 约 3.0 天 后到点`

## 硬结论
**这轮真实完成的是 `Run 1 / EMA due-now refresh`，不是 Scout。**

翻成人话：
- 美股这根该补的 bar 已经真实补上；
- `Paper Seat` 当前不再被 due-now 卡住；
- 刷新后全 desk 又回到 **`EMA = waiting_not_due`**，其中最靠前的只剩今晚稍后的 `Crypto 1d+1wk` due-soon；
- 所以下一轮如果没有新的 due-now / overdue lane，才该按顶板切回 `Rank 128`，而不是继续磨 `Rank 127` 或回头抢 `P3 continuity`。

## 对 desk 的含义
- `Paper Seat`：`EMA / 创业板ETF 1d primary anchor / running paper` 继续成立；本轮额外真实消化了 `美股 1d+1wk` due lane。
- `Live Seat`：继续暂空。
- `Scout Seat`：主资源位不变，仍应是
  - `Rank 128 = P1 fresh intake next`
  - `Rank 127 = P1 weak candidate / budget used / evidence_pool`
  - `Rank 125 / 112 / 111 = P1 evidence_pool or budget_used`
  - `P0 park`
  - `P3 hosted continuity sidecar only`

## 本轮 reader-facing 落点
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`

## 风险 / 边界
- 本轮没有改动任何 scout 研究结论，只是如实消化了 paper due lane；
- `manual_narrow_paper_last_run_summary.json` 虽显示 `new_closed_trades_appended=1`，但按本轮 `Next 3` 不足以授权 bot3 改认领 `P3 continuity`；
- 当前美股 due 已消化，不代表今晚 `Crypto 1d+1wk` 可以提前补账；它现在只是 `due_soon`，还不是 `due-now`。

## 下一步建议
1. 下一轮先继续做 `EMA due-check first`；
2. 若仍无新的 due-now / overdue lane，则切 `Rank 128 / MAX(5m) impulse confirmation tier` 的 source intake + 两条轻量诚实守门；
3. 只有 `Rank 128` guard-pass 且 EMA 仍 waiting_not_due，才给它 1 次最小 clean replication。

## Commit hash
未提交。

原因：工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit。
