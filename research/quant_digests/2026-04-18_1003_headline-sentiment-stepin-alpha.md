# 别把 Binance 这份 sentiment backtester 只读成“AI 新闻 demo”：对 short-cycle crypto desk，更该先测的是「headline polarity × next-few-bar drift」这条 event-driven raw alpha
- 时间：2026-04-18 10:03 UTC
- 类型：GitHub repo source audit + Binance Spot `1m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`crypto headline polarity（bullish / bearish）会在发布后的下几个 1m bar 里带来同向价格漂移`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：event-driven / sentiment / news / BTC / 1m / 5m / 15m / external-data / public-data / repo / cost / risk
- 证据类型：工程经验 + repo audit + public-data probe

## 1. 这次看了什么
看的是 Binance 官方仓 `binance/ai-trading-prototype-backtester`。它不是在发明复杂模型，而是把一条很朴素的 raw alpha 假设写成了可复跑骨架：新闻标题被标成 `bullish / bearish / unknown` 后，按分钟对齐到 BTCUSDT K 线，在有新 headline 的 bar 里做一步交易。

## 2. 核心结论
- **一句话核心结论**：这份 repo 真正可复用的，不是“AI 新闻一定能赚”，而是**把外部新闻事件干净映射到 `1m/5m/15m` 交易实验**的骨架。
- **一句话证明方式**：我直接审了 repo 的 `StrategyManager` / `successive_strategy` / sample `sentiment_data.csv`，再把样本里的 `48` 个可用 `bullish/bearish` 事件对齐到 Binance Spot `BTCUSDT 1m` 公共数据做 event study。
- repo 默认逻辑很简单：上一根到这一根之间若出现新 headline，就取**最后一条**标签；`bullish` 买 `order_quantity`，`bearish` 卖同样数量，`unknown` 跳过；仓位只靠 `total_quantity_limit` 限制。
- 这说明它的 base alpha 很清楚：**headline polarity -> short-horizon directional drift**；不是 filter，也不是 overlay。
- 但我用 repo 自带样本（2023-07-30~2023-08-27，`44` 条 bullish、`4` 条 bearish）做 portability probe 后，signed mean 并不漂亮：next `1m/5m/15m` 约 `-0.44 / -1.67 / -4.23 bps`；哪怕只看 bullish，也只有 next `3m` 微正（约 `+0.54 bps`），其余主要是负的。
- 所以当前 first verdict 很直接：**“新闻情绪一出来就追 BTC” 这条裸 directional 读法不够厚**；更像应该往“headline class / source quality / surprise filter / cross-sectional routing”继续拆，而不是直接照抄 successive buy/sell。

## 3. 为什么和当前项目有关
它和 `momentum` 有关，不在于新闻一定比价格信号更强，而在于它补了我们研究池里相对缺的一块：**公开可得的外部事件型 raw alpha 骨架**。如果后面要接入 Twitter/NewsAPI/RSS/ETF headlines/监管事件，这份 repo 提供了最小可复现路径：事件时间戳、标签、分钟对齐、单事件持有窗、成本后判断。

## 3.5 策略拆解（必填）
- 方向属性：事件驱动 / 单资产方向
- 基础 alpha：`headline polarity -> next-few-bar drift`
- regime：高关注新闻、单一资产对新闻更敏感时可能更强
- filter / veto：新闻源质量、headline surprise、同分钟多条冲突新闻、事件后成交量/波动扩张
- risk / sizing / execution overlay：单事件固定持有窗、事件后 `1~3 bar` time stop、headline score 分层 sizing、只做高置信度来源

## 4. 可复刻的最小实验
- 研究假设：高置信度 bullish headline 后，`BTC/ETH/SOL` 在 next `1/3/5/15m` 更容易同向漂移；bearish 同理。
- 可计算定义：按分钟聚合新闻，保留每分钟最后一条有效标签；计算 `signed_return = sign(sentiment) * fwd_return`。
- 最小回测切口：先用 repo 自带 `sentiment_data.csv` + Binance `data.binance.vision` `BTCUSDT 1m`；然后再换成更干净的实时 RSS / NewsAPI / ETF headline feed，扩到 `ETH/SOL`。
- 最该先看：`signed mean bps` 和 `hit rate`；第二步再看按 source / headline type 分层后的 tail。
- **下一步怎么测**：不要继续测 repo 默认“连续加仓”。先把 headline 分成 `exchange/product/listing/regulation/security` 五类，只保留 `source in {Reuters, Binance, ETF issuers, exchange official}` 的高置信度事件，再比较 next `1/3/5m` 的 signed drift 是否从当前负值翻正。

## 5. 风险与保留意见
- 这份 repo 自带样本很小，而且 `bearish` 只有 `4` 条，明显不够下强结论。
- 新闻标签是离线情绪分类结果，不等于 live 时点可无延迟拿到；真实可交易性会被抓取延迟和 headline 去重吃掉。
- 它默认只做 BTC 单资产，实际上这类新闻可能更适合做**cross-sectional router**（例如利好交易所生态币、利空相关主题币），不一定该压成 BTC 主信号。
- 因此这轮我仍把它记为 **raw alpha 候选**，但不是现成 production shell。

## 6. 数据源与公开性
- 新闻数据：repo 自带 `sentiment_data/sentiment_data.csv`，字段含 `source / collected_timestamp / published_timestamp / headline / sentiment`。
- 价格数据：Binance `data.binance.vision` Spot `BTCUSDT 1m` daily klines，公开可得。
- 更新频率：新闻为事件驱动；K 线为 `1m`。
- 最小可复现实验口径：保留 `bullish/bearish` 事件，按 `published_timestamp` floor 到分钟，对齐 `BTCUSDT 1m`，计算 next `1/3/5/15/30/60m` signed return。

## 7. 来源
- Binance. *ai-trading-prototype-backtester*. GitHub.
- Repo URL: `https://github.com/binance/ai-trading-prototype-backtester`
- Readable files: `README.md`, `aitradingprototypebacktester/strategy_manager.py`, `aitradingprototypebacktester/strategy/successive_strategy.py`, `sentiment_data/sentiment_data.csv`
- Public market data: `https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1m/`
- Local artifacts:
  - `reports/artifacts/quant_digests/2026-04-18_news_sentiment_events.csv`
  - `reports/artifacts/quant_digests/2026-04-18_news_sentiment_summary.csv`
