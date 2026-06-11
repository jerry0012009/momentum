# 为 PyTrendline 落地第一版 event-level validation

## 为什么这次选这个

这轮没有新开题，而是直接延续刚刚已经澄清的主线：

- `PyTrendline event source bridge` 已经完成；
- 下一步不该继续停在概念桥接层；
- 应该直接拿 `PyTrendline` 定义出来的事件去看：事件之后的一段时间，价格到底偏涨还是偏跌。

因此这轮最值得做的，不是再补更多文档，而是把 bridge 进一步推进成 **真正的 observation / validation 页面**。

这轮最值得复用/借鉴的点是：**当 event source 已经准备好后，最小可行的下一步不是上策略，而是先做固定 horizon 的 forward-return 观察，这样能最快把“事件定义”变成“事件证据”。**

## 核心结论（中文摘要）

核心结论：**`PyTrendline` 现在已经不只是“能产出 event sample”，而是已经能直接进入第一轮 event-level validation；但在当前 `BTC-USD / 10d / 5m` 样本里，breakout 事件整体 forward-return 仍偏弱，暂时没有给出很强的正面信号。**

证据如何支持这个结论：**本次直接对齐 `pytrendline_event_sample.csv` 与同窗口 `candles_window.csv`，为 215 条事件计算 `+1 / +3 / +6 / +12 bars` 的 forward return；结果显示 breakout 样本在四个 horizon 上的 `mean_forward_return` 分别约为 `-0.02% / -0.03% / -0.04% / -0.08%`，而 `touch` 样本数很少（仅 5 条），暂时只能作为弱提示，不能下强结论。**

## 本轮做了什么

本轮只做一个主点：**把 `PyTrendline event sample` 推进成第一版 event-level validation。**

具体改动：

1. 新增脚本：
   - `scripts/build_pytrendline_event_validation_report.py`

2. 复用现有输入：
   - `outputs/research/pytrendline_event_sample.csv`
   - `reports/artifacts/pytrendline_research/candles_window.csv`

3. 生成产物：
   - `reports/artifacts/pytrendline_event_validation/summary.json`
   - `reports/artifacts/pytrendline_event_validation/overall_by_family_horizon.csv`
   - `reports/artifacts/pytrendline_event_validation/side_summary_h6.csv`
   - `reports/artifacts/pytrendline_event_validation/slope_summary_h6.csv`
   - `reports/artifacts/pytrendline_event_validation/quality_summary_h6.csv`
   - `reports/artifacts/pytrendline_event_validation/event_forward_detail.csv`
   - `reports/site/factors/pytrendline_event_validation/report.html`

4. 更新站点导航：
   - `Engine Lab · PyTrendline` 现在已包含第 3 张卡：
     - `PyTrendline Event Validation v1`

5. 更新 TODO：
   - 将 `PyTrendline event-level validation` 第一轮标记为已完成；
   - 明确说明这版只覆盖 bridge v1 的可见范围：
     - breakout
     - touch candidate
     - support vs resistance
     - slope / quality buckets
   - 更完整的 `rebound / retest / representative only vs all valid` 仍待 bridge v2。

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_pytrendline_event_validation_report.py scripts/build_trendline_tracks_site.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_pytrendline_event_validation_report.py`
- `./.venv/bin/python scripts/build_trendline_tracks_site.py`
- `./.venv/bin/python scripts/build_plans_site.py`

在线验证：

- `https://jp.jerrypsy.top/momentum/factors/pytrendline_event_validation/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/factors/trendline_pytrendline_track/report.html` 返回 200，且 `Reports included: 3`

样本摘要：

- `symbol = BTC-USD`
- `timeframe = 5m`
- `sample_key = BTC-USD_10d_5m_window96`
- `total_events = 215`
- `matched_events = 215`
- `breakout_events = 210`
- `touch_events = 5`
- 默认 horizon：`+1 / +3 / +6 / +12 bars`

关键统计（`overall_by_family_horizon.csv`）：

- `breakout`
  - `+1 bars`：`sample_count=210`，`up_ratio=53.33%`，`mean_forward_return≈-0.02%`
  - `+3 bars`：`sample_count=208`，`up_ratio=42.79%`，`mean_forward_return≈-0.03%`
  - `+6 bars`：`sample_count=203`，`up_ratio=50.25%`，`mean_forward_return≈-0.04%`
  - `+12 bars`：`sample_count=190`，`up_ratio=48.95%`，`mean_forward_return≈-0.08%`

- `touch`
  - `+6 bars`：`sample_count=3`，`up_ratio=100%`，`mean_forward_return≈+0.15%`
  - 但样本太小，当前只能视为提示，不足以下结论。

## 风险 / 边界

- 当前只是一份 **单一 BTC-USD / 10d / 5m / window96** 的 v1 观察页；
- bridge v1 主要覆盖 breakout 与少量 non-breakout candidate，不代表完整 `rebound / retest` 语义；
- 因此这页更适合回答“能不能开始观察”“当前 breakout 这类对象在单窗里大致像什么”，而不适合直接当成终局 alpha 证明。

## 下一步建议

1. 先做 `PyIndicators source vs PyTrendline source` 的第一轮 source-level 对照；
2. 再决定要不要补 `PyTrendline bridge v2`：
   - `representative only vs all valid`
   - 更完整 `rebound / retest`
3. E 模块继续优先找：
   - `rebound / retest / confirmation` 外部证据
   - 能帮助解释为什么 breakout 弱、哪些 confirmation 更合理的材料。

## Commit hash

- `c753a86` — `feat(momentum): add pytrendline event validation v1`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交与本轮无关的其它 site / reading 脏文件，因为它们不属于这次 `PyTrendline event-level validation v1` 的最小闭环。
