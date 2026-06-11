# breakout confirm_1 补入同一套成本 / 执行框架

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，选的是一个真正紧邻、而且现在最该回答的小问题：**如果把 `support_breakout_confirm_1 @ h24` 也放进和 raw 完全同一套成本 / capital-allocation first-pass 框架里，它会不会比 raw 更诚实，甚至更值得升成主原型？**

之所以选这个点：
1. `support_breakout_v0_h24` 页前面已经把 raw 的 `cost / overlap / 1-slot / equal-weight concurrent(entry)` 都补出来了；
2. 页面里也早就写了 `confirm_1` 应该进同一套框架比较，但还没有真正把它放进去；
3. 这是一刀很小，却直接关系到后续资源顺序：到底该继续以 `raw` 为主原型，还是让 `confirm_1` 抢位。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 把输入读取从只看 `support_breakout_raw` 扩成同时可读 `support_breakout_raw / support_breakout_confirm_1`；
   - 抽出通用的 `build_simple_breakout_trades(...)`，让 `raw` 与 `confirm_1` 都按同一口径生成 h24 short trades；
   - 新增 `breakout_honesty_snapshot(...)`，把每条线在同一套 first-pass 约束下压成一行可比较摘要：
     - gross 累计
     - `20bps` per-asset 累计
     - `test + 20bps`
     - `up + 20bps`
     - `equal-weight concurrent(entry) + 20bps`
     - `1-slot global + 20bps`
   - 在 `support_breakout_v0_h24` 主报告中新增一段：
     - **如果把 confirm_1 也放进同一套成本 / 执行框架，谁更像该继续保留的原型？**
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/confirm1_trades.csv`
   - `reports/artifacts/support_breakout_v0_h24/confirm1_summary.csv`
   - `reports/artifacts/support_breakout_v0_h24/confirm1_summary_by_asset.csv`
   - `reports/artifacts/support_breakout_v0_h24/confirm1_summary_by_split.csv`
   - `reports/artifacts/support_breakout_v0_h24/confirm1_summary_by_regime.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_confirm1_same_frame_compare.csv`
3. 更新站点可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 在 breakout follow-up 的 latest progress 链里补上这次 `confirm_1 same-frame compare` 的正式读法。

## 核心结果

### 1) 在完全同一套 first-pass 框架下，raw 仍明显强于 confirm_1

来自 `raw_confirm1_same_frame_compare.csv`：

- **gross 累计**
  - `raw_v0`: `92.45%`
  - `confirm_1`: `74.91%`
- **20bps / per-asset independent**
  - `raw_v0`: `75.03%`
  - `confirm_1`: `59.38%`
- **20bps / equal-weight concurrent(entry)**
  - `raw_v0`: `19.40%`
  - `confirm_1`: `12.04%`
- **20bps / 1-slot global**
  - `raw_v0`: `13.83%`
  - `confirm_1`: `5.06%`

这说明 `confirm_1` 不是“更加现实后一对照反而更强”的那类确认变体；它在同一套成本 / 资金约束下仍落后于 raw。

### 2) confirm_1 没证明自己是更诚实的后段版本

- `test + 20bps`
  - `raw_v0`: `-3.08%`
  - `confirm_1`: `-5.56%`

也就是说，`confirm_1` 现在还不能用“虽然更弱，但 test / realism 更稳”来替自己抢位；至少这轮 first-pass 证据不支持这个说法。

### 3) 当前最合理的项目级读法

这轮之后，关于 `raw vs confirm_1` 的顺序更清楚了：
- `raw` 继续作为 breakout-short 的主原型 / 主 follow-up 入口；
- `confirm_1` 仍保留为 `co-primary confirmation variant`；
- 但它当前更像“值得一起进后续 honesty 框架的紧邻确认层”，而不是可以反客为主取代 raw 的主线对象。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果把 confirm_1 也放进同一套成本 / 执行框架，谁更像该继续保留的原型？`
- 页面中已出现关键对照数：
  - `59.38%`
  - `12.04%`
  - `5.06%`
- `reports/artifacts/support_breakout_v0_h24/` 下已生成 `confirm1_*` 与 `raw_confirm1_same_frame_compare.csv`

## 风险 / 边界

1. 这轮仍是 **first-pass 同框架比较**，不是正式组合级 portfolio backtest；
2. `equal-weight concurrent(entry)` 与 `1-slot global` 仍是刻意保守但简化的执行近似；
3. 但它已经足够回答当前最需要的资源排序问题：`confirm_1` 还没有在 realism 维度上反超 raw。

## 下一步建议

下一步最值得接的仍是：
1. 若继续做 breakout 主线，先补 `raw` 的更正式组合级资金曲线 / sizing honesty；
2. 若要给 `confirm_1` 再一次机会，也应放在同一套更正式组合约束下，而不是另起一条独立大主线。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
