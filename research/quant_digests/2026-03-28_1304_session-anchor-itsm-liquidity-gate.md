# 别把这篇 2022 JFM 论文只读成股票开收盘现象：对 desk 更该先测的是「锚点后首段收益 → 下一段同向续动」raw alpha，再叠加低流动性 / 连续信息 gate

- 时间：2026-03-28 13:04 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/time-series/momentum/intraday/session-anchor/event-clock/continuation/liquidity-gate/information-discreteness/market-microstructure/btc/eth/alt/binance-perpetual/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2022 Journal of Financial Markets 开放获取 accepted PDF 全文 + Crossref 元数据 + Semantic Scholar 元数据
- 主题类型：raw alpha
- 基础 alpha：在有明确“锚点”的时段里，首段 `5m / 15m` 收益的方向，能预测下一段 `5m / 15m` 收益继续同向；低流动性、信息更连续时更强
- 是否可独立复现：是（用公开 Binance Futures `1m` K 线 / 成交 / 可选盘口代理即可做最小实验）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么

这次主看的是：

> **Zeming Li, Athanasios Sakkas, Andrew Urquhart (2022)**  
> **Intraday time series momentum: Global evidence and links to market characteristics**  
> *Journal of Financial Markets*

我把它选进来，不是因为它又给我们补了一层“可以拿来当 gate 的市场微结构解释”，而是因为它其实给了一个很干净的 **raw alpha 原型**：

> **某个有经济含义的时段锚点出现后，首段收益的方向，本身就能预测下一段收益继续同向。**

对论文原场景来说，这个锚点是股票市场的“开盘后前 30 分钟”和“收盘前最后 30 分钟”；对 crypto desk 来说，不该机械照抄成“日内开盘/收盘”，而应该翻译成：

- `00:00 UTC` 新日切换
- `08:00 / 16:00 UTC` funding 结算锚点
- `13:30 UTC` 美股现金开盘锚点
- 未来还可扩展到 CPI / FOMC / ETF 流量窗口等事件锚点

所以这篇东西真正值得先搬的，不是“股票也有 intraday momentum”这句废话，而是：

> **事件锚点后的首段同向续动，本身就可以作为可独立部署的短周期 raw alpha。**

这比继续补一篇纯 filter / pure explanation 更值钱，因为它天然能写成完整策略。

## 2. 论文里真正值得我们拿走的 headline

先把结果翻成人话：

> **市场在“开盘后第一段”形成的方向，不是立刻均值回归，而是有相当概率在“收盘前最后一段”继续走同向。**

论文用的是 **16 个发达市场股指** 的 **1 分钟数据**，样本期是 **2005-10-04 到 2017-12-29**，把每个交易日切成 30 分钟块，重点研究：

- `r_F`：开盘后前 30 分钟收益
- `r_L`：收盘前最后 30 分钟收益

核心预测回归非常简单：

- `r_L = α + β_F * r_F + ε`

几个最值得记的数字：

- **12 / 16** 个市场里，前 30 分钟对最后 30 分钟有显著正向预测力
- pooled regression 里，`β_F = 2.86`，`t = 7.53`
- 简单 market-timing 策略相对被动基准的年化 alpha 大约 **2.66% 到 7.45%**
- OOS 里，Clark-West `MSPE-adjusted` 在 **10 / 16** 个市场拒绝“没有预测力”
- forecast-encompassing test 在 **14 / 16** 个市场拒绝“历史均值已经包含了全部信息”

更关键的是，论文不是停在“有现象”就结束，而是往下给了两个非常 desk-friendly 的增强方向：

1. **低流动性时更强**  
   他们把市场按首段时窗里的流动性代理分组，发现 **低流动性组的 ITSM 收益几乎接近高流动性组的两倍**。

2. **信息更连续时更强**  
   他们用 `information discreteness (ID)` 去量化“第一段走势是一路平滑吸收，还是靠几根突然跳动冲出来”。结果是：**越像连续吸收、越不像离散跳变，后续续动越强。**

这两点很重要，因为它告诉我们：

- raw alpha 是真的存在
- 但它不是“任何首段上涨都无脑追”
- 真正强的是：**有锚点 + 首段已定向 + 流动性偏差/信息扩散机制支持**

## 3. 这篇东西的 base alpha 到底是什么

必须先回答用户指定的那句：

> **这篇东西的 base alpha 是什么？**

不是“流动性重要”。
也不是“连续信息更好”。
更不是“市场有时会趋势”。

真正的 base alpha 是：

> **锚点后首段价格方向，会在下一段继续同向扩散。**

也就是一个非常直接的短周期时间序列动量：

- 首段为正 → 下一段更偏多
- 首段为负 → 下一段更偏空

其中：

- **低流动性** 是增强器
- **连续信息吸收** 是增强器
- 它们都是 gate / filter
- 但 alpha 本体不是 gate，本体就是 **首段方向的后续同向续动**

所以这篇东西在我们的分类里，应当放在：

- **主标签：raw alpha**
- **附加可拆组件：liquidity gate / information-continuity gate**

这正好符合当前 desk 的优先级：

- 先补一个能独立部署的 raw alpha
- 再顺手带出两个后续可共享给别的 alpha 家族的 gate

## 4. 为什么它对 crypto 不是“硬凑”，而是能自然翻译

最大的反对意见很简单：

> 股票有开盘和收盘，crypto 24/7，怎么翻？

这里不能硬把“日内开盘/收盘”伪装成 crypto 自然结构；但也不能因此错过它真正可迁移的部分。

这篇论文可迁移的，不是“NYSE 有开盘铃”这个制度细节，而是：

> **当市场遇到一个会重新聚合订单流 / 风险预算 / 注意力的锚点时，首段价格发现不一定一次完成，而会向下一段继续扩散。**

crypto 里这样的锚点并不缺：

- `00:00 UTC`：新日、很多日频/风控/报表口径重置
- `08:00 / 16:00 UTC`：Binance / 主流 perp funding 节点
- `13:30 UTC`：美股现金开盘，macro / ETF / beta 风险偏好重新定价
- 大新闻发布时间：CPI、FOMC、NFP、SEC/ETF 事件窗口

所以对 crypto 最自然的翻译，不是“开盘前 30m / 收盘前 30m”，而是：

- 在某个**外生锚点**后观察第一段 `k` 分钟
- 用这段的方向去交易下一段 `h` 分钟
- 再用流动性与信息连续性做筛选

如果这能成立，它就不是一个图形学 breakout，也不是“看起来在涨就追”的口号，而是：

> **事件锚点驱动的短周期 time-series continuation alpha**

## 5. 我会怎么把它先落成 desk 可执行的完整策略

## 5.1 标的与时钟

先不要全宇宙乱扫，第一版直接做：

- 标的：`BTCUSDT perp`, `ETHUSDT perp`，再扩到 top 10~20 流动性 perp
- bar：`1m`
- 交易输出：`5m / 15m`
- 锚点先只保留最少 3 类：
  - `00:00 UTC`
  - `08:00 / 16:00 UTC` funding 节点
  - `13:30 UTC` 美股现金开盘

这样不会一开始就把自由度开爆。

## 5.2 信号定义

对每个锚点 `a`，定义：

- `r_F(a, k) = P(a+k) / P(a) - 1`
- `r_H(a, h) = P(a+k+h) / P(a+k) - 1`

先测最简单版本：

- `k ∈ {5m, 15m}`
- `h ∈ {5m, 15m, 30m}`
- `signal = sign(r_F)`

对应交易：

- `r_F > 0`：在第一段结束时做多下一段
- `r_F < 0`：在第一段结束时做空下一段
- `r_F ≈ 0`：不交易

这就是最裸的 raw alpha 版本。

## 5.3 Gate 1：低流动性增强

论文告诉我们，低流动性下这个 alpha 更强。crypto 最小实验里，不必执着完美 L2 depth，先用公开数据能快速做的代理：

- 方案 A：首段窗口内平均 `high-low / close`
- 方案 B：首段窗口内 `|return| / dollar volume`（Amihud-like）
- 方案 C：若你已经有盘口缓存，再补 quoted spread / top-of-book depth

第一版直接做分层：

- 只做流动性最差的 bottom tercile
- 或至少给 low-liq 样本单独算一层 PnL

如果 low-liq 明显优于全样本，就说明论文里的增强逻辑在 crypto 里也有可迁移性。

## 5.4 Gate 2：信息连续性增强

论文里用 `ID`（information discreteness）衡量“首段是平滑吸收，还是靠几次离散跳动冲出来”。

crypto 里可以直接做一个简化版：

- `pct_pos`：首段窗口里正收益 `1m` bar 的占比
- `pct_neg`：首段窗口里负收益 `1m` bar 的占比
- `ID = sign(r_F) * (pct_neg - pct_pos)`

解释：

- 若首段上涨，而且多数分钟都在小步上涨，`ID` 更低，代表信息更连续
- 若首段上涨只靠一两根大阳线，其余分钟杂乱，`ID` 更高，代表更离散

第一版就做：

- 只保留低 `ID`（连续吸收）样本
- 或至少比较 low-ID vs high-ID 两组的 hit rate / avg return

## 5.5 Entry / Exit / Sizing / Risk / Cost

为了满足“能直接落地完整策略”，初版可以写得非常朴素：

- **Entry**：锚点后第 `k` 分钟收盘入场
- **Direction**：`sign(r_F)`
- **Exit**：固定持有 `h` 分钟后平仓
- **Sizing**：`target_notional ∝ 1 / short-horizon realized vol`，并设单次事件 cap
- **Stop**：
  - 简单版：`0.8 ~ 1.0 x` 首段绝对振幅的反向止损
  - 更稳妥版：无盘中 stop，只做固定时间退出，避免被噪音洗掉
- **成本**：
  - baseline：round-trip taker `4 bps`
  - stress：round-trip taker `6 bps`
  - optimistic：maker entry + taker exit `2 bps`

第一轮不需要先搞复杂仓位管理。重点是：

> **这条 alpha 的毛边，到底在什么锚点、什么持有长度、什么 gate 下还活着。**

## 6. 对 `1m / 3m / 5m / 15m` 的真实关系

这篇论文原始设计是“前 30m → 后 30m”，所以它最自然映射到 crypto 的不是纯 `1m` 高频撮合，而是：

- **`5m / 15m` 最自然**：直接拿来做 formation / holding window
- **`1m / 3m` 不是不能做**，但更适合作为：
  - `5m / 15m` 主信号里的更细 entry timing
  - 或者在强锚点事件（CPI/FOMC/ETF 流量）下压缩版试验

也就是说：

- 如果你要一个能快测、又不至于完全被手续费吃掉的版本，先做 `5m/15m`
- 如果 `5m/15m` 跑出来有 pocket，再往 `1m/3m` 压缩

这比一上来就追 ultra-HFT 更符合当前 desk 的复现节奏。

## 7. 最小实验我建议怎么做

不要先做大而全。先做一个能在 1~2 天内给出 yes/no 的最小实验：

### 实验 A：anchor-only 裸 alpha

- 标的：`BTCUSDT perp`, `ETHUSDT perp`
- 样本：最近 `180 ~ 365` 天
- 锚点：`00:00`, `08:00`, `13:30`, `16:00 UTC`
- 形成窗：`5m`, `15m`
- 持有窗：`5m`, `15m`, `30m`
- 信号：`sign(r_F)`
- 成本：先扣 `4 bps`，再做 `6 bps` stress

输出：

- 每个锚点单独的 hit rate / avg bps / Sharpe / turnover
- `BTC` 与 `ETH` 分开看
- 全样本 vs 近 90 天滚动稳定性

### 实验 B：加 low-liq gate

在实验 A 的最佳 `(anchor, k, h)` 上，再加：

- 只做 low-liq tercile
- 对比 full sample / low-liq / high-liq

如果 low-liq 显著增强，就保留这条 gate。

### 实验 C：加 low-ID gate

再在最佳版本上比较：

- full sample
- low-ID（连续吸收）
- high-ID（离散跳动）

如果 low-ID 继续增强，就说明这篇论文最重要的第二层机制也能迁移。

### 实验 D：跨资产扩展

最后才扩到：

- `SOL`, `BNB`, `XRP`, `DOGE`, `ADA`
- 看 edge 是只属于大币，还是能外溢到高流动 alt

这一层若成立，就可以进一步做：

- 单资产 raw alpha
- 等权 basket
- 或横截面只交易最强/最弱首段冲击的 subset

## 8. 这条线最容易犯的错

有三个坑需要提前写清：

1. **把它误读成“只要涨了就追”**  
   错。它依赖的是“有锚点的首段价格发现”而不是任意时刻的短线冲高。

2. **把 gate 当 alpha 本体**  
   错。low-liq / low-ID 是增强器，不是本体。没有首段方向续动，本策略就不成立。

3. **在 crypto 里硬造假开盘/假收盘**  
   错。crypto 没有股票式开收盘，所以必须用 funding / cash-open / macro-event 这种真实锚点替代。

## 9. 为什么它值得现在进素材池

如果只从“是不是最新最花的 ML”看，这篇论文不算最炫。
但如果从当前 desk 的真实需要看，它非常对路：

- **base alpha 很清楚**：首段方向 → 下一段同向续动
- **可直接做完整策略**：entry/exit/sizing/risk/cost 都能写
- **和 5m / 15m 主线天然兼容**
- **还能顺手产出两个可复用 gate**：流动性、信息连续性
- **公开数据就能起步**，不用等 vendor

所以它不是“又一篇解释型 momentum 论文”，而是：

> **一个能被翻译成 crypto 事件锚点 continuation alpha 的原型，并且很适合先做最小实验。**

## 10. 下一步怎么测

如果只允许排一个最小复现实验，我建议直接排这个：

1. 用 Binance USDⓈ-M perpetual `1m` 数据抓 `BTC/ETH`
2. 只测 `13:30 UTC` 和 `08:00 / 16:00 UTC` 三类锚点
3. formation 先跑 `5m` 与 `15m`
4. holding 先跑 `5m` 与 `15m`
5. 先做裸 `sign(r_F)`，统一扣 `4 bps`
6. 如果任一 pocket 成立，再只加一个 gate：`low-liq`
7. 第二轮再加 `low-ID`

换句话说，先回答这个最关键的问题：

> **crypto 在“真实锚点后首段方向 → 下一段续动”这件事上，到底有没有净边？**

如果有，这条线就能进入：

- 独立 raw alpha 素材池
- funding / carry / breakout / cross-asset alpha 的 shared confirmation 层
- event-driven execution veto / size-up 模块

## 11. 来源与链接

### 主论文

- **Authors**: Zeming Li, Athanasios Sakkas, Andrew Urquhart
- **Year**: 2022（期刊版；accepted manuscript 可读）
- **Title**: *Intraday time series momentum: Global evidence and links to market characteristics*
- **Venue**: *Journal of Financial Markets*, Volume 57, Article 100619
- **DOI**: `https://doi.org/10.1016/j.finmar.2021.100619`
- **Readable URL**: `https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf`
- **Metadata URL**: `https://www.semanticscholar.org/paper/cee647f6b9ddd0d3a86d5f93dd0010f6f39bb696`
- **Repo URL**: 未找到官方公开 repo

### 地基论文

- **Authors**: Long Gao, Yufeng Han, Sophia Z. Li, Guofu Zhou
- **Year**: 2018
- **Title**: *Market intraday momentum*
- **Venue**: *Journal of Financial Economics*, Volume 129, Issue 2, Pages 394-414
- **DOI**: `https://doi.org/10.1016/j.jfineco.2018.05.009`
- **Readable URL**: `https://www.semanticscholar.org/paper/eb5931b46eb39831d053babe7bfed0f4687f0cea`
- **Repo URL**: 未找到官方公开 repo
