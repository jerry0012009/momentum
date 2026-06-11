# cross-venue contango shell first verdict：background / P0
- 时间：2026-04-25 13:26 UTC
- 对象：`research/quant_digests/2026-04-25_1152_crossvenue-contango-shell.md`
- 动作：fresh intake first verdict
- 结论：`cross-venue cheap-spot × rich-perp contango capture` first verdict 已诚实收口 `background/P0`。

## 为什么本轮直接收口
这轮允许补的最小 decisive blocker 很明确：repo 默认 `PRICE_DIFF_THRESHOLD = 0.15%` 是否在真实四腿费用、滑点与 funding drag 后，仍留下一个可交易净 spread pocket。

根据当前 digest 已经拆出的规则壳与费率口径，答案是否定的：
- 该 repo 的 base alpha 清楚，是 `long cheapest spot / short richest perp` 的跨 venue contango convergence；
- 但默认 admission 只有 `15 bps`；
- digest 已明确指出，仅 repo 粗费率就接近或超过这一门槛：`Bybit spot taker 10 bps + Gate futures taker 5 bps`，单次开仓已接近 `15 bps`；
- 若看更诚实的 round-trip 口径，则大致来到 `31~50 bps+`，且尚未计入滑点、maker miss、库存分散、funding drag、单腿 orphan risk；
- 因而当前留下来的不是一个已经显形的可交易净 spread pocket，而是一个“要靠 maker-first / 事件窗 / premium 增强 才可能成立”的工程壳。

## 改变系统认知的话
`cross-venue cheap-spot × rich-perp contango capture` 目前更像 fee-sensitive execution shell，而不是已经证明存在统一 fee-after 正 edge 的前排候选；在未拿出至少一个 majors / 事件 pocket 的明确净 spread 余量前，不值得占用 survivor/P2 资源。

## 与升级标准的对应
本轮 success criterion 要求：只有当至少一个 majors / event pocket 在统一 fee-after 口径下仍留下明确正的 contango capture 空间、且不是靠韩国 premium 或不可得库存假设支撑，才 `keep_P1`。

当前 digest 没有提供这样的 pocket：
- 没有一个已钉死的 asset × venue × threshold 组合在统一成本后仍明确为正；
- 现有证据反而说明默认 `15 bps` admission 过薄；
- 韩国 premium 与跨境库存不应被当成 short-cycle desk 的可复用 base alpha。

因此本轮 first verdict 应直接落为 `background/P0`，不进入 survivor。

## 运行态回写要点
- `Fresh intake slot` 当前对象完成 first verdict，收口到 `background/P0`
- front slot 顺延到 `research/quant_digests/2026-04-25_1227_lookbackopt-pairs-voltrail-shell.md`
- `cycle_plan` 第 1 项标记 `done`

## 一句话结果
`cross-venue cheap-spot × rich-perp contango capture` first verdict 已收口 `background/P0`：repo 提供的是完整跨 venue contango execution shell，但默认 `15bps` admission 在统一 fee-after 口径下已明显过薄，当前没有拿出一个不依赖韩国 premium / 理想库存假设的明确净 spread pocket，因此不进入 survivor。