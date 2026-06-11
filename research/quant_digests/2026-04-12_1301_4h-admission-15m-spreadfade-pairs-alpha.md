# 别把这份 2025 cointegration repo 只读成“4h alt-pairs 组合回测”：对 short-cycle desk，更该先测的是「4h pair admission × 15m spread execution」这条 pairs raw alpha，但 15m 直译版明显不过线

- 时间：2026-04-12 13:01 UTC
- 类型：2025 GitHub repo + 配套 PDF report source audit（`README.md` + `Cointegration_backtest.py` + `Cointegration_test_scanner.py` + `Cointegration_top_sharpe_20.py` + PDF full text）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**通过 cointegration / hedge ratio / half-life 选出来的 pair，其 spread 极端偏离后更容易向均值回归；真正有价值的不是“固定做某一对”，而是“先慢频选对，再做 spread fade”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/engle-granger/halflife/pair-admission/spread-fade/risk-parity/binance-perpetual/4h/15m/5m/repo/public-data/cost/risk
- 证据类型：GitHub repo / PDF 报告 + Binance 公共数据 probe

## 1. 这次看了什么
这次看的是 **Tom Chatelon (2025), _Cointegration Trading Strategy Applied to the Crypto Market_**，形式上是一个 GitHub repo + 自带 PDF 报告，不是正式期刊论文。

它最容易被误读成：

> “又一个 crypto pairs 回测，挑 20 对，跑个 Sharpe 很高的组合。”

但按当前 desk 的 intake 口径，更值钱的读法其实是：

> **base alpha 不是“某几个 pair 天生会回归”，而是“先用 4h 慢频 admission 把当前最像 cointegrated 的 pair 选出来，再做 spread fade”。**

这点很关键，因为我们最近已经积累过不少 pairs / stat-arb digest，但很多都还停在“固定 pair + 固定 z-score”。这份材料真正能补的，是 **admission 和 execution 的拆分**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 desk 拿走的，不是它声称的高 Sharpe 组合本身，而是这条清楚的 raw-alpha 拆法：**`4h pair admission` 决定今天做哪对，`spread fade execution` 决定怎么做。**
- **一句话证明方式：** 作者先在 Binance Futures `4h / 730d` 上跑全市场 pair scan，再用 rolling beta、ADF/half-life 过滤、固定 z-score 开平、16bps 成本、risk parity 和 20% vol targeting 做组合回测；我再把它下钻成 `15m` 轻量 portability probe，看这条壳直接压到 short-cycle 后还能不能活。
- 源报告口径里，作者从 **70 个币、2415 对 pair** 起步，最后筛到 **407** 对候选，再取 **Sharpe 最高的 20 对** 进组合。
- 源报告给出的前排个体 pair Sharpe 大致在 **`1.536 ~ 2.462`**，组合在 **5x leverage / 20% target vol** 口径下给出 **Sharpe `4.26`、CAGR `30.05%`、总收益 `69.14%`、最大回撤 `-3.06%`**。
- 但我用 Binance USDⓈ-M 公共 `15m` 数据，把 repo 里最靠前的 5 对（`FLOW/HIVE`、`ADA/XMR`、`ADA/ETC`、`ONE/ZIL`、`NEAR/NEO`）做一个 **120d / rolling 30d / 同样 `entry=2 / exit=0.5 / stop=4 / fee=16bps`** 的轻量直译 probe，结果只有 **`ADA/ETC` 1 对为正（`+2.33%`）**，其余 4 对都明显为负。
- 这 5 对的 **中位数结果** 是：**`9` 笔交易、胜率 `20%`、单笔平均约 `-521 bps`、总收益 `-43.99%`、Sharpe `-7.53`、最大回撤 `-46.84%`**。
- 所以这轮最重要的 first verdict 很直接：**repo 里的 4h pair ranking 不能机械直译成 15m raw alpha；short-cycle 要抄的不是“top20 pair 名单”，而是“admission 机制 + execution 分层”。**

## 3. 为什么和当前项目直接相关
这轮不是为了再写一篇“pairs 也能做”的泛综述，而是为了补一个当前素材池里还不够清楚的点：

- base alpha 很明确：cointegrated spread mean reversion；
- 但真正决定 short-cycle 能不能做的，很可能不是 spread 公式本身，而是 **谁来当今天的 pair**；
- 这正好可以接到我们后续的 `pairs / basket stat-arb / basis / funding / cross-sectional RV` 主线里：
  - `raw alpha`：spread MR
  - `admission`：哪个 pair 当前值得做
  - `execution`：15m/5m 怎么进、怎么出、怎么 clip、怎么降换手

换句话说，这份材料对 desk 的价值不是“提供一组神奇 alt pair 名单”，而是 **把 pairs alpha 从“固定对象”改成“动态录取”**。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral / relative-value / mean reversion
- 基础 alpha：被 admission 选中的 pair，其 hedge-adjusted spread 偏离后更容易回归
- regime：只在 cointegration 关系、残差平稳性、half-life 还有效时启用
- filter / veto：`ADF p-value` 不过线、half-life 太长、`|z|` 未到阈值时不交易
- risk / sizing / execution overlay：rolling beta、`entry=2 / exit=0.5 / stop=4`、`max_hold=200 bars`、风险平价权重、20% vol target、最大杠杆 5x、成本按每笔 `16bps`

## 4. repo 里最值得拿走的，不是收益数字本身，而是这套可执行框架
### 4.1 pair scan 不是点缀，而是 alpha admission 核心
`Cointegration_test_scanner.py` 先在 Binance USDT perpetual 上批量拉历史数据，对大量 pair 跑 cointegration scan；PDF 里写的是：
- 数据源：Binance Futures `klines`
- 频率：`4h`
- lookback：`730d`
- 初始币池：约 `70`
- 初始 pair：`2415`
- 最终进入 cointegration test / 组合选择的候选：`407`

这说明 repo 的重心不是固定做一对，而是 **每天/每轮先筛谁有资格交易**。

### 4.2 交易壳很清楚，几乎就是可直接复现的完整 shell
从 `Cointegration_backtest.py` 和 `Cointegration_top_sharpe_20.py` 看，作者把关键规则写得非常明确：
- rolling beta：**`90d` 窗口**
- spread：`X - beta * Y`
- z-score 开平：**`|z| > 2` 开仓、`|z| < 0.5` 平仓**
- emergency stop：**`|z| > 4`**
- max hold：**`200 bars`**
- cost：**每笔 round-trip `16bps`**
- 进一步过滤：**`p-value < 0.05`、half-life <= 30 天**

这意味着它不是一篇只有观点没有框架的“想法文”，而是一套已经把 **entry / exit / risk / cost / portfolio construction** 写进代码的完整 raw-alpha shell。

### 4.3 top-20 risk parity 组合值得学，但不该直接抄进 short-cycle
`Cointegration_top_sharpe_20.py` 做了三件事：
1. 对单 pair 回测并按 Sharpe 排序；
2. 取 top 20；
3. 用 inverse-vol / risk parity 拼组合，再放大到 `20%` annual vol、杠杆上限 `5x`。

这对我们很有参考价值，但也带来一个很容易踩的坑：

> **源策略的 edge 很可能是“慢频筛 pair + 分散化 + 组合平滑”共同产物，而不是某个 pair 在更短周期上天然稳健。**

## 5. 这轮 `15m` portability probe：为什么说“15m 直译版明显不过线”
### 5.1 快检口径
我没有逐表复刻 repo 的完整动态 `ADF / half-life` 录取流程，而是先做一个更便宜的 short-cycle first verdict：

- 标的：源报告 top 5 pair
  - `FLOWUSDT-HIVEUSDT`
  - `ADAUSDT-XMRUSDT`
  - `ADAUSDT-ETCUSDT`
  - `ONEUSDT-ZILUSDT`
  - `NEARUSDT-NEOUSDT`
- 数据：Binance USDⓈ-M 公共 `15m` klines
- 样本：近 `120d`
- rolling beta：`30d`
- 执行壳：`entry=2`、`exit=0.5`、`stop=4`、`max_hold=200`
- 成本：每笔 `16bps`

本地 artifact：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/tom_ctn_pairs_15m_portability_probe_2026-04-12.csv`

### 5.2 结果不是“稍弱”，而是**直接坏掉**
5 对里只有 1 对保住正收益：
- `ADAUSDT-ETCUSDT`：约 **`+2.33%`**，Sharpe 约 **`0.92`**，3 笔交易

其余 4 对都明显恶化：
- `ONEUSDT-ZILUSDT`：约 **`-9.35%`**
- `ADAUSDT-XMRUSDT`：约 **`-43.99%`**
- `FLOWUSDT-HIVEUSDT`：约 **`-86.91%`**
- `NEARUSDT-NEOUSDT`：约 **`-88.67%`**

从交易形态上看，坏得也很一致：
- 大多数 pair 的 **中位持有期直接顶到 `200 bars`**，说明不是“回不快”，而是**根本没按原想法回去**；
- `FLOW/HIVE` 这种 pair 甚至出现 **28 笔**但单笔平均约 **`-625 bps`**，说明短周期里并不是“多交易就更容易收敛”，反而更像被噪音和结构漂移反复打脸。

### 5.3 desk 该怎么读这个失败结果
这个失败结果不是说：
- pairs 没价值；
- cointegration 在 crypto 不成立；
- repo 没用。

更像是在告诉我们：

> **source 里的 edge 主要属于“4h selection + portfolio smoothing”，不是“把 top pair 名单直接压到 15m 还照样赚”。**

所以对 short-cycle desk，更合理的继承方式不是“照抄 top 20”，而是：
- 慢频做 pair admission；
- 快频只做 execution / rebalance / clip；
- 甚至允许 `15m` 只服务于已经被 `4h` admission 录取的 pair，而不是自己重新发明一套 pairs 世界观。

## 6. 下一步怎么测
这篇东西值得继续，但下一步不能再是“把 15m 阈值多调几轮”。更合理的是：

1. **先完整复刻 source 的 4h admission 引擎**
   - 重做 `cointegration scan + rolling p-value + half-life + top-N ranking`
   - 看当前市场里哪些 pair 仍能过线，而不是沿用 repo 当时的 top pair 名单

2. **把 admission 和 execution 明确拆层**
   - `4h / 1h`：负责录取 pair
   - `15m / 5m`：只负责 execution
   - 比较 `纯 bar-close zscore`、`partial clip rebalance`、`hysteresis band` 三种壳

3. **先测“录取 pair 后再下钻”的收益保存率**
   - 对每个被 `4h` admission 录取的 pair，只在录取窗口内开放 `15m` 交易
   - 看它相对“15m 全时段乱做”的 post-cost 改善幅度

4. **补真实 short-cycle friction**
   - funding
   - 双腿不同步成交
   - 单币重复暴露上限
   - maker/taker 路径

如果这 4 步之后，`15m` 层仍然只是在消耗 edge，那这条材料就该被定位成：
**`4h/1h pair-admission engine`，而不是独立的 short-cycle 直接信号。**

## 7. 风险与保留意见
- 这不是正式期刊论文，而是个人 repo + PDF 报告；优点是规则和代码都写得很实，缺点是外部同行评审和 reproducibility 约束弱一些。
- 我这轮 `15m` probe 是 **轻量直译**，没有完整复刻 repo 的 `p-value / half-life` 动态 gate，所以它更像 portability first verdict，不是作者结果的逐表复现。
- 源报告的漂亮组合绩效，很可能有一部分来自 **组合分散 + 风险平价 + 4h 慢频平滑**；把它强行压到 `15m`，天然就更容易被 microstructure 噪音、token idiosyncratic drift 和手续费吃掉。
- 因为这轮 probe 只测了 top 5 pair，结论是“不能机械下钻”，不是“所有 short-cycle pairs 都不行”。

## 8. 来源
1. **Tom Chatelon (2025), _Cointegration Trading Strategy Applied to the Crypto Market_. GitHub repository + attached PDF report.**
   - Author / Year / Title / Venue：Tom Chatelon / 2025 / *Cointegration Trading Strategy Applied to the Crypto Market* / GitHub repository
   - DOI：无
   - Readable URL：<https://github.com/tom-ctn/cointegration-trading-strategy-applied-to-crypto-market>
   - Repo URL：<https://github.com/tom-ctn/cointegration-trading-strategy-applied-to-crypto-market>
   - PDF URL：<https://raw.githubusercontent.com/tom-ctn/cointegration-trading-strategy-applied-to-crypto-market/main/COINTEGRATION%20TRADING%20STRATEGY%20APPLIED%20TO%20THE%20CRYPTO%20MARKET.pdf>
   - README：<https://raw.githubusercontent.com/tom-ctn/cointegration-trading-strategy-applied-to-crypto-market/main/README.md>

2. **Repo source files audited this round**
   - `Cointegration_backtest.py`
   - `Cointegration_test_scanner.py`
   - `Cointegration_top_sharpe_20.py`

3. **本地 portability probe artifact**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/tom_ctn_pairs_15m_portability_probe_2026-04-12.csv`

## 9. 一句话带走
**别把这份 repo 的 top-20 alt pair 名单直接压进 `15m`；对 short-cycle desk，真正该继承的是“先慢频录取 pair，再快频执行 spread fade”这条分层思路。**
