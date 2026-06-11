# 别把这篇 Hegic 论文只读成 AMM 定价诊断：对 short-cycle desk，更该先测的是「on-chain option quote-vs-benchmark residual fade × delta-aware hedge」这条 raw alpha
- 时间：2026-04-13 05:08 UTC
- 类型：2025 arXiv / paper full text
- 主题类型：raw alpha
- 基础 alpha：链上期权 AMM 的 `option ask / quoted premium` 若系统性低于一个更稳健的模型基准价（论文里用 `Black-Scholes + two-regime MS-AR-(GJR)-GARCH volatility`），就可以把“**quote-vs-benchmark residual 回补**”当成一条可交易的 relative-value alpha；最直接的 desk 版是 `long underpriced option + delta hedge`，赚 residual 压缩而不是赌纯方向。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：options / on-chain / relative-value / stat-arb / AMM / Hegic / Arbitrum / wBTC / ETH / delta-hedge / mispricing
- 证据类型：论文全文（arXiv abstract + PDF）

## 1. 先回答：这篇东西的 base alpha 是什么？
**base alpha = `链上期权报价相对模型基准价的可交易错价回补`。**

不是“DeFi 期权挺有意思”，也不是“AMM 定价需要校准”，而是更直接的：
- 先给每张链上期权一个外部基准价；
- 再看 Hegic 的实际 quote 相对这个基准是不是**持续偏便宜**；
- 若偏离足够大，就做 `long option + delta hedge`，等 residual 回补或到期兑现。

所以它属于 **raw alpha / relative-value / stat-arb**，不是 filter / regime / overlay。

---

## 2. 这次看了什么
这次看的是 **Anastasiia Zbandut (2025)** 的 arXiv 论文：
**_Pricing of wrapped Bitcoin and Ethereum on-chain options_**。

论文表面在做的是 **Hegic on-chain options 的定价诊断**：
- 样本：**Arbitrum 上 Hegic 的 wBTC / ETH 期权**；
- 时间：**2022-10-24 到 2024-05-21**；
- 对照：`Black-Scholes`，但波动率不是随便塞个常数，而是用 **two-regime MS-AR-(GJR)-GARCH**；
- 目标：解释为什么链上 AMM quote 会和 benchmark price 偏离。

但对我们 desk 来说，真正值得 intake 的不是“AMM 校准建议”，而是：
> 这篇论文已经把 **链上期权 quote 偏离外部 fair value** 这件事做成了一个可量化的 residual；而 residual 本身，就是一条可被短周期监控和执行的 raw relative-value alpha 候选。

---

## 3. 核心结论
### 3.1 一句话结论
**这篇论文最值得 desk 先测的，不是 Hegic 定价机制本身，而是 `benchmark - quoted premium` 这个 residual：它在 wBTC call 上更大、更 persistent，并且会随 order size / strike / maturity / volatility 上升，随 underlying trading volume 下降。**

### 3.2 论文里最有用的几个直接结论
按论文摘要和正文前几节，作者给出的可交易线索很清楚：

1. **benchmark price 通常高于 Hegic quote**；
   - 尤其是 **call options**；
   - **ETH puts** 是少数例外。

2. **wBTC 的 mispricing 更大、更 persistent；ETH 更接近 benchmark。**
   - 这直接给了 desk 一个最初的排序：
   - **先看 wBTC，再看 ETH；先看 call，再看 put。**

3. residual 会随着以下变量上升：
   - **更大的 order size**
   - **更远离 ATM 的 strike**
   - **更长的 maturity**
   - **更高的 estimated volatility**

4. residual 会随着以下变量下降：
   - **更高的 underlying trading volume**

这几条很关键，因为它们说明这条 alpha 不是“全市场随机乱闪”，而是**有明确横截面结构的错价**。

---

## 4. 为什么和当前项目有关
这条线和当前 `/root/clawd/jerry/momentum` 很相关，原因不是“我们突然转去做期权论文”，而是它刚好满足现在 intake 更看重的几件事：

1. **base alpha 讲得清楚**
   - 不是宏观叙事，不是模糊解释；
   - 就是 `quoted premium < benchmark fair value` 的 relative-value residual。

2. **短周期角色清晰**
   - `1m/3m/5m/15m` 在这里不是拿来预测 long-run vol；
   - 而是拿来做：
     - 高频/准高频 quote 监控
     - residual 扩张时的 entry
     - residual 回补时的 early exit
     - hedge rebalancing

3. **它补的是当前 desk 相对少的“链上 options AMM 错价”素材**
   - 我们最近 options / parity / cross-venue 题很多，但大多是 **CEX options**；
   - 这篇给的是 **DeFi AMM quote vs external benchmark**，数据结构和执行 frictions 都不一样；
   - 因此不是简单重复已有的 Deribit / Binance options 条目。

4. **它天然属于 raw relative-value，而不是又一个 overlay**
   - 你不是拿一个低频因子去 veto 别的信号；
   - 你是在直接交易“期权 quote 本身相对 fair value 的偏离”。

---

## 5. 对 desk 最有价值的改写：别照抄论文 headline，直接拆成 residual trade
论文原文的目标更偏“诊断和校准 Hegic pricing logic”，并没有把它写成完整交易系统。

但对 desk，更值得直接落成下面这条壳：

### 5.1 最小 raw alpha 壳
对每张可交易链上期权，在每个观测时刻计算：

- `model_price_t`：基准模型价
- `quote_ask_t`：Hegic 实时报价 / 可成交 ask
- `residual_t = (model_price_t - quote_ask_t) / underlying_mid_t`

若：
- `residual_t` 足够大；
- `quote` 可成交；
- `gas + fee + hedge slippage + hedge carry` 后仍有边际；

则做：
- **long underpriced option**
- **short/long perp or spot 做 delta hedge**

赚的是：
- residual 向 0 回补；
- 或到 expiry 时实现的保底内在价值 / 更合理时间价值。

### 5.2 为什么它更像 raw alpha，而不是纯校准任务
因为真正入场的不是“模型参数有研究价值”，而是：
- `当下这张合约便宜了多少`；
- `这个便宜是否大到覆盖现实 frictions`；
- `它会不会在接下来几根 bar / 几小时内回补`。

只要这三步能量化，它就是可交易 alpha，不只是 paper explanation。

---

## 6. 这篇 paper 给 desk 的 4 个最实用启发
### 6.1 先做横截面排序，不要一上来就全链扫所有合约
论文已经给出第一层 admission：
- **underlying 优先级：wBTC > ETH**
- **option side 优先级：call > put**
- **market state 优先级：高波动期更值得看**

所以第一版别上来就做“所有 strike / 所有 expiry / 所有 side 一视同仁”，而是先做：
- `wBTC calls`
- `短中期限`
- `高 residual`
- `delta 可对冲`

### 6.2 order size 是关键，不只是辅助解释变量
论文明确说 residual 会随 **order size** 上升。
这说明链上 AMM 报价不是“单一 mid 一刀切”，而是**和你吃多少 size 有关**。

对我们最重要的启发是：
> 这条线不能只用 quote-level mid 回测，必须把 `size-aware quote` 写进实验口径。

否则你回测到的是“纸上 residual”，不是可成交 residual。

### 6.3 先把 vol proxy 简化，别被论文的 MS-GARCH 门槛吓住
论文用的是：
- `two-regime MS-AR-(GJR)-GARCH`

这当然更严谨，但 desk 第一轮最小实验不需要先把学术波动率模型完整复刻。

更现实的推进顺序是：
1. **先用简化版 benchmark**：
   - BS + rolling realized vol / EWMA vol / perp implied proxy
2. 看 residual 是否已经有结构；
3. 只有第一轮过线，再升级到 regime-sensitive vol。

也就是说，**论文给的是“高配 benchmark”**，不是说没有它就完全不能做最小实验。

### 6.4 这条线天生更适合 maker-first / patience execution
因为链上期权的真问题不是“信号算不出来”，而是：
- gas
- quote stale
- 链上拥堵
- AMM size impact
- hedge leg 不同步

所以 desk 版更像：
- **稀疏事件驱动**
- **maker-first 或 patience-first**
- **size clip 很小**
- **先 paper-trade / replay，再谈放量**

而不是像 perp 单腿信号那样 5m 一根一根无脑打。

---

## 7. 主题定位（必填拆解）
- 方向属性：options / on-chain / relative-value / stat-arb
- 基础 alpha：`Hegic quote` 相对 `external benchmark fair value` 的 residual 回补
- 主题定位：**raw alpha**
- 标准壳：`long underpriced option + delta hedge`
- 更适合先做的标的：`wBTC call`
- 更适合先做的状态：`高 vol / 低 depth / 较高 order-size quote`

### 7.1 为什么不把它归类成 overlay
因为它不是在给别的主信号加确认；
它自己就是主信号：**你直接交易 quote-vs-fair-value gap。**

### 7.2 为什么我仍然把“可直接落地完整策略”写成“否”
因为论文虽然把 alpha 核心讲清楚了，但没把这几个 desk 关键问题 fully close：
- quote 数据接口和刷新机制
- 链上成交 / gas / MEV / stale quote
- hedge leg 的 venue 选择和资金搬运
- American-style 行权与持有路径
- on-chain option 流动性容量

所以它已经足够进研究池，但还没到“今天就能无脑上线”的程度。

---

## 8. 最小可复现实验（下一步怎么测）
### 8.1 数据源
必须先写清，不然这题很容易变成空谈。

**期权 quote：**
- Hegic Arbitrum on-chain quote / trade / contract state
- 公开性：公开链上数据，可通过合约调用、事件、索引服务或协议接口拿到
- 更新频率：接近链上事件频率；desk 初版可先按 `1m/5m` snapshot 化

**underlying price / hedge leg：**
- wBTC / ETH 对应的 CEX perp / spot（Binance、OKX、Bybit 等）
- 公开性：公开 API 可得
- 更新频率：秒级到 1m 级

**波动率 / benchmark：**
- 第一轮：rolling realized vol / EWMA vol
- 第二轮：再升级到 regime-sensitive GARCH / MS-GARCH

### 8.2 第一轮最小实验口径（建议先做这个）
先别复刻论文全套统计回归，直接做 trading version：

1. 只选：
   - `wBTC calls`
   - `近 7d / 14d` 到期
   - `delta` 在一个可对冲区间内的合约

2. 每 `5m` 生成一次 snapshot：
   - option ask / quote
   - underlying mid
   - benchmark model price
   - residual
   - order-size-sensitive executable quote

3. 定义 entry score：
   - `score = (model_price - executable_option_ask) / underlying_mid`

4. 初始入场阈值先试三档：
   - `score > 30 bps`
   - `score > 60 bps`
   - `score > 100 bps`

5. hedge：
   - 用 perp 做 delta hedge
   - `|net delta|` 超阈值时再 rebalance，不要每个 tick 乱调

6. exit 两套并行：
   - **gap-close exit**：`score` 回到入场时的 25% 以下就平
   - **time-stop exit**：持有超过 `6h / 12h / 24h` 强平
   - **expiry-stop**：距到期 `< 12h` 不再新开；旧仓在 `expiry - 2h` 前平掉

### 8.3 第二轮升级版
若第一轮真看到结构，再加：
- 论文的 regime-sensitive vol
- strike bucket / maturity bucket / call-vs-put 分层
- size-aware quote ladder
- gas / slippage / MEV 模拟
- `wBTC vs ETH` 横截面对比

### 8.4 最先看 6 个指标
- `signals/day`
- `median entry residual`
- `residual half-life`
- `net pnl after fee + gas + hedge carry`
- `delta rebalance count`
- `fillable size / capacity`

---

## 9. 对 1m / 3m / 5m / 15m 的实际映射
这题不是拿 15m K 线预测下一根方向，而是：

- **1m / 3m**：更适合 quote monitoring 和 hedge rebalancing
- **5m**：更适合 first-pass snapshot / backtest bar size
- **15m**：更适合先做粗颗粒 feasibility，不适合做真正入场时钟

所以它和当前 short-cycle desk 的关系不是“预测下一根涨跌”，而是：
> 把短周期用在 **错价监控、执行、回补退出**，而不是硬套到方向预测。

这点是合理的，不算偏题。

---

## 10. 风险与保留意见
1. **这条线最怕成交与对冲不同步**
   - option 成了，hedge 没成，短时风险会被放大。

2. **链上 option quote 可能 stale**
   - 看起来很便宜，不代表你真能拿到那个价。

3. **American-style / protocol-specific exercise logic 不能忽略**
   - 不能把它偷换成 textbook European option 再装作没差别。

4. **真实成本不只是 fee**
   - gas、桥、oracle latency、size impact、MEV 都可能吃掉 residual。

5. **模型价本身也有误差**
   - 若 vol proxy 很差，你交易的可能是“模型错”，不是“市场错”。

所以这题的正确姿势不是“看到 residual 就梭”，而是：
**先做 benchmark robustness + executable residual 校验。**

---

## 11. 一句话结论
> 这篇 2025 Hegic 论文最值得 desk intake 的，不是“链上期权 AMM 怎么校准”，而是它清楚暴露出一条可交易的 raw relative-value 线：**`on-chain option quote-vs-benchmark residual fade × delta-aware hedge`**；其中论文直接给出的第一批优先级是 **wBTC > ETH、call > put、高 vol > 低 vol**。

---

## 12. 来源
1. **Anastasiia Zbandut** (2025). *Pricing of wrapped Bitcoin and Ethereum on-chain options*. arXiv.  
   - Readable URL: `https://arxiv.org/abs/2512.20190`
   - PDF URL: `https://arxiv.org/pdf/2512.20190.pdf`

2. 论文正文中的核心样本描述（作者原文）  
   - Protocol / chain: `Hegic on Arbitrum`
   - Underlyings: `wBTC`, `ETH`
   - Sample window: `2022-10-24` to `2024-05-21`
   - Benchmark: `Black-Scholes + two-regime MS-AR-(GJR)-GARCH volatility`

3. Hegic / on-chain options 研究语境（论文文献综述中涉及）  
   - 链上 AMM option pricing, oracle lag, pooled-liquidity inventory risk, denomination / settlement frictions
   - 用途：说明这条 residual 不只是统计噪音，而是有明确协议结构来源
