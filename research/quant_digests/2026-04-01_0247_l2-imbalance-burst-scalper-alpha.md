# 别把这份 2026 新 repo 只读成超低延迟 bot：对 desk 更该先测的是「L2 imbalance × volume-burst continuation」1m/3m raw alpha

- 时间：2026-04-01 02:47 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `strategies/orderbook_imbalance.py` + `config/config.yaml` + `backtest/backtester.py`）+ Binance USDⓈ-M Perpetual 公开 `1m` proxy quick check
- 主题类型：raw alpha
- 基础 alpha：当 top-10 L2 盘口出现单边深度失衡、同时成交量突增且短窗价格动量同向时，未来 `1m/3m/5m` 更容易继续沿失衡方向漂移；RSI 只做过热/过冷 veto，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book/l2-imbalance/volume-burst/directional/continuation/single-asset/btc-eth-sol/binance-bybit/1m/3m/5m/repo/public-data/cost/execution
- 证据类型：repo source audit + 公开数据最小 proxy quick check

> 先回答 base alpha：**这不是 filter，不是 overlay。base alpha 就是“L2 盘口单边失衡 × 成交量突增 × 同向短窗动量”之后的超短线 continuation。RSI、止损、追踪止盈、5 分钟 time stop 只是风控/出场壳。**

## 1. 这次看了什么
这次主材料不是论文，而是一个很新的 repo：**`devinbrumbelow5-jpg/kimmy-scalper`**（GitHub metadata 显示创建于 `2026-03-30`）。表面标题是“ultra-low latency crypto scalping bot”，但真正值得 desk 抽出来的，不是 UI、sub-agent、paper/live mode 这些壳，而是它在 `strategies/orderbook_imbalance.py` 里给出的**完整短线 directional skeleton**：

1. `orderbook_depth = 10`，用 top-10 bid/ask volume 算 `imbalance = bid_volume / (bid_volume + ask_volume)`；
2. `imbalance_threshold = 0.65`，只有极端失衡才触发；
3. `momentum_lookback = 20`，要求短窗价格动量与盘口方向一致；
4. `volume_spike_multiplier = 2.0`，要求成交量爆发；
5. `rsi_period = 14`，仅用于避免过热 long / 过冷 short；
6. 交易壳是现成的：`0.5%` 初始止损、`1.0%` 初始止盈、`+0.5%` 后激活 `0.3%` trailing、`300s` time exit、`0.5%` 资金风险上限、日亏损/回撤阈值。

更重要的是：repo 自带 `backtest/backtester.py`，但它不是用真实 L2 回放，而是**拿 OHLCV 高低点去合成 orderbook**。所以这份 repo 的价值，不在“它回测赚没赚钱”，而在**它把一个可落地的 microstructure alpha 骨架写得很清楚**，方便我们直接拆成真实可测版本。

## 2. 核心结论
- 一句话核心结论：**repo 里的可用部分不是“超低延迟 bot”这个 headline，而是一个可独立复现的 raw alpha：L2 单边失衡只有在“volume burst + 同向短窗动量”同时成立时，才更像 1m/3m continuation。**
- 一句话证明方式：**源码给出了明确定义、入场与出场全壳；我再用 Binance 公共 `1m` kline 的 taker-buy proxy 做最小 transfer check，发现这条线在 bar-space 里仍能留下薄毛边，但只适合极低成本执行。**

关键数据点（本地 `1m` proxy quick check，`BTC/ETH/SOL`，近 10 天，public kline，用 `taker_buy_quote/quote_volume` 近似买盘压力）：
1. **严格照 repo 的 `2.0x` volume burst 门槛搬到 `1m` bar-space，信号反而偏稀且平均边际为负**；说明 repo 的事件级阈值不能直接平移成分钟 bar 阈值。
2. 把 bar-space 口径改成更温和的 `buy_ratio > 0.70 / < 0.30`、`volume_ratio20 > 1.5x` 后，**3 分钟持有 pooled gross `+0.460 bps/trade`，5 分钟持有 gross `+0.481 bps/trade`**。
3. 但这条线**成本壳很薄**：3 分钟持有的 break-even 大约只有 `0.23 bps(one-way)`，5 分钟持有约 `0.24 bps(one-way)`；一旦按 `0.25 bps(one-way)` 计，净值已接近或略低于 0。
4. 分资产看，当前 10 天窗口里 **ETH 3m proxy 最强（`+1.06 bps/trade`）**，BTC 只有 `+0.08 bps`，SOL 大约 `+0.36 bps`；所以这更像**需要按币种分层 admission**，不是全市场统一阈值。

## 3. 为什么和当前项目有关
- 它是**raw alpha**，不是又一个“给 breakout/mean-reversion 打辅助”的 gate。
- 它补的是我们当前素材池里很需要的一块：**“microstructure directional raw alpha + 完整出场壳”**。最近我们已经有不少 `L1 imbalance / OFI / VWAP-pressure` 证据，但这份 repo 的额外价值是把**volume burst admission、RSI veto、time stop、trailing stop**一起写成了可直接复刻的完整策略骨架。
- 它跟当前 short-cycle desk 的关系非常直接：**最适合 `1m` 触发、`3m/5m` 持有**；不是 `15m` 主 bar raw alpha，但可以作为 `15m` 体系里的“快时钟子模块”或者单独的 ultra-short alpha lane。

## 3.5 策略拆解（必填）
- 方向属性：单资产 directional / microstructure continuation
- 基础 alpha：
  - 计算 `imbalance_t = bid_vol_top10 / (bid_vol_top10 + ask_vol_top10)`
  - long：`imbalance_t > 0.65` 且短窗动量为正、volume burst 成立、RSI 未过热
  - short：`imbalance_t < 0.35` 且短窗动量为负、volume burst 成立、RSI 未过冷
- entry：信号触发后下一次可成交报价入场（真实版优先用 next-tick / next-1s mid + fill model；proxy 版用 next-1m open）
- exit：优先按 `TP 1.0% / SL 0.5% / trailing / 300s time stop` 的层级执行
- sizing：单笔风险预算上限 `0.5%` 账户权益；币种分层上限，避免 ETH/SOL 信号强时单币过度集中
- risk / veto：波动过大暂停、API/数据断流暂停、gross exposure cap、连续错误暂停
- cost：这条线不是“随便 taker 也能活”的 alpha，更像**maker-ish 或超低费率 taker**才有生存机会

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：真实 L2 盘口失衡只有在“短窗动量确认 + 成交量爆发”时，才会从纯噪音变成可交易 continuation；若不加 admission，盘口失衡本身不够稳。

**数据源与公开性**：
- 一级数据：Binance / Bybit 公开 websocket depth + trades（公开可得，无私钥）
- 最低配 proxy：Binance USDⓈ-M Futures 公共 REST klines（`quote_volume`、`taker_buy_quote_volume` 可得）
- 更新频率：真实版建议 `100ms~1s`；最小诚实 proxy 可先落在 `1m`，再映射到 `3m/5m` 持有

**最小可复现实验口径**：
1. 资产：先 `BTC/ETH/SOL`，后续扩到流动性前 10 永续；
2. 采样：`1s` event bar 或 `5s` bar 为主，不建议先用 `15m`；
3. 特征：`top10 depth imbalance`、`trade-flow buy ratio`、`20s/60s price momentum`、`volume burst`、`spread`；
4. 入场：阈值触发后 next-tick / next-bar；
5. 出场：固定 `60s / 180s / 300s` 三档 + `TP/SL/trailing` 对照；
6. 成本阶梯：`0 / 0.1 / 0.25 / 0.5 / 1.0 bps(one-way)`；
7. 先看指标：`gross/net bps per trade`、`fill survival`、`queue loss`、`holding-time pnl decomposition`。

**下一步最该先测**：
- **不要先优化模型，先验证 repo 里最关键的 transfer 问题**：
  1. `event-time 2.0x` volume burst 到底对应分钟口径的多少倍？
  2. `imbalance 0.65` 应该用绝对阈值还是 rolling quantile？
  3. 在真实 L2 下，这条线到底活在 `30s/60s/180s` 哪个持有区间？
- 如果只能做一个最小实验，我会先做：**`ETH/USDT perp` 的 `1s top10 imbalance × 20s volume burst × 180s hold`，成本分 maker/taker 两条曲线单独跑。**

## 5. 风险与保留意见
- repo 的 backtester 用 OHLCV 合成 orderbook，这会严重美化微结构策略；**不能把 repo 自带回测结果当证据**。
- 我这次 public quick check 也只是 proxy，不是真实 L2；`taker_buy_quote/quote_volume` 只能近似主动买盘压力，不能替代 top-10 depth imbalance。
- 当前 proxy 证据说明它**更像薄边 alpha**：gross 有毛边，但只要 one-way 成本上到 `0.25 bps` 左右就基本吃光；因此不适合作为“默认 taker 策略”。
- 这条线和 `15m` 主 bar 的关系不是“直接把信号压成 15m bar-close”；更合理的用法是**快时钟触发器**或 `15m` 母策略下的执行/加减仓子模块。

## 6. 来源
1. **devinbrumbelow5-jpg. (2026). _kimmy-scalper_. GitHub Repository.**
   - Repo URL: `https://github.com/devinbrumbelow5-jpg/kimmy-scalper`
   - Readable URL: `https://github.com/devinbrumbelow5-jpg/kimmy-scalper`
2. **devinbrumbelow5-jpg. (2026). _strategies/orderbook_imbalance.py_. GitHub Raw Source.**
   - URL: `https://raw.githubusercontent.com/devinbrumbelow5-jpg/kimmy-scalper/main/strategies/orderbook_imbalance.py`
3. **devinbrumbelow5-jpg. (2026). _config/config.yaml_ + _backtest/backtester.py_. GitHub Raw Source.**
   - URL: `https://raw.githubusercontent.com/devinbrumbelow5-jpg/kimmy-scalper/main/config/config.yaml`
   - URL: `https://raw.githubusercontent.com/devinbrumbelow5-jpg/kimmy-scalper/main/backtest/backtester.py`
4. **Binance USDⓈ-M Futures API Docs. _Kline/Candlestick Data_.**
   - URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 7. 本地快检产物
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/summary.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/grid.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/by_symbol_bestproxy.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/cost_ladder_bestproxy.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/signals.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/panel.csv`
- `reports/artifacts/quant_digests/kimmy_scalper_proxy_20260401_0245/meta.json`
