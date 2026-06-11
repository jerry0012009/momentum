# 别把 CEX/DEX spread alpha 继续写成“看到价差就打”：这篇 2026 arXiv 更该先测的是「priority-fee / delay aware same-asset spread arbitrage」完整策略

- 时间：2026-04-01 00:34 UTC
- 类型：2026 arXiv 全文 PDF + 2023 JEDC/ICDCSW 论文链路 + Binance / Uniswap / Ethereum 公共数据映射
- 主题标签：raw-alpha/relative-value/stat-arb/same-asset/cex-dex/spatial-arbitrage/priority-fee/stochastic-delay/convexity-cost/execution-latency/binance/uniswap/ethereum/public-data/1m/3m/5m/15m/paper
- 证据类型：论文全文 + arXiv 摘要 + 本地 PDF 文本抽取 + 公开数据源映射
- 主题类型：raw alpha
- 基础 alpha：同一资产在 CEX 与 DEX 之间出现可执行价差后，做跨 venue 对冲套利，赚的是 **价差向一致价格回归**；priority fee、gas、随机延迟、AMM convexity cost 不是主 alpha，而是决定这条 alpha 何时还能活、下多大、是否值得打
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次为什么选它
先回答一句：**这篇东西的 base alpha 是什么？**

答案很清楚：

> **same-asset cross-venue dislocation mean reversion**。
> 当 Binance 等 CEX 的有效价格和 Uniswap 等 DEX 的可执行价格出现足够大的偏离时，做一边买、一边卖，等价差回归。

所以它不是纯 filter，也不是只有 execution 讨论。它本身就是一条 **可独立交易的 relative-value / stat-arb raw alpha**。

之所以值得进池，不是因为“又来一篇 CEX 领先 DEX”，而是因为它把过去这条线里最欠缺的部分补上了：

- **entry 不是看到 spread 就冲**，而是先过 no-trade band；
- **sizing 不是拍脑袋**，而是被 AMM 深度/convexity cost 约束；
- **cost 不是只扣手续费**，而是把 gas / priority fee / 随机延迟一起拉进来；
- **exit / timeout / fee choice** 可以直接写成完整策略，而不再只是“有个 lead-lag 现象”。

如果说 3 月底那批 spatial-arb / parity 题更多是在补“有无 edge”，这篇更像是在补：
**这条 edge 怎样才算可下单、可存活、可 desk 化。**

## 2. 这篇论文到底在做什么
本轮核心主线是：

1. **Philippe Bergault, Yadh Hafsi, Leandro Sánchez-Betancourt (2026)**  
   *Trading in CEXs and DEXs with Priority Fees and Stochastic Delays*  
   arXiv:2602.10798  
   DOI: 10.48550/arXiv.2602.10798  
   URL: https://arxiv.org/abs/2602.10798

它把 CEX/DEX 交易写成一个 **mixed control** 问题：

- 在 **CEX** 上可以连续调整仓位；
- 在 **DEX** 上下单是离散 impulse；
- DEX 单会因为区块打包而有 **随机延迟**；
- 这个延迟可以通过 **priority fee** 部分控制；
- 系统允许 **多个 pending orders** 同时挂在链上等待执行。

论文最值钱的，不是数理控制本身，而是它给出一个非常 desk 化的结论：

> **真正该交易的不是“观测到的 spread”，而是“扣完池子冲击、gas、priority fee、延迟风险之后，仍然活着的 spread”。**

作者数值解里给出几个非常直观的策略结构：

- 当 CEX/DEX 价格接近时，最优动作是 **wait**；
- 只有当偏离穿出一条 **continuation/no-action band**，才进入 exercise region；
- 偏离越大、离终点越近、库存越偏，越愿意付更高的 priority fee 去抢执行；
- 如果链上整体执行更快，那么低优先级费用的适用区域会扩大，高 fee 区域会缩小；
- priority-fee 档位增加带来的价值提升很快 **plateau**，论文显示 **超过约 30 档后增益已很小**；
- 相比随机选 fee 档，**最优 fee 选择把 value function 提高了 18.2%**。

这条 `18.2%` 很重要：
它不是在说“alpha 强 18.2%”，而是在说 **同一条 spatial-arb alpha，fee / delay 选得对不对，本身就能造成很大的执行质量差异**。

## 3. 为什么我把它定性成 raw alpha，而不是 overlay
因为核心利润来源不是“更聪明地下单”，而是：

- **CEX 与 DEX 同资产价差会回归**；
- 你通过两边对冲把方向暴露压掉；
- 收的是 **跨 venue mispricing 的回归**。

priority fee / delay / gas / convexity cost 的角色是：

- 过滤掉伪机会；
- 决定何时出手；
- 决定付多少执行成本；
- 决定这笔单在现实中还能不能赚钱。

所以它更准确的读法是：

- **raw alpha 本体**：same-asset spread reversion；
- **策略落地骨架**：priority-fee / delay aware execution；
- **shared 价值**：这套 veto / sizing / timeout 也能反过来服务别的跨 venue alpha。

## 4. 这条线最硬的定量证据，不止来自 2026 新文，还来自作者 2023 的实盘式回放
2026 论文更偏控制与 delay/fee 决策。要判断这条线是否真能变成策略，需要看作者更早的实证底稿：

2. **Álvaro Cartea, Fayçal Drissi, Marcello Monga (2025 version / forthcoming JEDC)**  
   *Decentralised Finance and Automated Market Making: Execution and Speculation*  
   arXiv:2307.03499  
   DOI: 10.48550/arXiv.2307.03499  
   URL: https://arxiv.org/abs/2307.03499

3. **Álvaro Cartea, Fayçal Drissi, Marcello Monga (2023)**  
   *Execution and Statistical Arbitrage with Signals in Multiple Automated Market Makers*  
   2023 IEEE 43rd International Conference on Distributed Computing Systems Workshops (ICDCSW)  
   DOI: 10.1109/ICDCSW60045.2023.00012

这条 2023→2026 的链路说明：
不是只有“理论上有价差”，而是作者已经在 **Uniswap v3 + Binance** 上把这类策略做过滚动窗口 OOS 回放。

其中 2023/2025 这篇更直接给了 desk 真能用的数字：

### ETH/USDC（流动性更高）
- 滚动 OOS 执行次数：`8,579` 次
- speculative strategy 平均 **gross** PnL：`23,818`
- 对比：TWAP 只有 `919`
- 单笔一把梭：`-827,692`
- speculative strategy 平均费用：`15,096`

也就是说，即便把费用单独列出来，
`23,818 - 15,096 ≈ 8,722`，粗看仍然有正的净边。

### ETH/DAI（流动性更差）
- 滚动 OOS 执行次数：`1,747` 次
- speculative strategy 平均 **gross** PnL：`2,671`
- 对比：TWAP `-2,233`
- 单笔一把梭：`-148,352`
- speculative strategy 平均费用：`2,381`

这里净边已经明显变薄，
但重点恰好说明：**这条 alpha 对深度与成本极敏感，不能脱离 execution 讨论。**

我会把这组结果解读成三句话：

1. CEX→DEX spread reversion **不是幻觉**；
2. 但它不是“发现 spread 就赚”，而是 **执行质量主导留存利润**；
3. 越不液的池子，越要先做成本/延迟 veto，而不是迷信 headline spread。

## 5. 对 short-cycle desk，最应该抄的不是 PDE，而是这 4 个交易结论
### A. 真正的信号不是原始 spread，而是 executable spread
先算：

- CEX 可成交中价 / 对手价
- DEX marginal quote
- DEX executable quote（含 pool impact）
- pool fee
- gas
- priority fee
- 延迟风险 buffer

最后才得到：

`edge_t = sign-adjusted(CEX_price - DEX_exec_price) - all_in_cost_t - delay_risk_buffer_t`

只有 `edge_t > 0`，才叫信号。

### B. entry 应该是“穿出 no-trade band”，不是 spread>0 就下
2026 论文里的 continuation region 本质上就是：

- 偏离太小 -> 不值得付费，不做；
- 偏离够大 -> 才进入 exercise region；
- 离收盘/收敛终点越近，band 越窄，越容易触发；
- 库存偏得越厉害，band 会向一边倾斜。

翻成人话就是：
**不是所有价差都值得抢，只有大到能覆盖“执行不确定性”的那部分才值得。**

### C. 高 fee 不应该常开，只该留给“大偏离 + 高时间紧迫 + 高库存偏移”状态
这也是论文数值图最有用的部分：

- fee level 不是常数；
- 偏离越大，越应该用更高 priority 去换执行确定性；
- 但如果链拥堵下降、低费也够快，就该自动降费；
- fee 档位加太多没必要，**有限几个档就够**。

这对 desk 很实用，因为它暗示第一版根本不用做复杂连续优化，
**先做 3 档 fee bucket（low / mid / high）就足够做最小实验。**

### D. sizing 应该由“更难成交的一侧”和 pool convexity 决定
2023/2025 那篇的关键经验是：

- AMM execution cost 与 trade size 线性相关；
- 但与池子深度、汇率水平是非线性的；
- 本质上要把 **convexity cost** 当成真正的容量约束。

所以对 desk：

- 不是固定 notional 两边对冲；
- 而是先用 DEX 池子深度算这笔单打进去会把边吃掉多少；
- 然后再反推 CEX 对冲腿的可下规模。

## 6. desk 化之后，我会把它写成什么最小策略
### 策略定义
- **主题类型**：raw alpha
- **alpha 家族**：same-asset cross-venue stat-arb / spatial arb
- **适用频率**：`1m / 3m / 5m / 15m`，其中最值得先跑 `1m/3m/5m`
- **更像真实执行的对象**：ETH、WBTC 等有深 CEX 与深 DEX 池的资产

### Entry
当下列条件同时满足时进场：

1. `edge_t > theta_t`
   - `edge_t` 为扣除池冲击 / gas / priority fee / delay buffer 后的 executable edge
   - `theta_t` 为最小安全边际，可设成 rolling 成本波动的分位阈值
2. CEX 与 DEX 两侧都有足够容量
3. 当前 priority-fee bucket 对应的期望延迟仍在容忍区间内
4. 不在事件性 gas spike / 链异常拥堵黑名单里

### Position / sizing
- 先按 DEX 池深度计算最大可接受 trade size，使得冲击后 edge 仍为正；
- 再按 CEX 可成交量对冲；
- 同一时刻限制 pending DEX orders 数量；
- 若已有未确认链上单，则下调新单 size，避免堆叠延迟风险。

### Exit
任一触发即平：

1. spread 回到 band 内
2. 对冲后净 edge 回到 `<= 0`
3. 超过最大持有时间（例如 `3~10` 个 bar，按频率设）
4. pending order 未按预期时间确认，且 CEX 侧风险超过阈值
5. gas / priority fee 突然跳升，导致预期净边转负

### Risk / cost
必须显式记：

- taker/maker fee
- pool fee
- gas
- priority fee
- 延迟造成的补滑点
- 未确认订单期间的裸露风险

## 7. 为什么它比继续补一个 generic filter 更值得
因为这轮目标优先级是：
**可独立复现且可直接落地为完整策略的 raw alpha > 纯 filter / overlay。**

这篇满足：

- raw alpha 清楚；
- 公开数据可拿；
- entry / exit / sizing / risk / cost 都能定义；
- 还能顺手补齐跨 venue 线最缺的 execution veto 组件。

如果这轮继续去补某个“更聪明的情绪 filter”或“再一个 crowding gate”，价值反而没它高，
因为那些东西大多还得挂靠别的 alpha 才能活。

而这条线自己就能交易。

## 8. 公开数据能不能支撑最小复现实验？可以
### 数据源
1. **CEX：Binance 公共数据**
   - `bookTicker` / aggTrades / klines
   - 公开可得
   - 频率：秒级到分钟级

2. **DEX：Uniswap v3 公共链上数据**
   - pool `slot0`、liquidity、swaps、tick
   - 公开可得
   - 频率：逐笔 / 逐区块

3. **Ethereum fee 数据**
   - `eth_feeHistory`、base fee、priority fee 建议值
   - 公开可得
   - 频率：逐区块

4. **可选补充**
   - 公共 RPC / Dune / Flipside / 自建 archive 节点
   - 第一轮不要求 mempool 全量，先用区块级 feeHistory 近似即可

### 最小可复现实验口径
先别做太难的 tick-by-tick 全链撮合重建，第一轮直接做：

- 资产：`ETH/USDC`（先），再加 `WBTC/USDC`
- 频率：`1m / 3m / 5m`
- CEX 价格：bar close 或 bar 内 VWAP
- DEX 价格：同 bar 内最后一个可观测 marginal quote + 由池深度推 executable quote
- fee bucket：`low / mid / high` 三档
- delay 假设：映射成 `1 / 2 / 3` 个区块或经验均值延迟

然后做三组回测：

- **A：不考虑 priority fee，只扣固定 gas**
- **B：固定三档 fee bucket，不做状态切换**
- **C：按 dislocation / inventory / 剩余时间切换 fee bucket**

要看的不是只有总收益，而是：

- 多少原始 spread 在扣完 all-in cost 后还活着
- 不同 fee bucket 的 fill-quality / net edge 差异
- timeout / 未确认订单对净值的伤害
- 哪些时间段（亚洲/欧洲/美盘）这条线更容易活

## 9. 我认为最值得先测的 3 个假设
### 假设 1：priority fee 不是“多扣一项成本”，而是 alpha 生死开关
对照：
- 固定低 fee
- 固定中 fee
- 状态切换 fee

如果状态切换明显提高 net expectancy，这条线就不是 generic spatial-arb，
而是 **priority-aware spatial-arb**。

### 假设 2：大部分 headline spread，真实都是死在延迟和池冲击里
对照：
- raw observed spread
- executable spread after impact
- executable spread after impact + gas + fee + delay buffer

如果 surviving ratio 断崖式下降，就说明这条线真正的 alpha 研究核心不是“找 spread”，而是“找 surviving spread”。

### 假设 3：这条策略更适合 1m/3m，而不是 15m
原因很简单：
- spread 收敛通常更快；
- 延迟风险对长 bar 的解释力更差；
- 15m 可能更像把大量已收敛机会平均掉。

所以 15m 可以保留作 stress aggregation，但 **主实验应优先 1m/3m/5m**。

## 10. 这条线的明显短板
也要把丑话写前面：

1. **2026 论文主结果偏数值控制，不是现成交易代码**
   - 需要我们自己把 band / fee bucket desk 化。

2. **priority fee 与真实成交延迟的映射，第一轮只能近似**
   - 没有全量 mempool 时，先做区块级近似。

3. **same-asset 跨 venue 套利容易被 infra 吞掉**
   - 真实上线对链上执行、对冲路由、风控同步要求高。

4. **这条线更像 ETH/WBTC 主流资产策略**
   - 不适合直接外推到所有山寨币池。

但这些不是否定理由，反而是它值得进池的原因：
**它是少数能逼着我们把 “alpha × execution × latency × cost” 一次讲完整的 raw alpha 题。**

## 11. 我的判断
我会把这条线放进当前 desk 研究池，而且优先级不低。

不是因为它 headline 最性感，
而是因为它把一条已经“知道大概有 edge”的家族，往前推进了一整步：

- 从“有 spread”
- 变成“有 surviving spread”
- 再变成“有 fee / delay aware 的完整策略骨架”

如果后面要补跨 venue alpha，这篇比继续补一个泛化 filter 更值钱。

## 12. 下一步怎么测
直接做一个 **三阶段最小实验**：

### Phase A：可执行 spread 生存线
- 标的：ETH/USDC
- 频率：`1m / 3m / 5m`
- 信号：`raw spread -> executable spread -> net executable spread`
- 输出：surviving spread ratio、分时段生存率、平均净边

### Phase B：fee bucket 状态切换
- `low / mid / high` 三档 priority fee
- 用 spread 大小 + 剩余持有时间近似切换
- 输出：不同档位的成交概率、延迟、净收益、timeout 率

### Phase C：完整策略回放
- entry：穿出 band
- sizing：按 pool convexity 限额
- exit：回到 band / timeout / 净边转负
- 输出：gross/net PnL、hit rate、平均持有时间、fee 占毛利比例、不同拥堵 regime 表现

第一轮实验只要回答一个问题：

> **扣完 impact + gas + priority fee + 延迟 buffer 后，这条 same-asset cross-venue alpha 还剩多少？**

如果剩得下来，就值得继续做 infra；
如果剩不下来，这篇也仍然能沉淀成跨 venue 策略的 shared veto / sizing 模块。

## 13. 来源
1. **Philippe Bergault, Yadh Hafsi, Leandro Sánchez-Betancourt (2026). _Trading in CEXs and DEXs with Priority Fees and Stochastic Delays_. arXiv.**  
   - Venue: arXiv  
   - DOI: 10.48550/arXiv.2602.10798  
   - Readable URL: https://arxiv.org/abs/2602.10798  
   - PDF URL: https://arxiv.org/pdf/2602.10798.pdf

2. **Álvaro Cartea, Fayçal Drissi, Marcello Monga (2025 version; forthcoming in JEDC). _Decentralised Finance and Automated Market Making: Execution and Speculation_. arXiv.**  
   - Venue: Journal of Economic Dynamics and Control (forthcoming) / arXiv  
   - DOI: 10.48550/arXiv.2307.03499  
   - Readable URL: https://arxiv.org/abs/2307.03499  
   - PDF URL: https://arxiv.org/pdf/2307.03499.pdf

3. **Álvaro Cartea, Fayçal Drissi, Marcello Monga (2023). _Execution and Statistical Arbitrage with Signals in Multiple Automated Market Makers_. 2023 IEEE 43rd International Conference on Distributed Computing Systems Workshops (ICDCSW).**  
   - Venue: ICDCSW 2023  
   - DOI: 10.1109/ICDCSW60045.2023.00012  
   - Readable URL: https://doi.org/10.1109/ICDCSW60045.2023.00012

4. **Ethereum JSON-RPC / fee history endpoints.**  
   - 用途：base fee / priority fee / 区块级延迟近似  
   - 公开性：公开可得

5. **Binance Public Market Data + Uniswap v3 public on-chain pool state.**  
   - 用途：CEX mid / DEX executable quote / liquidity / swap traces  
   - 公开性：公开可得
