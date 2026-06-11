# bot3 optimization loop — NSGA-II pair admission first verdict

- 时间：2026-04-03 13:24 UTC
- 执行轮次：13 分钟自动执行
- 对象：`research/quant_digests/2026-04-03_1135_nsga2-pair-admission-alpha.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮判断
这条题材的可交易主语仍然是已有的 `pairs spread mean reversion`。

`NSGA-II / Pareto` 在这里提供的新增信息，主要是：
1. 把 pair selection / bucket construction 写成多目标优化问题；
2. 用 `return / risk / turnover(or fragility)` 之类目标做 pair admission；
3. 帮助从一组可做的 MR pair 里挑出更稳的一篮子。

这对 desk 有价值，但它更像 **pairs engine 的 shared admission upgrade**，而不是新的独立 raw alpha 主语。原因很直接：
- entry / exit 仍依赖已有的 `spread / z-score / OU / percentile` 壳；
- 真正赚钱的 base alpha 仍是 pair spread 回归，而不是 NSGA-II 本身；
- 当前 digest 没有给出足够强的新 alpha 主语，更多是在已有 pairs 家族上增加一个多目标筛选层。

## 为什么不进前排
按当前 policy，fresh intake 只有在能形成新的、可独立 desk 化的 alpha 主语时，才值得拿 `keep_P1` 或更高前排位。

这条对象虽然有研究价值，但当前更适合被归档为：
- pairs 研究栈里的 admission / ranking 参考件；
- 以后若要升级现有 pairs engine，可作为 shared overlay / admission layer 再调用；
- 不应占用当前前排的独立 raw alpha 名额。

## runtime 改写
- `Fresh intake slot` 改写为本对象，并把 latest_result 写成 `background/P0`
- `Background pool` 更新为本对象的最新 parked 记录
- `cycle_plan` 第 2 条写回 `done`

## 一句话结果
`NSGA-II / Pareto pair admission × spread shell` 更像已有 pairs MR 家族的 admission 升级件，不是新的独立 raw alpha，因此本轮 first verdict 直接记入 `background/P0`。
