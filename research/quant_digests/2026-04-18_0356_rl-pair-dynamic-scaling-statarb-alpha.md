# 别把这篇 2024/2025 RL pairs 论文只读成“用深度学习替代阈值”：对 short-cycle desk，更该先拆的是「spread excursion 越深，是否值得加仓」这条 crypto stat-arb 旁支

- 时间：2026-04-18 03:56 UTC
- 类型：2024 *Journal of Risk and Financial Management* 论文全文可读页 + DOI 元数据 + Binance USDⓈ-M `15m` public-data portability probe（`ETH/BTC`、`SOL/ETH`、`BNB/ETH` proxy pairs）
- 主题类型：raw alpha
- 基础 alpha：**pairs / stat-arb spread mean reversion**——先找高度联动的一对资产，估计 hedge ratio，把两者相对价格残差（spread）标准化成 `z-score`；当 spread 偏得过深时，做“long cheap leg / short rich leg”或其反向，赌的是相对价格回归，而不是单边趋势
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（论文已经给出 pair formation、spread、入场/出场、RL action/reward、成本对照；只是 desk 真正更值得先抄的不是整套 RL，而是 **dynamic sizing 这一层**）
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / dynamic-sizing / spread-zscore / hedge-ratio / crypto / btc / eth / sol / bnb / 15m / 5m / paper / public-data / cost / risk
- 证据类型：论文全文 + public-data portability probe

先回答 base alpha：**说得清楚，就是 pair spread mean reversion。** 这不是 filter，也不是纯 overlay 伪装。更准确地说，这篇论文的 headline 看起来像“RL 做 pair trading”，但对我们 desk 更值钱的旁支问题其实是：

> **同样是做 spread fade，仓位是否应该跟着 spread excursion 深度一起变化？**

也就是：不是只问“到阈值了要不要做”，而是进一步问“偏得更离谱时，要不要做得更大”。

## 1. 这次看了什么
主来源：
- **Authors：** Hongshen Yang, Avinash Malik
- **Year：** 2024（published 2024-12）
- **Title：** *Reinforcement Learning Pair Trading: A Dynamic Scaling Approach*
- **Venue：** *Journal of Risk and Financial Management*, 17(12), 555
- **DOI：** <https://doi.org/10.3390/jrfm17120555>
- **Readable URL：** <https://arxiv.org/html/2407.16103v2>
- **Paper URL：** <https://www.mdpi.com/1911-8074/17/12/555>
- **Repo URL：** N/A（本轮未见作者公开实现仓库）

论文做的事并不复杂：
- 数据是 `BTC-GBP` 和 `BTC-EUR` 的 `1m` 数据，样本量约 `263,520` bars；
- baseline 是传统 pair trading（类似固定阈值开平仓）；
- RL 1：让 agent 决定**什么时候开/平**；
- RL 2：再进一步让 agent 决定**开多大**，也就是 dynamic scaling；
- 比较 PPO / A2C / DQN / SAC 等算法，主结果里 A2C 最好。

对我们最重要的不是“RL 名字很新”，而是它把 pair strategy 的一个老问题讲得很直接：

> **spread 偏离的“深度”本身，可能就值得进 sizing 层，而不是只拿来过 entry threshold。**

## 2. 核心结论
- **一句话核心结论：** 这篇东西真正适合当前 desk 的，不一定是整套 RL agent，而是把它简化成一句更容易落地的人话：**同样满足 spread fade admission 时，更深的 `|z|` 偏离，可能值得更重仓，而不是永远 1x fixed size。**
- **一句话证明方式：** 我先读论文主结果和 transaction-cost 对照，再用 Binance 永续公开 `15m` 数据做一个粗糙 portability probe，看“更深 excursion 是否至少带来更高 gross mean-reversion bps”。
- **最重要的 first verdict：** **可以进 raw alpha 素材池，而且更像“完整 pairs 策略里的 sizing branch”。** 但 current liquid-major `15m` proxy 先给出的 verdict 也很重要：**gross 上偶尔能看到“偏得越深、回归越明显”，可一旦把 realistic cost 加进来，naive dynamic sizing 很容易把 edge 全吃掉。**

## 3. 论文里最值得记住的 3 个数据点
### 3.1 主表结果：RL 2（动态仓位）明显强于传统阈值版
论文在默认 `0.02%` transaction cost 下，给出的代表性结果是：
- 传统非 RL pair trading：**8.33%** cumulative return
- RL 1（只决定 timing）：**9.94%** cumulative return（A2C）
- RL 2（timing + quantity，也就是 dynamic scaling）：**31.53%** cumulative return（A2C）

翻成人话：
- 不是“RL 一上来就神奇预测方向”；
- 更像是 **同一条 spread mean-reversion 骨架上，dynamic sizing 那层把收益曲线拉开了。**

### 3.2 降低手续费后，动态仓位版本弹性最大
论文 transaction-cost sensitivity 给出的结果也很像 crypto desk 会关心的东西：
- 在 **0.05%** 费用下：
  - 传统：**5.02%**
  - RL 1：**5.76%**
  - RL 2：**7.40%**
- 在 **0.01%** 费用下：
  - 传统：**9.43%**
  - RL 1：**9.88%**
  - RL 2：**33.99%**
- 在 **0%** 费用下：
  - 传统：**10.54%**
  - RL 1：**9.94%**
  - RL 2：**80.92%**

最该记住的不是绝对数，而是方向：
**dynamic sizing 这条支路，对 friction 极其敏感。** 成本低时很像放大器；成本高时也可能先把自己放大死。

### 3.3 论文真正新意不在“是不是 RL”，而在“让 size 也变成决策变量”
论文自己把两种 adoption 区分得很明白：
- RL 1：决定 timing
- RL 2：决定 timing + quantity

从 desk 实操角度，这个区分非常重要：
- 如果你已经有成熟 pair admission / spread / hedge-ratio 流水线，
- 那你不一定非得先上 RL，
- **先把“size 是否跟 excursion 深度联动”单独拿出来做一个 sizing overlay 实验，往往更便宜。**

## 4. 为什么它和当前项目直接相关
如果只把这篇论文读成“又一个 RL trading paper”，它其实没那么值钱；但如果读成：

> **`raw alpha = spread mean reversion`，`值得先抄的旁支 = excursion-aware sizing`**

那它就和当前 desk 很贴了，原因有 4 个：

1. **base alpha 很硬。**
   是 pair/stat-arb，不是解释型综述，也不是用低频宏观数据硬装成 5m 主信号。
2. **可快速复现。**
   只靠公开 K 线就能先做 `5m/15m` 最小实验，不必等 order book、funding、链上数据全到齐。
3. **它补的是我们当前很需要的“position sizing / risk branch”。**
   最近 intake 里 raw alpha 已经不少；这篇更像是在问：**现有 pair alpha 有没有值得单独拆出来的 size lever。**
4. **它天然适合做负结论。**
   即使最后结论是“gross 有帮助，但 net 不行”，这个结论也很值钱，因为它能阻止 desk 把 fixed-threshold pairs 过早升级成 aggressive size ladder。

## 4.5 策略拆解（必填）
- 方向属性：双资产 / 市场中性 / spread mean reversion
- 基础 alpha：`spread z-score excursion -> mean reversion`
- regime：pair 是否还稳定联动、spread 分布是否还近似平稳
- filter / veto：pair admission（相关性、cointegration、rolling half-life、volume、session）
- risk / sizing / execution overlay：**本篇最值钱的地方就在 sizing**——仓位不是固定 1x，而是让 size 随偏离深度变化；execution 上必须单独做 cost ladder

## 5. public-data portability probe：先看 current majors 上这条支路像不像真的
### 5.1 最小实验设计
我没有硬复刻论文的 `BTC-GBP/BTC-EUR 1m` 场景，而是做了一个更贴近当前 desk 的 portability probe：

- 数据：Binance USDⓈ-M public `15m klines`
- 样本：`2025-12-01` 到 `2026-04-18`
- proxy pairs：
  - `ETHUSDT - BTCUSDT`
  - `SOLUSDT - ETHUSDT`
  - `BNBUSDT - ETHUSDT`
- 估计方法：rolling hedge ratio（20d 窗口）
- 信号：`|z| >= 1.5` 时做 spread fade
- 持有：固定 `8` bars（约 2h）
- 对照：
  - `static size = 1x`
  - `dynamic size = min(|z| / 1.5, 4 / 1.5)`
- 成本代理：round-trip **8 bps**

### 5.2 先给结果，再解释
#### ETH-BTC proxy pair
- `2654` 笔触发
- static gross：**+0.85 bps/笔**
- dynamic gross：**+1.09 bps/笔**
- 但加 `8 bps` 成本后：
  - static net：**-7.15 bps/笔**
  - dynamic net：**-9.52 bps/笔**

这说明：
- deeper excursion 加仓在 **gross** 上有一点帮助；
- 但帮助远远不够覆盖 short-cycle 双腿交易的成本。

#### SOL-ETH proxy pair
- `2883` 笔触发
- static gross：**-1.20 bps/笔**
- dynamic gross：**-1.06 bps/笔**
- 分 bucket 看更有意思：
  - `|z| 1.5~2.0`：**-5.87 bps**
  - `|z| 2.5~3.0`：**+2.38 bps**
  - `|z| 3.0+`：**+3.66 bps**

翻成人话：
- **浅偏离不值得做；深偏离才开始像能回归。**
- 这正是 dynamic sizing / dynamic threshold 值得测的原因。

#### BNB-ETH proxy pair
- `4695` 笔触发
- static gross：**-1.02 bps/笔**
- dynamic gross：**-0.98 bps/笔**
- bucket：
  - `|z| 1.5~2.0`：**-2.33 bps**
  - `|z| 2.0~2.5`：**+1.02 bps**
  - `|z| 2.5~3.0`：**+2.25 bps**

这也在重复同一件事：
- 不是所有 threshold-cross 都值得开；
- 更深的 excursion bucket，gross 上更像真的；
- 但 naive 全覆盖 + 双腿成本，依然会把它压成负值。

### 5.3 这个 probe 最值钱的结论是什么
**不是“这个 pair probe 赚了很多钱”。恰恰相反，最值钱的是它把 dynamic scaling 这件事讲得更老实了：**

1. **它更像一个 gross-alpha amplifier，不是自动过成本的圣杯。**
2. **它和 dynamic threshold / admission 非常难分家。**
   因为 deeper excursion bucket 本来就更像“该做的单”，你不能只加仓、不提高 admission。
3. **如果没有更强的 pair selection，直接对 liquid majors 机械套用，基本大概率先死在换手和双腿成本。**

## 6. 我们该怎么把它改成 desk 可用的版本
### 6.1 不要先抄 RL，先抄“离散 size ladder”
与其上来就 PPO/A2C，不如先做更便宜的版本：
- `1.5 <= |z| < 2.0`：不开，或只做 `0.5x`
- `2.0 <= |z| < 2.5`：`1.0x`
- `2.5 <= |z| < 3.0`：`1.5x`
- `>= 3.0`：`2.0x`

这样先回答的是：
**“加仓有没有独立信息量？”**
而不是把 timing / sizing / reward shaping 一次全缠在 RL 黑盒里。

### 6.2 先让 deeper excursion 和更低频触发一起出现
从本轮 probe 看，更像真的不是“任何 `1.5σ` 都做”，而是：
- **只有更深 excursion 才开；**
- 或者 **浅 excursion 只在更强 pair / 更高 liquidity / 更低 cost 桶里开。**

也就是说，这条线最好先往：
- dynamic threshold
- pair admission
- size ladder

这 3 个方向一起测，而不是只单独测“size 更大”。

### 6.3 成本必须先按最坏情况做，不要按论文最优费率想象
论文里 `0.01%`、`0%` 时 RL 2 的弹性很好看，但对我们 desk 来说，真正要防的是：
- 双腿进出场
- 主动成交比例上升
- signal 深度越大，单腿 liquidity 反而可能越差

所以第一轮最好先按：
- `4 bps`
- `8 bps`
- `12 bps`

三档去压，而不是默认自己拿得到论文里接近最优的交易费率。

## 7. 可复刻的最小实验
### 7.1 最小研究假设
**在 crypto pairs / stat-arb 里，更深的 spread excursion 不只是“更容易触发 entry”，而且可能包含额外信息量：它值得更高仓位，或者至少值得更高 admission 优先级。**

### 7.2 一个 desk-friendly 最小实现
在 `5m` 或 `15m` 上：
1. 从 liquid perp universe 里先选固定候选 pairs；
2. rolling 估计 hedge ratio；
3. 计算 spread 和 `z-score`；
4. 做三个版本：
   - fixed threshold + fixed size
   - fixed threshold + dynamic size
   - dynamic threshold + dynamic size
5. 全部统一用同一套 `max hold / stop / gross exposure cap / cost ladder`。

### 7.3 下一步怎么测
1. **先做 5m / 15m 双频对照。**
   这类 pair fade 很可能在 `15m` 太钝、`5m` 成本又太高；频率点需要单独找。
2. **先把 pair selection 和 sizing 拆开做 ablation。**
   `pair admission only`、`sizing only`、`admission + sizing` 三组必须分开，不然看不清 alpha 来自哪里。
3. **只在 deeper excursion bucket 做 pocket book。**
   本轮 probe 已经暗示 `|z| < 2` 的浅触发很可能是噪音源。
4. **加 maker/taker split。**
   如果 future 版本只有 maker-first 才过成本，那这条线就该归到 execution-sensitive pocket，而不是 broad alpha。
5. **把 RL 推迟到最后。**
   先证明“离散 size ladder 有信息量”，再考虑让 agent 学连续仓位，不然只是更贵地拟合噪音。

## 8. 风险与保留意见
- 论文原始数据是 `BTC-GBP / BTC-EUR 1m`，与当前 Binance perp majors proxy 不是同一环境；本轮 portability probe 只能给 first verdict。
- 本轮 probe 没有做严格 pair formation，也没有做 cointegration / half-life / walk-forward pair ranking；所以它更像 **“dynamic sizing 支路在当前环境下值不值得继续花时间”** 的快检，而不是正式策略回测。
- 结果已经很明确地提示：**size 会放大 gross，也会放大 friction。** 如果 pair selection 不够强，dynamic sizing 只是更快亏钱。
- 所以这轮不应被读成“RL pairs 可直接上线”，而应读成：
  **`pairs raw alpha` 值得继续，`dynamic sizing` 值得保留，但必须在 cost-aware / admission-aware 框架里测。**

## 9. first verdict
这篇材料**值得进研究池，而且属于 raw alpha 主线**，因为它的 base alpha 非常清楚：就是 crypto pairs / stat-arb spread mean reversion。

但对当前 desk，最该先落地的不是“训练一个 RL 代理”，而是：

> **把 dynamic scaling 降级成人类可控的 size ladder / admission ladder，先验证 deeper excursion 是否真的值得更多风险预算。**

如果下一轮要继续推进，我会把它标成：

> **`raw alpha（pairs/stat-arb） + sizing overlay（excursion-aware）` 的高优先级 follow-up**

而不是“已证明 production-ready 的完整 RL 策略”。

## 10. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`
- portability outputs：
  - `reports/artifacts/quant_digests/2026-04-18_rlpairs_dynamicscaling_probe_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_rlpairs_dynamicscaling_probe_trades.csv`

## 11. 来源
1. **Yang, H., & Malik, A. (2024). _Reinforcement Learning Pair Trading: A Dynamic Scaling Approach_. Journal of Risk and Financial Management, 17(12), 555.**
   - DOI: <https://doi.org/10.3390/jrfm17120555>
   - Readable URL: <https://arxiv.org/html/2407.16103v2>
   - Paper URL: <https://www.mdpi.com/1911-8074/17/12/555>
2. **arXiv version**
   - <https://arxiv.org/abs/2407.16103>
3. **Baseline pair trading reference mentioned by the paper**
   - Gatev, Goetzmann, Rouwenhorst (2006), *Pairs Trading: Performance of a Relative-Value Arbitrage Rule*
4. **This round public-data probe**
   - Binance USDⓈ-M public klines API (`15m`, perpetual majors proxy pairs)
