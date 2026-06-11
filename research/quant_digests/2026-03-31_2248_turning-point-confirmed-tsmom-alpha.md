# 别把这篇 2021 动量论文只读成 generic TSMOM：对短周期 desk 更该先测的是「turning-point confirmed continuation」raw alpha

- 时间：2026-03-31 22:48 UTC
- 类型：2021 论文（本地全文）
- 主题标签：raw-alpha/trend/momentum/time-series-momentum/turning-points/confirmed-continuation/structure/1h/15m/5m/crypto/paper/cost
- 证据类型：论文证据（全文）
- 主题类型：raw alpha
- 基础 alpha：当价格已经走出一段**被确认的同向 turning-point 结构**（上升时是更高低点+更高高点，下降时是更低高点+更低低点）后，后续再延续至少一个 momentum cycle 的概率显著高于随机
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（entry/exit 与成本口径较清楚，但仓位、实盘确认延迟与滑点处理仍需 desk 自补）

## 1. 这次看了什么
这次看的是 **Oliver Borgards (2021)** 的 **_Dynamic time series momentum of cryptocurrencies_**。  
它表面上是在讲“crypto 也有 time-series momentum”，但对我们更值钱的不是这个 headline，而是论文里那套**不用固定 lookback / fixed holding period，而是直接用 turning points 把趋势切成 formation cycle 与 continuation cycle** 的方法。

这篇东西之所以值得 intake，不是因为我们缺第 N 篇“动量有效”论文，而是因为：

1. 最近 intake 已经堆了很多 **pairs / stat-arb / relative-value / carry**；
2. 当前主线文档里，趋势家族仍然是核心学习线；
3. 这篇给的是一个**不同于均线 / Donchian / 固定回看收益**的 trend raw alpha 骨架；
4. 它还顺手回答了一个很 desk 化的问题：
   **什么时候 continuation 比“看起来像趋势”更可信？——当价格已经确认跨过上一个关键 turning point 时。**

## 2. 先回答：这篇东西的 base alpha 是什么？
这篇东西的 **base alpha 很清楚**：

- 先用平滑滤波识别价格 turning points；
- 把一个完整的上升/下降结构定义成 **formation cycle**；
- 若 formation cycle 之后还能继续接出新的同向 cycle，就把它视作 **momentum period**；
- 交易上不是预测“下一根涨跌”，而是赌：
  **已确认的同向结构，继续延续至少一个 cycle 的概率偏高。**

所以这不是 filter，也不是解释型论文。  
**核心 alpha 本体就是结构确认后的趋势延续。**

## 3. 一句话核心结论
**最值得先测的不是固定 N 根收益动量，而是“formation cycle 完成后，继续跟随已确认 turning-point 结构直到链条断裂”的 continuation raw alpha。**

## 4. 一句话说明它怎么证明
作者用 **20 个加密货币、2014-2019、1D / 1h / 5m** 数据，把价格切成连续 momentum cycles，再直接比较 formation period 后是否真有后续同向 cycles，并回测一套 **formation 完成即入场、cycle 失效即离场** 的交易规则，还显式扣了 **0.2%/trade** 成本。

## 5. 为什么它和当前 desk 有直接关系
对我们现在这条研究主线，它补的是一个很具体的缺口：

- 不是继续往 pairs / carry 里加更多 admission layer；
- 也不是把 trend 继续锁死在 EMA / breakout / retest 里；
- 而是补一条 **structure-aware trend raw alpha**。

它和当前学习地图是对齐的：

- `MAINLINE1_STRATEGY_FACTOR_MAP` 里，趋势跟随仍是核心；
- `LEARNING_TRACK` 里，趋势/动量仍是主线 1；
- 最近 digest 已经明显向 pairs、relative value、carry 倾斜；
- 所以这轮回补一个**趋势 raw alpha 家族**，比再写一个新 filter 更值得。

更重要的是，这篇论文给 trend family 带来的不是“再换一个指标”，而是一个新拆法：

- **固定 lookback 动量**：先拍一个回看窗口，再问未来是否延续；
- **turning-point continuation**：先确认价格已经形成一段结构，再问这段结构是否会继续链式延续。

对短周期 desk 来说，后者更接近真实下单语言。

## 6. 论文里最值得 desk 化的，不是 broad momentum，而是「confirmed turning-point continuation」
### A. formation cycle 不是“涨了几根”，而是一个完整结构
论文不是简单看 `ret_t-k:t`。
它把一个 momentum cycle 定义为一组连续 turning points：

- 上升结构：低点抬高 + 高点抬高；
- 下降结构：高点降低 + 低点降低。

第一个完整 cycle 叫 **formation period**；
如果后面还能继续接出同向 cycle，就进入 **momentum period**。

这很重要，因为它把“趋势开始了”从模糊的视觉感觉，改写成了**结构已被确认**。

### B. 真正更适合 desk 的旁支：critical point 被越过后，趋势常常会再加速一下
论文里一个很值钱、但不必照抄原始大框架才能用的旁支，是：

- 在 momentum cycle 的衔接处，
- **价格在真正越过前一个关键 extreme 之前和之后，行为不一样**；
- 一旦越过这个关键点，相当于“continuation 被确认”，后续往往会出现更强的同向 price impulse。

这对 desk 的意义比“crypto 有动量”更大：
**它给了一个结构确认型 entry trigger，而不是只会说 past return 为正就买。**

### C. 它天然允许 long / short 双边
论文不是只讲上涨 continuation。  
在负向 cycles 上，它同样研究了下降结构的延续。

这对 crypto desk 很关键，因为：

- 我们不想只拿牛市追涨版本；
- 下降结构的 continuation，往往更陡、更快、更像短周期可交易 pocket；
- 这比很多只适合单边牛市的动量论文更实用。

## 7. 关键数据点
先记最有 desk 价值的 4 个数据点：

1. **样本与频率**：20 个 crypto，`2014-01-01 ~ 2019-12-31`，覆盖 `1D / 1h / 5m`。  
2. **结构延续确实存在**：作者报告 crypto 在各频率上都能观察到 formation cycle 后继续出现后续 cycles，且平均 cycle 数普遍高于股票基准。举例说，**正向 momentum period 的平均 cycle 数**：
   - `1D`: `1.761`
   - `1h`: `1.691`
   - `5m`: `1.471`
3. **1h 频率在扣 0.2% 成本后仍存活**：
   - long momentum net total return：`+308.9%`
   - short momentum net total return：`+268.2%`
   - buy-and-hold gross total return：`+190.8%`
4. **5m 版本被成本打穿**：
   - 5m long net total return：`-1164.0%`
   - 5m short net total return：`-1169.8%`
   这说明它**不是不能做快，而是不能 naïve 地用论文原始触发频率直接高换手照抄。**

这 4 个点基本已经把 desk 最关心的事说清了：

- 有 raw alpha 吗？有；
- 主要活在哪？更偏 `1h / 可下采样到 15m 执行`；
- 最容易死在哪？`5m` 纯硬跑的成本与 churn。

## 8. 如果把它翻成 desk 语言，策略骨架是什么
### 策略骨架
- **方向属性**：trend / momentum / continuation
- **base alpha**：formation cycle 完成后，已确认结构更可能继续链式延续
- **trigger**：前一个关键 turning-point extreme 被有效突破/跌破
- **exit**：同向 cycle 不再成立，或出现反向 confirmed turning structure
- **regime**：趋势更顺、噪音更低、成本可控的市场段
- **overlay**：cost gate / volatility gate / churn veto

### 论文原始交易规则（最值得先忠实复现的一版）
作者的规则很朴素：

- 当新的正向 formation period 完成时做多；
- 当新的负向 formation period 完成时做空；
- 只要 momentum cycle 条件还成立就继续持有；
- 一旦链条断掉就退出；
- 统一假设交易费 `0.2%/trade`，先忽略滑点。

也就是说，**它不是预测 next bar，而是持有“已经被确认的结构”直到失效。**

## 9. 对我们最值得先测的，不是论文原版 5m，而是 3 个更 honest 的 desk 化分叉
### 分叉 1：1h 结构信号，15m 执行
这是我认为最优先的一版。

原因：
- 论文里真正 survives cost 的是 `1h`，不是 `5m`；
- 但我们 desk 默认执行层又更偏 `5m / 15m`；
- 所以最自然的 desk 化不是硬把结构识别也降到 `5m`，而是：
  **`1h` 做结构确认，`15m` 做执行与风控。**

### 分叉 2：只交易“critical point exceedance”后的 continuation pocket
也就是别照搬整段 momentum period，只交易最有信息密度的那一小段：

- formation cycle 形成；
- 价格真正穿过前一个关键 extreme；
- 只持有一个有限窗口（例如 `2~6` 个 15m bar，或 `1~3` 个 1h bar）；
- 不贪完整周期。

这更像短周期 desk，而不是学术意义上的 full-cycle 持有。

### 分叉 3：把它作为 trend family 的 shared confirmation layer
如果 baseline trend alpha 本身更简单（比如 EMA / breakout / Donchian），也可以把这篇论文拆成一个 **continuation confirmation gate**：

- breakout 之后，
- 只有在 turning-point 结构也确认延续时才加仓/保留；
- 若只是假突破但结构没完成，就 veto。

这时它就从主 alpha，变成 **服务于趋势 alpha 的 confirmation layer**。

## 10. 这条线的明显短板
### 短板 1：turning point 识别天然容易带“确认滞后”
这篇东西最需要防的，不是传统 overfitting，而是**结构确认和实时可交易之间的时序错位**。

如果你在回测里把 turning point 标得太理想化，很容易把未来信息偷进来。  
所以 desk 复现时必须区分：

- `pivot identified`（事后知道）
- `pivot confirmed and tradable`（当时真的能下）

### 短板 2：论文样本是 Bitfinex spot，不是我们现在常做的 perp
这会影响：

- 手续费层级
- 做空摩擦
- funding/basis 扰动
- 微观结构与成交活跃时段

所以不能把论文数值直接搬到 Binance/Bybit perp。

### 短板 3：5m 在论文口径下已经明确被成本打穿
这其实反而是好事，因为它强迫我们诚实：

- 不能看到 5m gross return 高就激动；
- 要先承认 churn 可能是这类结构动量的第一杀手；
- 真正要做的是 **降噪 + 降换手 + 结构确认后只吃最肥一段**。

## 11. 我对这篇东西的判断
我不会把它读成“又一篇说动量有效”。  
我会把它放进研究池，作为：

**趋势 raw alpha 家族里，一个不同于 fixed-lookback momentum 的结构确认 continuation 模板。**

更具体说，它的价值排序大概是：

1. **primary**：trend raw alpha 候选
2. **secondary**：trend strategy 的 continuation confirmation layer
3. **tertiary**：帮助我们重写 breakout / retest / EMA 类模板里的“什么时候继续持有更合理”

如果后续 transfer check 不行，它至少也会留下一个可复用模块：
**confirmed turning-point continuation gate**。

## 12. 下一步怎么测
直接做一个 **A / B / C 三层实验**。

### A. 原始论文忠实 desk 化
目标：先验证这条 alpha 在今天的公开 crypto 数据上还有没有边。

- 市场：Binance 或 Bybit USDT perp majors
- 频率：`1h`
- turning point：只允许使用**已确认** pivot
- entry：formation cycle 完成后入场
- exit：cycle 失效 / 反向结构确认
- 成本：先跑 `2 / 4 / 6 / 10 bps per side`

**先回答：1h 结构 continuation 在 modern perp 上还活不活。**

### B. 1h 结构、15m 执行
目标：把它真正翻成 desk 口径。

- `1h` 负责信号确认
- `15m` 负责入场、减仓、time stop
- 加 `ATR` 或 realized vol 做仓位缩放
- 记录 average hold、turnover、延迟确认损耗

**先回答：结构信号能否下采样成 15m 可执行 alpha，而不是只停留在论文频率。**

### C. critical-point pocket 版本
目标：测试“只吃确认后的第一段加速”，是否比持有完整周期更优。

- 只在价格越过前 extreme 后开仓
- 只持有固定窗口（如 `2~6` 个 15m bar）
- 与完整持有版本对比：
  - post-cost Sharpe
  - PF
  - MDD
  - win rate
  - turnover
  - MAE / MFE

**先回答：对短周期 desk，最值钱的是整段趋势，还是确认后的那一段加速 pocket。**

### 第一轮必须输出的指标
- trade count
- gross / net return
- PF
- Sharpe
- MDD
- average hold time
- average bars-to-confirmation
- confirmation lag cost
- long / short 分开表现
- bull / bear / chop regime 分开表现

## 13. 来源
1. **Borgards, O. (2021). _Dynamic time series momentum of cryptocurrencies_. North American Journal of Economics and Finance, 57, 101428.**  
   - Authors: Oliver Borgards  
   - Year: 2021  
   - Venue: North American Journal of Economics and Finance  
   - DOI: `10.1016/j.najef.2021.101428`  
   - Readable URL: <https://doi.org/10.1016/j.najef.2021.101428>  
   - Accepted-version URL: <https://centaur.reading.ac.uk/100181/>

2. **University of Reading CentAUR accepted version（可读全文入口）**  
   - Readable URL: <https://centaur.reading.ac.uk/100181/>  
   - 用途：获取正文、方法与表格细节；本次 digest 的关键数值均据此整理。
