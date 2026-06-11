# Rank 224 / BTC reference + dual-spread copula conditional mispricing：fresh intake keep_P1

- 时间：2026-03-28 14:24 UTC
- 对象：`research/quant_digests/2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1`
- Rank：`224`

## 这轮做了什么
按当前 `cycle_plan` 执行这条 fresh intake，回答它是否真的是新的、值得入板的 raw alpha，还是旧 `pairs / z-score / cointegration` 家族的换壳。

## 本轮判断
结论不是 `promote_P2`，也不是直接丢背景，而是 **`keep_P1`**。

原因很简单：
1. **它确实不是 plain pairs 换皮。** 这条线的本体不是单 spread 偏离，而是 `BTC` 参考腿下两条 spread 的 **relative mispricing**：用 copula 条件概率决定“哪条 spread 被高估/低估”，交易的是 `spread-vs-spread` 回归，而不是传统 `single-spread z-score` 回归。
2. **它已经是完整 raw alpha skeleton。** formation / trading 切分、pair funnel、entry/exit、成本口径都在文中给全了，且公开 Binance perp 数据可复现。
3. **但当前还不值得直接升 `P2`。** 我们最近已经 intake 了多条 `pairs / stat-arb / dynamic cointegration / factor residual / pair-book construction` 线；这篇真正新增的是 `conditional mispricing signal layer`，而不是一个已证实在 `15m` 仍能留下净边的新 pocket。现阶段仍缺最关键一步：**在同一 formation/trading split、同一成本口径下，copula dual-spread 是否真的比 plain dual-spread / single-spread baseline 多出净增益**。在这一步没做前，直接升 `P2` 会把“结构新颖”误当成“edge 已验证”。

## 会改变系统认知的话
`Rank 224 / BTC reference + dual-spread copula conditional mispricing` 不是旧 pairs/z-score 家族的简单换壳，而是值得保留的 `signal-layer upgrade` 型 raw alpha；但在还没完成 `copula vs plain z-score / dual-spread baseline` 的同口径对照前，证据只够 `keep_P1`，不够直接升 `P2`。

## 唯一合法下一步（survivor）
若后续给它 survivor 唯一 follow-up，应该直接做一件事：
- 在同一批 `BTC` 参考 spread 候选、同一 formation/trading 切分、同一 after-cost 假设下，正面对照：
  1. `single-spread z-score`
  2. `dual-spread plain threshold / z-score`
  3. `dual-spread copula conditional mispricing`
- 目标不是继续补论文背景，而是回答：**copula 这层是否留下独立净增益，还是复杂度上升但净边不增。**

若对照后没有明确增益，这条线就应按 `keep_P1 后转 background` 收口，而不是继续在 `copula family / AIC / tail dependence` 上无限细化。
