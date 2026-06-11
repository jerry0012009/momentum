# EMA 60m rolling falsification 结果切片（crypto cache）

## 本轮认领

按最新收紧要求，本轮不再补 protocol / gate 文案，直接交一个真实结果切片：
- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：产出 `EMA 60m gross vs 20bps` 的 rolling / walk-forward 最小结果，并落到网页可见页。

## 本轮实际推进

### 1) 在 `build_ema_psar_raw_alpha_report.py` 内新增真实计算路径（复用本地缓存）

新增了基于本地缓存的 rolling 计算（不重跑重型下载）：
- 数据源：`reports/artifacts/pytrendline_event_validation_v3_crypto_180d/cache`
  - `BTC_USD__180d__60m.csv`
  - `ETH_USD__180d__60m.csv`
  - `SOL_USD__180d__60m.csv`
- 规则：固定 `EMA9/EMA20`
- 窗口：`45d window + 15d step`
- 成本口径：`20bps`（逐笔线性近似）

新增产物：
- `reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_window_metrics.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_asset_summary.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema60m_crypto_rolling_overall_summary.csv`

### 2) 把结果直接落到主报告页

更新：`reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 `Q13. 真做一版 EMA 60m rolling falsification slice 后，现有缓存样本在说什么？`
- 给出可见结论、资产汇总表、最差窗口表；不再只停留在门槛协议。

同时顺延章节：
- 旧 gate 段移为 `Q14`
- 边界段移为 `Q15`

### 3) 同步 plans / TODO

- 更新 `docs/TODO.md`（补“最新结果”而非只补 protocol）
- 重建 `reports/site/plans/momentum_todo.html`

## 本轮关键数据点（真实结果）

在 `BTC/ETH/SOL` 的 cache 180d 切片下（45d+15d）：
- 总窗口：`30`
- gross 正窗口：`4/30`（`13.33%`）
- 20bps 正窗口：`2/30`（`6.67%`）
- 达到“多数窗口 net 为正”的资产：`0/3`
- 各资产 median window net20：
  - BTC：`-16.24%`
  - ETH：`-11.45%`
  - SOL：`-19.71%`

当前门槛读法：该切片明显落在 `fail` 档。

## 最小验证

执行：
- `python3 scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_plans_site.py`

结果：
- 报告和 plans 均成功生成；
- 仅有 matplotlib 中文字体 warning，无阻塞报错。

## 影响与下一步

- 这轮已经满足“先交结果”的收紧要求；
- 当前更合理下一步：优先做 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m`，看 PSAR 是否能在最脆口袋里提供真实修复，而不是继续追加 EMA 线上的 protocol 文案。

## Commit

本轮**未提交**。

原因：repo/worktree 仍包含大量与本轮无关或跨轮在途 dirty/untracked 变更，当前不具备安全 selective commit 条件；为避免混入非本轮改动，暂不提交。