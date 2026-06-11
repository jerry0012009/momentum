# 别把这份 Cartea-Jaimungal pairs repo 只当 textbook 复刻：对 desk 更该先测的是「OU half-life gate × wide-band spread MR」raw alpha

- 主题类型：raw alpha
- 基础 alpha：beta-hedged cointegration spread mean reversion（pairs / stat-arb / relative value）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但要把 band、half-life、成本一起管
- 时间：2026-04-01 04:28 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/ou/optimal-stopping/band-widening/half-life-gate/threshold-governance/binance/perpetual/5m/15m/1m/3m/repo/book/public-data/cost
- 证据类型：2025/2026 GitHub repo source audit（`README.md` + `band_calc.py` + `backtest.py` + `config.json` + `run_and_rank.py`）+ Cartea/Jaimungal 经典 co-integrated assets 文献锚点 + Binance `5m` 本地 threshold-transfer quick check

## 1. 这次看了什么

这次主材料不是新论文，而是一份 **2025-12 创建、2026-01 更新** 的新 repo：

- GitHub：`djienne/pair_trading_cartea_jaimungal_penalva`
- repo 自己写得很直白：**rolling cointegration + OU process + optimal trading bands + fee-aware backtest**

表面看它只是把教科书里的 pairs trading 代码化，但对我们 desk 真正有价值的，不是“又一个 cointegration spread 回归”，而是它把下面这条链条连完整了：

1. **spread 不是只看 z-score**，而是先估 OU；
2. **entry band 不是拍脑袋定 1σ / 2σ**，而是显式把交易成本塞进 band 计算；
3. **不是所有 stationary spread 都值得做**，half-life 太慢、beta 太离谱、band 太窄，都该直接 veto；
4. **pairs 的 base alpha 仍然是 raw alpha**，但能不能落地，主要卡在 `half-life × threshold × cost` 这三个旋钮上。

它和我们最近那批 pairs digest 的区别在于：

- 不是继续讨论“有没有 pair”；
- 不是继续找“哪个参数点最好看”；
- 而是更明确地把 **OU half-life / optimal band / fee-aware widening** 提成核心组件。

## 2. 先回答：这篇东西的 base alpha 是什么？

一句话：

**base alpha = 两个近 cointegrated 资产的 beta-hedged spread 偏离均衡后，向长期均值回归；在 spread 足够偏、且回复速度足够快时做反向收敛。**

所以它是标准的：

- `pairs`
- `stat-arb`
- `relative value`
- `mean reversion`

不是 filter，不是 overlay，不是纯解释型材料。

如果把 repo 里那层 OU / optimal stopping 数学全拿掉，raw alpha 本体仍然成立；但如果不把 **band widening** 和 **half-life gate** 写进去，实盘上通常会被过度交易和成本吞掉。

## 3. 这份 repo 最值得 desk 抄的到底是什么

### 3.1 `band_calc.py` 的重点不是“数学更高级”，而是 **band 要对 cost 有反应**

repo 在 `band_calc.py` 里不是简单用固定 `k * std` 设阈值，而是：

- 先对 rolling spread 估 `kappa / mu / sigma`
- 再把 `transaction_cost` 塞进 `CointOpti(...)`
- 然后通过数值积分 + root solve 去找 long/short 最优 entry band

翻成人话：

> **band 不是固定参数，而是“回复速度、波动、成本”共同决定的 admission hurdle。**

这比很多 short-cycle pairs repo 诚实，因为后者往往默认：

- spread 偏了就进；
- 回均值就出；
- 成本只是回测最后扣一下。

而这份 repo 的做法更像：

- 先问“偏这么一点值不值得动手”；
- 再问“动手以后，均值回复能不能快到覆盖成本”。

### 3.2 `backtest.py` 的骨架足够完整，已经不是“只会画 z-score 图”

repo 的交易状态机很直接：

- `z <= lower`：做多 spread（long Y / short beta * X）
- `z >= upper`：做空 spread
- 回到 `mu`：平仓
- 手续费按每次调仓的交易额显式扣减

它没有把仓位管理做得很复杂，但这反而适合 desk intake，因为你能清楚拆出：

- **entry**：band break
- **exit**：mean cross
- **sizing**：1 : beta 的 beta-neutral package
- **risk**：靠 band、mean exit、后续可加 half-life timeout / structure break kill-switch
- **cost**：按 turnover 扣 fee

也就是说，它已经是一个完整策略骨架，不只是“信号候选”。

### 3.3 `run_and_rank.py` 的意义：先在全市场找“可交易 pair 供给”，再谈单对优化

repo 支持：

- 扫描可用符号
- 两两配对
- rolling calibration
- backtest ranking

这点对 desk 很重要，因为 pairs 不是单一 alpha，而是**供给池**：

- 今天活的是 `ETH-ADA`
- 明天活的是 `AVAX-ETH`
- 后天可能整池都不值做

所以真正该测的，不只是某一对，而是：

> **在给定频率、给定成本下，市场里有多少对 pair 能稳定供给正 alpha？**

## 4. desk 角度的核心判断：别把“optimal stopping”当主角

这次最值得带走的不是“我也要马上把 free-boundary 数值解搬进主线”。

更重要的，是先把它读成一句更朴素的话：

> **short-cycle pairs 最怕的不是没偏离，而是 band 太窄、回复太慢、交易太勤。**

所以对我们更有价值的，不是 headline 里的 optimal stopping 四个字，而是它隐含的三条策略纪律：

1. **只做回复快的 spread**（half-life gate）
2. **只做偏离足够深的 spread**（wide-band admission）
3. **band 必须随成本变宽，而不是固定死**

这三条都能直接迁移到 `1m / 3m / 5m / 15m` 的最小实验里。

## 5. 本地最小 quick check：我没有硬复刻 free-boundary solver，而是先测它最关键的 desk 含义

### 5.1 数据与口径

为了避免把 repo 的日频回测结果硬搬成结论，我做了一个更小、更快的 `5m` transfer check：

- 数据源：本地已有 Binance `5m` 样本
- 标的池：`ADA / AVAX / BNB / DOGE / ETH / LINK / SOL / XRP`
- 样本长度：每个品种 `1500` 根 `5m` bar（约 5.2 天）
- pair 数量：`28` 对
- rolling window：`288` 根 `5m` bar（约 1 天）
- spread：rolling OLS `y - (alpha + beta * x)`
- mean-reversion 速度代理：spread AR(1) 推 half-life
- gate：只保留 `half-life < 144 bars`（小于半个 formation window）且 `|beta| < 10` 的时点
- backtest：
  - long/short beta-neutral package
  - 触发后持有到 spread 回均值
  - 手续费先做 one-way `6 bps` 与 `10 bps` 的简化 proxy

注意：

- 这不是 repo 原版数值解的逐行复刻；
- 它只是在测 **“band 是否该放宽、half-life gate 是否有必要”**；
- 所以这轮证据属于 **desk transfer proxy**，不是正式 alpha 认证。

### 5.2 结果一：**1σ 真的太窄，均值上直接变负**

在 one-way `6 bps` 成本下，对全部 `28` 对 pair 做 threshold sweep：

- `1.0σ`：
  - 平均收益 **-0.51%**
  - 仅 `14 / 28` 对为正
  - 中位交易次数 **36**

这行结果非常值钱，因为它几乎把 repo 的核心直觉用最小实验复读了一遍：

> **窄 band 会把你推向高频噪声交易，而不是更高 edge。**

### 5.3 结果二：**band 放宽到 2.5σ 左右，平均结果反而最好**

同样是一批数据、同一套 pairs proxy，在 one-way `6 bps` 下：

- `2.0σ`：平均收益 **+1.03%**，正收益 `17 / 28`，中位交易 `18`
- `2.5σ`：平均收益 **+1.46%**，正收益 `18 / 28`，中位交易 `15`
- `3.0σ`：平均收益 **+1.25%**，正收益 `20 / 28`，中位交易 `9`

也就是说：

- `2.5σ` 给了这轮样本里最好的**平均回报**；
- `3.0σ` 虽然平均回报略低，但**正收益 pair 数更多**，更像“稳一点但慢一点”的版本；
- 最强单对从窄 band 的 `AVAXUSDT-ETHUSDT`，切到宽 band 后变成 `ADAUSDT-ETHUSDT`，说明 **赢家 pair 会随阈值改变，不是固定一对吃天下**。

### 5.4 结果三：**half-life 确实不该只是报表字段**

这批最靠前 pair 的 median half-life 大多在：

- `12 ~ 18` 根 `5m` bar
- 也就是约 **60 ~ 90 分钟**

这正好落在我们能接受的短周期回复速度区间里。

翻成人话：

- 如果一个 spread 需要 `6h / 12h` 才回复，`5m` 上你大概率已经不是在做短周期 stat-arb，而是在扛结构性偏离；
- 如果 half-life 本来只有 `60~90m`，那它更适合被做成 `5m` 主信号，`15m` 做 gate / disable。 

### 5.5 结果四：成本上去以后，宽 band 还没立刻死，但别高兴太早

在 one-way `10 bps` 的更重成本假设下：

- `2.5σ`：平均收益 **+1.08%**，正收益 `16 / 28`
- `3.0σ`：平均收益 **+1.02%**，正收益 `19 / 28`

这看起来还活着，但这里必须诚实：

1. 样本只有约 `5.2` 天，太短；
2. 没有 maker/taker 混合、滑点、资金费、冲击成本；
3. 只做了最小 package proxy，没有盘口成交约束。

所以正确结论不是“这就能直接实盘”，而是：

> **这条线至少证明了：把 band 放宽、把回复速度写进 gate，并不是纸上谈兵；在极简 5m proxy 里它确实改善了可交易性。**

## 6. 这条主题为什么值得进当前素材池

因为它不是单纯再写一遍 pairs 教科书，而是刚好补到当前 desk 最缺的那块：

### 6.1 它补的是 **threshold governance / admission logic**，不是又一个 signal 壳

pairs 的 alpha 本体我们已经有很多变体：

- static cointegration
- dynamic cointegration
- Hurst / ADF / OU
- basket / multiquote / multi-spread

但真正上线最容易出事的，是：

- threshold 定得太随意
- half-life 只看不管
- band 不随成本变化

这份 repo 给的价值，就是把这三个问题拎出来做成显式组件。

### 6.2 它对 `1m / 3m / 5m / 15m` 都有可迁移意义

- `1m / 3m`：更适合做 **entry trigger + maker priority + execution veto**，band 应更宽
- `5m`：最适合做完整 signal transfer，先看 spread 回复能否穿过成本壳
- `15m`：更适合做 **relationship gate / pair availability refresh / disable state**

所以它不是只能服务一条慢频线，而是可以拆成：

- `5m raw alpha skeleton`
- `15m regime / gate`
- `1m / 3m execution layer`

## 7. 如果要把它变成完整 desk 策略，我会怎么写

### 7.1 Entry

- 先做 rolling OLS / rolling Bayesian hedge ratio
- 只在 `half-life < H_max`、`beta` 稳定、spread 波动足够的窗口开仓
- entry band 不用固定 1σ / 1.5σ，先从 **2.0σ ~ 3.0σ** sweep

### 7.2 Exit

- 基础版：spread 回到 rolling `mu`
- 增强版：
  - `half-life timeout`
  - `pair relationship invalidation`
  - `PnL stop / spread stop`

### 7.3 Sizing

- 先做 beta-neutral notional
- 再叠加 spread-vol target
- 单 pair 风险预算 capped，避免某一组结构断裂拖整本 book

### 7.4 Risk

- `pair disable`：half-life 连续恶化 / beta 飘移 / residual variance 爆掉
- `portfolio cap`：同簇 pair 不要高度重叠
- `turnover budget`：避免 band 一放窄就把 book 变成假高频

### 7.5 Cost

- maker/taker 分层
- 把 fee tier / rebate 显式入模
- band 至少要对 `fee + slippage` 有单调反应

## 8. 下一步怎么测

### 必做 1：把 repo 的 free-boundary band 真正搬到 intraday proxy

这轮我只测了它的**策略含义**，下一轮该测它的**数值实现是否真的优于固定阈值**：

- 对照组：`1.5σ / 2σ / 2.5σ / 3σ`
- 实验组：repo `band_calc.py` 的 OU optimal bands
- 比较：trade count、mean return、median return、positive-pair count、turnover、holding time

### 必做 2：把样本拉长到至少 `90d ~ 365d`

这次 `1500` 根 `5m` 只是最小 transfer check，太短。

下一轮至少做：

- Binance / Bybit perpetual 公共数据
- `90d / 180d / 365d`
- major-only 与 broader liquid universe 分开跑

### 必做 3：把 **pair availability** 当成时间序列来测

不要只问“哪一对最好”，要问：

- 每天 / 每周有多少对 pair 满足 half-life / beta / variance gate？
- 这些 pair 的 churn 有多高？
- 供给是集中在少数币，还是能稳定轮换？

### 必做 4：加入 in-trade structure break kill-switch

如果下一轮只做 mean-cross exit，结论会偏乐观。

至少要补：

- in-trade half-life deterioration
- rolling ADF / residual variance break
- max holding bars

## 9. 最终判断

### 结论

**值得进入研究池，而且优先级不低。**

但它值得进入的原因，不是“optimal stopping 很 fancy”，而是：

1. **base alpha 清楚**：就是 cointegration spread mean reversion；
2. **能独立落地成完整策略**：entry / exit / sizing / risk / cost 都能写出来；
3. **这轮本地 `5m` proxy 已经给出可迁移信号**：宽 band + half-life gate 比窄 band 更像活的东西；
4. **它补的是当前 pairs 线最容易被忽略的 admission 纪律**，而不是重复造一个 signal 名词。

### 当前归类

- 主题类型：`raw alpha`
- 基础 alpha：`beta-hedged cointegration spread mean reversion`
- 是否可独立复现：`是`
- 是否可直接落地完整策略：`是`

## 10. 来源与落地文件

### 主要来源

1. **`djienne` (repo created 2025-12-27, pushed 2026-01-05). _pair_trading_cartea_jaimungal_penalva_. GitHub repository.**  
   - Readable URL: <https://github.com/djienne/pair_trading_cartea_jaimungal_penalva>  
   - Repo URL: <https://github.com/djienne/pair_trading_cartea_jaimungal_penalva>  
   - 关键文件：
     - <https://raw.githubusercontent.com/djienne/pair_trading_cartea_jaimungal_penalva/master/README.md>
     - <https://raw.githubusercontent.com/djienne/pair_trading_cartea_jaimungal_penalva/master/band_calc.py>
     - <https://raw.githubusercontent.com/djienne/pair_trading_cartea_jaimungal_penalva/master/backtest.py>
     - <https://raw.githubusercontent.com/djienne/pair_trading_cartea_jaimungal_penalva/master/config.json>
     - <https://raw.githubusercontent.com/djienne/pair_trading_cartea_jaimungal_penalva/master/run_and_rank.py>

2. **Álvaro Cartea, Sebastian Jaimungal (2015). _Algorithmic Trading of Co-Integrated Assets_. SSRN Electronic Journal.**  
   - DOI: <https://doi.org/10.2139/ssrn.2637883>  
   - Venue：SSRN Electronic Journal  
   - 说明：repo 的 OU / optimal stopping 交易直觉可视为这条经典 co-integrated-assets 线的工程化落地。

3. **Álvaro Cartea, Sebastian Jaimungal, José Penalva (2015). _Algorithmic and High-Frequency Trading_.**  
   - Venue：book / monograph  
   - Readable URL（书目信息可从出版社/图书站点检索）  
   - 说明：repo README 明确说明实现参考了这本书与 FrenchQuant 教学视频。

### 本地 artifacts

- Quick-check 目录：`reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/`
- 阈值汇总：`reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/threshold_sweep_summary_5m_6bps.csv`
- 成本对照：`reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/cost_threshold_compare_5m.csv`
- 汇总 JSON：`reports/artifacts/quant_digests/ou_optimal_band_pairs_20260401/summary_threshold_sweep.json`
- Digest：`research/quant_digests/2026-04-01_0428_ou-halflife-wideband-pairs-alpha.md`
- Page URL（build/publish 后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-01_0428_ou-halflife-wideband-pairs-alpha.html`
