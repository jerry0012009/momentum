# 别把 2025 intraday lottery 论文继续只借来做 gate：它更该先回到自己的 headline ——「past-hour MAX rich-vs-cheap 横截面 fade」raw alpha
- 时间：2026-03-25 23:34 UTC
- 类型：2025《Studies in Economics and Finance》论文 + OpenAlex 摘要元数据 + Binance Futures 公共 `5m/15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**过去 1 小时里刚打出“最极端 5m 上冲”的币，下一小时往往相对更弱；做法不是追它，而是做一篮子 `long low-MAX / short high-MAX` 的横截面 lottery-fade**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/lottery-fade/max-effect/intraday/5m/15m/1h/relative-value/market-neutral/binance/perpetual/paper
- 证据类型：论文摘要证据 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，也不是把 MAX 拿去给别的策略做确认层。它自己的 base alpha 就是 cross-sectional mean reversion / lottery fade。** 更直白点：谁在过去一小时里打出最夸张的单根 `5m` 涨幅，下一段更容易从“被追逐”回到“被回吐”。

## 1. 这次看了什么
主线来源是：

1. **Manisha Yadav (2025), _Intraday lottery demands in cryptocurrency market_, Studies in Economics and Finance**  
2. **OpenAlex 对该文的结构化摘要元数据**（用于补充可公开读取的摘要信息）
3. **Binance USDⓈ-M Futures 公共 `5m` K 线最小快检**（把论文 headline 直接翻成 desk 可跑的 raw alpha 骨架）

这轮之所以值得写，不是因为我们第一次见到“彩票偏好/极端收益会回吐”这个想法，而是因为：
- 最近 desk 已经有一条 **`positive-jump variance 横截面 fade`**；
- 也已经把这篇 2025 论文借去做过一次 **EMA reclaim confirmation gate**；
- 但到这一步，更诚实的动作其实应该是：**别再只把它当旁支过滤器，先把它自己的 headline alpha 作为一条更短、更干净、更容易复现的 raw alpha baseline 收进池里。**

## 2. 核心结论
- **一句话核心结论：** 如果要做短周期 lottery-fade，最先该测的不一定是更复杂的 jump decomposition；这篇 2025 论文提示，**仅用“过去 1 小时最大单根 `5m` 收益（MAX）”就能形成一条可独立复现的横截面 raw alpha。**
- **一句话证明方式：** 作者用 **top 100 liquid crypto 的高频数据**，把过去 1 小时 `5m` 收益里的 `MAX` 当成彩票需求代理，再用 **portfolio sorts + Fama-MacBeth cross-sectional regressions** 检查其对下一段收益的预测力。

### 3 个关键数据点
1. **论文口径非常直接。** 作者用的是 **top 100 most liquid cryptocurrencies**，把 **过去 1 小时的 `5m` log return** 做成 `MAX` 指标，再预测 **后续 1 小时** 收益。  
2. **论文 headline 数字够清楚。** OpenAlex 摘要给出的核心结果是：**`MAX` 每上升 1 个标准差，后续收益约下降 `0.043%`（4.3 bps）**，方向就是典型的 lottery-fade。  
3. **本地 public-data 快检：毛收益有，成本是硬门槛。** 我在 Binance 公共 `5m` perp 数据上，用 `BTC/ETH/BNB/XRP/ADA/LINK/LTC/BCH/XLM/ETC/TRX/ATOM` 做了最小横截面版本：
   - 样本：**2026-02-12 07:30 UTC ~ 2026-03-25 23:30 UTC**，约 **998 个非重叠 hourly rebalances**  
   - 规则：每小时做一次 **`long bottom 30% MAX / short top 30% MAX`**  
   - **gross：`+1.42 bps/hour`，累计 `+15.25%`，Sharpe `3.62`**  
   - **若粗暴按 `1 bp/side` 计全换手成本：净值变成 `-22.68%`**  

## 3. 为什么和当前项目有关
### 3.1 它补的是“更简单的 lottery-fade 基线”
最近素材池里已经有：
- `24h loser reversal`
- `high-vol loser bucket`
- `positive-jump variance fade`

但这些都比 `past-hour MAX` 更“加工过”。这篇 2025 论文的价值在于：**它把同一类行为金融/短周期过度追逐，压缩成了一个极其便宜、极其容易公有数据复现的 baseline。**

### 3.2 它也修正了我们前几天对同一篇论文的读法
3 月 20 日那篇 digest，我们把它 desk 化成了 **EMA reclaim 的 confirmation gate**。那个读法没错，但更像“借材料做旁支”。

这轮回到它真正的主线上，价值反而更高：
- **base alpha 说得清；**
- **能独立成策略；**
- **和 recent raw-alpha intake 直接同类可比。**

尤其适合拿来和下面几条做 A/B：
- `positive-jump variance fade`
- `24h loser × high-vol interaction`
- `volume-decay throttle` 下的 XS short-term reversal

## 3.5 策略拆解（必填）
- 方向属性：**横截面 / relative-value / mean-reversion**
- 基础 alpha：**过去 1 小时 `MAX(5m return)` 越高，下一小时相对回报越差；做 `long low-MAX / short high-MAX`**
- regime：**更可能在高投机、高离散度、短时追涨更强的时段里更有效**；但这点应作为下一轮显式检验，不先脑补为 always-on
- filter / veto：
  - 仅保留流动性前列合约
  - 排除公告/宏观事件前后极端跳变窗口
  - 与 `liquidation cascade` 题材做冲突检查，避免把真趋势延续错当成回吐
- risk / sizing / execution overlay：
  - 组合层保持 dollar-neutral / equal-weight baseline
  - 优先 **小时级再平衡**，不要直接每根 `5m` 追着换
  - 成本上先测 `maker-first 1~2 bar`，再测 taker fallback；否则毛边大概率直接被换手吃光

## 4. 可复刻的最小实验
### 研究假设
`past-hour MAX` 是一条 **比 jump-variance 更轻、更快、更便宜** 的 lottery-fade 原型；若它连最小 public-data 版本都没有 gross edge，就没必要继续往复杂版本上加料。

### 一个可计算定义
对每个币 `i`：
- `MAX_i,t = max(r_i,t-11 ... r_i,t)`，其中 `r` 是 `5m` log return
- 每小时做一次横截面排序：
  - long：`MAX` 最低的 bottom 30%
  - short：`MAX` 最高的 top 30%
- 持有下一小时，组合等权 market-neutral

### 最小回测切口（本轮已快检）
- 数据源：**Binance USDⓈ-M Futures 公共 K 线**
- 公开性：**公开可得，无需私钥**
- 更新频率：`5m`
- 标的：`BTC / ETH / BNB / XRP / ADA / LINK / LTC / BCH / XLM / ETC / TRX / ATOM`
- 样本：**2026-02-12 ~ 2026-03-25**
- 第一层 honest 结论：
  - **hourly non-overlap gross = `+1.42 bps/hour`，Sharpe `3.62`**
  - **但 `1 bp/side` 粗成本下已明显转负**

### 最该先看的 2 个指标
1. **净 bps / rebalance**：不是先看 Sharpe，而是先看单次换手到底能不能养活自己  
2. **turnover-adjusted edge**：和 `positive-jump variance`、`24h loser reversal` 比，谁在相同 cost ladder 下更耐磨

## 5. 风险与保留意见
- 这篇论文的 headline 很漂亮，但**本地最小快检已经说明：它首先是“有毛边”，不代表“能直接落地 taker 交易”。**  
- 我的快检只用了 **12 个 Binance perp**，比论文的 **top 100 liquid crypto** 更窄；统计显著性和横截面丰富度都更弱。  
- `MAX` 很容易和 **liquidation / panic / news shock** 混在一起；若不分清“过度追逐”与“真实信息到达”，会把 continuation 和 reversal 看混。  
- 因为这条线极度依赖换手，**它更像一条需要 execution / threshold / regime 共管的 raw alpha**，而不是可以无脑 always-on 的独立机器。  

## 6. 下一步怎么测
1. **先和今天的 `positive-jump variance fade` 做正面对照。** 同一 universe、同一 cost ladder、同一持有期，比较谁的 `net bps / turnover` 更高。  
2. **做阈值稀疏化。** 不要每小时都做，先测 `MAX dispersion` 进入前 30%/20%/10% 才开仓，看能否把毛边压缩成更少但更厚的交易。  
3. **把执行从 taker 改成 maker-first。** 若 `gross +1.42 bps/hour` 是真边，那么它只可能在低摩擦执行里存活；默认应测 `maker 1 bar -> taker fallback`。  
4. **把 `5m signal / 15m execution` 单独跑一版。** 对当前 desk，更现实的路线不是 bar-bar 追切，而是让 `5m MAX` 负责发现过热对象，`15m` 做低频篮子执行。  
5. **补“真 continuation 误伤”排查。** 把 `funding/OI/liquidation` 共振最强的窗口单独切出来，看 `MAX fade` 是否在这些时段反而失效。  

## 7. 来源
1. **Yadav, M. (2025). _Intraday lottery demands in cryptocurrency market_. Studies in Economics and Finance, 42(4), 799–835.**  
   - Authors: Manisha Yadav  
   - DOI: `10.1108/SEF-07-2024-0461`  
   - Readable URL: `https://doi.org/10.1108/SEF-07-2024-0461`  
   - Repo URL: `N/A`
2. **OpenAlex work record for the same paper**（用于公开摘要抓取与元数据核对）  
   - Readable URL: `https://api.openalex.org/works/https://doi.org/10.1108/SEF-07-2024-0461`
3. **Binance Developers – USDⓈ-M Futures Kline/Candlestick Data**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/intraday_max_lottery_xs_20260325_2330/summary.json`
- `reports/artifacts/quant_digests/intraday_max_lottery_xs_20260325_2330/summary_15m_variants.json`
- `reports/artifacts/quant_digests/intraday_max_lottery_xs_20260325_2330/hourly_longlow_shorthigh_returns.csv`
- `reports/artifacts/quant_digests/intraday_max_lottery_xs_20260325_2330/universe.json`
