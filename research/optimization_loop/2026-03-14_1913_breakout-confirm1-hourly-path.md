# breakout confirm_1 补入更正式 hourly portfolio path 对照

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，直接接上一轮已经做好的 `hourly mark-to-market` 统一资金曲线 first-pass。

上一轮只把 `raw v0` 放进了更正式一点的 hourly equal-weight path；这轮要回答的紧邻小问题是：**如果把 `support_breakout_confirm_1 @ h24` 也推进到同一套 portfolio-path 口径，它会不会在执行层反超 raw，因而更值得抢主原型位置？**

这是一刀很小，但对当前资源顺序很关键，而且完全可以复用现有 cache / trades 逻辑，不需要重跑重型下载。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 扩展 `breakout_honesty_snapshot(...)`，让 `raw / confirm_1` 的同框架比较不只停在：
     - `per-asset independent`
     - `equal-weight concurrent(entry)`
     - `1-slot global`
   - 现在同一张比较表里也加入了：
     - `hourly_path_cost20_cumulative_return`
     - `hourly_path_max_drawdown`
   - 也就是把两条线都推进到更正式一点的 `hourly mark-to-market` 统一资金曲线口径。
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/confirm1_capital_allocation_equal_weight_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/confirm1_capital_allocation_equal_weight_hourly_summary_20bps.csv`
   - 并刷新 `reports/artifacts/support_breakout_v0_h24/raw_confirm1_same_frame_compare.csv`
3. 更新站点可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 在 breakout follow-up 的 latest results 链里补上 `confirm_1 hourly portfolio path` 的正式读法。

## 核心结果

### 1) confirm_1 在更正式 portfolio path 下仍没有反超 raw

当前 `20bps` 下：
- `raw` 的 hourly equal-weight path：
  - 累计约 `14.04%`
  - max drawdown 约 `-12.03%`
- `confirm_1` 的 hourly equal-weight path：
  - 累计约 `11.54%`
  - max drawdown 约 `-13.60%`

也就是说，把两者都从 entry-only 再推进到更正式一点的统一资金曲线后，`confirm_1` 依然没有在“更现实的执行层口径”里反超 raw；不仅收益更低，回撤也略更差。

### 2) 这让当前资源顺序更稳了

结合之前已落页的结果：
- `per-asset independent @ 20bps`：`raw 75.03% > confirm_1 59.38%`
- `equal-weight concurrent(entry) @ 20bps`：`raw 19.40% > confirm_1 12.04%`
- `hourly mark-to-market path @ 20bps`：`raw 14.04% > confirm_1 11.54%`
- `1-slot global @ 20bps`：`raw 13.83% > confirm_1 5.06%`

这说明：随着口径越来越诚实，`confirm_1` 也没有出现“越现实越强”的翻盘迹象。

### 3) 当前最诚实的项目级读法

这轮之后，更合理的固定读法是：
- `raw` 继续作为 breakout-short 的主原型；
- `confirm_1` 仍保留为 `co-primary confirmation variant`；
- 但它当前更像“紧邻确认层、值得跟着一起进 honesty / execution 框架”，而不是可以取代 raw 的更优主线。

## 验证 / 证据

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `再往前推到更正式的 hourly mark-to-market path`
  - `11.54%`
  - `-13.60%`
- `reports/artifacts/support_breakout_v0_h24/` 下已生成：
  - `confirm1_capital_allocation_equal_weight_hourly_path_20bps.csv`
  - `confirm1_capital_allocation_equal_weight_hourly_summary_20bps.csv`
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步同样口径。

## 风险 / 边界

1. 这轮仍是 **hourly mark-to-market first-pass**，不是最终 portfolio engine；
2. 但它已经比 entry-only 更接近真实统一资金曲线；
3. 对当前最需要回答的资源排序问题来说，这套证据已经足够说明：`confirm_1` 没有在更现实口径下反超 raw。

## 下一步建议

下一步若继续 breakout 线，更值得补的是：
1. `raw` 的进一步 sizing / portfolio honesty；
2. 或直接问 `avoid_fluctuating` 这类环境 gate 放进更正式组合路径后，会不会比“换成 confirm_1”更有价值。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
