# 别把这篇 2026 PolySwarm 只读成“LLM 群聊预测系统”：对 short-cycle desk，更该先拆的是「CEX-implied probability × stale Polymarket quote」和「negation-pair parity gap」这两条 prediction-market raw alpha 壳

- 时间：2026-04-14 11:22 UTC
- 类型：2026 arXiv working paper 全文抽取（本地 PDF）+ 公开 API/执行壳拆解
- 主题类型：raw alpha
- 基础 alpha：**`CEX-implied probability` 与 `Polymarket` 陈旧报价之间的价差回归 / 延迟修复；以及同平台 `P(E)+P(¬E)≠1` 的 negation-pair parity gap 收敛。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/prediction-market/event-driven/relative-value/stat-arb/latency-arbitrage/stale-price/negation-pair/parity-gap/polymarket/binance/cex-dex/probability/kelly/1m/3m/5m/paper/fulltext/public-api/cost/risk
- 证据类型：全文公式 + 系统架构参数 + 可直接转成最小实验的公开数据接口

## 1. 这次看了什么
主来源：
- **Authors：** Rajat M. Barot, Arjun S. Borkhatariya
- **Year：** 2026
- **Title：** *PolySwarm: A Multi-Agent Large Language Model Framework for Prediction Market Trading and Latency Arbitrage*
- **Venue：** arXiv working paper / preprint
- **DOI：** N/A
- **Readable URL：** <https://arxiv.org/abs/2604.03888>
- **PDF URL：** <https://arxiv.org/pdf/2604.03888>
- **Repo URL：** N/A（文中未给公开代码仓库）

这篇 paper 表面最显眼的是“50 个 LLM persona 做 prediction-market trading”。但如果按我们当前 desk 的 intake 优先级来读，**更值得单独拎出来的不是 LLM 群体预测本身，而是 paper 里已经写得很清楚、而且能用公开接口快速复现的两条短周期 raw alpha 壳：**

1. **CEX → Polymarket latency arb**：
   用 CEX 实时价格和波动率，把某个价格里程碑合约翻译成 `implied probability`，去抓 Polymarket 上还没来得及更新的陈旧报价。
2. **same-platform negation-pair parity arb**：
   同一事件正反两个市场如果出现 `P(E)+P(¬E)≠1`，就是直接的概率平价偏离。

对我们来说，这比“让 LLM 猜概率”更像真正可快速 admission 的 alpha，因为它更接近：
- **event-driven / latency**
- **relative-value / stat-arb**
- **公开 API 可拿到**
- **能映射到 `1m/3m/5m` 甚至更快的事件窗口**

## 2. 先回答最重要的问题：base alpha 是什么？
这篇东西的 **base alpha** 不是“AI 比人聪明”。

更适合我们 desk 的 base alpha 是：

> **当 Polymarket 对某个事件 / 价格里程碑的 implied probability 更新慢于外部信息或内部逻辑约束时，错误概率会向更合理的概率回归；可交易的就是这个回归过程本身。**

拆成两条：

### 2.1 latency arb leg
- 对 `BTC/ETH` 价格里程碑类市场，paper 直接给了：
  \[
  p_{cex} = \Phi\left(\frac{\ln(S/K)}{\sigma\sqrt{T}}\right)
  \]
  其中：
  - `S` = 当前 CEX spot price
  - `K` = Polymarket 合约 strike
  - `σ` = 小时波动率
  - `T` = 距到期时间（小时）
- 若 `p_cex` 和 `p_poly` 差很多，说明 Polymarket 报价还没 fully absorb 外部价格信息。
- **可交易 edge = `|p_cex - p_poly|`**。

### 2.2 negation-pair parity leg
- 若同平台两个互为否定的市场满足不了：
  \[
  P(E) + P(¬E) = 1
  \]
  就不是“观点不同”这么简单，而是**概率加总约束被破坏**。
- 这条更像 prediction-market 版的 put-call parity / cross-leg consistency arb。
- 它甚至不依赖 headline news，只依赖平台内部 quote consistency。

所以这轮 digest 里，**我把它明确定位成 raw alpha，不是 filter / overlay**。

## 3. 核心结论
- **一句话核心结论：** 这篇 paper 真正适合我们 desk intake 的，不是 LLM 群体预测，而是它已经写清楚的 **`CEX-implied probability × stale Polymarket quote` latency arb** 和 **`negation-pair parity gap`** 两条短周期 raw alpha 壳。
- **一句话原因：** 它们的 alpha 本体都很清楚：一个赚“外部信息先到、平台价格后到”的时间差，一个赚“平台内部概率约束没对齐”的结构差。
- **一句话落地性：** 这两条都能只靠**公开 Polymarket API + 公开 Binance WebSocket**做最小实验，不需要先解决“LLM 预测是否真的有 alpha”这个更难的问题。

paper 里给出的、对最小实验最有帮助的实操参数包括：
- **扫描频率：** `5s scan loop`
- **外部价格流：** `Binance WebSocket`，文中写的是 `~100ms ticks`
- **组合概率：** `p_combined = 0.7 * p_swarm + 0.3 * p_mkt`
- **latency-arb 过滤：** `edge >= 4%`、`poly stale > 8s`、`TTE ∈ [0.5h, 720h]`、`cooldown 30s`
- **风险控制：** `quarter-Kelly`、`max position cap = $10`、`daily loss limit`
- **链上延迟背景：** `Polygon PoS` 大约 `2s / block`
- **uncertainty veto：** 若 swarm 分歧太大（文中示例是 `std > 30%`），不做

这些参数不一定要原样照抄，但它们已经足够构成一个 **complete shell**：
- alpha
- entry
- sizing
- risk cap
- execution cadence

## 4. 为什么这轮值得进研究池
这轮有价值，不是因为它“新潮用了 LLM”，而是因为它补的是我们当前素材池里还不算拥挤的一条 lane：

### 4.1 它不是又一篇 trend / TSMOM 变体
最近 intake 里 raw alpha 很多已经在：
- trend / continuation
- mean reversion
- pairs / stat-arb
- funding / basis
- microstructure OFI

而这篇更像：
- **prediction-market microstructure / latency**
- **event-driven probability arb**
- **平台内部 consistency arb**

### 4.2 它和已有 prediction-market digest 也不重复
它不是：
- `semantic-equivalent cross-platform parity gap` 那种跨平台语义对齐 arb；
- 也不是 `favorite-side VWAP stretch × momentum` 那种单市场微观动量。

它更接近：
1. **同一市场对外部信息吸收太慢**；
2. **同一平台内部概率约束自己没对齐**。

这两个都是更“硬”的价差，不是纯主观看法 alpha。

### 4.3 它天然适合更快时间框架
这条壳不是为 `15m` 设计的。它更适合：
- `event tick / 5s / 15s / 30s / 1m`
- 或至少 `1m/3m/5m`

换句话说，它虽然不是默认 desk 的 `5m/15m` K 线 alpha，但它是明确的 **更快高强度 alpha lane**，符合用户允许范围。

## 5. 策略拆解（必填）
- 方向属性：**prediction-market / event-driven / relative-value / stat-arb**
- 基础 alpha：**`p_cex` 或内部逻辑约束先变，`p_poly` 后修复；交易的是概率错误的收敛。**
- regime：**高流动性、价格里程碑合约、较短但非极短到期、可观测外部锚（如 BTC/ETH spot）**
- filter / veto：**staleness、edge threshold、cooldown、low-liquidity veto、uncertainty veto**
- risk / sizing / execution overlay：**quarter-Kelly / fixed notional cap / daily loss cap / Polygon block-latency awareness / maker-first 或限价执行**

## 6. 对 desk 最值得拿走的不是“50 agents”，而是这两条规则化壳
### 6.1 壳 A：价格里程碑合约 latency arb
**适用对象：**
- `Will BTC be above X at time Y?`
- `Will ETH touch X this week?`
- 任何能从 CEX spot + vol 近似转成 probability 的 milestone / barrier-ish market

**最小规则：**
1. 实时拉 Binance `bookTicker` 或 mid；
2. 用 rolling realized vol 算 `σ`；
3. 计算 `p_cex`；
4. 抓 Polymarket 当前 `p_poly`；
5. 若 `|p_cex-p_poly|` 超过阈值且 Polymarket 报价 stale，就做向 `p_cex` 靠拢的那一边；
6. 当 edge 收敛、时间衰减不再有利、或 quote 更新完成时退出。

**它的好处：**
- base alpha 很清楚；
- 不需要先相信 LLM；
- 外部锚是公开 CEX 行情，不难拿；
- 本质是一个短周期 relative-value 收敛壳。

### 6.2 壳 B：negation-pair parity arb
**适用对象：**
- `E` 和 `¬E` 同时挂牌的 yes/no 市场；
- 或多个 mutually exclusive outcomes 组成完备分区的市场。

**最小规则：**
1. 枚举同类事件对；
2. 做 title / resolution rule 的严格匹配；
3. 计算 `P(E)+P(¬E)-1`；
4. 超阈值时买低估那边 / 避开高估那边；
5. 收敛后平仓，或者若分辨率很高也可持有到 resolution。

**它的好处：**
- edge 不依赖预测未来，而依赖内部一致性；
- 更像“结构性错价”，而不是观点交易；
- 很适合作为另一条纯规则化 alpha，不吃 LLM 推理质量。

## 7. 最小可复现实验（能直接开做）
### 7.1 数据源
- **Polymarket**：公开 `Gamma / CLOB API`
- **Binance**：公开 WebSocket `bookTicker` / kline / recent volatility 所需数据
- **可选新闻流**：公开 RSS / X / headlines（若要做更完整 news-to-market latency 版）

### 7.2 更新频率
- `Binance bookTicker`：亚秒级（paper 写 `~100ms ticks`）
- `Polymarket market scan`：先按 `5s` 轮询
- `1m/3m/5m` 聚合：只用于研究报表，不是 alpha 原生频率

### 7.3 最小实验口径
**Lane 1：BTC/ETH price milestone contracts**
- universe：近 `30d` 内有成交的 `BTC/ETH` price markets
- 每 `5s` 采样一次
- 计算：
  - `p_cex = Φ(ln(S/K)/(σ√T))`
  - `edge = p_cex - p_poly`
- 入场：`|edge| >= 4%` 且 `stale > 8s`
- 方向：`edge > 0` 做 Yes，`edge < 0` 做 No
- 出场：
  - `|edge| < 1.5%`；
  - 或持仓超过固定上限（如 `30m/2h`）
  - 或接近 resolution 前强制平
- 成本：
  - CLOB 交易费
  - Polygon gas
  - 半个 spread / slippage

**Lane 2：negation-pair parity**
- universe：互斥 / 否定型事件对
- 每 `5s` 计算 `sum_prob = P(E)+P(¬E)`
- 入场：`|sum_prob-1| >= fee_buffer + slippage_buffer + safety_margin`
- 出场：`|sum_prob-1|` 回到阈值内或事件临近 resolution

## 8. 这条壳和 `1m / 3m / 5m / 15m` 的关系
- **最自然的时间尺度：** `5s / 15s / 30s / 1m`
- **研究汇总尺度：** `1m / 3m / 5m`
- **不推荐直接压成：** 传统 `15m` bar-only alpha

原因很简单：
这类 edge 来自**信息吸收延迟**和**市场内部一致性破坏**，不是来自每根 `15m` K 线自身的形态统计。硬压成 `15m`，反而会把最有价值的短时错价磨平。

所以它更适合被 desk 放进：
- **faster event-driven lane**
- **prediction-market / external-data lane**
- **relative-value / stat-arb lane**

## 9. 风险与不该自欺的地方
### 9.1 这篇 paper 更像系统设计文，不是完整 OOS PnL 论文
paper 明确给了：
- 系统架构
- 公式
- 扫描与执行参数
- 评价指标（Brier / log-loss / calibration）

但它**不是那种已经给出严谨 out-of-sample 交易 PnL 表格的论文**。所以这轮最诚实的读法应该是：

> **这是一条完整且可复现的 raw alpha 壳，不是已经被 paper 自己严格证明过的 production alpha。**

### 9.2 prediction-market 的真成本不能只看 quoted probability
一定要显式记：
- spread
- queue priority
- fill probability
- gas / settlement friction
- event resolution 风险
- 大额下的 market impact

### 9.3 LLM 这层先别当 admission 必需品
如果先把“50-agent swarm 是否真有稳定预测力”绑进 admission，就会把最容易测的 raw alpha 变成一个很慢的 AI 项目。

对当前 desk，正确顺序应是：
1. **先测纯规则 latency / parity alpha**；
2. 只有纯规则部分站住后，才把 LLM classification 当增强层看待。

## 10. 下一步怎么测
1. **先做不含 LLM 的纯规则版**：只跑 `BTC/ETH` 价格里程碑市场的 `p_cex - p_poly` latency edge，验证是否有净收敛空间。  
2. **并行做 negation-pair scanner**：找 `P(E)+P(¬E)` 偏离是否在真实费用后仍可收敛。  
3. **把研究频率定在事件级，不要先压成 15m**：保存 `5s` 原始快照，再导出 `1m/3m/5m` 汇总。  
4. **先做 fixed-notional，再谈 Kelly**：早期 admission 先用固定仓位；确认收敛分布后再上 quarter-Kelly。  
5. **最后才加 LLM / news classifier**：如果纯规则版已成立，再加 headline parsing 去扩大可交易 universe，而不是本末倒置。

## 11. first verdict
这篇东西**值得进研究池，而且是新 lane**，但正确 intake 方式不是“复刻 50 个 LLM persona”，而是：

> **先把它拆成一条 prediction-market 短周期 raw alpha 壳：`CEX-implied probability × stale quote` + `negation-pair parity gap`。**

它满足我们当前优先级的原因是：
- **base alpha 清楚**；
- **公开数据可拿**；
- **entry/exit/sizing/risk/cost 都能定义**；
- **更适合 `1m/3m/5m` 的高强度事件窗口**；
- **和现有 trend / TSMOM / funding / basis intake 不同，能补一个 prediction-market / event-driven / relative-value 新素材位。**

如果要一句话下结论：

> **别先把 PolySwarm 当“AI 预测市场论文”；对 short-cycle desk，更值得先复现的是它藏在系统设计里的两条硬错价 alpha。**
