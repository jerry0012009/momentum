# 别把 crypto pairs baseline 只当老派日频：这篇 2021 开放获取论文更该先留作「plain-vanilla spread convergence」完整 raw alpha 对照组，但 2025Q4~2026Q1 Binance `15m` 只剩 gross、成本后仍不活
- 时间：2026-03-26 15:05 UTC
- 类型：2021 开放获取论文（全文 PDF 可读）+ Binance Spot 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**在高相关/可协整的币对里，短期相对赢家与相对输家会向长期均衡关系回归；因此做法是 long 低估腿、short 高估腿，吃 spread convergence，而不是赌市场整体方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/plain-vanilla/cointegration/hedge-ratio/long-short/long-only-control/binance/spot/15m/5m/1m/3m/paper/external-data/cost
- 证据类型：论文全文证据 + 当前公开市场最小 transfer check

## 1. 这次看了什么
先把 **base alpha** 说死：**这不是“pairs 很高级所以可能赚钱”，而是“同一对高相关币如果暂时走散，短期更容易收敛而不是无限发散”，所以交易上应当 short 相对贵的一腿、long 相对便宜的一腿。**

主材料是 **Saji Thazhungal Govindan Nair (2021), _Pairs trading in cryptocurrency market: A long-short story_**。它对当前 desk 真正有价值的地方，不是又证明一次“crypto 不完全有效”，而是给了一个非常适合作为 **pair/stat-arb 家族 plain-vanilla baseline** 的完整骨架：
- 先用 **correlation / distance / cointegration** 挑对；
- 再用 **cointegration beta** 当 hedge ratio；
- 交易逻辑不是 long-only，而是 **long-short spread convergence**；
- 最后明确拿 **long-short vs long-only** 做 payoff / risk 对照。

这轮之所以值得写，即使最近已经 intake 过不少 pairs 主题，也有很直接的理由：**当前素材池里 fancy pairs 很多，但缺一个公开可读、逻辑极简、能当控制组的 plain-vanilla benchmark。** 没有这个控制组，后面再看 network pairs、dynamic threshold、basket stat-arb，很容易把“复杂”误当“更强”。

## 2. 核心结论
- 论文样本是 **BTC / ETH / LTC / NEO** 四个币的 **2018-01-01 ~ 2019-12-31 日频美元价格**，并切成四个 **6 个月 panel** 做 formation / trading 对照。
- 作者不是只做一种方法，而是并排看 **correlation、distance、stochastic return differential、Engle-Granger cointegration**，最后把 **cointegration beta** 当成最小方差 hedge ratio 来交易。
- 论文最值得记住的判断很简单：**long-short pairs 在大部分子样本里稳定优于 long-only 持有同一对币。**
- 文中给出的几个醒目数字：
  - Panel A 里 **ETH-NEO** long-short 累计利润 **857.52 美元**、profit per unit of risk **112.33**；
  - Panel B 里 **BTC-ETH** long-short 累计利润 **1527.91 美元**、profit per unit of risk **152.88**；
  - 即便在更剧烈波动的 Panel C，**BTC-ETH** 与 **ETH-LTC** 的 long-short 仍显著优于 long-only。
- 翻成人话：**这篇 paper 最值钱的不是“哪一对历史上最赚钱”，而是它把 pairs 最朴素的完整策略链条写全了：选对 → 定 hedge ratio → long-short 开仓 → 与 long-only 对照。**

## 3. 为什么和当前项目直接相关
这轮我仍然把它归到 **raw alpha / 完整策略候选**，而不是解释性综述，原因有 3 个：
1. **base alpha 非常清楚**：spread convergence 本身就是 alpha，不是 filter；
2. **能直接服务现有 desk 的 pairs/stat-arb 素材池**：它是很多更复杂 papers 的母体控制组；
3. **它回答了一个很现实的问题**：如果连 plain-vanilla baseline 都活不下来，就别急着给 fancy pairs 加更多状态机和优化层。

也就是说，这篇东西比“再找一个更花哨的 pair 变体”更值钱的地方在于：**它帮我们建立 pairs 家族的最低可接受基线。** 后续无论是 network peripheral pair、basket OU、dynamic threshold，最好都先拿它做对照。

## 3.5 策略拆解（必填）
- 方向属性：**relative value / stat-arb / mean reversion / market-neutral**
- 基础 alpha：**pair spread 偏离长期均衡后回归**
- regime：默认偏向 **range / non-trending / correlation-stable** 环境；强单边趋势与结构断裂期更容易失效
- filter / veto：
  - formation 期相关性、协整显著性、残差稳定性
  - 近端 rolling correlation 崩塌 / beta 漂移过快时不做
- risk / sizing / execution overlay：
  - 用 **cointegration beta** 或 rolling OLS beta 做 hedge ratio
  - gross 归一、净敞口尽量市场中性
  - 强制加入 fee / spread / impact 阶梯，不能只看 gross

更 desk 化的最小版本可以写成：
- **pair selection**：从大币 universe 里选 formation 窗口相关性最高、且 spread 较稳定的 pairs；
- **signal**：`z_t = (spread_t - mean(spread)) / std(spread)`；
- **entry**：`|z_t| > z_enter` 时，long 低估腿 / short 高估腿；
- **exit**：next bar 收盘、或 `z` 回到 0 附近；
- **sizing**：按 `1 : beta` 配对并做 gross normalization；
- **cost**：按 round-trip bps 直接扣减；
- **risk**：当 rolling correlation / hedge ratio 漂移超阈值时整对禁做。

## 4. 这轮最小 transfer check：当前 Binance `15m` 还能不能留住这条 plain-vanilla edge
为了不只复述论文，我做了一个非常克制的当前快检：
- 市场：**Binance Spot**
- 周期：**`15m`**
- 样本：近 **120 天**，前 **60 天 formation**、后 **60 天 trading**
- universe：`BTC / ETH / BNB / SOL / XRP / ADA / DOGE / LTC`
- 先按 formation 期 return correlation 选 top-3 pairs，再用 log-price OLS 估计 hedge ratio
- 交易规则：**上一根 close 的 spread z-score 超阈值，下一根 open 开 long-short，对应 bar close 平仓**
- 成本口径：**6 bps round-trip**

### 4.1 当前选出的 top-3 pair
- `ETH/BTC`
- `DOGE/ADA`
- `SOL/ETH`

### 4.2 结果怎么读
组合层（`z_enter = 1.0`）结果：
- **gross ≈ +0.21 bps/bar**
- **annualized gross Sharpe ≈ 8.73**
- **cumulative gross ≈ +12.7%**
- 但 **6 bps round-trip 后 ≈ -3.50 bps/bar**
- **cumulative net ≈ -86.7%**
- 同期 long-only 对照大约 **-0.01 bps/bar / cumulative ≈ -2.7%**

阈值往上抬也没救活：
- `z_enter = 2.5` 时，平均 active share 已降到 **9.7%**；
- 但组合 **gross 只剩 +0.07 bps/bar**，**net 仍约 -0.51 bps/bar**。

这组数字很像论文给我们的现实提醒：**plain-vanilla pairs 作为 raw alpha 骨架是成立的，但在主流 venue 的短周期实现里，真正的第一性约束仍然是换手与成本。**

## 5. desk 化判断
这篇 paper 我会保留，而且优先级不低，但定位要说准：
- **它是 raw alpha / 完整策略 baseline**，不是 filter；
- **它适合当 pairs 家族的 control group**，不适合直接当 live-ready 成品；
- 当前 `15m` Binance transfer 的诚实结论是：**gross 有、cost 后没了。**

所以它的最现实用途不是“今天直接上”，而是：
1. 给后续所有 fancy pairs 提供基准线；
2. 明确告诉我们，pairs 下一步不能再只卷 signal，必须卷 **selection stability + turnover governance + maker pocket**；
3. 让 desk 在评估新 papers / repos 时，能先问一句：**你比 plain-vanilla baseline 多出来的复杂度，真的换来了净 edge 吗？**

## 6. 可复刻的下一步怎么测
### 6.1 第一优先：把 `always next-bar close` 改成真正的 spread-exit
这轮快检为了克制，只做了单 bar holding。下一轮更该测：
- `entry: |z| > 1.5 / 2.0`
- `exit: z → 0` 或 `max_hold = 4 / 8 bars`
- 比较 **单 bar、半回归、零轴回归** 三种 exit 的 turnover / net edge

### 6.2 第二优先：把 pairs 选择做成“稳定性 funnel”
别只看 formation corr。下一轮至少补：
- rolling correlation 稳定度
- beta 漂移幅度
- spread half-life
- 最小成交额 / depth / tick size 过滤

### 6.3 第三优先：只在 maker / rebate pocket 里复测
当前 6 bps round-trip 基本把 edge 全吃光。更值得测的是：
- maker-only 或低 fee bucket
- `5m / 15m` 的 active-share 限制
- 同时记录 quote life 与挂单成交率

### 6.4 第四优先：把它升级成“plain baseline vs fancy variant”固定对照表
后面每来一篇新的 pairs / stat-arb paper，都固定和这条 baseline 比：
- gross / net bps
- turnover
- active share
- selection stability
- cost break-even

## 7. 风险与保留意见
- 原论文是 **2018~2019 日频 + 4 个币**，样本老、币池小，不能把历史 payoff 直接平移到今天的大币 `15m`；
- 我这轮 transfer 也不是 clean replication，而是 **desk 化最小映射**；
- 结果说明的是：**机制在，净利润不一定在**；
- 因此更合理的结论不是“pairs 不行”，而是：**plain-vanilla pairs 在当前主流短周期口径下，更像研究控制组，而不是可直接上线的 alpha 成品。**

## 8. 来源
1. **Nair, S. T. G. (2021). _Pairs trading in cryptocurrency market: A long-short story_. Investment Management and Financial Innovations, 18(3), 127-141.**
   - DOI: `10.21511/imfi.18(3).2021.12`
   - Readable URL: `https://www.businessperspectives.org/index.php/journals/investment-management-and-financial-innovations/issue-385/pairs-trading-in-cryptocurrency-market-a-long-short-story`
   - PDF URL: `https://www.businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/15401/IMFI_2021_03_Govindan.pdf`
   - Repo URL: `N/A`
2. **Binance Spot public klines API**
   - Readable URL: `https://api.binance.com/api/v3/klines`

## 9. 本地相关产物
- Digest：`research/quant_digests/2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`
- Artifact：`reports/artifacts/quant_digests/pairs_longshort_story_20260326_1505/summary.json`
- Artifact：`reports/artifacts/quant_digests/pairs_longshort_story_20260326_1505/threshold_sweep.json`
