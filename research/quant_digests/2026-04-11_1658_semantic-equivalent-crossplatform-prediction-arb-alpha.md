# 别把这篇 2026 prediction-market 论文只读成“语义匹配数据集”：对 short-cycle desk，更该先测的是「semantic-equivalent cross-platform parity gap × hold-to-resolution」这条 raw alpha

- 时间：2026-04-11 16:58 UTC
- 类型：2026 arXiv 全文 HTML + arXiv API 元数据 + Polymarket / Kalshi public API live availability probe
- 主题标签：raw-alpha/prediction-market/relative-value/stat-arb/cross-platform/semantic-alignment/law-of-one-price/conditional-arbitrage/negative-risk/subset/polymarket/kalshi/1m/3m/5m/15m/paper/public-data/cost/risk
- 证据类型：paper full-text + live public-data probe

- 主题类型：raw alpha
- 基础 alpha：**对“语义上等价”的跨平台 prediction market，做 `买便宜 YES + 买另一边便宜 NO` 的条件套利；当执行后 bundle 成本在费用后仍显著低于 `1.00` 时，持有到 resolution 或 recross。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 先回答一句：这篇东西的 base alpha 是什么？
这轮 **base alpha 很清楚**，不是“prediction market 生态很碎”，也不是“LLM 能做语义匹配”。

真正能进 desk 素材池的，是一条很直接的 **cross-platform relative-value / stat-arb raw alpha**：

> **如果两个平台上写法不同、但结算语义等价的市场，其 `YES@A + NO@B` 或 `YES@B + NO@A` 这组 bundle，在扣掉 bid-ask / fee / gas / slippage 后仍明显低于 `1.00`，那就是一笔可以锁到 resolution 的条件套利。**

翻成人话：
**不是赌事件方向，而是赌“同一件事不该在两个平台上长期报出不同概率”。**

所以它不是：
- 宏观解释；
- 外部情绪 filter；
- 单平台 maker / taker execution shell；
- 也不是上一篇那类固定 strike / same-hour market mismatch 的特例。

它本身就是一条可以单独建簿、单独记账、单独做风控的 **raw alpha**。

---

## 为什么这轮值得写，而不是把它当成“又一篇 prediction-market 综述”
原因有 5 个：

1. **它是完整 raw alpha，不是解释型题目。**  
   entry、cost、持有逻辑、收益兑现方式都能写清楚。

2. **它和已经写过的 prediction-market digest 不重复。**  
   之前更多是：
   - 同平台 strike surface / pair-sum / term structure；
   - 单平台 favorite-side momentum；
   - 明确同小时合约的跨平台对照。  
   这篇更底层：**先解决“哪些市场其实是同一件事”**，再做跨平台套利。

3. **它不是只能服务 prediction market。**  
   这套“语义等价 -> 价差监控 -> bundle parity”框架，本质上是一个 **event-driven RV scanner**，以后也能迁移到：
   - 同一宏观事件的多数据源合约；
   - 不同 venue 的事件期权 / binary markets；
   - 甚至 crypto 自身的跨 venue list duplication / semantic event contracts。

4. **公开数据入口够直接。**  
   Polymarket Gamma API、Kalshi public trade API 都能直接抓到 live event / market metadata，第一轮最小实验不需要私有库。

5. **论文给了非常硬的经济量级。**  
   不是“可能存在错价”，而是直接报告：**高流动性场景下中位 execution-aware 偏离仍有 `2%~4%`，朴素策略 800 天 `15` 笔交易累计收益 `1218.66%`。**

---

## 主要来源

### 1) 主来源论文
- **Authors / Year**: Jonas Gebele, Florian Matthes / 2026
- **Title**: *Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets*
- **Venue**: arXiv preprint (`cs.CE`)
- **DOI**: `10.48550/arXiv.2601.01706`
- **Readable URL**: <https://arxiv.org/abs/2601.01706>
- **HTML Full Text**: <https://arxiv.org/html/2601.01706v1>
- **Repo URL**: 无公开 repo（论文写明 aligned dataset 计划在发表后公开）

### 2) live public-data probe
- **Artifact JSON**: `/root/clawd/jerry/momentum/reports/artifacts/literature/prediction_market_semantic_alignment_probe_2026-04-11.json`
- **Artifact CSV**: `/root/clawd/jerry/momentum/reports/artifacts/literature/prediction_market_semantic_alignment_probe_2026-04-11.csv`
- **Polymarket API**:
  - events: <https://gamma-api.polymarket.com/events?limit=2&closed=false>
  - markets: <https://gamma-api.polymarket.com/markets?limit=2&closed=false>
- **Kalshi API**:
  - events: <https://api.elections.kalshi.com/trade-api/v2/events?limit=2>
  - markets: <https://api.elections.kalshi.com/trade-api/v2/markets?limit=2>

---

## 这篇论文真正给了什么

## 1) 它先把“同一事件”的定义从人脑判断，变成可系统扫描的对象
论文不是简单说“Polymarket 和 Kalshi 有时不一样”，而是先把跨平台 market relation 分成三类：

1. **equivalent**：两个市场 YES-region 完全相同；
2. **subset**：一个市场的 YES 条件严格包含另一个；
3. **negative-risk partition**：多个二元市场跨平台拼起来，能覆盖完整 mutually-exclusive outcome set。

对交易最重要的不是这个分类本身，而是：

> **一旦 relation 被确定，就能写出明确 bundle，去问“这组东西是不是买得太便宜了”。**

也就是把“语义问题”直接变成 **可交易的 parity 问题**。

---

## 2) 这条 alpha 的交易语句其实非常短
对 **equivalent pair**，论文给的核心 no-arbitrage 条件是：

> `1 - Δ <= min( YES_A + NO_B , YES_B + NO_A ) <= 1 + Δ`

其中 `Δ` 是两边执行成本之和。

如果：

- `YES_A + NO_B + cost < 1`

那你就：

- 在 A 买 YES
- 在 B 买 NO
- 持有到 resolution

到期必有一边兑付 `1`，另一边归零；
只要入场总成本小于 `1`，就是锁利润。

翻成人话：
**不是猜谁赢，而是凑出一张“无论谁赢都值 1 块钱”的组合，但你现在只花了不到 1 块。**

这就是它的 raw alpha 本体。

---

## 3) 论文最值钱的地方，是它证明这不是极偶然的尖刺
论文覆盖 **2018~2025、10 个 major prediction-market venues、102,275 个 events**，然后给出几组非常硬的数据：

### 3.1 semantic overlap 不是零星噪音
- **约 `6%` 的 event** 至少和另一个平台存在一条 semantic relation；
- 这些 event 虽然数量占比不高，但贡献了 **接近 `10%` 的 total event-days**；
- 也就是说，真正跨平台重复挂牌的，往往是 **持续时间更长、关注度更高** 的大事件。

对 desk 的意义：
**不是所有 event 都值得扫，但值得扫的那部分，往往恰好是更液、更久、更能容纳资金的那部分。**

### 3.2 它不是只有一种套利，而是三层结构
论文识别出：
- **`1,501` 个 equivalence classes / `6,709` 条 equivalence relations**
- **`1,645` 组 subset-related sets / `6,421` 条 subset relations**
- **`1,123` 个 negative-risk constructions / `2,771` 个 markets**

这很重要，因为它说明这不是单一“Kalshi vs Polymarket 同一题”的小花样，
而是一个 **完整 family**：
- exact-equivalent RV
- superset/subset coverage arb
- 多 outcome cross-platform partition arb

可以先从 exact-equivalent 做第一阶段，再逐步扩到 subset / partition。

### 3.3 真正最该记住的量级：**中位 execution-aware 偏离 `2%~4%`**
论文在结果部分明确写到：

> **即使在最 liquid 的 constructions 里，价格通常仍会离 execution-adjusted parity `2%~4%`。**

这不是“偶尔跳一下”。
而是说明：

> **就算你已经把 fees / spreads / execution frictions 算进去，很多语义等价 market 依然没被拉平。**

对交易含义很直接：
**这条 alpha 不是必须做极速撮合的纯 HFT 级别，更多像是 structural dislocation book。**

### 3.4 论文还给了一个非常硬的 sanity check：朴素策略也不差
作者做了一个非常保守的 mechanical simulation：
- 每次只拿 **当时最高收益的 1 笔 equivalent-market arbitrage**；
- 不做复杂 timing，也不滚动切换；
- 开仓后一直持有到 resolution；
- 扣掉 execution frictions。

结果：
- **`800` 天**
- **`15` 笔 completed trades**
- **累计收益 `1218.66%`**

这不代表可以直接照搬上线，
但至少说明：
**paper 里的 edge 不只是统计显著，而是有真钱簿记含义。**

---

## 为什么我把它归类成 raw alpha，而不是 filter / overlay
因为它的交易闭环本身已经成立：

- **交易对象**：语义等价 / 子集可覆盖的跨平台 prediction-market contracts
- **方向**：买便宜 bundle（`YES_A + NO_B` 或 `YES_B + NO_A`）
- **触发**：execution-aware bundle cost 显著低于 `1`
- **退出**：持有到 resolution，或在 recross 时提前平掉
- **仓位**：每个 event 固定 notional / maturity-bucket cap / venue cap
- **风控**：resolution-semantics 白名单、时间窗限制、平台信用与提款风险限制
- **成本**：bid/ask + fees + gas + transfer friction

这已经不是“给别的 alpha 加一层 gate”，
而是一条可以自己独立成书的 **relative-value raw alpha**。

---

## live public-data probe：这条线现在就有公开入口，不是论文里空中楼阁
本轮我没去伪装成“已经拿到 paper 原始对齐数据”，而是先做了一轮 **公开接口最小可复现实验口径检查**。

### 1) 两边公开 API 都可直连
probe 结果里，四个入口都返回 `200`：
- Polymarket events
- Polymarket markets
- Kalshi events
- Kalshi markets

这意味着第一轮最小系统完全可以不依赖私有权限，先做：
- event universe 拉取
- title / resolution text / endDate 对齐
- 市场清单刷新
- 顶层 parity monitor

### 2) 当前 live co-listed family 不难找到
probe CSV 里最明显的几组当前 family：

1. **Democratic Presidential Nominee 2028**
   - Polymarket slug: `democratic-presidential-nominee-2028`
   - Kalshi event ticker: `KXPRESNOMD-28`
   - token overlap / jaccard: `2028 democratic nominee presidential` / `1.0`

2. **Presidential Election Winner 2028**
   - Polymarket slug: `presidential-election-winner-2028`
   - Kalshi event ticker: `KXPRESPERSON-28`
   - jaccard: `1.0`

3. **Republican Presidential Nominee 2028**
   - Polymarket slug: `republican-presidential-nominee-2028`
   - Kalshi event ticker: `KXPRESNOMR-28`
   - jaccard: `1.0`

这说明：
**语义重复不是历史资料里才有，当前 live universe 里就能捞到。**

### 3) Polymarket 一侧的 live liquidity 已经很够研究
例如 `Democratic Presidential Nominee 2028` 这个 live family：
- event liquidity 约 **`46.37M`**
- 24h volume 约 **`6.15M`**

其内部单候选 market（本轮抓到的 sample）例如：
- **Gavin Newsom**：`last 0.275 / bid 0.274 / ask 0.275`
- **AOC**：`last 0.088 / bid 0.087 / ask 0.089`
- **Jon Stewart**：`last 0.022 / bid 0.021 / ask 0.023`

这至少说明两件事：
1. live family 在；
2. 单腿 price grid / spread / top-of-book 都能拿到。

Kalshi 这次公开 market list 能拿到 event/market identifiers，但 sample quote 字段没稳定返回；
所以第一轮工程上更现实的做法不是假装“一步到位跨平台实盘”，而是：

> **先用公开 event universe + Polymarket side 全量 quote 做 semantic-matching scanner，Kalshi 作为第二腿的 market-availability & contract-definition source，再补 quote 采集器。**

也就是说：
**数据口是通的，只是 quote completeness 需要第二步单独补。**

---

## 它和我们已经写过的 prediction-market alpha 到底差在哪
这轮必须明确说清楚，不然容易看起来像重复：

### 已有 digest 更像这些方向
- same-event strike mismatch
- pair-sum / complementary-outcome parity
- term-structure mispricing
- favorite-side momentum / VWAP continuation
- 同平台 surface fitting

### 这轮新补的是更底层的一层
> **先解决“两个平台上哪两个市场其实是同一件事”，再去做 parity / subset / negative-risk。**

所以它不是已有策略的一个小调参，
而是一个 **上游 alpha factory**：
- 给 exact-equivalent arb 提供 pairs
- 给 subset arb 提供 superset/subset relation
- 给 negative-risk 提供 partition candidates

它甚至可以反过来给我们现有的 prediction-market research pipeline 做候选生成器。

---

## 这条 alpha 对 `1m / 3m / 5m / 15m` 怎么映射
这里要说老实话：

**它不是那种“下一根 5m K 线涨跌”的 directional alpha。**

它更像：
- **信号刷新频率** 在 `1m / 3m / 5m / 15m`
- **持仓期限** 则由 event resolution 或 recross 决定

也就是说，`1m/3m/5m/15m` 在这里代表的是：

### `1m`
适合：
- 大事件 family
- 高流动性 nomination / election books
- 需要更快发现 parity gap 扩大的场景

### `3m / 5m`
适合：
- 默认监控频率
- 足够压噪声，又不会把 structural gap 看丢
- 我觉得是第一轮最合理的 default

### `15m`
适合：
- 长 dated、低交易活跃度 event family
- 只做慢刷新、低维护负担的 watchlist

翻成人话：
**这条 alpha 的“短周期”不是 holding horizon，而是 monitor horizon。**

---

## 最小实验应该怎么做
这轮最重要的不是再写一遍论文摘要，而是把第一轮实验口径钉死。

## 实验 A：exact-equivalent bundle scanner（最优先）
### 数据源
- Polymarket Gamma events / markets（公开）
- Kalshi trade-api events / markets（公开）
- 必要时加 Polymarket CLOB / websocket 刷新 top-of-book

### 步骤
1. 拉 active event universe；
2. 用 `title + endDate + resolution text + category` 做第一层粗匹配；
3. 人工先只保留 20~50 个高置信 family；
4. 对每个候选 family，落到具体 YES/NO market；
5. 计算：
   - `bundle1 = yes_A_ask + no_B_ask + fees`
   - `bundle2 = yes_B_ask + no_A_ask + fees`
6. 若 `min(bundle1, bundle2) <= 1 - h`，记为 executable candidate。

### 建议频率
- default：`5m`
- 高流动大事件：加 `1m`

### 先看的指标
- 每个 family 的 executable fraction
- gap persistence（持续几根采样）
- fee 后净 edge 分布
- 距 resolution 的剩余时间 bucket

---

## 实验 B：subset-arb（第二优先）
例子就是论文里那种：
- superset：`共和党赢 2028 大选？`
- subset：`JD Vance 赢 2028 大选？`

如果：
- `YES(superset) + NO(subset) + fees < 1`

那就是 deterministic coverage。

这条线的好处是：
**不要求两个市场一模一样，只要逻辑包含关系清楚就能做。**

但它更容易踩 resolution 细节坑，
所以应该排在 exact-equivalent 之后。

---

## 实验 C：negative-risk cross-platform partition（第三优先）
比如同一个多 outcome 事件：
- 平台 A 给了主要候选人
- 平台 B 给了“其他”或 party bucket

把它们拼成完整 partition，检查：
- `sum(YES_i + fees_i) < 1`

这条线利润最“像白送钱”，
但工程复杂度也最高，
因为你要确保：
- mutually exclusive
- collectively exhaustive
- 结算口径完全对齐

所以第三步再做，不适合当第一枪。

---

## 直接落地时最该防的 6 个坑
1. **resolution source 看起来像一回事，其实不是。**  
   论文里专门举了 weather station 的例子：文本像一样，但观测源不同，最后不是同一 claim。

2. **cutoff time 差一点点，也可能不是同一个 market。**  
   尤其 election / macro / sports 的“官方确认”定义可能不同。

3. **mid-price 可见，不代表 executable。**  
   一定要用 best ask / best available bundle，而不是看中间价自嗨。

4. **长 dated event 的 capital lockup 很贵。**  
   paper 里高 APY 往往和剩余期限短有关；别被名义 APY 迷惑。

5. **平台信用 / 提现 / 合规分割是真风险。**  
   这类策略不是纯 price series backtest，账户层 friction 是真实 alpha tax。

6. **semantic matcher 不能只靠标题字符串。**  
   标题是候选生成器，不是最终真相；resolution rule 必须入白名单。

---

## 我对这条线的判断
### 为什么值得进池
因为它满足当前优先级里最稀缺的一类：

- **raw alpha**
- **relative-value / stat-arb**
- **可独立复现**
- **能直接写成完整策略壳**
- **公开数据入口可拿**

### 为什么它又还没到“直接上实盘”
因为还缺 3 个东西：
1. live quote completeness（至少第二腿要补稳定 top-of-book）
2. resolution-rule whitelist
3. capital / transfer / jurisdiction 风险建模

所以我的结论不是“现在就能一键跑”，而是：

> **它已经够格作为完整 raw alpha 候选进入第一梯队，但应先做 exact-equivalent scanner + executable bundle replay，不要一上来就做全自动跨平台真仓。**

---

## 下一步怎么测（最小可执行版本）
### 第一步：先只做一个 family 白名单
从本轮 probe 里先挑：
- `Democratic Presidential Nominee 2028`
- `Republican Presidential Nominee 2028`
- `Presidential Election Winner 2028`

只做这 3 组 family，别一口气全生态扫描。

### 第二步：只做 exact-equivalent，不碰 subset / partition
因为：
- 语义最清楚
- 最容易做人工验真
- 最容易先回答“有没有真钱 edge”

### 第三步：采样频率先用 `5m`，高流动事件再加 `1m`
记录：
- best executable bundle cost
- edge persistence
- event remaining time
- family volume / liquidity bucket

### 第四步：先回放，不先下单
第一轮 output 应该是：
- family-level gap 分布
- 扣费后 still-positive 的次数 / 占比
- 事件到期前不同时间 bucket 的 edge 稳定性
- 如果按“gap > 2 ticks 且连续 2 个采样仍在”入场，resolution PnL 会怎样

如果这一步结果还像论文里的 `2%~4%` persistent divergence，
再升级到第二轮：
- subset arb
- negative-risk partition
- 更完整的 quote collector

---

## 一句话结论
这篇 2026 论文最值得 desk 先拿走的，不是“semantic alignment framework”这几个字，
而是它背后那条很硬的 **cross-platform conditional-arbitrage raw alpha**：

> **把语义上等价的 prediction markets 凑成一个必值 `1.00` 的 bundle，只要当前买入成本在费用后仍明显低于 `1.00`，这就是一笔可独立建簿、可持有到 resolution 的 structural RV trade。**

对我们现在的素材池来说，这条线值钱的地方在于：
**它不是又一个单平台形态，而是一个可以持续生成新 pairs / subset / partition 候选的上游引擎。**

---

## 参考链接
1. **Gebele, J., & Matthes, F. (2026). _Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets_. arXiv.**  
   - DOI: <https://doi.org/10.48550/arXiv.2601.01706>  
   - Readable URL: <https://arxiv.org/abs/2601.01706>  
   - HTML: <https://arxiv.org/html/2601.01706v1>

2. **Polymarket Gamma API（public）**  
   - Events: <https://gamma-api.polymarket.com/events?limit=2&closed=false>  
   - Markets: <https://gamma-api.polymarket.com/markets?limit=2&closed=false>

3. **Kalshi Trade API（public）**  
   - Events: <https://api.elections.kalshi.com/trade-api/v2/events?limit=2>  
   - Markets: <https://api.elections.kalshi.com/trade-api/v2/markets?limit=2>
