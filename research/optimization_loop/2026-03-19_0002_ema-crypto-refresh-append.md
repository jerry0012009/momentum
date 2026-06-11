# 2026-03-19 00:02 UTC｜EMA Crypto due-now 续写

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Run 1 / EMA due-check only` 执行。
- 本轮 wall-clock 正好撞上 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC` 的真实 close 窗口；这不是 `waiting_not_due`，而是应先消化的真实 `Paper Seat` 动作。
- 因此本轮没有转去 Scout；主点就是把这笔 crypto paper refresh 如实续写，并把 desk 状态同步到最新。

## 做了什么改动
1. 实际执行：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 结果：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv` 新增 `1` 条 completed-bar row；累计从 `17` 增至 `18`。
   - `Crypto 1d+1wk（BTC/ETH/SOL）` 续写到 `latest_completed_bar_utc=2026-03-18 00:00 UTC`。
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 更新后显示：
     - A 股三条 lane -> `2026-03-19 07:00 UTC`
     - 美股 `1d+1wk` -> `2026-03-19 20:00 UTC`
     - Crypto `1d+1wk` -> `2026-03-20 00:00 UTC`
   - `reports/site/factors/ema_psar_raw_alpha/report.html` 已随 refresh 链重建。
3. 最小同步写回：
   - 更新 `docs/TODO.md` 的 `Paper Seat` 最新补充
   - 更新 `docs/TODO.md` 的 `Next 3 bot3 runs` 顶部说明，避免下一轮还按旧的 `Crypto due_soon -> 2026-03-19 00:00 UTC` 读法误判。

## 验证 / 证据
- `ema_paper_trading_refresh_history.csv` 末行已出现：
  - `history_recorded_at_utc=2026-03-19 00:02 UTC`
  - `deployment_scope=Crypto 1d+1wk（BTC/ETH/SOL）`
  - `latest_completed_bar_utc=2026-03-18 00:00 UTC`
  - `monitor_status=refresh_green_backstop_live`
  - `review_action=keep_secondary_backstop`
- 最新 due guardrail 已无 `due-now / overdue` lane；最靠前的是 A 股下一次 `2026-03-19 07:00 UTC`。
- `manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，说明当前没有新的 `P3` 托管位状态变化需要抢回 continuity。
- `run_ema_paper_trading_guarded_refresh.py --require-due` 本次虽然以 code `2` 结束，但从产物看它已先完成真实 due refresh，并在收尾阶段如实给出“当前已无 due-now / overdue lane、后续应等待下一根 completed bar”的 guard 提示；本轮按产物与 guardrail 结果记为成功消化 due window，而不是失败空转。

## 风险 / 边界
- 这轮只处理了 `Run 1 / Paper Seat` 的真实 due-now 动作，没有顺带展开 Scout。
- `require-due` 的退出码表现仍有点别扭：它在真实 append 完成后仍返回非零。当前不影响本轮 desk 判断，但后续若反复出现，可单独做一次脚本退出码语义清理。
- 工作区仍有大量与本轮无关的脏文件；本轮未尝试提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 重新处于 `waiting_not_due`，按顶板恢复：
  1. fresh source intake（优先比较 `realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate`）
  2. 若新 source guard-passed，则给它 `1` 次最小 clean replication
  3. 只有 fresh source 也 exhausted，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`
- 到 `2026-03-19 07:00 UTC` 左右，再优先检查 A 股三条 lane 是否进入新的 due-now 窗口。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合做安全 selective commit。
