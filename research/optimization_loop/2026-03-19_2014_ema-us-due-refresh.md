# 2026-03-19 20:14 UTC — EMA 美股 due window 如实续写

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前权威顺序。
- 本轮开始时，上一轮板上顺序仍是：`Run 1 = EMA due-check only`，只有当 `EMA` 继续 `waiting_not_due` 时，才切 `Run 2 = CLV asymmetric admission layer reserve source intake`。
- 这次实际执行后，`Run 1` 没有被 waiting window 卡住，而是遇到了真实到点的美股 due window，所以本轮主点应诚实收成 **Paper Seat 的到点执行**，而不是把 `Run 1` 和 `Run 2` 混成一轮两个主点。

## 动手前检查
- 已检查 repo 状态与最近 optimization logs（沿用本轮开头的工作区检查结果；未额外扩大脏文件触碰范围）。
- 已重读 `docs/TODO.md` 顶部当前 `TRADING DESK BOARD`。
- 已核对 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最新 `run_at_utc = 2026-03-19T19:31:17Z`，`new_closed_trades_appended = 1`。

## 本轮认领
- 主点：`Run 1 / EMA due-check only`
- 紧邻子点：更新 `TRADING DESK BOARD` 的下一轮排班（不并行打开 `Rank 99` 新 intake）

## 本轮做了什么
### 1) 真实执行 Paper Seat due-check
运行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

结果不是继续 `waiting_not_due`，而是：
- `ema_paper_trading_refresh_history.csv` 新增 `2` 条 completed-bar rows（累计 `20` 条）；
- 重新生成 `reports/site/factors/ema_psar_raw_alpha/report.html`；
- refresh 完成后，guardrail 重新回到 **无 `due-now / overdue` lane**；
- 当前最近到点变成：`Crypto 1d+1wk（BTC/ETH/SOL） = due_soon / 约 3.7 小时`。

换句话说，这轮不是“检查一下然后继续等”，而是把**刚到点的美股窗口真的落账了**。

### 2) 核对 P3 sidecar，但不让它抢主资源
- `manual_narrow_paper_last_run_summary.json` 显示本日最新一次 narrow-paper 托管刷新已出现 `new_closed_trades_appended=1`。
- 但当前 append 已由托管链先行外显；本轮没有证据表明它已经变成必须立即由 bot3 抢占主资源的 desk blocker。
- 因此本轮不把它改写成新的默认 seat，只在板上记录为 **sidecar 观察项**，继续遵守 `Scout Seat > P3 continuity` 的默认优先级。

### 3) 回写下一轮排班
已更新 `docs/TODO.md` 顶部最新补充，明确：
- 本轮主点已被 `Run 1 / EMA due refresh` 消化；
- 从下一轮开始，若 `EMA` 再次回到 `waiting_not_due`，则按当前板上顺序切到 **`Rank 99 / CLV asymmetric admission layer reserve` source intake**；
- 若 `Rank 99` 守门通过，再给它 1 次最小 clean replication；若失败，再回 fresh intake。

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 脚本输出：
    - `[ema-refresh-history] 已向 ema_paper_trading_refresh_history.csv 追加 2 条新 completed-bar rows（累计 20 条）。`
    - `[ema-refresh-guard] 当前没有 due-now / overdue lane。`
    - `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 3.7 小时 后到点`
- reader-facing 落点：
  - `reports/site/factors/ema_psar_raw_alpha/report.html`
- 板面同步：
  - `docs/TODO.md` 顶部最新补充（20:14 UTC）

## 风险 / 边界
- 本轮没有并行打开 `Rank 99`，这是刻意收窄：避免在同一轮里既把 `Paper Seat` 的真实 due refresh 当主点，又顺手再认领新的 Scout 主任务，导致 desk 记录失真。
- `manual_narrow_paper` 的 `new_closed_trades_appended=1` 说明 sidecar 有新状态，但当前尚不足以推翻顶板默认顺序；若后续出现真实 status-sync 缺口，再单独认领。
- `run_ema_paper_trading_guarded_refresh.py` 退出码显示为 `2`，但从脚本正文输出看是 **require-due guard 的流程性退出**：刷新动作已真实完成、报告也已重建。本轮按实际产出记账，不把它误判成失败轮。

## 下一步建议
1. 下一轮先继续跑 `Run 1 = EMA due-check only`（优先盯 Crypto 1d+1wk 的 due_soon 窗口）。
2. 若届时 `EMA` 已回到 `waiting_not_due`，立刻执行 `Run 2 = Rank 99 / CLV asymmetric admission layer reserve source intake + 两条轻量诚实守门`。
3. 若 `Rank 99` 守门通过，再只给它 1 次最小 clean replication；否则按 7.10 回 fresh source。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件，本轮只做了最小局部回写与报告刷新，不安全混提。
