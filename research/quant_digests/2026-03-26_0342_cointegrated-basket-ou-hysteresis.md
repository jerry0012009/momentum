# 别把 basket stat-arb 只当 pairs 扩容：这份 2026 新 repo 更该先测的是「3-leg cointegrated basket + OU alpha + hysteresis bucket」完整 raw alpha
- 时间：2026-03-26 03:42 UTC
- 类型：2026 GitHub 新仓库 + notebook 输出审计 + Binance Futures 公共 `15m/1h/4h` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**对 3-leg cointegrated basket 的 spread 做均值回归交易——先用 Johansen / rolling weights 找稳定组合，再用 OU/z-score 偏离开仓，靠 bucketed sizing / hysteresis / risk-parity 把 spread alpha 变成可执行组合；`regime-aware` 与 `bucket` 是治理层，不是 alpha 本体**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/cointegrated-basket/ou-alpha/hysteresis/bucketed-sizing/risk-parity/crypto/binance/perpetual/15m/1h/4h/repo
- 证据类型：GitHub notebook 输出审计 + 代码规则拆解 + 本地公共数据快检

> 先回答 base alpha：**这篇东西的 base alpha 不是 filter，不是 throttle，也不是 bucket sizing。base alpha 就是“多腿 cointegrated spread 偏离均衡后回归”这条 relative-value / stat-arb raw alpha。** 值得写它，是因为最近 digest 虽然已经补了不少 pairs / spread，但还缺一张更接近 desk 真实部署形态的卡：**不是只做 2-leg pair，而是直接把 3-leg basket、入场滞后、仓位 bucket、组合配重一起拆给你。**

## 1. 这次看了什么
这次主看一份非常新的 GitHub repo：

1. **Sujith Kamme (2026). _Trading Cointegrated Crypto Baskets with Regime-Aware Statistical Arbitrage_. GitHub repository / Jupyter notebook.**
   - Repo：`https://github.com/sujith-kamme/statistical-arbitrage-crypto`
   - 创建时间（GitHub API）：`2026-03-20T03:07:38Z`
   - 主 notebook：`labs/research.ipynb`
2. notebook 的主线不是“单对 pair 回归”，而是：
   - 在一篮子币里找 **2~4 leg cointegrated baskets**；
   - 对 spread 做 **ADF / variance-ratio / half-life / predictability** 筛选；
   - 用 **OU alpha + two-tier regime score** 出交易方向；
   - 再用 **hysteresis / bucketed sizing / risk parity** 做组合落地。

翻成人话：
- 很多 pairs 研究只回答“这两条线像不像会回归”；
- 这份 repo 往前多走了一步，直接回答：
  1. **如果不是两条线，而是 3 条腿呢？**
  2. **如果 spread 的回归强度有高低档，仓位要不要跳档？**
  3. **如果 basket 本身是 market-neutral 候选，最后多个 basket 之间怎么配？**

这比“又一个 z-score pairs demo”更接近我们当前 desk 的素材池需求：**它给的是完整 raw alpha 骨架，而不是只给一个 entry 信号。**

## 2. 核心结论
- **一句话核心结论：** 这份新 repo 真正该先 intake 的，不是“regime-aware”这几个字，而是 **3-leg cointegrated basket spread → OU alpha → hysteresis bucket** 这条完整 raw alpha 链；它在 repo 自带 OOS 输出里是成立的，但对 desk 来说更诚实的短周期读法不是“直接压成 15m 主信号”，而是 **`1h/4h discovery` + `15m execution`**。
- **一句话它怎么证明：** repo notebook 已经把 basket discovery、筛选、OOS、风险中性检验都跑出来；我再把 repo 选出的 4 个 baskets 拿到 Binance perp 上做固定权重 proxy，结果是：**`1h` 还像样，`15m` 直接转负。**

我的 desk 化判断很明确：
- **alpha 本体值得保留；**
- **15m bar-close 直接照抄不值得；**
- 真正该进研究池的是：**用慢一点的发现时钟找 basket，再把短周期资源用在执行，不要把 discovery 和 execution 压成同一个 15m 信号。**

## 3. 3 个最关键的数据点
1. **repo 自带的 walk-forward 结果，不只是“看起来有道理”，而是已经到完整组合层。** notebook 输出显示：
   - `155` 个候选 baskets 经过阈值后只剩 `10` 个；
   - 再做 diversification 后最终只保留 `4` 个 baskets；
   - 这 4 个 baskets 的 **OOS net Sharpe = `1.764`，net cumulative = `5.61%`，max drawdown = `-1.38%`，annual turnover = `7.05x`，entry events ≈ `15/年`**。  
   这说明它不是“多腿越多越好”的故事，反而是在强调：**basket stat-arb 的胜负手先在 admission funnel，再在仓位治理。**
2. **把同一批 baskets desk-transfer 到 Binance perp 后，`1h` 还能活，`15m` 基本就塌。** 我用 repo 最终留下的 4 个三腿 baskets，在 Binance USDⓈ-M 上做固定 train-weight proxy（Johansen 取权重，spread z-score 入场，含 `6 bps` taker-ish 成本）得到：
   - **`1h` 聚合平均：net cumulative `+3.61%`，Sharpe `+4.91`**
   - **`15m` 聚合平均：net cumulative `-3.24%`，Sharpe `-4.74`**  
   这不是“15m 也许差一点”，而是很明显地提示：**这条 alpha 的 discovery 时钟不该被硬压到 15m。**
3. **最好的 basket 在慢时钟上很强，但压快后会反过来伤人。** repo 里最强的一组之一 `OPUSDT / FILUSDT / APTUSDT`，我这边 proxy 的结果是：
   - **`4h`：net cumulative `+15.38%`，Sharpe `+5.06`**
   - **`1h`：net cumulative `+5.85%`，Sharpe `+8.04`**
   - **`15m`：net cumulative `-5.28%`，Sharpe `-6.89`**  
   读法非常直白：**不是 spread alpha 不存在，而是把它压成更快的 bar-level 交易后，噪音和成本先把它吃掉。**

## 4. 为什么它和当前 desk 直接相关
### 4.1 它服务的是哪类 raw alpha
- 分类：**relative-value / stat-arb / cointegrated-basket mean reversion raw alpha**
- 不是：
  - 单独的 regime filter
  - 纯 risk overlay
  - 只讲“怎么配仓”的组合学

### 4.2 它补的是哪块空白
最近 digest 已经有：
- 2-leg pairs
- distance / copula / dynamic-factor / Kalman β 偏离
- funding / basis / spread / basket 类 relative-value

但还比较缺一张**更接近 desk 真实落地的 basket 卡**：
- 不只是“两个币的 spread 回不回”；
- 而是“**三腿组合**能不能更稳、怎么发现、怎么分档开仓、怎么在多个 basket 之间分配 gross”。

所以这篇的价值不在“又证明一次 mean reversion”，而在于它把 **basket discovery → alpha extraction → sizing governance → portfolio layer** 连成了一条完整链。

## 5. 策略拆解（按完整策略卡写）
### 5.1 方向属性
- market-neutral / relative-value / basket stat-arb / mean reversion

### 5.2 基础 alpha
1. 先找一组 `2~4` 个币，使其 log-price 之间存在可交易的 cointegrated 关系；
2. 由 Johansen / rolling weights 构造 spread：
   - `spread_t = w1*log(P1_t) + w2*log(P2_t) + w3*log(P3_t) (+ ...)`
3. 当 spread 偏离其 rolling equilibrium，赌其向中枢回归；
4. 这就是 alpha body。

### 5.3 entry
repo 不是直接写死“z > 2 就开”，而是先构造：
- OU alpha
- two-tier regime score
- 然后再映射到 bucketed / hysteresis position

对 desk 的最小版可先写成：
- `|z| > z_entry` 开仓；
- `z > +entry` 做 short spread；
- `z < -entry` 做 long spread；
- 同时记录 half-life 与最近 spread 波动，防止在明显失稳期追反转。

### 5.4 exit
repo 输出给了两个很重要的 exit 观念：
1. **hysteresis**：不要刚穿阈值就来回翻；
2. **bucketed sizing**：回归强度分层，而不是 all-in / all-out。

desk 最小版可先用：
- `|z| < z_exit` 平仓；
- `max_hold` 超时平仓；
- `|z|` 继续远离时做风险退出；
- 之后再引入 hysteresis 防抖。

### 5.5 sizing
这里是这份 repo 比普通 pairs notebook 更值钱的地方：
- 先把 alpha 映射成离散 bucket；
- 再对 surviving baskets 做 risk parity；
- 最后组合成 portfolio。

换成人话：
- 它承认“信号有强弱档”；
- 也承认“不同 basket 波动不一样，不该同权硬上”。

### 5.6 risk / cost
- half-life 过滤
- stationarity / predictability 过滤
- regime-aware veto
- basket 间 risk parity
- 交易成本明确计入（repo notebook OOS `tcost_bps = 20`）

也就是说，这篇不是只给“alpha 会不会回归”；它直接把 `entry / exit / sizing / risk / cost` 五件套摆齐了。

## 6. 本地最小快检：把 repo 的 baskets 拿到 Binance perp，上快慢时钟看 transfer 边界
### 6.1 数据与口径
- 数据：Binance USDⓈ-M Futures 公共 K 线
- baskets：直接用 repo OOS 最终保留的 4 组 3-leg baskets：
  - `OPUSDT / FILUSDT / APTUSDT`
  - `FILUSDT / NEARUSDT / APTUSDT`
  - `ADAUSDT / ATOMUSDT / CRVUSDT`
  - `DOTUSDT / OPUSDT / LTCUSDT`
- 时钟：`4h / 1h / 15m`
- proxy 规则：
  - train 段 Johansen 固定权重
  - test 段 spread rolling z-score
  - `entry = 1.75 / 2.0 / 2.2`（随时钟加严）
  - `exit = 0.35 / 0.4 / 0.5`
  - `max_hold = 8 / 12 / 24 bars`
  - 成本：按 `6 bps taker-ish` 的 leg turnover 粗记

### 6.2 结果怎么读
#### 先看 aggregate
- **`4h` 平均：net cumulative `+1.60%`，Sharpe `+0.62`**
- **`1h` 平均：net cumulative `+3.61%`，Sharpe `+4.91`**
- **`15m` 平均：net cumulative `-3.24%`，Sharpe `-4.74`**

这组结果最有价值的，不是“1h 比 4h 还高”这件事本身，而是它把边界说清了：
- **这类 basket alpha 还能往 `1h` 压；**
- **但把 discovery 直接压成 `15m` 主信号，当前就是负的。**

#### 再看单 basket
1. `OP/FIL/APT`
   - `4h`：`+15.38% / Sharpe 5.06`
   - `1h`：`+5.85% / Sharpe 8.04`
   - `15m`：`-5.28% / Sharpe -6.89`
2. `ADA/ATOM/CRV`
   - `4h`：`+2.23% / Sharpe 3.05`
   - `1h`：`+3.55% / Sharpe 5.27`
   - `15m`：`-1.83% / Sharpe -3.51`

这说明两个问题：
- 不是所有 basket 都值得继续；
- 但 surviving basket 确实可能在 `1h` discovery 上保留边。

### 6.3 desk 读法
对当前 short-cycle desk，我更愿意把它定义成：
- **primary alpha clock：`1h/4h`**
- **execution clock：`15m`**

而不是：
- `15m` 每根 bar 都重新发现一次 basket、重新交易一次。

## 7. 这条线现在该怎么放进研究池
我的判断：**值得进研究池，而且是 raw alpha 前排，但别误标。**

更诚实的标签应是：
- `raw alpha / basket stat-arb / slower-discovery faster-execution`

而不是：
- `15m always-on spread signal`

也就是说，值得保留的不是“15m 压快后还能赚”；而是：
1. **3-leg basket 比 2-leg pairs 更像可扩展的 relative-value 家族；**
2. **OU alpha + hysteresis + bucket sizing 给了很完整的部署骨架；**
3. **短周期该服务 execution，不该强行接管 discovery。**

## 8. 下一步怎么测（必须）
1. **把固定 train-weight 改成真正的 rolling walk-forward。** 当前 proxy 还是 train-once/test-once；下一轮必须做 `1h` 的 rolling re-estimation，确认不是一次性样本幸运。  
2. **把 `1h discovery → 15m execution` 真正拆成两层。** 不要再跑 `15m` 直接重估 basket；而是用 `1h` 出方向，用 `15m` 做挂单/切片/回归触发。  
3. **把 raw alpha、本地 hysteresis、risk parity 三层拆开 A/B。** 先跑：
   - raw spread z-score only
   - `+ hysteresis`
   - `+ bucket sizing`
   - `+ basket-level risk parity`
   看哪一层真的在贡献净边。  
4. **补资金费与腿流动性约束。** 这类多腿 basket 在 perp 上很容易被 funding / 某一腿容量拖死；下一轮必须记录每条腿的 funding、quote volume、以及最脆弱腿的 participation。  
5. **和现有 2-leg pairs 做正交性检查。** 如果 basket 只是在复制 pair spread 的 beta-neutral 版本，就没必要单独占预算；要验证它是否提供了新的 residual source。  
6. **把仓位 bucket 改成 cost-aware bucket。** repo 里 bucket 更像 alpha-strength bucket；desk 版下一轮应直接加 `expected edge > fee budget` 的 no-trade 条件。  

## 9. 风险与保留意见
- 这是一份新 repo，不是成熟期刊论文；证据强度天然弱于“论文 + 开源代码 + 独立复现”三件套。  
- repo 的 notebook 输出是存量输出，不等于外部独立复核。  
- 我的 Binance 快检是 **desk transfer proxy**，不是 repo faithful replication；它更适合回答“压到 perp 短周期后还有没有边”，不适合拿来否定 repo 原始设定。  
- 当前最明确的负面信息是：**15m direct transfer 不成立。** 所以这条线不该被包装成 bar-by-bar 高频主 alpha。  

## 10. 来源
1. **Kamme, S. (2026). _Trading Cointegrated Crypto Baskets with Regime-Aware Statistical Arbitrage_. GitHub repository / notebook.**  
   - Venue：GitHub repository  
   - DOI：无  
   - Readable URL：`https://github.com/sujith-kamme/statistical-arbitrage-crypto`  
   - Repo URL：`https://github.com/sujith-kamme/statistical-arbitrage-crypto`  
   - Evidence note：repo 创建于 `2026-03-20T03:07:38Z`；主 notebook `labs/research.ipynb` 含 walk-forward、筛选、OOS 与市场中性检验输出。  
2. **Johansen, S. (1991). _Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models_. Econometrica, 59(6), 1551–1580.**  
   - Venue：Econometrica  
   - DOI：`10.2307/2938278`  
   - Readable URL：`https://doi.org/10.2307/2938278`  
   - Repo URL：无  
   - 作用：多变量 cointegration / basket 权重估计的理论基础。  
3. **Avellaneda, M., & Lee, J.-H. (2010). _Statistical Arbitrage in the U.S. Equities Market_. Quantitative Finance, 10(7), 761–782.**  
   - Venue：Quantitative Finance  
   - DOI：`10.1080/14697680903124632`  
   - Readable URL：`https://doi.org/10.1080/14697680903124632`  
   - Repo URL：无  
   - 作用：把多资产统计套利放到组合层与成本层去读的经典地基。  
4. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地产物
- `reports/artifacts/quant_digests/cointegrated-basket-ou-hysteresis_20260326_0340/summary.csv`
- `reports/artifacts/quant_digests/cointegrated-basket-ou-hysteresis_20260326_0340/interval_aggregate.csv`
- `reports/artifacts/quant_digests/cointegrated-basket-ou-hysteresis_20260326_0340/meta.json`
- `reports/artifacts/quant_digests/cointegrated-basket-ou-hysteresis_20260326_0340/*_series.csv`

## 12. 一句话 verdict
**进研究池，而且按 raw alpha 前排保留；但更诚实的 desk 化方向是 `1h/4h basket discovery + 15m execution`，不是把 basket cointegration 直接压成 15m 主信号。**
