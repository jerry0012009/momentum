# 为 event-level validation 写死默认 horizon 与指标模板

## 为什么这次选这个

这轮没有新开题，而是直接延续刚刚用户对主线的澄清：

- 主线不是继续停在 bridge / 概念层；
- 主线应该是拿 `PyTrendline` 定义出来的事件去做 event-level observation / validation；
- 同时 `E. External Alpha / Literature Scout` 也应当被认真使用，并尽量直接服务当前主线问题。

在这个上下文下，当前最值得补的一步，不是立刻再开一份新回测，而是先把 **event-level validation 的默认执行模板** 写死。这样后面的自动任务和人工任务都会少走弯路，不会每次都重新讨论“看哪些 horizon、报哪些指标”。

这轮最值得复用/借鉴的点是：**当主线方向已明确时，优先把默认 protocol 固化成文档，往往比立刻新增一次零散实验更能提高后续自动循环的有效性。**

## 核心结论（中文摘要）

核心结论：**当前 `momentum` 主线已经足够明确，应该把 event-level validation 的默认观察口径固定下来；默认使用 `+1 / +3 / +6 / +12 bars` 作为 horizon，并统一报告 `up_ratio / mean / median / IQR / sample_count`。**

证据如何支持这个结论：**当前 TODO 已明确主线是 `PyTrendline event-level validation -> cross-engine comparison -> evidence 足够后再进 signal/strategy`；如果 horizon 与指标模板不固定，后续每轮任务都会在 protocol 层重复发散，而无法高效积累可横向比较的证据。**

## 本轮做了什么

本轮只做一个主点：**把 event-level validation 的默认模板写进 TODO，并同步网页镜像。**

具体改动：

1. 在 `A1-D. event-level validation` 下补充默认模板 v1
   - 默认 horizon：`+1 / +3 / +6 / +12 bars`
   - 可同步换算成人类更直观的时间：
     - `5m` bar：`5m / 15m / 30m / 60m`
     - `30m` bar：`30m / 90m / 180m / 360m`
     - `60m` bar：`1h / 3h / 6h / 12h`
   - 默认最小指标模板：
     - `up_ratio_after_h`
     - `mean_forward_return_h`
     - `median_forward_return_h`
     - `iqr_forward_return_h`
     - `positive_asset_ratio_h`（跨资产时）
     - `sample_count`

2. 在 `A2-C` 与 `B1-B` 的 `PyTrendline event-level validation` 待办下，补充“默认按模板 v1 执行”
   - 明确后续默认看：
     - 固定 horizon
     - 固定 forward-return 统计

3. 在 `E2-B. quality / reproducibility audit` 下补一条
   - 若材料与主线直接相关，额外标记它服务哪类主线用途：
     - `event source design reference`
     - `validation metric / protocol reference`
     - `confirmation / retest / filter reference`
     - `clean-room replication candidate`

4. 重建并发布：
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python scripts/build_plans_site.py`
- 同步发布 `plans/momentum_todo.html`

结果检查：

- `docs/TODO.md` 已出现默认 horizon / 默认指标模板说明；
- 站点镜像 `https://jp.jerrypsy.top/momentum/plans/momentum_todo.html` 已同步更新。

## 风险 / 边界

- 这次没有新增任何统计结果，只是把 protocol 固化；
- `+1 / +3 / +6 / +12 bars` 是当前默认模板，不代表未来不能因事件频率或资产特征做补充；
- 当前模板适合作为第一轮统一对照口径，不是最终唯一口径。

## 下一步建议

1. 直接按这个模板，做第一轮 `PyTrendline event-level validation`；
2. 再做 `PyIndicators source vs PyTrendline source` 的第一轮 source-level 对照；
3. E 模块的材料筛选也优先找能支撑：
   - validation metric
   - confirmation / retest
   - clean-room replication

## Commit hash

- `d2a296e` — `docs(momentum): add validation template defaults`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交其它 reading / factors / site 页面脏文件，因为它们不属于这次“默认 validation 模板”这个最小闭环。
