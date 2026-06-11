# EMA 美股 due 窗口已消化，桌面回到 crypto due-soon

## 为什么这次选这个
- 当前轮次先按 `TRADING DESK BOARD` 的 `Run 1 -> Run 2 -> Run 3` 执行。
- 本轮 wall-clock 已到 `2026-03-18 20:00 UTC`，而上一轮顶板里 `美股 1d+1wk` 的下一次 close 正好是 `2026-03-18 20:00 UTC`，因此最诚实的动作不再是继续 Scout，而是先做一次真实 `EMA due-check / guarded refresh`。
- 同时 `manual_narrow_paper_last_run_summary.json` 最新一次仍为 `new_closed_trades_appended=0`，说明没有新的 `P3 narrow paper` 状态变化值得抢主资源。

## 这轮做了什么
1. 先检查了 repo 状态、最近 optimization logs、最新 due guardrail 与 narrow-paper 托管状态。
2. 实际执行：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
3. 刷新完成后，把 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 最小回写到 `2026-03-18 20:02 UTC` 的真实状态。

## 验证 / 证据
### 1) 真实 paper refresh 已发生，不是空转
脚本输出里的关键信号：
- `ema_paper_trading_refresh_history.csv` **追加 2 条新 completed-bar rows**（累计 `17` 条）
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已重新生成

### 2) 本轮实际消化了 20:00 UTC 的 due window
刷新后 `ema_paper_trading_refresh_history.csv` 新增：
- `美股 1d+1wk（SPY/QQQ/AAPL）` -> `latest_completed_bar_utc=2026-03-18 00:00 UTC`
- `贵州茅台 1d+1wk` -> `latest_completed_bar_utc=2026-03-18 00:00 UTC`

这说明本轮不是“`require-due` 发现没到点就退出”，而是先真实续写了 due-now lane；脚本末尾再次打印“当前没有 due-now / overdue lane”时，含义是 **本轮已经把 due-now 窗口消化完了**。

### 3) 刷新后桌面重新回到 no-due-now，但 crypto 已进入 due-soon
最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示：
- `Crypto 1d+1wk（BTC/ETH/SOL）` -> `2026-03-19 00:00 UTC`，`due_soon`，约 `4h` 后到点
- `创业板ETF 1d` -> `2026-03-19 07:00 UTC`
- `贵州茅台 1d+1wk` -> `2026-03-19 07:00 UTC`
- `沪深300ETF 1d` -> `2026-03-19 07:00 UTC`
- `美股 1d+1wk（SPY/QQQ/AAPL）` -> `2026-03-19 20:00 UTC`

### 4) `P3 continuity` 仍没有新的抢占理由
`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次：
- `run_at_utc = 2026-03-18T20:00:14Z`
- `new_closed_trades_appended = 0`

因此当前不该把 bot3 主资源拉回 `Rank 2 / 17 / 29 / 32b` 的 continuity。

## 风险 / 边界
- 这轮主要服务 `Paper Seat`，没有同时打开 `Rank 65` clean replication，遵守了“本轮最多 1 个主点 + 1 个紧邻子点”的约束。
- `run_ema_paper_trading_guarded_refresh.py --require-due` 最终返回码是 `2`，但从输出和产物看，这是“刷新完成后再次检查已无 due-now lane”的脚本收尾语义，不是本轮失败；本轮日志里已明确按产物如实记账，避免把退出码误写成失败。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮不做 commit，避免混提。

## 对当前 desk 的硬结论
**`Paper Seat / EMA` 已把 20:00 UTC 的真实 due-now 窗口消化完毕，当前重新回到 `running paper / no due-now`；但 `Crypto 1d+1wk` 已进入 `due_soon`，所以下一轮仍应先做 `Run 1 / EMA due-check only`，若仍无新的 due-now / overdue，再切到 `Rank 65` 的最小 clean replication。**

## 下一步建议
1. 下一轮先看 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC` 是否已进入真实 due-now。
2. 若仍没有新的 due-now / overdue，再按顶板顺序执行：
   - `Rank 65 / perp-stress resetComplete / re-arm gate` 的 **1 次最小 clean replication**
3. 若 `Rank 65` 也不能给出更高层 verdict，再回到 fresh source 比较：
   - `exec-TF switch alignment gate` > `regime-matrix shared-state gate`

## 提交
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，安全 selective commit 成本过高，容易混提。
