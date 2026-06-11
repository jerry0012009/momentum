# XGBoost spread inventory ladder · fresh intake first verdict = background / P0

- Time: 2026-04-07 17:56 UTC
- Target: `research/quant_digests/2026-04-07_1711_xgboost-spread-adaptive-maker-alpha.md`
- Cycle action: 作为当前 fresh intake 第一条对象，判断 `predicted-optimal spread × inventory-skew quote ladder` 是否真提供了独立于既有 `maker spread capture / reservation-price skew / optimal market making` 家族的新 raw alpha 主语，还是只是用 `xgboost` 包装传统做市报价宽度与库存倾斜控制
- Verdict: `background / P0`

## 为什么这一步应直接收口
这条 digest 的优点很清楚：它没有停留在抽象 A-S 公式，而是把 `盘口短窗特征 -> 预测最优报价宽度 bucket -> inventory skew / size clamp` 串成了一个可训练、可下单的做市壳。对 desk 来说，这比只谈 fair value 偏移更接近真实执行。

但按当前 bot2/bot3 policy，fresh intake 只有在它压出**独立于既有家族、值得继续占用 survivor 配额的新 raw alpha 主语**时，才配拿到 `keep_P1`。这条对象目前还达不到：

1. **主语仍是老的 maker spread capture。** 真正被交易的东西，依旧是“在低毒性时段报合适宽度、吃到 spread，同时靠 skew 控库存”。`xgboost` 只是把报价宽度选择函数从手工规则换成了监督学习近似器。
2. **增量在控制器，不在 alpha 本体。** `predicted-optimal spread bucket`、`inventory_skew`、`size-down near limits` 的组合，更多是在补 `quote aggressiveness / quote width control` 这一层执行器，而不是产生一个新资产、新时钟或新失衡口袋。
3. **与既有 intake 家族高度重合。** 它和此前已经 intake 过的 `OFI reservation price skew`、`optimal market making`、`inventory-bounded maker spread capture` 属于同一条 maker quoting 家族：差别主要在“如何定宽、如何 skew”，不是“为什么这条边会存在”。
4. **诚实成交问题仍停在 research shell。** digest 自己也承认未来窗口标签、queue position、partial fill、撤单延迟、taker hedge slippage 这些 realism 还没被压成独立可信 pocket；在这种前提下，把它升成 survivor 会把“ML 控价器”误认成“新 alpha 主语”。

## 结论
因此，这一步最诚实的 first verdict 应写成：

> `predicted-optimal spread × inventory-skew quote ladder` 仍属于既有 `maker spread capture / reservation-price skew / optimal market making` 家族里的报价宽度控制与库存偏移工程细化；`xgboost` 改变的是控制器形式，不足以构成独立的新 raw alpha 主语，因此本轮直接记为 `background / P0`，不进入 survivor。

## Runtime write-back
- `Fresh intake slot.latest_result` 更新为本次 first verdict
- `Fresh intake slot.latest_result_record` 指向本日志
- `Fresh intake slot.status` 写回 `done`
- `Background pool.latest_parked` 更新为本对象
- `cycle_plan` 第 1 条写回 `done`
