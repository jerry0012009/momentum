# Confirmation ladder 报告接入主线并沉淀结论

## 为什么这次选这个

这轮最自然的延续主线，不是再开新题，而是把刚刚跑完的 `trendline_confirmation_ladder` 报告真正接到新的站点结构里。

前面几轮已经完成了三件事：
1. 把项目口径改成 `Structure-Event Mainline`；
2. 把 `PyIndicators / PyTrendline` 降成 `Engine Labs`；
3. 用缓存/断点续跑把 confirmation ladder 长任务跑完。

因此这轮最值得复用/借鉴的点是：**长任务一旦产物落地，下一步不要停在“文件跑出来了”，而要立刻把它接回主线目录、TODO 和阅读顺序，让研究结论变成可复用知识，而不是孤立文件。**

## 核心结论（中文摘要）

核心结论：**更强的 breakout confirmation 并没有把 breakout 这条线真正救起来；真正值得继续看的，仍然是 retained rebound subsets 里最宽松的一档 inside confirmation。**

证据如何支持这个结论：**在 2Y 样本里，breakout 侧最像样的一档 `breakout hold = 3` 也只有 `positive_asset_ratio=50.00%`、`mean_total_return=-2.57%`；而 retained rebound 子集（`flat + down_high`）里，`rebound inside = 0` 给出 `positive_asset_ratio=75.00%`、`mean_total_return=5.57%`、`trade_retention=100.00%`，说明“更强确认”对 breakout 没有形成有效拯救，但对 rebound 而言，过强确认反而未必优于宽松口径。**

## 做了什么改动

本轮主点只有一个：**把 confirmation ladder 正式并入 Mainline。**

具体改动：

1. **将 `Trendline Confirmation Ladder Report` 接入主线阅读顺序**
   - 重新生成 `Structure-Event Mainline` 页面；
   - 现在 Mainline 已从 `Reports included: 4` 升到 `Reports included: 5`；
   - 第 4 页正式变成 `Trendline Confirmation Ladder Report`。

2. **把 ladder 完成状态写回 `docs/TODO.md`**
   - 勾选：`完成 Trendline Confirmation Ladder Report 的最终生成与站点接入`；
   - 勾选：`在 mainline 中明确回答更强 confirmation 是改善质量还是只是样本塌缩`；
   - 把结论沉淀成主线语言，而不是只留在单独报告页里。

3. **同步更新站点镜像页**
   - 更新 `plans/momentum_todo.html`；
   - 更新 `Structure-Event Mainline`、`PyIndicators Lab`、`PyTrendline Lab`、首页与 plans 索引；
   - 发布 `trendline_confirmation_ladder/report.html` 到站点目录。

## 验证 / 证据

最小必要验证：

- 重新构建：
  - `./.venv/bin/python scripts/build_plans_site.py`
  - `./.venv/bin/python scripts/build_trendline_tracks_site.py`
  - `./.venv/bin/python scripts/build_site_index.py`
- 发布：
  - `reports/site/factors/trendline_confirmation_ladder/report.html`
  - `reports/site/factors/structure_event_mainline/report.html`
  - `reports/site/plans/momentum_todo.html`
  - 以及相关 index 页面

在线验证：

- `https://jp.jerrypsy.top/momentum/factors/structure_event_mainline/report.html`
  - 返回 200；
  - 页面显示 `Reports included: 5`，说明 ladder 已进入主线顺序。

- `https://jp.jerrypsy.top/momentum/factors/trendline_confirmation_ladder/report.html`
  - 返回 200；
  - 页面 headline 已能直接读到两条最关键结论：
    - 2Y breakout 最像样的一档仍然不够强；
    - 2Y retained rebound 子集里，`inside = 0` 最值得继续看。

补充证据（来自生成产物）：

- `breakout_ladder_summary.csv`
  - `60m_730d / breakout hold = 3`
    - `positive_asset_ratio = 0.5`
    - `mean_total_return ≈ -2.57%`
    - `trade_retention ≈ 75.9%`

- `rebound_retained_subset_summary.csv`
  - `60m_730d / retained_union / rebound inside = 0`
    - `positive_asset_ratio = 0.75`
    - `mean_total_return ≈ +5.57%`
    - `trade_retention = 1.0`

## 风险 / 边界

- 这页当前仍是 **operational confirmation ladder**，不是完整的 `raw_breach → close_confirm → confirm1 → confirm3 → retest_hold` 全事件宇宙。
- 当前 ladder 的样本来源仍主要是 `PyIndicators` 这一侧；还没有把 `PyTrendline` source 接进来做同口径比较。
- 本轮只提交了站点页面与 TODO 变更，没有把 `reports/artifacts/trendline_confirmation_ladder/` 的大体积中间产物一起提交，避免把 31MB 级别的数据和无关脏文件混进本轮 commit。

## 下一步建议

1. 在主页或 mainline 顶部补一个最小 **decision board**：
   - `breakout` → `park / weak`
   - `rebound retained subsets` → `continue / feature candidate`
   - `pytrendline source` → `unknown / need bridge`

2. 按刚补好的 `Cross-Engine Mapping` 文档，做第一版：
   - `PyTrendline -> unified event schema` 试映射；
   - 不急着再做新回测，先把 source bridge 建起来。

## Commit hash

- `8f9f063` — `feat(momentum): publish confirmation ladder mainline page`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交：
- `reports/artifacts/trendline_confirmation_ladder/` 下的大体积缓存与明细表；
- 与本轮无关的 reading 页面脏文件；
- workspace 中其它无关 untracked 文件。
