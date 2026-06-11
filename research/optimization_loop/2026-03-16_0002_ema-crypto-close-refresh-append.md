# 2026-03-16 00:02 UTC｜EMA close 到点后落下首条非 seed 的连续 refresh 记录

## 为什么这次选这个
- 先看了 `docs/TODO.md`、最近两轮 loop 记录和当前 repo 状态。
- 当前 steering 明确：默认优先最接近 paper 的对象，且 EMA 线不要再补近义说明页，应该在 **真实 completed bar 到点后**继续沿同一 ledger 续写。
- 本轮刚好命中 `Crypto 1d+1wk` 的 next close 到点窗口，因此选 EMA 作为主点，做一刀 deployment-facing 的真实续写。

## 本轮主点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：把这次真实续写同步回 `docs/TODO.md` 与 plans 镜像，避免状态只留在 artifact。

## 做了什么改动
1. 到点后执行：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py`
2. 脚本先重建 EMA 报告与相关 artifacts，再对 refresh history 做 append-only 追加：
   - `ema_paper_trading_refresh_history.csv` 新增 `1` 条 completed-bar 记录，累计从 `5` 条变为 `6` 条。
   - 新增键为：`Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-15 00:00 UTC`。
3. 同步回写 `docs/TODO.md`（line-305 子条目）：
   - 新增 `2026-03-16 00:01 UTC` 最新补充，明确这次已经出现首个非 seed 的连续续写证据；
   - 同时保持该父任务未勾完成（`[ ]`），因为 A股三条 lane 还没到下一次 close，week-1 review 也未到期。
4. 重建 plans 镜像：
   - `python3 scripts/build_plans_site.py`

## 验证 / 证据
- 运行输出确认：
  - `已向 ema_paper_trading_refresh_history.csv 追加 1 条新 completed-bar rows（累计 6 条）`。
- 文件核对：
  - `tail reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv` 可见新增 `Crypto-1d | 2026-03-15 00:00 UTC` 行；
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv` 当前 `Crypto 1d+1wk` 的 `latest_completed_bar_utc` 已到 `2026-03-15 00:00 UTC`。
- 守门状态核对：
  - 当前无 `due-now / overdue`；
  - `创业板ETF / 贵州茅台 / 沪深300ETF` 下一次 close 约 `7h` 后，仍属 `waiting_not_due`。
- 网页可见性：
  - `reports/site/plans/momentum_todo.html` 已同步出现 `2026-03-16 00:01 UTC` 的新增补充。

## 风险 / 边界
- 这轮推进只新增了 `Crypto-1d` 一条真实 completed-bar 续写，不代表整个 EMA ledger 已进入全量连续刷新。
- `week-1 review` 仍未到期，不能提前写 yellow/red verdict。
- 因此 line-305 仍保持未完成，下一刀应在 A股 next close 到点后继续追加，而不是回头补近义文案。

## 执行层 hygiene
- `git status --short` 显示 worktree 存在大量与本轮无关的既有脏改/未跟踪文件；本轮仅做 EMA ledger 续写与 TODO/plans 同步，不混提无关改动。
- 本轮有一次 shell 检索命令因反引号触发子命令提示（`command not found`），已改用保守读法继续核对，不影响主任务完成。

## Commit hash
- HEAD：`f09a838`
- 本轮未提交。

## 未提交原因
- 当前工作区存在大量与本轮无关的历史脏改和未跟踪产物；在此状态下做 selective commit 风险高，故本轮保持未提交。