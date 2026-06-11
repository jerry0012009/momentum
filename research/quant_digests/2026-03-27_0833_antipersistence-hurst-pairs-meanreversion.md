# 别把 Hurst 只当抽象状态分数：对 short-cycle desk，更值得先测的是「anti-persistence gated pairs mean reversion」完整 stat-arb 骨架
- 时间：2026-03-27 08:33 UTC
- 类型：2024 开放获取论文（全文 PDF）+ Binance Futures 公共 `15m` desk 最小快检
- 主题类型：raw alpha
- 基础 alpha：**对高协同币对的 spread 做均值回归；只有当 spread 的局部 Hurst exponent 进入 anti-persistent 区间（`H < 0.5`）时才开仓，以更快回归、缩短持仓、降低资金占用。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/hurst/anti-persistence/admission-layer/speed-of-reversion/portfolio-capacity/binance/perpetual/15m/1h/paper
- 证据类型：开放获取论文全文 + Binance 公共 `15m` 最小 transfer check

## 1. 这次看了什么
先回答一句：**这篇东西的 base alpha 是什么？**

不是“分形指标好像能解释市场状态”，也不是“给现有策略再加一个抽象 regime score”。**它的 alpha 本体，是 pairs / relative-value 的 spread mean reversion；`H < 0.5` 只是把“哪些发散更可能很快回归”这件事变成一个可交易的 admission layer。**

主材料是：
- **Mar Grande, Florentino Borondo, Juan Carlos Losada, Javier Borondo (2024)**
- **_Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study_**
- Venue：**Mathematics**
- DOI：`10.3390/math12182911`
- Readable URL：`https://www.mdpi.com/2227-7390/12/18/2911`
- Open PDF：`https://oa.upm.es/86488/1/10254881.pdf`
- Repo URL：**未见作者公开策略仓库**

这篇 paper 对当前 desk 的价值很直接：
- base alpha 不是 breakout / retest，而是 **pairs / stat-arb / relative-value**；
- 论文不是只给“解释”，而是把 **entry / exit / max age / pair ranking / portfolio capacity** 都讲清楚了；
- 最关键的是，它服务的是短周期最敏感的一件事：**交易能不能更快回到均值，而不是把仓位长时间锁死。**

## 2. 核心结论
### 2.1 这篇 paper 真正值钱的是“pairs alpha + H gate”的完整读法
如果只把它读成“市场 anti-persistent 时更容易回归”，那价值会被读小。

更值得 intake 的读法是：
1. **raw alpha**：spread mean reversion（long loser / short winner）；
2. **admission layer**：只有在 `H < 0.5` 时才开；
3. **exit discipline**：回到均值就平、继续恶化到 `2σ` 外就止损、超时就失效；
4. **portfolio layer**：只做 co-movement 靠前的 pairs，并控制并发占用。

翻成人话：**别把 Hurst 当“解释市场”的研究型因子；它在这篇 paper 里更像 pairs raw alpha 的可执行触发器。**

### 2.2 论文里最该记住的不是 headline，而是 4 个硬结果
1. **`H < 0.5` 与“更快回归”存在稳定统计关系。**
   - 论文在 `TW = 1/3/5/7/10/14/21/28` 天都做了检验；
   - 所有窗口下差异都显著，**`p < 0.001`**。

2. **`TW = 5` 天时，treatment 组回归明显更快。**
   - 论文给的直观数字是：**中位 mean-reversion time 大约快了 18 小时**。

3. **这个效果不是“只对最相关 pairs 才成立”。**
   - 作者分别对 **correlation / cointegration / mutual information / DTW** 做 co-movement 分层；
   - 结论是：`H < 0.5` 的加速回归效果在这些分层里都还在，不是某一个 pair ranking 指标的假象。

4. **H gate 的价值不只是方向更准，而是显著减轻资金占用。**
   - 论文报告：满足 `H < 0.5` 的交易，**实际回到均值的持仓中位时长约 13 小时**；
   - 对照组大约是 **22 小时**；
   - 组合容量上，作者还给出一个很实用的结果：在 H-based 策略里，**当并发上限给到 20 笔时，组合可容纳 pair 数约从 32 提高到 66；并发上限 40 笔时，约从 65 提高到 132。**

### 2.3 这不是“纯 filter 文”，因为完整策略骨架已经给够了
paper 的交易规则并不含糊：
- **开仓**：spread 偏离均值 `1σ~2σ` 之间，且 `H < 0.5`；
- **平仓**：回到均值；
- **失败退出**：继续恶化到 `2σ` 外；
- **超时退出**：`72h`；
- **pair selection**：月度重排，优先 co-movement 更强的 pairs；
- **portfolio goal**：减少长时间占用的慢回归单。

所以它不是“先有别的 alpha，再拿 Hurst 做解释”；**它本身就是一套能落地的 pairs 交易框架。**

## 3. 为什么它和当前 desk 直接相关
如果按本轮 intake 规则问：

- **这篇东西的 base alpha 是什么？**

答案很清楚：
- **pairs / relative-value / stat-arb 的 spread mean reversion raw alpha。**

这就意味着它不是纯 regime、不是纯 overlay、也不是“只能服务已有 breakout 线”的小修补。

它补的是 desk 当前仍值得继续堆的方向：
- `mean reversion`
- `pairs / relative value`
- `stat-arb`
- `entry / exit / sizing / risk / cost` 一次写全

而且它特别贴 short-cycle desk 的现实痛点：
- 很多 pairs 逻辑不是方向错，而是 **回得太慢**；
- 回归太慢，手续费、资金占用、并发挤兑都会把 edge 吃掉；
- 所以 **“更快回归”本身就是策略生存变量，不只是统计解释。**

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：
  - 找高协同资产对；
  - 监控 spread 相对其 rolling mean 的偏离；
  - 当 spread 在 `1σ~2σ` 之间发散时，做 long-loser / short-winner 的均值回归。
- admission layer：
  - 只在 spread 的 **local Hurst exponent `H < 0.5`** 时允许开仓；
  - 直觉上，它在筛掉“看起来偏离了，但其实还在延续趋势”的坏单。
- pair selection：
  - 月度更新；
  - 可按 correlation / cointegration / MI / DTW 选 top pairs；
  - 论文回测里 **cointegration** 版本最好。
- entry：
  - signal bar 收盘后确认 `|z| ∈ (1, 2)` 且 `H < 0.5`；
  - `next bar` 执行。
- exit：
  - spread 回到均值；
  - 或继续发散到 `2σ` 外；
  - 或超过 `72h`。
- sizing：
  - 首轮可用 pair-equal gross；
  - 再加 vol-adjusted pair sizing；
  - 组合层要限制最大并发和单币聚集暴露。
- risk：
  - divergence stop；
  - max holding age；
  - cluster / sector cap；
  - funding / 流动性 veto。
- cost：
  - 这条线的关键不是“开不开仓”本身，而是 **H gate 能否显著减少 time-in-trade 与并发锁仓。**

## 4. 当前 `15m` desk 最小快检：H gate 在 Binance perp 上确实筛出“更快回归”的单
为了避免只复述 paper，我做了一个 desk 向的最小 transfer check。

### 4.1 数据与口径
- 数据源：**Binance USDⓈ-M Futures 公共 `15m` K 线**
- 公开性：公开 API，可直接拉取
- 更新频率：`15m`
- 窗口：截至 `2026-03-27 08:30 UTC` 往前 **60 天**
- 标的：`ETHUSDT / BNBUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / ADAUSDT`
- pairs：共 **15 对**
- spread 口径：rolling return-vol ratio 估计 hedge ratio 后，做 log-price spread
- H 口径：spread 的 rolling `7d` GHE proxy
- 事件定义：`|z| ∈ (1, 2)` 时记为候选发散
- 观察窗口：向后看最多 `72h`，统计多久回到均值 / 是否先恶化

产物目录：
- `reports/artifacts/quant_digests/hurst_pairs_gate_transfer_20260327_0833/summary.json`
- `reports/artifacts/quant_digests/hurst_pairs_gate_transfer_20260327_0833/candidate_events.csv`

### 4.2 结果一：`H < 0.5` 在 15m 上明显对应更快的 mean reversion
在这个最小 proxy 下，一共抓到 **853** 个候选发散事件：
- 其中 **366** 个满足 `H < 0.5`
- **487** 个不满足

两组差异很明显：
- **`H < 0.5` 组中位退出时间：9.25 小时**
- **`H >= 0.5` 组中位退出时间：36.5 小时**
- 也就是说，H gate 让中位回归时间**快了 27.25 小时**

这和 paper 的方向完全一致：**H gate 最有价值的，不是让所有单都变赚钱，而是先把“慢回归、耗资金”的那批单大幅筛掉。**

### 4.3 结果二：回到均值的 hit-rate 也明显改善
同一个 15m proxy 里：
- **`H < 0.5` 组 mean-hit rate：27.3%**
- **`H >= 0.5` 组 mean-hit rate：8.2%**

这说明它不是只把 trade duration 截短而已，而是确实更集中地保留了“较快回到均值”的事件。

### 4.4 这轮快检该怎么读
先说诚实结论：
- 这**不是**论文原始 hourly spot 回测的严格 replication；
- 这是一个偏 desk 的、public-data 的 15m proxy；
- 还没有把真实成交成本、资金费、借贷费、组合并发约束完整接进去。

但它已经足够回答一个最关键的问题：
- **把 `H < 0.5` 当 pairs admission layer，有没有 transfer 味道？**

这轮答案是：**有，而且方向相当干净。**

## 5. 对当前 desk 真正该 intake 的是什么
### 5.1 不要把它 intake 成“通用 Hurst regime”
最容易跑偏的地方，是把这篇 paper 读成：
- Hurst < 0.5 所以市场更适合做反转；
- Hurst > 0.5 所以市场更适合做趋势；
- 然后把 Hurst 硬塞进所有策略当总开关。

这读法太宽了，最后往往变成抽象 filter。

更合理的 intake 是：
- **base alpha 仍然是 pairs spread mean reversion；**
- **H 只是这个 alpha 的 admission layer / speed filter；**
- **它优先服务 stat-arb / relative-value 家族，而不是无差别服务所有 setup。**

### 5.2 它值得进研究池的原因，是“完整、诚实、可 desk 化”
这篇 paper 的边际价值，不在于提出一个神秘新因子，而在于：
- base alpha 说得清；
- H gate 的角色说得清；
- entry / exit / max age / portfolio capacity 都给得够细；
- 还能直接映射到 `15m/1h` 的 Binance 公共数据最小实验。

这就符合当前 bot7 的优先级：
- **不是纯解释型；**
- **不是只能做宏观 gate；**
- **而是能拆成完整策略的 raw alpha 候选。**

## 6. 下一步怎么测
这条线真正该做的 follow-up，不是再争论 Hurst 理论，而是尽快完成 desk 化的 4 个最小实验。

1. **做 honest full backtest：`no-H` vs `H<0.5`。**
   - 统一 `next-bar open`
   - 统一 `max hold`
   - 统一 `1σ~2σ` 开仓、`2σ` 失败退出、回均值平仓
   - 成本至少看 `4 / 8 / 12 bps per side`

2. **画 timeframe 边界：`5m / 15m / 1h`。**
   - 论文主体更接近小时级；
   - desk 关心的是：H gate 在更快 bar 上会不会噪声过大；
   - 先回答它到底适合 `15m`，还是更像 `1h` 才稳定。

3. **把 H 阈值当超参数诚实比较，而不是教条。**
   - 比 `no-H / H<0.45 / H<0.5 / H<0.55`
   - 先看 post-cost expectancy、hit rate、median holding time、MSOT
   - 不要默认 `0.5` 一刀切就是最优

4. **把“快回归”真的接到组合容量指标。**
   - 记录 `MSOT`、capital lock hours、cluster overlap
   - 这条线是否值得留，不只看单笔收益，还要看它有没有**释放并发预算**

5. **先限制到 majors universe，再决定是否外扩。**
   - `BTC/ETH/BNB/SOL/XRP/DOGE/ADA` 这类大币先做干净；
   - 如果在 majors 上都不稳，没必要先扩到长尾 pairs。

## 7. 风险与保留意见
- 论文样本是 **2019–2024 的 Binance 20 币种数据**，和当前 perp desk 不是完全同一市场结构；
- 我的 15m 快检使用的是 **简化 spread + GHE proxy**，不是论文逐字复刻；
- Hurst 估计对窗口长度和实现方式敏感；
- paper 回测报告的利润数字是辅助信息，这轮更该盯的是：
  - **mean-reversion speed**
  - **hit rate**
  - **capital lock / MSOT**
- 因此，这条线当前最合适的状态是：
  - **进入 pairs/stat-arb 研究池；**
  - **优先做 honest full backtest；**
  - **暂时不要把 Hurst 扩写成全 desk 通用 regime 总闸。**

## 8. 来源
1. **Grande, M., Borondo, F., Losada, J. C., & Borondo, J. (2024). _Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study_. Mathematics.**
   - DOI：`10.3390/math12182911`
   - Readable URL：`https://www.mdpi.com/2227-7390/12/18/2911`
   - Open PDF：`https://oa.upm.es/86488/1/10254881.pdf`
   - Repo URL：未见公开作者仓库
2. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - 数据公开性：公开可得
   - 更新频率：`15m`

## 9. 本地相关产物
- Digest：`research/quant_digests/2026-03-27_0833_antipersistence-hurst-pairs-meanreversion.md`
- Artifact：`reports/artifacts/quant_digests/hurst_pairs_gate_transfer_20260327_0833/summary.json`
- Page URL（build/publish 后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-27_0833_antipersistence-hurst-pairs-meanreversion.html`
