# breakout v0 补做 hourly portfolio path first-pass

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把现有 `equal-weight concurrent(entry)` 再往前推进一小步，做一版更正式的 **hourly mark-to-market 统一资金曲线**，回答 breakout v0 在 `20bps` 下从 entry-only 近似走到组合级路径后还剩多少。

## 为什么选这个

这轮没有再补说明文案，而是直接接上 breakout 线当前最值得补的真实结果：
1. 前面已经有 `per-asset independent / equal-weight concurrent(entry) / 1-slot global` 三档 first-pass；
2. 其中 `equal-weight concurrent(entry)` 仍只是按入场时并发仓位均分资金，离真正组合级路径还差半步；
3. 在 13 分钟节奏下，把它推进成 `hourly mark-to-market` 是一个足够小、但能真实压缩执行幻想的结果切片。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `build_equal_weight_hourly_portfolio_path(...)`
     - 对当前已选中的 v0 交易做 hourly mark-to-market；
     - 每个活跃小时按并发仓位等权持有；
     - `20bps` round-trip cost 拆成 entry / exit 各一半；
   - 新增 `summarize_hourly_portfolio_path(...)`
     - 输出 active hours / 平均并发 / 累计净收益 / max drawdown 等摘要；
   - 在 `support_breakout_v0_h24` 主报告中新增一段：
     - **更正式一点的组合级资金曲线 first-pass：把 equal-weight 从 entry-only 推到 hourly path 后，还剩多少？**
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_summary_20bps.csv`
3. 更新站点可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 在 breakout 线 follow-up 进度链里补上这次 hourly portfolio path 的正式读法。

## 关键结果

### 1) 更正式的 hourly equal-weight path 把结果再压窄了一截

当前在 `20bps` 下：
- `per-asset independent`：累计约 `75.03%`
- `equal-weight concurrent(entry)`：累计约 `19.40%`
- **`equal-weight concurrent(hourly path)`：累计约 `14.04%`**
- `1-slot global`：累计约 `13.83%`

这说明：
- breakout v0 不是“一进统一资金曲线就没了”；
- 但 `entry-only` 的 equal-weight 仍偏乐观；
- 更正式一点的 portfolio path 会把它从 `19.40%` 再压到大约 `14.04%`。

### 2) 这条线仍没被组合约束直接抹掉，但执行空间更诚实了

来自 `capital_allocation_equal_weight_hourly_summary_20bps.csv`：
- active hours：`444`
- mean active positions：约 `2.70`
- max active positions：`4`
- cumulative net return：约 `14.04%`
- max drawdown：约 `-12.03%`

当前更诚实的项目级读法是：
- breakout v0 仍可保留为 `conditional alpha / v0 prototype`；
- 但不该再按独立记账或 entry-only equal-weight 去想象统一资金下的可执行空间；
- 后续若继续推进，重点应转到更正式的 portfolio path / sizing honesty，而不是继续扩 breakout 变体。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `更正式一点的组合级资金曲线 first-pass`
  - `14.04%`
  - `-12.03%`
  - `444`
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步这条结果；
- `reports/artifacts/support_breakout_v0_h24/` 下已生成新的 `hourly_path / hourly_summary` artifacts。

## 风险 / 边界

1. 这轮仍是 **portfolio first-pass**，不是最终 portfolio engine；
2. 当前 path 只对现有已选中交易做 hourly mark-to-market，尚未加入更复杂的动态再平衡 / sizing policy；
3. 但它已经足够回答一个更接近实盘的问题：entry-only 的组合层读法到底还有多乐观。

## 下一步建议

下一步最值得接的是：
1. 若继续 breakout 线，就做更正式的 portfolio path / sizing honesty；
2. 或者把 `confirm_1` 也放进同一套 hourly portfolio path，对照它是否在更正式组合约束下更稳。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
