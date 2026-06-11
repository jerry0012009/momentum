# 别把 BTC 短周期均值回复继续写成 1h 教学图：这篇 2025 thesis 更该先测的是「BB oversold → middle-band exit」单币 raw alpha
- 时间：2026-03-31 00:28 UTC
- 类型：2025 Haaga-Helia University of Applied Sciences thesis 全文 PDF + 本地全文抽取 + 表格级结果复核
- 主题类型：raw alpha
- 基础 alpha：**BTC 在 intraday（至少 1h 级别）出现局部过度下跌后，价格有较高概率向其短窗均值回归；最直接的实现是 `close < lower Bollinger Band(20,2)` 做多，回到 `middle band` 平仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（原文是 long-only + 无杠杆 + 0.1% fee；desk 版需要补 short side、max-hold、止损与 perp 成本）
- 主题标签：raw-alpha/single-asset/mean-reversion/bollinger-bands/middle-band-exit/btc/hourly/intraday/5m/15m/1m/3m/paper/public-data/cost
- 证据类型：全文证据（thesis）+ 表格级结果复核 + desk 化迁移

## 1) 这次看了什么
主看这篇：

1. **Marja Ekström (2025). _Bitcoin trading performance evaluation: A comparative study of momentum and mean reversion strategies from 2020 to 2025_. Master’s thesis, Haaga-Helia University of Applied Sciences.**
   - Venue：Master of Business Administration thesis
   - DOI：**无 DOI（thesis）**
   - Readable URL：`https://www.theseus.fi/handle/10024/902903`
   - PDF URL：`https://www.theseus.fi/bitstream/handle/10024/902903/Ekstrom%20Marja.pdf?sequence=2`
   - Repo URL：**未提供**

先把 **base alpha** 说清楚：

> **这次主角不是 Bollinger Bands 这个指标本身，而是“BTC intraday oversold snapback” 这条单币 raw alpha：价格短时偏离均值过深时，会向中轨回归。**

一句话核心结论：

> **这篇材料最值得 intake 的，不是“均值回复和动量谁更好”的泛比较，而是一个可直接复现的完整策略骨架：`BB(20,2) 下轨跌破做多 → 回到中轨平仓`。**

一句话它是怎么证明的：

> **作者用 2020-10-31 到 2025-11-03 的 BTC/EUR 连续小时数据（43,916 根 1h bar），把 MA20/50 动量、BB(20,2) 均值回复和 HODL 放在同一套回测指标下对比，并额外显式扣了 0.1% 交易费。**

为什么这轮值得看它：
- 最近素材池里 pairs / cross-sectional / funding / options 已经很多，**单币 intraday mean reversion** 反而需要继续补一张“规则极简、成本明确、能直接 desk 化”的底层卡片；
- 它不是纯解释型论文，而是 **entry / exit / cost / trade count / exposure** 都给了；
- 虽然不是顶刊，但 **全文可读 + 口径完整 + 可直接复现**，比很多只能看到摘要的新论文更适合这轮快验证 intake。

## 2) 核心结论
先给四字段结论，不绕：
- **主题类型：raw alpha**
- **基础 alpha：BTC intraday oversold mean reversion**
- **是否可独立复现：是**
- **是否可直接落地完整策略：是**

最关键的 3 个数据点：
1. **小时级 BB 均值回复显著赢过同文动量与 HODL**：年化收益 **106.8%**、Sharpe **1.86**、最大回撤 **-35.6%**、Profit Factor **1.15**，而同样 1h 频率下 MA20/50 动量只有 **37.5% / 0.89 / -47.5% / 1.05**，HODL 是 **51.3% / 0.93 / -76% / 1.03**。
2. **加 0.1% 每笔手续费后，BB 线仍存活**：年化收益从 **106.8%** 降到 **74.8%**，Sharpe 从 **1.86** 降到 **1.48**，最终 1 万欧资金从 **382,096€** 回落到约 **221,000€**；但仍明显强于 momentum 与 HODL 的风险调整后结果。
3. **这条线的核心代价是高交易频率**：BB 策略在样本内共 **423 笔交易**，市场暴露仅 **26.6%**；同文 momentum 只有 **138 笔**、暴露 **52.3%**。也就是说，这条 alpha 不是 always-on trend，而是“少数过冲时刻下注、快速回吐出场”。

## 3) 为什么和当前 desk 直接相关
这轮它和当前 desk 的关系非常直接：

1. **它补的是 raw alpha 本体，不是 filter。**
   不是“波动大时谨慎”这类二层建议，而是一个可以直接写成交易规则的单币 MR 骨架。

2. **它给了完整策略闭环。**
   - entry：跌破下轨做多
   - exit：回到中轨平仓
   - sizing：全仓/固定资本（论文版）
   - cost：0.1% 每笔明确扣减
   - evaluation：年化收益、Sharpe、波动、Profit Factor、MDD 都有

3. **它补的是单币 intraday lane。**
   我们最近 intake 里，relative value / cross-sectional / pairs 很多；这篇更像一张“如果只做 BTC 单币，最简均值回复骨架该长什么样”的底层卡。

4. **它天然适合做 15m/5m transfer。**
   原文用 1h 证明“日频趋势 ≠ 小时级均值回复”；这正好支持我们继续问下一句：
   > **如果把时钟再压到 `15m/5m`，这条 oversold snapback 是变强、变弱，还是只在特定 regime 存活？**

## 3.5) 策略拆解（必填）
- 方向属性：**single-asset / mean reversion / long-only（论文原版）**
- 基础 alpha：**BTC intraday price overshoot 会向 rolling mean 回归**
- entry：
  - 计算 `BB(20,2)`；
  - 当收盘价 **跌破下轨** 时做多；
- exit：
  - 当价格 **重新上穿中轨（20-period moving average）** 时平仓；
- sizing：
  - 论文以固定 `10,000€` 初始资本全程回测；
  - 不使用杠杆，不做空；
- risk / veto：
  - 原文没有 stop-loss；
  - desk 版必须补：`max_hold`、单笔风险上限、趋势日 veto、极端波动熔断；
- cost：
  - 每次开/平仓按 **0.1%** 收费；
  - BB 策略样本内 **423 笔交易**，因此费损很敏感；
- 适配周期：
  - 论文直接证据在 **1h**；
  - desk 最值得先转的是 **15m baseline / 5m aggressive** 两个版本。

## 4) 论文里真正值得复现的部分
### 4.1 研究口径非常简单，但足够诚实
- 标的：**BTC/EUR**
- 交易所来源：**Gemini**（经 CryptoDataDownload 提供）
- 样本期：**2020-10-31 到 2025-11-03**
- 频率：**1h**（并另外聚合成 daily 做对照）
- 小时样本量：**43,916 根 bar**
- 日样本量：**1,829 根 bar**

这对 desk 的价值在于：
- 不需要稀缺链上/订单簿数据；
- 不需要黑箱模型；
- 只用公开 K 线就能先做一轮最小转译。

### 4.2 规则不是 headline 比较，而是两个非常可执行的 skeleton
论文同时测了两个策略：

#### 动量（对照组）
- `MA20 > MA50` 做多
- `MA20 < MA50` 清仓
- long-only

#### 均值回复（主角）
- `BB(20,2)`
- `close < lower band` 做多
- `close > middle band` 平仓
- long-only

这里最值钱的其实不是“Bollinger”三个字，而是它把 intraday MR 写成了一个**极简、低自由度、低过拟合风险**的策略定义。

### 4.3 论文给了一个很重要的频率分层结论
这篇最值得 desk 记住的话不是“均值回复永远比动量强”，而是：

> **BTC 在 daily 更像 trend / buy-and-hold 资产，在 hourly 更像 overshoot-revert 资产。**

这句话对我们有两个直接启发：
1. **不要把日频结论硬迁到 15m/5m。**
2. **同一个 alpha 是否成立，可能首先是 sampling interval 问题，而不是 feature engineering 问题。**

## 5) 关键实证结果
### 5.1 daily 和 hourly 的排序完全反转
#### daily 结果
- HODL：累计收益 **678%**，CAGR **32.65%**，年化波动 **49.21%**，Sharpe **0.82**，MDD **-73.39%**
- Momentum（MA20/50）：累计收益 **384.78%**，CAGR **24.28%**，年化波动 **35.63%**，Sharpe **0.79**，MDD **-38.40%**
- Mean reversion（BB）：累计收益 **-9.67%**，CAGR **-1.39%**，年化波动 **14.47%**，Sharpe **-0.02**，MDD **-39.43%**

翻成人话：
- **日频上别碰这条 BB 均值回复；**
- 日频 BTC 更像长期趋势/持有资产。

#### hourly 结果
- Momentum（MA）：年化收益 **37.5%**，波动 **50%**，Sharpe **0.89**，MDD **-47.5%**，Profit Factor **1.05**，最终 1 万欧变 **49,413€**
- Mean reversion（BB）：年化收益 **106.8%**，波动 **44.35%**，Sharpe **1.86**，MDD **-35.6%**，Profit Factor **1.15**，最终 1 万欧变 **382,096€**
- HODL：年化收益 **51.3%**，波动 **75.04%**，Sharpe **0.93**，MDD **-76%**，Profit Factor **1.03**，最终 1 万欧变 **79,792€**

翻成人话：
- **一旦切到小时级，BB oversold→mid-band exit 就不再是边角料，而是主策略。**
- 它不是因为“赚得最猛”才赢，而是 **赚得更快的同时，波动和回撤反而更低**。

### 5.2 费后结果依然支持继续做 first verdict
论文把 0.1% 手续费单独核算，结果很有用：
- BB：年化收益 **106.8% → 74.8%**，Sharpe **1.86 → 1.48**，最终资产 **382,096€ → ~221,000€**
- Momentum：年化收益 **37.5% → 30.2%**，最终资产 **49,413€ → ~42,300€**
- HODL：基本不变

这组数字的意义不是“费后依然超神”，而是：
- **这条线不是零成本幻觉；**
- 但它也确实说明，哪怕吃掉 42.3% 的累计费损估算，这个骨架仍有继续 desk transfer 的资格。

### 5.3 交易特征：高频率、低暴露、靠局部过冲吃饭
- Mean reversion：**423 笔交易**、市场暴露 **26.6%**、fee sensitivity = **High**
- Momentum：**138 笔交易**、市场暴露 **52.3%**、fee sensitivity = **Medium**
- HODL：**1 笔**、市场暴露 **100%**

这说明这条 alpha 的本质不是“长期看多 BTC”，而是：
> **多数时间空仓，等 BTC 跌出短期过冲后，赌回到均值的那一小段。**

## 6) 对 desk 最值得单独拎出来的 branch idea
如果只从这篇材料里挑一个最值得移植到 `1m/3m/5m/15m` 的分支，不是“继续比较 MA vs BB”，而是：

> **把 raw alpha 固定成 `oversold breach → middle-band snapback`，再把“趋势日 / 强单边日”降级成 veto，而不是反过来把 filter 写成主体。**

为什么？
- 论文已经告诉我们：**同一套简单规则，在 daily 会失败，在 hourly 会成功**；
- 这说明真正关键的不是又多叠几个指标，而是先把 **“在哪个 sampling interval、在哪种日内状态下做这条 MR”** 说清楚；
- 对 desk 来说，这比继续发明一个更复杂的 BB 变体更有价值。

所以我会把它拆成：
- **raw alpha 本体**：下轨跌破做多、回中轨平仓
- **第一优先级 shared gate / veto**：禁做强趋势日、禁做事件型单边扩散段

## 7) desk 化后的最小实验
### 7.1 baseline 先做 `15m`
第一轮不要急着上 `1m`，先做一个最诚实的 baseline：
- 标的：**BTCUSDT perp（Binance / OKX 至少一所）**
- bar：`15m`
- 信号：`BB(20,2)`
- entry：`close < lower band`
- exit：`close >= middle band`
- sizing：固定 notional 或 vol-target 小仓位
- risk：`max_hold = 8 bars`；`stop = 1.2~1.5 × band_width` 或近端 swing low；重大事件前后 veto
- cost：至少做 `2 / 4 / 6 bps one-way` 三档

这轮实验回答的问题很简单：
> **1h 看到的 oversold snapback，压到 15m 后还有没有净边？**

### 7.2 aggressive 版本再下探到 `5m`
如果 `15m` 还留边，再测：
- `5m` bar
- lookback 先保留 `20`
- 但额外要求：最近 `3~6` 根 bar 的累计跌幅达到某个分位，避免把普通噪音也算进 oversold
- exit 仍先用 middle-band，不要一上来就加太多花哨逻辑

### 7.3 先别急着对称化 short side
因为论文原始证据只支持 **long-only oversold bounce**。
所以 desk 第一轮更诚实的做法是：
- 先只测 long side；
- 等 long 侧站住后，再做 `upper band breach → mean exit` 的 short 对称试验；
- 不要在没有证据前，默认“上下都一样”。

## 8) 下一步怎么测（直接可执行）
1. **先复刻原规则到 BTC perp `15m`。** 不加新指标，先看最朴素 transfer 是否留下正的费后 Sharpe。  
2. **做 frequency ladder：`1h → 15m → 5m → 3m`。** 不要直接从 thesis 跳到 `1m`；先看 edge 是平滑衰减还是断崖消失。  
3. **加一个 trend-day veto 对照。** 例如当 `MA20 < MA50`（在更高一级时钟）或 `ADX/realized trend strength` 极高时，暂停 MR 入场。重点看它到底是在减少假信号，还是把真 alpha 也一起杀掉。  
4. **显式做 friction ladder。** 至少比较 `0 / 2 / 4 / 6 bps` one-way；若 `15m` 在 `4bps` 后已归零，就没必要继续往 `3m/1m` 深挖。  
5. **补 max-hold / stop-loss 版本。** 原论文没有 stop；desk 需要验证“中轨未回补时，哪种止损最少破坏期望值”。  
6. **测试事件避让。** CPI / FOMC / ETF headline / 大所事故等时段，把 MR 线单独隔离，看它是否只是正常流动性环境下成立。  
7. **最后才做对称 short。** 若 short side 不成立，就把它诚实地保留为“单边 long-only MR pocket”，不要强行对称化。

## 9) 风险与保留意见
- **来源不是顶刊，是 thesis。** 优点是全文和规则完整；缺点是外部审稿强度有限。  
- **只测 BTC/EUR 单一标的。** 不能自动外推出 ETH / SOL / 更小币。  
- **原文没有 slippage，只有 fee。** 这对短周期是明显乐观。  
- **原文是 spot long-only。** 我们真正关心的是 perp execution，资金费率、冲击成本和爆仓/杠杆约束都还没进来。  
- **1h 结果不能自动保证 5m/1m 成立。** 这正是下一轮要验证的核心。  
- **daily 直接失败。** 说明这条 alpha 非常依赖采样频率，不能被写成“BTC 天生均值回复”。

## 10) 来源
1. **Marja Ekström (2025). _Bitcoin trading performance evaluation: A comparative study of momentum and mean reversion strategies from 2020 to 2025_. Haaga-Helia University of Applied Sciences, Master’s thesis.**  
   - Venue：Master’s thesis  
   - DOI：无  
   - Readable URL：https://www.theseus.fi/handle/10024/902903  
   - PDF URL：https://www.theseus.fi/bitstream/handle/10024/902903/Ekstrom%20Marja.pdf?sequence=2  
   - Repo URL：无
2. **CryptoDataDownload dataset lineage (paper-described source).**  
   - Site URL：https://www.cryptodatadownload.com/
3. **Bollinger Band formula as stated in thesis.**  
   - `Upper = MA20 + 2 × σ20`  
   - `Lower = MA20 - 2 × σ20`

## 11) 本轮最短 takeaway
如果只记一句：

> **这篇材料最值得 desk 先复现的，不是“均值回复比动量强”这句口号，而是一条极简 raw alpha：`BTC 15m/5m 下轨跌破做多，回到中轨就走；趋势日先 veto。`**
