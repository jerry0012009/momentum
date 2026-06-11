# 2026-04-08 21:57 UTC — Polymarket BTC/ETH divergence pair fresh intake 收口为 background

## 本轮执行小点
- target: `research/quant_digests/2026-04-08_1225_polymarket-btceth-divergence-pairs-alpha.md`
- action: 判断 `BTC/ETH 5m divergence-pair discount × hard-expiry reprice` 是否真能压成独立 prediction-market relative-value raw alpha，而不是被既有 family 吸收

## 读取与最小 honesty 检查
- 重读当前 digest：`research/quant_digests/2026-04-08_1225_polymarket-btceth-divergence-pairs-alpha.md`
- 用 `grep -RIn` 检索现有 prediction-market / Polymarket 家族材料，重点命中：
  - `research/quant_digests/2026-03-26_1152_polymarket-5m-divergence-basket-underpricing.md`
  - `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`

## 结论
`2026-04-08_1225` 这条 intake 没有提供新的独立主语；它与 `2026-03-26_1152_polymarket-5m-divergence-basket-underpricing.md` 实际上是同一 repo / 同一 alpha 本体（`BTC_UP+ETH_DOWN` 或 `BTC_DOWN+ETH_UP` 的 5m divergence basket 折价 + hard-expiry payout reprice`），新增 digest 只是重述，不足以证明它区别于既有 prediction-market relative-value family，因此本轮 first verdict 应收口为 `background / P0`，不进入 survivor / P2。

## 为什么不是 keep_P1
1. **不是新对象**：已存在 2026-03-26 的同 repo 同主语 digest，当前 intake 没有形成新的 queue-facing identity。
2. **独特性不足**：现有材料仍停在 prediction-market relative-value / hard-expiry pair-discount 这一级，尚未证明相对已有 `binary basket underpricing`、`complementary outcome mispricing`、`final-window lag arb` 家族存在不可吸收的独立增量。
3. **honesty 证据没有新增**：本轮没有新增盘口深度、真实可成交容量、resolution 延迟或 sweep 成本层面的 decisive 新证据，无法把它从“已知 family 的一个实例”升级成前排候选。

## runtime 影响
- `Fresh intake slot` 维持 `done`，最新结论更新为该对象收口到 `background / P0`
- `Background pool.latest_parked` 改写为该对象
- `cycle_plan[1]` 写回 `done`
- 不触发 rank / survivor / P2 / P3 变化

## 一句话 result
`BTC/ETH 5m divergence-pair discount × hard-expiry reprice` 与 2026-03-26 已收录的同 repo 同主语 digest 重合，当前新增信息不足以形成新的独立 raw alpha，因此本轮 fresh intake 收口为 `background / P0`。
