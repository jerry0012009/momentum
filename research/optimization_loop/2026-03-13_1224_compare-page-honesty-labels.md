# 固定 compare-page honesty labels，并修正页面可读性

## 为什么这次选这个

这轮继续严格沿最近几轮的 confirmation protocol 线程推进，没有切回新研究分支，也没有重跑实验，而是顺着上一轮刚补好的 `source onboarding checklist` 再推进一个很小、但很影响页面可读性的点。

最近几轮已经把这些东西陆续补进 protocol 里：
- native -> mainline 最小映射
- source-to-protocol 示例行
- 字段分层表
- source onboarding checklist

但还差一个很实用的收口：**当 source 第一次进入 compare 页面时，到底应该挂什么“诚实标签”来提醒读者 coverage 边界？**

如果这一步不补，页面作者很容易各写各的说法：
- 有时说 baseline source
- 有时说 raw-only
- 有时说 partial
- 有时又只在正文里口头解释

这会让 compare 页可读性下降，也更容易让读者误把“已接入 compare”理解成“coverage 已经完整”。

这轮最值得复用/借鉴的点是：**当 protocol 已经足够细时，下一步最值钱的不是再加更多技术名词，而是固定一套页面级 honesty labels，让读者能一眼看懂 source 的成熟度和边界。**

## 核心结论（中文摘要）

核心结论：**`TRENDLINE_CONFIRMATION_PROTOCOL` 现在已经固定了一套 `compare-page honesty labels (v1)`，可以用统一标签表达 source 的 coverage 与定位边界，例如 `source #1 / baseline compare source`、`raw-breach-only source`、`partial ladder coverage`、`rebound-only source`、`mechanism-backed but not full-event-universe`。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.4 compare-page honesty labels (v1)`，并给出 `PyIndicators / PyTrendline v1 / Optimal Stopping` 的默认示例；重建后的 `reports/site/plans/trendline_confirmation_protocol.html` 与 `reports/site/plans/momentum_todo.html` 已同步显示该新章节和对应 TODO 勾选。**

## 本轮做了什么改动

本轮只做一个主点：**固定 compare-page honesty labels，并顺手修正页面可读性。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 新增：
     - `4.4 compare-page honesty labels（v1）`
   - 固定 5 类默认标签：
     - `source #1 / baseline compare source`
     - `raw-breach-only source`
     - `partial ladder coverage`
     - `rebound-only source`
     - `mechanism-backed but not full-event-universe`

2. 在同一节中明确每个标签的：
   - 适用场景
   - 读者应如何理解

3. 补了 3 个当前默认示例：
   - `PyIndicators`
     - 推荐标签：`source #1 / baseline compare source` + `partial ladder coverage`
   - `PyTrendline v1`
     - 推荐标签：`raw-breach-only source`
   - `Optimal Stopping`
     - 推荐标签：`mechanism-backed but not full-event-universe`

4. 修正页面可读性
   - 最初我先用 markdown 表格写了这组标签定义；
   - 重建 plans 页面后发现镜像页里表格会被压成一整段，不够可读；
   - 因此同轮改成了列表版定义，确保镜像页面能稳定渲染。

5. 更新 `docs/TODO.md`
   - 新增并标记为 `[x]`：
     - `在 confirmation protocol 中固定 compare-page honesty labels (v1)`
   - 结果说明里明确：
     - 已统一这 5 类标签
     - 并补了 `PyIndicators / PyTrendline v1 / Optimal Stopping` 的默认示例

6. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`4.4 compare-page honesty labels（v1）`
     - 已出现：
       - `source #1 / baseline compare source`
       - `raw-breach-only source`
       - `partial ladder coverage`
       - `rebound-only source`
       - `mechanism-backed but not full-event-universe`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 在 confirmation protocol 中固定 compare-page honesty labels（v1）。`

## 风险 / 边界

- 这轮没有新增新的实验或比较结果；
- 它解决的是 **compare 页面上 source 边界表达不一致** 的问题，而不是直接新增 alpha 证据；
- 这些 honesty labels 目前仍是 `v1`，后面如果新 source 类型变多，标签体系可能还需要再扩充，但现在先固定一版比继续口头解释更有价值。

## 下一步建议

1. 如果继续沿 protocol 线程推进，下一步可以考虑：
   - 把这组 honesty labels 回挂到具体 compare / foundation 页面里，而不只停留在 protocol 文档；
2. 如果转回实证推进，则可以开始：
   - 仅对已明确挂好 honesty label 的 source 做第一轮真实 compare，避免读者误读 coverage 完整度。

## Commit hash

- 已提交：`docs(momentum): add compare-page honesty labels`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。