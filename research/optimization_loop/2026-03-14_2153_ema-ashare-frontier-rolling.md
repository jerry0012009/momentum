# EMA A股 frontier：第一刀 rolling / OOS honesty 落页

## 本轮认领

- 主点：`EMA / PSAR raw alpha focus`
- 任务：把 Top-3 里还未完成的 `EMA non60m frontier（尤其 A股）rolling / OOS honesty` 真正交付成结果页与 durable artifacts，而不是继续 protocol 文案。

## 为什么选这个

当前 relay baton 对 EMA 的第一优先项，就是先把 A股 frontier 做第一刀 rolling / OOS。前序已经有：
1. `EMA non60m` 全体 survivor（18/18）
2. frontier queue
3. frontier 与 PSAR 静态 head-to-head

但还缺最关键的一刀：**这些 A股 frontier pocket 在 rolling / OOS 下到底还能不能守住。**

## 本轮动作

1. 扩展 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 A股 frontier rolling 切片（`沪深300ETF/创业板ETF` × `1d/1wk`）；
   - 口径：`10y` 数据，`EMA9/EMA20`，`730d window + 180d step`，`20bps`；
   - 同时加入同口径 `PSAR` 对照，避免只看 EMA 单边；
   - 为避免未来 `python3` 环境缺 `yfinance` 直接失败，新增 `cache-first` 逻辑：优先读 `reports/artifacts/ema_psar_raw_alpha/ashare_frontier_cache/*.csv`，缺失时再触发下载。
2. 新增 durable artifacts
   - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_window_metrics.csv`
   - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_pocket_summary.csv`
   - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_frontier_rolling_overall_summary.csv`
3. 更新可见页面
   - `reports/site/factors/ema_psar_raw_alpha/report.html` 新增 **Q19**（A股 frontier rolling 结果）
   - 原 Q19/Q20 顺延为 Q20/Q21
4. 更新任务入口
   - `docs/TODO.md` 将 Top-3 第 1 条标为完成 `[x]`，并写入结果口径
   - 同步 `reports/site/plans/momentum_todo.html`

## 结果（核心）

A股 frontier rolling 的当前读法是 **mixed，不是整片塌掉**：

- 窗口总数：`68`
- `EMA` net20 正窗口占比：`50.00%`
- `PSAR` net20 正窗口占比：`55.88%`
- `EMA` 在 A股 frontier 里达到“多数窗口为正”的 pocket：`2/4`
- `PSAR` 同口径也是：`2/4`

按 pocket 看：

1. `沪深300ETF 1d`：EMA 仍可守（median net20 约 `+0.13%`，高于 PSAR 的 `-1.12%`）
2. `沪深300ETF 1wk`：mixed（EMA median net20 约 `+9.21%`，但 PSAR 正窗口占比更高）
3. `创业板ETF 1d`：EMA 虽未到多数正窗口，但仍明显好于 PSAR（约 `-0.75%` vs `-16.19%`）
4. `创业板ETF 1wk`：当前最弱口袋（EMA median net20 约 `-11.64%`，明显弱于 PSAR 的 `+13.10%`）

## 项目级结论

- `EMA baseline family` 没被 A股 frontier 一刀否掉；
- 但也不能再用 `non60m overall 18/18` 大桶口径自证；
- 更诚实的下一棒应继续收窄到 **A股 weekly frontier（尤其 创业板ETF 1wk）**，而不是再平均撒在整个 non60m family。

## 验证

执行：
- `./.venv/bin/python scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_ema_psar_raw_alpha_report.py`（验证 cache-first 后系统 python 也可跑通）
- `python3 scripts/build_plans_site.py`

命中：
- `report.html` 出现 `Q19. 真把 A股 frontier 推到第一刀 rolling / OOS honesty...`
- 页面出现关键值：`-11.64%`、`13.10%`、`730d window + 180d step`
- plans 镜像已同步 Top-3 第 1 条为 `[x]`

## Commit

本轮未提交。

原因：当前 worktree 大量跨轮文件已处于 dirty / untracked；本轮涉及路径（`docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html`）在本轮前已非干净状态，无法安全做可归因 selective commit。
