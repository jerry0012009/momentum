# bot3 执行日志｜sparse lag-vote × next-bar fresh intake first verdict（background/P0）

- 时间：2026-04-12 03:48 UTC
- 对象：`research/quant_digests/2026-04-11_1353_sparse-lagvote-nextbar-alpha.md`
- 轮次动作：fresh intake first-verdict（含 1 条 honesty 子检查）

## 本轮最小证据

读取并复核本地 artifact：
- `reports/artifacts/literature/sparse_intraday_lasso_probe_asset_summary_2026-04-11_v2.csv`
- `reports/artifacts/literature/sparse_intraday_lasso_probe_xs_summary_2026-04-11_v2.csv`
- `reports/artifacts/literature/sparse_intraday_lasso_probe_top_features_2026-04-11_v2.csv`

### 1) `1m/3m` 最小可执行边际（统一成本口径前）
- XS 汇总：
  - `1m mean_bps = +0.0059`
  - `3m mean_bps = -0.0467`
- 单资产 top-decile 事件中最优也仅：
  - `LTCUSDT event_mean_bps = +1.2401`
  - `BTCUSDT event_mean_bps = +0.6572`

结论：即使按最乐观可见毛边际，`1m` 仅贴地微正，`3m` 已转负；若纳入统一 taker+滑点（例如 `4 bps/side`），净值均显著为负，无法形成可执行优势。

### 2) honesty 子检查（lookahead / 信号位移泄漏）
- 对 `...top_features_2026-04-11_v2.csv` 扫描特征名：未发现 `lead/future/ahead/target/label` 等前视字段。
- 被选特征均为 `ret_l* / mom_* / rv_*` 形式的滞后或窗口统计特征。

结论：未发现“靠前视特征偷收益”的主导证据；失败主因不是 lookahead，而是成本后边际不足。

## 本轮 verdict

- verdict：`background/P0`
- 唯一 decisive blocker：`成本后边际不足`（`1m` 毛边际过薄且 `3m` 直接为负，无法支撑最小执行壳）
- 系统认知变化一句话：
  - `sparse lag-vote × next-bar` 在当前 Binance perp portability 下不具备可交易净边际，问题核心是成本吞噬而非前视泄漏。

## 状态回写
- 已将 `cycle_plan` 第 1 小点写为 `done`。
- 已在 runtime state 回写 fresh intake 结论与 background parked 记录。