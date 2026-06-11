# 别把宏观日历继续只当 blackout：这篇 2026 *Journal of Behavioral and Experimental Finance* 更该先测的是「scheduled-macro impulse × pre-event sentiment」事件驱动 raw alpha

- 时间：2026-04-05 23:18 UTC
- 类型：2026 *Journal of Behavioral and Experimental Finance* 论文摘要/元数据（OpenAlex + Crossref）+ Fed FOMC 官方日历/历史事件时间戳 + Alternative.me Fear & Greed + 既有公开行情快检产物再拼接
- 主题类型：raw alpha
- 基础 alpha：**scheduled macro announcement 触发的短时价格/成交冲击；pre-event crypto sentiment 不是方向本体，更像 admission / amplitude gate。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（当前更诚实的定位是“raw alpha + sentiment gate”的候选，还缺分事件类别的 sign/surprise router）
- 主题标签：raw-alpha/event-driven/macro-announcement/sentiment-gate/news-impulse/first-reaction/continuation/admission-filter/fomc/cpi/nfp/pce/fear-greed/btc/eth/1m/3m/5m/15m/paper/metadata/public-data/cost/risk
- 证据类型：论文摘要证据 + 官方事件时钟 + 公开 sentiment 数据 + 本地最小 portability split

## 1. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = `scheduled macro announcement -> immediate crypto impulse`，而 `pre-event crypto sentiment` 决定这段 impulse 是否更值得参与。**

翻成人话：
- 这篇东西不是单纯说“宏观会影响 crypto”；
- 它真正可交易的部分是：**宏观事件公布后的前几分钟/前一小时，本身就是一个 event-time alpha shell**；
- 而 sentiment 不是拿来硬猜涨跌方向的，更像决定“这次冲击有没有更大概率延续、值不值得开 event sleeve”。

所以我不把它降级成纯 overlay。更准确的定位是：
- **raw alpha 本体**：announcement-time impulse；
- **辅助 gate**：pre-event sentiment。

## 2. 这次看了什么

主材料是：

**Nhan Huynh (2026). _Tuning into the news: Sentiment-driven high-frequency movements in cryptocurrency markets_. Journal of Behavioral and Experimental Finance.**

这篇 paper 最有价值的，不是“情绪会影响市场”这种废话，而是它把一件更贴 desk 的事说明白了：

> **crypto 对 scheduled macro news 的反应，不是均匀常数；反应强度会被 crypto-specific investor sentiment 显著调节。**

这和我们现有研究池的关系很直接：
- 之前已经有 **FOMC / CPI blackout / veto** 这一类 overlay 读法；
- 但这篇 paper 给出的更有意思升级，不是“继续站远一点”，而是：
- **把 event-time 宏观冲击从纯风控时钟，升级成一条可以单独建壳的 event-driven raw alpha。**

也就是说，这轮不是再补一个“宏观别乱做”的 shared gate，而是在问：

> **什么时候应该从 blackout 走向 selective participation？**

## 3. 为什么这轮值得进研究池

如果只看当前 desk 的缺口，这轮继续补 raw alpha 当然仍然比再补一个泛 filter 更值钱。

这篇值得进池，原因是三条：

1. **它给的是“外生事件驱动 alpha 壳”，而不是又一条内生价格形态。**  
   我们这几天已经补了不少 momentum / pairs / funding / options RV；但真正来自 **公开外生时钟**、又能映射到 `1m/3m/5m/15m` 的 raw alpha 素材，还是偏少。

2. **它天然适合最小实验。**  
   不需要 proprietary feed；只要：
   - 官方宏观发布时间戳
   - 公共 minute bars
   - 一个公开 sentiment proxy
   就能先做 honesty check。

3. **它能补上“事件 alpha”和“事件 veto”之间的中间层。**  
   以前容易二选一：
   - 要么把宏观全当 blackout；
   - 要么硬猜方向。  
   这篇更合理的读法是：
   - **先等事件落地形成真实 impulse；**
   - **再用 sentiment 决定参与阈值和 size。**

## 4. 论文里最值得拿走的证据

基于 OpenAlex 可重建摘要，这篇 paper 明确给了几条对 desk 真有用的信息：

1. **样本不是单币小样本，而是 top 100 cryptocurrencies 的 high-frequency intraday data。**  
   这说明作者看的不是单一 BTC 特例，而是更广义的 crypto intraday reaction。

2. **returns 和 trading activity 对 U.S. macroeconomic announcements “sharply and immediately” 反应。**  
   也就是：alpha 的物理时间尺度不是日线/月线，而是**发布后立刻**的 event window。

3. **反应会随着 announcement category 不同而系统变化。**  
   这很重要，因为它意味着 desk 不该把 FOMC / CPI / NFP / PCE 混成一个总桶。

4. **sentiment 对市场反应有显著调节作用。**  
   也就是：同样是宏观事件，不同 pre-event sentiment state 下，crypto 的 reaction strength 不一样。

5. **稳健性不只是一套情绪指标。**  
   摘要明确说结果对：
   - alternative sentiment measures
   - subsample analyses
   - model specifications
   - 其他 major economies 的宏观公告  
   都保持稳健。

这几点合在一起，足够支持一句 desk 化结论：

> **宏观事件不是只能拿来停机；它也可以是一个独立 event-time alpha 壳，但必须加 sentiment / category gate。**

## 5. 对 short-cycle desk，最诚实的读法是什么？

**最不诚实的读法：**
- “FOMC 后就做多/做空 BTC”；
- “情绪高就追，情绪低就反手”；
- “这篇论文已经给了完整方向表”。

这些当前都没有证据。

**最诚实的读法：**
- 先承认 **announcement-time impulse** 是 alpha 本体；
- 再承认 **sentiment 主要管 amplitude / admission，不直接管 sign**；
- 最后把 entry 建在 **post-release first reaction** 上，而不是 event 前盲猜。

所以这篇 paper 对 desk 最值得先测的，不是：
- pre-event blind directional bet；

而是：
- **post-event impulse continuation shell × pre-event sentiment gate**。

## 6. desk 版策略骨架

## 6.1 第一版：announcement impulse continuation

### 适用品类
- `BTC / ETH` 先做
- 后面再扩到 top-liquidity alts

### 事件池
第一轮只做 **官方可精确对时** 的 scheduled macro events：
- FOMC statement
- CPI
- NFP
- PCE

### pre-event gate
先用公开且便宜的 proxy：
- `Alternative.me Fear & Greed`
- 或更细一点：news-sentiment / tweet-breadth / search-breadth（第二轮再补）

### 入场
不做 event 前猜方向。先等公布后第一段真实冲击：
1. 定义 `r0 = first 1m / 3m post-release return`
2. 定义 `vol0 = first bar volume shock`
3. 当满足：
   - `|r0| > rolling quantile threshold`
   - `vol0 > rolling p80/p90`
   - pre-event sentiment 落在 admission bucket
4. 才按 `sign(r0)` 顺势入场

也就是：
**方向由第一段真实冲击给，sentiment 决定这次冲击值不值得跟。**

### 出场
初版先用最老实的 time barrier：
- `1m`：持有 `3~10` 根
- `3m`：持有 `2~6` 根
- `5m`：持有 `1~4` 根
- `15m`：持有 `1~2` 根

再加两条简单保护：
- 若价格重新跌回/升回 event anchor VWAP 另一侧，提前出；
- 若下一根出现反向异常 bar，提前减半。

### sizing
- baseline `0.5x` 起步，不用满仓
- 只在 gate 最强 bucket 才升到 `1.0x`
- 单次 event sleeve notional cap：组合 `10%~15%`

### risk
- 事件前不持过大方向裸露，避免把 event-alpha 和 event-gap 风险混在一起
- 只允许一轮 re-entry，不做无限加码
- 若 spread / slippage / impact 超阈值，宁可 miss，不追第二脚

### cost
- 第一轮必须按 taker 成本记账
- 单独记录：
  - event 后第一分钟冲击成本
  - 追价延迟 1 bar 后的成本衰减
  - gross-to-net decay

## 6.2 第二版：sentiment 只做 admission，不做 sign

这篇 paper 当前最值得沿用的纪律是：

> **sentiment 像 amplitude filter，不像方向按钮。**

所以第二版别急着写：
- greed 做多；
- fear 做空。

更值得先测的是：
- **neutral**：只允许最强 `r0` 才入场；
- **greed / fear extreme**：降低 admission threshold，但不改方向；
- **极端冲突状态**（例如 sentiment 很热但第一反应是大阴线）：先降 size，不做强解释。

## 7. 我做的最小 portability check

为了避免只抄摘要，我拿现成公开路径做了一个最便宜的 desk 化拼接：

- **事件时钟**：Fed 官方 scheduled FOMC statement 时间戳
- **行情反应**：沿用已有 `BTCUSDT` FOMC 事件窗快检结果
- **情绪 proxy**：Alternative.me Fear & Greed 日值
- **样本**：`2024-01-31` 到 `2026-03-18` 的 **18 次 FOMC 事件**

说明一下：
- 这不是 full-paper replication；
- 只是验证一句：**pre-event sentiment 是否真的会改变 event reaction magnitude。**

### 结果（FOMC-only portability split，BTCUSDT 1h 事件窗）

1. **greed bucket（F&G 均值 `73.9`，n=`7`）的事件后 1h 平均绝对收益最高：`1.07%`**  
   对比：neutral `0.88%`，fear `0.75%`。

2. **greed bucket 的 post/pre absolute-return ratio 平均值约 `6.63x`**  
   对比：neutral `3.58x`，fear `2.70x`。  
   翻成人话：同样是 FOMC，pre-event sentiment 偏热时，release 后的波动扩张更猛。

3. **greed bucket 的 post/pre volume ratio 平均值约 `3.92x`**  
   对比：neutral `3.53x`，fear `2.00x`。  
   也就是说，情绪不只影响价格动幅，也影响事件后成交活跃度。

4. 若把 fear + greed 合成 `extreme`，则：
   - extreme：事件后 1h 平均绝对收益 `0.95%`
   - neutral：`0.88%`  
   差距不算巨大，但**反应强度至少没有比 neutral 更弱**。

这组快检不能回答方向，但它能支持一句更关键的话：

> **sentiment 足够当 event-time admission / sizing gate，而不必被伪装成方向本体。**

## 8. 为什么这轮仍然算 raw alpha，而不是纯 overlay？

因为这轮的核心不是“有没有事件风险”，而是：

- **事件后到底有没有一段值得交易的 alpha window？**

如果答案只是“有风险”，那它就是 overlay；
但这篇 paper 明确说：
- returns 与 trading activity 在公告后**立刻**反应；
- 且反应强度受 sentiment 调节。

所以更诚实的分类是：
- **raw alpha**：announcement-time impulse
- **filter/gate**：pre-event sentiment
- **当前阶段结论**：先做 `raw alpha + gate`，而不是只做 blackout

## 9. 数据源、公开性、更新频率、最小可复现实验口径

### 9.1 数据源
1. **官方宏观日历 / 公布页面**
   - Fed FOMC：官方公开
   - BLS CPI / NFP：官方公开
   - BEA PCE：官方公开
2. **crypto sentiment proxy**
   - Alternative.me Fear & Greed：公开 API，日频更新
3. **分钟级行情**
   - Binance / OKX / Coinbase 等公共分钟 K 线

### 9.2 最小可复现实验口径
第一轮先做最便宜版本：
1. 收集 `FOMC + CPI` 的官方发布时间戳；
2. 对 `BTCUSDT / ETHUSDT` 取 `1m / 3m / 5m / 15m` bars；
3. 定义：
   - `r0` = 第一根 event bar 收益
   - `r1` = 接下来 `H` 根累计收益
   - `vol0` = 第一根 volume shock
4. 测试：
   - `sign(r0) * r1` 是否显著大于 0
   - 在 `high/neutral/low sentiment` 三桶里是否存在明显差异
5. 再按 event category 拆：
   - FOMC
   - CPI
   - NFP
   - PCE

这已经足够回答：
- 宏观事件后有没有 follow-through；
- 哪些类别值得保留成 event sleeve；
- sentiment 更像 admission 还是噪声。

## 10. 下一步怎么测（必须）

1. **先做 event-category 拆桶，不要混总样本。**  
   优先顺序：`FOMC -> CPI -> NFP -> PCE`。  
   先分别看四类事件后 `1m/3m/5m/15m` 的 follow-through。

2. **不要先猜方向，先测“第一反应 bar”是否可跟。**  
   具体就是测：
   - `sign(r0) * r1`
   - `sign(r0) * r2`
   - `sign(r0) * r3`
   在不同持有窗口下的 post-cost 表现。

3. **sentiment 只先做 threshold gate。**  
   第一轮只测：
   - `F&G <= 30`
   - `30 < F&G < 70`
   - `F&G >= 70`  
   不做更复杂 embedding / NLP，先验证公开 proxy 能不能把事件窗分层。

4. **把 blackout 与 selective participation 一起 A/B。**  
   至少比较三种：
   - 全 blackout
   - 无 blackout，纯 event-follow
   - blackout 改成 selective participation（只在指定 sentiment bucket 参与）

5. **必须把 cost 单独拉出来看。**  
   事件 alpha 最容易在 gross 上好看、在 net 上死掉。  
   所以每个窗口都要记录：
   - delay 0 / delay 1 bar
   - taker cost
   - slippage 假设
   - gross-to-net decay

## 11. 风险与保留意见

- 当前直接可得的是**摘要级证据**，没有 full sign table，所以不能装作 paper 已经给了完整可部署规则。
- 我这次 portability split 只用 **FOMC**，而 paper 说的是更广义 macro announcement categories；不能把 FOMC 结果直接外推到所有事件。
- Fear & Greed 只是一个廉价 proxy，不等于 paper 的完整 crypto-specific sentiment 构造。
- 这条线如果最终只体现为“波动更大”，却没有稳定 follow-through，那它就会降级成 overlay，而不是 raw alpha。

## 12. 来源

1. **Huynh, N. (2026). _Tuning into the news: Sentiment-driven high-frequency movements in cryptocurrency markets_. Journal of Behavioral and Experimental Finance.**
   - Authors / Year / Title / Venue：Nhan Huynh / 2026 / *Tuning into the news: Sentiment-driven high-frequency movements in cryptocurrency markets* / *Journal of Behavioral and Experimental Finance*
   - DOI：`10.1016/j.jbef.2026.101183`
   - Readable URL：`https://doi.org/10.1016/j.jbef.2026.101183`
   - Metadata URL：`https://api.openalex.org/works?search=%22Tuning%20into%20the%20news%3A%20Sentiment-driven%20high-frequency%20movements%20in%20cryptocurrency%20markets%22`
   - Repo URL：N/A

2. **OpenAlex work metadata / abstract**
   - 数据源：`https://api.openalex.org/works`
   - 公开性：公开可得
   - 用途：重建摘要与 publication metadata

3. **Crossref work metadata**
   - 数据源：`https://api.crossref.org/works/10.1016/j.jbef.2026.101183`
   - 公开性：公开可得
   - 用途：确认 DOI / author / venue / publication date

4. **Federal Reserve FOMC calendars**
   - 数据源：`https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
   - 公开性：公开可得
   - 更新频率：按会议公布
   - 用途：最小事件时钟

5. **Alternative.me Fear & Greed Index API**
   - 数据源：`https://api.alternative.me/fng/`
   - 公开性：公开可得
   - 更新频率：日频
   - 用途：pre-event sentiment proxy

## 13. 本地产物

- `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`
- `reports/artifacts/quant_digests/2026-04-05_tuning_news_sentiment_macro_alpha_probe/fomc_btc_event_sentiment_join.csv`
- `reports/artifacts/quant_digests/2026-04-05_tuning_news_sentiment_macro_alpha_probe/fomc_btc_event_sentiment_bucket_summary.csv`
- `reports/artifacts/quant_digests/2026-04-05_tuning_news_sentiment_macro_alpha_probe/fomc_btc_event_sentiment_extreme_vs_neutral.csv`
