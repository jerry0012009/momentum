# 2026-03-19 08:26 UTC · Rank 83 成本稳定性检查后压回 park

## 为什么这次选这个
- 先按 `Run 1 / EMA due-check only` 实跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果仍是 `waiting_not_due`：全 desk 无 `due-now / overdue`，最近 due 点是 `美股 1d+1wk -> 2026-03-19 20:00 UTC`。
- 顶板在 `08:05 UTC` 已把 `Rank 83 / Fib trend-strength admission layer` 做完最小 clean replication，并明确把下一手收紧成：**只允许给它 1 个 truly verdict-changing 的最小检查**，否则切去 `Rank 85` fresh intake。
- 按 `P1` 纪律，这条线不能继续靠 wording / writeback 续命；本轮最有边际价值的诚实检查是 **成本稳定性**，因为它直接回答：这条 strength admission layer 是真有 desk 级 survivability，还是只在低 friction 下看起来更好。

## 本轮认领
- 主点：`Rank 83 / Fib trend-strength admission layer` 的 1 次 truly verdict-changing 最小检查（`cost stability`）
- 紧邻子点：把 hard verdict 写回 `docs/TODO.md`，并补 reader-facing / factor 页面落点

## 做了什么改动
1. 继续按 `Run 1` 做 due-check：
   - 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 结论：`EMA = running paper / waiting_not_due`，本轮不得伪造 refresh，也不得把整桌误判成等待。
2. 新增脚本：`scripts/build_rank83_fib_trend_strength_cost_stability_check.py`
   - 不重跑上一轮 clean replication。
   - 直接复用 `reports/artifacts/scout_rank83_fib_trend_strength_15m/overall_summary.csv` 与 `asset_summary.csv` 已落地的 `6 / 10 / 15bps per side` 结果，专门做一次成本梯度检查。
3. 新增 / 更新 artifact：
   - `reports/artifacts/scout_rank83_fib_trend_strength_15m/cost_stability_summary.csv`
   - `reports/artifacts/scout_rank83_fib_trend_strength_15m/cost_stability_asset_summary.csv`
   - `reports/artifacts/scout_rank83_fib_trend_strength_15m/cost_stability_meta.csv`
4. 新增网页可见落点：
   - `reports/site/factors/scout_rank83_fib_trend_strength_15m/cost_stability_check.html`
   - `reports/site/reading/repo_scout/rank83_fib_trend_strength_cost_stability_check.html`
5. 最小 writeback：
   - 在 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 下追加本轮 note，明确把 `Rank 83` 从 `keep_P1 / evidence_pool` 收口为 **`park / evidence_pool`**，并把后续排班切到 `Rank 85 -> Rank 84`。

## 验证 / 证据
### 1) Run 1 / EMA due-check
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 返回：无 `due-now / overdue` lane；最近 due 点仍是 `美股 1d+1wk（SPY/QQQ/AAPL） -> 约 11.6h`。
- 这说明本轮合法主动作确实应落在 `Scout Seat`，而不是回头补 `EMA` continuity。

### 2) Rank 83 成本稳定性（主判据）
使用上一轮 primary variant `strength_sizing` 的 desk 级结果：
- `6bps/side`：
  - `mean_total_return ≈ +1.16%`
  - `positive_asset_ratio = 3/3`
  - `mean_trades ≈ 11.0`
  - `retention ≈ 66.38%`
- `10bps/side`：
  - `mean_total_return ≈ +0.27%`
  - `positive_asset_ratio = 2/3`
  - `retention ≈ 66.38%`
- `15bps/side`：
  - `mean_total_return ≈ -0.83%`
  - `positive_asset_ratio = 0/3`
  - `retention ≈ 66.38%`

按 asset 看 `strength_sizing`：
- `6bps`：`BTC +1.46% / ETH +0.51% / SOL +1.51%`
- `10bps`：`BTC +0.57% / ETH -0.37% / SOL +0.62%`
- `15bps`：`BTC -0.54% / ETH -1.46% / SOL -0.48%`

## 硬结论（hard verdict）
**`Rank 83 / Fib trend-strength admission layer = park / evidence_pool`**

一句话：
- 这条 admission layer 的改善主要停留在**低成本区间**；
- 一旦把 friction 提到更诚实的 `15bps/side`，跨资产结果就变成 `0/3` 全部翻负；
- 对当前 `crypto 15m` desk 来说，它更像成本敏感的研究线索，而不是值得继续占用 fast-lane 预算的候选。

## 风险 / 边界
- 这次检查是 **成本稳定性**，不是完整 `Light Stability Pack`。它没有新增时间稳定性 / 参数稳定性 / 跨标的扩容之外的新样本。
- 但按当前 desk 纪律，`Rank 83` 作为 `P1` 只配 1 次便宜诚实检查；本轮目标不是把研究做满，而是做出更诚实的 **promote / park** 决策。
- 本结论不等于 `Fib retest` 整条主线无价值，只表示当前这条 **strength admission layer** 在现有 `15m crypto` friction 口径下，不值得继续占默认 Scout 主资源位。

## 下一步建议
- 按顶板更新后的顺序，下一轮默认切到：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 85 / fresh pullback → reclaim re-arm gate source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 85 guard-passed，则给它 1 次最小 clean replication；若 Rank 85 也不合格，再切 Rank 84`
- 不要继续给 `Rank 83` 补 closeout / wording / operator packet 近义页。

## Commit hash
- 未提交。
- 原因：当前 repo 工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件，当前不适合做安全 selective commit，避免混提。