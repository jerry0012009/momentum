# EMA due-now 跟进完成，并恢复默认回退到 Scout

## 为什么这次选这个
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Next 3 bot3 runs`，当前窗口先做 `Run 1 — Paper Seat continuation`。
- 20:45 UTC 的 desk override 明确指出：`美股 1d+1wk（SPY/QQQ/AAPL）` 已经过下一次 close，但 `ema_paper_trading_refresh_history.csv` 还没出现新的 completed-bar append，因此本轮不能继续把默认主资源放在 `Scout` 或 `Rank 2 wiring`，而要先核对 `EMA due-now / overdue` 是否真实存在。

## 本轮做了什么
1. 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 这次不是空跑：脚本重建了 `reports/site/factors/ema_psar_raw_alpha/report.html`，并向 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv` 追加了 **1 条**新 completed-bar 记录。
3. 新追加的记录是：
   - `美股 1d+1wk（SPY/QQQ/AAPL）`
   - `latest_completed_bar_utc = 2026-03-16 00:00 UTC`
   - 当前状态仍是 `EMA BUY 0/3 | SELL 3/3 | HOLD 0/3`、`flat_3/3`
   - `review_action = keep_secondary_then_stricter_front_recheck`
4. 刷新后最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
   - 已经**没有** `due-now / overdue` lane
   - `Crypto 1d+1wk（BTC/ETH/SOL）` 变成最靠前的 `due_soon`（距下一次 close 约 `3.1` 小时）
   - A 股几条 lane 仍是 `waiting_not_due`
5. 对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小同步：
   - 把 20:45 UTC 的临时 `Run 1 first` override 收口为 20:52 UTC 最新状态
   - 明确写成：**本次 Run 1 已完成；从下一轮起默认恢复 `Run 2 / Scout Fast Lane first`**

## 验证 / 证据
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
  - 累计行数从 `6` 增到 `7`
  - 最新一行是 `2026-03-16 20:52 UTC` 记录的 `美股 1d+1wk（SPY/QQQ/AAPL） | 美股-1d | 2026-03-16 00:00 UTC`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 最新最靠前 lane 为 `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 3.1 小时 后到点`
  - 当前已无 `due-now / overdue` lane
- `reports/site/factors/ema_psar_raw_alpha/report.html`
  - 已随本轮 refresh 重建，可作为 reader-facing 可见落点
- 终端返回：
  - `[ema-refresh-history] 已向 ema_paper_trading_refresh_history.csv 追加 1 条新 completed-bar rows（累计 7 条）。`
  - `[ema-refresh-guard] 当前没有 due-now / overdue lane。`

## 结论
- 本轮 `Run 1` 的 hard verdict：**已完成当前应做的 EMA due follow-up，不应继续重复“美股是否漏补账”的同类检查。**
- 最新 desk 读法：`Paper Seat` 重新回到 `waiting_not_due / due_soon`；下一轮默认应该把主资源切回 **`Scout Seat`**，而不是继续停在 `Paper Seat` 空转。

## 风险 / 边界
- 这次新增 completed-bar 只解决了 `美股 1d+1wk` 的本轮 overdue 风险；并不改变 `EMA` 的总体 seat judgment。
- `Crypto 1d+1wk` 已进入 `due_soon`，后续若 close 已过但没有 append，需要重新临时切回 `Run 1`。
- A 股 lane 本轮仍有 `eastmoney_cache_fallback`，但当前没有伪造新 completed bar；这里只是如实维持 waiting 状态。
- 仓库里存在大量与本轮无关的脏文件，因此本轮**不做混提 commit**。

## 下一步建议
1. 下一轮默认按 `Run 2 / Scout Fast Lane` 执行，先比较 active Scout 候选的边际价值。
2. 若继续认领 `Rank 2 combo_all`，只允许做 `paper ledger / monitoring / refresh / review` 的最小接线，或一个真正会改变 paper verdict 的最小检查；不要再补 receipt / closeout 近义卡。
3. 若后续 wall-clock 进入 `Crypto 1d+1wk` 的 close 后窗口，再临时切回 `Run 1` 做 due-now follow-up。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的历史脏文件与未跟踪产物；本轮只做局部续写与指挥板同步，暂不安全做 selective commit。
