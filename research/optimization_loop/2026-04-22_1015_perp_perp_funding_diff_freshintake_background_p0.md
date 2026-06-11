# 2026-04-22 10:15 UTC — perp-perp funding diff z-fade fresh intake 收口 background/P0

## 本轮执行对象
- cycle_plan 第 1 项
- target: `research/quant_digests/2026-04-22_0958_perp-perp-funding-diff-zfade-shell.md`
- action: fresh intake：回答 `cross-venue perp-perp funding spread z-score fade × child execution` 在最小多 venue / 多资产 / child-execution 现实下，是否还能留下独立新增 after-cost alpha

## 读取到的最小决定性证据
来自 digest 附带公开 portability probe（Binance/Bybit，BTC/ETH，最近 200 个 8h funding 点）：
- `BTCUSDT` 平均绝对 funding spread 约 `0.377bps/8h`，`p95≈0.897bps`，最大仅 `1.473bps`
- `ETHUSDT` 平均绝对 funding spread 约 `0.388bps/8h`，`p95≈0.978bps`，最大仅 `1.570bps`
- repo 默认 admission `|spread|>=2bps + |z|>=2` 在 `BTC/ETH` 上都是 `0` 次触发
- 就算把绝对 spread 下调到 `0.5/1.0bps`，事件也仍然稀疏：`BTC 7/4` 次，`ETH 11/6` 次；而下一期收敛后的 spread 中位数只剩约 `0.28~0.46bps`

## 本轮诚实判断
这已经足够回答当前 fresh intake 的唯一 decisive blocker：
- 这条线的“方向正确性”并不是问题，spread 回归方向感存在；
- 但当前可见的 `BTC/ETH × Binance/Bybit` recent shell 厚度只有亚 `1bps` 级，明显不够支撑普通双腿 child execution；
- 同时它与已 live 的 funding/basis / carry family 高重叠，当前并没有留下“至少两个非单一 asset / venue-pair 支撑的独立新增 after-cost alpha”；
- 因此现阶段更像 `稀疏 carry / funding-disagreement router / maker-first infra hint`，不是值得前排保留的新 raw alpha front object。

## verdict
`cross-venue perp-perp funding spread z-score fade × child execution` 的 fresh intake first verdict 已诚实收口 `background/P0`：公开 recent portability 里 `BTC/ETH` 跨 Binance/Bybit 的 funding spread 常态只有亚 `1bps/8h`、repo 默认 `2bps` admission 完全不触发；即使下调到 `0.5~1.0bps` 也只剩稀疏事件与约 `0.28~0.46bps` 的下一期收敛厚度，不足以证明它相对已 live funding/basis 家族仍留下至少两个非单一 asset / venue-pair 支撑的独立新增 after-cost alpha，因此当前只保留为稀疏 carry / router / maker-first execution hint，不进入 survivor。

## runtime impact
- 当前对象直接转入 `Background pool`
- 未形成 `keep_P1`，因此不分配新 Rank
- `Fresh intake slot` 前移到下一条 conditional fresh intake：`research/quant_digests/2026-04-22_0908_macd-divergence-crossover-feetrap.md`
