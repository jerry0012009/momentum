# Rankless fresh intake：cross-asset OFI + VWAP pressure × SHAP microstructure alpha first verdict = background/P0

- 时间：2026-04-03 07:49 UTC
- 执行动作：只执行 `cycle_plan` 第 1 个 pending 小点：`research/quant_digests/2026-04-03_0732_crossasset-ofi-vwap-shap-microstructure-alpha.md`
- 结论：`cross-asset OFI + VWAP pressure × SHAP` 这条 fresh intake 的 first verdict = `background/P0`

## 为什么这轮直接收口到 background/P0
这份 digest 想强调的是“跨币迁移 + SHAP 可解释 + 工程仓库”，但它对应的 raw alpha 主语并不新：

1. **底层主语与已有 intake 高度重合。**
   当前对象的 base alpha 仍是 `OFI + VWAP pressure (+ spread/depth state) -> 短窗方向延续`。这和已经入池的下列对象是同一母线，而不是新的独立 raw alpha：
   - `2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
   - `2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`
   - 以及更广义的 `OBI / microprice / taker-flow continuation` 家族

2. **这轮新增值主要是“迁移性与解释性证据加强”，不是新的 desk 主语。**
   现在多出来的是：
   - 跨资产 SHAP 排序相似
   - 统一 CatBoost + walk-forward 工程化
   - maker/taker stress-test 叙事更完整

   这些都能加强我们对既有 `OFI / imbalance directional continuation` 家族的信心，但它们更像**同一家族的证据加厚**，不是足够独立到要单开一个 fresh front-slot / 正式 Rank 的新对象。

3. **最小实验壳也没有提供与既有 intake 明显不同的可检验增量。**
   它给出的 `1m/3m/5m/15m` 实验骨架，仍然是把 `OFI + VWAP pressure + spread` 聚合后做阈值化方向交易；和已有 `L1 imbalance × VWAP-to-mid × spread gate`/`single-asset OFI + VWAP pressure taker` 的实验壳没有形成新的、可单独命名的 alpha 主语。

## 本轮改变了什么系统认知
`cross-asset OFI + VWAP pressure × SHAP` 不该再作为新的 front-slot fresh intake 独立推进；它更适合作为**既有 microstructure directional continuation 家族的 supporting evidence**，而不是新的可单独 desk 化 raw alpha。

## runtime 回写
- `Fresh intake slot.latest_result`：更新为本轮 `background/P0` first verdict
- `Background pool.latest_parked`：更新为当前对象
- `cycle_plan[1]`：写回 `done`

## 不做的事
- 不分配 Rank：因为本轮 verdict 不是 `keep_P1 / P2 / P3`
- 不改写后续排班：遵循 policy，只执行当前最前的一个 pending 小点
