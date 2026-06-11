# 做第一版 Cross-Engine Source Comparison

## 为什么这次选这个

这轮继续沿当前最接近的主线推进，没有新开题。

前面已经完成：
1. `PyTrendline event source bridge v1`
2. `PyTrendline event validation v1`
3. TODO 中已明确下一步之一是：
   - `PyIndicators source vs PyTrendline source` 的第一轮并行比较

因此这轮最值得做的，不是再单独补某一边的页面，而是把两边当前的成熟度、覆盖范围、已有证据、当前最强/最弱点放到同一页上做 **source-level / evidence-level 对照**。

这轮最值得复用/借鉴的点是：**在两个 source 还不完全 apples-to-apples 之前，先做一版“成熟度/覆盖/证据”对照，比硬凑一份假精确的同口径回测更诚实，也更有决策价值。**

## 核心结论（中文摘要）

核心结论：**当前 `PyIndicators` 仍然是覆盖更广、证据更多的 baseline source，但它的 breakout 线整体偏弱，只剩 retained rebound subsets 更像可继续候选；`PyTrendline` 的定义更干净、explainability 更强，也已经进入 observation 层，但当前 coverage 仍窄，且 breakout validation v1 依然偏弱。**

证据如何支持这个结论：**`PyIndicators` 已覆盖 8 个资产、多档样本窗口，并累积了 45574 笔 ladder trades 与 1123 个 symbol-slope cells；而 `PyTrendline` 当前 validation v1 只在 `BTC-USD / 10d / 5m` 上对 215 条事件做了 `+1/+3/+6/+12 bars` 观察，其中 breakout 在 `+6/+12` bars 的 mean forward return 约为 `-0.04% / -0.08%`，说明它已进入验证层，但还不能直接宣布强阳性。**

## 本轮做了什么

本轮只做一个主点：**落地第一版 `Cross-Engine Source Comparison v1`。**

具体改动：

1. 新增脚本：
   - `scripts/build_cross_engine_source_comparison_report.py`

2. 复用现有证据：
   - `trendline_confirmation_ladder/summary.json`
   - `trendline_confirmation_ladder/sample_meta.csv`
   - `trendline_confirmation_ladder/breakout_ladder_summary.csv`
   - `trendline_confirmation_ladder/rebound_retained_subset_summary.csv`
   - `trendline_event_slope_audit/summary.json`
   - `pytrendline_event_validation/summary.json`
   - `pytrendline_event_validation/overall_by_family_horizon.csv`

3. 生成产物：
   - `reports/artifacts/cross_engine_source_comparison/summary.json`
   - `reports/artifacts/cross_engine_source_comparison/engine_scorecard.csv`
   - `reports/artifacts/cross_engine_source_comparison/key_metrics.csv`
   - `reports/site/factors/cross_engine_source_comparison/report.html`

4. 更新目录 / TODO：
   - `Structure-Event Mainline` 新增第 5 张卡：`Cross-Engine Source Comparison v1`
   - `docs/TODO.md` 将“第一轮并行比较”标记为完成
   - 同时新增下一条更严格的待办：
     - 在 `bridge v2 / 更可比 sample` 上做第二轮 **apples-to-apples numeric comparison**

## 这版 comparison v1 是什么，不是什么

它是：
- `source-level / evidence-level` 对照
- 回答：
  - 谁覆盖更广
  - 谁证据更多
  - 谁当前更强 / 更弱
  - 下一步缺口在哪

它不是：
- 严格 same-sample / same-window / same-bucket 的最终赛马
- 也不是最终策略层结论

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_cross_engine_source_comparison_report.py scripts/build_trendline_tracks_site.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_cross_engine_source_comparison_report.py`
- `./.venv/bin/python scripts/build_trendline_tracks_site.py`
- `./.venv/bin/python scripts/build_plans_site.py`

在线验证：

- `https://jp.jerrypsy.top/momentum/factors/cross_engine_source_comparison/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/factors/structure_event_mainline/report.html` 返回 200，且 `Reports included: 6`

关键锚点指标：

- `PyIndicators breakout (2Y)`
  - `breakout hold = 3`
  - `positive_asset_ratio = 50.00%`
  - `mean_total_return ≈ -2.57%`

- `PyIndicators rebound retained (2Y)`
  - `rebound inside = 0 / retained_union`
  - `positive_asset_ratio = 75.00%`
  - `mean_total_return ≈ +5.57%`

- `PyTrendline breakout v1`
  - `+6 bars`
  - `sample_count = 203`
  - `up_ratio ≈ 50.25%`
  - `mean_forward_return ≈ -0.04%`

- `PyTrendline breakout v1`
  - `+12 bars`
  - `sample_count = 190`
  - `up_ratio ≈ 48.95%`
  - `mean_forward_return ≈ -0.08%`

## 风险 / 边界

- 这版 comparison 仍是“异步成熟度对照”，不是严格 apples-to-apples。
- `PyIndicators` 侧当前是 multi-asset / multi-sample 的 strategy-style 与 subset-style 证据；
- `PyTrendline` 侧当前是单窗口、observation-style 的 v1 证据；
- 因此这页最适合用来做方向判断和排优先级，不适合直接拿来下最终胜负结论。

## 下一步建议

1. 做 `PyTrendline bridge v2`
   - 至少补：`representative only vs all valid`
   - 并尽量扩到 `rebound / retest` 语义

2. 在更可比样本上做第二轮对照：
   - 尽量同样窗口 / 同样 bucket
   - apples-to-apples numeric comparison

3. E 模块继续优先找：
   - `rebound / retest / confirmation` 的外部证据
   - 帮助解释为何 `breakout` 普遍偏弱、哪些过滤更值得尝试的材料

## Commit hash

- `66e92f8` — `feat(momentum): add cross-engine source comparison v1`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交与本轮无关的其它 site / reading 脏文件，因为它们不属于这次 comparison v1 的最小闭环。
