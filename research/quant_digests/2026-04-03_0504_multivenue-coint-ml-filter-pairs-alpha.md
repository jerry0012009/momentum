# 别把这份 2026 多 venue 新 repo 只读成“大而全研究脚手架”：对 short-cycle desk，更该先抄的是「cointegration spread raw alpha × ML entry filter × venue-tier risk stack」这条完整策略壳

- 主题类型：raw alpha
- 基础 alpha：**协整价差偏离后回归均衡**；翻成人话，就是“本来该一起走的两条币腿短时走散了，做多被低估腿、做空被高估腿，等关系回正”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-03 05:04 UTC
- 类型：2026 GitHub 新仓库 `README.md + config/config.yaml + docs/methodology.md` 审阅 + 经典 pairs 文献地基交叉
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/ml-filter/venue-tier/risk-stack/multi-venue/5m/15m/1m/3m/repo/public-data/cost
- 证据类型：repo（完整策略壳）+ config/methodology（参数与成本）+ classic paper（方法地基）

## 1. 这次看了什么
这轮更值得 intake 的，不是再抄一个“复杂模型选币器”，而是这份 2026 新 repo 其实已经把一条 **pairs / stat-arb raw alpha 的完整策略壳** 摆得很齐：

1. 先在多 venue universe 里筛流动性足够、协整显著的候选 pair；
2. 用 spread z-score 做 **均值回复入场**；
3. 用 **ML 只做 entry/exit timing enhancement**，不篡位成 alpha 本体；
4. 用 **half-life、venue tier、sector/correlation cap、Kelly fraction、cost model** 把它包成可交易组合；
5. 明确写了训练/测试、交易成本、无杠杆和 walk-forward 壳。

所以这轮最该带走的一句话是：

> **base alpha 不是“GBM / RF 能预测收益”，而是 cointegrated spread mean reversion；ML 只是确认层，venue-tier risk stack 才是让它能活着上线的交易壳。**

这和最近几轮学习进展是互补的：最近 raw alpha 池里，directional、carry、microstructure、cross-sectional 已经堆得不少；但 **能把 entry / exit / sizing / risk / cost 一次讲全的 market-neutral pairs 母板** 仍然值得继续补。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：协整价差均值回复。**

不是：
- “Random Forest 预测比较强，所以它是 alpha”；
- 也不是“多 venue 数据很多，所以 alpha 自然更稳”；
- 更不是“风控做得细，所以风控本身等于信号”。

真正的 alpha 是：
- 先找到长期一起走、短期会偶尔错开的币对；
- 当 spread 偏离历史常态过远时，做相对价值回归；
- 当 spread 回到均衡附近时退出。

翻成人话：
**赚的钱来自“走散之后会回去”，不是来自模型名字更花。**

## 3. 为什么这轮值得写，而不是继续补一张 generic directional 卡
如果拿当前 desk 的优先级看，这个主题仍然值得进池，原因有四个：

1. **它是 raw alpha，不是 filter。**
   - z-score 偏离本身就是入场触发，不是旁路确认。
2. **它直接给了完整策略壳。**
   - entry、exit、stop、position sizing、concentration cap、cost 都明确。
3. **它把 ML 放在正确位置。**
   - ML 只是 timing/过滤增强，这比“把 ML 包装成 alpha 本体”更适合快速复现。
4. **它补的是 market-neutral 素材池。**
   - 对 desk 来说，这比再多加一张单腿顺势卡更平衡，也更利于组合层分散。

如果要问：**它为什么比继续补 raw directional alpha 更值得？**
答案是：
**因为它补上的不是一个点子，而是一整套 pairs 生产线母板。** 这套母板以后可以接 cointegration、Kalman、copula、graph matching、funding gate、execution veto 等很多旁支。

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / market-neutral
- 基础 alpha：cointegrated spread mean reversion
- regime：只在协整关系稳定、半衰期不过长、流动性过关时启用
- filter / veto：ML timing filter、协整失稳、相关性过高、sector 过度集中、成本过高时 veto
- risk / sizing / execution overlay：Kelly fraction、venue tier 限额、单 pair notional cap、cost/slippage 假设、max holding、no leverage

## 4. 这次看的主来源
### 4.1 alpha / 工程主来源（repo）
1. **Tamer Atesyakar (2026)**  
   **Title:** *Crypto Statistical Arbitrage*  
   **Venue:** GitHub repository  
   **DOI:** N/A  
   **Readable URL / Repo URL:** https://github.com/abailey81/Crypto-Statistical-Arbitrage  
   **作者/仓库页署名：** Tamer Atesyakar  
   **创建时间：** 2026-03-13T16:54:17Z  
   **实际看的文件：** `README.md`, `config/config.yaml`, `docs/methodology.md`

### 4.2 方法地基（classic foundation）
2. **Engle, R. F.; Granger, C. W. J. (1987)**  
   **Title:** *Co-Integration and Error Correction: Representation, Estimation, and Testing*  
   **Venue:** *Econometrica*  
   **DOI:** `10.2307/1913236`  
   **Readable URL:** https://www.jstor.org/stable/1913236  
   **Repo URL:** N/A

3. **Gatev, E.; Goetzmann, W. N.; Rouwenhorst, K. G. (2006)**  
   **Title:** *Pairs Trading: Performance of a Relative-Value Arbitrage Rule*  
   **Venue:** *Review of Financial Studies*  
   **DOI:** `10.1093/rfs/hhj020`  
   **Readable URL:** https://academic.oup.com/rfs/article/19/3/797/1646694  
   **Repo URL:** N/A

## 5. 这条 alpha 到底有哪些硬信息，不是空想
### 5.1 这份 repo 不是只给概念，它把参数壳写得很细
从 `README.md` 和 `config/config.yaml`，至少能确认这些关键参数：

- 数据主频：**OHLCV 1h**；funding 统一到 **8h**；options snapshot 1h；
- walk-forward：**train = 2022-01-01 ~ 2023-06-30，test = 2023-07-01 ~ 2024-12-31**；
- pairs lookback：**90 天**；
- cointegration 显著性：**5%**；
- 可接受 half-life：**1~7 天优先**；
- CEX 入场阈值：**|z| > 2.0**；出场：**z 回到 0**；止损：**|z| > 3.0**；
- DEX 入场阈值：**|z| > 2.5**；出场：**|z| < 1.0**；止损：**|z| > 3.0~3.5**；
- 最大持有期：**30 天**；
- sizing：`volatility_weighted` / Kelly fraction / tiered cap；
- no leverage：README 明写 **1.0x only**。

这已经不是“有个想法”，而是 **直接能翻译成 backtest config 的策略骨架**。

### 5.2 这份材料真正值钱的，不是多 venue，而是“raw alpha + risk shell”一体化
README 给出的 Phase 2 逻辑非常清楚：

1. `Universe construction + cointegration testing`
2. `Baseline z-score mean reversion strategy`
3. `ML enhancement (Gradient Boosting + Random Forest)`
4. `Walk-forward backtest + crisis analysis`
5. `Report generation`

这说明 repo 作者默认的策略顺序也是：
**先有 baseline raw alpha，再加 ML enhancement。**

这点很关键，因为对 short-cycle desk 来说，第一轮最该复现的，永远应当是：
- 协整筛 pair 是否稳定；
- z-score 反转是否 after-cost 仍活着；
- half-life 和 cost 是否允许短周期化；
- 风控层是否让它从“纸上 alpha”变成“可交易 alpha”。

## 6. 有哪些关键数字可以直接带走
### 6.1 repo 报出来的主结果
README 的 walk-forward out-of-sample 结果里，Phase 2 `Altcoin Statistical Arbitrage` 给了这些数字：

- **Sharpe Ratio = 1.61**
- **Total Return = 6.84%**
- **Max Drawdown = 4.64%**
- **Win Rate = 51.18%**
- **Total Trades = 127**
- **BTC Correlation = -0.12**

这些数字的正确读法不是“照抄预期收益”，而是：
- 这条 raw alpha 至少在作者口径下能 survive walk-forward；
- 它的收益并不依赖高 BTC beta；
- 它比较像 **低相关 market-neutral 补充腿**，而不是组合唯一主力。

### 6.2 成本和风控不是装饰，而是这条卡能不能活的关键
`docs/methodology.md` 里对 pairs 成本给得也很具体：

- CEX pair trade 总成本约 **0.20%**；
- DEX pair trade 总成本约 **1.00%**；
- CEX 单边 slippage 假设 **0.05%**，DEX **0.30%**；
- DEX 还显式加了 **MEV / gas** 项；
- sector exposure cap = **40%**；
- max cross-pair correlation = **0.70**；
- Tier 1 / 2 / 3 最大持仓分别大致 **$100k / $50k / $10k**。

这套设计很适合 desk 的当前偏好：
**不要把 alpha 写成“入场公式”，而要写成“能扣费、能限仓、能停做”的完整壳。**

### 6.3 ML 在这里扮演的是 filter，不是 alpha 本体
repo 和 methodology 文档都把 ML 摆在 enhancement 位置，特征包括：

- lagged z-scores（1 / 2 / 4 / 8 / 24 bars）
- spread momentum / acceleration
- volume ratio
- BTC returns & volatility
- sector index returns
- correlation stability metrics
- volatility regime / HMM

这意味着对当前 desk，最合理的拆法是：

- **raw alpha：** spread z-score mean reversion；
- **filter / confirmation：** ML score、volatility regime、correlation stability；
- **overlay：** Kelly / sector cap / correlation cap / max holding / venue tier。

这正符合本轮任务的分类要求，不会把 filter 伪装成 alpha 本体。

## 7. 对当前 desk，更该抄哪一层，不该抄哪一层
### 7.1 最该先抄的是 baseline，不是全仓库宇宙
如果 desk 要最小可复现，我会先抄这四个部件：

1. **liquid universe + pair selection**
2. **cointegration + half-life filter**
3. **z-score entry / mean exit / stop**
4. **cost + cap + max-holding risk shell**

先别抄：
- 32 venue 全接入；
- DEX 复杂成本；
- 全量 ML ensemble；
- HRP/MVO/Black-Litterman 组合层。

因为第一轮要回答的是：
**这条 pairs raw alpha 在我们自己的 `5m / 15m` 口径下，是否仍有 after-cost 边际。**

### 7.2 ML 更像第二阶段增强层
当 baseline 已经能在 `15m` 活下来后，再考虑：
- 用 RF / GBM 给 spread 反转信号打分；
- 把低质量反转过滤掉；
- 把边际改善归因到 hit-rate 提升还是 turnover 降低。

如果 baseline 都活不下来，ML 大概率只是在 **更复杂地亏钱**。

## 8. 这条 alpha 与 `1m / 3m / 5m / 15m` 的关系
### 8.1 `15m` 是最优先主战场
这份 repo 原始口径是 **1h + 1~7 天 half-life**，所以 desk 化时最自然的下采样不是直接冲 `1m`，而是先落在 `15m`：

- 比 1h 更快，适合短周期 desk；
- 但比 1m/3m 更不容易被噪声和 fee 杀死；
- 更适合保留协整关系的稳定性。

### 8.2 `5m` 是第二站，不是第一站
`5m` 更适合做：
- 更密的 spread 更新；
- 更细的 execution slicing；
- 对 `15m` parent signal 的 child execution。

但如果一上来就把 pair MR 压到 `1m/3m`，很容易把 **半衰期优势换成纯手续费机器**。

### 8.3 `1m / 3m` 更像 execution / veto 层
对这类 pairs raw alpha，`1m/3m` 的合理位置通常不是主信号，而是：
- 做挂单择时；
- 做盘口/冲击 veto；
- 做 child order 切片；
- 做 spread 异常扩宽下的暂缓执行。

所以别把它硬伪装成 “1m 主 alpha”，这条线更诚实的结构是：
**15m 做 alpha admission，5m 做 tactical execution，1m/3m 做 microstructure veto。**

## 9. 最小可复现实验（直接服务当前 desk）
### 实验 A：最简 CEX pair baseline
- **Universe：** `BTC, ETH, BNB, SOL, XRP, DOGE` 或 top-10 高流动 perp
- **数据源：** Binance / Bybit / OKX 公共 perpetual klines
- **公开性：** 公开可得
- **更新频率：** 拉 `1m` 原始，聚合成 `15m`
- **pair selection：** rolling Engle-Granger + half-life filter
- **entry：** `|z| > 2.0`
- **exit：** `z` 回到 `0`
- **stop：** `|z| > 3.0`
- **要回答的问题：** 不加 ML，after-cost 的 pair MR 是否成立？

### 实验 B：half-life / threshold 网格
- **half-life gate：** `4~24 bars / 1~3 days / 3~7 days`
- **entry gate：** `1.5 / 2.0 / 2.5`
- **exit gate：** `0 / 0.5 / sign-flip`
- **目标：** 找到对 `15m` 来说最像“能活着交易”的参数区，而不是只找最高 Sharpe。

### 实验 C：ML enhancement 诚实对照
在 baseline 能活后，再加一个很薄的 filter：
- 特征：lagged z-score、spread momentum、BTC realized vol、volume ratio；
- 模型：先 `logit / ridge / random forest`；
- 输出：只决定 **trade / no-trade**，不直接替代 alpha；
- 目标：回答 ML 是提升 hit-rate，还是只是减少差交易。

### 实验 D：risk shell ablation
比较这几组：
1. 无 sector cap
2. `40% sector cap`
3. `40% sector cap + 0.7 correlation cap`
4. 再加 `max holding bars`

这一步回答：
**pairs alpha 的净值稳定性，有多少来自信号，有多少来自风险外壳。**

## 10. 这条线最容易犯的错
- **错法 1：** 把 ML 当 alpha，本末倒置。
- **错法 2：** 只看 pair entry，不看 cross-pair correlation，结果同一行业一起爆。
- **错法 3：** 只在 paper space 看 spread，不扣真实腿成本和 funding 结算影响。
- **错法 4：** 直接把 1h 参数搬到 1m，结果 half-life 还没形成，手续费先到。
- **错法 5：** 把多 venue 广度误当稳健性，实际上只是把工程复杂度放大。

## 11. 为什么它值得进研究池
这张卡值得进池，不是因为它又是一个“很大的 repo”，而是因为它非常适合做 **pairs / stat-arb 策略母板**：

- base alpha 清楚：cointegrated spread mean reversion；
- 分类清楚：ML 是 filter，不是 alpha 本体；
- 交易壳完整：entry / exit / sizing / risk / cost 都有；
- desk 迁移路径清楚：`1h → 15m` 比 `1h → 1m` 更诚实；
- 公开数据友好：Binance / Bybit / OKX / Hyperliquid 等公有接口就能做 MVP。

它对当前 desk 最直接的价值，不是提供一个“新奇 headline alpha”，而是补上一块 **能反复复用的 raw alpha 组件化模板**。

## 12. 下一步怎么测
1. **先做 `BTC/ETH`, `ETH/BNB`, `BTC/SOL` 三组 `15m` baseline**，只保留 cointegration + z-score + stop/exit。
2. **立刻跑成本梯度**：round-trip `4 / 8 / 12 / 16 bps`，先看生存区，不先追最高 Sharpe。
3. **再测 half-life gate**：短 half-life 是否明显优于长 half-life，确认它是否适合 short-cycle 化。
4. **若 baseline after-cost 仍为正**，再加最薄 ML filter，看它到底提升 hit-rate 还是只是减换手。
5. **最后才扩展多 pair book**，加入 sector/correlation cap，验证它能否作为组合中的低 beta 市场中性腿。

## 13. 一句话结论
如果只带走一句话，我会带走这句：

**别把这份 2026 多 venue 新 repo 只当“大而全 crypto 研究框架”；对 short-cycle desk，更该先抄的是「cointegration spread raw alpha × ML entry filter × venue-tier risk stack」这条可独立复现、可直接落地的 pairs 全策略骨架。**
