# 为 PyTrendline 落地最小 event-source bridge

## 为什么这次选这个

这轮我先重新检查了当前 `docs/TODO.md`，确认最近主线已经重新聚焦到：

1. `Structure-Event Mainline` 仍是上位主线；
2. `PyIndicators` 已经降级为 baseline source / 对照组；
3. 当前最近、最值得延续的未完成项，确实是：**`PyTrendline -> unified event schema` 的第一版试映射。**

所以这轮没有新开题，也没有重跑任何重型下载，而是直接复用现有 `pytrendline_research` 产物，把它从“explainability 页面”推进到“最小 event-source 输入”。

这轮最值得复用/借鉴的点是：**当一个定义引擎已经有足够丰富的静态产物时，下一步不一定要立刻做新回测；更高杠杆的做法，往往是先把它翻译成统一 schema 可消费的 source bridge。**

## 核心结论（中文摘要）

核心结论：**`PyTrendline` 现在已经可以输出一版最小 event-source sample，足以进入下一步 unified schema 对照与 source-level comparison；但这版 bridge 仍主要覆盖 breakout / touch candidate，还不能直接宣称已经覆盖完整 rebound 研究问题。**

证据如何支持这个结论：**本次完全复用已有 `pytrendline_research` 的 `support_trendlines.csv` 与 `resistance_trendlines.csv`，稳定产出 215 条 representative event rows，其中 breakout=210、touch=5，并已成功生成 `reports/site/factors/pytrendline_event_source/report.html` 与本地样本文件 `outputs/research/pytrendline_event_sample.csv`。**

## 本轮做了什么

本轮只做一个主点：**把 `PyTrendline -> unified event schema` 从概念推进成最小 bridge。**

具体改动：

1. 新增脚本：
   - `scripts/build_pytrendline_event_source_report.py`

2. 复用现有输入：
   - `reports/artifacts/pytrendline_research/support_trendlines.csv`
   - `reports/artifacts/pytrendline_research/resistance_trendlines.csv`
   - `reports/artifacts/pytrendline_research/summary.json`

3. 落地产物：
   - 本地样本：`outputs/research/pytrendline_event_sample.csv`
   - 站点页：`reports/site/factors/pytrendline_event_source/report.html`
   - 摘要：`reports/artifacts/pytrendline_event_source/summary.json`

4. 更新文档 / 目录：
   - `docs/CROSS_ENGINE_MAPPING.md` 增补 `PyTrendline mapping v1`
   - `docs/TODO.md` 将 `PyTrendline -> unified event schema` 第一版试映射标记为完成
   - `Engine Lab · PyTrendline` 轨道页加入第二张卡：
     - `PyTrendline Event Source Bridge v1`

## v1 bridge 的具体口径

这版最小 bridge 的做法是：

- 只取 `is_best_from_duplicate_group == True` 的 representative lines 作为默认样本；
- 统一映射：
  - `engine_line_id` ← `id`
  - `line_side` ← `support / resistance`
  - `line_origin_type` ← `group_best_line`
  - `event_family` ← `is_breakout ? breakout : touch`
  - `event_subtype` ← `breakout_tagged_line / line_touch_candidate`
  - `event_timestamp` ← breakout 用 `breakout_date`，否则回退 `ends_at_date`
  - `line_quality_bucket` / `score_bucket` ← 基于当前样本内 `score` 分位数分桶
  - `slope_bucket` ← 基于当前样本内 `slope` 方向 + 强度分桶

这让 `PyTrendline` 首次具备了一个足够具体的、可喂给 Mainline 的 source-level 样本，而不再只是解释型页面。

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_pytrendline_event_source_report.py scripts/build_trendline_tracks_site.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_pytrendline_event_source_report.py`
- `./.venv/bin/python scripts/build_trendline_tracks_site.py`
- `./.venv/bin/python scripts/build_plans_site.py`

结果验证：

- 生成成功：
  - `outputs/research/pytrendline_event_sample.csv`
  - `reports/site/factors/pytrendline_event_source/report.html`

- 摘要统计：
  - `all_lines = 228`
  - `representative_lines = 215`
  - `breakout_events = 210`
  - `touch_events = 5`
  - `support_lines = 125`
  - `resistance_lines = 90`

- 在线核对：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_event_source/report.html` 返回 200
  - `https://jp.jerrypsy.top/momentum/factors/trendline_pytrendline_track/report.html` 返回 200，并已显示 `Reports included: 2`

## 风险 / 边界

- 这版 bridge 仍然主要覆盖：
  - `breakout`
  - 非 breakout 的 `touch candidate`
- 它还没有覆盖：
  - 完整的 `rebound`
  - `retest_hold`
  - 更细的 state transition
  - 多 symbol / 多 sample 的统一输出

因此它当前的正确定位是：
- **足够进入 unified schema 比较**
- **还不足够直接进入完整 event validation 终局**

## 下一步建议

1. 在同样的 `PyTrendline v1` 基础上，再拆两种输出口径：
   - `representative only`
   - `all valid`

2. 然后做第一轮 source-level 对照：
   - `PyIndicators source vs PyTrendline source`
   - 先只比：
     - breakout vs rebound（PyTrendline 当前会暴露 coverage gap）
     - representative only vs all valid
     - slope / quality buckets

3. 如果 `PyTrendline` 在 source 层看起来像样，再决定是否进入更完整的 event validation / signal 层。

## Commit hash

- `6dc362f` — `feat(momentum): add pytrendline event source bridge`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交：
- `outputs/research/pytrendline_event_sample.csv`

原因是：
- 它位于 repo 既有的 `outputs/` 忽略规则下；
- 本次保留它作为本地产物已足够，不必为这一轮破坏全局 `.gitignore` 约定。
