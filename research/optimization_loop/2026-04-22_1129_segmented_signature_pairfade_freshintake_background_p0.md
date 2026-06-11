# 2026-04-22 11:29 UTC — segmented-signature pair fade fresh intake -> background/P0

## Target
- `research/quant_digests/2026-04-22_1026_segmented-signature-pairfade-shell.md`

## Why this step
- 这是当前 `cycle_plan` 最前的 pending 小点。
- 目标不是重做完整 signature 理论，而是只回答一个最小 decisive blocker：`spread z-score fade × segmented-signature admission` 相对已 live / 已 intake 的 pairs family，是否留下独立新增的 after-cost admission 价值。

## Minimal honesty / portability check
- 数据：`reports/artifacts/scout_tau_band_breakout_15m/cache/` 里的现成 `BTCUSDT / ETHUSDT / SOLUSDT` `120d 15m` 缓存。
- Pair：`BTC/ETH`、`ETH/SOL`、`BTC/SOL`。
- 对照：
  1. baseline：rolling-beta `spread z-score fade`
  2. gated：baseline + 简化 `segmented-signature` proxy gate
- gate 定义（最小可迁移近似，不冒充论文精确复现）：
  - `same-direction gate`：两腿最近 `w` bar log 变动同向；
  - `cohesion gate`：rolling return-corr 高于其 trailing median；
  - 只在两者同时通过时允许入场。
- 参数：`window = 24 / 60`，`entry z = 2.0`，`exit z = 0.5`，`max_hold = 16 bars`，统一双腿 round-trip 成本 proxy `16bps`。
- honesty guard：只用前一根 bar 的信号，下一根 open 入场/出场；不使用未来信息。
- artifact：`reports/artifacts/segsig_pairfade_first_verdict_20260422_1129.json`

## Key result
六个 pair/window 单元里，gate 都只是把交易数砍掉约 `44%~51%`，但没有把任何单元翻成 after-cost 为正；也没有留下满足“至少两个非单一 pair / window 支撑的新增 after-cost admission 价值”的正单元。

### Summary snapshot
- `BTC/ETH, w=24`：baseline `-16.26bps/trade` -> gated `-16.23bps/trade`
- `BTC/ETH, w=60`：baseline `-16.73bps/trade` -> gated `-14.43bps/trade`
- `ETH/SOL, w=24`：baseline `-12.61bps/trade` -> gated `-12.43bps/trade`
- `ETH/SOL, w=60`：baseline `-12.61bps/trade` -> gated `-9.86bps/trade`
- `BTC/SOL, w=24`：baseline `-13.51bps/trade` -> gated `-13.01bps/trade`
- `BTC/SOL, w=60`：baseline `-18.18bps/trade` -> gated `-17.21bps/trade`
- `positive_cells = 0`

## Verdict
- `background/P0`

## System-changing conclusion
- `segmented-signature pair fade` 在最小 crypto pairs portability / family 去重 / 成本现实检查里，没有证明自己相对已 live 的 `Rank 431 / 424` 与既有 rolling-OLS / cointegration pairs family 留下独立新增的 after-cost admission 价值；它当前更像“减少坏单的 pairs gate 提示”，不是值得前排保留的 standalone front object。

## Runtime writeback intent
- 当前 fresh intake 首判应诚实收口为 `background/P0`。
- 因未形成 `keep_P1 / P2 / P3`，不分配新 Rank。
- 下一条 conditional fresh intake 可切到 `research/quant_digests/2026-04-22_0545_polymarket-streak-pricehurdle-binary-alpha.md`。
