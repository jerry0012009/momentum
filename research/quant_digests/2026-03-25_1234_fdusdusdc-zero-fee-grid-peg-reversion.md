# 别把 U 型 grid 当 alpha：这份 2026 新仓库更该先复现的是「FDUSD/USDC 零费一跳回归」完整 raw alpha

- 时间：2026-03-25 12:34 UTC
- 类型：2026 GitHub 新仓库 + 2021 stablecoin arbitrage 论文 + Binance Spot 公共 `1m/5m` 最小快检
- 主题标签：raw-alpha/mean-reversion/relative-value/stablecoin/spot/grid/execution/cost/1m/3m/5m/15m/repo/paper/binance
- 证据类型：代码级 repo 拆解 + 理论论文 grounding + 公共 kline 最小事件研究

- 主题类型：raw alpha
- 基础 alpha：`FDUSD/USDC` 对 `1.0000` peg 的短周期偏离会回归，真正可交易的是“偏离后的一跳/两跳回收”，不是 U 型挂单形状本身
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次最值得 intake 的，不是“又一个 stablecoin grid 机器人”，而是一个**把完整策略链条写得很实**的新仓库：`wangshaofu/mm_bot`（2025 创建、2026-02 仍更新）。它把 stablecoin pair 的一条常见误解拆得很清楚：**alpha 是 peg deviation mean reversion；U 型 grid 只是 sizing / execution overlay。**

这件事为什么值得现在写进池子？因为最近 desk 的 raw alpha 素材虽然已经不只 trend，但还是更偏 perp / momentum / pairs。这个题目补的是另一条很短、很“脏活累活”的 relative-value 原型：**单场内、单 pair、低 beta、强 execution 约束、强 cost cliff**。它非常适合做 `1m/3m` 的高强度最小实验，也能降采样成 `5m` 版本；`15m` 更适合拿来做 inventory refresh / regime gate，而不是直接当逐 bar 入场键。

## 2. 先回答那句最重要的话：base alpha 是什么？
**base alpha = stablecoin peg reversion。**

更具体地说：当 `FDUSD/USDC` 在 Binance Spot 上跌到 `0.9998 / 0.9997 / 0.9996` 这类折价位时，后续很大概率会先回一跳（`+1 tick ≈ +1bp`），深一点时再看有没有两跳（`+2bp`）的空间。

所以：
- `U-shaped order distribution`：**不是 alpha**，只是把资金分散到更低价位的库存曲线；
- `dynamic grid refresh`：**不是 alpha**，只是让挂单跟着振幅和 best bid 走；
- `fee guard`：也**不是 alpha**，但它决定这条 alpha 能不能活；
- 真正应该先测的，是 **“折价 breach → 短时回到 fill+1tick / fill+2tick”** 这条原始回归链。

## 3. repo 里真正有价值的工程点
`wangshaofu/mm_bot` 的价值，不在“发明了新信号”，而在于它把完整策略需要的几个零件都交代清楚了：

1. **entry**：只在 best bid 下方挂买单，而且有 `buy_threshold`，避免追着价格在 peg 上方乱买；
2. **exit**：买到之后立刻镜像挂卖单，默认是“先收回一跳/几跳，再说”；
3. **sizing**：资金不是等距平铺，而是更偏向低价层的 U 型分布；
4. **risk**：有余额约束、最小下单单位、未成交订单刷新；
5. **cost**：最关键的是 `fee guard` —— 如果 maker/taker 费率不是它能承受的水平，策略直接不该跑。

对我们 desk 最有启发的一句翻译是：**这不是一个“grid alpha”，而是一个“one-tick peg reversion alpha + grid inventory allocator”。** 先把 alpha 本体测清，再决定要不要借 repo 的网格外壳。

## 4. 公共数据最小快检：过去 30 天 `FDUSD/USDC` 到底有没有这条边？
数据源：Binance Spot 公共 `api/v3/klines`，标的 `FDUSDUSDC`，窗口为最近 30 天；本地 artifact 在：
`reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/`

### 4.1 `1m` 事件研究（从上方跌破阈值才算新事件）
阈值取 `close <= 0.9997`：

- 30 天里共出现 **212** 个新 breach 事件，约 **7 次/天**；
- 后续 **15 分钟** 内，平均最大反弹 **+1.42 bps**；
- **89.15%** 的事件能先回到 **`entry + 1 tick`**；
- **44.34%** 的事件能回到 **`entry + 2 tick`**。

这组数说明：**一跳是主航道，两跳不是没有，但明显更挑环境。**

### 4.2 repo 风格的超简化回测（`1m`）
规则：
- 当 `close <= 0.9997` 且前一分钟不满足阈值时入场；
- 若后续 30 分钟内先触达目标价，则按目标价离场；
- 否则 30 分钟超时按收盘价离场。

结果：

**方案 A：目标 `+1 tick`**
- 212 笔 trades
- 平均毛收益：**+0.91 bps / trade**
- 胜率 / TP 率：**94.34%**
- 中位持有时间：**2 分钟**

**方案 B：目标 `+2 tick`**
- 212 笔 trades
- 平均毛收益：**+1.11 bps / trade**
- TP 率：**56.60%**
- 中位持有时间：**20 分钟**
- 5% 分位单笔：**-1.00 bps**

一句话总结：**+1tick 更像库存回收；+2tick 已经从“收租”变成“等行情帮你”了。**

### 4.3 `5m` 降采样后还能不能看？
如果把它硬塞进我们更常用的 `5m` 节奏，信号没有消失，但天然变钝：

- `5m close <= 0.9997` 的新事件，30 天里有 **100** 次；
- 这些事件里，后续 **30 分钟** 内有 **90%** 能回到 `entry + 1 tick`；
- 平均最大反弹约 **+1.61 bps**。

这说明它并非只能活在 tick 级；但**最佳形态仍是 `1m/3m` 执行，`5m` 只是慢一点的 proxy。**

## 5. 这条 alpha 为什么比“再补一个 filter”更值得？
因为它满足了当前 intake 更高优先级的那几个条件：

- **它是 raw alpha，不是纯 filter；**
- **它能独立复现；**
- **它能直接落地成完整策略**：entry / exit / sizing / risk / cost 都能写；
- 它给素材池补的是一条 **single-venue relative-value / stablecoin stat-arb** 支线，而不是再加一个泛化确认层。

更重要的是，它还能帮 desk 在方法论上少踩一个坑：
**不要把“能赚钱的库存分配器”误认成 alpha 本身。**
先验证 `breach → one-tick recovery` 是否稳定存在，再谈要不要套 grid、怎么套 grid。

## 6. 这条策略最怕什么
这条策略的第一风险不是方向，而是**成本和执行**：

1. **费用悬崖极陡**：
   - 我们测到的毛收益核心区间只有 **0.9~1.1 bps / trade**；
   - 这意味着只要 round-trip 成本来到 **1bp 以上**，策略几乎就被吃光；
   - 所以它本质上是**零费 / 超低 maker 费环境专用** alpha。

2. **容量有限**：
   - 单一 stablecoin pair，目标只收一两跳；
   - 它不适合承载大仓位，更像低风险 sidecar / cash management pocket。

3. **非常依赖 queue position**：
   - 回一跳不代表你能成交到那一跳；
   - 如果挂单排不到前面，理论 edge 会被 queue loss 吃掉。

4. **depeg / news regime 下会失真**：
   - 平时的 mean reversion，在异常时刻会突然变成“接飞刀”；
   - 这时 `1.0000` 不是吸引点，反而可能是旧世界的锚。

## 7. 怎么把它翻成 desk 可执行的最小实验
### 最小实验 A：先只测 alpha 本体
1. 数据：Binance Spot `FDUSDUSDC` `1m` + `5m` klines；
2. 事件定义：`close` 从上向下首次跌破 `0.9998 / 0.9997 / 0.9996`；
3. 出场：`+1 tick`、`+2 tick`、`30m timeout` 三套并行；
4. 指标：命中率、平均最大反弹、timeout 占比、超时后尾部损失；
5. 成本：至少做 `0 / 0.5 / 1.0 / 2.0 bps` 四档敏感性。

### 最小实验 B：再看 repo 外壳有没有增益
在 alpha 本体通过后，再去加：
- U 型库存曲线；
- 动态 grid 宽度（按最近振幅调节）；
- 单次最多挂几层 / 每层资金占比；
- 未成交订单刷新频率；
- inventory 上限。

也就是：**先证明“该买”，再优化“怎么买”。**

## 8. 下一步怎么测（直接给动作）
1. **做 fee cliff 图**：把 `+1tick / +2tick` 两套规则分别在 `0~2bps` round-trip 成本上画净收益曲线，先确认生存区间；
2. **加 order-book veto**：拉 Binance 公共深度快照，测试“top-of-book depth / spread widening / quote imbalance” 是否能把 `+2tick` 的 TP 率抬起来；
3. **做 depeg 例外隔离**：把大于 `5bp` 的异常偏离单独分桶，看普通 peg noise 和异常事件是不是两种完全不同的 process；
4. **试 `3m` 执行版**：把 `1m` 信号聚合到 `3m`，看 trade count 下降多少、净 edge 留下多少；
5. **把 `15m` 从入场键改成风控键**：用 `15m` 只做“今天允不允许跑这个 one-tick harvester”的 regime gate，例如过去 2 小时 peg 波动过大则停机。

## 9. 结论
如果只给一句结论：

**这篇 repo 最值得 desk 先偷的，不是 U 型 grid，而是“FDUSD/USDC 折价后一跳回归”这条可独立复现、可直接写成完整策略、但对费用极度敏感的 raw alpha。**

它很小、很窄、很 execution-heavy，但这恰好是优点：
- 好处是可快速复现、可快速验证、可快速知道自己是不是没有 edge；
- 坏处也很明确：**不是普适大 alpha，而是一条只有在零费/强排队权下才真的活的微利差 raw alpha。**

## 10. 来源
1. **wangshaofu (2025/2026)**, *mm_bot*（GitHub repo, Python）  
   - Repo URL: https://github.com/wangshaofu/mm_bot
   - Readable URL: https://github.com/wangshaofu/mm_bot
   - 说明：Binance stablecoin pair 自动网格/挂单机器人；本次重点不是照抄其 U 型分布，而是拆出其中真正的 alpha 本体。

2. **Ingolf Gunnar Anton Pernice (2021)**, *On Stablecoin Price Processes and Arbitrage*, in *Financial Cryptography and Data Security. FC 2021 International Workshops*, Lecture Notes in Computer Science, Springer, pp.124-135  
   - DOI: `10.1007/978-3-662-63958-0_11`
   - Readable URL: https://link.springer.com/chapter/10.1007/978-3-662-63958-0_11
   - DOI URL: https://doi.org/10.1007/978-3-662-63958-0_11
   - 用处：给 stablecoin peg 附近的套利 / 回归机制提供理论 grounding，提醒我们常态与异常状态不是同一种过程。

3. **Binance Spot API Docs / Public Klines**
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
   - Data endpoint used: `https://api.binance.com/api/v3/klines?symbol=FDUSDUSDC&interval=1m`

4. **本地最小实验 artifact**
   - `reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/probe_fdusdusdc_zero_fee_grid.py`
   - `reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/summary.json`
   - `reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/forward_stats_1m.csv`
   - `reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/forward_stats_5m.csv`
   - `reports/artifacts/quant_digests/fdusdusdc_zero_fee_grid_20260325_1205/repo_style_tp_runs.csv`
