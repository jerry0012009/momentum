# 别把这份 2026 Binance Futures bot 只读成“技术指标大杂烩”：对 short-cycle crypto desk，更该先拆的是「EMA200 趋势内 shallow Fibonacci pullback × MACD recross」这条完整 raw alpha 壳
- 时间：2026-04-19 18:15 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `TradingStrats.py` + `LiveTradingConfig.py` + `TradeManager.py`）+ Binance USDⓈ-M `15m/5m` portability probe（10 liquid majors，约 `6000` bars / symbol）
- 主题类型：raw alpha
- 基础 alpha：趋势未坏时，价格只做浅层回撤（约 `23.6%~38.2%` Fibonacci 区间），若随后出现 MACD 回正/回负 + engulfing 确认，下一段更容易恢复原方向 drift
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend-pullback/continuation/fibonacci/macd/engulfing/ema200/bracket-exit/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 配置参数 + 本地最小回测探针

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“顺趋势浅回撤后的 continuation”，不是 filter / overlay。**

主材料是 2026 GitHub 仓库 **Siddharth-war/Trading-Bot-For-Binance-Future**。repo 表面上是“11 个技术分析策略合集”，但对当前 desk 真正值得 intake 的不是整包，而是 `fibMACD` 这一条更完整的 raw alpha skeleton：
- `EMA200` 先判大方向；
- 最近 `100` 根里用 swing high / low 定最近一段 impulsive leg；
- 只在 pullback 落到 Fibonacci 回撤区间时观察；
- 再用 `MACD` 重新同向穿越 + engulfing candle 确认；
- 风控在配置里直接给出 `TP=1% / SL=1.5%` 的硬 bracket。  

这条线对我们有价值，不是因为 Fibonacci 本身多神，而是它把 **entry / exit / risk** 都交代清楚了，很适合做“完整策略最小实验”。

## 2. 核心结论
- **一句话结论：** 这条线当前不是“所有回撤都值得抄”的 broad-book 方案，而更像 **trend continuation 里的 long-biased shallow-pullback pocket**。  
- **一句话证据：** 我按 repo 规则重写最小探针，在 Binance USDⓈ-M `10` 个 liquid majors 上做 `15m/5m` portability probe；结果显示 **15m long 明显优于 short，且浅回撤（zone 1~2）明显优于深回撤**。

最关键 5 个数据点：
1. **15m long 全样本**：`n=14`，`gross_mean≈+17.86 bps/trade`，粗扣 `8 bps` 后 `net≈+9.86 bps`。  
2. **15m short 全样本**：`n=11`，`gross_mean≈-50.71 bps`，明显不能照搬成对称多空。  
3. **5m long 全样本**：`n=7`，`gross_mean≈+21.59 bps`，但样本太少，现阶段更像 child-execution pocket，不适合直接抬成主线。  
4. **浅回撤更像样**：`15m long` 里只看 Fibonacci `zone 1~2`（约 `23.6%~38.2%` 回撤）共 `n=6`，平均约 **`+60.72 bps gross`**；深回撤 `zone 3~5` 明显转弱。  
5. **退出分布很直白**：`15m long` 的 `6` 笔 TP hit 都是 **`+100 bps`**，但两笔 SL 直接 **`-150 bps`**，说明这条线不是“均匀小优势”，而是典型 **低频 bracket continuation shell**。  

## 3. 为什么和当前 desk 直接相关
这轮值得保留的，不是“再补一篇形态学文章”，而是补一个**可直接落地的趋势 pullback raw alpha skeleton**：
- **entry**：EMA200 趋势方向 + shallow fib pullback + MACD recross + engulfing
- **exit**：硬 `1% TP / 1.5% SL`
- **sizing**：repo 默认按账户百分比下单
- **risk**：单笔 bracket，很容易接入 cost ladder / hit-rate / expectancy 检查
- **cost**：能直接按 `4/6/8/10 bps` 做摩擦压力测试

更关键的是，这条线补的是当前池子里相对少一点的 **“顺趋势回踩 continuation 完整壳”**，而不是再补一个只有 signal、没有 exit 的半成品指标。

## 3.5 策略拆解（必填）
- 方向属性：单资产、偏 long 的 trend-pullback continuation
- 基础 alpha：趋势 leg 后的浅层回撤，如果很快重新被顺势买回/卖回，后续更容易续走原方向
- regime：`EMA200` 同向、回撤不深、MACD 只是短暂回调而非大级别翻转时更像可交易 pocket
- filter / veto：
  - 深回撤（`zone 3~5`）默认降级；
  - short leg 当前证据弱，默认不对称照搬；
  - 若波动太大导致 `1%/1.5%` bracket 失真，也应先 veto
- risk / sizing / execution overlay：
  - repo 默认 `TP=1% / SL=1.5%`
  - desk 更适合先保留 `15m` 母信号，再看是否用 `5m` 优化挂单/追单执行

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：GitHub 公开仓 `Siddharth-war/Trading-Bot-For-Binance-Future`
- 数据源 B（代理回测数据）：Binance USDⓈ-M Futures Klines（公开 REST，无需 API key）
- 更新频率：原仓默认可跑 `1m`，本轮 portability probe 优先用 `15m / 5m`
- 最小实验口径：
  - 标的：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`
  - 样本：每币约 `6000` 根 bar（`15m` 约 `62.5d`，`5m` 约 `20.8d`）
  - 信号：尽量按 repo `fibMACD` 规则重建 recent swing、Fib zone、MACD recross、engulfing
  - 出场：`TP=1% / SL=1.5%`，若未触发则 `15m` 最多持有 `12` bars、`5m` 最多 `18` bars 作为 desk 最小超时口径
  - 成本：粗扣 `8 bps` roundtrip

### 4.2 快检结果怎么读
- **真正能保留的旁支，不是“fib 全部有效”，而是 shallow pullback continuation。** 这正是更适合 short-cycle desk 的 desk 读法。  
- **short leg 当前不能直接收。** 15m short 平均明显为负，说明这条线至少现在不该做成对称 long/short 自动壳。  
- **5m 更像执行层，不像 base alpha 主周期。** 有正 pocket，但样本更稀，先别把它硬包装成 5m 主策略。  

## 5. 下一步怎么测
1. **先只保留 `15m long + zone 1~2`**，输出 `4/6/8/10 bps` cost ladder，看 edge 是否还能站住。  
2. **把 bracket 改成 ATR-normalized**：检验当前好坏到底来自 alpha 本体，还是固定 `1%/1.5%` 对不同币波动尺度不公平。  
3. **做 `15m signal -> 5m child execution`**：比较 next open、VWAP-style delay、限价回补三种入场。  
4. **补 volatility / funding veto**：确认失败样本是不是集中在高波动反抽或 funding 挤兑环境。  
5. **扩历史但缩 universe**：先集中在 `BTC/ETH/BNB/LINK` 这类更像 trend-friendly 的币，确认它是不是 selective pocket，而不是全市场 alpha。  

## 6. 风险与保留意见
- 这轮是 **repo portability probe**，不是逐行复刻作者完整交易引擎；所以它更适合做 intake verdict，不是最终定版。  
- 交易数偏少，说明这条线天然低频；它更适合作为“素材池里的完整策略原型”，而不是立即上 production。  
- Fibonacci zone 在这里更像“回撤深浅编码方式”，不是神秘数字本身；后续完全可以改写成 ATR pullback depth / percent pullback depth 做等价检验。  

## 7. 来源
1. **Siddharth-war. (2026). _Trading-Bot-For-Binance-Future_. GitHub repository.**  
   - Repo URL: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future  
   - Readable URL: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future
2. **Siddharth-war. (2026). _TradingStrats.py_ / _LiveTradingConfig.py_ / _TradeManager.py_ / _README.md_.**  
   - README: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future/blob/main/README.md  
   - TradingStrats: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future/blob/main/TradingStrats.py  
   - LiveTradingConfig: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future/blob/main/LiveTradingConfig.py  
   - TradeManager: https://github.com/Siddharth-war/Trading-Bot-For-Binance-Future/blob/main/TradeManager.py
3. **Binance Developers. _USDⓈ-M Futures Kline/Candlestick Data_.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 8. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe.py`
- Trades：`reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_events.csv`
- Summary：`reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_summary.csv`
- Router summary：`reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_router_summary.csv`
- JSON summary：`reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_summary.json`
