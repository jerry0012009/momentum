# 别把这篇 2020 自相关论文只读成“市场效率检验”：对 short-cycle desk，更该先测的是「15m 上一根方向 × 下一根反打」这条 raw alpha

- 时间：2026-04-11 01:58 UTC
- 类型：2020 arXiv 论文 + 公开 GitHub notebook / datasets + Binance USDⓈ-M `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**如果短周期收益的 lag-1 serial dependence 稳定不为 0，那么上一根 K 的方向本身就是下一根的可交易锚点；而当前 Binance majors 的可移植结果显示，`15m` 更像 anti-persistence，所以更值得先测的是“上一根涨/跌得够明显 → 下一根反打”，不是无脑追涨杀跌。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（alpha 本体清楚，但当前 `15m` 毛边本来就不厚，必须先补 friction ladder / session veto / event veto，才能判断是否能活成完整策略）
- 主题标签：raw-alpha/single-asset/mean-reversion/autocorrelation/serial-dependence/lag1/anti-persistence/one-bar-fade/btc/eth/sol/xrp/doge/bnb/ada/binance-perpetual/15m/5m/paper/repo/public-data/cost/risk
- 证据类型：论文可复现证据 + 开源 notebook + 公共数据 portability probe

## 1. 这次看了什么
主材料是：

- **Eugene Tartakovsky; Ksenia Plesovskikh; Anastasiia Sarmakeeva; Alexander Bibik (2020)**
- **Title:** *Autocorrelation of returns in major cryptocurrency markets*
- **Venue:** arXiv preprint
- **DOI:** `10.48550/arXiv.2003.13517`
- **Readable URL:** <https://arxiv.org/abs/2003.13517>
- **Repo URL:** <https://github.com/3jane/articles/tree/master/1-autocorrelation-time-bars>
- **Notebook / code:** `autocorrelation.ipynb`
- **公开数据入口（notebook 内明写）:** `https://storage.googleapis.com/3jane-articles/datasets/1-autocorrelation`

这篇 paper 的 abstract 很短，但有两件事非常值钱：

1. 它不是泛泛而谈“crypto 可能有效/无效”，而是直接盯 **return autocorrelation** 这条最短路径；
2. 它不是只有结论，**连 exact datasets、requirements、notebook 都给了**，这比很多 2024~2026 只有摘要的新材料更适合直接 intake。

原文 abstract 的核心意思是：

> **5m 和 1H 上，major crypto 市场存在持续、统计显著的收益自相关。**

但对 short-cycle desk 来说，真正有用的翻译不是“市场不完全有效”这句空话，而是：

> **上一根 bar 的方向，可能本身就是下一根 bar 的 alpha 锚点。**

一句话核心结论：

> **别把这篇 paper 只读成统计学练习；对当前 desk，更值得先搬的是“lag-1 serial dependence → one-bar router”这条 raw alpha 骨架，而当前 Binance majors 的 first verdict 更偏向 `15m` 反打，不是 `5m` 追涨。**

一句话证明方式：

> **论文用 Pearson autocorr、Ljung-Box、rolling first-order autocorr 做可复现实证；我再用 Binance USDⓈ-M 7 个 majors 的公开 `5m/15m` klines 做 portability probe，看“上一根方向”在当前市场到底更像 continuation 还是 fade。**

## 2. 为什么这轮值得选它，哪怕它不是最近 5 年新论文
默认当然优先近 5 年材料；但这次我还是选了这篇 2020 文献，原因很实际：

- 它和当前 digest 池里大量 `pairs / funding / basis / cross-venue` 主题**不重复**；
- 它补的是 **single-asset、最短路径、最小可验证** 的 raw alpha 地基；
- 它不是只有 abstract，而是 **paper + notebook + requirements + datasets** 一整套都开着；
- 它直接对应当前 desk 关心的 `5m / 15m`，不需要先借一大层外部数据或复杂组合壳。

翻成人话：

> **最近几轮 relative-value / stat-arb 已经很多了，这次更值得补一条“只看自己上一根 bar”就能做最小实验的 raw alpha 地基。**

## 3. 这篇东西最该拿走的，不是“有自相关”四个字，而是这 3 个零件
### 3.1 它给的是最短可复现研究骨架
notebook 直接把流程写死了：

- 下载 exact datasets
- 算不同 lag 的 Pearson autocorr
- 跑 Ljung-Box
- 画 rolling first-order autocorr

这意味着我们不是在猜作者怎么做，而是可以直接复制研究路径。

### 3.2 它盯的是“下一根怎么走”，不是中长周期宏大叙事
很多论文最后只能落到：

- regime 解释
- 风险溢价解释
- 大类配置解释

而这篇 paper 的研究对象离交易更近：

> **上一根收益，是否对下一根收益有方向信息。**

这正好符合当前 scout / first-verdict 逻辑。

### 3.3 它没把 sign 预设成“必须正”
abstract 说的是 **statistically significant autocorrelation**，并没有替我们把交易翻译成“永远追涨”。

这点很关键，因为对 desk 来说，真正重要的不是“有没有相关”，而是：

- 相关是正的还是负的；
- 在哪个周期上更稳；
- 大波动 bar 之后是更容易续动还是更容易反打。

也就是说，这篇 paper 给的是：

> **可被 desk 化的最底层问题定义。**

而不是已经替你写好的最终策略。

## 4. 对当前 desk 来说，最值得 desk 化的读法是什么
如果只照标题走，最容易把它读成：

- “crypto 短周期不完全有效”
- “所以可以追涨杀跌”

但这其实不够诚实。

对我们更有价值的读法应该是：

> **先把 `lag-1` 当成最小 alpha 锚点，再让市场自己告诉我们：当前更像 continuation 还是 mean reversion。**

而这轮 public-data probe 给出的答案很清楚：

- `5m`：整体几乎没什么统一 sign，继续追并不干净；
- `15m`：7 个 major 都是 **负的 lag-1 autocorr**，所以当前更像 **one-bar fade**。

所以这次真正进入研究池的，不该是“autocorr continuation”这 4 个字，而是：

> **`15m` 上一根方向 × 下一根反打。**

这是一条 raw alpha，不是 filter，也不是 overlay。

## 5. 本地 portability probe：Binance USDⓈ-M majors 上，这条线现在更像 continuation 还是 fade？
我用 Binance USDⓈ-M 公开 klines 做了一个很克制的最小快检：

- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / BNBUSDT / ADAUSDT`
- 周期：`5m` 与 `15m`
- 每个标的每个周期最近 `1500` 根 bar
- 指标：
  - `lag1_autocorr`
  - 若下一根继续跟随上一根方向，signed next-bar bps 是多少
  - 若只挑大 bar（`|ret| >= q75 / q90`），这个 signed next-bar bps 会怎样

本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/return_autocorr_continuation_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/return_autocorr_continuation_probe_detail_2026-04-11.csv`

### 5.1 `5m`：整体接近 0，没资格直接当主线 continuation alpha
aggregate `5m` 结果：

- 平均 `lag1_autocorr ≈ -0.0018`
- 若无脑顺着上一根方向做下一根，平均只剩 **`+0.30 bps`**
- 但一旦只看 `|ret| >= q75` 的较大 bar，反而变成 **`-0.47 bps`**

翻成人话：

> **`5m` 没有给出干净统一的方向答案；它更像“混合态”，不适合作为这轮单主题主 lane。**

### 5.2 `15m`：7 个 majors 全部转成负 lag-1，自带反打味道
aggregate `15m` 结果很整齐：

- 7 个标的的 `lag1_autocorr` **全部为负**
- 平均 `lag1_autocorr ≈ -0.0589`
- 如果你顺着上一根方向去做下一根，平均是 **`-1.45 bps`**
- 反过来说，如果你做“上一根的反向”，毛边大约就是 **`+1.45 bps`**

这不是单一币种偶然抽风，而是这 7 个 majors 同时给出的方向。

### 5.3 只挑较大 bar，`15m` 的 one-bar fade 更干净
如果只在大一点的 bar 后动手：

- 当 `|ret| >= q75`（各币 `15m` 绝对收益前 25%）时：
  - 顺势 continuation 的平均 signed next-bar bps ≈ **`-2.29 bps`**
  - 等价地，fade 的平均毛边 ≈ **`+2.29 bps`**
  - fade 胜率均值约 **56.7%**
- 当 `|ret| >= q90` 时：
  - fade 平均毛边约 **`+1.47 bps`**
  - fade 胜率均值约 **56.8%**

这说明更合理的 desk 化壳不是“每根都反着做”，而是：

> **上一根方向明显、但还没大到变成真 break 的时候，下一根更容易 snap back。**

### 5.4 各币 `15m` 都是同方向：追随输，反打赢
`15m` continuation 的平均 signed next-bar bps（越负越说明更该 fade）：

- `ETH`: **-2.17 bps**
- `SOL`: **-2.21 bps**
- `DOGE`: **-1.57 bps**
- `XRP`: **-1.37 bps**
- `BTC`: **-1.31 bps**
- `ADA`: **-1.07 bps**
- `BNB`: **-0.41 bps**

这比“某个币特别灵”更重要，因为它说明：

> **当前窗口里，`15m` anti-persistence 更像 market-wide short-cycle texture，而不是单币孤例。**

## 6. 但要非常诚实：现在还不能把它直接吹成 production alpha
### 6.1 这是 close-to-close proxy，不是 executable PnL
现在看的只是：

- 上一根 close 到这一根 close 的收益
- 下一根 close 到再下一根 close 的 signed bps

还没有显式加入：

- maker / taker 区分
- 入场延迟
- spread crossing
- 滑点
- funding / fee tier

所以这里的 bps 只能当 **directional first verdict**，不是 live 可赚 bps。

### 6.2 `15m` 的毛边不厚，必须严肃看成本
`15m` 的 fade 平均毛边大概是：

- 全样本：`+1.45 bps`
- 大 bar 条件后：`+2.29 bps`

这意味着：

> **如果交易壳是 taker-heavy，它很可能直接被成本吃掉。**

所以这条线更像：

- maker-first
- 限制只做最液体币
- 只做较大 bar 后的 next-bar fade
- 带严格 session / event veto

### 6.3 `5m` 和 `15m` 给了相反的研究信号
这也是好事，因为它告诉我们别偷懒：

- `5m` 不够干净，不值得用“一套 sign 逻辑”硬压；
- `15m` 反打更清楚，应该先把资源集中在这里。

所以它不是“全周期 alpha”，而更像：

> **一个先在 `15m` 诚实落地、再向 `5m/3m` 做 transfer check 的 raw alpha 骨架。**

## 6.5 策略拆解（必填）
- 方向属性：single-asset / mean reversion / one-bar fade
- 基础 alpha：`15m` lag-1 negative serial dependence（上一根方向 → 下一根反打）
- regime：优先在常规流动性时段、无重大宏观事件窗口使用
- filter / veto：只在 `|15m ret|` 超过 rolling 分位阈值后开；高 funding 结算窗口 / 重大新闻前后 veto
- risk / sizing / execution overlay：maker-first、单笔时间止盈止损、每币 gross cap、连续亏损 throttle

## 7. 可复刻的最小实验
### 数据源 / 公开性 / 更新频率
- Binance USDⓈ-M `fapi/v1/klines`
- 公开可抓，无需私有 key
- 更新频率：`1m` 及以上都可；这轮主看 `15m`

### 最小研究假设
> 当某 liquid major 在 `15m` 出现方向明确的较大单根收益时，下一根 `15m` 更可能对上一根做部分反打，而不是继续顺着上一根延展。

### 最小回测切口
- 标的：`BTC / ETH / SOL / XRP / DOGE / BNB / ADA`
- 周期：`15m`
- 入场：若上一根 `|ret| >= rolling q75`，则下一根开盘反向入场
- 出场：
  1. 下一根收盘强平（one-bar hold）
  2. 或更 desk 化一点：`1 bar time stop + intrabar ATR stop`
- 先看三项：
  1. 毛 `signed next-bar bps`
  2. 扣 `2 / 4 / 6 bps` friction ladder 后是否仍活
  3. 分币、分时段是否集中在个别 pocket

## 8. 下一步怎么测
下一步我不会先扩更多币，而会先把这条线做成一个 honest shell：

1. **先把 `15m q75 fade` 做成 one-bar 持有基线**
   - 入场：上一根绝对收益超过 rolling `q75`
   - 方向：反着上一根做
   - 出场：下一根 close
   - 这是最小、最干净、最不容易自欺的 baseline

2. **显式做 friction ladder**
   - 至少测 `2 / 4 / 6 bps`
   - 若 `2 bps` 已死，这条线就不值得继续包装成完整策略
   - 若只在 `0~2 bps` 活，就把它降级为 maker-only candidate 或 admission component

3. **做时段与事件剔除**
   - 剔除 funding 结算前后
   - 剔除 CPI / FOMC / NFP 等大事件窗口
   - 看 anti-persistence 是不是主要来自 event-noise，而不是平时就稳定存在

4. **把 `5m` 当 transfer check，不当主 lane**
   - 先不要强行把 `15m` 逻辑复制到 `5m`
   - 只检查：`15m` 触发后，是否能在 `5m` 找到更优 execution / better fill，而不是期待 `5m` 自己也有同样 sign

5. **若 one-bar fade 太薄，再补 shared gate**
   - 例如仅在 `ATR / realized vol` 中段做
   - 或只在 BTC / ETH 主流币上做
   - 但这些都应被写成 filter，不要伪装成 alpha 本体

如果这套 one-bar fade 在 `15m` 上连 `2~4 bps` 的 honest friction ladder 都活不下来，就该把它降级成：

- execution timing helper
- spread-entry optimizer
- 其他 mean-reversion alpha 的 child-entry layer

而不是继续硬吹成独立策略。

## 9. 来源
- Tartakovsky, Eugene; Plesovskikh, Ksenia; Sarmakeeva, Anastasiia; Bibik, Alexander (2020).
  - *Autocorrelation of returns in major cryptocurrency markets*
  - arXiv: <https://arxiv.org/abs/2003.13517>
  - DOI: <https://doi.org/10.48550/arXiv.2003.13517>
- 3Jane reproducibility repo:
  - <https://github.com/3jane/articles/tree/master/1-autocorrelation-time-bars>
  - README: <https://raw.githubusercontent.com/3jane/articles/master/1-autocorrelation-time-bars/README.md>
  - requirements: <https://raw.githubusercontent.com/3jane/articles/master/1-autocorrelation-time-bars/requirements.txt>
  - notebook: <https://raw.githubusercontent.com/3jane/articles/master/1-autocorrelation-time-bars/autocorrelation.ipynb>
- 本地 portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/return_autocorr_continuation_probe_summary_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/return_autocorr_continuation_probe_detail_2026-04-11.csv`
