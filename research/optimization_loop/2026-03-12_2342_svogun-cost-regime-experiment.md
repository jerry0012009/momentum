# 为 Svogun 2022 落地第一版 cost / regime experiment

## 为什么这次选这个

这轮我没有继续在主线内部补更多结构页，而是延续上一轮刚落地的 `Svogun 2022` replication report，往前推进半步：**把它从 clean-room 计划页，推进成一个最小可运行的本地 survival experiment。**

这个选择有两个原因：

1. 最近主线内部已经连续完成了：
   - `PyTrendline event bridge`
   - `PyTrendline event validation`
   - `Cross-Engine Source Comparison`
   所以内部闭环暂时已经够用。

2. 我们最近内部最明确的痛点就是：
   - breakout / trend 类信号整体不够强；
   - 继续只看 gross 表现，风险很高；
   - 后续必须更早把 `成本` 与 `regime` 拉进默认报告框架。

因此，这轮最值得复用/借鉴的点是：**当内部 breakout 结果已经显露疲态时，E 模块最有价值的推进不是继续做 scout，而是直接把“成本 + 状态切分”变成一个本地可运行的约束实验。**

## 核心结论（中文摘要）

核心结论：**在当前 8 币 60m 样本上，cost 确实会把 breakout / trend baseline 的均值与胜率进一步压低，而 regime（bubble proxy）也会显著重排结果；因此 `gross / net / regime split` 应当被提升为后续 breakout 主线的默认报告项，而不是可选附录。**

证据如何支持这个结论：**本次在同一批本地缓存 bars 上，同时对 `ma_crossover` 与 `rolling_breakout_20` 跑了 `gross / net_low / net_high` 和 `bubble_proxy` 分层；例如在 `60m_730d` 上，`rolling_breakout_20` 的 `mean_return` 从 `gross ≈ +0.117%` 下降到 `net_low ≈ +0.017%`、再到 `net_high ≈ -0.183%`，而 bubble proxy 的不同切分也会明显改变均值与胜率。**

## 本轮做了什么

本轮只做一个主点：**落地 `Svogun 2022 · Cost/Regime Experiment v1`。**

具体改动：

1. 新增脚本：
   - `scripts/build_svogun2022_cost_regime_experiment_report.py`

2. 复用现有本地缓存数据：
   - `reports/artifacts/trendline_confirmation_ladder/cache/60m_365d/bars.csv`
   - `reports/artifacts/trendline_confirmation_ladder/cache/60m_730d/bars.csv`

3. 规则设计（最小 clean-room 版本）
   - `ma_crossover`
     - EMA(12) 上穿 EMA(48)
   - `rolling_breakout_20`
     - close 上破前 20 根 close 高点
   - signal 在 bar close 触发，next bar open 入场，持有 12 bars，exit close 离场

4. 成本与状态设置
   - `gross`
   - `net_low = gross - 10bps`
   - `net_high = gross - 30bps`
   - regime 先用轻量 `bubble_proxy`：
     - 价格在慢均线上方
     - `trend_strength` 高于样本中位数
     - `vol24` 高于样本中位数

5. 生成产物
   - `reports/artifacts/svogun2022_cost_regime_experiment/summary.json`
   - `reports/artifacts/svogun2022_cost_regime_experiment/overall_summary.csv`
   - `reports/artifacts/svogun2022_cost_regime_experiment/bubble_summary.csv`
   - `reports/site/reading/svogun2022_cost_regime_experiment/report.html`
   - 本地明细：`reports/artifacts/svogun2022_cost_regime_experiment/event_returns.csv`（未提交）

6. 更新导航与文档
   - `Svogun 2022 · Cost/Regime Replication Report` 增加实验页入口
   - `Trendline Replication Briefs` 增加实验页入口
   - `Trendline Alpha Scout` 增加实验页入口
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 标记：`experiment v1 done`
   - `docs/TODO.md` 补充当前新增的最小实验结论

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_svogun2022_cost_regime_experiment_report.py`
- `./.venv/bin/python scripts/build_svogun2022_cost_regime_experiment_report.py`
- 重新生成并发布：
  - `scripts/build_svogun2022_cost_regime_replication_report.py`
  - `scripts/build_trendline_replication_briefs_report.py`
  - `scripts/build_trendline_alpha_scout_report.py`
  - `scripts/build_plans_site.py`

在线验证：

- `https://jp.jerrypsy.top/momentum/reading/svogun2022_cost_regime_experiment/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/reading/trendline_replication_briefs/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/reading/trendline_alpha_scout/report.html` 返回 200

关键样本摘要：

- 样本：`60m_365d` + `60m_730d`
- 资产：8 个 crypto symbols
- 总事件数：`14868`
- 规则：`ma_crossover`、`rolling_breakout_20`
- 持有期：`12 bars`

关键统计（`overall_summary.csv`）：

### 1) 60m_730d / rolling_breakout_20
- `gross`
  - `trade_count = 8205`
  - `win_ratio ≈ 48.60%`
  - `mean_return ≈ +0.117%`
  - `positive_symbol_ratio = 75.00%`
- `net_low`
  - `mean_return ≈ +0.017%`
  - `positive_symbol_ratio = 50.00%`
- `net_high`
  - `mean_return ≈ -0.183%`
  - `positive_symbol_ratio = 12.50%`

=> 这说明：**看似还算勉强存活的 breakout baseline，一旦加高成本，优势会快速塌掉。**

### 2) 60m_730d / ma_crossover
- `gross mean_return ≈ -0.077%`
- `net_low mean_return ≈ -0.177%`
- `net_high mean_return ≈ -0.377%`

=> 这说明：**简单 trend baseline 在当前口径下本来就不强，加成本后只会更差。**

### 3) regime / bubble proxy split（60m_365d / rolling_breakout_20）
- `bubble_proxy = False`
  - `gross mean_return ≈ +0.214%`
  - `win_ratio ≈ 51.45%`
  - `positive_symbol_ratio = 100.00%`
- `bubble_proxy = True`
  - `gross mean_return ≈ -0.116%`
  - `win_ratio ≈ 44.85%`
  - `positive_symbol_ratio = 25.00%`

=> 这说明：**状态切分确实会重排结果，而且不只是轻微扰动。**

## 风险 / 边界

- 这仍然是 **最小 survival experiment**，不是完整论文复现；
- 当前只用了两条 baseline 规则，不等于论文里的全规则族；
- 成本口径是简化近似（10bps / 30bps round-trip），暂时不是交易所级真实成本模型；
- regime 也只是轻量 `bubble_proxy`，不等于论文中的完整 bubble 检测方案。

但即使如此，这轮已经足够回答一件关键事情：**gross / net / regime split 值得被提升为主线默认约束。**

## 下一步建议

1. 若继续走 E 模块：
   - 在这个实验脚手架上再补一条更贴近当前主线的规则：
     - `confirmation-aware breakout baseline`
     - 或 `rebound / retest` baseline

2. 若切回主线：
   - 把 `gross / net / regime split` 明确写进 breakout / confirmation 主线的默认报告模板；
   - 后续任何 breakout 新实验，默认都不要只给 gross 总表。

3. 后续更严格时再升级：
   - 成本模型从常数 bps 升级为更细颗粒近似；
   - `bubble_proxy` 升级为更可审计的 regime classifier。

## Commit hash

- `d1375c8` — `feat(momentum): add svogun cost regime experiment`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有提交：
- `reports/artifacts/svogun2022_cost_regime_experiment/event_returns.csv`

原因是：
- 该文件是 3.8MB 的事件级明细；
- 当前网页与结论只依赖 summary / bubble summary / site report，先不把大体积明细数据塞进本轮 commit。
