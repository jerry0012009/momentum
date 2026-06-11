# 别把这篇 2021 liquidity-volatility 论文只读成“流动性风险解释”：对 short-cycle desk，更该先测的是「high illiq-vol + high illiq-level × alt-basket long-short」这条 raw alpha

- 时间：2026-04-11 14:43 UTC
- 类型：2021 *Finance Research Letters* 论文摘要（OpenAlex + Crossref）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**横截面上，最近一段时间里“流动性更不稳定、且整体更差”的币，后续 1 小时更容易拿到更高回报；可交易翻译是 `long high(liquidity-volatility + illiquidity-level) / short low(...)`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/relative-value/liquidity/illiquidity/liquidity-volatility/illiquidity-level/alt-basket/market-neutral/15m/1h/binance-perpetual/paper/abstract/public-data/cost/risk
- 证据类型：论文摘要 + 本地 public-data portability probe

## 1. 这次看了什么
主材料：

- **Thomas Leirvik (2021)**
- **Title:** *Cryptocurrency returns and the volatility of liquidity*
- **Venue:** *Finance Research Letters*, Volume 44
- **DOI:** `10.1016/j.frl.2021.102031`
- **Readable URL:** <https://doi.org/10.1016/j.frl.2021.102031>
- **Repo URL:** 无公开 repo

OpenAlex 摘要能稳定拿到的核心信息是：

> 作者在按市值计的前五大 crypto 上，记录到**流动性波动（volatility of liquidity）与预期收益总体显著正相关，而且这一关系明显时变**；同时，流动性水平与流动性波动大多负相关，因此**在流动性水平偏低时，回报更高**。

这轮最值得拿走的，不是“流动性风险也有溢价”这句大白话，而是一个更能给 desk 直接做实验的翻译：

> **别只盯着“流动性差”本身；更该盯着“流动性本来就差，而且还在剧烈波动”的那一侧。**

对短周期 desk，这句话可以被压成一个很直接的横截面 raw alpha：

- 用 `15m` bar 的公开数据先做一个 **illiquidity proxy**；
- 再分别看它的 **level** 和 **volatility**；
- 最后把两者合成一个横截面 score；
- 做 `long high score / short low score`。

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的：

> **liquidity-volatility premium / illiquidity-stress premium**。

翻成人话：

- 不是“过去涨得猛所以继续追”；
- 也不是“刚跌得狠所以抄反弹”；
- 而是看**谁的成交承接更差、而且这种差还不稳定**；
- 这类币在后续一段时间更可能给出更高的风险补偿。

如果把它写成交易语句，就是：

> **在横截面上，做多“高流动性波动 + 低流动性水平（等价于高 illiquidity level）”那一篮子，做空反方向那一篮子。**

所以它不是 filter，不是 overlay，本身就可以单独形成一个 cross-sectional long-short raw alpha。

## 3. 这篇 2021 论文真正给了什么
### 3.1 它的核心不是 liquidity level，而是 liquidity 的“波动”
很多人看到这类题目，第一反应会把它读成：

- 流动性差 -> 收益高；
- 或者 illiquidity premium 的老故事。

但这篇 paper 更关键的一层是：

> **作者看的不是静态流动性水平，而是流动性本身的波动。**

也就是：

- 市场不是简单分成“流动性好 / 不好”；
- 还要看这种流动性到底稳不稳；
- **越不稳定，投资者要求的补偿越高。**

这对 crypto 很重要，因为很多币的问题不是“长期都不 liquid”，而是：

> **有时能成交，有时突然抽干；平时看起来能做，真要换仓时深度却不在。**

这恰好更像短周期 desk 真正面对的风险。

### 3.2 作者给出的方向是正的：流动性波动越高，预期收益越高
OpenAlex 摘要的关键信息可以浓缩成一句：

> **volatility of liquidity 和 expected returns 整体显著正相关。**

也就是：

- 流动性越不稳定的币；
- 后续回报要求越高；
- 对交易上就是：**高 liquidity-vol bucket 并不一定是 veto，也可能是你真正该拿 risk premium 的地方。**

这很适合补当前素材池，因为我们已有不少：

- reversal
- OFI
- lead-lag
- pairs / basis / funding

但“**把 liquidity stress 本身当横截面 alpha**”这条线还不算拥挤。

### 3.3 摘要还额外给了一个很有生产力的二阶提示：level 和 volatility 要一起看
摘要里另一句很关键：

> **流动性水平和流动性波动大多负相关；当流动性水平低时，回报更高。**

这意味着对 desk 来说，真正值得优先测试的可能不是：

- 只看一个单变量 `vol(liquidity)`；

而是：

- **`vol(liquidity)` + `level(liquidity)` 的联合排序。**

翻成人话：

- **最有味道的，不是“流动性偶尔波动一下”的币；**
- **而是“本来就差，而且还很不稳定”的币。**

这也是我这轮 portability probe 里重点验证的版本。

## 4. 为什么这轮值得写，而不是继续补一个 generic filter
先问一句：为什么这轮还值得做，而不是继续写一个 overlay / regime？

因为这条线满足 3 个当前更稀缺的条件：

1. **它是 raw alpha，不只是 veto。**
2. **它服务的是 cross-sectional / relative-value book，能补当前素材池结构。**
3. **它能直接压到 `15m` + `1h` 的最小实验，不需要等低频外部数据。**

更重要的是，它提供的是一种和已有 reversal/OFI 很不同的抓手：

> **不是从价格路径本身找 edge，而是从“成交承接的脆弱性”找风险补偿。**

## 5. 本地 public-data portability probe：把论文的 daily idea 压成 `15m` 横截面实验
本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_series_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_universe_2026-04-11.txt`

### 5.1 Probe 设定
数据口径：

- 市场：Binance USDⓈ-M perpetual
- bar 频率：`15m`
- forward return：下一段 **`1h`（4 根 `15m`）** close-to-close return
- 价格数据：`fapi/v1/klines`
- 成交代理：每根 K 线自带 `quote volume`

代理变量：

- 先构造一个非常朴素的 **Amihud 风格 illiquidity proxy**：
  - `ILLIQ_t = abs(ret_t) / quote_volume_t`
- 再对每个币分别算：
  1. `lvl` = rolling mean of `log(ILLIQ)`
  2. `lv` = rolling std of `log(ILLIQ)`
- 横截面打分：
  - `score = z(lv) + z(lvl)`

也就是：

> **高 score = illiquidity 本来就高，而且这种 illiquidity 还在剧烈波动。**

组合做法：

- 每个时点按 score 排序
- **做多 top 20%，做空 bottom 20%**
- 持有未来 `1h`

### 5.2 为什么这个 proxy 虽然不等于原文 exact spec，但仍值得做
这里我没有硬装成“完全复刻论文”，而是做了一个 desk-friendly 的 public-data proxy。

原因很简单：

- 论文摘要告诉你的核心是 **方向关系**：`liquidity volatility ↑ -> expected return ↑`；
- 但短周期 desk 真正先要回答的是：
  - 这个关系能不能压到 `15m`？
  - 公开数据能不能先做第一轮 transfer check？

所以这轮 probe 的目标不是学术精确复刻，而是：

> **先看它能否长成一个可以继续打磨的 short-cycle raw alpha family。**

## 6. 结果先说结论：这条线更像“广义 alt-basket premium”，不是 majors-only alpha
### 6.1 broad universe：信号很干净
我先在一组更接近可交易 alt-basket 的 universe 上测：

- **`top25_30d_quotevol`**
- 规则：USDT perp、上市超过 30 天、按 24h quote volume 取前 25

结果很直白：

#### `top25_30d_quotevol`
- **24h window**：
  - long-short 平均 **`+12.44 bps / 1h`**
  - `t ≈ 4.42`
  - 胜率 **`54.4%`**
- **3d window**：
  - long-short 平均 **`+28.88 bps / 1h`**
  - `t ≈ 7.53`
  - 胜率 **`57.4%`**
- **7d window**：
  - long-short 平均 **`+34.76 bps / 1h`**
  - `t ≈ 5.09`
  - 胜率 **`57.9%`**

翻成人话：

> **在更广一点、允许 alt 进入的 perp universe 里，这条 `high illiq-vol + high illiq-level` 横截面书不是贴地噪声，而是相当像一个活的 risk-premium factor。**

而且一个很有意思的现象是：

- **3d / 7d 窗口明显比 24h 更强**。

这意味着它可能不是“超高频瞬时冲击”类信号，而更像：

> **一种需要几天滚动窗口才能稳定识别的流动性压力溢价。**

### 6.2 majors12：几乎没边
我再把 universe 缩到更 desk 常用的 majors12：

- `BTC, ETH, SOL, BNB, XRP, DOGE, ADA, AVAX, LINK, SUI, ARB, WLD`

结果几乎消失：

#### `majors12`
- **24h**：`+0.09 bps / 1h`，`t ≈ 0.08`
- **3d**：`+0.38 bps / 1h`，`t ≈ 0.31`
- **7d**：`+1.44 bps / 1h`，`t ≈ 0.90`

也就是：

> **这条线不是一个“拿大币就能做”的主流 perp alpha。**

它更像：

- **广义 alt-basket** 的横截面风险补偿；
- 不太像 **BTC/ETH/SOL 这种 majors-only** 的日常轮动信号。

## 7. 这组结果怎么翻成人话
这轮最重要的，不是“paper 方向对了”这么简单，而是多了两个更实用的 desk 结论：

### 7.1 单看 liquidity volatility 不够，和 level 合起来才像 alpha
如果只看 `vol(log ILLIQ)`，first-pass 结果并不够干净；

真正变得像样，是在做：

- `z(liquidity-volatility)`
- **加上** `z(illiquidity-level)`

以后。

所以对 desk 来说，更好的读法不是：

> “流动性波动高 -> 买。”

而是：

> **“承接本来就差，而且还越来越不稳”的那一侧，更值得要求风险补偿。**

### 7.2 这条线更像 alt stress premium，不像 majors router
如果你把它理解成“给 BTC/ETH/SOL 做一个 universal filter”，大概率会失望。

更合理的理解是：

- 这是 **broad alt perp cross-section** 的风险溢价抓手；
- 不是 **majors-only** 的主信号。

这很重要，因为它直接决定了后续该往哪条 lane 走：

- **该去做 alt-basket 相对价值书；**
- 不是把它硬塞进 BTC/ETH 主盘内核。

## 8. 对当前 desk，更合理的策略骨架是什么
### 8.1 Universe
第一版不要用 majors-only。

更合理的是：

- Binance USDⓈ-M USDT perp
- 上市 > 30 天
- 24h quote volume 排名前 20~30
- 再叠加最小 ADV / 最小成交笔数 / funding 异常过滤

### 8.2 Signal
每个 `15m` bar：

1. 算 `ILLIQ_t = abs(ret_t) / quote_volume_t`
2. 对每个币滚动算：
   - `lvl = mean(log ILLIQ)`
   - `lv = std(log ILLIQ)`
3. 横截面 z-score 后合成：
   - `score = z(lv) + z(lvl)`
4. **long top bucket / short bottom bucket**

### 8.3 Entry / Exit
- `t` 收盘算 rank
- `t+1` 开始持有未来 **`1h`**
- 每 `15m` 滚动更新；也可以先做 staggered book

### 8.4 Sizing
- 每侧等权
- 单币 notional cap
- 赛道集中度 cap
- 先做 market-neutral gross，别急着加方向暴露

### 8.5 Risk / Cost
这条线虽然是 raw alpha，但它的风险也非常显然：

- 它天然偏向 **更差、更不稳流动性** 的币；
- 所以最怕两件事：
  1. **真实成交冲击比 proxy 想象得大**
  2. **极端事件 bar 把篮子变成脆弱小币拥挤仓位**

所以至少要补：

- 最小成交额/挂单深度过滤
- 新币/异常公告 veto
- 单赛道 cap
- 单币 cap
- 成交成本 stress

## 9. 为什么这轮我把“可直接落地完整策略”打成“否”
不是因为它没有 signal，而是因为它目前更像：

> **一个方向清楚、transfer 也通过了的 raw alpha 候选。**

还没到“完整策略可直接上线”的原因有三个：

1. **exact paper spec 还没完全从正文恢复到逐公式级别**；
2. **当前强边主要出现在 broad alt universe，不是 majors universe**；
3. **它天然吃流动性风险，所以成本/容量/滑点约束会很重要。**

所以现在最好的定位不是“成品策略”，而是：

> **值得进入复现池的 alt-basket cross-sectional alpha family。**

## 10. 下一步怎么测（必须给）
### 第一优先：把 `quote-volume proxy` 升级成更像真实流动性的指标
并排跑：

- `abs(ret) / quote_volume`（当前 proxy）
- Corwin-Schultz / high-low spread proxy
- top-of-book spread / depth proxy
- taker buy imbalance 联合 proxy

目标：确认 edge 是真的来自 liquidity stress，而不是 volume/volatility 混淆。

### 第二优先：把持有期从 `1h` 展开成 horizon surface
至少并排跑：

- next `15m`
- next `30m`
- next `1h`
- next `2h`

看这条 premium 更像：

- 需要一点 carry 时间去兑现；
- 还是短窗口就被抢光。

### 第三优先：拆 universe，别把 majors 和 alts 混为一谈
至少分 3 桶：

- majors
- liquid alts
- tail alts

目标：找清楚这条线真正活在哪一层，而不是拿全市场平均掩盖结构差异。

### 第四优先：把 score 从简单相加升级成更稳的 joint ranking
可以试：

- `score = z(lv) + z(lvl)`
- 双排序（先按 level 分桶，再按 volatility 排）
- 交互项 `lv * lvl`
- 和 funding / OI / sector-neutralization 联合

目标：判断它到底是独立 premium，还是更适合作为 alt-basket admission layer。

## 11. 一句话落地结论
> **这篇 2021 FRL paper 真正值得带回 desk 的，不是“流动性风险有溢价”这句空话，而是：在更广的 alt perp 横截面里，`高 illiquidity 波动 + 高 illiquidity 水平` 这类名字，后续 `1h` 确实更容易给出更高回报；但这条线几乎不属于 majors-only，更像一个 broad-alt cross-sectional raw alpha 候选。**
