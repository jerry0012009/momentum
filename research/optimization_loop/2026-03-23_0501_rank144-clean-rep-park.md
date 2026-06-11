# 2026-03-23 05:01 UTC · Rank 144 / intraday volatility commonality clean replication → park

## 0. 先判 interrupt
- `Paper / 正在自动运行` 顶板未出现新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `tiny-live / live-shadow plumbing` 也未写入新的 blocking anomaly。
- 因此本轮继续按 `Next 3` 默认顺序执行，认领 `Rank 144` 唯一允许的最小 clean replication。

## 1. 本轮认领
- **主点**：`Rank 144 / intraday volatility commonality asymmetric follow-up gate`
- **紧邻子点**：把 clean replication 结果回写为 desk-level scorecard，并最小更新 `docs/TODO.md` 顶板路由。

## 2. 本轮做的最小 clean replication
这轮不再复读 digest，也不碰 production runner，只做顶板允许的唯一 decisive check：
- 数据：Binance USDⓈ-M `BTCUSDT / ETHUSDT / SOLUSDT`
- 频率：`15m`
- 阈值冻结：`rv1h z-score > 1.0`
- 共振定义：`commonality_count >= 2`
- 交易代理：`next-bar open` 入场，`hold 8 bars`
- 成本：`12 bps / side`
- 目的：确认它在 **冻结阈值 + 分资产拆分** 后，是否还值得保留 active Scout 预算

artifact：
- `reports/artifacts/scout_rank144_intraday_vol_commonality_15m/threshold_config.csv`
- `reports/artifacts/scout_rank144_intraday_vol_commonality_15m/asset_split_summary.csv`
- `reports/artifacts/scout_rank144_intraday_vol_commonality_15m/pooled_summary.csv`
- `reports/artifacts/scout_rank144_intraday_vol_commonality_15m/promotion_scorecard.json`
- `reports/site/factors/scout_rank144_intraday_vol_commonality_15m/report.html`

## 3. 结果
### pooled
- `long, c0_1 = -21.57 bp`
- `long, c2_3 = -18.93 bp`
- `long delta = +2.64 bp`
- `short, c0_1 = -25.75 bp`
- `short, c2_3 = -27.85 bp`
- `short delta = -2.10 bp`

### split by asset（short side）
- `BTC: -24.78 -> -23.64 bp`（小幅改善）
- `ETH: -26.96 -> -26.11 bp`（小幅改善）
- `SOL: -25.52 -> -33.80 bp`（明显恶化）

### honest read
这刀把上一轮的 intake 直觉直接打回来了：
- 它**没有**在冻结阈值后的 pooled short side 继续改善；反而更差；
- 它也**没有**形成足够干净的 cross-asset short follow-up 稳定性；
- long 侧虽有一点改善，但仍明显为负，不足以改写 “不是 shared allow gate” 的判断。

所以最诚实的 desk verdict 是：
> `Rank 144` 这条线可以留在 evidence pool 里当旁证，但不再值得占 active Scout 的默认预算。

## 4. 轻量 scorecard
- `usefulness = 1/3`
- `time_stability = 1/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `hard-fail flags = not_post_cost_positive_even_in_best_bucket; cross_asset_asymmetry_persists_in_clean_rep; router_attachment_still_not_done`
- `recommended_action = park`
- `why_now = 用一次冻结阈值 + BTC/ETH/SOL 分资产 clean replication，回答 Rank 144 还能不能继续留在 active Scout`
- `main_weakness = 依然只是公共行情代理，尚未真正接到 production breakout-short router，也没有更长窗口的时间稳定性`

## 5. 顶板回写
已对 `docs/TODO.md` 做最小局部修改：
- `Rank 144` 从 active Scout 调整为 `P0 / park / evidence only`
- `Next 3` 默认 `Run 1` 回到 `Rank 140 / pbo-cscv deflated sharpe honesty gate`
- `最近关键 evidence` 顶部新增本轮 frozen-threshold clean replication 结论

## 6. 本轮结论
- `Rank 144 = park`
- 不升 `P2`
- 不保留 active Scout 预算
- 后续若要 reopen，必须带着更强的新信息回来（例如真正接到 breakout-short router 后的 route-aware replication），否则默认只当 evidence pool 引用
