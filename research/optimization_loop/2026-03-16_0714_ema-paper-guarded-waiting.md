# 2026-03-16 07:14 UTC｜EMA paper guarded refresh 回执：到点检查已执行，当前如实转回 waiting_not_due

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前 desk 状态：

- **Repo / worktree**：仓库仍有大量与本轮无关的既有脏改和未跟踪文件；本轮继续只做 selective 改动，不混提。
- **最近 runs**：`06:24 breakout hard verdict sync` 已把 Live Seat 的唯一重枪打完；`07:06 small-live reopen resume row` 已补了 tiny-live plumbing 的恢复样例。
- **Run 1 / Paper Seat**：板上明确要求 `07:00 UTC` 后第一轮先执行 `EMA paper ledger` 的 guarded refresh / append；若 data source 还没给出新 completed bar，就必须如实记成 waiting，而不是伪造 refresh。

因此这轮只认领 **Run 1 / Paper Seat continuation** 这个主点，不扩到别的席位。

## 本轮做了什么
### 1) 实际执行 EMA guarded refresh
执行：

```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

这次不是 dry-run，而是按 runbook 真跑一遍守门入口，让它重建 EMA 报告 / 审计 artifact 后再判当前是否存在 `due-now / overdue` lane。

### 2) 得到的真实结果：当前没有新的 due-now / overdue lane
脚本输出确认：

- `ema_paper_trading_refresh_history.csv` **没有新增 completed-bar rows**，仍为 `6` 条；
- `ema_paper_trading_due_guardrail_snapshot.csv` 当前最靠前 lane 已变成：
  - `美股 1d+1wk`：约 `12.8` 小时后到点；
  - `Crypto 1d+1wk`：约 `16.8` 小时后到点；
  - `创业板ETF 1d`：约 `23.8` 小时后到点；
- 对 A 股 lane 来说，下一次 close 已经被如实推到 **`2026-03-17 07:00 UTC`**，说明本轮到点检查后，当前状态应被诚实读取成 **`waiting_not_due`**，而不是继续重复 paper refresh。

### 3) 同步 reader-facing 落点
本轮把这次执行回执同步回：

- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

同步内容包括两层：
1. `Paper Seat` 最新补充增加 `2026-03-16 07:13 UTC` 的实际回执；
2. `Next 3 bot3 runs` 增加一条最新执行回执，明确说明：**Run 1 已经执行过，后续轮次默认应切回 `Run 2 -> Run 3`，不要继续重复同一轮 paper 守门。**

## 验证 / 证据
### 命令与返回
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `code 2`
  - 原因不是脚本失败，而是 `require-due` 下当前确实没有 `due-now / overdue` lane
- `python3 scripts/build_plans_site.py`
  - 成功重建 `reports/site/plans/momentum_todo.html`

### 关键 artifact 核对
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
  - 仍为 `6` 条历史 completed-bar rows，没有伪造新行
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d` 的 `next_expected_close_utc` 已是 `2026-03-17 07:00 UTC`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`
  - A 股相关 lane 当前 `refresh_clock_utc=2026-03-16 07:13 UTC`
  - `创业板ETF 1d / 沪深300ETF 1d` 当前数据源记成 `eastmoney_cache_fallback`
  - `latest_completed_bar_utc` 仍是 `2026-03-13 00:00 UTC`

### 网页可见性核对
`reports/site/plans/momentum_todo.html` 已能检索到：
- `2026-03-16 07:13 UTC`
- `2026-03-17 07:00 UTC`
- 最新 `Run 1` 执行回执

## 本轮 hard verdict
一句话结论：
**EMA 的 `07:00 UTC` 后首轮守门已经实际执行，但当前没有新的 completed daily bar 可追加，所以更诚实的 desk 读法是：Paper Seat 已完成到点检查、现已重新回到 `waiting_not_due`，后续轮次默认切回 Live / Scout / tiny-live plumbing。**

证据支持这句话的方式是：
- 守门脚本在 `--require-due` 下返回 `code 2`；
- refresh history 没有新增行；
- due guard 已把 A 股下一次 close 顺延到 `2026-03-17 07:00 UTC`。

## 风险 / 边界
- 这轮不是新的 paper refresh append，也不是新的 week-1 review；它只是把“到点后到底有没有新 completed bar”这件事用真实执行结果讲清楚。
- `eastmoney_cache_fallback` 说明当前 A 股 lane 使用的是保守缓存回退口径；它能支持诚实的 waiting 判定，但**不能**被误读成已经拿到了新的 completed bar。
- 因此后续若继续停在 Paper Seat 重复跑同一轮守门，收益会很低；默认应切到 `Run 2 / Run 3`。

## 下一步建议
1. 下一轮默认按板上顺序切回 `Run 2`：优先处理 `breakout` 的 `bench / narrower-scope / replace` 收口，而不是再做同样本 heavy rerun。
2. 若 `Run 2` 也 blocked，则继续去 `Run 3`，补 `tiny-live plumbing` 或 Scout 的更快 verdict 切片。
3. 到下一次真实 due 窗口前，不要再把同一轮 `EMA guarded refresh` 当作主点重复执行。

## Commit hash
- HEAD：`1f84291`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件；本轮只更新 `TODO`、站点 plans 镜像与运行日志，继续保持未提交更安全。
