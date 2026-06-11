# bot3 optimization loop — RS semivariance downside continuation fresh intake first verdict

- 时间：2026-04-23 00:13 UTC
- 执行对象：`research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
- 动作：fresh intake first verdict
- 目标：只补 1 个最小 decisive blocker——它是否真是可独立承接的 short-only after-cost alpha，而不是更适合作为 downside risk / filter overlay

## 本轮只做的最小 blocker
在 digest 已给出的 `BTC/ETH/SOL`、`1h RS- dominance + 最近 15m 下跌 -> next 15m open short` 框架上，不再扩展第二条研究线；只补 1 个最便宜、最会改变结论的 honesty 检查：

1. 把最强口径固定在 digest 自报的 `q=0.95 / hold=8x15m`；
2. 用本地 `120d` Binance perp `5m/15m` cache 重算 month split；
3. 在原 digest `6bps` 之外，再看一个更诚实的 `10bps round-trip` 梯度，判断 edge 是否仍像独立 raw alpha，而不是只剩 downside overlay 提示。

## 结果
按上述最小检查，`RS- downside continuation` 没能诚实保住独立 fresh intake：

- `6bps` 下只剩 `ETH`、`SOL` 还能保住正均值，`BTC` 在同口径 `q=0.95 / hold=8` 已约 `-1.38bps/trade`；
- 加到更诚实的 `10bps` 后，`ETH` 只剩约 `+1.75bps/trade`、`SOL` 约 `+4.93bps/trade`，但 `BTC` 约 `-5.38bps/trade`；
- month split 进一步暴露它不是稳定跨时段 pocket：`SOL` 在最近 `2026-03` 已约 `-18.37bps/trade`，`ETH` 在 `2026-03` 也约 `-3.71bps/trade`，正边际主要集中在更早月份而不是持续存在的 downside state；
- 因而它没有通过本轮 success criterion 里要求的“不是单币 lucky-run、且最小 honesty / execution realism 后仍成立”的门槛。

## 结论
**`1h RS- dominance × 15m downside continuation` 的 fresh intake first verdict = `background/P0`。**

更诚实的 runtime 读法是：
- `RS+/RS-` 非对称在 desk 上仍有价值，
- 但当前更像 existing semivariance / downside-state family 的 **directional veto / downside filter / sizing hint**，
- 还没有证明自己是相对现有 overlay 语义可独立排队的新 short-only raw alpha。

## 对 runtime 的影响
- 不分配 Rank；
- 不进入 survivor；
- `cycle_plan` 第 1 项应写为 `done`；
- Fresh intake front slot 的当前对象收口后，前排可自然落到下一条已存在的 conditional fresh intake。

## 用到的本地材料
- `research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
- `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/summary.csv`
- `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/basket_summary.csv`
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/{BTCUSDT,ETHUSDT,SOLUSDT}__120d__15m__perp.csv`
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/exec_cache/{BTCUSDT,ETHUSDT,SOLUSDT}__120d__5m__perp.csv`
