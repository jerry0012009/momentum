# 别把 crypto 新闻情绪硬写成逐根 15m 主信号：`BTC-news shock blackout / cross-asset veto` 更像 breakout-short / Fib / EMA-PSAR 的 shared overlay
- 时间：2026-03-22 21:58 UTC
- 类型：近 5 年论文 + 公开数据映射方案
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/news-sentiment/btc/eth/cross-asset/event-risk/filter/risk-overlay/paper/crypto/5m/15m
- 证据类型：论文证据

## 1. 这次看了什么
这轮主看 **Christian Kreuzer, Christian Sparrer, Gregor Dorfleitner (2026)** 的论文 **_Beyond pure hype: news sentiment and its role in the BTC and ETH futures market_**。它最值得我们 desk 借的，不是“做一条新闻情绪因子去猜下一根 15m”，而是更窄的一刀：**把 BTC 相关新闻冲击当成一段短时信息事件窗，用来给现有 15m continuation / retest / breakout 做 `blackout / veto / size-down`。**

## 2. 核心结论
- **一句话核心结论：** crypto 新闻情绪更像 `event-risk overlay`，不是逐根 15m 主信号；尤其 **BTC 新闻会外溢到 ETH futures**，所以更适合做 cross-asset 风险层。  
- **一句话证明方式：** 作者用 **9100+ BTC 新闻、5400+ ETH 新闻**，构建 crypto-specific sentiment，并把它和 **BTC/ETH futures returns + COT 持仓**做回归，检验 contemporaneous impact、lagged reversal 与 cross-asset spillover。  
- 关键数据点 1：论文样本里，**一倍标准差的 BTC crypto-specific sentiment 上升，对应 BTC futures 当日回报约 `+0.46%`**。  
- 关键数据点 2：**BTC 主要是负面新闻更有价格效应**；ETH 则更像 **正面 ETH 新闻**带动回报。  
- 关键数据点 3：作者额外发现 **BTC news sentiment 对 ETH futures 也有显著影响**，说明这不是“各自看各自新闻”的孤立市场。  

> 人话：新闻冲击当然有信息，但把它硬塞进“这根 15m 多/空”很容易假精确；更诚实的做法是：**当 BTC 新闻刚砸进来时，先把现有 setup 的 follow-up 资格和仓位收紧。**

## 3. 为什么和当前三条收口线直接相关
这题比继续泛找更值得，因为它补的是当前三条线还缺的一块：**crypto-native、非日历型、公开可拉取的事件风险层**。

- **V3 final-verdict / breakout-short follow-up**：新闻冲击后最容易出现的不是“立刻顺滑延续”，而是高波动 + 假跟随；对 breakout-short 更像 `event blackout / delayed confirmation`。  
- **Fibonacci confirmation / retest_hold**：回踩 hold 最怕消息驱动的二次扫穿；新闻窗可先做 `retest_hold veto`，避免把 headline shock 误认成结构回踩。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 原始触发常死在事件噪声里；新闻 overlay 的价值不是替代 trigger，而是让 raw alpha 少在“信息刚进场但路径未稳定”的阶段硬上。  

另外，最近我们已经有 **宏观日程 blackout**、**Fear & Greed extremity**、**funding / OI / basis** 这类 overlay；但这些不是 crypto 原生新闻流。**这篇论文补的正是“加密资产自己发生了什么”这一层。**

## 4. 可复刻的最小实验
- **研究假设**：BTC 新闻冲击后的 `30~90 分钟` 是 15m continuation / retest 的高噪声窗，直接做 `blackout / size-down / stricter-confirm` 会比 baseline 更诚实。  
- **公开数据源**：  
  1. **GDELT DOC 2.0 API**（公开、免 key 可直接 HTTP 查询；新闻库近实时更新，站点说明其公开数据历史会持续滚动更新，主站数据每 `15 分钟`更新）；  
  2. Binance 5m / 15m perp klines（公开 REST）；  
  3. 第一版只抓 `bitcoin OR btc` 相关新闻，不必一上来做多币种 NLP。  
- **最小口径**：  
  1. 每 15 分钟拉一次 GDELT，统计最近 `30m` 的 `BTC article count`、`avg tone`、`negative-share`；  
  2. 定义 `btc_news_shock = article_count_z >= 2` 或 `negative_article_count >= N`；  
  3. 对现有三条线做 A/B：`baseline` vs `news_blackout_2bar` vs `news_size_down_0.5x` vs `news_need_extra_confirm`；  
  4. 先只看 `BTC/ETH/SOL`、15m、最近 `60~120 天`。  
- **最该先看的指标**：  
  - `post_cost_expectancy`  
  - `false_follow_ratio`（入场后 2~4 bar 反向）  
  - 辅助看 `trade_retention`，防止只是靠砍单美化。  

## 5. 下一步怎么测（必须动作）
先不要做复杂情绪模型，第一刀只测 **事件窗**：

1. **A：baseline** —— 不加新闻层；  
2. **B：blackout** —— 若最近 30m 出现 `btc_news_shock`，则未来 2 根 15m 不允许新开 continuation；  
3. **C：size-down** —— shock 窗内把 breakout-short / EMA / Fib 新仓统一降到 `0.5x`；  
4. **D：stricter-confirm** —— shock 窗内必须额外满足 `2-close persistence` 或 `same-clock RVOL confirm` 才放行。  

通过条件：若 B/C/D 中任一能在 OOS 下同时改善 `expectancy` 与 `false_follow_ratio`，且 `trade_retention >= 70%`，再考虑把它升成 shared overlay。

## 6. 风险与保留意见
- 论文是**日频 futures 回归**，不是直接替我们证明 15m 可交易阈值；我们借的是“新闻冲击是信息事件层”这个角色，不是照搬系数。  
- 新闻源选择会显著影响结果；第一版宁可简单透明，也别一上来做黑盒 NLP。  
- 新闻到价格的传导可能对 BTC 最强、对 ETH/SOL 次之，因此更适合先做 **BTC 事件驱动的 cross-asset veto**，而不是给每个币各建一套新闻模型。  
- 若事件窗过长，容易退化成机械砍单；所以必须汇报 `trade_retention`。  

## 7. 来源
1. **Kreuzer, C., Sparrer, C., & Dorfleitner, G. (2026). _Beyond pure hype: news sentiment and its role in the BTC and ETH futures market_. Review of Derivatives Research.**  
   - Authors: Christian Kreuzer / Christian Sparrer / Gregor Dorfleitner  
   - Year: 2026  
   - Venue: Review of Derivatives Research  
   - DOI: `10.1007/s11147-025-09223-6`  
   - Readable URL: `https://link.springer.com/article/10.1007/s11147-025-09223-6`  
   - Repo URL: N/A

2. **The GDELT Project. _GDELT DOC 2.0 API Debuts!_**  
   - Authors / Org: The GDELT Project  
   - Year: 2017  
   - Title: GDELT DOC 2.0 API Debuts!  
   - Venue: GDELT Project Blog  
   - DOI: N/A  
   - Readable URL: `https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/`  
   - Repo URL: N/A

3. **The GDELT Project. _The GDELT Project_.**  
   - Authors / Org: The GDELT Project  
   - Year: 2026 access  
   - Title: The GDELT Project  
   - Venue: Official Website  
   - DOI: N/A  
   - Readable URL: `https://www.gdeltproject.org/`  
   - Repo URL: N/A
