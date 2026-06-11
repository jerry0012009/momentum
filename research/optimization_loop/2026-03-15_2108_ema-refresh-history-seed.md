# 2026-03-15 21:08 UTC｜EMA 续跑账本补最小 continuity：把覆盖式 refresh snapshot 接成 append-only history

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、最近几轮 optimization logs。
- 当前 steering 下，`EMA baseline family` 仍是最接近 `paper trading / 伪实盘` 的对象；但真正未完成的主线不是再补近义 runbook，而是让同一张 live ledger 能继续诚实续写。
- 现在还没到下一根真实 `completed daily bar`，所以不能伪造新的 `market-close refresh / week-1 review` 结果。
- 但当前 execution 层还剩一个很实际的小缺口：`ema_paper_trading_daily_refresh_snapshot.csv` 只保留“最新覆盖式快照”，如果下一次 close 真到点，账本连续性仍会偏弱。
- 因此本轮选一个更 deployment-facing、且能在本轮完整交付的小任务：**把覆盖式 refresh snapshot 接成 append-only refresh history**，为后续真实 refresh / review 留下同一份连续账本轨迹。

## 做了什么改动
### 1) 扩展守门入口，顺手写 append-only history
修改：`scripts/run_ema_paper_trading_guarded_refresh.py`

新增逻辑：
- 读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`
- 生成去重键：
  - `deployment_scope × market_freq_book × latest_completed_bar_utc`
- 追加写入：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- 每次运行都会先判断是否已有相同 completed-bar 记录；若已有，就不重复追加。

这意味着后续真正到点时，EMA 不再只有“覆盖掉旧状态的最新快照”，而能沿同一份 append-only history ledger 累计真实 refresh / review 轨迹。

### 2) 回写 TODO，把这刀明确记成已完成的 execution 子步
更新：`docs/TODO.md`

在 EMA 那条尚未完成的主任务（继续沿 live ledger 落下下一轮真实 refresh / week-1 review）下面，新增一条 `[x]` 最新补充：
- 当前已把 `daily_refresh_snapshot` 接成 append-only `refresh_history`
- 这仍不等于未完成主任务已经收工
- 但它确实补上了“下一次真实 close 来时，账本不再只剩一张覆盖式快照”的最小连续性缺口

### 3) 刷新 plans 镜像，让站点能看到这条 execution 进展
执行：`python3 scripts/build_plans_site.py`

结果：
- `reports/site/plans/momentum_todo.html` 已同步出现这条 `refresh_history` 更新
- 这次没有重刷整份 EMA 主报告，避免在没有新 completed bar 的情况下再制造一轮近义 refresh 页面

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/run_ema_paper_trading_guarded_refresh.py`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --show-limit 2`
- `python3 scripts/build_plans_site.py`

验证结果：
- 语法检查通过。
- 守门脚本已成功写入：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- 首次 seed 成功追加 `5` 条 active `1d` lane completed-bar rows：
  - `创业板ETF 1d`
  - `美股 1d+1wk（SPY/QQQ/AAPL） / 美股-1d`
  - `Crypto 1d+1wk（BTC/ETH/SOL） / Crypto-1d`
  - `贵州茅台 1d+1wk / A股-1d`
  - `沪深300ETF 1d`
- 同一次守门输出仍显示：当前**没有** `due_now / overdue` lane；最靠前的是 `Crypto 1d+1wk`，距下一次 close 约 `3.2` 小时。也就是说，这轮确实没有伪造新的 refresh，只是把已有真实 completed-bar 状态写进了 append-only history。
- `reports/site/plans/momentum_todo.html` 已包含 `refresh_history` 这条更新，站点可见。

## 风险 / 边界
- 这不是新的 EMA alpha 证据，也不是新的 week-1 review；它只是在 execution 层把“账本连续性”补硬了一刀。
- 当前 history 去重口径是 `deployment_scope × market_freq_book × latest_completed_bar_utc`；它适合先保证“一根 bar 只进一次 history”，但还不是更复杂的 correction / amendment 体系。
- 本轮没有改写 breakout verdict；breakout 仍维持 `same-sample freeze / one_more_gate`，下次有效推进仍应来自新的 forward / shadow `pure-test/down-tail` honesty，而不是继续切旧样本。

## 下一步建议
1. 下一次真实 close 到来时，默认先跑：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 若进入 `due_now / overdue`，就在同一条链路上：
   - 先刷新 artifacts
   - 再把新的 completed-bar row 追加进 `ema_paper_trading_refresh_history.csv`
   - 然后继续判断 `keep / stricter recheck / demote / stay shadow`
3. 若仍未到点，就继续等，不伪造新的 refresh / week-1 review。

## 执行层 hygiene
- `git status --short` 显示当前 worktree 里存在大量与本轮无关的历史脏改 / 未跟踪文件；本轮没有把这些无关变动混在一起。
- 本轮直接相关的文件只有：
  - `scripts/run_ema_paper_trading_guarded_refresh.py`
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
  - `docs/TODO.md`
  - `reports/site/plans/momentum_todo.html`

## Commit hash
- HEAD：`9884685`
- 本轮未提交。

## 未提交原因
- 当前 repo 里存在大量与本轮无关的脏文件与未跟踪产物；为避免误把其他研究线或历史改动一起混提，本轮保持未提交更安全。
