# 别把这篇 2025 动量论文只读成“vol-managed”：对 desk 更该先测的是「XS momentum × short-leg single-name jump veto」完整 raw alpha
- 时间：2026-03-29 20:11 UTC
- 类型：2025 *Financial Markets and Portfolio Management* 开放获取全文 PDF + Binance USDⓈ-M Perpetual 公共 `15m` transfer check
- 主题类型：raw alpha
- 基础 alpha：**横截面动量（cross-sectional momentum）**——做多近期相对强的币、做空近期相对弱的币；这篇 paper 对 desk 最值钱的旁支不是“动量有效”本身，而是 **短腿里单个币的极端上跳，会把整条 alpha 直接打穿**，所以需要把 `single-name short-jump veto / cap` 单独当成完整策略组件来测。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/large-cap/long-short/short-leg-crash/jump-veto/inverse-volatility/volatility-managed/binance/perpetual/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：全文论文证据 + 本地表格抽取 + Binance perp 最小 transfer check

## 1. 这次看了什么
看的是 **Klaus Grobys, James W. Kolari, Davide Sandretto, Syed Jawad H. Shahzad, Janne Äijö (2025)** 的 *Cryptocurrency momentum has (not) its moments*。

先把 **base alpha** 说清楚：

> **这不是纯风控论文。alpha 本体就是大市值 crypto 的横截面动量：多最近 1 个月涨得最好的 quintile，空最近 1 个月最差的 quintile，周频持有、等权再平衡。**

这篇最值得 desk intake 的，不是 headline 式地说“volatility management 有用”，而是更具体的一句：

> **crypto XS momentum 很容易被 short leg 里单个币的暴涨打穿；所以真正该先搬进短周期实验的，是 `raw alpha + single-name short-jump control`，而不是先把它当成一个笼统的 vol-scaling 话题。**

一句话核心结论：

> **大市值 crypto 的 XS momentum 不是完全没 alpha，而是收益常常被极少数 short-side jump 事件主导；去掉最极端单点或加风险缩放后，收益会明显变样。**

一句话它怎么证明：

> **作者用 2016-2023 的 top-30 大市值 crypto、按月度 formation + 周度持有构建 long-short 动量组合，再比较原始收益、trimmed 收益、vol-managed 收益以及 tail exponent。**

## 2. 核心结论
### 2.1 原始 raw alpha 不是“没有”，而是被尾部事件盖住了
论文口径：
- universe：**按市值选 top 30 crypto**
- formation：**过去 1 个月收益**
- skip：**1 个交易日**
- hold：**1 周**
- 组合：**多 winners quintile，空 losers quintile，双边等权**
- 样本：**2016-01 ~ 2023-12，共 416 个周观测**

原始结果非常说明问题：
- **全样本 raw momentum = `0.90%/周`，t = `1.06`，不显著**
- **2016-01 ~ 2020-07 子样本 = `1.74%/周`，t = `1.85`**
- **2020-08 ~ 2023-12 子样本 = `-0.19%/周`，t = `-0.13`**

翻成人话：
- 你如果只看全样本，会得出“这条 alpha 不太行”；
- 但 paper 继续往下拆后发现，问题不一定是动量完全不存在，而是 **尾部结构把均值污染得很严重**。

### 2.2 真正把组合打穿的，是 short leg 里的单币爆拉
最关键的数字在这里：
- **2020 年 12 月出现一次 `-255.28%` 的 momentum crash**
- 论文明确写到：这个 crash **不是典型 equity momentum 那种市场反转型 crash**
- 而是 **short leg 里单个币暴涨** 导致
- 具体例子：**Mindol (MIN)** 在 **2020-12-23** 从 **`0.54 USD` 涨到 `7.86 USD`**，单日级别约 **`+1400%`**

因为组合双边都只有少量等权名字，这种事件会直接把 short leg 炸穿。

这正是这篇 paper 对短周期 desk 最有价值的地方：

> **crypto 的 XS momentum，失效形态不一定是“因子均值回归”，而可能只是“单个弱币在你做空时发生离散跳涨”。**

### 2.3 去掉极端点后，alpha 长得完全不一样
作者做了三种 trimming：
- `5%-95%` 缩尾
- `1%-99%` 缩尾
- 只去掉 **绝对值最大** 的单个观测

结果：
- `5%-95%` trimming 后，均值 **`1.33%/周`**，t = **`3.94`**
- `1%-99%` trimming 后，均值 **`1.47%/周`**，t = **`3.23`**
- 只去掉最大单点后，均值 **`1.51%/周`**，t = **`2.63`**

也就是说：

> **这条 raw alpha 不是“平均上不赚钱”，而是“少数极端 short-jump 把平均值扭坏了”。**

### 2.4 vol management 能改善，但没有消灭尾部问题
作者按 Barroso-Santa-Clara 风格做波动率缩放（target vol `c=10`）：
- **4 周滚动波动率**：`2.40%/周`，t = `1.81`
- **8 周滚动波动率**：`1.86%/周`，t = `2.09`
- **12 周滚动波动率**：`1.33%/周`，t = `1.45`

风险调整后（控制 crypto market factor + plain momentum factor）：
- alpha 约 **`1.69%/周`**，t = **`2.32`**
- alpha 约 **`1.32%/周`**，t = **`3.21`**
- alpha 约 **`0.76%/周`**，t = **`2.00`**

但 paper 也提醒一个重要保留：
- plain momentum 的 kurtosis 非常高（约 **`123.48`**）
- vol-managed 版本虽然下降，但仍然很厚尾（约 **`68~106`**）
- 作者估计的 **power-law exponent 接近 `3`**，意味着 **方差层面仍接近“统计上不稳定”的边缘**

所以更稳的读法不是“vol scaling 解决了一切”，而是：

> **先承认 short-leg jump 是主风险源，再决定用 veto、cap 还是 inverse-vol 去减它。**

## 3. 为什么和当前项目直接相关
这轮最该回答的问题是：

> **它为什么比继续补一个别的 filter 更值得？**

因为它仍然是 **raw alpha**，而且是 **完整策略骨架**：
- 有明确 entry：过去窗口的横截面强弱排序
- 有明确 exit：下次 rebalance 或持有到期
- 有明确 sizing：双边等权 / inverse-vol
- 有明确 risk：trim / veto / cap / vol scaling
- 有明确 cost：换手、双边再平衡、short-side blow-up

对当前 desk，它的意义有两层：
1. **补 raw alpha 素材池**：不再只围绕 breakout / continuation，而是补一个更标准的 `cross-sectional long-short` 母体；
2. **补 live 组件拆解**：告诉我们 crypto XS momentum 里，最该优先工程化的可能不是“更多信号”，而是 **short basket 的单名额外约束**。

## 3.5 策略拆解（必填）
- 方向属性：**横截面 / long-short / relative-strength**
- 基础 alpha：**做多近期相对强势币，做空近期相对弱势币**
- regime：**更适合有分化而非全面同步挤压的市场；若全市场单边 squeeze，short leg 风险显著放大**
- filter / veto：**对 short 候选加入 single-name jump veto / listing-age veto / abnormal-news veto / recent squeeze veto**
- risk / sizing / execution overlay：**per-name short cap、inverse-vol scaling、gross leverage cap、事件窗口 blackout、分层成本假设**

## 4. Binance USDⓈ-M Perpetual 公共 `15m` transfer check
我补了一个**很轻的 desk proxy**。先说明：

> **这不是论文周频口径的硬复刻，而是看“这篇 paper 最值得搬的 lesson，到了我们 15m desk 上是不是立刻有感觉”。**

### 4.1 proxy 口径
- 数据：Binance USDⓈ-M Perpetual 公共 `15m` klines
- 样本：**2026-02-26 22:30 UTC ~ 2026-03-29 19:15 UTC**
- universe：`BTC ETH SOL XRP BNB DOGE ADA LINK LTC AVAX TRX SUI APT ARB 1000PEPE`
- 信号：过去 **32 根 `15m` bar（8 小时）** 横截面动量排序
- 组合：多 top 3，空 bottom 3，持有未来 **4 根 bar（1 小时）**
- 成本：粗略按每次换仓 **`8 bps`** 总成本
- 额外测试：对 short leg 加一个很粗的 jump veto（若候选短腿在最近 `1 bar > +6%` 或 `4 bars > +12%`，则不纳入 short）

### 4.2 proxy 结果
粗看结果并不好：
- base 版本平均 **约 `-10.0 bps/次`**
- hit rate **约 `36.9%`**
- 我设的这版 short-jump veto **触发次数 = `0`**
- 单次最差的 short-name 未来 1 小时贡献可到 **约 `-627.9 bps`**

这组结果最有价值的地方反而是负面信息：

> **在 liquid-major `15m` perp 口径里，这篇 paper 的 raw alpha 不能直接平移成现成 pocket；而且我这版“只抓极端跳涨”的 veto 还不够细，没抓到造成坏交易的 short-side squeeze。**

所以这篇 paper 对 desk 的更合理定位是：
- **值得进入 raw-alpha 素材池**；
- 但第一落点不该是“major-perp 直接交易版”；
- 更该先去 **更宽的 liquid-alt universe** 测：
  - short-name jump veto
  - per-name short cap
  - inverse-vol sizing
  - 最近上新 / 叙事币 / 高 squeeze 币剔除

## 5. 下一步怎么测
### 最小可复现实验（建议直接开做）
**目标：验证 crypto XS momentum 的亏损，是否主要集中在 short leg 的 single-name squeeze。**

#### 实验 A：raw alpha baseline
- universe：Binance/OKX perpetual，先做 **30~60 个非稳定币、流动性合格合约**
- bar：`15m` 为主，`5m` 做执行映射
- formation：`32 / 64 / 96` bars
- hold：`4 / 8 / 16` bars
- 组合：多 top decile / 空 bottom decile，双边等权
- 成本：`4 / 8 / 12 bps` friction ladder

#### 实验 B：short-leg jump control
在 baseline 上只改一个东西：
- 若某个候选 short 名称满足以下任一条件，则 veto 或降权：
  - 最近 `1~4` bar 出现 `q95` 以上单边上跳
  - 最近 `N` bar funding / basis / OI squeeze 异常
  - 上线年龄太短 / 流动性不稳 / 新闻事件窗口

比较：
- mean / median return
- hit rate
- 正收益日占比
- 最差单笔 / 最差单名贡献
- **PnL 是否更不集中在单个 short outlier**

#### 实验 C：cap vs veto vs inverse-vol
同一套 raw alpha，平行比较：
1. plain equal-weight
2. short-name cap（单名最大权重上限）
3. short-jump veto
4. inverse-vol cross-sectional sizing
5. `veto + inverse-vol`

如果 `5m/15m` 上出现“收益差不多，但 tail 明显变浅”，这篇 paper 就算对 desk 真正有用了。

## 6. 风险与保留意见
- 论文主样本是 **周频 / top-30 大市值 / 2016-2023**，不是我们要直接交易的 `5m/15m` perp 口径。
- 这篇 paper 没有给出短周期现成可抄参数；它给的是 **风险形态**，不是 turnkey intraday recipe。
- 我这次的 `15m` proxy 只是 transfer check，不是完整无重叠严谨回测。
- 目前证据更支持把它 intake 成：
  - **raw alpha 母体：XS momentum**
  - **关键风险模块：short-leg single-name jump control**
  而不是“major-perp 已验证 pocket”。

## 7. 来源与落地线索
1. **Grobys, Klaus; Kolari, James W.; Sandretto, Davide; Shahzad, Syed Jawad H.; Äijö, Janne (2025)**  
   *Cryptocurrency momentum has (not) its moments*  
   Venue: *Financial Markets and Portfolio Management*  
   DOI: <https://doi.org/10.1007/s11408-025-00474-9>  
   Readable URL: <https://link.springer.com/article/10.1007/s11408-025-00474-9>  
   PDF URL: <https://link.springer.com/content/pdf/10.1007/s11408-025-00474-9.pdf>  
   Repo URL: N/A（论文未提供官方代码仓库）

2. Binance USDⓈ-M Perpetual public klines  
   API docs: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
