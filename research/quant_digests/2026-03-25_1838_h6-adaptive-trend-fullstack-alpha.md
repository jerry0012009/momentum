# 别把 AdaptiveTrend 只读成 `70/30` overlay：更该先测的是「H6 own-past momentum + ATR trailing + 月度 Sharpe 选币」完整 raw alpha
- 时间：2026-03-25 18:38 UTC
- 类型：论文（arXiv 近 5 年）
- 主题类型：raw alpha
- 基础 alpha：`6h` 自身过去收益延续（own-past momentum / intermediate-frequency trend following）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/time-series/intermediate-frequency/h6/atr-trailing/asset-selection/portfolio-construction/binance/perpetual/15m/5m/paper
- 证据类型：论文证据（全文可读）+ 公共数据最小快检

## 1. 这次看了什么
这次主看 **Duc Bui, Thanh Nguyen (2026)** 的 arXiv 论文 *Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets*。

这轮不再把它继续拆成 `70/30` 仓位旁支；按当前 desk 对 **raw alpha / 完整策略骨架** 的优先级，更值得先拿出来的是它的主干：

> **用 `6h` own-past momentum 做慢时钟方向，用 `ATR trailing stop` 管退出，用月度 rolling Sharpe 做 universe/参数筛选。**

对我们更重要的人话版是：**不要把 15m desk 的趋势研究只写成“每根 15m 都在追涨”；更像样的读法是“慢信号、快执行”。**

## 2. 核心结论
- **一句话核心结论：** 这篇东西最值钱的不是“又一个趋势指标”，而是把 `entry / exit / selection / sizing / cost` 串成一条完整链，适合直接变成 short-cycle desk 的最小完整策略候选。  
- **一句话它怎么证明：** 论文在 `2022-2024`、`150+` 个 Binance perpetual 上做 OOS 回测、成本建模、ablation 和 timeframe 对比，不只是给一个漂亮 equity curve。  
- 论文报告的主配置结果：`Sharpe 2.41`、`Max Drawdown -12.7%`、`Calmar 3.18`。  
- ablation 里，**动态 trailing stop** 是最大贡献模块之一，报告 `Sharpe +0.73`、`MDD 改善 9.7pct`；**月度参数/选币优化** 贡献更大，报告 `ΔSharpe ≈ +1.07`。  
- 论文还明确给出一个对我们很重要的判断：**`H6` 比 `H1/H4/H8/D1` 更像平衡点**——太快被换手和噪声吃掉，太慢又错过 crypto 的短命延续。

我补了一个很轻的 desk 化快检（Binance Futures 公共 `1h` 数据重采样、top7 主流永续、近 `120d`、`4bps/side`、long-only 简化版 walk-forward）：四个冻结版本全都没转正，但 **`H6` 退化最少**。等权组合总收益：`H1 -4.03%`、`H4 -1.19%`、`H6 -0.70%`、`H8 -0.84%`；平均每窗口交易数：`18.3 / 5.7 / 4.7 / 3.7`。这说明它**还不是可直接照搬的正 alpha**，但 `H6` 作为慢时钟骨架，比硬上 `H1` 更诚实。

## 3. 为什么和当前项目有关
- `LEARNING_TRACK` 里当前主线仍有 **趋势家族 + ATR + 波动管理**；这篇正好把三者接成完整策略，而不是只给一个 trigger。  
- `FACTOR_BACKLOG` 里 ATR sizing、trailing stop、volatility regime 仍缺少一个“完整策略母体”；AdaptiveTrend 正好能补这块地基。  
- 最近 digest 已经补了不少 `mean reversion / XS / relative value / carry`，这篇则把 **trend raw alpha** 重新拉回素材池，而且是**全链条定义清楚**的那种。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 多资产 long-short
- 基础 alpha：`H6` 累计收益超过阈值后的自身延续
- regime：top-cap / 可交易 universe + 月度 rolling Sharpe 选币
- filter / veto：entry threshold；short 侧用更高阈值
- risk / sizing / execution overlay：`ATR trailing stop`、`70/30` long-short 配比、交易费/滑点/资金费建模

## 4. 可复刻的最小实验
- **研究假设：** 对 `5m/15m` desk，更值得测的是“`H6` 信号时钟 + `15m` 执行轨道”，而不是把趋势直接降采样成每根 `15m` 都重新翻单。  
- **数据源 / 公开性：** Binance Futures 公共 OHLCV + funding；CoinGecko/交易所公开市值或流动性代理；都公开可取。  
- **最小口径：**  
  1. universe 先收紧到 `BTC/ETH/SOL/BNB/XRP/DOGE/ADA` 或 top20 liquid USDT perps；  
  2. 用 `15m` 数据聚成 `6h` signal bar；每月只在月初重估一次 `L / θ / ATR multiplier`；  
  3. long：`MOM_H6 > θ` 时下一根 `15m open` 入场；short 先不着急全开，可先做 `70/30` 或 `long-only + short veto` 对照；  
  4. exit 用 `ATR trailing stop`，并强制加入 `4/8/12 bps` 成本层 + funding；  
  5. 先看 `post-cost return / MDD / trade_count / positive_asset_ratio / funding-adjusted pnl`。  
- **下一步怎么测：** 第一轮不要复刻论文全量 `150+` 币。先做 **`H1 vs H4 vs H6 vs H8` 同骨架 honest shootout**，确认 `H6` 是否在 `15m next-open + no overlap + realistic costs` 下依旧最稳；若不是，就把它降格为“slow-clock regime / execution spine”，而不是 raw alpha 主线。

## 5. 风险与保留意见
- 这是 **arXiv 预印本**，不是已同行评审定稿；  
- 我们的本地快检只是 paper-inspired 简化版，不是全文复现；  
- 若 edge 只在 `H6` 原生 bar 上成立、映射到 `15m` 执行后就消失，那它更适合作为 **slow-clock overlay**，不是 desk 主信号；  
- 月度选币 / 月度调参必须严格前视隔离，否则很容易把 walk-forward 写脏。

## 6. 来源
1. **Bui, D., & Nguyen, T. (2026). _Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets_. arXiv (cs.CE).**  
   - Venue: arXiv preprint  
   - DOI: <https://doi.org/10.48550/arXiv.2602.11708>  
   - Readable URL: <https://arxiv.org/abs/2602.11708>  
   - Full Text (HTML): <https://arxiv.org/html/2602.11708v1>  
   - PDF: <https://arxiv.org/pdf/2602.11708>  
   - Repo URL: `N/A（论文页未给公开代码仓）`
2. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). _Time Series Momentum_. Journal of Financial Economics.**  
   - Venue: Journal of Financial Economics  
   - DOI: <https://doi.org/10.1016/j.jfineco.2011.11.003>  
   - Readable URL: <https://www.sciencedirect.com/science/article/pii/S0304405X11002613>

## 7. 本地 artifacts
- `reports/artifacts/quant_digests/adaptivetrend_h6_quickcheck_20260325_1838/summary.json`
