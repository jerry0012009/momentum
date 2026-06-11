# 2026-03-23 09:11 UTC · Rank 145 routing freeze writeback

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / decisive writeback`
- 本轮目标：不是再跑新实验，而是把 **Rank 145 已完成的 frozen-threshold A/B** 写回 authoritative 顶板，避免后续自动轮次继续把它当默认 primary。

## 0. 路径判断
- `Paper launch queue = empty`
- 未见 `Paper / 正在自动运行` runner 的 `stale / error / refresh 失步 / ledger / open-position / red-watch` 异常。
- 因此本轮仍属 `Scout`，且按 `Next 3 bot3 runs` 的精神，优先完成一个能 **改变后续 routing** 的最小收口动作。

## 1. 本轮核实的可验证事实
核实 artifact：
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.csv`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`

核实结论：
- desk 共享代理使用 `Rank32b 15m 6bps BTC/ETH/SOL`。
- 在 `8/10/12% DD × 0.25/0.5 size × 95/98% recover` 全部组合下：
  - **0 次触发 reduced mode**
  - 组合 baseline 维持：
    - `post_cost_return ≈ +47.89%`
    - `max_drawdown ≈ 1.85%`
    - `calmar ≈ 125.89`
- 因此 `Rank 145` 当前最诚实口径不是“继续默认 fresh verify”，而是：
  - **`P1 / keep_P1 / reserve / not default primary`**

## 2. 本轮实际交付
已将上述结论写回 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

### A. Active Scout 排序改写
- 把 `Rank 14b` 提到默认第一位；
- `Rank 140` 作为 `active compare anchor` 保留第二位；
- `Rank 145` 下调为第三位，并明确标注：
  - `frozen-threshold A/B done`
  - `shared proxy未触发`
  - `退出默认primary，转reserve`

### B. Next 3 bot3 runs 改写
- `Run 1 -> Rank 14b`
- `Run 2 -> Rank 140`
- `Run 3 -> Rank 145 reserve`
- 同时写明：若没有更差 shared proxy 或更接近 tiny-live 的真实回撤场景，`Rank 145` 不再占默认 primary。

### C. 最近关键 evidence 更新
- 新增 `2026-03-23 09:08 UTC` 条目，把 Rank 145 的 shared-proxy A/B 结论写成 reader-facing authoritative evidence。

## 3. 为什么这步有杠杆
这步没有生成新因子，但它避免了更贵的错误：
- 避免后续 cron 继续按旧顶板，把默认 Run 1 浪费在已完成 decisive cut 的 `Rank 145` 上；
- 让后续 bot3 自动轮次把主预算重新投向 `Rank 14b` 和 `Rank 140` 这两个仍可能改变 routing 的候选；
- 把“实验已做完，但顶板没同步”的状态风险消掉。

## 4. 简短 scorecard
- `main point`：Rank 145 shared-proxy frozen-threshold A/B authoritative writeback
- `adjacent sub-point`：Scout routing reorder
- `verification`：artifact 已存在且数值核实完成
- `delivery`：`docs/TODO.md` 顶板已同步；后续 run 顺序已改写
- `result`：**完成一个能直接改变后续自动执行方向的小步**

## 5. 本轮结论
本轮最有杠杆的小步不是重跑实验，而是把已完成的 Rank 145 结果写回 authoritative 顶板：
- `Rank 145` 仍保留 `P1 / keep_P1`，但降为 `reserve`；
- 默认主位切换到 `Rank 14b -> Rank 140`；
- 下轮 auto run 不应再把 Rank 145 当成默认 primary。
