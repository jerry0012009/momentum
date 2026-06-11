# 2026-03-17 00:21 UTC — EMA crypto due-now refresh resolved

## 本轮席位与认领
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 按 `2026-03-17 00:14 UTC` 的临时 override，本轮先执行 `Run 1 / Paper Seat continuation`，因为 `Crypto 1d+1wk（BTC/ETH/SOL）` 已过 `2026-03-17 00:00 UTC` close，但 ledger 还没出现新的 completed-bar append。
- 本轮只认领 1 个主点：核实并消化这次 crypto due-now / overdue follow-up；不同时打开新的 Scout 候选。

## 为什么这次选这个
- 这轮最重要的不是继续做 Scout fast intake，而是先确认 `EMA` 是否真的漏跑了 paper refresh。
- 如果 crypto lane 该补账却没补，继续跑 Scout 会让交易台主板读法失真。

## 做了什么改动
1. 实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 触发 `scripts/build_ema_psar_raw_alpha_report.py` 重建 `EMA` reader-facing report 与相关 artifacts。
3. 将新的 crypto completed-bar row 追加进：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
4. 刷新 due guardrail：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
5. 最小更新 `docs/TODO.md` 顶部指挥板：
   - 在 `Paper Seat` 下补 `2026-03-17 00:20 UTC` 最新补充
   - 将 `Next 3 bot3 runs` 当前窗口 override 从“临时切回 Run 1”恢复成“回到 Scout Seat 优先”

## 验证 / 证据
- `ema_paper_trading_refresh_history.csv` 已新增：
  - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
- `ema_paper_trading_refresh_history.csv` 累计条数：`8`
- 新增 crypto row 的关键信息：
  - `refresh_clock_utc = 2026-03-17 00:20 UTC`
  - `latest_completed_bar_utc = 2026-03-16 00:00 UTC`
  - `signal_state = EMA BUY 3/3 | SELL 0/3 | HOLD 0/3`
  - `position_state = long_open_3/3`
  - `monitor_status = refresh_green_backstop_live`
  - `review_action = keep_secondary_backstop`
- 最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
  - `Crypto 1d+1wk（BTC/ETH/SOL）` 已回到 `waiting_not_due`
  - `next_expected_close_utc = 2026-03-18 00:00 UTC`
- 脚本最终输出结论：当前已没有 `due-now / overdue` lane，应等待下一根 completed bar，而不是伪造 refresh。

## 硬结论（hard verdict）
- 这次 `Paper Seat` 的 crypto due-now 窗口**已被真实消化，不是误报也不是持续漏跑**。
- 从下一轮起，交易台默认顺序应恢复为：
  - `Scout Seat（fresh paper/repo intake first）`
  - `Rank 2 narrow-paper append/review（仅限真实 append/review need）`
  - `tiny-live plumbing`
- 当前没有理由继续把主资源卡在 `EMA due-followup` 上。

## 可部署产物 / reader-facing 落点
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`

## 风险 / 边界
- 运行过程中出现 matplotlib 中文字形缺失 warning，但不影响 CSV / HTML 产物生成，也不影响本轮 desk verdict。
- 工作区仍有大量与本轮无关的历史脏文件；本轮未提交 commit，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍是 `waiting_not_due`，默认切回 `Scout Seat`，优先做新的 `paper / repo based 5m / 15m crypto` fresh intake / clean replication。
- `Rank 2` 仅在出现真实 `append/review need` 或会改变 paper verdict 的最小检查时再继续认领。

## Commit hash
- 未提交。本轮只做选择性落盘，避免把仓库内与本轮无关的大量脏文件混进同一提交。
