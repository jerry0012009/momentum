# 别把这篇 2025 intraday MAX 论文只读成“彩票效应”：对 short-cycle desk，更该先测的是「past-hour MAX overvaluation × cross-sectional fade」这条 raw alpha

- 时间：2026-04-11 12:58 UTC
- 类型：2025 *Studies in Economics and Finance* 论文摘要/元数据（Crossref + OpenAlex）+ 2021 *Financial Innovation* 开放获取母体论文 + Binance USDⓈ-M `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**过去 1 小时里打出更极端单次正收益（MAX） 的币，在接下来一根 `5m/15m` 横截面里更容易相对跑输；也就是 `long low-MAX / short high-MAX` 的 intraday cross-sectional mean-reversion / anti-lottery alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/relative-value/intraday/max-effect/anti-lottery/lottery-demand/overvaluation/past-hour-extreme-return/market-neutral/binance-perpetual/5m/15m/paper/metadata-plus-open-mother-paper/public-data/cost/risk
- 证据类型：2025 论文摘要+元数据证据 + 2021 开放获取母体论文全文证据 + 公共数据 portability probe

## 1. 这次看了什么
主材料：

- **Manisha Yadav (2025)**
- **Title:** *Intraday lottery demands in cryptocurrency market*
- **Venue:** *Studies in Economics and Finance*
- **DOI:** `10.1108/SEF-07-2024-0461`
- **Readable URL:** <https://doi.org/10.1108/SEF-07-2024-0461>
- **Publisher page:** <https://www.emerald.com/insight/content/doi/10.1108/SEF-07-2024-0461/full/html>
- **Repo URL:** 无公开 repo

辅助母体材料：

- **Melisa Ozdamar; Levent Akdeniz; Ahmet Sensoy (2021)**
- **Title:** *Lottery-like preferences and the MAX effect in the cryptocurrency market*
- **Venue:** *Financial Innovation*
- **DOI:** `10.1186/s40854-021-00291-9`
- **Readable URL:** <https://doi.org/10.1186/s40854-021-00291-9>
- **Open PDF:** <https://jfin-swufe.springeropen.com/track/pdf/10.1186/s40854-021-00291-9>
- **Repo URL:** 无公开 repo

这轮最值得拿走的，不是“crypto 也有 lottery demand”这句行为金融大词，而是一个非常具体、非常 desk-friendly 的翻译：

> **日/周频的 MAX effect 可以是 continuation，但 intraday 的 past-hour MAX 更像 overvaluation；对短周期 desk，应该先测 `long low-MAX / short high-MAX` 这条横截面 fade。**

一句话核心结论：

> **同样都叫 MAX，日频/周频可以是“最近飙得猛的继续强”，但到了 past-hour intraday 口径，极端上冲更像短时被追价过头，下一根更该被淡化而不是被追。**

一句话证明方式：

> **2025 论文摘要直接给出：用“过去 1 小时的 5 分钟收益 MAX”解释后续收益时，MAX 的系数是负的；我再把这个信号压到 Binance USDⓈ-M 16 币种 `5m/15m` 横截面 long-short 篮子里，检查它到底是纯学术结论，还是能长成 desk 的低成本 raw alpha。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 很清楚：

> **intraday anti-lottery / MAX-overvaluation fade**。

翻成人话：

- 看的不是“过去 1 小时总共涨了多少”；
- 看的是“过去 1 小时里，有没有某一根冲得特别离谱”；
- 如果某币刚在最近 1 小时里打出更极端的单次正收益，它下一根更容易相对全市场回吐；
- 所以可交易版本不是追 strongest spike，而是：
  - **做空高 MAX 币；**
  - **做多低 MAX 币；**
  - 组成一个 market-neutral long-short book。

它不是：

- 纯 regime gate；
- 纯行为金融解释；
- 纯风险指标。

它本身就能独立形成多空横截面 book，所以归类成 **raw alpha** 是成立的。

## 3. 2025 这篇新论文，到底说了什么
Crossref/OpenAlex 摘要里，最关键的信息其实已经足够具体：

### 3.1 它测的是 intraday 版 MAX，不是老日频定义
论文把 Bali et al. 的 MAX 指标改成了更贴近高频市场的口径：

- **信号窗口：过去 1 小时**
- **基础收益采样：`5m` log return**
- **样本：top 100 most liquid cryptocurrencies**
- **检验：portfolio-level analysis + Fama-MacBeth cross-sectional regressions**

也就是：

> **这不是“过去一个月谁打过大阳线”，而是“过去一个小时谁刚被追得最猛”。**

这对 `1m/3m/5m/15m` desk 很重要，因为它不是那种很难往短周期迁移的低频信号。

### 3.2 结论方向是负的：高 MAX 对后续收益不是利好，而是利空
摘要给出的最硬一句是：

> **MAX 每增加 1 个标准差，后续收益下降约 `0.043%`。**

这句话翻成人话就是：

- 最近 1 小时里越是打出“夸张单根上冲”的币；
- 接下来越容易在横截面里变成**相对弱者**。

也就是 **anti-lottery / fade**，不是 continuation。

### 3.3 作者还特意把 IVOL / skewness 拉进来一起比，结论仍说 MAX 才是主效应
摘要还说：

- 论文同时看了 **idiosyncratic volatility (IVOL)**；
- 看了 **idiosyncratic / systematic skewness**；
- 但拆开以后，**MAX 才是更核心的效应**。

对 desk 的意义是：

> **第一落点先别急着加太多花哨修饰，先测 MAX 本体。**

IVOL、skewness 可以是第二轮增强层，不该一开始就把 base alpha 稀释掉。

## 4. 为什么这轮值得做：它刚好补了一个“时间尺度翻号”的缺口
这轮真正有研究价值的地方，在于它和 2021 的开放获取母体论文形成了一个很好的对照：

### 4.1 2021 开放获取母体论文：日/周频 MAX 更像 continuation
2021 *Financial Innovation* 那篇 paper 的核心结论是：

- 过去一个月里 `MAX` 更高的币；
- 下一周平均回报更高；
- `high MAX - low MAX` 的组合差约：
  - **raw spread = `3.03%/周`**
  - **risk-adjusted alpha = `1.99%/周`**

也就是：

> **日/周频看，最近打过大阳线的币，更像“继续强”。**

### 4.2 2025 intraday 版：past-hour MAX 反而更像短时 overvaluation
2025 这篇新 paper 则告诉你：

- 到了 **past-hour / `5m`** 这个更短尺度；
- 逻辑开始翻过去；
- **极端上冲更像短时被追价过头，而不是下一段还能继续当 winner。**

这对 desk 的价值很高，因为它不是又补了一个“MAX 效应存在”的老故事，而是补了更重要的一句：

> **MAX 不是单向信号，它可能是一个典型的 horizon router：慢一点看 continuation，快一点看 mean reversion。**

这正适合我们当前的短周期研究主线。

## 5. 为什么它比继续补一个 generic filter 更值得
先问一句：**这轮为什么不继续补 shared gate，而要补这个题？**

因为当前更缺的是：

1. **能独立站住的 raw alpha 素材**；
2. **不是 breakout / trend / basis 那几条老线重复变体的新横截面骨架**；
3. **能直接映射到 `5m/15m` 最小实验的 short-horizon mean reversion 方向。**

这篇 paper 满足这三条：

- 是 raw alpha，不是 overlay；
- 是 `cross-sectional / relative-value / mean reversion`，补当前素材池结构；
- 信号定义极简单，公共数据足够快就能做实验。

## 6. 本地 portability probe：在 Binance `5m/15m` perp 上，这条线还有没有交易价值？
本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_lottery_max_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_lottery_max_probe_series_2026-04-11.csv`

### 6.1 Probe 设定
- 标的：16 个 Binance USDⓈ-M 主流 perp
  - `BTC, ETH, SOL, XRP, BNB, ADA, DOGE, TRX, LINK, AVAX, DOT, LTC, BCH, NEAR, ATOM, APT`
- 数据：Binance 公共 `fapi/v1/klines`
- 样本长度：近 `60d`
- 两个版本：
  1. **`5m_1bar`**：过去 1 小时 `5m` MAX → 下一根 `5m`
  2. **`15m_1bar`**：过去 1 小时 `15m` MAX（4 根）→ 下一根 `15m`
- 做法：
  - 每个时点对全市场做横截面排序；
  - **做多低 MAX 桶，做空高 MAX 桶**；
  - 测 `top/bottom k = 2/3/4`；
  - 成本按 `turnover × {0, 0.25, 0.5, 1, 2} bp` 粗略打折。

这里的重点不是“精确复刻论文数值”，而是看：

> **把它压成短周期 perp 篮子后，它更像可执行 alpha，还是只剩学术 sign。**

### 6.2 结果先说结论
结论很清楚：

> **这条线在 `15m` 明显比 `5m` 更像活的，而且只能活在低成本版本里；一旦按 taker-ish `1bp` 粗打折，边大多被吃掉。**

### 6.3 这轮最值得记住的 6 个数
#### A. 论文原始结论
1. **2025 论文摘要：MAX 每升高 1 个标准差，后续收益约下降 `0.043%`。**

#### B. 本地 `15m` 版本
2. **`15m_1bar / k=4 / gross`：**
   - 平均 **`+0.811 bps / trade`**
   - 胜率 **`53.3%`**
   - 累计 **`+46.7%`**
   - 最大回撤 **`-18.1%`**
3. **`15m_1bar / k=4 / 0.25bp`：**
   - 平均 **`+0.517 bps / trade`**
   - 累计 **`+29.8%`**
4. **`15m_1bar / k=4 / 0.5bp`：**
   - 平均 **`+0.223 bps / trade`**
   - 累计 **`+12.9%`**
5. **但到 `1bp` 时，`15m_1bar / k=4` 已转负：**
   - 平均 **`-0.365 bps / trade`**
   - 累计 **`-21.0%`**

#### C. 本地 `5m` 版本
6. **`5m_1bar` 很脆：**
   - `k=4 / gross` 只有 **`+0.086 bps / trade`**
   - `0.25bp` 后已变成 **`-0.015 bps / trade`**

### 6.4 结果怎么翻成人话
这组 probe 最有用的地方，是把这条 alpha 的“活法边界”说清楚了：

- **alpha sign 是对的；**
- **`15m` 比 `5m` 更像第一落点；**
- **它不像 taker 横扫策略，更像低成本 / maker-ish 稀疏 market-neutral fade。**

也就是说，正确读法不是：

- 看到某币刚冲一根就裸空单币；
- 或者在 `5m` 上疯狂换仓追求极致频率；

更合理的读法是：

> **把它落成 `15m` 的 cross-sectional anti-lottery basket，再用低成本执行去保住边。**

## 7. 对当前 desk，最合理的策略骨架是什么
### 7.1 Universe
- 先固定高流动性 USDT perp 池：`top 12~20`
- 初版直接用这轮的 16 币池
- 后续再加 ADV、最小挂单深度、最小名义成交额过滤

### 7.2 Signal
每个 `15m` bar 收盘：

1. 对每个币算过去 4 根 `15m` 收益里的 **最大单根正收益**；
2. 在横截面里按这个 `MAX_1H` 排序；
3. **做多最低 `k` 个，做空最高 `k` 个**。

翻成人话就是：

- 最近 1 小时里**没怎么被追过**的，放 long 候选；
- 最近 1 小时里**被单根猛追过头**的，放 short 候选。

### 7.3 Entry / Exit
- `t` 收盘算信号
- `t+1` 整根 `15m` 持有
- 下一根收盘全部换仓

第一版不要一上来就加太多条件，先看 raw alpha 本体。

### 7.4 Sizing
- 每侧等权
- `k=4` 当前最稳
- gross 先固定在 `2x`
- 单币 cap 可设为组合资金 `10%~12%`

### 7.5 Risk
- 单币异常公告 / 合约异常 / 极端 funding 时段可 veto
- 横截面太集中到某一赛道时，加 sector cap
- 当天组合回撤超过阈值，暂停新开仓

### 7.6 Cost / Execution
这条线最关键的一句不是“有没有 alpha”，而是：

> **它必须活在低成本执行里。**

当前 probe 已经很明确：

- `0.25~0.5bp` 仍有活路；
- `1bp` 基本就被吃掉。

所以更合理的执行假设是：

- **post-only / maker-ish** 优先；
- 避免在刚冲完的极端 bar 末尾用 taker 扫进去；
- 可以配轻微延迟挂单 / spread-improvement / turnover veto。

## 8. 这轮最值得带回 desk 的，不只是 alpha 本体，还有一个很重要的“别混时间尺度”提醒
如果只看标题，很容易把 2021 和 2025 两篇都压成一句：

- “MAX effect 在 crypto 里成立。”

但这其实会误导 desk。

更准确的说法应该是：

- **慢频率 MAX：更像 continuation；**
- **快频率 MAX：更像 overvaluation fade。**

所以真正该研究的不是“MAX 到底是正还是负”，而是：

> **什么 horizon 下，MAX 从 continuation 翻成 mean reversion？**

这是一个非常有生产力的后续分支。

## 9. 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / market-neutral / mean reversion
- 基础 alpha：`long low past-hour MAX / short high past-hour MAX`
- regime：更适合短时冲高冲低比较分散、但不是全市场单边逼空的阶段
- filter / veto：重大新闻时段、单币公告、异常 funding、极端成交量离群
- risk / sizing / execution overlay：`k=4` 稀疏持仓、等权、gross cap、post-only 优先、turnover veto、最大赛道暴露约束

## 10. 为什么这轮我仍把“可直接落地完整策略”打成“是”
不是因为它已经证明自己能在保守 taker 成本下稳定赚钱，而是因为它已经具备完整策略最关键的 5 个部件：

1. **entry**：过去 1 小时 MAX 横截面极值
2. **exit**：固定下一根退出
3. **sizing**：每侧等权 / gross cap / 单币 cap
4. **risk**：news veto / sector cap / kill-switch
5. **cost**：明确知道必须压到 `0.25~0.5bp` 这一档，不能假装 taker 也能扛

所以它已经不是“只有因子没有壳”的主题，而是：

> **策略壳完整，但执行成本是主约束。**

## 11. 下一步怎么测（必须给）
### 第一优先：直接做 horizon router
并排跑：

- `5m signal -> next 5m`
- `5m signal -> next 15m`
- `15m signal -> next 15m`
- `15m signal -> next 30m / 45m`
- `1h signal -> next 1h`

目标：找出 **MAX 从 intraday fade 翻回 continuation 的时间分界点**。

### 第二优先：把“单根 MAX”扩成“top-k MAX”
测：

- `MAX1`：过去 1 小时最大单根正收益
- `MAX2/3`：过去 1 小时 top 2/3 正收益均值

看它更像：

- 单次冲高过热；
- 还是一串短时追价行为。

### 第三优先：加最少量的成本保护，不要先加花哨预测器
优先加：

- `spread / depth / maker fill feasibility`
- `turnover veto`
- `same-sector concentration cap`
- `skip top news bars`

而不是先上复杂 ML。

### 第四优先：和 2021 日频 MAX 做同族对照
同一个 universe，统一写成：

- `short-horizon MAX fade`
- `medium-horizon MAX continuation`

如果这两条都能站住，就能长成一个很有价值的 **MAX horizon router family**。

## 12. 一句话落地结论
> **这篇 2025 paper 最值得带回 desk 的，不是“彩票偏好”四个字，而是：过去 1 小时里冲得最离谱的币，在 `15m` 横截面里更像该淡化而不是该追；这条 `long low-MAX / short high-MAX` anti-lottery fade 在 Binance majors perp 上有 gross edge，但只能活在低成本执行里。**
