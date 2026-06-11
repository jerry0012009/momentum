# breakout hourly honesty 结果补齐到 durable artifacts 与总入口

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把已经落在页面里的 `hourly portfolio path` 下 `split / regime honesty` 结果补成真正可复用的 durable artifacts，并同步刷新 `alpha_closure_board` 与 `Top 3 relay baton`，让 breakout 线的当前总口径不再停留在旧的 `confirm_1 会不会抢位` 上。

## 为什么选这个

这轮没有再开新回测，而是收一个已经有真实结果、但入口层还没完全同步的小缺口：
1. `support_breakout_v0_h24` 页面里已经有 `hourly path` 下的 `split / regime` 读法；
2. 但对应的 CSV artifacts 之前并没有实际落盘，`Current relay baton` 里第 3 条也仍是未完成状态；
3. 同时 `alpha_closure_board` 的 breakout 卡片还主要停留在 `confirm_1 没抢位`，没有把“`test / up` 弱点在更正式组合口径下仍存在”这件事同步到总决策页。

因此本轮选这个点，是为了把 breakout 线当前真正有用的项目级结论补齐成：**不仅 confirm_1 没翻盘，而且 raw 的弱口袋在 hourly path 下也仍然存在，所以下一步应优先看 `avoid_fluctuating` gate，而不是继续纠结变体排序。**

## 做了什么改动

1. 重新执行 `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
   - 确认并补齐如下 durable artifacts：
     - `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_by_split_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_by_regime_20bps.csv`
2. 更新 `docs/TODO.md`
   - 将 `Current relay baton` 里的：
     - `support_breakout_confirm_1 -> hourly portfolio path / sizing honesty` 标记为完成；
     - `在更正式组合口径下复核 split / regime honesty` 标记为完成；
   - 并补上这条 breakout 线在 `20bps hourly mark-to-market` 下的正式结果口径。
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - 将 breakout 卡片的 strongest evidence / next step 同步成最新状态：
     - raw vs confirm_1 的更正式口径已看清；
     - `test / up` 弱点在同样的 hourly path 下仍存在；
     - 因此下一步默认应把 `avoid_fluctuating` 放进同一套 hourly portfolio path / sizing honesty 里复核。
4. 重建可见产物
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 本轮得到的关键结果

### 1) breakout 的弱点在更正式组合口径下并没有消失

来自新补齐的 durable artifacts：
- `capital_allocation_equal_weight_hourly_by_split_20bps.csv`
- `capital_allocation_equal_weight_hourly_by_regime_20bps.csv`

当前 `20bps hourly mark-to-market` 下：
- `test`：累计约 `-2.92%`
- `up`：累计约 `-1.99%`，max drawdown 约 `-13.76%`
- `validate`：累计约 `+6.50%`
- `flat`：累计约 `+12.72%`

这说明 breakout v0 在统一资金曲线下仍然更像：
- 有一定执行空间；
- 但明显带条件；
- 还不能因为 overall hourly path 约 `+14.04%` 就被误读成“环境依赖问题已经被消掉”。

### 2) 当前 breakout 线的入口级读法被收紧了

`alpha_closure_board` 现在不再只说：
- `confirm_1` 没有在更正式口径下反超 raw；

而是进一步写死：
- 即使把 realism 推到 `hourly portfolio path`，`test / up` 弱口袋仍在；
- 所以下一步不该继续花资源纠结 `confirm_1` 会不会抢主线位；
- 更值得做的是把 `avoid_fluctuating` 放进同一套 `hourly portfolio path / sizing honesty` 里复核，看它是否比“换确认变体”更直接改善这些弱口袋。

### 3) Current relay baton 终于和真实结果对齐了

本轮之后，`Current relay baton` 中至少两条 stale 状态被清掉：
- `confirm_1 -> hourly path` 已完成；
- `split / regime honesty -> hourly path` 已完成。

这让后续 bot3 / Jerry 再看 TODO 时，不会再误以为这些结果还没交付。

## 验证

### 1) durable artifacts 已落盘

验证命中：
- `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_by_split_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_hourly_by_regime_20bps.csv`

### 2) 总决策页已同步新口径

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `test 仍约 -2.92%`
  - `up 仍约 -1.99%`
  - `avoid_fluctuating ... 同一套 hourly portfolio path / sizing honesty`

### 3) plans / TODO 镜像已同步

验证命中：
- `docs/TODO.md` 中 `Current relay baton` 的 breakout 第 1 条与第 3 条均已更新；
- `reports/site/plans/momentum_todo.html` 已同步相同结果。

## 当前更诚实的项目级读法

breakout 线现在已经可以更稳定地这么看：
- `raw` 仍是 breakout-short 主原型；
- `confirm_1` 没在更现实口径下翻盘；
- `test / up` 的弱点在统一资金曲线下也依然存在；
- 所以下一步最值得花资源的，不是再做变体排序，而是看 `avoid_fluctuating` 这种环境 gate 能不能在同一套 hourly honesty 框架下真正改善弱口袋。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 等路径在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
