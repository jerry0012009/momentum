主题类型：overlay
基础 alpha：无独立方向性 alpha；它服务于任意已有 raw alpha，把“薄书 + 流动性集中 + 预期冲击成本上升”转成进场 veto、仓位缩放与执行成本上限
是否可独立复现：是
是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（作为共享 overlay 直接挂到已有 1m/3m/5m/15m perp 策略上）

# Slippage-at-Risk：把 perp 盘口“快要变薄”提前翻译成 size cap / execution veto

## 1. 这次看了什么

如果只看标题，这篇 2026 arXiv 很像“交易所风险管理论文”。但对我们更有用的读法不是保险基金怎么定，而是：**把当前盘口深度、OI、流动性集中度，压缩成一个可实时更新的 execution / sizing overlay**，挂到已有的 breakout、mean reversion、basis、funding、order-flow alpha 上。

更直白地说，这篇东西不是教你“何时做多/做空”，而是教你在 **alpha 方向没变** 时，先问一句：**这笔单在当前盘口结构下，值得做、做多大、会不会因为流动性坍塌把本来有 edge 的单子做成负 EV？**

如果非要回答一句“为什么这轮选 overlay 而不是继续补 raw alpha”：今晚扫到的几条新 raw-alpha 候选里，要么已被 digest 覆盖，要么只能拿到 abstract / metadata，难以支撑高质量新 intake；而这篇 2026 新文全文可得、参数和实施路径都很清楚，且能直接服务我们已经积累的一整池短周期 raw alpha，部署价值足够高。

## 2. 来源与我认为最值得提炼的那一层

### 论文
- **Author / Year / Title / Venue**：Otar Sepper (2026), *Slippage-at-Risk (SaR): A Forward-Looking Liquidity Risk Framework for Perpetual Futures Exchanges*, arXiv
- **DOI**：10.48550/arXiv.2603.09164
- **Readable URL**：https://arxiv.org/abs/2603.09164
- **HTML / full text**：https://arxiv.org/html/2603.09164
- **Repo URL**：未见作者仓库

### 这篇东西的 base alpha 是什么？
不是新的方向性 alpha。它是一个 **shared execution / risk overlay**：
- raw alpha 负责回答：现在该 long / short / spread 哪边？
- SaR overlay 负责回答：**这笔单在当前流动性状态下还能不能做，做多大，预期滑点够不够把 edge 吃掉？**

所以别把它伪装成“新主信号”。它的正确定位就是：**overlay**。

## 3. 论文里最能直接搬到 desk 的核心机制

论文定义了三层量：

1. **单币种、单时点的执行滑点函数**
   - 给定一个要强平/交易的名义规模 `Q_i`
   - 沿盘口逐档吃单，得到该规模下的平均冲击成本 `S_i(Q_i)`

2. **横截面 SaR / ESaR / TSaR**
   - `SaR(alpha)`：全市场 token 的滑点分布分位数
   - `ESaR(alpha)`：尾部 token 的平均滑点
   - `TSaR(alpha)`：尾部 token 的总美元滑点暴露

3. **集中度修正（paper 里是重点）**
   - 同样深度的盘口，如果流动性由极少数做市商撑着，真实脆弱性远大于“看上去有深度”
   - 作者用 `HHI / N_eff / CR1` 给滑点加 haircut，把“薄书 + 集中”翻成更高的 adjusted slippage

对短周期 desk 来说，最有价值的不是 paper 里的保险基金 sizing，而是下面这个转译：

> **同一笔 alpha 信号，在流动性分布健康时可以正常做；在 book 变薄、且深度高度集中时，应该减仓、延后、拆单，甚至直接 veto。**

## 4. 论文里能直接拿来当阈值直觉的几个数字

作者用 Hyperliquid 2025-10-09 ~ 2025-11-03 的数据做实证：
- **184 个 perp 合约**
- **5 分钟 order-book snapshots**（深度到 2500 bps）
- **15 分钟 OI snapshots**
- 含账户级归因，因此可以做真正的集中度修正

我觉得最有用的几组数字是：

### 4.1 常态下的“全场流动性体温计”
在 `beta = 10% stress notional` 下，作者给出的样本期汇总值：
- `SaR(0.95) = 2.84%`
- `SaR_adj(0.95) = 3.47%`
- `ESaR_adj(0.95) = 8.92%`
- `TSaR_adj(0.95) = $127.4M`
- 尾部只有 **9 个 token**，但对应了 **$196M / 2.3% OI**

翻成人话：**看起来只是少数几个尾部标的在出事，但它们已经足够把全场执行风险拉高。**

### 4.2 它不是事后统计，而是真的“提前变坏”
论文最重要的不是定义，而是 lead-lag：
- `TSaR` 对 **12 小时后 deficit** 的相关性约 **0.61**
- 对 **24 小时后 deficit** 的相关性仍有 **0.42**
- Granger causality：`F = 8.47, p << 0.001`

这说明它不是“市场炸了以后你才知道危险”，而是**盘口先变脆，坏结果后发生**。

### 4.3 案例里，风控信号比崩盘先到
以 2025-10-10 Hyperliquid cascade 为例：
- 事件前 36 小时，100bps 深度 **$1.12B → $284M（-75%）**
- 事件前 24 小时，`SaR_adj(0.95)` **2.41% → 3.12%（+30%）**
- `TSaR` **$89M → $156M**，到级联时一度冲到 **$847M**
- 预估滑点 vs 实际滑点回归 `R² = 0.78`

对 desk 的启发很直接：**如果我们的 alpha 本来就是 20~80 bps 级别的短周期 edge，那种 盘口预期冲击成本向 1%+ 迁移 的环境，本来就该少做。**

## 5. 怎么把它改写成适合 1m / 3m / 5m / 15m 的 desk 版本

论文原始版本更像“交易所级别全市场风险仪表盘”。对我们来说，建议拆成两层：

### 5.1 交易级 overlay：单标的 execution veto / size cap
对每个可交易 symbol `i`，每 1 分钟或 5 分钟更新：

1. **定义压力成交规模**
   - `Q_i = min(beta * OI_i, cap_notional_i)`
   - desk 起步可先用：
     - BTC / ETH：`beta = 1%~2%`
     - 中腰部 alt：`beta = 2%~5%`
   - 不必上来就照 paper 的 10%，否则对短周期交易太保守

2. **从 L2 book 计算 raw slippage**
   - 沿 bid / ask 档位 walk the book
   - 算出吃掉 `Q_i` 之后的 VWAP 偏离中间价百分比

3. **算 concentration proxy**
   - 在 fully on-chain venue（如 Hyperliquid）可尽量接近 paper 思路
   - 若拿不到 maker 级归因，就退而求其次，用 `top-k depth share`、`前 1/3/5 档深度占比`、`盘口撤单率` 做 pseudo-concentration proxy

4. **得到 adjusted slippage**
   - `adj_slip_i = raw_slip_i * (1 + haircut_i)`

5. **做 veto / size / cost**
   - 若 `adj_slip_i > expected_alpha_i * 0.5~0.7`：直接 veto
   - 若 `adj_slip_i` 进入过去 30 天自身分位数 top decile：仓位减半
   - 若 `adj_slip_i` 处于低位：允许恢复正常 size

### 5.2 场馆级 overlay：全局 gross exposure scaler
除了单标的，还可以对 watchlist 横截面做一个 venue-level `SaR_95`：

- `SaR_95_t = quantile_95( adj_slip_i,t over tradable universe )`
- `TSaR_t = sum( adj_slip_i,t * Q_i ) over tail tokens`

然后把它直接作为组合总杠杆 / 总 gross 的缩放器：

- `gross_scale = clip(theta / SaR_95_t, 0.3, 1.0)`
- 或者更离散一点：
  - `SaR_95` 在过去 60 天 < 70 分位：满仓
  - 70~90 分位：`gross x 0.7`
  - >90 分位：`gross x 0.4` + 只保留最高 conviction 信号

这特别适合我们已有的：
- breakout / momentum
- mean reversion
- basis / funding pocket
- order-flow imbalance
- perp-perp relative value

因为这些 alpha 最大的共同敌人之一，不是“方向判断错了”，而是**执行环境突然恶化**。

## 6. 最小可复现实验（公开数据、能快做）

### 6.1 数据源
**公开性：公开可得**

1. **Hyperliquid public order book / candles / asset context**
   - 文档：
     - https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
     - https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
   - 可直接拿：
     - `l2Book`
     - `candle`（支持 `1m / 3m / 5m / 15m`）
     - `activeAssetCtx`（含 `openInterest`）

2. **已有策略自己的 signal 输出**
   - breakout / MR / basis / flow 任一已有信号都行

### 6.2 更新频率
- `l2Book`：实时 websocket
- `activeAssetCtx`：可轮询 / 订阅
- `candle`：1m/3m/5m/15m 原生支持

所以这个 overlay 天然能映射到我们当前主工作周期。

### 6.3 最小实验口径
先别全市场，直接做一个 **SaR-lite overlay A/B test**：

#### Universe
- BTC, ETH, SOL, HYPE, PEPE, DOGE, ARB, AVAX
- 覆盖：高流动性主流 + 中等流动性 alpha 常见币

#### Timeframe
- overlay 每 **1m** 更新一次
- signal 在 **5m / 15m** 上跑；若有高频策略再加 `1m / 3m`

#### 交易逻辑
先选 2 个已有 raw alpha：
1. 一个 trend / breakout
2. 一个 mean reversion 或 spread / basis pocket

然后只比较：
- **Baseline**：原策略照常交易
- **Overlay-1**：加单标的 `adj_slip_i` veto
- **Overlay-2**：加全局 `SaR_95` gross scaler
- **Overlay-3**：两者都加

#### 成本口径
每笔 round-trip 成本改写为：
- `fee + 2 * adj_slip_i`

别再只用静态手续费；这正是 paper 真正想纠正的地方。

#### 最重要的输出指标
不是只看 Sharpe，要看：
- net PnL
- trade hit-rate
- average edge after cost
- MAE / MFE
- tail loss / worst 5 trades
- skipped-trade ratio
- gross-to-net conversion
- 在高 SaR 分位环境中的表现衰减幅度

## 7. 我会怎么先测（具体，不空）

### 实验 1：先验证它是不是“有用的 veto”
- 取最近 30 天 Hyperliquid 1m L2 + OI
- 对每个 5m 信号时点，记录：
  - 该币 `adj_slip_i`
  - 全场 `SaR_95`
  - 信号后 5m / 15m forward return
- 先不做策略，只做条件分桶：
  - 低 SaR / 中 SaR / 高 SaR
  - 看同一个 raw alpha 在不同 SaR 桶里的净 edge 是否明显塌陷

**如果 edge 只在低 SaR 桶显著存在，这个 overlay 就成立了。**

### 实验 2：把它变成 size function，而不是 binary veto
对每个信号，把仓位函数写成：
- `size = base_size * f(adj_slip_i, SaR_95_t)`
- 一个最简单的 `f`：
  - 低于 50 分位：1.0x
  - 50~80 分位：0.75x
  - 80~90 分位：0.5x
  - >90 分位：0~0.25x

然后看：
- 回撤是否更小
- 高波动时段净值曲线是否更平
- alpha 是否从“赚的时候靠天、亏的时候一脚踩穿”变成可部署形态

### 实验 3：做 venue-stress router
如果我们手上同时有多 venue 或多 execution path：
- 先不问哪边信号更强
- 先问 **哪边的 SaR 更低**
- 把订单路由到更便宜、更新鲜的 liquidity path

这一步最适合之后接到 perp-perp basis、cross-venue spread、DEX/CEX same-asset lead-lag 里。

## 8. 这篇东西的局限，别误用

1. **它不是方向信号**
   - 不会告诉你 BTC 该涨还是跌
   - 只会告诉你：现在这笔单做下去，冲击成本和流动性脆弱度是否在吃掉 edge

2. **paper 的账户级集中度，在 CEX 上不一定拿得到**
   - 所以真正落地时，很多时候是 `SaR-lite`，不是论文原版
   - 但即便只用公开 L2 depth + OI，已经够做一版实用 execution veto

3. **paper 偏交易所风险管理，不是为 trader 写的**
   - 所以不要照抄保险基金 sizing 那段
   - 对 desk 最值钱的是：`raw_slip -> adjusted_slip -> veto/size/cost`

## 9. 一句话结论

这篇 2026 SaR 论文最适合我们的读法，不是“又一个宏大风控框架”，而是：

> **把盘口深度、OI、流动性集中度，压成一个可以每 1m / 5m 刷新的 shared overlay，专门给现有 short-cycle raw alpha 做进场 veto、仓位缩放和成本上限。**

它不替代 raw alpha，但很可能能让我们手上已经有的 alpha，少死很多本来不该死的单。

## 10. 下一步怎么测

按优先级我建议直接做下面 3 步：

1. **先做 Hyperliquid SaR-lite 采集器**
   - 拉 `l2Book + activeAssetCtx + candle`
   - 每 1 分钟落一版 `raw_slip / adj_slip / SaR_95 / TSaR`

2. **先挂到两个已有策略上**
   - 一个 breakout / momentum
   - 一个 mean reversion / relative-value
   - 先看 overlay 是否显著改善 net-of-cost 和 tail risk

3. **最后再谈更复杂的 concentration proxy**
   - 先用 top-k depth concentration 代理就够
   - 等确认 veto 有价值，再补 maker concentration / cancel dynamics / spoof filter

---

## 来源链接
- Paper abstract / metadata: https://arxiv.org/abs/2603.09164
- Paper HTML: https://arxiv.org/html/2603.09164
- DOI: https://doi.org/10.48550/arXiv.2603.09164
- Hyperliquid docs / websocket subscriptions: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
- Hyperliquid docs / info endpoint: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
