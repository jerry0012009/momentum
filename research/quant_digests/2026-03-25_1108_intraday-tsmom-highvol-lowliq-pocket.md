# 别把 intraday TSMOM 当全天候 bar-bar 信号：这篇 2022 JFM 论文更值得先偷的是「高波动 × 较低流动性 pocket」里的 15m own-past momentum
- 时间：2026-03-25 11:08 UTC
- 类型：2022 JFM 论文 + 2025 GitHub 工程 companion + Binance Futures 公共 `15m/5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：单资产 own-past intraday return continuation（过去 `15~30m` 的方向延续到下一根短周期 bar）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/intraday/time-series/own-past-return/pocket-selection/liquidity/volatility/binance/perpetual/5m/15m/paper/repo
- 证据类型：论文证据 + 工程仓库 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是“流动性/波动 filter”，而是 very-short-horizon 的 own-past momentum。**

主论文是 **Li, Sakkas, Urquhart (2022), _Intraday time series momentum: Global evidence and links to market characteristics_**。它最值钱的地方不是再说一遍“日内也有 momentum”，而是把 desk 更该偷的旁支讲清了：**ITSM 不是全天候普适信号，它更集中出现在特定 microstructure pocket，尤其是低流动性、高波动、离散信息更强的时候。**

我另外看了一个 2025 GitHub 工程 companion：`anthonymakarewicz/bitcoin-momentum-trading`。它虽然是 BTC 单资产 + ML 包装，但 entry/exit/cost 骨架写得比较完整，适合当我们把论文想法 desk 化时的工程参考。

## 2. 核心结论
- **一句话核心结论：** 这条线值得进 raw alpha 池，但正确读法不是“每根 bar 都追”，而是先把 **高波动 × 较低流动性** 的 pocket 挑出来，再测 very-short-horizon continuation。
- **一句话它怎么证明：** 论文用 `16` 个发达市场高频样本做国际证据，并在截面和时间序列两侧都检验到：ITSM 在 **low liquidity / high volatility / discrete information** 条件下更强。
- 论文摘要里最硬的三点：
  1. 样本覆盖 **16 个发达市场** 的高频数据；
  2. ITSM 在大多数国家 **样本内外都显著**；
  3. 强度与 **低流动性 / 高波动 / 离散信息** 正相关，说明不是纯粹 data-mined 花活。
- 我补的 Binance Futures 最小快检（`BTC/ETH/SOL/BNB/XRP/ADA`，公共 `15m/5m` K 线）也给出一个很 desk 化的结论：
  - `15m` 上，如果直接把“过去 1~2 根 bar 的方向延续到下一根”无脑铺满全时段，**全样本 gross 是负的**：lookback=`1` 时 **-0.62 bps/bar**，lookback=`2` 时 **-0.64 bps/bar**；
  - 但切到 **high-vol + low-liq pocket** 后，`15m` 立刻翻正：lookback=`1` 时 **+0.79 bps/bar**，lookback=`2` 时 **+1.04 bps/bar**，命中率 **49.5% / 51.4%**；
  - `5m` 上同样 pocket 只剩 **+0.28 bps/bar**，说明更快频率不是没有 edge，而是边际已经薄到很容易被 fee/slippage 吃掉。
- 翻成人话：**base alpha 在 pocket 里有东西，但“全天候连续开火”大概率会把 edge 自己磨掉。**

## 3. 为什么和当前项目直接相关
- 它补的是 **raw alpha**，不是又一篇只谈 filter 的旁路材料；只是这条 raw alpha 天生更像 **pocket alpha**。  
- 这很符合当前 desk：我们不是继续围着 breakout / retest 内循环，而是在补一个可独立运行的短周期趋势/延续家族分支。  
- 它还自然拆成三层：
  - alpha 本体：own-past intraday continuation；
  - pocket 选择：高波动、较低流动性、离散信息更强；
  - execution 现实：5m 往往太薄，15m 更可能留下可交易边际。

## 3.5 策略拆解（必填）
- 方向属性：单资产、可多可空、短持有的 intraday TSMOM
- `entry`：
  - `ret_lb = Close_t / Close_{t-L} - 1`
  - 若 `ret_lb > 0`，下一根开多；若 `< 0`，下一根开空
  - 当前最值得先测的是 `15m, L=2`（即过去 `30m` 方向预测下一根 `15m`）
- `regime / pocket gate`：
  - 仅在 rolling realized vol 位于最近窗口 **top tercile** 时开启；
  - 仅在 rolling quote-volume 位于该资产样本 **lower tercile / lower half** 时保留；
  - “离散信息”先用 **单根绝对收益冲击 / news clock / funding 时点前后** 做 proxy 补测
- `exit`：持有 `1` 根；若下一根反向信号出现则反手
- `sizing`：按 `1 / realized_vol` 做 inverse-vol sizing；单币 notional cap `10%~15%`
- `risk`：
  - 单日亏损阈值熔断；
  - 同方向总 gross cap；
  - 跳过 funding 结算前后极端拥挤时段
- `cost`：必须先跑 `4 / 8 / 12 bps round-trip`；因为当前 gross pocket 只有 `0.8~1.0 bps/bar` 量级，若没有更稀疏触发或 maker/microstructure 优势，净值大概率不够厚。

## 4. 可复刻的最小实验
- 数据源：Binance USDⓈ-M Futures `fapi/v1/klines`（公开可得，`5m/15m` 实时更新）
- universe：先做 `BTC/ETH/SOL/BNB/XRP/ADA`，全部是高流动合约
- 最小实验：
  1. `15m`：`L in {1,2,4}`，先只测 next-bar continuation；
  2. pocket gate：`RV top tercile × quote-volume bottom tercile`；
  3. 对照：`all bars` vs `gated bars`；
  4. 输出：gross bps/bar、hit-rate、trade share、post-cost bps/bar。
- 当前 admission 级结果已经很清楚：
  - `15m all bars` 不值得直接上线；
  - `15m gated pocket` 值得进入下一轮 sparse-execution / maker-first 验证；
  - `5m` 更像高强度实验频段，不像默认生产频段。

## 5. 下一步怎么测（必须）
1. **先做 sparse 化**：不要 bar-bar 连续交易，改成“只有 `|ret_lb|` 超过 rolling percentile 阈值才触发”，看 gross 是否还能留住。  
2. **补 discrete-information proxy**：把 funding 时间点、OI 突变、单根绝对收益冲击加入 gate，验证论文里的第三条机制。  
3. **做 15m→5m 执行切片**：信号仍在 `15m` 生成，但执行改成 `5m` TWAP / maker-first，别直接把 alpha 本体压到 `5m`。  
4. **做 cost ladder**：`4 / 8 / 12 bps RT` + participation cap，确认这条线到底是“可交易 pocket”还是“只有 paper edge”。  
5. **做 cross-symbol pooling vs 单币**：判断 edge 是否主要来自 `SOL/XRP/ADA` 这种相对更跳的币，而不是 BTC/ETH。

## 6. 风险与保留意见
- 论文证据来自全球传统市场，不是原生 crypto；我们当前做的是 **transfer test**，不是原文精确复现。  
- 本地快检只用了 K 线级流动性/波动 proxy，还没把订单簿、OI、funding、news clock 放进来。  
- 这条线非常容易被误读成“5m/15m 都能无脑追动量”；实际上它更像 **有条件触发的 pocket alpha**。  
- 工程 companion repo 是 BTC 单资产 ML 框架，能借的是 backtest 骨架，不是要把黑箱模型当结论本体。

## 7. 来源
1. **Li, Z., Sakkas, A., & Urquhart, A. (2022). _Intraday time series momentum: Global evidence and links to market characteristics_. Journal of Financial Markets, 57.**  
   - Venue: `Journal of Financial Markets`  
   - DOI: `10.1016/j.finmar.2021.100619`  
   - Readable URL: `https://ideas.repec.org/a/eee/finmar/v57y2022ics138641812100001x.html`  
   - DOI URL: `https://doi.org/10.1016/j.finmar.2021.100619`

2. **anthonymakarewicz. (2025). _bitcoin-momentum-trading_ (GitHub repository).**  
   - Repo URL: `https://github.com/anthonymakarewicz/bitcoin-momentum-trading`  
   - Readable URL: `https://github.com/anthonymakarewicz/bitcoin-momentum-trading/blob/main/README.md`  
   - 工程注记：repo 用 `5m` BTC OHLCV 特征预测下一段 momentum 方向，notebook 输出里 `XGBoost accuracy ≈ 54.17%`，并给了 `prob>0.7 / <0.3`、`0.5% TP/SL`、`max hold 15 bars`、`8 bps` cost 的完整 backtest 骨架。

3. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/itsm_vol_liq_transfer_scan_20260325_1105/summary.json`
- `reports/artifacts/quant_digests/itsm_vol_liq_transfer_scan_20260325_1105/chosen_summary.csv`
- `reports/artifacts/quant_digests/itsm_vol_liq_transfer_scan_20260325_1105/state_scan.csv`
