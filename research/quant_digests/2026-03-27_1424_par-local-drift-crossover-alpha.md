# 别把这篇 2023 AIMS intraday 论文只当奇怪的曲线拟合：它更像「单币局部漂移线突破后顺势持有到反向翻仓」raw alpha
- 时间：2026-03-27 14:24 UTC
- 类型：2023 AIMS Mathematics 开放获取全文 PDF
- 主题类型：raw alpha
- 基础 alpha：价格一旦显著偏离本地非线性预测线，短周期局部趋势会继续延伸；直到价格重新穿回并给出反向信号才翻仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/single-asset/trend/intraday/polynomial-autoregression/local-drift/signal-line-crossover/reverse-on-opposite/buffered-entry/1m/3m/5m/15m/paper/no-cost-model
- 证据类型：论文全文证据

## 1. 这次看了什么
这次看的是 **Gil Cohen (2023), _Intraday trading of cryptocurrencies using polynomial auto regression_**, 发表在 **AIMS Mathematics**。

先直接回答这篇东西的 **base alpha**：

> **不是“高位突破某条固定前高/前低”，而是“价格相对一条局部非线性漂移线的有缓冲突破/跌破”，随后顺着这段局部 drift 继续持有，直到出现反向穿越才翻仓。**

所以它首先是 **raw alpha**，不是 confirmation filter，也不是纯 risk overlay。更具体地说，它是一条 **单币 directional / local-trend-follow** 线：
- 信号本体 = 价格相对预测线的位置；
- 交易逻辑 = 上穿做多、下穿做空；
- 持仓逻辑 = 一直持有到反向信号；
- 不是在已有 breakout 上再套一个 gate，而是本身就能独立成策略。

这点对当前 desk 有价值，因为我们最近 intake 里横截面、pairs、carry、lead-lag 比较多，这篇补的是 **same-asset 单币方向性 raw alpha**，而且不是传统 Donchian/high-low breakout 的重复体。

## 2. 核心结论
- **样本口径：** 论文用 **2021-12-01 到 2022-11-30 的 1 分钟数据**，覆盖 **Bitcoin / Ethereum / BNB / Cardano** 四个主流币。
- **训练/测试切分：** 前 **6 个月训练**（`2021-12 ~ 2022-05`），后 **6 个月实际交易/报告结果**（`2022-06 ~ 2022-11`）。
- **模型骨架：** 作者不是做固定均线，而是用一个 **带两段滞后输入的三次 polynomial autoregression (PAR)** 拟合局部价格轨迹，再画出一条实时更新的 prediction line。
- **信号定义：**
  - 价格 **向上穿过预测线并超过缓冲带** → `long`
  - 价格 **向下跌破预测线并超过缓冲带** → `short`
  - **持有直到反向信号出现**，也就是一个典型的 `reverse-on-opposite` 结构。
- **缓冲带不是拍脑袋：** 论文对 entry buffer `δ` 做了优化，最终 **四个币的最优 `δ` 都是 `1.5%`**。
- **最佳窗口并不一样：**
  - BTC：最佳是 **67 分钟** 配置
  - ETH：最佳是 **61 分钟**
  - BNB：最佳是 **62 分钟**
  - ADA：最佳是 **47 分钟**
  这说明它不是“一套窗口全币通吃”，而更像每个币各自存在一个 **局部 drift half-life / signal memory**。
- **关键结果：**
  - **BTC：** `+15.58%`，PF `2.30`，PP `71.67%`，对比同期 B&H **`-44.8%`**
  - **ETH：** `+16.98%`，PF `2.04`，PP `66.67%`，对比 B&H **`-33.6%`**
  - **BNB：** `+9.33%`，PF `1.75`，PP `67.6%`，对比 B&H **`+0.28%`**
  - **ADA：** `+4.26%`，PF `1.38`，PP `66.7%`，对比 B&H **`-41.8%`**
- **多空不对称也很明显：**
  - BTC 的 edge 更偏 **short side**：short PF `3.44`，long PF `2.73`
  - ETH 更偏 **long side**：long NP `10.478%`，short NP `6.5%`
  - BNB 明显更偏 **short side**：short NP `7.94%` / PF `3.05`，long NP `1.386%` / PF `1.16`
  - ADA 相反更偏 **long side**：long NP `2.326%`，short NP `1.933%`

## 3. 为什么和当前项目有关
这篇值得进池，不是因为它证明了“曲线拟合也能赚钱”，而是因为它给出了一条很清晰的 **可最小复现单币 alpha 骨架**：

1. **raw alpha 很清楚**：
   价格相对局部预测线的方向偏离，不是别的 alpha 的附属 gate。
2. **和当前积累互补**：
   - 不是横截面打分；
   - 不是 pairs spread；
   - 不是 basis/funding carry；
   - 也不是简单 breakout/retest。
   它补的是 **单币局部 drift-follow** 母策略。
3. **可很快做最小实验**：
   论文本身就是分钟级；对我们 desk 来说，完全可以直接从 `1m / 3m` 开始，然后再压到 `5m / 15m` 的 bar-based 近似。
4. **还能服务后续组件拆解**：
   就算最终原始信号不够强，也能拆出：
   - `prediction-line distance` 作为 feature
   - `directional asymmetry by asset` 作为 regime filter
   - `reverse-on-opposite` 作为 exit logic 候选

## 3.5 策略拆解（必填）
- 方向属性：单币 directional / 局部趋势跟随 / 双向可做
- 基础 alpha：价格相对局部非线性漂移线的突破/跌破会延续，而不是立刻回归
- entry：价格上破 prediction line + buffer 做多；下破 prediction line - buffer 做空
- exit：持有到反向信号；本质上是 `flip-on-opposite`
- sizing：论文没有做复杂仓位；最小复现先单币等权/固定 notional，再加 inverse-vol 或 ATR target
- risk：限制单币最大杠杆、设置波动熔断、news/liquidation spike veto、夜间流动性稀薄时段单独评估
- cost：**论文几乎没把手续费/滑点/资金费建模清楚**，这正是它还不能直接上线的主要缺口
- 更适合的 regime：有持续 order-flow 偏向、局部 drift 明显、而不是高噪音来回抽插的时段
- 主要 veto：极端公告针、低流动性 alt、爆仓连锁导致的单根异常 wick、资金费结算前后微结构扭曲时段

## 4. 可复刻的最小实验
**研究假设：** 论文真正可迁移到 desk 的，不是“非得用作者这套精确 PAR 参数”，而是：

> **用 rolling local curve / local drift line 做 signal anchor，再用 buffer 过滤噪音、用 opposite crossover 做 exit，这条 directional raw alpha 在分钟级 crypto 上可能成立。**

### 最小实验 A：先按论文精神做 1m / 3m 原型
1. **Universe：** Binance USDT perpetual 先取 `BTC/ETH/BNB/SOL/ADA`，优先流动性最足、撮合最稳定的合约。
2. **Bar：** 先做 `1m`，再做 `3m`；这是因为原论文本来就是 minute 级。
3. **信号线：**
   - 方案 A：直接复刻 paper spirit，做 rolling polynomial regression / polynomial autoregression
   - 方案 B：做一个更稳更轻的 proxy：rolling 3 次多项式拟合收盘轨迹，取下一步/当前估计线
4. **窗口：** 先扫 `40/50/60/70/80` 分钟；再折算到 bar-count：
   - `1m`：40~80 bars
   - `3m`：14~27 bars
5. **entry：**
   - `close > pred_line * (1 + δ)` → long
   - `close < pred_line * (1 - δ)` → short
   - `δ` 先不要照抄 `1.5%`；分钟 perp 上太粗，先扫 `10/20/30/40/60 bps`，再加 `k * ATR` 版本
6. **exit：** opposite signal；并额外加一个 `max_hold`（如 `60/90/120` 分钟）做稳健性对照。
7. **成本：** 至少跑三档 round-trip friction：`4 / 8 / 12 bps`；若是 taker-heavy 原型，再加一档更苛刻的 `16 bps`。
8. **比较基线：**
   - plain EMA crossover
   - Donchian breakout
   - 纯过去 `N` bar return sign continuation
   关键是看它到底提供了新 alpha，还是只是换皮 trend-follow。

### 最小实验 B：压缩成 5m / 15m desk 版本
如果 `1m/3m` 原型有形，再做 `5m/15m`：
- `5m` 先扫 `8/12/16` bars（对应约 `40/60/80` 分钟）
- `15m` 先扫 `3/4/5/6` bars（对应约 `45/60/75/90` 分钟）
- buffer 不再用固定百分比，优先试 `0.5 * ATR` / `0.75 * ATR` / `1.0 * ATR`

这样更符合 perp 短周期实盘，而不是死抄论文的 `1.5%`。

## 5. 我对这条线的当前判断
我的判断是：**值得进研究池，而且优先级不低，但要明确它现在仍是“可复现 raw alpha 候选”，不是可直接上线版本。**

原因：
- **优点**
  - base alpha 清楚；
  - 分钟级原生；
  - entry/exit 很完整；
  - 多空双边可做；
  - 和我们最近的 XS / pairs 素材互补。
- **缺点**
  - 论文几乎没严肃处理成本；
  - 只测了 4 个币；
  - 参数优化痕迹较重；
  - 没清楚回答它到底优于 simpler trend baselines 多少。

所以它最适合当前 desk 的姿势不是“直接相信 paper PnL”，而是：

> **把它当成“局部 drift-follow 母策略原型”，先做最小对照实验，确认它是否真的优于简单均线/动量穿越。**

## 6. 下一步最该怎么测
如果只给一个最优先动作，我会做这个：

> **在 Binance BTC/ETH `1m` 上做 `rolling polynomial line + buffered crossover + opposite flip`，并与 `EMA crossover` 和 `Donchian breakout` 做同窗长、同成本对照。**

这是最便宜也最关键的一步，因为它能回答唯一真正重要的问题：

**这篇 paper 提供的是新 alpha，还是只是更复杂的趋势线外观。**

建议最先盯三个输出：
1. 成本后 PF 是否仍 > `1.1~1.2`
2. edge 是否主要集中在 long 或 short 一边
3. `1m` 成立后，压到 `5m` 是否反而更稳

如果这三条里有两条成立，它就值得继续做 desk 化；否则就把它降级成 feature source / exit candidate。

## 7. 来源与可复用材料
1. **Cohen, G. (2023). _Intraday trading of cryptocurrencies using polynomial auto regression_. AIMS Mathematics, 8(4), 9782–9794.**  
   DOI：<https://doi.org/10.3934/math.2023493>  
   Readable URL：<https://www.aimspress.com/article/doi/10.3934/math.2023493>  
   PDF URL：<https://www.aimspress.com/aimspress-data/math/2023/4/PDF/math-08-04-493.pdf>
2. **Repo URL：** 暂未见作者官方复现仓库；更适合按论文规则直接轻量重写。
3. **可直接复用的实现要点：**
   - rolling local curve / prediction line
   - buffer-based entry
   - reverse-on-opposite exit
   - asset-specific long/short asymmetry 统计
