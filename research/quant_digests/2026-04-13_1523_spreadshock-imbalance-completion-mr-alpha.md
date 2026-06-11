# 别把这份 2026 BTC perp microstructure repo 只读成“何时别追”：对 short-cycle desk，更该先测的是「spread-shock completion × imbalance-consistency fade」这条 raw alpha

- 时间：2026-04-13 15:23 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `vortexbar_lab.py` + `ob_poc_v4.py` + bundled PDF report）
- 主题类型：raw alpha
- 基础 alpha：`当盘口价差突然拉宽、且最近几根里主动吃单持续单边时，最值得先测的不是继续追同向，而是等“事件接近走完”后做短持有反转；更直白地说，就是 adverse-selection completion 后的 microstructure mean reversion`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/mean-reversion/adverse-selection/spread-shock/taker-imbalance/volume-bar/domain-score/btc/perpetual/binance/bybit/1m/3m/5m/15m/repo/public-data/risk
- 证据类型：开源代码 + 自带 PDF 报告 + 公共 order-book/trade 数据可复刻

## 1. 这次看了什么

这轮主看的是 GitHub 新仓库 **Woonggyu Lee / `btc-perp-microstructure` (2026)**。

它表面上的读法很容易变成：

> “又一个 order-book / LightGBM / microstructure 研究仓库。”

但对我们 desk，更值得先 intake 的不是“又多了一个微观结构看板”，而是这条**跟现有 continuation 系材料不完全同向**的 raw alpha：

> **base alpha = 当市场制造商因为信息不对称而把 spread 拉宽、且主动成交方向已经持续偏一边时，短窗口里更值得押注“事件完成后的回摆”，而不是继续追最后一脚。**

翻成人话：
- 不是看“现在涨了，所以继续追多”；
- 而是看“这段单边吃单已经把价差打宽、并且开始显得过度拥挤”，然后去测**短持有反打**；
- `domain score` 只是把这类“值得反打”的微观状态再细分得更连续、更可筛选。

所以这轮它是：
- `raw alpha`
- 不是单纯 `filter`
- 不是纯 `regime`
- 但也**还不能直接吹成完整 executable shell**，因为 repo 里主要给的是研究信号与 walk-forward 结果，不是诚实的 live execution / fee / queue-fill 壳。

## 2. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 最值得复现的，不是“预测下一跳继续同向”，而是“spread shock + 单边吃单持续”之后的短持有反转 raw alpha；它补的是我们当前素材池里较少被单独拆开的 `adverse-selection completion -> fade` 分支。**

### 一句话证明方式
> README / 源码把逻辑写得很清楚：价格方向本身几乎像随机游走（README 报 `AC1 ≈ 0.003`），但**什么时候容易出现可交易的短回摆**是可筛选的；repo 报告里，`RT3` 触发器 8-fold walk-forward 的平均 Spearman 为 **0.133**，`Domain Score` 16-fold 全部为正，方向正确率 **59.7%**，再加 trailing 200-event rolling-Spearman 质量过滤后，Spearman 从 **0.130 提到 0.212**，覆盖约 **61%** 事件。注意：这些是 repo 自报结果，默认理解为**未计入真实 taker/maker 成本的研究证据**。

## 3. base alpha 到底是什么

这题最关键的是先把 **base alpha** 说清楚。

### 3.1 不是“价差扩大就追趋势”
`vortexbar_lab.py` 里的 `compute_rt3_trigger(...)` 做了两件事：

1. **`spread_pct`**：当前 spread 在最近一段历史里处在什么分位数。
   - 默认 `spread_window = 500`
   - `spread_pct_on = 0.80`
   - 翻成人话：**“现在的盘口价差，已经进入最近样本里偏宽的前 20% 了吗？”**

2. **`imb_consistency`**：最近 `K` 根里，主动买卖是不是大部分朝同一边。
   - 默认 `imb_consistency_on = 0.75`
   - README 讨论的强化版本是 `K=8`
   - 翻成人话：**“最近这段 aggressive flow，是不是基本都在一个方向上打？”**

代码里先识别 “近期发生过 spread shock + 当前单边吃单还很一致” 的状态，再构出 `entry_direction`。但 README 明确说得很重要：

> **最强信号不是继续同向追，而是事件接近完成后的短期 mean reversion。**

也就是说，真正该拿来做 raw alpha 的，不是“`RT3 ON` 就顺着吃单方向追”，而是：

> **把 `RT3 / Domain Score` 当作“过热完成”检测器，然后做与主导 taker imbalance 相反方向的短持有反打。**

### 3.2 repo 的第二层，其实已经更接近 1m 级可测 alpha
`ob_poc_v4.py` 里还有一层更适合 desk 直接开测的定义：

- 默认 `grid_interval_sec = 60`
- 默认 `max_hold_bars = 15`
- `compute_variable_target_vec(...)`：
  - 先取当前 1 分钟网格上的 `taker_imb` 方向
  - **等第一次 future imbalance 反向翻转时退出**
  - 若 15 根内没翻，就在 `max_hold_bars` 强平

翻成人话：

> **入场方向 = 反着当前一分钟的单边吃单；出场 = 等失衡方向翻回去，或者最多拿 15 分钟。**

这已经不是“抽象研究结论”，而是很接近一条可以写成回测函数的短周期 raw alpha。

## 4. repo 里最有价值的，不是模型名，而是这三个结构

## 4.1 RT3：先抓“有毒单边流”已经打出来的时刻
源码里 `rt3_on` 的核心条件非常朴素：

- 近期出现过 spread shock
- 且最近 `K` 根里，taker imbalance 的方向高度一致

这更像在抓：

> **“单边主动单已经把做市商打得不愿意继续报紧 spread 了。”**

对于 desk，这个状态本身就很值钱，因为它天然对应：
- 追价越来越容易买在尾巴上
- maker 更容易被 adverse selection 打
- 如果事件已经走到后段，反打可能比追单更合理

## 4.2 Domain Score：把“值不值得反打”从 0/1 改成连续分数
`compute_domain_score(...)` 把 6 个组件加总成 `0~6` 左右的连续分数：

1. **streak**：主动成交单边持续多久
2. **ob_opp**：盘口挂单方向是否跟成交方向对着干
3. **low_vol**：短时波动是不是偏低
4. **absorption**：吃单很重，但价格并没有走得一样大
5. **good_hours**：作者经验上更好的时段
6. **3consec**：是否已经连续 3 根同向大波动

翻成人话：

> 它不是在问“会不会涨”，而是在问：**“这更像一段该反打的拥挤尾声，还是一段还没走完的真趋势？”**

README 给出的单调关系也支持这个读法：
- `score 0` 附近接近随机
- `score >= 4` 时 mean-reversion 强度明显更高

这类分数对我们 desk 的好处是：
- 可以做 **hard trigger**（`score >= q` 才开）
- 也可以做 **size ladder**（分数越高，单笔风险越大/越小自己定）
- 或者只把它当 **已有 OFI/continuation 书的 veto**

但要强调：

> **这轮主 digest 还是 raw alpha 本体：`score 高时做反打`；不是把它降级成 shared overlay。**

## 4.3 repo 真正补的是“completion fade”，不是又一个 continuation
我们这段时间已经积了不少：
- OFI continuation
- imbalance continuation
- fair-value shift continuation
- maker skew / quote bias

这份材料的不同点在于：

> **它更像 continuation 分支的反面兄弟：不是看“单边流刚开始时顺着走”，而是看“单边流已经把 spread 打宽、并且趋于完成时反着做”。**

所以它跟现有池子的关系不是重复，而是：
- 同样使用 public trade + depth 数据栈
- 但补的是**不同相位**的 alpha
- 以后很适合做一个 `start-vs-end router`

也就是：
- 早段事件：也许继续看 continuation
- 尾段事件：切换到 completion fade

## 5. 为什么这轮仍值得写，而不是再补一个 pairs / carry
这轮我也刻意卡了一下自己：

> **它为什么比继续补 raw alpha 更值得？**

答案是：**因为它本身就是 raw alpha，而且是跟我们现有 microstructure continuation 池明显不同相位的一支。**

更具体地说，它有三个优点：

1. **base alpha 非常清楚**
   - 不是模糊地说“微观结构有用”
   - 而是明确到：`spread-shock + sustained imbalance -> short-horizon fade`

2. **复现门槛比很多 options / prediction-market 题材低**
   - 数据直接用 Binance / Bybit 公共 trade + depth 就能起步
   - 不依赖奇怪的私有变量或难拿的全市场历史库

3. **能直接扩充当前 short-cycle 原料池**
   - 它不是慢频 macro overlay
   - 不是纯综述
   - 也不是只能给某一条 breakout 书做附庸
   - 它本身就是一条可以独立立项的 microstructure MR raw alpha

## 6. 对 `1m / 3m / 5m / 15m` 怎么映射

这一题对 short-cycle desk 的好处，是它并不只活在亚秒级。

### 6.1 `1m`：最自然的第一落点
`ob_poc_v4.py` 默认就是：
- `grid_interval_sec = 60`
- `max_hold_bars = 15`

所以最自然的第一版不是硬上 100ms 高频执行，而是：

- 每分钟算一次 `taker_imb`
- 同步更新 spread / absorption / streak 等分数
- 当 `domain_score >= threshold` 时
- **做与当前 taker imbalance 相反方向的 1m 反打**
- 出场：
  - imbalance sign flip
  - 或 `1/3/5/15` 分钟 time stop

这对我们很友好，因为直接就是分钟级回测。

### 6.2 `3m`：很适合作为 fast-but-not-HFT 版本
如果 `1m` 太噪，第二步最应该测的是：

- `3 x 1m` 聚合 imbalance sign / score
- 只在连续 2~3 分钟都处于高分状态时开仓
- 持有 `1~3` 个 3m bar

这相当于把“尾声拥挤”再确认一层，减少单分钟假信号。

### 6.3 `5m / 15m`：更像事件桶，而不是机械压缩成普通 candle alpha
这题若直接压成普通 `5m/15m OHLCV`，信息会损失很多，所以更好的做法是：

- 先在 `1m` 生成 event log
- 再把最近 `5m / 15m` 的：
  - high-score event count
  - 平均 domain score
  - 最近一次 event 距今多久
  - 累计单边 imbalance 是否已衰减
  聚成 slower-book 的输入

也就是说：
- **base alpha 的真主战场是 `1m / 3m`**
- **`5m / 15m` 更像事件聚合版或 admission layer**

这点要说清楚，别把它伪装成“一根 15m K 就能还原”的东西。

## 7. 最小可复现实验该怎么做

## 7.1 数据源
**公开可得**，不需要私有 feed：

- Binance USDⓈ-M / Spot：
  - `aggTrades`
  - depth snapshot / diff-book stream（100ms/250ms/1000ms 级别都可）
- Bybit 也可做交叉验证

### 公开性
- 公共 API / WebSocket
- 不依赖账户私有成交

### 更新频率
- trade：实时
- order book：子秒级更新

### 最小复现实验口径
先别一步到位复刻作者 5.4B ticks 全年样本，最小版可以这样：

1. **资产**：`BTCUSDT perpetual`
2. **频率**：
   - 原始层：trade + top-of-book / shallow depth
   - 回测层：`1m` 网格
3. **事件定义**：
   - `spread_pct >= 80%`（rolling percentile）
   - `imb_consistency >= 0.75`
   - `domain_score >= q90` 或 `>= 4`
4. **方向**：
   - `side = -sign(taker_imb)`
5. **出场**：
   - `1m / 3m / 5m / 15m` time-stop sweep
   - 或 imbalance sign flip
6. **成本**：
   - 至少跑 `2 / 4 / 6 / 8 bps per side`
7. **输出**：
   - mean bp/trade
   - hit rate
   - holding-time 分布
   - event rate
   - 不同时段表现
   - 与 continuation 信号的重叠/冲突占比

## 7.2 第一批最该看的不是 Sharpe，而是这 4 件事
1. **事件频率够不够**
   - 如果 1m 上一天只出几次，就不适合当主书

2. **`1m->3m` 是否真的最强，还是只是一分钟噪音**
   - README 已暗示 `1–3 bars` 最强 MR，先验证这点

3. **成本后是否还能活**
   - 这类 microstructure edge 很容易 gross 有、net 没

4. **它和现有 continuation alpha 是互补还是互相打架**
   - 这是后面做 router 的关键

## 8. 这轮最重要的判断

### 8.1 这是 raw alpha，不该降级成纯 filter
先把这个点钉住：

> **base alpha 说得清：就是“单边挤压尾声 -> 短回摆”。**

所以它不是那种“只能服务别的书”的材料。

### 8.2 但目前更像可复现候选，不是现成上线壳
我不愿意把“是否可直接落地完整策略”写成“是”，原因也很简单：

- repo 给了研究逻辑、特征、walk-forward 结果
- 但没有把真实的 taker/maker fee、queue position、slippage、订单撤改单摩擦说透
- README 上最亮眼的指标主要是 Spearman / direction / MR leg，不是成本后净收益

所以对 desk 的正确姿势是：

> **把它收进 raw alpha 素材池，优先做 first-cost verdict；不要因为 README 漂亮就直接把它当 ready-to-trade。**

### 8.3 它的真正战略价值，是补“相位切换”而不是重复 OFI continuation
如果后面这条线成立，它最有价值的用法未必是孤立跑一本新策略，而可能是：

- continuation alpha 负责抓事件前半段
- completion-fade alpha 负责抓事件后半段
- 两者中间用 spread / domain score / elapsed-time 做切换

这对当前 desk 是非常实用的结构增量。

## 9. 下一步怎么测

按优先级，我建议直接这样排：

1. **先做 `1m` event-study**
   - 不上模型，直接规则版：
   - `spread shock + imbalance consistency -> opposite-side fade`
   - 看 `1/3/5/15m` 持有收益曲线

2. **再做 `Domain Score` 分层**
   - 按 `score 0~6` 分桶
   - 看 mean bp/trade 是否单调
   - 先验证 repo 自报的“分数越高，MR 越强”能不能在我们口径复现

3. **和现有 continuation 信号做 overlap matrix**
   - 当 continuation 强、但 completion-fade 也强时，谁赢？
   - 这一步比单独再做一个微观结构 Sharpe 更值钱

4. **补成本与时段压力测试**
   - `Asia / Europe / US`
   - `2/4/6/8 bps`
   - `1m` vs `3m`
   - 只有这一步过了，才值得继续谈 maker/taker 壳

## 10. 来源与元数据

### 10.1 主来源（本轮主 digest）
1. **Woonggyu Lee. (2026). _BTC Perpetual Futures Microstructure Research_. Venue: GitHub repository / bundled research brief. DOI: N/A.**
   - Readable URL: https://github.com/wglee-quant/btc-perp-microstructure
   - Repo URL: https://github.com/wglee-quant/btc-perp-microstructure

### 10.2 理论锚点
2. **Glosten, L. R., & Milgrom, P. R. (1985). _Bid, ask and transaction prices in a specialist market with heterogeneously informed traders_. Venue: Journal of Financial Economics, 14(1), 71–100. DOI: `10.1016/0304-405X(85)90044-3`.**
   - Readable URL: https://doi.org/10.1016/0304-405X(85)90044-3
   - Repo URL: N/A

3. **Engle, R. F., & Russell, J. R. (1998). _Autoregressive Conditional Duration: A New Model for Irregularly Spaced Transaction Data_. Venue: Econometrica, 66(5), 1127–1162. DOI: `10.2307/2999632`.**
   - Readable URL: https://doi.org/10.2307/2999632
   - Repo URL: N/A

## 11. 最后一行结论

> **这份 2026 repo 最值得先收进研究池的，不是“又一个 order-flow dashboard”，而是 `spread-shock completion × imbalance-consistency fade` 这条 microstructure mean-reversion raw alpha。它最适合先在 `1m / 3m` 做 first verdict；若成立，再把 `5m / 15m` 做成事件聚合版或 router 组件。**
