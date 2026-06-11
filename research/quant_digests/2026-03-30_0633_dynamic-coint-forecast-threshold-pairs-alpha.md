# 别把 pairs 只做成 rolling z-score：这篇 2026 Frontiers 更该先测的是「dynamic-coint spread forecast × percentile trigger × PIW gate」完整 raw alpha
- 时间：2026-03-30 06:33 UTC
- 类型：2026 *Frontiers in Applied Mathematics and Statistics* 开放获取全文 HTML + 表格/段落级抽取
- 主题类型：raw alpha
- 基础 alpha：**动态协整关系下的 spread mean reversion**——先筛出仍然维持长期均衡关系的币对，再对未来 spread 偏离做预测；当预测的 spread score 落到下分位就做多 spread、上分位就做空 spread，吃的是相对价格向动态均衡回摆的 alpha，而 **PIW（prediction interval width）只是 sizing / veto 层，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/dynamic-cointegration/spread-forecast/percentile-threshold/prediction-interval-width/uncertainty-gate/eth-bnb/binance/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：开放获取全文论文证据 + 可直接转译的 desk 级策略骨架

> 先把 **base alpha** 说清楚：
>
> **这不是“用深度学习做个过滤器”。真正的 alpha 本体，是动态协整 spread 的均值回归；论文最值得 desk 拿走的，是“预测 spread 偏离 + 分位阈值触发 + 不确定度宽度控仓”这套完整入场骨架。**

## 1. 这次看了什么
这次主看 **Johannes Tshepiso Tsoku, Katleho Makatjane (2026)** 的开放获取论文 **_Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_**（*Frontiers in Applied Mathematics and Statistics*）。

如果只用一句人话概括它最适合我们 desk 的读法：

> **别再把 crypto pairs 固定成“rolling z-score 超过 ±2 就上”。这篇 paper 更值钱的部分，是把 pairs raw alpha 拆成三层：`dynamic-coint pair selection` → `forecasted spread score trigger` → `PIW uncertainty gate`。**

这里最重要的是别把角色搞反：
- **alpha 本体**：协整 spread 的回摆；
- **信号生成器**：对未来 spread 偏离做 forecast；
- **风险/仓位层**：用 prediction interval width 判断“这次 forecast 到底靠不靠谱”。

所以它不是纯 filter，也不是纯 explainability 文献，而是可以独立落成完整策略的一条 **pairs / stat-arb raw alpha**。

## 2. 核心结论
### 2.1 这篇东西真正新增了什么
最近库里关于 pairs 已经积了不少：
- 固定 threshold spread MR
- threshold map / correlation-signed threshold
- cointegration sizing
- OBI veto / 成本生存线
- multi-pair stat-arb

但还相对缺一块：

> **不是“spread 现在离均值多远”，而是“未来几个 bar / 几个时点，spread 偏离预计会不会自己走回去，而且当前预测置信度够不够高”。**

这篇 paper 最值得 intake 的，不是 “DNN/LSTM/ensemble” 这些模型名，而是下面这条可直接 desk 化的骨架：

1. **先做动态协整，而不是静态 pair 关系。**
2. **再预测 future spread / dynamic score，而不是只看当前 z-score。**
3. **最后用 upper/lower percentile thresholds 做交易，而不是死写 ±1σ / ±2σ。**
4. **同时把 PIW 当成 uncertainty gate / sizing dial。**

翻成人话就是：

> **同样都是做 spread MR，paper 的重点不是“看到偏离就赌它回归”，而是“只在模型预计这次偏离会回归、且预测带不算太宽时才上”。**

### 2.2 对 desk 最有价值的一句
如果只偷一句，不是“动态 ensemble 最优”，而是：

> **pairs 的 raw alpha 可以继续保留为 spread MR，但 entry 不一定要盯当前 spread 本身，完全可以改成“预测后的 spread score 是否穿过 rolling percentile thresholds”，再用 PIW 决定这笔要不要降杠杆甚至 veto。**

这句对 `1m / 3m / 5m / 15m` 很有用，因为它天然把整条策略拆成三块：
- `raw alpha layer`：spread MR
- `entry timing layer`：forecast-score percentile trigger
- `risk layer`：PIW width / uncertainty veto

## 3. 3 个关键数据点
### 3.1 样本与结构证据
论文使用 **2018-01-02 到 2025-10-31** 的加密货币价格样本，共 **2,842 个观测**。文中使用 dynamic Johansen cointegration 去识别时间变化的长期均衡关系。

作者给出的一个关键信号是：
- **Trace statistic = `276.319`**
- **95% critical value = `69.819`**
- 第一特征值约 **`0.0773`**

这说明作者确实不是在拿普通相关性硬冒充可交易 spread，而是在主张：

> **先确认存在统计上显著的动态长期关系，再围绕这个 spread 做 MR。**

### 3.2 预测层：ensemble 比单模型更稳
在 spread forecasting 这一层，作者比较 DNN、LSTM 和 dynamic weighted ensemble：
- **Dynamic Ensemble**：`MSE = 0.012124`、`RMSE = 0.110108`、`MAE = 0.083607`、`MFE = -0.043546`
- **LSTM** 在相对误差上最好：`MAPE = 1.490429%`

对 desk 来说，这些数字最重要的含义不是“我们也要马上上深度学习”，而是：

> **spread signal 不一定非得由当前偏离直接触发，完全可以先做一个 forecast layer；只要 forecast layer 真能降低 magnitude error / bias，它就值得当 timing 层。**

### 3.3 信号层：percentile trigger + uncertainty width
论文交易信号部分给了几组很值得记的数：
- 图 6 口径下，**共生成 `113` 个信号**
- 其中 **`81` 笔赢、`32` 笔输**，文中写成 **`71.68%`** 赢率
- 表 4 又给出：**hit rate = `0.5821`**、**avg profit/trade = `0.0111`**、**Sharpe = `1.3662`**、**Sortino = `1.1411`**、**MDD = `-0.2875`**、**correlation with market = `-0.6517`**
- 预测区间宽度方面，作者给出 **平均 PIW = `0.0772`**、最小 **`0.0232`**、最大 **`0.3094`**、期末 **`0.0337`**

这里有两个读法：
1. **正面读法**：forecast-score trigger + PIW gate 这套东西，至少给出了“信号质量 + 风险轮廓”同时可看的完整交易面板；
2. **保留意见**：**`81/113 = 71.68%` 与表 4 的 `hit rate 0.5821` 明显不一致**，说明这篇 paper 更适合当 idea source，而不是拿来逐字符抄参数。

这反而对我们有帮助：

> **它给的最值钱资产不是某个神奇超参数，而是一套可以拆回 desk 骨架的策略结构。**

## 4. 为什么和当前项目直接相关
先回答最关键的问题：

> **它为什么比继续补另一个 generic trend/momentum headline 更值得？**

因为当前素材池里：
- trend / momentum / breakout 已经不少；
- pairs / stat-arb 虽然也在补，但很多还停在 `current spread > threshold` 这一层；
- **“forecasted spread + uncertainty-aware gating” 这种完整 timing 框架还不多。**

所以这篇 paper 的价值非常直接：
1. **它仍然是 raw alpha，不是纯 filter。**
2. **它补的是 pairs raw alpha 的 timing / sizing 组件，而不是再换一种同质化 spread 名字。**
3. **它可以直接落在 `15m -> 5m -> 3m/1m` 的最小实验链路上。**
4. **即使不照搬深度学习，核心框架也能先用轻量模型复现。**

## 5. 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / mean reversion**
- 基础 alpha：**动态协整 spread 的回摆**
- 论文最值得 desk 化的口径：
  - `pair selection`：只保留 rolling 窗里仍通过动态协整/协整稳定性检查的币对
  - `signal core`：预测未来 spread / dynamic score
  - `entry`：forecast score 穿越 upper / lower percentile thresholds
  - `sizing / veto`：PIW 越宽越小仓，宽到阈值外直接不做
  - `exit`：forecast score 回到均值带 / spread 回归中线 / max hold 到期
- 对 desk 的短周期翻译：
  - `15m` 先做信号主时钟
  - `5m` 做切片与二次确认
  - `1m/3m` 只做 execution veto，不要一开始就把整套模型硬压成超高频

## 6. 论文里的完整策略机制，怎么翻成人话
### 6.1 alpha 本体：不是价格方向，而是相对价格错位回摆
这条线的根不是“预测 ETH 明天涨跌”，而是：
- 某个 pair 在动态长期关系下本来应保持某种平衡；
- 现在 spread 偏离了；
- 模型判断这次偏离有较高概率回到中枢；
- 那就做一笔 long-short spread trade。

所以它属于非常标准的 **relative-value / stat-arb raw alpha**。

### 6.2 真正有用的新层：forecast score，而不是裸 spread
很多 pairs 研究都停在：
- 当前 spread 超出某阈值 -> 开仓

这篇更像：
- 先把当前 spread 及其时间结构喂给模型；
- 生成 **predicted dynamic score**；
- 再看它是否穿越 upper / lower percentile thresholds。

对 desk 的意义是：

> **entry 可以从“静态超阈值”升级为“预测后的极端分位事件”。**

这样做的潜台词是：
- 同样都是 `1σ` 偏离，有些会继续发散；
- 有些则已经最容易开始回摆；
- forecast layer 想做的，就是把这两类状态拆开。

### 6.3 PIW 最适合我们的读法：不是 headline，而是 size / veto
这篇 paper 另一块可直接挪走的东西是 **prediction interval width**。

我不会把它读成“又一个 fancy 指标”，而会直接 desk 化成：
- **PIW 窄**：说明模型对 forecast 更有把握，可以正常开仓；
- **PIW 中等**：缩仓；
- **PIW 极宽**：说明不确定度上升，直接 veto。

这特别适合短周期，因为很多 spread 策略不是死在方向错，而是死在：
- 该做的时候仓位太小
- 不该做的时候仓位太大
- 波动结构切换时还在硬做

## 7. 对 desk 最可执行的最小实验
### 7.1 不照抄 daily，不照抄 deep learning，先测最小 transfer
这篇 paper 的原始实现更偏日频 / 中频，而且还存在资产描述和指标口径不完全一致的问题。所以最合理的 desk 路线不是“完整复刻论文”，而是先把它拆成一个 **最小可验证的 pairs full-stack hypothesis**：

> **在 Binance perp `15m` 上，若只保留 rolling 动态协整仍稳定的 majors pair，再用 forecasted spread score 的分位触发入场，并把 PIW/forecast uncertainty 作为 size-veto，那么这条 spread MR 是否比裸 z-score 更像样？**

### 7.2 一个能马上开跑的版本
**Universe**
- 先只跑高流动性 majors pair：`ETH-BNB`、`ETH-SOL`、`BNB-SOL`、`ETH-XRP`、`BTC-ETH`
- 首轮别扩太多 pair，先看 transfer 是否存在

**Sampling**
- 主时钟：`15m`
- execution 细化：`5m`
- 若 `15m` gross 明显活，再往 `5m` 缩；`1m/3m` 先只做 execution veto

**Formation / estimation**
- rolling `30d~45d` 形成窗
- 每根 bar 更新一次 pair 的 rolling 协整检验 / hedge ratio
- spread 标准化后，先不用深度学习，第一轮就做：
  - `AR(1) / ARIMA` baseline
  - `LightGBM` 或轻量 `LSTM` 二选一
- 目标是预测 `next 1~4 bars` 的 standardized spread score

**Entry**
- 若 forecast score > rolling `90th/95th percentile`：做空 spread
- 若 forecast score < rolling `10th/5th percentile`：做多 spread
- 只有在 rolling 协整仍显著、且 hedge ratio 没明显跳变时才允许开仓

**Sizing / veto**
- 用 forecast interval width 或 forecast residual std 做 proxy
- `PIW proxy` 落在最近 `40%` 最窄区间：正常开仓
- 落在 `40%~70%`：半仓
- 落在最宽 `30%`：直接 veto

**Exit**
- spread 回到零轴附近 / forecast score 回到中性带
- 或 `max hold = 4~8 bars`
- 或继续向不利方向再走 `1.0~1.5σ` 直接止损

**Cost**
- 第一轮必须显式扣：
  - `2 / 4 / 6 bps` 单边成本
  - funding 先按持仓穿越结算与否单独记账
- 不要先假设 maker fill；先按 taker 版看生存线

### 7.3 最该先回答的 4 个问题
1. **比裸 z-score pairs 好吗？**
   - baseline：`current z-score threshold`
   - challenger：`forecast-score threshold`
2. **PIW proxy 真能提升净收益/回撤比吗？**
3. **这套东西只在高相关 majors pair 上有效，还是在更分散 pair 也有 transfer？**
4. **alpha 真在 `15m`，还是必须压到 `5m` 才能看见？**

## 8. 风险与保留意见
### 8.1 这篇 paper 不能直接照抄的地方
有几处要明确写出来：
- **样本频率并不高。** 论文主样本是 `2018-01-02 ~ 2025-10-31` 共 `2,842` 个观测，本质更像日频/中频，不是纯 1 分钟高频；
- **资产定义有内部不一致。** 部分段落写 BTC 相关 pair，图表段落又强调 `ETH / BNB / LTC / XRP / USDT`；
- **交易指标也有不一致。** `81/113` 对应的赢率与表 4 的 `0.5821` hit rate 不一致；
- **成本没有写得足够实盘。** 对短周期 desk，这一条非常关键；
- **未见官方策略仓库。** 说明它更适合做 research intake，不适合参数照搬。

### 8.2 但这不影响它进入研究池
因为我们要 intake 的不是“论文里某个神秘最优超参数”，而是：

> **dynamic-coint spread MR + forecast percentile trigger + uncertainty-width gating** 这条完整骨架。

这条骨架对短周期是可转移的，而且能直接服务 pairs / stat-arb 主线。

## 9. 下一步怎么测
1. **先做 `15m` ETH-BNB / ETH-SOL 两对，验证 transfer。** 不要一上来全市场铺开。  
2. **同窗对照三版：** `裸 z-score` / `forecast-score` / `forecast-score + PIW veto`。  
3. **持有期至少拆 `1 / 2 / 4 / 8 bars`。** 这条 alpha 很可能不是 next-bar-only。  
4. **把 PIW 做成正式组件，不要只写在备注里。** 记录每笔交易入场时的 uncertainty decile。  
5. **若 `15m` gross 活、净后死，优先修阈值和 veto，不要先换更复杂模型。**  
6. **若 `15m` 根本不活，再决定要不要压到 `5m`；不要直接跳 `1m`。**

## 10. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-30_0633_dynamic-coint-forecast-threshold-pairs-alpha.md`

## Sources
1. **Tsoku, J. T., & Makatjane, K. (2026). _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_. Frontiers in Applied Mathematics and Statistics, 12, 1749337.**  
   - DOI: `10.3389/fams.2026.1749337`  
   - DOI URL: `https://doi.org/10.3389/fams.2026.1749337`  
   - Readable URL: `https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full`  
   - PDF URL: `https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/pdf`  
   - Repo URL: `未找到论文官方策略仓库（截至 2026-03-30）`
2. **Binance API / market data docs**（论文实时部署段落引用的数据入口）  
   - URL: `https://www.binance.com/`
3. **Yahoo Finance / yfinance**（论文历史样本说明中的数据来源）  
   - URL: `https://finance.yahoo.com/`
