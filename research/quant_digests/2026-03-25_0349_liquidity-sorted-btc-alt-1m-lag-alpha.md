# 别把 BTC→ALT lead-lag 继续只写成“大冲击篮子事件”：这篇 2026 论文更该先测的是「trade-count 分层的 1m 滞后跟随」完整 raw alpha
- 时间：2026-03-25 03:49 UTC
- 类型：2026 论文（全文 PDF）+ Binance 公共数据口径
- 主题类型：raw alpha
- 基础 alpha：BTC 的 `1m` 收益会领先一批低 trade-count alt 的短时价格反应；低流动性币对 BTC 冲击的吸收更慢，可做 `BTC lead -> ALT delayed follow-through` 的逐分滞后交易
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/lead-lag/btc/altcoin/liquidity/trade-count/1m/high-frequency/machine-learning/entry-exit/cost/binance/crypto
- 证据类型：论文证据

## 1. 这次看了什么
主看 **Kurihara & Matsumoto (2026)** 的 *Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy*。它和我们昨天那条 `BTC 5m shock -> alt basket` 不是同一件事：昨天更像**事件阈值 + 篮子交易**，这篇更值钱的是把同一家族拆成了一个更细、也更容易工程化的版本——**按 trade count 先筛 follower，再做 `1m` 级 BTC→ALT 连续滞后跟随**。

## 2. 核心结论
- **一句话核心结论：** 这篇东西最值得先偷的，不是“BTC 会影响 alt”这句废话，而是 **“低 trade-count alt 对 BTC 的反应确实更慢，所以 follower 应该按 liquidity 排，不该把所有 alt 混成一个篮子”**。
- **一句话怎么证明：** 作者用 Binance `1m` 数据，对 Bull/Bear 两段事件期分别做 cross-correlation、ISI 指标、Granger causality、VAR / IRF，再把结论直接写成带 fee 的 out-of-sample lag strategy。
- 他们定义的 **Immediate Sensitivity Indicator (ISI)** 与对数 trade count 呈显著正相关：Bull 期相关系数 **0.561**、Bear 期 **0.483**，两边都是 **p < 1e-16**。翻成人话：越不活跃的币，越容易慢半拍。
- Granger 因果检验里，`BTC(t-1) -> ALT(t)` 对全部样本币都显著；小币上的 F-stat 非常大，比如 Bull 期 **QKC 706.5、GNO 2109.4、BIFI 1334.3**，而反向 `ALT -> BTC` 大多不显著。
- 论文不是只停在解释层，而是给了完整交易骨架：特征只用 `BTC(t-1)` 和 `ALT(t-1)` 收益，双模型分别判断 **entry / hold**，手续费按 **0.02%** 计入，阈值搜索后得到 **entry≈0 或 1bp、hold=-1bp** 的“易进难出”结构。
- 在附录给出的额外样本里，lag strategy 对几只小币明显赢过 buy-and-hold：Bear 子样本 **QKC 116% vs -9%**, **BIFI 96% vs -6%**, **PIVX 69% vs -12%**；但 ETH/LTC 没占到便宜，说明 edge 更像**低流动性 follower edge**，不是“所有主流币都能跟”。

## 3. 为什么和当前项目有关
- 这条线仍然是 **raw alpha 本体**，不是 filter；而且它把我们最近已积累的 `BTC lead-lag` 家族继续拆细成了一个更可执行的子方向：**先做 follower ranking，再做 entry/exit**。
- 对当前 desk 更有价值的地方在于：它告诉我们 **asset selection 本身就是 alpha 的一部分**。不是先有 trigger、再随手挑几只 alt，而是要先用 trade count / responsiveness 去挑“谁会慢半拍”。
- 它也适合作为我们现有 `5m shock` 事件框架的补件：事件版回答“什么时候开机”，这篇回答“开机后优先打哪些 follower、持多久”。

## 3.5 策略拆解（必填）
- 方向属性：cross-market / leader-laggard / intraday momentum
- 基础 alpha：BTC 先动，低 trade-count alt 在后 1~3 个 `1m` bar 才把信息补进去
- regime：论文在 Bull / Bear / Sideways / Crash 都做了分段验证；主 edge 更集中在小币、尤其是 Bull/Bear 下的滞后吸收
- filter / veto：先按 `20d` 或 `30d` median trade count 做 follower 分层，只在慢反应分组开机；超大冲击和极差流动性币要单独限流
- risk / sizing / execution overlay：论文是 binary hold/not-hold，实盘里更适合改成等风险或按 `BTC impulse × follower liquidity score` 缩放；统一 next-bar 执行并强制计入 2~6 bps round-trip 成本

## 4. 可复刻的最小实验
- **研究假设：** Binance 上较低 `1m trade count` 的 alt perp，会对 `BTCUSDT` 的 `1m` 方向冲击出现更高的 next-bar 跟随概率。
- **可计算定义：** 先用 `1m kline` 自带的 `number of trades` 做流动性代理；对每个币计算最近 `20d` 的 `ISI = corr_0 - mean(corr_-1..-5)` 或更简单的 `lag1 corr - lag0 corr` proxy，然后只交易最慢的 bottom tercile followers。
- **最小回测切口：** `BTCUSDT` + 20~40 个 Binance USDT perp，频率先做 `1m` 生成信号、`3m/5m` 汇总评估；样本先跑最近 `6~12` 个月。
- **最该先看 2 个指标：** 1) `post-cost avg return / trade` 是否在 2~6 bps 成本下仍为正；2) edge 是否明显集中在低 trade-count 分组，而不是全市场平均都有。
- **第一版别急着上 LightGBM：** 先做最朴素规则版——`BTC 1m return` 超分位、ALT 当根未充分同步、next bar 开仓、持有 `1~3` 分钟——先验证“慢半拍 follower 是否存在”，再决定要不要上双分类器。

## 5. 风险与保留意见
- 论文的强 edge 主要落在 **很小、很慢的 alt**；对我们 desk 真正可交易的中高流动性 perp，边际可能会小很多。
- 它用的是 Binance 现货/USDT 交易对口径；映射到 perp 后，资金费率、做市结构和 taker 成本都会改写结果。
- 论文的 sizing 很轻，更多是“是否持有”而非完整仓位优化；所以我们能复用的是 **signal skeleton**，不是直接照搬仓位管理。
- 若把 edge 建立在极低流动性币上，真实冲击成本可能远高于文中 `2bp/side` 设定，容易出现“统计显著、交易不显著”。

## 6. 来源
1. **Kurihara, T., & Matsumoto, T. (2026). _Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy_. Asia-Pacific Financial Markets.**  
   - DOI: `10.1007/s10690-026-09589-z`  
   - Readable URL: `https://link.springer.com/article/10.1007/s10690-026-09589-z`  
   - PDF URL: `https://link.springer.com/content/pdf/10.1007/s10690-026-09589-z.pdf`  
   - Repo URL: `N/A`
2. **Binance Developers. _Market Data API / Kline-Candlestick Data_.**  
   - DOI: `N/A`  
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`  
   - Repo URL: `N/A`
