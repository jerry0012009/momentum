# 别把 HyperLiquidBot 只读成“四策略拼盘”：对 short-cycle crypto desk，更该先拆的是「低波动 BB squeeze 突破 × EMA/MACD 同向确认」这条 raw alpha 壳

- 时间：2026-04-22 05:15 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：低波动 Bollinger Band compression 后，价格向上/向下突破 band，并被 EMA9/EMA21 + MACD histogram 同向确认，押注后续 1–2 小时顺势延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：breakout / momentum / volatility-compression / bollinger-band / ema / macd / atr / hyperliquid / binance-perpetual / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data quick probe

## 1. 这次看了什么

这次看的是 2026 新仓库 `OlieSmith/HyperLiquidBot`。它表面上是 Hyperliquid perpetuals 多策略 bot：momentum、mean reversion、trend following、BB compression 四个模块，再由 risk manager 做加权投票、仓位和 trailing stop。对我们更有价值的不是“多策略拼盘”本身，而是里面 `strategies/bb_compression.py` 可以单独拆成一条 raw alpha：**先找 Bollinger Band 宽度处在近 50 根底部 25% 的压缩状态，再等 close 突破上下轨；若同时 EMA/MACD 趋势模块同向，就用 ATR stop + 2R target 管退出。**

## 2. 核心结论

- 这是一个可独立复现的完整策略壳：entry 是 squeeze breakout，exit 可用 repo 的 ATR trailing stop / profit target，sizing 可用 conviction bucket，risk 有 max positions + cooldown。
- 我做了 Binance USDⓈ-M 10 个 liquid majors 的迁移 probe：`15m` 持有 `4/8` bars、`5m` 持有 `12/24` bars；全池结果不好，说明不能直接 broad-basket 上线。
- 全池：`15m 4 bars` 共 `238` 笔，gross `-4.43 bps/trade`，粗扣 `8 bps` 后 `-12.43 bps/trade`；`5m 12 bars` 共 `259` 笔，gross `-4.39 bps/trade`，net `-12.39 bps/trade`。
- 但有清楚 pocket：`SOL 15m 4 bars` gross `+15.37 bps/trade`、net `+7.37 bps/trade`；`SOL 15m 8 bars` gross `+18.83 bps/trade`、net `+10.83 bps/trade`；`AVAX 15m 8 bars` gross `+17.05 bps/trade`、net `+9.05 bps/trade`。
- 一句话：**这条不是“所有币低波动突破都追”，而是一个 alt-router 候选；先筛 SOL/AVAX/XRP/BNB 这类 pocket，再谈 maker-first 或 child execution。**

## 3. 为什么和当前项目有关

`momentum` 当前已经有 Donchian、EMA、ATR、volume confirmation 等积木，但仍需要更多可复现 raw alpha 壳。这个 repo 的价值是把「波动压缩 → 方向突破 → 趋势确认 → ATR 风控」打包成完整可测流程：它不是单纯 filter，也不是纯解释型材料。对 `5m / 15m` 来说，它可以补一个与 mean-reversion / pairs / funding 不同的 **volatility breakout continuation** 候选。

## 3.5 策略拆解（必填）

- 方向属性：顺势 / 突破 / 波动压缩释放
- 基础 alpha：BB width 处于近 50 根低分位后，价格突破 band 的下一段延续
- regime：低波动压缩状态；`bb_width_percentile <= 0.25`
- filter / veto：EMA9/EMA21 同向 + MACD histogram 同向且增强；低流动性币和 meme 币可 blocklist
- risk / sizing / execution overlay：ATR trail `4.5 × ATR` 且 clamp 到 `2%~8%`；profit target `2R`；max positions；cooldown；实盘优先 maker/limit 或 breakout 后 1–2 bar 回踩入场，避免 taker 追在最差点

## 4. 可复刻的最小实验

- 研究假设：低波动压缩后的 band 突破，只有在 EMA/MACD 同向且标的属于强 pocket 时，才有足够短周期延续。
- 可计算定义：`BB(20,2)`，`bb_width=(upper-lower)/sma`，`width_percentile=rank(width, last 50)`；long 条件为 `width_pct<=0.25 & close>upper & EMA9>EMA21 & MACD_hist>0 & hist rising`，short 对称。
- 最小切口：Binance USDⓈ-M `SOL/AVAX/XRP/BNB/BTC/ETH`，`15m` 近 180–365 天；先测 `hold=4/8 bars`，再加 ATR stop / 2R target。
- 先看指标：`gross/net bps per trade`、trade count、symbol positive ratio、成本从 `4/8/12 bps` 的 friction ladder。

## 5. 风险与保留意见

全池均值为负，说明 squeeze breakout 在 crypto majors 上很容易变成追高杀低；样本只用了最近约 `1500` 根 bar，且 quick probe 用 Binance 替代 Hyperliquid，未模拟限价成交、盘口滑点和资金费率。SOL/AVAX pocket 可能只是近期趋势段带来的选择偏差。下一步必须做更长样本、rolling split、maker-vs-taker 成本和 symbol admission；如果 pocket 不稳定，就只保留为 breakout router / volatility regime component。

## 6. 来源

- OlieSmith. (2026). `HyperLiquidBot` — HyperLiquid perpetuals trading bot: momentum, mean reversion, trend following, BB compression. Repo created `2026-03-19`, pushed `2026-04-14`.
- Repo URL: https://github.com/OlieSmith/HyperLiquidBot
- Source files: `strategies/bb_compression.py`, `strategies/trend_following.py`, `risk.py`, `main.py`
- Probe artifacts:
  - `reports/artifacts/quant_digests/olie_bbcompress_consensus_trades_2026-04-22.csv`
  - `reports/artifacts/quant_digests/olie_bbcompress_consensus_summary_2026-04-22.csv`
