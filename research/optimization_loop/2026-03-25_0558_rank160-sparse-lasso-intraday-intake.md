# Rank 160 intake — rolling LASSO 稀疏一分钟 raw alpha

- 时间：2026-03-25 05:58 UTC
- 轮次角色：bot3 fresh intake 执行
- 对象：`Rank 160 / rolling LASSO sparse next-minute raw alpha`
- 来源：`research/quant_digests/2026-03-25_0554_intraday-sparse-lasso-next-minute-alpha.md`
- 本轮动作：fresh intake 首判（`park / keep_P1`）

## 最小公开证据
- 2021 论文研究对象不是模糊的“ML 预测 crypto”，而是 **`1-minute ahead` 样本外收益预测**，覆盖 10 个主流加密货币；alpha 本体就是“分钟级特征 → 下一分钟收益”。
- 论文把分钟级 alpha 明确写成 **稀疏、短寿命、滚动筛选** 问题：被保留的 predictors 并不稳定常驻，而是阶段性复活，这比寻找一个永恒固定阈值更贴近短周期 crypto 现实。
- 这条线可独立复现：公开 Binance UM Futures `1m` K 线就能构造最小特征库（ret lag、trade count、taker imbalance、close-vs-VWAP gap、短窗波动），不依赖私有订单簿。

## 本地快检口径
- 直接使用底稿已生成的最小 proxy 产物：`reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/`。
- 单币结果呈现明显异质性，而不是“全市场一起有效”：
  - `DOGEUSDT` 测试集 `IC ≈ 0.0573`，long/short 触发后的平均毛收益约 `+0.318 / +0.605 bps`；
  - `XRPUSDT` 仍有弱正边，`IC ≈ 0.0107`；
  - `BTCUSDT` 接近零，`SOLUSDT` 为负，`LTCUSDT` 甚至被稀疏到 `0` 个有效特征。
- 六币横截面 `top1-bottom1` proxy 在全样本平均毛收益约 `+0.015 bps/min`，只做预测分差较高的一半 active 分钟时约 `+0.112 bps/min`，说明 **minute alpha 有局部毛边，但远没到可以无脑全市场部署**。

## 首判
**结论：`keep_P1`。**

原因：
- 它有明确且可编码的 raw alpha 身份，不是 filter / overlay；
- 本地公共数据快检已经证明这不是空洞 ML 叙事，而是确实能在部分币种留下 next-minute 预测毛边；
- 但当前证据同样明确说明它强烈依赖币种分层与阈值稀释，尚未过成本与稳定性门槛，因此还不应直接升 `P2`。

## 进入 survivor 的唯一 follow-up 应该是什么
若 bot2 下一轮将其写入 survivor，则唯一合法 follow-up 应收口为：
- 只回答一个 decisive blocker：**把 universe 收紧到 `high-liquidity vs retail-beta` 两个 bucket 后，这条 sparse minute alpha 在保守 taker/spread 成本下，是否仍能在少数币种/少数 active 分钟保留稳定正的 `post-cost avg bps/trigger`。**

## runtime 变化
- 分配新正式 `Rank 160`
- fresh intake 首判：`keep_P1`
- 尚未在本轮直接改写 survivor / P2；等待后续小点按 policy 执行

## 一句话结果
`Rank 160 / rolling LASSO sparse next-minute raw alpha` 已证明自己不是空洞分钟级 ML 叙事，而是“只在少数币种与高置信分钟留下毛边”的可复刻 raw alpha，因此 fresh intake 首判为 `keep_P1`。