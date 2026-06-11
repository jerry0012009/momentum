# 别只把 funding spread 当 carry：对 short-cycle desk，更该先测「low-funding perp 充当 cheap synthetic future」这条完整 relative-value raw alpha

- 时间：2026-04-06 11:05 UTC
- 类型：2025 GitHub 仓库 README / methodology / strategy code + Binance / Hyperliquid 公共文档
- 主题类型：raw alpha
- 基础 alpha：**同一份 BTC carry 暴露会在不同载体上被错价：当“dated future 年化基差”显著高于“低 funding perp 所隐含的 synthetic carry”并能覆盖交易成本时，做空更贵的 carry 载体、做多更便宜的 carry 载体，等 carry gap / basis gap 收敛；若暂时没有 dated future，也可先退化成“低 funding venue perp 多头 vs 高 funding venue perp 空头”的 perp-perp synthetic carry spread。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/carry/funding/basis/synthetic-futures/perpetual-futures/calendar-spread/cross-venue/btc/15m/1h/public-data/repo/cost/risk
- 证据类型：仓库 README + methodology + strategy code + 公共 API 文档

## 1. 这次看了什么
这轮主材料不是论文，而是一套最近更新、而且明显带有“可直接落地壳子”的仓库：

- **Tamer Atesyakar (2025), _Crypto Statistical Arbitrage_**
  - 类型：GitHub repo
  - Readable URL：<https://github.com/abailey81/Crypto-Statistical-Arbitrage>
  - Repo URL：<https://github.com/abailey81/Crypto-Statistical-Arbitrage>
  - README raw：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md>
  - Methodology：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/methodology.md>
  - Synthetic futures code：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/futures_curve/synthetic_futures.py>
  - Futures curve package：<https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/futures_curve/__init__.py>
  - DOI：N/A
  - Venue：GitHub

补充的公开数据/文档口径：

- **Binance USDⓈ-M Futures Mark Price / Funding 文档**
  - Readable URL：<https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price>
- **Hyperliquid Info endpoint 文档**
  - Readable URL：<https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint>

我最后选它，不是因为又想补一篇泛泛的“funding / basis / calendar spread 综述”，而是因为它给了一个对 desk 很实用、但我们最近 intake 里还没被单独讲透的组件：

> **把低 funding perp 视为 cheap synthetic future，用它去替代更贵的 carry 载体。**

这和“单纯收 funding”不一样，也和“看到 basis 大就做空”不完全一样。它更像一条完整的 **carry / basis / relative-value raw alpha**：

- alpha 本体明确；
- entry / exit / sizing / risk / cost 都能直接写；
- 还能自然退化成更快可测的 perp-perp 版本。

---

## 2. 先回答：这篇东西的 base alpha 是什么？
### 2.1 base alpha 是清楚的，而且是 raw alpha
先讲一句人话：

> **同样一份 BTC carry 暴露，有时候用“dated future”买太贵；这时改用“低 funding perpetual”去合成那份暴露，成本更低。贵的那边未来会向便宜的那边收敛。**

把它写成 desk 语言，就是：

- 观察 **期货年化基差**；
- 观察 **perp funding 所隐含的 synthetic carry**；
- 扣掉两边交易成本、滑点、换腿成本后，得到：
  - `net_carry_gap = futures_carry - synthetic_perp_carry - all_costs`
- 当这个 gap 够大，就：
  - **short 贵的 carry 载体**
  - **long 便宜的 carry 载体**
- 等 gap 收敛、funding flip、basis 回到阈值内时平仓。

这不是 filter。
这也不是 overlay。
它本体就是一条 **relative-value / carry / basis** raw alpha。

### 2.2 为什么它比“继续补一篇普通 funding capture”更值得
因为我们最近材料池里已经有不少：

- funding persistence / sign-flip
- basis mean reversion
- cross-venue funding differential
- futures curve / calendar spread

但这篇 repo 真正多走了一步：

> **不是只盯 funding 本身，而是把 funding 变成“替代 futures carry 的定价输入”。**

也就是说，它把几条已经存在的零件——

- funding
- basis
- calendar spread
- cross-venue carry

拼成了一条更完整的策略壳，而不是再单独多收一个 feature。

这正好符合当前 bot7 的优先级：

> **可独立复现且可直接落地完整策略（entry/exit/sizing/risk/cost）的 raw alpha 候选。**

---

## 3. repo 到底给了什么对 desk 有用的证据
### 3.1 它不是一句空话，而是明确把 synthetic futures 写成独立策略分支
`synthetic_futures.py` 一开头就把策略写得很明确：

- 用多个 perpetual 组合去 **replicate futures exposure**；
- 比较：
  - `Futures Carry Cost = Basis_Annual / 100`
  - `Perp Carry Cost = Funding_Rate_Annual / 100`
- `Savings = Futures_Carry - Perp_Carry - Transaction_Costs`

而且代码里直接把策略分成：

- `SINGLE_VENUE_LONG`
- `SINGLE_VENUE_SHORT`
- `CROSS_VENUE_SPREAD`
- `FUNDING_HARVEST`
- `CARRY_REPLICATION`

这说明它不是在讲概念，而是在讲 **哪种腿结构对应哪种 alpha 壳**。

### 3.2 repo-level 的 BTC futures curve 结果很夸张，但至少告诉我们“这条路值得 first test”
README 给的 Phase 3（BTC Futures Curve Trading）repo-level walk-forward 结果是：

- **Sharpe：5.81**
- **Total Return：203.70%**
- **Max Drawdown：0.89%**
- **Total Trades：44,652**
- **Out-of-sample 测试区间：2023-07-01 到 2024-12-31**
- **注明：transaction costs included，1.0x only**

我不会把这些数字直接当成 synthetic futures 子策略自己的已验证收益，原因很简单：

- 这是 **Phase 3 整体书架** 的结果，不是单独 `synthetic_futures.py` 的隔离结果；
- repo 是大而全的系统工程，分支之间可能共享过滤与组合层；
- 没有直接看到“只做 synthetic carry replication”那条单独的 attribution 表。

但这些数字至少说明：

> **作者不是只在嘴上说 carry/basis，而是真把它做成了 walk-forward 框架里的一部分。**

### 3.3 它把完整策略参数写出来了，这对我们最有价值
`SyntheticFuturesConfig` 里直接给了第一版可测壳：

- **入场最小 funding spread**：`10% annualized`
- **最小 z-score**：`1.5`
- **最小 confidence**：`0.5`
- **max positions**：`5`
- **单仓最小/最大 notional**：`$10k / $500k`
- **单 venue 最大暴露**：`40%`
- **profit target**：`5%`
- **stop loss**：`3%`
- **max holding days**：`30`
- **max leverage**：`2x`

更重要的是，它还给了 venue 偏好：

- `preferred_long_venues`: **Hyperliquid / dYdX**（默认更低 funding）
- `preferred_short_venues`: **Binance / Bybit**（默认更高 funding）

翻成人话就是：

> **先在低 funding venue 挂 cheap long leg，再在高 funding venue 放 expensive short leg。**

这就不是“我知道 funding 有差”，而是“我已经知道这条 alpha 的默认腿怎么摆”。

### 3.4 它还给了 crisis 下的参数收缩逻辑
代码里专门写了 crisis 参数：

- 入场 funding spread 阈值翻倍；
- 仓位乘数降到 `0.25`；
- 最大持仓时间砍半；
- stop 更紧。

这非常对 desk 胃口，因为 carry / basis 壳最怕的不是平时，而是：

- exchange-specific liquidation spiral
- index / mark 偏离
- funding 机制失灵
- 单 venue 风险突然暴露

也就是说，这篇材料不是只会告诉你“信号是什么”，还告诉你：

> **什么时候这条 alpha 要缩表。**

---

## 4. 对 short-cycle desk，最值得拿走的不是“大而全系统”，而是这个更小、更诚实的策略壳
### 4.1 别一开始就复刻 repo 全家桶，先做最小壳
对我们最实用的拆法不是直接复刻 32 venues 多阶段系统，而是先拆成两级实验：

#### 版本 A：更快的 perp-perp synthetic carry spread（最快可测）
当暂时不接 dated future 时，先测：

- long 低 funding venue perp
- short 高 funding venue perp
- 只吃 funding/carry 差与价差收敛

这版最适合先做 `15m` 监控 + `1h` 主调仓。

#### 版本 B：完整的 futures vs synthetic futures carry substitution（正式版）
当能稳定拿到 quarterly futures / dated futures 数据时，再测：

- short 昂贵的 dated future carry
- long 低 funding perpetual synthetic leg
- 让 futures basis 与 synthetic carry gap 回归

这版才是最完整的“same exposure, different carrier mispricing”版本。

### 4.2 这条 alpha 跟普通 funding arbitrage 的差别在哪
普通 funding arbitrage 更像：

- 直接收 funding；
- 或跨 venue 收 funding differential；
- 但未必显式比较“替代 carry 载体”的定价。

这条 synthetic-futures 壳则更像：

> **把 perp funding 当成 futures carry 的替代贴现率。**

因此它更接近：

- carry substitution
- exposure-carrier relative value
- term-structure execution optimization

这会让它比“只盯 funding sign”更像一条完整策略，而不是单一 feature。

### 4.3 它和我们当前短周期框架的关系
对 `1m / 3m / 5m / 15m`，我会很诚实地定位：

- **alpha 本体节奏**：更偏 `15m / 1h`
- **1m / 3m / 5m` 的作用**：执行择时、滑点控制、腿同步、异常 veto

也就是说：

- **不要**把 funding / basis 这种天然较慢的东西硬伪装成“逐分钟主信号”；
- **要**把它当成 `15m / 1h` 的 raw alpha，再把更快周期拿来做 execution layer。

这正符合用户给的约束。

---

## 5. 公开数据能不能快速复现？能，但要分清主信号和执行层
### 5.1 数据源：公开可得
最快的公开数据入口可以直接用：

- **Binance USDⓈ-M Futures**
  - mark / index / last funding / next funding time
  - 文档：<https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price>
- **Hyperliquid Info API**
  - mids / perp metadata / user-visible market data
  - 文档：<https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint>
- 再补：Bybit / OKX / dYdX / GMX 的 funding 与 perp price 公共口径（repo 里已默认纳入 allowed venues）

如果先走最小实验，实际上只需要：

- perp mid / mark
- funding rate history
- next funding time
- 交易费与滑点假设

### 5.2 更新频率：适合 `15m / 1h` alpha，`1m / 3m / 5m` execution
这条线天然不是“每分钟重新发明世界”的 alpha：

- funding 事件是 **离散** 的；
- annualized carry 的变化，更多靠 **basis / price spread** 在 intraday 内波动；
- 因此最合理的 first test 是：
  - `15m` 监控 feature
  - `1h` 计算主信号 / 是否换腿
  - `1m / 3m / 5m` 只用于腿同步和冲击成本控制

### 5.3 最小可复现实验口径
**最快实验（版本 A）**：

- 标的：`BTC` perp cross-venue
- venues：Binance / Bybit / Hyperliquid / dYdX（先挑 2~3 个）
- bar：`15m`
- signal refresh：每 `1h`
- feature：
  - `funding_spread_annual_pct`
  - `cross_venue_basis_spread`
  - `zscore(funding_spread, lookback=14d hourly)`
  - `cost_adjusted_edge_bps`
- entry：`funding_spread_annual_pct > 10%` 且 `|z| > 1.5` 且净 edge > round-trip costs
- exit：edge 回落、funding flip、profit target、stop、max hold

**完整实验（版本 B）**：

- 在版本 A 上再加：
  - quarterly future / dated future basis
  - `futures_carry - synthetic_perp_carry`
- 核心问题变成：
  - **同一份 BTC carry 暴露，用 futures 买贵了多少？用 low-funding perp 合成便宜了多少？**

---

## 6. 如果直接落地成完整策略，我会怎么写
### 6.1 entry
先用最小、可执行的定义：

1. 计算每个 venue 的 annualized funding carry；
2. 计算目标 futures / perp 载体的 annualized basis carry；
3. 估计全套 round-trip cost：
   - taker / maker fee
   - slippage
   - 跨 venue 资金占用 / 借币 / gas（如果有）
4. 只有当：
   - `net_carry_gap > threshold`
   - `|zscore(carry_gap)| > 1.5`
   - 市场流动性 / 深度 / mark-index 偏离未超阈值
   才开仓。

### 6.2 position structure
分两种：

- **perp-perp 版本**：
  - long 低 funding venue perp
  - short 高 funding venue perp
- **future-vs-synthetic 版本**：
  - short 昂贵 future
  - long cheap synthetic perp leg
  - 必要时叠加对冲腿，保证总 delta 近似中性

### 6.3 exit
代码给的壳已经够实用：

- `profit_target_pct = 5%`
- `stop_loss_pct = 3%`
- `max_holding_days = 30`
- `funding_flip_exit = True`

对 short-cycle 版，我会再补一层更快的 exit：

- `15m` 内若 `net_carry_gap` 回到 `0.5 * entry_threshold` 内，先减仓；
- 若 legs 之间的 execution slippage 急剧扩大，也提前退出；
- funding 发放前后 1~2 个 bar 单独做 veto，避免硬吃结算跳变。

### 6.4 sizing
先用 repo 的保守框架：

- max positions：`5`
- 单 venue 最大暴露：`40%`
- 单笔 notional：`$10k` 到 `$500k`
- max leverage：`2x`

落到我们 desk，我会先这样简化：

- `size ∝ min(net_edge / target_edge, 1.0)`
- 再乘上：
  - liquidity factor
  - venue health factor
  - crisis multiplier

### 6.5 risk
这条壳最关键的风险不是方向，而是 **载体风险**：

- funding regime 突变
- venue-specific liquidation / outage
- mark/index 失真
- 单边腿先成交，另一边来不及对冲
- 极端事件下 carry gap 不收敛，反而继续扩

所以风控要盯：

- venue health
- mark-index dislocation
- basis gap 扩张速度
- 单腿滑点
- 可平仓深度

### 6.6 cost
这里千万别偷懒。
这条 alpha 如果不把 cost 算全，会特别容易“看起来年化很美，实际一上手就磨没”。

至少要显式计入：

- 双腿手续费
- 双腿滑点
- funding 收/付方向
- inventory / collateral 占用
- 如果走 DEX / hybrid，再加 gas 与失败重试成本

---

## 7. 这轮最值得立刻做的，不是全复刻，而是 3 个最小实验
### 7.1 实验 1：perp-perp funding spread 的 post-cost 单调性
目的：验证 repo 给的 `10% annualized + z>1.5` 壳，在我们口径下还有没有边。

要看：

- `net_funding_spread_decile` 与未来 `1h / 4h / 8h` PnL 是否单调；
- 交易成本后 decile-10 vs decile-1 还能不能拉开。

### 7.2 实验 2：加入 basis 后，synthetic carry gap 是否优于纯 funding spread
目的：回答 repo 真正新颖的那部分值不值钱。

也就是比较：

- 只用 funding differential
- 用 `futures_carry - synthetic_perp_carry`

哪一个更有：

- 单调性
- hit-rate
- 风险调整后收益

### 7.3 实验 3：1m/3m/5m execution veto 是否能明显改善 realized edge
目的：别把 execution 留到最后。

具体测：

- 不加 veto 的裸入场
- 加 `spread / depth / impact / mark-index` veto 的入场

看是否能明显减少：

- adverse entry
- 单腿偏离
- 结算前后被噪音扫出

---

## 8. 我对这条主题的判断
### 8.1 这是 raw alpha，不是 filter 伪装
因为它的本体就是：

> **做多便宜 carry 载体，做空昂贵 carry 载体，吃错价收敛。**

不是“市场差时别做”的风控建议。
不是“高波动时减仓”的 overlay。
是可以直接独立回测、独立开平仓、独立算成本的一条策略。

### 8.2 它为什么值得进当前素材池
因为它给 desk 补上的不是第 N 条 funding feature，而是：

- **carry substitution**
- **synthetic future leg construction**
- **futures curve 与 perp funding 的桥梁层**

这是一个明显更“可组装成完整策略”的组件。

### 8.3 我会把它放在什么优先级
我的判断：

- **优先级：中高**
- 不是因为它已经被证明“马上可上实盘”；
- 而是因为它同时满足：
  - raw alpha 身份清楚
  - 可独立复现
  - 能写完整策略壳
  - 还能和已有 funding / basis / curve / execution 组件自然拼装

---

## 9. 下一步怎么测
我建议下一步直接做一个 **两层实验**：

1. **快速 verdict（2~4 小时研发工时）**
   - 用公开 funding + perp mid 数据
   - 先测 perp-perp 版本
   - 看 `net_funding_spread` 的 post-cost decile 单调性

2. **正式最小版（半天到一天）**
   - 补一层 dated future / quarterly futures basis
   - 构造 `synthetic_carry_gap`
   - 做 `15m` 监控、`1h` 主调仓、`5m` execution veto

如果第二层显著优于第一层，就说明：

> **repo 里最值得 desk 拿走的，不是“funding arbitrage”四个字，而是“synthetic future 作为 carry 载体替代”这条 alpha 结构。**

## 10. 来源清单
- Tamer Atesyakar (2025), _Crypto Statistical Arbitrage_ (GitHub Repo)  
  <https://github.com/abailey81/Crypto-Statistical-Arbitrage>
- Repo README  
  <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md>
- Methodology  
  <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/methodology.md>
- Synthetic futures strategy code  
  <https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/futures_curve/synthetic_futures.py>
- Binance USDⓈ-M Futures Mark Price / Funding docs  
  <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price>
- Hyperliquid Info endpoint docs  
  <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint>
