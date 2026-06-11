# Rank 211 / CME BTC futures sign classifier survivor follow-up drop to background

- Time: 2026-03-28 04:21 UTC
- Target: `Rank 211 / CME BTC futures sign classifier`
- Action: survivor 唯一一次 follow-up（更细 public microstructure / execution 特征 + realistic cost gate）
- Verdict: `drop_to_background`

## What changed
这轮已经把这条对象最关键、也最该改变层级的 follow-up 补完了：不再停留在 15m public-kline headline，而是把公开 `1m futures klines` 里的更细成交/流量 proxy（`trade_count`、`taker_buy_quote`、`taker imbalance`、`close-vs-VWAP deviation`、15m 内 1m return/range path）聚合成 `microstructure-enriched` 版本，直接和 `kline_proxy` 做同口径 next-bar sign + 高阈值 abstain 比较。

结论没有把对象往上推，反而把 exit decision 收紧了：**更细 public microstructure 并没有把这条线拉过 realistic cost gate。**

## Minimal experiment
- Data: Binance Futures public `BTCUSDT 1m klines`, `limit=1500`
- Aggregation: 聚合成 `15m` bar；目标仍是 `next 1 bar sign`
- Baseline (`kline_proxy`): 过去 6 根 `15m` 的 return/range + rolling vol + volume/trade-count z-score
- Follow-up (`microstructure_enriched`): baseline 再加
  - `15m` 内 `1m` return mean/std/last
  - `15m` 内 `1m` range mean/max
  - `taker imbalance`（全窗均值、最后 5 分钟均值、最后 1 分钟）
  - `close-vs-VWAP deviation`（均值、末值）
- Train/test: 简单时间切分 `70/30`
- Trading readout: 只看 `next-bar long/short`；阈值分别检查 `0.55/0.45`、`0.60/0.40`、`0.65/0.35` 与 `top/bottom 10%`
- Cost gate: round-trip `1 / 2 / 4 / 6 bps`

Artifacts:
- `reports/artifacts/rank211_microstructure_followup_20260328_0421/meta.json`
- `reports/artifacts/rank211_microstructure_followup_20260328_0421/summary.csv`
- `reports/artifacts/rank211_microstructure_followup_20260328_0421/bar_features_15m.csv`
- `reports/artifacts/rank211_microstructure_followup_20260328_0421/predictions.csv`

## Key result
最好的 `microstructure_enriched` 档位也只是：
- `q90_10`: `gross +1.05 bps/trade`, `hit 50.0%`, `trade_rate 61.5%`
- 扣 `2 bps` 后仍是 `-0.95 bps/trade`
- 扣 `4 bps` 后是 `-2.95 bps/trade`

对照 baseline：
- `kline_proxy q90_10`: `gross +1.15 bps/trade`
- 扣 `2 bps` 后 `-0.85 bps/trade`

也就是说，这轮 follow-up 的新增信息并没有形成“净值跳变”——它只把 gross 从约 `+1.15` 换成约 `+1.05` / `+0.26` 这一档，**没有任何一档穿过 2bps，更别说 4bps。**

## Why this is enough for a survivor exit
policy 给 survivor 的唯一一次 follow-up，本来就要求回答一个很窄的问题：
> 加更细 microstructure / execution 特征后，高置信度 abstain classifier 能不能把 net edge 拉过原先 public-kline 下的 taker 不过线结论？

这轮答案已经是 **不能**：
1. 更细 public 特征并没有带来足够 gross uplift；
2. 高阈值分层没有把 edge 推到 `2bps` 以上；
3. 因此它不能合理升级到 `P2`；
4. survivor 预算也已用完，不能继续 open-ended keep_P1。

## Runtime implication
- `Rank 211` 的 survivor 唯一一次 follow-up 已消费完。
- 正式 verdict：`drop_to_background`。
- 不进入 `P2`，也不保留前排 survivor 锁定权。

## Result sentence
`Rank 211 / CME BTC futures sign classifier` 的唯一一次 survivor follow-up 已给出正式出口：把公开 1m 成交/流量 microstructure 特征加进 high-threshold abstain classifier 后，最好的极端分层仍只有约 `+1.05 bps/trade gross`、扣 `2/4bps` 后继续为负，因此这条线不能升 `P2`，应直接 `drop_to_background`。
