# pre-pump anomaly composite fresh intake -> background/P0

- 时间：2026-04-23 19:26 UTC
- 对象：`research/quant_digests/2026-04-23_1710_prepump-anomaly-composite-alpha.md`
- 轮次角色：bot3
- 结论：`background/P0`

## 本轮只补的最小 decisive blocker
验证这条 `pre-pump anomaly composite` 是否已经留下**可独立排队的 cross-sectional after-cost anomaly pocket**，而不是只剩 `volume / OI / funding / top-trader` 的拥挤度 router 提示。

## 最小复核方法
用 Binance public data 做 repo 思路的最小可执行 proxy，避免把它误吹成已经可前排保留的 raw alpha：

- universe：`BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/BNB` perp
- bar：`1h`
- 信号：
  - `24h volume / abs(24h return)` 作为 volume-price dislocation
  - `24h OI change`
  - `24h top-trader long/short ratio change`
  - 最近已知 funding（负 funding 更偏多头挤仓）
- 组合：按 digest/repo 权重近似打分（`0.25 vol + 0.25 funding + 0.20 OI + 0.15 L/S`；Fear & Greed 不纳入最小首判）
- 过滤：沿用 repo 精神，排除 `abs(24h move)>20%` 和 `abs(24h move)<0.3%` 的对象
- 检验：每小时取 `top1` / `top3`，看未来 `2h / 4h / 8h` 收益，并统一扣 `8bps roundtrip`

## 结果
样本共 `468` 个 hourly events（当前公开口径只覆盖 `2026-04`）。

### 组合表面结果
- `top1 -> +2h`: `mean gross ≈ +7.78bps`，`net8 ≈ -0.22bps`
- `top1 -> +4h`: `mean gross ≈ +13.73bps`，`net8 ≈ +5.73bps`
- `top1 -> +8h`: `mean gross ≈ +27.11bps`，`net8 ≈ +19.11bps`
- `top3 -> +4h`: `mean gross ≈ +10.69bps`，`net8 ≈ +2.69bps`

看起来像是有一点 continuation，但 decisive blocker 在下面两点：

### blocker 1：当前可见正边际高度集中在少数币，不满足“非单币 pocket”
`top1 @ +4h net8` 的 symbol 分布与均值：

- `BTC`：`233` 次，`mean net8 ≈ -0.27bps`
- `ETH`：`72` 次，`mean net8 ≈ -18.98bps`
- `SOL`：`73` 次，`mean net8 ≈ +25.99bps`
- `XRP`：`37` 次，`mean net8 ≈ +50.36bps`
- `DOGE`：`37` 次，`mean net8 ≈ -4.13bps`
- `AVAX`：`6` 次，`mean net8 ≈ +79.77bps`
- 其余更少

也就是说，当前 after-cost 余量不是一个广谱 cross-sectional anomaly shell，而更像少数 `SOL/XRP/AVAX` 挤仓窗口拉动；最大出现频率的 `BTC/ETH` 并没有保住同向正边际。

### blocker 2：当前可见正边际高度集中在少数日期，不满足“非单拥挤窗口 lucky-run”
按日聚合 `top1 @ +4h net8`：

- 最佳单日 `2026-04-07` 贡献约占总净值 `90.07%`
- 最佳 `top3` 天合计贡献约 `176.55%`
- 同时最近几天明显回吐：
  - `2026-04-18 ≈ -1181.55bps`
  - `2026-04-19 ≈ -1172.00bps`
  - `2026-04-11 ≈ -962.01bps`

这说明当前表面均值主要来自少数拥挤爆发日，而不是稳定、可迁移的 anomaly pocket。

## runtime verdict
`pre-pump anomaly composite` 已完成 fresh intake first verdict 并收口 `background/P0`：最小 public proxy 虽显示 `top1` 在 `+4h/+8h` 有表面正 gross，但 after-cost 余量高度集中在 `SOL/XRP/AVAX` 等少数币与少数挤仓日期；`BTC/ETH` 这两个最大出现主语未保住同向正边际，且单日贡献集中到 `top1 day≈90.07% / top3 days≈176.55%`，因此它没有证明自己已形成可独立排队的、非单币且非单窗口 lucky-run 的 cross-sectional anomaly alpha，当前只保留为 `crowding / volume-price / OI build-up` router 提示。
