# 别把 BB 触边只当老派指标：这份 2026 新仓库更值得先复现的是「5m BTC 均值回归 + EMA 趋势过滤 + 诚实出场」完整 raw alpha 骨架
- 时间：2026-03-24 03:18 UTC
- 类型：2026 GitHub 新仓库 + 本地独立最小复核 + 论文地基
- 主题类型：raw alpha
- 基础 alpha：5m BTC 在中期趋势未破坏时，价格向 Bollinger Band 极端伸展后，向均值/对侧带回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/bollinger/ema/btc/5m/hyperliquid/binance/entry-exit/sizing/cost/repo/paper/crypto
- 证据类型：仓库源码 + 公开回测脚本 + 本地独立最小复核

## 1. 这次看了什么
先回答 base alpha：**这不是 filter，而是一个原生 raw alpha——在 EMA(200) 定义的趋势方向里，做 5m 的 band-edge mean reversion。**

本轮主看 **debugger-engineer (2026) 的 `btc-trading-bot`**。它最值得收进素材池的，不是“Bollinger 这三个字”，而是它把完整策略链条一次写清了：
- entry：`price <= lower BB 且 > EMA200` 做多；`price >= upper BB 且 < EMA200` 做空
- exit：对侧 band 止盈、`2.5%` 硬止损、以及 `inverted TP -> break-even`
- execution：在 band 位置挂限价单，若 60 秒内没成交或价格走远就撤单
- sizing：按 `target_risk_pct / (leverage * stop_loss_pct)` 反推仓位

这符合当前 desk 的最高优先级：**可独立复现、且可直接落地为完整策略的 5m raw alpha。**

## 2. 核心结论
- **一句话结论：** 这份新仓库真正值钱的不是 README 里那串收益数字，而是它把“趋势内短线回归”写成了可直接 first-verdict 的完整策略骨架。
- **一句话它怎么证明：** 源码和公开回测脚本把信号、出场、费用和仓位都写死了；我再按仓库逻辑独立重跑 Binance 5m BTC，确认它不是只有标题党、但也比 README 宣传更薄更诚实。

关键数据点（本地独立复核，按仓库脚本口径）：
1. **365d：954 笔，胜率 `59.85%`，净收益 `$1119.55`，平均每笔 `$1.17`**（固定 `$475` notional / `$95` 保证金口径）。
2. **90d：236 笔，胜率 `61.86%`，净收益 `$331.85`，平均每笔 `$1.41`。**
3. **平均持仓约 `30.4` 根 5m bar（约 2.5 小时），365d 里只有 `7` 次硬止损。**

这几个数有两个重要含义：
- 它确实像一个**短持有期、可密集复核**的 5m raw alpha；
- 但 README 声称的 `69%` 胜率、`~88.8% annually` 并没有被我这次独立重跑原样复现，所以**它更像“值得测”，不是“可直接信”**。

## 3. 为什么和当前 desk 直接相关
这轮价值很直接：我们最近 intake 里 pairs / relative-value / event alpha 已经不少，而这条线补的是 **单币、短持有、原生 5m、规则极少的 mean reversion 主策略**。

它对当前素材池的补充点在于：
- **raw alpha 足够清楚**：不是“加个 BB filter”，而是直接拿 band stretch 当入场本体；
- **执行链条完整**：entry / exit / sizing / cost 全有；
- **迁移成本低**：天然适合先做 `5m`，再压到 `3m/1m` 或放大到 `15m`。

## 3.5 策略拆解（必填）
- 方向属性：均值回归（但只在 EMA 定义的趋势方向里开仓）
- 基础 alpha：短线过度伸展后，回到带中轴/对侧带的概率大于随机
- regime：趋势未坏、但局部波动过冲时更友好
- filter / veto：EMA200 本质上是方向约束，不是这篇策略的 alpha 本体
- risk / sizing / execution overlay：2.5% hard stop、break-even 保护、限价进场、风险反推仓位、maker/taker fee 区分

## 4. 与 `1m/3m/5m/15m` 的关系（实话版）
- **5m：原生成立。** 这是这篇最适合我们 desk 的地方。
- **3m/1m：可以测，但必须先过成本生存线。** 更快周期容易把“回归 edge”磨成手续费和滑点。
- **15m：可迁移，但不要机械照搬 20 bar。** 更合理的是先做“等效时间窗”换算：`20x5m≈100 分钟`，15m 先从 `7 bar` 左右起步，而不是盲抄 `20 bar`。

## 5. 最小可复现实验口径（本轮）
### 5.1 数据源、公开性、更新频率
- 价格信号：Binance `BTCUSDT` 5m K 线（公开 REST，分钟级可取）
- 执行假设：Hyperliquid perp（仓库原始执行环境）
- 更新频率：5m 主周期；可映射到 `1m/3m/15m`

### 5.2 本轮独立复核口径
- 规则：仓库 `BB(20,2) + EMA(200) + SL=2.5%`
- 成本：maker `1bp`；stop 出场按 taker `5bp`
- 样本：近 `30/90/180/365d` Binance 5m BTC
- 结果文件：`reports/artifacts/quant_digests/bb_ema_hyperliquid_style_20260324/metrics.json`

## 6. 下一步怎么测（必须）
1. **先做执行诚实化**：把“band 触发即成交”改成 `next-bar open`、`band 限价 1 bar`、`maker/taker 混合` 三种成交模型，先看 edge 剩多少。  
2. **做频率迁移**：按等效时间窗把策略迁到 `3m / 15m`，比较 `post-cost expectancy / trade count / avg hold`，确认它到底是 5m 特供还是能跨频率生存。  
3. **做 filter ablation**：比较 `有 EMA200`、`无 EMA200`、`只做多`、`只做空`，判断 EMA 是真 edge 还是只是减少反向交易。  
4. **做跨标的复核**：同口径测 `ETH/SOL`，如果只在 BTC 活，就把它标记成 `BTC-specific raw alpha`，别误升成通用模板。  
5. **做 friction ladder**：至少测 `2/4/6/8 bps` 总成本；若成本略升就失活，这条线只能算 research toy。  

## 7. 风险与保留意见
- 仓库很新，README 数字与本次独立重跑存在偏差，必须防宣传口径与真实口径不一致。  
- 该策略属于**趋势内均值回归**，最怕单边加速行情；若 1m/3m 强行下钻，滑点与连续冲击会明显放大。  
- 目前复核只用了 Binance 价格代理，尚未做 Hyperliquid 原生撮合口径与资金费率影响。  

## 8. 来源
1. **debugger-engineer. (2026). _btc-trading-bot_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/debugger-engineer/btc-trading-bot  
   - Repo URL: https://github.com/debugger-engineer/btc-trading-bot
2. **debugger-engineer. (2026). _test/backtest_perps.py_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/debugger-engineer/btc-trading-bot/main/test/backtest_perps.py  
   - Repo URL: https://github.com/debugger-engineer/btc-trading-bot/blob/main/test/backtest_perps.py
3. **Svogun, D., & Bazán-Palomino, W. (2022). _Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?_ Journal of International Financial Markets, Institutions and Money, 79, 101601.**  
   - Venue: Journal of International Financial Markets, Institutions and Money  
   - DOI: https://doi.org/10.1016/j.intfin.2022.101601  
   - Readable URL: https://api.crossref.org/works/10.1016/j.intfin.2022.101601  
   - Repo URL: N/A
4. **Binance Developers. _Spot Market Data Endpoint: Kline/Candlestick data_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
5. **Hyperliquid Docs. _API / exchange docs_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/

## 9. 本地复现产物
- `reports/artifacts/quant_digests/bb_ema_hyperliquid_style_20260324/metrics.json`
