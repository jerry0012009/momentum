# 别把 abnormal-return 继续只当 event-clock：这篇 2020 FMPM 论文更该直接进素材池的是「异常日同向持有到收盘」完整 raw alpha
- 时间：2026-03-28 06:41 UTC
- 类型：论文 + follow-up 摘要交叉
- 主题标签：raw-alpha/event-driven/time-series/single-asset/abnormal-day/continuation/day-close/cumulative-return/threshold/liquid-majors/btc/eth/ltc/1m/3m/5m/15m/paper
- 证据类型：论文证据（主）+ 后续文献摘要交叉（辅）

- 主题类型：raw alpha
- 基础 alpha：当某个币在当天尚未收盘前，累计涨跌幅已经达到“异常日”阈值时，后续剩余时段更可能继续沿同方向走，而不是立刻反手；因此可做“异常日中途识别 → 同向持有到收盘”的事件驱动策略。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 为什么这轮值得写它
这篇不是新论文，但这次值得重写它的原因很直接：**它其实给的是一个能独立落地的 raw alpha，不只是一个 event-clock gate。**

前面几轮 intake 里，我们已经积累了很多 `gate / filter / overlay` 读法；如果再把这篇只读成“冲击后别追太久”，会继续强化 desk 现在偏多的确认层，而不是补充真正可复现、可单独回测、可单独放进素材池的事件驱动 alpha。对当前短周期研发来说，更值钱的读法是：

> **先定义异常日，再在异常日尚未结束时，顺着异常方向做到 day close。**

这件事的好处是：
- 它是 **单资产、单腿、低解释门槛** 的 raw alpha；
- `entry / exit / sizing / veto / cost` 都很好补齐；
- 可以直接映射到 `1m / 3m / 5m / 15m` 做最小实验；
- 还能自然接到我们后面已有的 `funding / liquidity / regime` 组件上做二次筛选。

## 2. 论文到底说了什么
主文献是：
- **Caporale, G. M., & Plastun, A. (2020). _Momentum effects in the cryptocurrency market after one-day abnormal returns_. Financial Markets and Portfolio Management, 34, 251–266.**
- DOI: `10.1007/s11408-020-00357-1`

论文用 `BTCUSD / ETHUSD / LTCUSD` 的小时数据研究：**如果某一天最终会成为“异常大涨日”或“异常大跌日”，在这一天还没结束之前，价格路径有没有可交易的提前识别性？**

作者的答案是：**有，而且最强的部分发生在“当天剩余时段”，不是次日。**

按文章摘要与正文摘录：
- 样本期：`2015-01-01 ~ 2019-09-01`（文末个别段落出现 `2017` 的字样，和摘要/方法段不一致，更像排版或文字失误；以摘要与方法段口径为主）。
- 频率：小时级。
- 标的：`BTC / ETH / LTC` 对美元。
- 异常阈值：动态阈值，文中写法为 BTC 约 `2σ`、ETH/LTC 约 `1.5σ`。
- 关键发现：**异常日当日，价格更倾向沿异常方向继续走；而“到次日继续 carry”明显弱得多，且部分情形反而转成 contrarian。**

这意味着对 desk 最该吸收的，不是“做个 event age gate 就完了”，而是：

> **异常日剩余时段本身，就是一个可以独立交易的 continuation alpha。**

## 3. 这篇东西的 base alpha 是什么
一句话版：

> **`cumulative intraday move 已经大到足以把今天推向 abnormal day` 这一事实，本身就是信号。**

把它翻成人话：
- 如果 BTC/ETH/LTC 当天中途已经涨/跌到一个“不是普通波动”的程度，
- 那么这往往不是“已经走完”的标志，
- 更像“今天就是趋势异常日，剩余时段继续沿方向漂”的标志。

所以它不是单纯的：
- 趋势跟随指标；
- breakout 形态确认；
- regime filter；

而是一个完整的 **event-driven directional alpha**：
1. 先识别“今天正在变成 abnormal day”；
2. 一旦识别，就按异常方向入场；
3. 核心收益段来自“从识别时点到 day close”这一段剩余路程。

## 4. 为什么它适合 1m / 3m / 5m / 15m desk
这篇论文原始频率是 `1h`，但它的结构特别容易降采样到更短周期：

### 4.1 信号不是靠复杂标签，而是靠“日内累计位移”
你只需要：
- 当日 open（或固定 UTC session open）
- 当前累计收益
- 一个 rolling 波动阈值

这比很多 minute-paper 更容易从公开交易所 K 线直接复现。

### 4.2 exit 非常清楚
最原始、最忠于论文 headline 的 exit 就一句：
- **持有到日终/会话终点**。

这对最小实验非常友好，因为不需要先发明很多复杂出场。

### 4.3 它天然适合后续叠加 desk 现有组件
这条 alpha 可以直接接上：
- `spread veto`：点差/冲击成本太高就不做；
- `funding veto`：perp 方向过贵时缩仓；
- `post-event timeout`：离收盘太近时不追；
- `liq filter`：只做最液的大币，避免把 tail coin 的反转口袋混进来。

## 5. 论文里最值得记住的 3 个数据点
先记这 3 个就够：

1. **同日 continuation 比次日 carry 更稳。**
   论文最有交易意义的发现不是“异常日之后几天怎么走”，而是“异常日本日剩余时段就已经能赚”。

2. **正异常日的当日顺势策略，在样本累计收益上很夸张。**
   论文给出的 Strategy 1（当日顺势）累计收益，正异常日大致达到：
   - BTC：`143.11%`
   - LTC：`311.39%`
   - ETH：`507.63%`
   这些数字显然不能直接照搬到今天的 perp 环境，但足够说明：**当日 continuation 才是主菜。**

3. **次日不是稳定延续，而是会开始分化。**
   论文明确提到，在 `BTC 正异常日` 与 `ETH 负异常日` 等情形里，次日甚至会出现 contrarian 倾向。也就是说：
   - **alpha 主体 = same-day continuation**
   - **next-day carry = 可选支线，不该当默认主交易段**

这点和后续文献是对得上的。比如 **Zaremba, Bilgin, Long, Mercik, & Szczygielski (2021, IRFA)** 的《_Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_》强调：crypto 的短期 continuation / reversal 很受流动性分层影响，不是所有币、所有时段都统一延续。对我们来说，这反而强化了今天的结论：

> **先把它收缩成“液体大币的异常日剩余时段 continuation”来做，别把它泛化成整个 cross-section 的全天候规则。**

## 6. 可直接落地的完整策略骨架
下面这版就是可以直接开做的最小可交易 skeleton。

### 6.1 Universe
先只做：
- `BTCUSDT perp`
- `ETHUSDT perp`
- 可选加 `SOLUSDT perp`

不要一开始就扩到全市场。这个题的第一阶段目标不是横截面扩容，而是确认**单资产异常日 continuation** 到底还活不活。

### 6.2 事件定义
在 `1m / 3m / 5m / 15m` 上都做一版，但先以 `5m` 为主：
- 定义会话：先用 `UTC 00:00 ~ 23:59`，因为最贴论文；
- 计算 `ret_from_open_t = close_t / open_day - 1`；
- 计算过去 `N=30~60` 天的日收益标准差 `σ_day`；
- 当 `|ret_from_open_t| >= k * σ_day` 时，判为“今天正在变成 abnormal day”；
- 初始先测：`k ∈ {1.25, 1.5, 1.75, 2.0}`。

### 6.3 Entry
- 若 `ret_from_open_t >= +kσ`：做多；
- 若 `ret_from_open_t <= -kσ`：做空；
- 仅允许在离日终还有至少 `M` 根 bar 时入场；
- 初始先测 `M ∈ {4, 8, 12}`（按当前周期换算）。

### 6.4 Exit
最小实验先只做 3 个 exit：
1. **day-close exit**：持有到 UTC 日终；
2. **time-stop exit**：持有 `H` 根 bar（如 `4/8/12` 根）后平；
3. **retrace exit**：若从事件后最高/最低点反拉超过 `x ATR` 则提前出。

但第一轮对照里，**day-close 必须是主基准**，因为这才是论文最核心、最少主观加工的出口。

### 6.5 Sizing
- 基础版：固定 notional；
- 第二版：按 `1 / intraday_vol` 逆波动缩放；
- 第三版：按事件强度 `|ret_from_open| / σ_day` 分层，但设 cap，避免极端消息日无限放大。

### 6.6 Risk / cost / veto
必须同时做：
- taker 版成本：`2~4 bps` 单边假设；
- maker/taker 混合版：更乐观但不能作为主结果；
- skip 条件：
  - 点差分位 > `p90`
  - 事件发生时资金费率/预期 funding 极端不利
  - 距离日终太近
  - 异常幅度过大（如 `>3σ_day`）但 order book 极薄

## 7. 下一步怎么测
这部分必须马上落地，不要停在摘要。

### 实验 A：单资产基准
- 标的：`BTCUSDT perp`
- 周期：`5m`
- 样本：最近 `365d`
- 规则：`ret_from_open` 触发 `kσ` 后同向持有到 UTC 日终
- 目标：看 **gross / fee-after / slippage-after** 是否仍保留正 expectancy

### 实验 B：周期迁移
把同一规则平移到：
- `1m`
- `3m`
- `15m`

目标不是挑最好看那个，而是回答：
- alpha 是更像 **越早捕捉越好**，还是
- 更像 **需要 5m/15m 降噪后才成立**。

### 实验 C：会话定义鲁棒性
并行测两种 session：
1. `UTC day`
2. `rolling 24h anchor every 4h`（更贴近 24/7 crypto）

如果只有固定 UTC 才有效，这条 alpha 更像“日历会话效应”；
如果 rolling anchor 也有效，说明它更接近真正的**事件 continuation**。

### 实验 D：加入一个 veto 就够
第一轮只加一个 veto：
- `spread / microstructure veto`

如果加这一层之后净值曲线明显更稳，就说明这条 alpha 的问题主要不在方向，而在执行。

## 8. 我现在对它的判断
我的判断是：**值得进素材池，而且优先级高于再补一个泛 gate。**

原因不是它“最新”，而是它满足当前 bot7 更关键的 4 个条件：
- base alpha 清楚；
- 能独立复现；
- 能直接拼成完整策略；
- 能快速映射到 `1m / 3m / 5m / 15m` 最小实验。

更重要的是，它帮我们补的是一块现在很缺的积木：

> **“异常日剩余时段 continuation”这种单资产事件 alpha**，正好处在 trend / breakout / shock-reaction 之间，既不是纯 breakout 形态，也不是纯均值回归。

这类信号如果活着，后面既能单独跑，也能给已有框架提供一个高解释性的事件腿。

## 9. 风险与保留意见
- 样本较老，且是现货环境；迁移到当下 perp 必须重做成本检验。
- 原论文不是为 2026 的资金费率/清算链/做市结构写的，所以不能把文中高累计收益直接当现实预期。
- 这条 alpha 很可能只在**液体大币 + 非极端拥挤时段**仍然成立；别一上来扩到小币。
- 如果实验发现“只有 very-early signal 有效、late-day 追价无效”，那它就会从完整 raw alpha 降级成 `event-start timing gate`。但这要由回测决定，不该先验假设。

## 10. 来源
1. **Caporale, G. M., & Plastun, A. (2020). _Momentum effects in the cryptocurrency market after one-day abnormal returns_. Financial Markets and Portfolio Management, 34, 251–266.**
   - DOI: https://doi.org/10.1007/s11408-020-00357-1
   - Readable URL: https://link.springer.com/article/10.1007/s11408-020-00357-1
   - PDF URL: https://link.springer.com/content/pdf/10.1007/s11408-020-00357-1.pdf
   - Repo URL: N/A（未见官方代码仓库）

2. **Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_. International Review of Financial Analysis, 78, 101908.**
   - DOI: https://doi.org/10.1016/j.irfa.2021.101908
   - Readable URL: https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002349.html
   - Repo URL: N/A（未见官方代码仓库）