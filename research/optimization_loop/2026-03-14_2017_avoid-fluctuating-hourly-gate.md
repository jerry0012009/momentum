# breakout：avoid_fluctuating 同框架 hourly gate 复核

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把 `avoid_fluctuating` 真正放进与 raw 完全一致的 `20bps hourly mark-to-market` 组合口径，验证它是否比“换成 confirm_1”更能改善弱口袋。

## 本轮改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `confirm_trend_regime / trend_policy` 计算（基于 confirm 时点 `EMA50/EMA200 + EMA50 slope24`，按 `uptrend/downtrend/fluctuating` 划分）；
   - 把 `avoid_fluctuating` 过滤后的事件/交易推进到与 raw 一致的同框架回测流程；
   - 新增 gate 对照摘要与对应 artifacts：
     - `raw_avoid_fluctuating_same_frame_compare.csv`
     - `avoid_fluctuating_*` 系列 summary / hourly path / split / regime 文件；
   - 在 `support_breakout_v0_h24` 页面新增一节：
     - “真把 avoid_fluctuating 放进同一套 hourly portfolio path / sizing honesty 后，它比换 confirm_1 更像样吗？”
2. 更新 `docs/TODO.md`
   - `Current relay baton` 第 1 项标记为完成 `[x]`；
   - 补入本轮关键结果（保留率、overall/path、up/test 变化）。
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - breakout 卡片 evidence/next 同步到最新口径：
     - `avoid_fluctuating` 已完成同框架复核；
     - `up` 与回撤改善，但 `test` 仍偏弱；
     - 下一步应转向“带最小 gate 的更正式 sizing/portfolio honesty”，而非继续变体排序。
4. 重建页面
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果（20bps，同框架）

对比 `raw_v0` vs `avoid_fluctuating`：

- 交易保留：`48 -> 40`（保留率约 `83.33%`）
- hourly overall 累计：`14.04% -> 15.46%`
- hourly max drawdown：`-12.03% -> -9.97%`
- `up` 弱口袋累计：`-1.99% -> +0.95%`
- `test`：`-2.92% -> -2.67%`（仅小幅改善，仍为负）

项目级读法：
- `avoid_fluctuating` 确实比“换成 confirm_1”更像样；
- 但它不是万能开关，`test` 仍没被修好；
- breakout 线仍应定位为 `conditional alpha / strategy-facing prototype`。

## 验证

- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现新 gate 小节与关键数值（`83.33% / 15.46% / -9.97% / +0.95% / -2.67%`）。
- `reports/artifacts/support_breakout_v0_h24/` 已生成：
  - `raw_avoid_fluctuating_same_frame_compare.csv`
  - `avoid_fluctuating_capital_allocation_equal_weight_hourly_by_split_20bps.csv`
  - `avoid_fluctuating_capital_allocation_equal_weight_hourly_by_regime_20bps.csv`
  - 及配套 `avoid_fluctuating_*` summary/path 文件。
- `alpha_closure_board` 与 plans 镜像已同步最新 breakout 读法。

## Commit

本轮未提交。

原因：当前 worktree 存在大量在途脏改动，且涉及与本轮同路径文件；此时 selective commit 无法保证仅打包本轮改动。