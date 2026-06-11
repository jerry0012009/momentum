# 别把这份 2026 新 repo 只当“微观结构观察笔记”：对 short-cycle desk，更值得先测的是「US session window cross-sectional reversal」这条 raw alpha

- 时间：2026-04-01 02:26 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/mean-reversion/intraday/us-session/open-close-window/spot-crypto/binance/15m/30m/45m/60m/repo/public-data/cost
- 证据类型：2026 GitHub notebook source audit + Binance US 公共 `15m` spot kline 数据 + notebook 内交易成本/容量拆解 + 经典 intraday microstructure 论文引用

- 主题类型：raw alpha
- 基础 alpha：US equity session 开盘 / 收盘附近，crypto 横截面里**刚刚跑输的一篮子更容易在接下来 30~120 分钟回补、刚刚跑赢的一篮子更容易回落**，因此可做 `long recent losers / short recent winners` 的 dollar-neutral intraday reversal
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是 ETF，不是 overlay，也不是“美股开盘会影响 crypto”这种解释层。**

它的 alpha 本体很直接：
- 在固定的 US session 窗口里，先看一组币在最近 `30m` 的横截面收益排名；
- **做多最弱的一小撮、做空最强的一小撮**；
- 然后只持有接下来的 `30m ~ 120m`。

翻成人话：**这是一条“时段限定的横截面 intraday mean reversion”**，不是 filter。

## 2. 为什么这轮值得写，而不是继续补一个 pairs / funding 旁支
最近库里 pairs / funding / basis / carry 已经很厚；继续补当然没错，但边际信息增量在下降。相反，这份 2026 新 repo 补的是另一个还不算拥挤的 raw-alpha 口袋：

1. **它是完整策略，不是纯解释。** signal、hold window、分组方法、交易成本、容量分析都在 notebook 里给了。
2. **它跟 desk 的时间尺度天然兼容。** 主实验直接就是 Binance `15m`，并且 hold 只到后续 `30~120m`，非常适合 `5m/15m` 迁移。
3. **它顺手回答了一个很现实的问题：edge 死在 signal 不够，还是死在 cost/impact？** 这比只看 gross Sharpe 更值钱。

## 3. 这次看了什么
### 3.1 主来源（repo）
- **Author / Repo owner**：BNeillDickey
- **Year**：2026（repo 页面 2026-03 仍有更新）
- **Title / Repo**：*intraday-crypto-reversal-project*
- **Repo URL**：https://github.com/BNeillDickey/intraday-crypto-reversal-project
- **Readable URL**：https://github.com/BNeillDickey/intraday-crypto-reversal-project
- 关键文件：`Intraday_Crypto_Reversal_Project.ipynb`

### 3.2 repo 内引用的理论地基
1. **Heston, Korajczyk, & Sadka (2010). _Intraday Patterns in the Cross-Section of Stock Returns_. Journal of Finance, 65(4), 1369–1407.**
2. **Bogousslavsky, V. (2016). _Intraday Trading Patterns and the Role of the Systematic Risk Factors_. Review of Financial Studies, 29(7), 1912–1950.**
3. **Gao, Han, Li, & Zhou (2018). _Market Intraday Momentum_. Journal of Financial Economics, 129(2), 394–414.**

这些论文本身不是 crypto paper，但 repo 不是空口移植：它直接把思路搬到 Binance spot `15m` 数据上做了实证。

## 4. repo 里到底怎么定义这条 alpha
### 4.1 close-window 版本
- **Universe**：25 个 Binance spot 资产
- **信号窗**：`15:30–16:00 ET`
- **持有窗**：`16:15–17:00 ET`
- **方向**：横截面 reversal
  - long：这 `30m` 里最差的一组
  - short：这 `30m` 里最好的一组
- **分组**：默认 `10%` / `10%` 两端 decile
- **持仓**：dollar-neutral

### 4.2 morning-window 版本
- **信号窗**：`09:30–10:00 ET`
- **持有窗**：`10:15–10:45 ET`
- 其余做法相同

### 4.3 数据与过滤
- **价格频率**：Binance US `15m` spot klines
- **起始时间**：自 `2020-09-01`
- **流动性过滤**：30-day rolling ADV，默认最低 `1000 USD/day`
- **目的**：把已经“名义在 universe 里、实际上早就死流动性”的老币剔掉

## 5. 最值得拿走的硬数据点
### 5.1 close-window：gross signal 很强
repo 给出的 close-window 主结果：
- **Gross SR（test）**：`7.45`
- **Gross alpha**：约 **`24.0 bps/day`**
- 这说明 **signal 本体不是没有**，而且还不弱。

### 5.2 morning-window：同方向、而且几乎低相关
morning-window 结果：
- **Gross SR（test）**：`7.29`
- **Gross alpha**：约 **`22.8 bps/day`**
- 与 close-window 的日度 PnL 相关性只有 **`ρ = 0.121`**

这点很重要：它不是同一条 effect 换个时间重复讲，而更像是 **US 开盘与收盘两段不同机构流的两个 pocket**。

### 5.3 真正把它杀死的是 impact，不是 commission
close-window 的成本拆解最有价值：
- **gross alpha**：`24.0 bps/day`
- **commission**：`14.0 bps/day`
- **spread**：`7.4 bps/day`
- **impact**：**`97.0 bps/day`**
- **full-model total TC**：**`118.4 bps/day`**

repo 自己也给了很诚实的 waterfall：
- Zero TC：**SR `+7.45`**
- Commission only：**SR `+4.02`**
- Commission + Spread：**SR `+2.21`**
- Full model (+ Impact)：**SR `-24.22`**

翻成人话：
- **这条 alpha 不是“佣金一扣就没了”**；
- 它先是能活过 fee + spread；
- 真正把它打死的是 **中小币横截面组合在现实容量下的冲击成本**。

这比“净值为负”本身更重要，因为它告诉我们：**研究下一步应该盯 execution/capacity，不是先把 alpha 本体判死刑。**

## 6. 为什么这对当前 desk 仍然有研究价值
### 6.1 这条线属于可迁移的 raw alpha，而不是不可用的学术噪声
虽然 repo 在 spot 中小币上做出来的 full-cost 结果是负的，但它依然值得进研究池，因为：

1. **signal pocket 清楚**：
   - 只在固定时段出现；
   - 只持有短时间；
   - 方向明确是横截面 reversal。
2. **失败原因清楚**：
   - 不是 signal 不存在；
   - 是 impact 吃掉了 gross alpha。
3. **迁移路径清楚**：
   - 迁到更液体的 perp / maker-only / 更少 legs / 更低 participation；
   - 或者把它降成 portfolio sleeve，而不是独立放大器。

### 6.2 这比“继续卷同类 pairs 阈值”更像新 intake
当前 pairs 线上我们已经有很多：distance、cointegration、Hurst、copula、basket。相比之下，这条线补的是：
- **横截面 intraday reversal**
- **时间窗 pocket alpha**
- **US session flow transfer 到 crypto**

这三件事组合起来，对短周期 desk 是新增量。

## 7. 对 `1m / 3m / 5m / 15m` 的 desk 化读法
### 7.1 先别照抄整个 25 币 spot universe
repo 结果已经告诉我们：
- alpha 主要来自中小币；
- 但中小币的 impact 太贵；
- 大币单独拎出来，signal 会明显变弱。

所以 desk 化时不要直接复制“25 spot names + 10% tails + 全额轮动”。更诚实的 first pass 应该是：
- 先把 universe 限制在 **perp / 大中流动性币**；
- 同时把 notional / participation ratio 明确卡住；
- 用 maker / mixed execution 重新评估 net。

### 7.2 最适合的不是 1m 乱扫，而是 15m signal + 5m execution
我更倾向的 desk 迁移结构：
- **signal 计算**：`15m`
- **执行 / 滑点监控**：`1m` 或 `5m`
- **持有**：`30m ~ 120m`

原因：
- alpha 本体来自 session-window 的更慢 order-flow pocket；
- 不是逐根 `1m` micro alpha；
- 但 execution quality 的确要在更快层级上看。

### 7.3 这条线更像“低持仓占用的 sleeve”，不是全天主引擎
因为它天然只在几个固定窗口出手：
- US open pocket
- US close pocket

所以它更适合做：
- 一个 **时段限定 sleeve**；
- 或者接在现有 intraday 组合里当 **uncorrelated pocket**；
- 而不是硬写成 24/7 全天候 alpha。

## 8. 可以怎样落成完整策略骨架
### 8.1 Entry
在每个交易日固定窗口：
1. 取候选币池最近 `30m` 收益；
2. 做横截面排序；
3. long bottom tail，short top tail；
4. next bar / 下一个执行窗进场。

### 8.2 Exit
优先按时间退出，别过度拟合：
- close-window：持有 `30m / 45m / 60m / 90m / 120m` 做 sweep
- morning-window：同样做固定时长退出
- 不先加花哨止盈止损，先验证 alpha 是否稳定 survive cost

### 8.3 Sizing
建议 first pass 用最朴素的两层：
- **signal layer**：每侧 equal-weight
- **risk layer**：
  - 单币 notional cap
  - 单次总 gross cap
  - participation cap（例如不超过近 `x` 分钟 ADV 的 `y%`）

### 8.4 Risk / veto
这条线最值得加的不是新信号，而是三个风险约束：
1. **流动性 veto**：rolling ADV / top-of-book 深度不够时不做
2. **单边大趋势 veto**：若 beta / market mode 特别强，避免“反转”直接撞上趋势日
3. **事件 veto**：重大宏观/crypto 事件窗口附近 size-down 或禁开

### 8.5 Cost
必须至少跑三套：
- maker-only
- mixed
- taker-heavy

否则很容易重演 repo 里“gross 很漂亮，impact 一扣全没”的问题。

## 9. 我对这份 repo 的 desk 结论
### 9.1 值得 intake 的不是“spot 中小币可直接重仓做”
不是。repo 已经很诚实地说明：按它的容量假设，这条线在 spot 横截面上 **净值活不过 impact**。

### 9.2 真正值得 intake 的，是这条更窄的命题
**“US session 特定时间窗里，crypto 存在可重复的横截面 intraday reversal pocket；下一步要验证的不是它有没有，而是它在更液体 execution shell 下还能剩多少。”**

这就很适合当前 desk：
- raw alpha 清楚；
- 最小实验便宜；
- 失败也能快速知道失败在 signal 还是 cost。

## 10. 最小可复现实验（直接面向当前 desk）
### 实验 A：perp liquid-universe close-window reversal
- **标的池**：BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK, AVAX, LTC, BCH, DOT（按可交易性可缩）
- **市场**：同 venue perpetual
- **信号频率**：`15m`
- **信号窗**：`15:30–16:00 ET`
- **进场**：`16:00 ET` 后的首个可执行 bar（保守可用 `16:15 ET`）
- **持有**：先试 `30m / 45m / 60m / 90m`
- **组合**：long bottom `20%`，short top `20%`
- **成本**：maker / mixed / taker 三套
- **回答问题**：在更液体 perp shell 下，close-window reversal 能否至少 survive `commission + spread + realistic slippage`？

### 实验 B：morning-window reversal 独立验证
- **信号窗**：`09:30–10:00 ET`
- **持有**：`10:15–10:45 ET` 及延长版本到 `12:15 ET`
- **目的**：验证 open-pocket 是否仍与 close-pocket 低相关，是否值得做成第二条独立 sleeve

### 实验 C：15m signal + 5m execution overlay
- 信号还是按 `15m` 排名生成；
- 但执行时只在 `5m` 上满足 `spread / depth / impact budget` 才挂单；
- 对照“无 execution veto”的原始版本。

## 11. 下一步怎么测
**第一轮别急着做全宇宙，也别先卷参数。** 最实用的顺序是：

1. **先把 repo 原始定义迁到 perp liquid universe**
   - 保留：固定 session window、cross-sectional ranking、固定持有时长
   - 不保留：spot 中小币、过高 participation
2. **先只测两个 pocket**
   - `09:30–10:00 ET`
   - `15:30–16:00 ET`
3. **先只扫 4 个持有长度**
   - `30m / 45m / 60m / 90m`
4. **先冻结成本三档**
   - maker / mixed / taker
5. **若 gross 仍显著、且 maker/mixed 能活**
   - 再考虑加 regime veto（如单边趋势日禁做反转）
6. **若 gross 本身就塌**
   - 这条线直接降级，不继续浪费时间在 execution 微调上

一句话说：**先验证“更液体 shell 能不能救活它”，别先把时间花在更复杂的信号工程。**

## 12. 风险与局限
1. 主证据来自 **spot Binance 横截面**，不是 perp；
2. repo 的成本模型虽然诚实，但仍然是模型，不是逐笔成交回放；
3. 这类时段 alpha 可能受 regime 影响，例如 ETF / 宏观事件周期；
4. 若 universe 过小，横截面排序会退化成噪声；若 universe 过大，又容易把流动性黑洞带进来。

## 13. 一句话结论
这份 2026 repo 最值得 desk intake 的，不是“spot 中小币反转能直接赚钱”，而是：**US open/close 附近的 crypto 横截面里确实存在一条清楚的 intraday reversal raw alpha；下一步最该做的是把它迁到更液体的 perp / maker-friendly execution shell，看它能否从“gross alpha”升级成“after-cost alpha”。**

## 14. 来源链接
1. **BNeillDickey. (2026). _intraday-crypto-reversal-project_. GitHub repository.**  
   - Repo URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
2. **Heston, S., Korajczyk, R., & Sadka, R. (2010). _Intraday Patterns in the Cross-Section of Stock Returns_. Journal of Finance, 65(4), 1369–1407.**
3. **Bogousslavsky, V. (2016). _Intraday Trading Patterns and the Role of the Systematic Risk Factors_. Review of Financial Studies, 29(7), 1912–1950.**
4. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market Intraday Momentum_. Journal of Financial Economics, 129(2), 394–414.**

## 15. 文件与页面
- Digest：`research/quant_digests/2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`
- Page URL（build/publish 后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-01_0226_us-session-cross-sectional-reversal-alpha.html`
