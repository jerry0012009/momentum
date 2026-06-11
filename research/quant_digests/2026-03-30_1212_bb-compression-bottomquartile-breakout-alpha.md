# 别把 squeeze 直接升级成短周期 alpha：这份 2026 新仓库里更该先诚实快检的是「bottom-quartile BB compression breakout」raw alpha 候选
- 时间：2026-03-30 12:12 UTC
- 类型：2026 GitHub 新仓库 + `bb_compression.py` / `main.py` / `risk.py` source audit + Binance USDⓈ-M Perpetual 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：15m 液态 perp 在最近 `50` 根里属于最窄 `25%` 的 Bollinger 压缩后，若价格向 band 外突破，后面一段应继续沿突破方向扩张
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/breakout/compression/bollinger-band/squeeze/vol-expansion/continuation/liquid-perps/hyperliquid/binance/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：仓库源码 + 公开交易所数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这是 raw alpha，不是 filter。alpha body 就是“低波压缩后向 band 外突破，赌扩张延续”，而不是先有别的主信号再拿 squeeze 当确认。**

本轮主看 **OlieSmith (2026) 的 `HyperLiquidBot`**，但我没有把整仓库按“多策略投票 bot”去读；更适合我们 desk 的，是把里面能独立成立的一条腿单独拎出来：`strategies/bb_compression.py`。

源码把这条腿写得很直白：
- 周期：`15m`
- 宽度定义：`BB(20,2)` 的标准化 band width
- 压缩定义：当前 width 位于最近 `50` 根里的 **bottom 25%**
- 入场：`close > upper BB` 做多，`close < lower BB` 做空
- 评分：`compression_score * 0.7 + breakout_pct * 0.3`

仓库主循环还额外给了完整落地壳：
- universe：`24h volume > $1m` 的 Hyperliquid liquid perps
- veto：只允许顺 `200-bar SMA` 方向开仓
- sizing：按 conviction 做 `2% / 5% / 10%` 仓位
- risk：`ATR(14) * 3` trailing stop，并夹在 `1%~8%`
- cooldown：平仓后 `30min`

所以它不是“又一个 squeeze 观察器”，而是一个**可独立复现的 15m breakout alpha 候选**。但候选不等于晋级——我额外做了一个公开数据最小快检。

## 2. 核心结论
- **一句话结论：** 这条 `bottom-quartile BB compression breakout` 的 alpha body 很清楚，但在我这次公开 Binance perpetual `15m` proxy 上，**还不够好到直接升格成 desk 的 standalone raw alpha**。
- **一句话它怎么证明：** 我按 repo 的核心规则做了一个诚实快检：`next-bar open` 入场、`ATR*3` trailing stop、`3bps/side` 成本、`200-SMA` 方向过滤、`30min` cooldown，先在 `BTC/ETH/SOL` 三个公开可取的 majors 上看 120 天结果。

关键数据点（Binance USDⓈ-M Perpetual，近 `120d`，`15m`，独立最小 proxy）：
1. **BTC：`100` 笔，胜率 `39.0%`，总收益 `-4.8%`，平均持仓 `29.0` 根 15m bar。**
2. **ETH：`98` 笔，胜率 `34.7%`，总收益 `-14.2%`，平均持仓 `15.8` 根 bar。**
3. **SOL：`106` 笔，胜率 `25.5%`，总收益 `-33.8%`；去掉 `200-SMA` 过滤后更差，BTC 会从 `-4.8%` 恶化到 `-16.2%`。**

这几个数说明三件事：
- **压缩突破本体是 clear raw alpha 假说**，不是概念不清；
- 但它在公开 proxy 上**没有自动变成可上线的 standalone breakout 策略**；
- `200-SMA` 方向过滤 **有帮助，但只是在止血，不是在把负 alpha 变正**。

当前更诚实的 verdict：**`admit_to_research_pool / do not promote as standalone yet`**。

## 3. 为什么和当前 desk 直接相关
这轮仍然值得写，原因不是“又学了个 squeeze 指标”，而是它补了一个我们当前 raw alpha 池里还没单独冻结下来的命题：

- **它是原生 breakout / expansion alpha**，和最近 intake 的 mean reversion / pairs / options parity 不是同一类；
- **repo 是 2026 新源**，且把 entry / sizing / trailing stop / cooldown 一次写全，迁移到 desk 非常便宜；
- **最关键的是它被快检打回来了**：这会帮我们避免把“压缩 + band breakout”误升成主线 alpha，而更可能把它降级成 breakout 家族的 participation gate 或 vote leg。

也就是说，这篇笔记不是在吹它，而是在帮素材池更快完成 **“可复现 ≠ 可晋级”** 的筛选。

## 3.5 策略拆解（必填）
- 方向属性：突破 / 波动扩张 continuation
- 基础 alpha：低波压缩结束后的方向性扩张
- regime：最近 `50` 根里处于低 width 分位时最相关
- filter / veto：仓库主循环里的 `200-bar SMA` 是方向过滤，不是 alpha 本体
- risk / sizing / execution overlay：`ATR*3` trailing stop、`1%~8%` 止损带、`2/5/10%` conviction sizing、`30min` cooldown、`max_positions=10`

## 4. 与 `1m/3m/5m/15m` 的关系（实话版）
- **15m：原生周期。** 这条线现在最适合先留在 `15m` 做真假判定。
- **5m：可迁移，但不要直接照抄 `20/50`。** 更合理的是按等效时间窗缩放到约 `60` 根 BB 窗口、`150` 根压缩 lookback，再重新做 width percentile。
- **3m / 1m：目前不建议直接下钻。** 既然 `15m` public proxy 还没过生存线，更快周期大概率先被噪音和成本吃掉，除非先补 order-flow / volume-expansion / session filter。

## 5. 最小可复现实验口径（本轮）
### 5.1 数据源、公开性、更新频率
- repo 原始执行环境：Hyperliquid perpetuals（公开 API，可分钟级轮询）
- 本轮 proxy 数据：Binance USDⓈ-M Perpetual `klines`（公开 REST）
- 更新频率：原始信号 `15m`，可迁移到 `5m/3m/1m`

### 5.2 本轮独立快检口径
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 样本：近 `120d`
- 信号：`BB(20,2)`；当前标准化 band width 属于最近 `50` 根 **bottom 25%**；close 突破上/下 band
- 入场：`next-bar open`
- 方向过滤：仅做 `200-SMA` 同向突破
- 出场：`ATR(14) * 3` trailing stop，且限制在 `1%~8%`
- 冷却：`30min`
- 成本：`3bps/side`
- 结果文件：`reports/artifacts/quant_digests/bb_compression_hyperliquidbot_20260330_mincheck.csv`

## 6. 下一步怎么测（必须）
1. **先做 participation ablation**：在当前 breakout body 上依次加 `volume spike`、`dollar-volume expansion`、`funding 同向/逆向 veto`，看它到底缺的是参与度过滤还是 alpha body 本身就不够强。  
2. **做 timeframe transfer**：把 `15m` 规则缩放到 `5m`（如 `BB≈60`、compression lookback≈`150`），比较 `post-cost return / trade count / avg hold / false breakout ratio`。  
3. **做 standalone vs vote-leg 对照**：比较 `纯 bb_compression`、`bb_compression + trend_following 共识`、以及 `bb_compression 仅作 admission gate` 三种角色，确认它更像主 alpha 还是组合里的一票。  
4. **做 universe 筛选**：只保留 `BTC/ETH` 或 `top-dollar-volume decile`，不要默认让这条线在 SOL 这类高噪声标的一视同仁。  
5. **做成本阶梯**：至少测 `2/4/6/8 bps` 总成本；若只在超低成本下存活，就把它标成 execution-sensitive toy，不要误判成稳健 breakout alpha。  

## 7. 风险与保留意见
- 这是 **repo-based 新候选**，不是论文里经过正式统计检验的结论；当前最硬的证据仍是源码 + public proxy。  
- 仓库真正运行时是 **多策略聚合**，`bb_compression` 可能更适合作为组合中的一票，而不是 standalone。  
- 本轮 proxy 用的是 Binance perpetual，不是 Hyperliquid 原生撮合；负 verdict 不等于永远无效，但已经足够阻止我们把它直接升成主线。  

## 8. 来源
1. **OlieSmith. (2026). _HyperLiquidBot_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/OlieSmith/HyperLiquidBot  
   - Repo URL: https://github.com/OlieSmith/HyperLiquidBot
2. **OlieSmith. (2026). _strategies/bb_compression.py_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/OlieSmith/HyperLiquidBot/main/strategies/bb_compression.py  
   - Repo URL: https://github.com/OlieSmith/HyperLiquidBot/blob/main/strategies/bb_compression.py
3. **OlieSmith. (2026). _main.py_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/OlieSmith/HyperLiquidBot/main/main.py  
   - Repo URL: https://github.com/OlieSmith/HyperLiquidBot/blob/main/main.py
4. **OlieSmith. (2026). _risk.py_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/OlieSmith/HyperLiquidBot/main/risk.py  
   - Repo URL: https://github.com/OlieSmith/HyperLiquidBot/blob/main/risk.py
5. **Binance Developers. _USDⓈ-M Futures Market Data: Kline/Candlestick Data_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 9. 本地复现产物
- `reports/artifacts/quant_digests/bb_compression_hyperliquidbot_20260330_mincheck.csv`
