# 单特征不够时，raw alpha 也可以长成“双排序”：liquidity × risk interaction 的横截面组合

- 主题类型：raw alpha
- 基础 alpha：`cross-sectional long-short on liquidity × risk interaction`，不是单看 risk，也不是单看 liquidity，而是做两者的交互排序
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 先回答一句：这篇东西的 base alpha 是什么？
这篇材料真正的 **base alpha** 不是“crypto 有很多 anomaly”这种综述句，而是：**把两个横截面特征一起排序时，某些组合桶的未来收益显著强于各自单独排序；其中最值得 desk 先盯的是 `liquidity × risk` 这一支。**

翻成人话：不是“高波动就买”或“低流动性就买”，而是**在相对更难交易、同时风险更高的那一角，收益分布会系统性偏离别的角落**。这是一条可以独立建成长短组合的 **cross-sectional / relative-value raw alpha**。

---

## 为什么这轮还值得写它
最近池子里已经有很多：
- 单币 microstructure continuation / fade
- pairs / spread mean reversion
- funding / basis / carry
- cross-market lead-lag

但 **“双特征交互后再做横截面组合”** 这条路，虽然在股票 literature 很常见，在当前 crypto digest 池里还不算拥挤。它值得 intake 的原因有三点：

1. **raw alpha 归因比“模型黑箱”更清楚**：先有两个特征，再看交互桶，不需要 ML 黑箱；
2. **和现有单特征池互补**：它回答的是“两个弱信号能不能拼成一个更强的 raw alpha”；
3. **可直接落地成完整策略**：形成期、排序、持有期、组内等权、成本假设、长短腿都能明确定义。

我这轮选它，不是因为它一定马上胜过继续补 pairs / OFI，而是因为它补的是 **raw alpha 素材池里一个目前相对稀缺的结构位**：`interaction alpha`。

---

## 主要来源

### 1) 主论文
- **Authors / Year**: Aleksander Mercik, Barbara Będowska-Sójka, Sitara Karim, Adam Zaremba (2025)
- **Title**: *Cross-sectional interactions in cryptocurrency returns*
- **Venue**: *International Review of Financial Analysis*
- **DOI**: <https://doi.org/10.1016/j.irfa.2024.103809>
- **Readable URL**: <https://www.sciencedirect.com/science/article/pii/S1057521924007415>
- **Repo URL**: 无公开官方仓库

### 2) 最小 transfer 数据源
- **Source**: Binance USDⓈ-M Futures public klines
- **Readable URL**: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
- **公开性**: 全公开
- **更新频率**: `1m` 原始 bar 可取，`3m/5m/15m` 可聚合

---

## 这篇论文真正给了什么
基于 2017–2023 数据，作者：
- 复制并分类了 **40 个** crypto return-predicting signals；
- 做了 **9360** 个 bivariate interaction strategies；
- 在保守多重检验下，发现：
  - **equal-weighted** 组合里有 **154** 个显著 interaction gains；
  - **value-weighted** 组合里有 **61** 个显著 interaction gains；
- 论文的 out-of-sample top-vs-bottom interaction 组合给出：
  - **equal-weighted long-short 平均周收益 1.18%**，**Sharpe 1.54**；
  - **value-weighted long-short 平均周收益 1.05%**，**Sharpe 1.06**。

摘要里最值得 desk 留意的一句不是“交互很多”，而是：

> **top Sharpe 的 equal-weighted interaction，核心驱动反复落在 liquidity measures（trading volume / bid-ask spread）与 volatility measures（idiosyncratic volatility / VaR）的组合上。**

也就是说，这篇论文最像 desk raw alpha 的，不是泛泛地“多做双排序”，而是先从 **`liquidity × risk`** 这一支下手。

---

## 我这轮 intake 的主主题：`liquidity × risk`，不是把论文 9360 个桶全搬进来
因为 desk 要的是 **可最小实验、可直接复现**，不是大而全复刻。抽成最小策略后，这篇论文最值得先测的 base alpha 可以改写成：

> **在可交易 universe 内，定期按“相对更差的流动性 + 相对更高的风险”做交互排序，做多 top bucket、做空 bottom bucket。**

这里的 `risk` 在原文里可落到：
- idiosyncratic volatility
- Value-at-Risk (VaR)
- 其他波动 / 分布尾部风险特征

这里的 `liquidity` 在原文里可落到：
- trading volume
- bid-ask spread
- 其他交易摩擦 proxy

对 short-cycle desk 来说，最自然的第一版不是复刻全部 40 因子，而是先做：
- **liquidity proxy**：最近 `24h` quote volume、Amihud、Corwin-Schultz proxy、或 top-of-book spread proxy
- **risk proxy**：最近 `24h` realized vol、left-tail VaR、downside semivariance

---

## 这条 alpha 为什么不是 filter，而是 raw alpha
因为它的下注逻辑本身是闭环的：
- 有明确的 **formation rule**：双排序 / 交互分桶；
- 有明确的 **portfolio construction**：long top bucket / short bottom bucket；
- 有明确的 **holding period**：固定持有到下次 rebalance；
- 不依附 breakout / trend / pairs 的主信号才能开仓。

所以它不是“high vol 时才允许做别的策略”的 gate，而是它自己就是一条 **cross-sectional raw alpha**。

---

## desk 化后的完整策略骨架（先做最小可行版）

### 1) Universe
先只做流动性足够的永续：
- `BTC, ETH, BNB, SOL, XRP, DOGE, ADA, LINK, LTC, AVAX, BCH, DOT, TRX, SUI`
- 目的不是追论文里的小币极端收益，而是先在 **可交易 universe 内测试是否还有 interaction edge**。

### 2) Bar / rebalance 口径
- 主实验周期：`15m`
- 形成窗：最近 `96` 根 `15m` bar（约 `24h`）
- rebalance：每 `4` 根 bar（每小时）或每 `8` 根 bar（每 2 小时）
- 持有：到下次 rebalance

### 3) 特征定义（最小版）
#### 流动性
- `liq_score = - rank(rolling_mean_quote_volume_24h)`
- 也可升级为：
  - `Amihud = |ret| / dollar_volume`
  - `spread proxy = high-low / close` 或 CS proxy

#### 风险
先测三版：
- `rv24 = rolling_std(ret, 96)`
- `VaR5_24 = rolling_quantile(ret, 5%)`
- `downside_semivar_24`

### 4) 交互打分
最小版直接线性拼：
- `interaction_score = 0.5 * rank(risk) + 0.5 * rank(illiquidity)`

后续再升级成：
- 双排序 3×3 或 5×5 桶；
- 只交易 `(high-risk, low-liq)` vs `(low-risk, high-liq)` 两角；
- 或者只做 long-only top bucket，因为论文摘要也提示 **成本尤其伤 short leg**。

### 5) 入场 / 出场
这类组合不是逐 bar 单笔交易，所以规则应写成组合版：
- **Entry**：到 rebalance 时更新排名，long top bucket / short bottom bucket
- **Exit**：下一次 rebalance 平旧仓并按新排名换仓
- **Timeout**：固定到下一 rebalance
- **Stop**：
  - 单币权重上限 `15%`
  - 单边 gross 上限 `100%`
  - 组合回撤阈值 `1.5~2.0 ATR_portfolio` 或日内 `max DD` 硬停

### 6) Sizing
- 组内等权先做 baseline；
- 组合层做 beta-light / dollar-neutral；
- 如果 long-only 更强，再加一个 market beta hedge 版本对照。

### 7) 成本
- `15m` 先按 round-trip `10 / 15 / 20 bps` 三档压测；
- 若转向 `5m`，默认成本线更严格；
- 如果 short leg 明显拖累，直接测试 `top-bucket long-only` + beta hedge。

---

## 我做的一个最小 transfer quick check（Binance 永续，15m）
为了避免只抄论文 headline，我做了一个 **很克制的 desk proxy**：

### 快检口径
- 标的：上面 14 个 Binance USDⓈ-M 永续
- 数据：每个标的最近 **2200 根 `15m` bars**（约 22.9 天）
- 形成窗：最近 `96` 根 `15m` bars（24h）
- rebalance：**每小时**（每 4 根 `15m`）
- 持有：未来 **4 根 `15m`**（1 小时）
- long/short：
  - `long = top 3 interaction-score`
  - `short = bottom 3 interaction-score`

### 我先扫了 6 个 interaction proxy
1. `risk × illiquidity`
2. `risk × MAX`
3. `risk × MIN(abs)`
4. `MAX × MIN(abs)`
5. `VaRtail × illiquidity`
6. `VaRtail × MAX`

### 结果（gross, 未扣费）
最接近论文主线的 `risk × illiquidity`：
- **525 次 hourly rebalance**
- 平均 long-short 收益：**-0.00273% / 小时**（约 **-0.27 bps / h**）
- `Sharpe-like`：**-0.86**
- 胜率：**50.7%**
- 累计：**-1.65% gross**

其他几支也没更好：
- `VaRtail × illiquidity`：累计 **-2.06% gross**
- `MAX × MIN(abs)`：累计 **-2.74% gross**
- `risk × MAX`：累计 **-7.67% gross**

### 这组快检告诉我什么
很简单：

> **论文里的 weekly interaction alpha，不能天真地直接压缩成 `15m` 的“24h proxy × hourly rebalance”组合。**

也就是说，这篇论文 **有 raw alpha 价值**，但当前这版最小 intraday transfer **先判不通过**。

---

## 这不代表论文没用，代表“直接压缩时间尺度”不够
我会把这篇东西的当前 verdict 写得很明确：

### 值得保留的部分
1. **raw alpha 结构值得保留**：双特征 interaction 在 crypto 截面里确实有实证；
2. **比单特征更像组合研究素材**：适合未来做 alpha blending / interaction search；
3. **论文给了具体优先方向**：先看 `liquidity × risk`，不是盲扫 40×40。

### 目前不值得直接 fast-lane 复现的部分
1. 论文主频率是 **weekly**；
2. 顶级结果偏 **equal-weighted**，天然更吃小币 / 摩擦；
3. 我这轮 `15m` naive proxy 快检 **gross 都没站住**；
4. 对 short-cycle desk 来说，若没有更好的 liquidity / tail-risk intraday proxy，直接推进大概率是在卷负 alpha。

所以，这轮最诚实的判断不是“马上开做”，而是：

> **把它作为“interaction raw alpha 家族”的重要 source 留档，但当前不进 fast-lane 第一优先。**

---

## 如果还想继续挖，下一步应该怎么测
不是再加更多因子乱扫，而是只做 3 个更像 desk 的升级：

### 方向 1：把 liquidity proxy 做对
当前用的是 `24h quote volume`，太粗。
优先升级成：
- top-of-book spread proxy
- Amihud / price impact proxy
- taker imbalance × spread 联动摩擦

### 方向 2：别按“每小时全量换仓”做
interaction 策略未必适合高 turnover。
优先试：
- `4h` rebalance
- `1d` 形成、`4h` 执行切片
- `staggered rebalance`（避免全组合同一时刻翻仓）

### 方向 3：把 short leg 单独审判
论文摘要已经暗示：**成本对 short leg 杀伤更大**。
所以必须单独做：
- `top bucket long-only`
- `top bucket long-only + perp beta hedge`
- `top-bottom long-short`
三版对照。

如果这三步后仍然没有 gross edge，就可以很干脆地把它降级成 **中频 cross-sectional interaction 理论储备**，别继续烧时间。

---

## 给当前 desk 的最终判断
### 我的 verdict
- **这是一条合格的 raw alpha 论文主题**，不是 filter / overlay；
- **它也确实可独立复现成完整策略**，尤其在周频/中频横截面上；
- 但对当前 `1m / 3m / 5m / 15m` desk 来说，**最小 `15m` transfer quick check 先给负号**；
- 所以它现在更适合进入：
  - `interaction-alpha reserve`
  - `future cross-sectional blending`
  - `long-only vs long-short cost decomposition`

而**不应该**立刻挤掉那些已经在 `5m/15m` 上更接近可交易的 pairs / OFI / carry / lead-lag 候选。

---

## 下一步怎么测（直接可执行）
1. 用 Binance 永续公开数据，补三类更像实盘的 liquidity proxy：`spread`, `Amihud`, `impact proxy`
2. 保留 `risk × illiquidity` 主线，不再盲扫更多 interaction family
3. 把 rebalance 从 `1h` 降到 `4h / 8h`
4. 先做 `top-bucket long-only`，再做 `beta-hedged long-only`
5. 成本统一按 `10 / 15 / 20 bps` 三档压测
6. 若 gross 仍不正，直接 park，不再把它当 fast-lane raw alpha

---

## 参考
1. **Mercik, A., Będowska-Sójka, B., Karim, S., & Zaremba, A. (2025). _Cross-sectional interactions in cryptocurrency returns_. International Review of Financial Analysis.**  
   DOI: <https://doi.org/10.1016/j.irfa.2024.103809>  
   Readable URL: <https://www.sciencedirect.com/science/article/pii/S1057521924007415>

2. **Binance USDⓈ-M Futures REST API — Kline/Candlestick Data**  
   <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
