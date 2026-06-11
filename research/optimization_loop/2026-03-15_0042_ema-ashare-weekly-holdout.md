# EMA A股 weekly frontier strict holdout

## 本轮认领

- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：把 `A股 weekly frontier` 从第一刀 `rolling / OOS honesty` 再推进到更严格的 `strict holdout honesty`，直接决定它还该不该继续算进 `EMA baseline family`。

## 为什么选这个

这一刀正好命中当前 `Current relay baton` 的第 1 项，而且比继续补 wording 更值钱：
1. `EMA 60m` 与 `PSAR overlay` 的真实结果已经落页；
2. `A股 frontier` 也已经有第一刀 rolling 结果，但结论仍停在 `mixed`；
3. 当前最该回答的问题已经收窄成：`创业板ETF 1wk / 沪深300ETF 1wk` 到底只是 frontier 偏薄，还是已经足以把它们从 `EMA baseline family` 里继续收窄出去。

## 本轮做了什么

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 `build_ema_non60m_ashare_weekly_holdout_slice()`；
   - 对 `沪深300ETF / 创业板ETF` 的 `1wk` 数据做更严格 holdout：
     - 固定 `EMA9/EMA20` 与 `PSAR`
     - `730d lookback + 365d forward holdout`
     - `365d` 步长按年滚动
   - 生成 3 份新 artifact：
     - `ema_non60m_ashare_weekly_holdout_window_metrics.csv`
     - `ema_non60m_ashare_weekly_holdout_pocket_summary.csv`
     - `ema_non60m_ashare_weekly_holdout_overall_summary.csv`
   - 在 `EMA / PSAR Raw Alpha Focus Report` 新增 **Q20**，正式回答：A股 weekly frontier 在更严格 holdout 下是否还该继续算作 `EMA baseline family` 的支持 pocket。
2. 更新 `scripts/build_alpha_closure_board_report.py`
   - 将 `EMA / PSAR` 总决策卡片同步成最新口径：A股 weekly frontier 已不应再被计作 `EMA baseline family` 的支持证据。
3. 更新 `docs/TODO.md`
   - 将 `EMA：把 A股 weekly frontier 再推进到更严格的 rolling / holdout honesty` 标记为已完成；
   - 并把新的 strict holdout 结论写回 long-form 进度区。
4. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果

### 1) A股 weekly frontier 的更严格 holdout 已明显偏向 PSAR

来自 `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_weekly_holdout_overall_summary.csv`：
- 两格 weekly pocket 一共 `14` 个 holdout
- `EMA` 的 net20 正 holdout 占比仅约 `42.86%`
- `PSAR` 约 `85.71%`
- `EMA` 只在约 `35.71%` 的 holdout 里优于 `PSAR`
- 当前整体 verdict：`PSAR-lean`

### 2) 创业板ETF 1wk 已不该继续替 EMA baseline family 辩护

来自 `ema_non60m_ashare_weekly_holdout_pocket_summary.csv`：
- `创业板ETF 1wk`
  - `EMA` 正 holdout 占比约 `42.86%`
  - `EMA` median net20 约 `0.00%`
  - `PSAR` 正 holdout 占比约 `100.00%`
  - `PSAR` median net20 约 `4.03%`
- 当前最诚实的读法：这格更像应从 `EMA baseline family pocket` 里剔出去，至少降级成 `PSAR/mixed pocket`。

### 3) 沪深300ETF 1wk 也不再只是“mixed 但 EMA 勉强还行”

- `沪深300ETF 1wk`
  - `EMA` 正 holdout 占比约 `42.86%`
  - `EMA` median net20 约 `-5.17%`
  - `PSAR` 正 holdout 占比约 `71.43%`
  - `PSAR` median net20 约 `1.01%`
- 当前更像 `mixed but PSAR-lean`，不再适合继续算作 EMA 的稳定支撑口袋。

## 项目级含义

这轮之后，关于 `EMA baseline family` 的口径应更严格：
- `EMA 60m crypto`：已经是 fail pocket；
- `A股 weekly frontier`：现在也不该继续算作 `EMA baseline family` 的支持 pocket；
- 若还继续讲 `EMA family`，更诚实的说法应收窄成：`A股 daily` 仍可保留观察，而 `A股 weekly` 目前更像 `PSAR/mixed branch`。

也就是说，`EMA / PSAR` 线并没有整体收工，但 `EMA baseline family` 的边界现在比前一轮更清楚了。

## 验证

已执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q20. 如果把 A股 weekly frontier 再推进到更严格 holdout honesty...`
- `reports/site/factors/alpha_closure_board/report.html` 已出现 A股 weekly strict holdout 结论
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步 strict holdout 数字与分类结论

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然包含多条在途改动；`docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`scripts/build_alpha_closure_board_report.py`、以及多份已生成站点文件在本轮前就处于 dirty 状态。此时做 selective commit 无法保证只打包本轮改动。
