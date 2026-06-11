# 别把这篇 2025 新 arXiv 只读成“市场物理”：对 short-cycle desk，更该先测的是「sub-hour fade / 1h-1d follow / overextension veto」这条 horizon-routed raw alpha

- 时间：2026-04-04 21:32 UTC
- 类型：2025 arXiv 全文 HTML source audit（可直接读方法与表格）
- 主题类型：raw alpha
- 基础 alpha：**同一个 own-past price signal，在不同 intraday horizon 下不是固定“永远追涨杀跌”或“永远均值回复”，而是要按时间尺度路由：`sub-hour` 弱趋势更像应当 fade，`1h~1d` 弱趋势更像应当 follow；无论在哪个 regime，过强、过拥挤的趋势都要额外加一个 overextension veto。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/mean-reversion/horizon-router/intraday/sub-hour-fade/1h-1d-follow/overextension-veto/cubic-signal/own-past-return/single-asset/cross-asset/1m/3m/5m/15m/paper/public-method/cost/risk
- 证据类型：论文全文方法证据

## 1. 这次看了什么
这轮故意**不再围着某个固定形态打转**，而是补一条更底层、也更能反哺多类 raw alpha 的东西：

> **同一个价格偏移，什么时候该追，什么时候该反？**

主材料是 **Sara A. Safari, Christof Schmidhuber (2025)** 的 arXiv 全文 **_Trends and Reversion in Financial Markets on Time Scales from Minutes to Decades_**。

它不是 crypto 专论文，但这轮仍值得进池，原因很简单：
1. **方法完整可实现。** 不是只讲抽象机制，文中把 trend strength 直接写成可计算的 `t-stat-like` 信号，再用多项式回归去测未来收益对当前趋势强度的响应。
2. **horizon 正好贴 desk。** 论文显式把 intraday 扩到 **`2 minutes ~ 1 day`**，这和我们要落地的 `1m / 3m / 5m / 15m` 非常接近。
3. **它补的是“路由层”，但不是空滤镜。** 真正可交易的本体仍然是 raw alpha：
   - 一条是 **sub-hour mean reversion**；
   - 一条是 **1h~1d weak-trend continuation**；
   - 再加一层 **强趋势别无脑追** 的 veto。

翻成人话：

> **不是所有短线动量都该追，也不是所有短线冲击都该抄底。关键不是“方向”，而是“这段 move 属于哪个时间尺度”。**

## 2. 先回答：这篇东西的 base alpha 是什么？
这轮必须先把 base alpha 说清楚。

### 2.1 base alpha 不是 filter 本身
这篇东西最容易被误读成“一个关于市场状态的解释框架”。

但对我们 desk，更值得拿来交易化的读法其实是：

- **Raw alpha A：sub-hour 弱趋势反转（fade）**
  - 适用大致 `1m / 3m / 5m` 聚合出来的 `2~32min` 级别冲击；
  - 逻辑：极短周期里，弱趋势整体更像微观结构噪音、tick-size bounce、流动性回补，应该优先做均值回复。
- **Raw alpha B：1h~1d 弱趋势延续（follow）**
  - 适用 `15m` 主线，必要时也可用 `5m` 做执行；
  - 逻辑：到了更长一点的 intraday 尺度，弱趋势开始表现出 herding / delayed reaction 的延续性。
- **Shared veto：强趋势过热时不再无脑顺势**
  - 无论是 fade regime 还是 follow regime，过于显著的趋势都不该线性放大；
  - 这正是论文里 cubic 项最值钱的地方。

所以它不是“只有 filter 没 alpha”。

> **它本质上给了两条可独立跑的 raw alpha，再额外给一层 shared overextension veto。**

## 3. 核心结论（先给 desk 可执行信息）
### 3.1 一句话核心结论

> **对 short-cycle desk，最值得先测的不是“趋势是否存在”这种废话，而是：`sub-hour` 先 fade、`1h~1d` 再 follow，并且两边都要对“太强、太显眼”的趋势做 veto。**

### 3.2 一句话证明方式

> **作者把多资产、多时间尺度的 trend strength 统一成可比较的统计量，再直接回归“下一段收益 vs 当前趋势强度”，结果显示：线性项 `b` 在极短周期为负、在 `≥1h` 转正，而 cubic 项在 `≥1h` 又转负，说明延续不是无限线性的。**

### 3.3 论文里最值钱的 4 个数据点
1. **样本覆盖很硬：** `14 years` 的 futures tick data + `30 years` 日频 + 更长历史；intraday 部分明确做到 **`2 minutes ~ 1 day`**。
2. **总规律：** across asset classes，市场在 **few hours ~ few years** 更偏 trending regime；更短和更长尺度更偏 reversion regime。
3. **极短 intraday（up to 16 minutes）**：线性项 **`b = -0.912%`**，`t = -13.6`；cubic 项 **`c = +0.259%`**，`t = +4.6`。也就是：**弱趋势明显均值回复，但特别极端的 move 反而可能继续冲。**
4. **较长 intraday（≥ 1 hour）**：线性项 **`b = +0.132%`**，`t = +2.9`；cubic 项 **`c = -0.039%`**，`t = -2.8`。也就是：**弱趋势开始延续，但趋势太强时又出现过热回摆。**

## 4. 为什么这轮值得优先，而不是继续补一个固定形态
如果只看最近 digest，raw alpha 素材其实已经很多：pairs、basis、options relative value、maker、single-asset MR、XS ranker 都有了。

这轮更值得补的，不是再找一个“又一个具体形态”，而是补一个**更像通用路由器母体**的原始假设：

1. **它直接服务至少两类 raw alpha**
   - trend / momentum
   - mean reversion / shock fade
2. **它和当前项目文档高度对齐**
   - `LEARNING_TRACK.md` 还在补多周期动量、波动管理、状态过滤；
   - 这篇正好把“什么时候 trend、什么时候 MR”从经验口号推进到可计算规则。
3. **它很适合最小实验，不需要新数据采购**
   - 只要 OHLCV 就能先做第一轮；
   - 不依赖私有订单流、期权全链路或复杂外部数据库。
4. **它能帮助 desk 少走弯路**
   - 很多 1m/3m 策略死法，不是方向完全错，而是把本该做 fade 的 horizon 拿去追，或把本该做 continuation 的 horizon 当成过度反应去接反手。

翻成人话：

> **这轮是在补“追 / 反”的时钟，而不是再补一个局部入场花样。**

## 5. 论文里真正值得 desk 拿走的，不是理论故事，而是信号形状
### 5.1 核心信号不是普通 return，而是“标准化趋势强度”
作者不是直接拿过去收益做回归，而是先把趋势变成跨资产、跨 horizon 可比较的强度量 `φ`：

- 本质上类似一个 **trend t-stat / normalized trend strength**；
- 不同 horizon 下都归一化到可比较；
- 再去看未来收益 `R(t+1)` 对 `φ` 的函数形状。

### 5.2 真正值钱的是这个函数不是直线，而是弯的
论文核心不是“未来收益跟过去收益同号/反号”这么简单，而是：

`future_return ≈ a + b·φ + c·φ^3 (+ 更短周期时再加 φ^5)`

这意味着：
- 不是所有正动量都应该加仓；
- 不是所有负动量都应该反手；
- **趋势强度进入极端区后，边际 alpha 会反过来恶化。**

对 desk 最重要的移植，不是把论文多项式一字不差搬过来，而是先提炼出两个最便宜的决策：

1. **linearity split：** `sub-hour` 与 `≥1h` 的 `b` 号不同；
2. **tail veto：** 无论追还是反，到了极端区都别线性放大。

## 6. desk 化后的最小可复现实验（直连 `1m / 3m / 5m / 15m`）
### 6.1 第一版先做成两本书 + 一个 veto
#### Book A：sub-hour fade
- 数据：`1m` 或 `3m` perp kline
- 构造：
  - 用 `2 / 4 / 8 / 16 / 32 min` 多个 horizon 的 standardized return / trend t-stat
  - 聚合成 `phi_short`
- entry：
  - `phi_short > z1` 做空；
  - `phi_short < -z1` 做多。
- exit：
  - 回到 `|phi_short| < z0`；或
  - 固定持有 `2~6` bars；或
  - 遇到 tail-veto 触发直接减半/平仓。

#### Book B：1h~1d follow
- 数据：`15m` 主线，`5m` 负责更细执行
- 构造：
  - 用 `1h / 2h / 4h / 8h / 1d` 的 standardized trend strength 聚成 `phi_mid`
- entry：
  - `phi_mid > z1` 做多；
  - `phi_mid < -z1` 做空。
- exit：
  - `phi_mid` 回到中性区；或
  - 持有 `4 / 8 / 16` 个 `15m` bar；或
  - 进入 overextension 区间时主动减仓。

#### Shared overextension veto
- 若 `|phi| > z2`：
  - 不追新仓；
  - 已有顺势仓减半；
  - fade 书也不在第一次极端时盲目抄底摸顶，等一根确认后再进。

### 6.2 第一轮参数先别炼丹
先用非常便宜的栅格：
- `z1 ∈ {0.5, 0.75, 1.0}`
- `z2 ∈ {1.5, 2.0, 2.5}`
- fade 持有：`2 / 4 / 6` bars
- follow 持有：`4 / 8 / 16` 个 `15m` bars

### 6.3 Universe
先别全市场乱跑：
- `BTC / ETH / SOL / BNB` 四个高流动 perp 起步；
- 第二轮再扩到 `10~20` 个高流动币。

### 6.4 成本口径
这条线非常吃成本，所以第一轮必须直接跑：
- `4 / 8 / 12 bps` round-trip ladder
- 单独记录：
  - turnover
  - post-cost bps/trade
  - median holding time
  - maker fill 可行性（如果后面要把 Book A maker 化）

## 7. 这轮最关键的“下一步怎么测”
1. **先别把两个 regime 混成一个信号。**
   - 第一轮必须拆开跑：
     - `sub-hour fade only`
     - `1h~1d follow only`
     - `router + veto`
2. **先看 horizon 边界在哪。**
   - 对 crypto，不必假设论文里的边界原封不动成立；
   - 重点测：分界点是 `32m/64m`，还是更像 `45m/90m`。
3. **确认极端区到底是继续冲还是开始钝化。**
   - 论文说 tail 不是线性的；
   - 我们要测 crypto perp 里最极端那段，到底更像：
     - squeeze continuation，还是
     - exhaustion snapback。
4. **15m 先做 clean version。**
   - `15m` 更适合先验证 `1h~1d` weak-trend continuation；
   - 若这层站不住，没必要立刻往 `3m/1m` 压。
5. **若 sub-hour fade 有边但成本后变差，优先试 maker-first 执行。**
   - 这条书天然更像 maker alpha；
   - 如果只能 taker，很多 edge 可能会被 fee 吃掉。
6. **把最终结果写成 router 组件，而不是只记单一策略。**
   - 若验证成立，后面可以服务：
     - breakout 追单前的 allow/veto；
     - MR 策略的 horizon admission；
     - trend 书的 extreme-trend de-risk。

## 8. 风险与保留意见
- **不是 crypto 专论文。** transfer 到 perp 市场必须重测，不能直接拿系数当结论。
- **论文聚合了多资产 futures。** 这种“跨资产 universality”对我们有启发，但也可能掩盖 crypto 特有的 funding、liquidation、全天候交易效应。
- **R-squared 很小。** 这类规律更像“弱但稳定的统计边”，不是一眼暴利神迹；要靠严肃的成本与执行控制。
- **极短周期很容易被手续费和最小价格跳动吞掉。** 如果 `sub-hour fade` 最终只能在 maker 条件下活，就要老实把它归成 execution-sensitive alpha，而不是纸上富贵。

## 9. 来源
1. **Safari, S. A., & Schmidhuber, C. (2025). _Trends and Reversion in Financial Markets on Time Scales from Minutes to Decades_. arXiv.**
   - Venue: arXiv preprint
   - DOI: N/A（当前未见正式 DOI）
   - Readable URL: `https://arxiv.org/html/2501.16772v1`
   - arXiv URL: `https://arxiv.org/abs/2501.16772`
   - Repo URL: N/A
2. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). _Time Series Momentum_. Journal of Financial Economics.**
   - DOI: `10.1016/j.jfineco.2011.11.003`
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2011.11.003`
   - Repo URL: N/A
   - 用途：给“trend continuation 是可交易 alpha”这条主线补经典母体，但本轮真正新增的是更短 horizon 的 follow/fade 切换读法。

## 10. 本轮结论（给后续 intake / replication 用）
这篇东西**值得进研究池，而且应记成 raw alpha 主题，不是纯解释型综述**。

但最诚实的入池方式不是“市场会自己告诉你该追还是该反”，而是：

> **先把 `sub-hour fade` 与 `1h~1d follow` 分成两本书，再用 overextension veto 管住极端区；若 `15m` 这本弱趋势 continuation 先站住，就继续往 `5m` 执行压缩；若 `sub-hour` 那本只在 maker 条件下存活，就把它标成 execution-sensitive mean-reversion alpha。**
