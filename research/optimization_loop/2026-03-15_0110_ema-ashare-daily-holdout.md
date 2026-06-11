# EMA A股 daily strict holdout

## 本轮认领

- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：把 `A股 daily` 也推进到和 `A股 weekly` 同样更严格的 `strict holdout honesty`，直接回答：当 `A股 weekly` 已从 `EMA baseline family` 里出局后，`A股 daily` 还能不能继续算作剩余支持 pocket。

## 为什么选这个

这轮直接接 `Current relay baton` 的第 1 项，而且是一个真正的结果导向小任务：
1. `EMA 60m` 与 `PSAR overlay` 的真实结果已经落页；
2. `A股 weekly frontier` 也已经被 strict holdout 收窄成 `PSAR/mixed branch`；
3. 当前最值钱的问题不再是继续补 protocol，而是把 `A股 daily` 也用同样严格的口径验掉，决定 `EMA baseline family` 到底还剩什么。

## 本轮做了什么

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 `build_ema_non60m_ashare_daily_holdout_slice()`；
   - 对 `沪深300ETF / 创业板ETF` 的 `1d` 数据做 strict holdout：
     - 固定 `EMA9/EMA20` 与 `PSAR`
     - `730d lookback + 365d forward holdout`
     - `365d` 步长按年滚动
   - 生成 3 份新 artifact：
     - `ema_non60m_ashare_daily_holdout_window_metrics.csv`
     - `ema_non60m_ashare_daily_holdout_pocket_summary.csv`
     - `ema_non60m_ashare_daily_holdout_overall_summary.csv`
   - 在 `EMA / PSAR Raw Alpha Focus Report` 新增 **Q21**，正式回答：`A股 daily` 在更严格 holdout 下是否还能替 `EMA baseline family` 守门。
2. 更新 `scripts/build_alpha_closure_board_report.py`
   - 将 `EMA / PSAR` 总决策卡片同步成最新口径：
     - `A股 weekly` 已移出 `EMA family`
     - `A股 daily` 仍可暂时保留，尤其 `创业板ETF 1d` 仍是 daily survivor
3. 更新 `docs/TODO.md`
   - 将 `EMA：把 A股 daily 也推进到 strict holdout` 标记为完成；
   - 并把新的 strict holdout 结果写回 long-form 进度区。
4. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果

### 1) A股 daily strict holdout 整体仍偏向 EMA-lean

来自 `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_daily_holdout_overall_summary.csv`：
- 两格 daily pocket 一共 `16` 个 holdout
- `EMA` 的 net20 正 holdout 占比约 `62.50%`
- `PSAR` 约 `43.75%`
- `EMA` 在约 `62.50%` 的 holdout 里优于 `PSAR`
- 当前整体 verdict：`EMA-lean`

这说明：把 `A股 weekly` 拿掉后，`A股 daily` 还没有一起塌掉。

### 2) 创业板ETF 1d 仍是 EMA family 里最像样的 daily pocket

来自 `ema_non60m_ashare_daily_holdout_pocket_summary.csv`：
- `创业板ETF 1d`
  - `EMA` 正 holdout 占比约 `75.00%`
  - `EMA` median net20 约 `12.05%`
  - `PSAR` 正 holdout 占比约 `50.00%`
  - `PSAR` median net20 约 `5.13%`

这格当前仍能继续替 `EMA baseline family` 辩护。

### 3) 沪深300ETF 1d 更像 mixed，但仍没有出现 weekly 那种明显反超

- `沪深300ETF 1d`
  - `EMA` 正 holdout 占比约 `50.00%`
  - `EMA` median net20 约 `-2.60%`
  - `PSAR` 正 holdout 占比约 `37.50%`
  - `PSAR` median net20 约 `-4.49%`

所以它不算强 pocket，但也还没有像 `A股 weekly` 那样变成明显的 `PSAR-lean` 反证。

## 项目级含义

这轮之后，关于 `EMA baseline family` 的口径可以更干净地收成一句话：
- `EMA 60m crypto`：fail pocket
- `A股 weekly frontier`：移出 `EMA family`
- `A股 daily`：仍可暂时保留，尤其 `创业板ETF 1d` 仍是能替 EMA 守门的 daily survivor

也就是说，这条线当前不是“EMA family 全灭”，而是已经被压缩成更窄、但还没被完全打死的 daily survivors。

## 验证

已执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q21. 如果把 A股 daily 也推进到 strict holdout...`
- `reports/site/factors/alpha_closure_board/report.html` 已出现 daily strict holdout 结果与 family 重分类口径
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步 strict holdout 数字与结论

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`scripts/build_alpha_closure_board_report.py`、以及对应站点文件在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
