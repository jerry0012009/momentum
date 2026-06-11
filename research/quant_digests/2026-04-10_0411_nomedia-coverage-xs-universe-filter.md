# 别把这篇 media-coverage working paper 只读成“注意力故事”：对 short-cycle desk，更该先把它当作「no-coverage weekly universe gate × XS sleeves」
- 时间：2026-04-10 04:11 UTC
- 类型：2025 working paper（EFMA 2025 conference PDF）
- 主题类型：filter
- 基础 alpha：cross-sectional under-attention drift（无媒体覆盖币种后续收益更强）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：media-coverage / investor-attention / cross-sectional / relative-value / universe-selection / weekly-gate / momentum / reversal / public-data
- 证据类型：论文证据

## 1. 这次看了什么
Ba Chu（2025-01-11）的 working paper **Media Coverage and the Cross-section of Cryptocurrency Returns**。它不是讲“新闻情绪”，而是更朴素的一件事：**一周里完全没被主流媒体提到的币，下一周往往比高曝光币更能涨**。

## 2. 核心结论
- 论文按周把币分成 `no coverage / low coverage / high coverage` 三组；下一周等权收益约为 `4.08% / 2.25% / 1.46%`。
- 做 `long no-coverage, short high-coverage` 的 long-short，平均约 `2.61%/周`，`t≈3.90`；但**真正更稳的是 long-only no-coverage**。
- 扣交易成本后，`no-coverage` long-only 仍约 `3.15%/周`（`t≈2.96`）；而高曝光组净收益转负。原因很直接：`no-coverage` 组周换手约 `19.67%`，高曝光组约 `79.27%`，对应单边成本约 `93bps` vs `373bps`。
- 这个效应最集中在**小市值、高非流动性、高特异波动、低 beta、且过去一周涨得多**的币上。换句话说，**“涨过、但还没被媒体追着写”的币，后面更容易继续漂移**。

## 3. 为什么和当前项目有关
这篇东西对我们更像 **shared universe gate**，不是逐根 `5m/15m` 主信号。它最适合服务两类现有/未来 raw alpha：
- `cross-sectional momentum / leader continuation`：优先在“最近已强、但 media 还没跟上”的名字里做多；
- `XS reversal / loser-bounce`：少碰已经被媒体过度覆盖、交易拥挤且成本高的名字。

更直白地说：它回答的不是“这根 K 线买不买”，而是**“哪些币值得让你的短周期 alpha 去交易”**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：无媒体覆盖带来的 under-attention drift
- regime：周频更新；小盘、低流动性、高 idio-vol、高过去收益子样本更强
- filter / veto：剔除高覆盖、拥挤、成本高的名字；优先 no-coverage / low-coverage 桶
- risk / sizing / execution overlay：把它当周频 universe mask；单名额外加 ADV/cost cap，short 腿默认弱化或先不做

## 4. 可复刻的最小实验
- 研究假设：**周频 media under-attention gate 能提升短周期 XS 策略的成本后收益。**
- 数据源、公开性、更新频率：
  - `Common Crawl News Dataset`：公开可取，按周聚合新闻提及次数；
  - `CoinMarketCap` 或可替代公开币种清单/市值数据：公开可得；
  - 交易数据用 Binance/Bybit 公共 `15m` 或 `5m` K 线。
- 最小口径：每周末先按过去 `7d` 新闻篇数把币分成 `no / low / high coverage`；再在 liquid universe 内，只对 `no-coverage` 桶运行一个现成 XS sleeve（如 `24h winner long` 或 `24h loser-bounce long`），与“全市场直接跑同一 sleeve”做 A/B。
- 先看指标：`post-cost return`、`positive asset ratio`；辅看 `turnover / 名单稳定度`。

## 5. 风险与保留意见
- 这是**周频 universe 过滤器**，不是 bar-level timing alpha，别硬伪装成 `5m` 主信号。
- Common Crawl 的币名匹配、ticker 歧义、同名噪声需要先做 alias 清洗。
- 效应最强的地方往往也是容量最差、冲击成本最高的地方，所以 desk 里更适合先做 **long-only small sleeve / 权重上限约束**。
- 论文样本的交易环境与今天的 perp 生态不完全一致，真正上线前要先做“coverage gate × 现有短周期 alpha”联测，而不是单看论文周收益。

## 6. 来源
- Chu, B. (2025). *Media Coverage and the Cross-section of Cryptocurrency Returns*. Working paper / EFMA Annual Meetings 2025.
- DOI：暂无
- Readable URL：`https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2025-Greece/papers/crypto_news_v4.pdf`
- 数据说明（文中）：`Common Crawl News Dataset` + `CoinMarketCap` 周频面板
