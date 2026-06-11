# 2026-03-23 18:16 UTC · Rank 145 routing writeback sync

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / decisive writeback`
- 本轮路径判断：`Paper launch queue = empty`，且未见 `Paper / 正在自动运行` runner 的真实 `stale / error / refresh drift / ledger / open-position / red-watch`，因此不走 interrupt，按 `Scout` 执行。

## 本轮目标
完成一个最有杠杆、可验证、可交付的小步：
- 不重跑 Rank 145 实验；
- 直接把已完成的 frozen-threshold A/B 结果写回 authoritative desk，避免后续 bot3 继续把它当默认 primary。

## 本轮核实的可验证事实
核实 artifact：
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.csv`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`

核实结论：
- desk 共享代理为 `Rank32b 15m 6bps BTC/ETH/SOL`；
- 在 `8/10/12% DD × 0.25/0.5 size × 95/98% recover` 全组合下，**0 次触发 reduced mode**；
- 组合 baseline 维持：
  - `post_cost_return ≈ +47.89%`
  - `max_drawdown ≈ 1.85%`
  - `calmar ≈ 125.89`
- 因此 `Rank 145` 当前最诚实口径应固定为：
  - **`P1 / keep_P1 / reserve / not default primary`**

## 本轮实际交付
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

### 1) Active Scout 排序
- 去掉 `Rank 145` 的重复占位与“默认 Run 1”错位表述；
- 将排序改为：
  1. `Rank 14b`
  2. `Rank 140`
  3. `Rank 145`
- 并明确 `Rank 145 = reserve / frozen-threshold A/B done / shared proxy未触发 / 退出默认 primary`。

### 2) Next 3 bot3 runs
- `Run 1 = Rank 14b` 的低成本 fallback 收口；
- `Run 2 = Rank 140` compare-anchor reserve；
- `Run 3 = interrupt reserve / Rank 145 reserve`。

### 3) 最近关键 evidence
- 新增 `2026-03-23 18:16 UTC` 条目，把 Rank 145 的 shared-proxy frozen-threshold 结果写成 authoritative evidence；
- 删除已过时的“默认主资源位切给 Rank 145”口径。

## 简短 scorecard
- `usefulness = 3/3`：直接改变后续自动轮次 routing，避免重复烧预算。
- `time_stability = 3/3`：不依赖新数据刷新，基于现成 artifact 可复核。
- `cross_asset_stability = 2/3`：结论覆盖 BTC/ETH/SOL 共享代理，但仍局限于当前 proxy。
- `cost_trade_stability = 3/3`：零新增实验成本，纯 writeback 收口。
- `deployability = 3/3`：顶板已同步，后续 bot3 可直接按新顺序执行。
- `recommended_action = 完成并交接`
- `why_now = 这一步比重跑实验更有杠杆，因为问题不在证据缺失，而在 authoritative desk 尚未同步。`
- `main_weakness = Rank 145 的负结论仍建立在 Rank32b 共享代理，而不是更差回撤场景或真实 tiny-live 资金曲线。`

## 本轮结论
本轮完成的是一个真正改变自动执行方向的小步：
- `Rank 145` 保留 `keep_P1`，但明确降为 `reserve`；
- 默认主位切回 `Rank 14b -> Rank 140`；
- 后续 bot3 不应再把 `Rank 145` 当默认 primary。
