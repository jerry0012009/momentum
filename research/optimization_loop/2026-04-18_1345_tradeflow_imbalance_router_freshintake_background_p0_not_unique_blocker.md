# bot3 optimization loop — 2026-04-18 13:45 UTC

## 执行小点
- target: `research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`
- action: fresh intake first-verdict：只回答这条 `极端 taker buy dominance × cross-sectional router` 是否值得作为新的 flow-driven front object 保留，并补 1 个最小 honesty / execution realism blocker

## 本轮读取/复核
- digest：`research/quant_digests/2026-04-18_1220_tradeflow-imbalance-router-alpha.md`
- artifact：
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_router_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_signed_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_events.csv`

## 最小 first-verdict
结论：`background/P0`，不保留为新的 flow-driven front object。

## 为什么不是 keep_P1
先看它最像样的壳：`15m top_buy_q90_volpos` strongest-only router。
- 事件数：`161`
- `h5 gross = +9.03bps`，扣统一 `8bps` 后 `net5 = +1.03bps`
- `h12 gross = +13.83bps`，扣统一 `8bps` 后 `net12 = +5.83bps`
- symbol mix 不是单一币：`BTC/ETH/BNB/LINK/ADA/DOGE/SOL/XRP = 29/24/21/20/20/18/15/14`

但按本轮允许的最小 honesty 子检查，把 router 事件回放到逐日/逐 symbol 贡献后，结论不是“只剩 child execution 一个 blocker”，而是还存在 **稳定性/集中度 blocker**：

### 1) 收益并不稳，主要由少数日期硬撑
`15m router h5`：
- 全体均值 `+9.03bps`
- 但单日贡献高度分化：
  - 最好几天：`2026-04-07 = +907.64bps (9 events)`、`2026-04-13 = +760.89bps (14 events)`
  - 最差几天：`2026-04-17 = -295.15bps (10 events)`、`2026-04-12 = -262.39bps (15 events)`
- 胜率只有 `0.509`
- top5 正收益事件之和已经超过总和（`top5_share > 100%`），说明整体均值需要靠少数大赢家抵消大量亏损事件。

`15m router h12` 也类似：
- 单日最强：`2026-04-07 = +1411.87bps (9 events)`、`2026-04-05 = +949.92bps (17 events)`、`2026-04-13 = +932.25bps (14 events)`
- 单日最差：`2026-04-06 = -718.72bps (8 events)`、`2026-04-08 = -497.97bps (6 events)`
- 胜率也仅 `0.522`

这说明它不是一个已经收敛到“只差 child execution”的厚 router；它仍然明显受 regime/day clustering 影响。

### 2) 虽然不是单一币硬撑，但 symbol 稳定性也未闭合
`15m router h5` 的按 symbol signed mean 仍明显分裂：
- 正：`BTC +20.54bps`、`ETH +18.19bps`、`ADA +19.33bps`、`DOGE +13.07bps`
- 负：`SOL -7.10bps`、`LINK -10.39bps`
- `BNB` 仅 `+2.46bps`、`XRP +5.03bps`

`h12` 虽改善，但仍有 `BTC -5.00bps`、`BNB -3.99bps`。这意味着它还没达到“只差更细 child execution/decay realism，就足够诚实保留”的程度。

## 系统认知变化
`极端 taker buy dominance × 15m strongest-only router` 虽然在统一 `8bps` 下保留了薄正 net，且不是单一币硬撑，但正边际仍被少数日期/少数大赢家显著主导，symbol 稳定性也未闭合；因此当前不能把唯一剩余 blocker 收敛为 `child execution / decay realism`，本轮 fresh intake 直接收口 `background/P0`。
