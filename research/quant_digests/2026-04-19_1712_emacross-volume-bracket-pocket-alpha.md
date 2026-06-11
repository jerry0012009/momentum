# 别把这份 2026 多策略 bot 只读成 beginner 拼盘：对 short-cycle crypto desk，更该先拆的是「EMA crossover × volume expansion × hard bracket exit」这条完整 raw alpha 壳
- 时间：2026-04-19 17:12 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `trading_engine.py` + `config.yaml` + `docs/BACKTEST_RESULTS.md`）+ Binance USDⓈ-M `15m` portability probe（8 liquid majors，近 `120d`）
- 主题类型：raw alpha
- 基础 alpha：短周期趋势启动时，`9/21 EMA` 金叉/死叉配合成交量放大，后续更容易继续走出一段可兑现 drift
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend/momentum/ema-crossover/volume-confirmation/bracket-exit/stop-loss/take-profit/binance-perpetual/15m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 配置参数 + 本地最小回测探针

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是“EMA crossover 确认短周期趋势切换，再用 volume expansion 过滤假突破”，不是 filter / overlay。**

主材料是 2026 GitHub 仓库 **PatrickSebastine/mean-reversion-trading-bot**。虽然 repo 名字里更强调 mean reversion，但对当前 desk 更值得 intake 的旁支，其实是里面那条**规则完整、可独立复现、可直接落地**的 momentum 壳：
- `9/21 EMA` 金叉/死叉给方向
- `RSI` 只做“不追太过头”的基础约束
- `volume > 1.5x 20-bar avg` 做 breakout 质量确认
- 风控直接写死：`2% stop / 4% take-profit / 10% position / 3% daily breaker`

这比很多只给 entry、不交代 exit/sizing/risk/cost 的 repo 更适合进当前 raw alpha 素材池，因为它给的是一整套**可最小复刻的完整策略骨架**。

## 2. 核心结论
- **一句话结论：** 这条 repo-based momentum 线可以当作完整 raw alpha skeleton 收进池子，但当前更像 **BTC-first selective pocket**，不是拿去对 8 个 liquid majors 一把梭的 broad-book 方案。
- **一句话证据：** 我按 repo 源码规则重写了一个最小探针，在 Binance USDⓈ-M `15m`、近 `120d`、`8` 个 liquid majors 上做 portability probe；结果显示整体 barely positive，但币种分化很大。

最关键 5 个数据点：
1. **全样本合并**：`88` 笔，扣除 `6 bps` roundtrip 成本后，`ALL_EQ avg_net_bps = +0.35 bps/笔`，说明**整体只是勉强站在线上**。  
2. **BTCUSDT 最强**：`14` 笔，`avg_net_bps = +61.10`，`hit rate = 57.1%`。  
3. **ETHUSDT 也能活**：`7` 笔，`avg_net_bps = +31.12`，但样本数偏少。  
4. **DOGE / LINK / ADA` 只是弱正**：分别约 `+12.34 / +8.44 / +2.93 bps/笔`，离“稳定 production alpha”还差得远。  
5. **SOL / XRP / AVAX 明显拖后腿**：`avg_net_bps = -37.80 / -26.63 / -48.05`，说明这套规则并不具备普适跨币稳定性。  

## 3. 为什么和当前 desk 直接相关
这轮不该再把“完整策略骨架”都让给 mean reversion / pairs。这个 repo 的价值在于，它补的是 **single-asset trend / momentum raw alpha**，而且不是只有 headline alpha：
- **entry** 清楚：`EMA crossover + volume confirmation`
- **exit** 清楚：`2% stop / 4% TP`
- **sizing** 清楚：仓位按 balance 百分比
- **risk** 清楚：daily loss breaker + max open positions
- **cost** 清楚：可以直接转成 bps 成本压力测试

也就是说，它不是“值得读一读”的材料，而是**可以立刻进复现实验队列**的 raw alpha skeleton。

## 3.5 策略拆解（必填）
- 方向属性：单资产双向 trend / momentum
- 基础 alpha：趋势切换后的短段 drift continuation
- regime：成交量放大、快慢均线刚完成交叉时更像可交易 pocket
- filter / veto：低量能交叉、已明显超买/超卖、连续 whipsaw 段应 veto
- risk / sizing / execution overlay：
  - repo 默认 `2% stop / 4% TP / 10% balance sizing / 3% daily loss breaker`
  - short-cycle 真实瓶颈不在“有没有止损”，而在**交叉滞后 + 假突破 + taker 成本**
  - 如果要生产化，优先改的是 admission / execution，不是先堆更多指标

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：`PatrickSebastine/mean-reversion-trading-bot` 仓库源码（公开）
- 数据源 B（代理回测数据）：Binance USDⓈ-M Futures Klines（公开 REST，无需 API key）
- 更新频率：支持 `15m`（本轮用 `15m`；后续可下钻 `5m` child execution）
- 最小实验口径：
  - 标的：`BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK`
  - 样本：近 `120d`
  - 信号：`9/21 EMA crossover + RSI gate + volume > 1.5x 20-bar avg`
  - 出场：`2% stop / 4% TP / 64-bar max hold`
  - 成本：`6 bps` roundtrip 代理口径

### 4.2 快检结果怎么读
- **这条线不是“全币都能跑”的通用趋势 alpha。** BTC 很强，ETH 尚可，但部分高 beta 币反而被 whipsaw 吃掉。
- **volume confirmation 有价值，但还不够。** 如果只靠 `1.5x avg vol`，仍然挡不住不少假交叉。
- **更合理的落地姿势，是把它当作 selective pocket + execution shell。** 先缩到 `BTC/ETH`，再考虑是否给 alt 扩编。

## 5. 下一步怎么测
1. **先做 BTC/ETH-only stability table**：同样规则扫 `5m/15m/30m`，看 edge 是来自 timeframe，还是来自单一币种偶然样本。  
2. **加入 ADX / BB-width / ATR-expansion admission**：不是改 base alpha，而是测试“哪类 crossover 更像真 breakout”。  
3. **把 exit 从固定 `4% TP` 改成 trailing / signal-flip**：检查这条线到底更像“短 R multiple shell”，还是“让利润奔跑”的 drift sleeve。  
4. **做 long/short 分腿统计**：当前多个山寨负样本可能主要是 short leg 或 chop 段导致，先拆开再判断要不要做方向偏置。  
5. **做成本压力测试**：至少输出 `4/6/8/10 bps` cost ladder；若 `BTC/ETH` 在 `+50%` 成本压力下仍为正，才值得进下一轮更细复现。  

## 6. 风险与保留意见
- 这轮 probe 是按 repo 公开规则写的**最小代理回测**，不是逐行复刻作者引擎，所以它更像 intake 证据，不是最终定案。  
- `88` 笔总交易数不算多，说明这条线频率本来就不高；若 desk 真要映射到 `5m`，更可能是**15m setup + 5m 执行**，而不是纯 5m 主信号。  
- 固定 `2%/4%` bracket 在不同币种上并不公平，部分负样本可能来自波动尺度不匹配，而不一定是否定 base alpha 本身。  

## 7. 来源
1. **Patrick Sebastine. (2026). _mean-reversion-trading-bot_. GitHub repository.**  
   - Repo URL: https://github.com/PatrickSebastine/mean-reversion-trading-bot  
   - Readable URL: https://github.com/PatrickSebastine/mean-reversion-trading-bot
2. **Patrick Sebastine. (2026). _README.md_ / _trading_engine.py_ / _config.yaml_ / _docs/BACKTEST_RESULTS.md_.**  
   - README: https://github.com/PatrickSebastine/mean-reversion-trading-bot/blob/master/README.md  
   - Engine: https://github.com/PatrickSebastine/mean-reversion-trading-bot/blob/master/trading_engine.py  
   - Config: https://github.com/PatrickSebastine/mean-reversion-trading-bot/blob/master/config.yaml  
   - Backtest results: https://github.com/PatrickSebastine/mean-reversion-trading-bot/blob/master/docs/BACKTEST_RESULTS.md
3. **Binance Developers. _USDⓈ-M Futures Kline/Candlestick Data_.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 8. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_emacross_volume_bracket_probe.py`
- Summary：`reports/artifacts/quant_digests/emacross_volume_bracket_probe_summary_2026-04-19.csv`
- Trades：`reports/artifacts/quant_digests/emacross_volume_bracket_probe_trades_2026-04-19.csv`
