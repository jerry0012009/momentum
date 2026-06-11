# 别把高频 pairs 的阈值继续写死成一个数：这篇 2025 *Computational Economics* 更该先测的是「RF 预测阈值桶 × HF pair threshold-rebalance」
- 时间：2026-04-06 07:54 UTC
- 类型：2025 *Computational Economics* 开放获取全文（Springer PDF）+ Crossref / OpenAlex 元数据
- 主题类型：raw alpha
- 基础 alpha：高相关 crypto pair 的相对价格偏离会向均衡权重回归；alpha 本体是 **thresholded relative-value mean reversion**，只是 entry / rebalance 宽度不再写死，而是按 pair 的 moments + VaR + corr 映射到不同阈值桶
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/high-frequency/threshold-rebalance/optimal-threshold/random-forest/ml/binance/btc-quoted/1m/3m/5m/15m/paper/open-access/public-data/cost/risk
- 证据类型：开放获取论文全文 + 元数据

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是 high-frequency crypto pairs 的 relative-value mean reversion。**

但这篇更值得 intake 的点，不是“pairs 也能赚钱”，而是：**别再默认所有 pairs 都该共用一个固定 entry 阈值。** 作者直接把“最佳阈值落在哪个区间”当成一个可学习对象，用 pair 自身的均值、方差、偏度、峰度、VaR、相关性去预测阈值桶，然后再把这个阈值桶喂给高频 pairs 策略。

这对当前 desk 有直接价值，因为我们最近已经补了不少 **pair selection / spread construction / copula / Hurst / dynamic-coint**，但**“不同 pair 到底该配多宽的 trigger 才扛得住成本和噪音”** 还没有单独冻结成一张策略骨架卡。这篇刚好补的是 raw alpha 的 entry 层，不是外围解释。

## 2. 论文里最该拿走的东西
### 2.1 论文做了什么
- 作者：**Mahmut Bağcı, Pınar Kaya Soylu**
- 年份：**2025**
- 标题：**The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms**
- 期刊：**Computational Economics**
- 市场与样本：**Binance 上 50 个 crypto 资产的 BTC 报价市场**，使用 **2022–2023 两年逐分钟价格**；作者还用 **2024 年 1–2 月** 做 out-of-sample test。
- 策略内核：不是传统“先 z-score，后双边开平”的教科书写法，而是**pair threshold rebalancing**：
  - 初始两腿等权；
  - 当两腿总价值比超过 `1 + T` 时，卖出相对高估腿的一部分，同时买入相对低估腿，把组合重新拉回等权；
  - `T` 就是策略最关键的 entry / rebalance 阈值。

翻成人话：**这不是又一个 pair-selection 论文，而是在问“pair 选完以后，trigger 宽度该怎么配”**。

### 2.2 论文里最硬的 6 个数据点
1. **阈值扫描范围：1% 到 30%，步长 1%。** 不是拍脑袋用 `2σ`，而是把每个 pair 在每个月的“最佳阈值”先穷举出来。
2. **显式计入 0.1% 交易费。** 这点很关键，因为高频 pairs 最大的问题本来就不是 paper alpha，而是门槛太窄后会被手续费磨死。
3. **输入特征非常克制：** 只用 pair 的 mean / variance / skewness / kurtosis / VaR / correlation coefficient，没有上来就黑盒深度学习。
4. **Random Forest 是全场最稳的分类器。** 在训练/验证里，正相关 pair 的二分类平均准确率 **87.51%**，弱相关 **83.99%**，负相关 **84.68%**；三分类、四分类也都是 RF 最优。
5. **Out-of-sample（2024-01/02）也没塌。** 测试集里，RF 对正相关 pair 的二分类平均准确率 **92.17%**（best **93.94%**）；弱相关 **77.15%**；负相关 **81.68%**。
6. **作者给了实盘感很强的 pair 例子。** 例如 2024 年 2 月，**STX–THETA** 在实际最优阈值 **24%** 时，作者记录到 **41.2%** 的最高收益案例；另外像 **MANA–THETA**（30% 阈值）对应 **25.9%**，**DOGE–STX**（29% 阈值）对应 **25.1%**。

### 2.3 真正改变我们实验设计的结论
论文里最有用的不是“RF 准确率不错”这句废话，而是下面这三个结构性判断：

1. **阈值分布明显随相关性分层。**
   - 正相关 pair 的最佳阈值大量落在 **0–15%**；
   - 弱相关更常落在 **10–20%**；
   - 负相关则更常落在 **22.5–30%**。

2. **说明 pair trigger 不是 universal constant。**
   相关性越弱、关系越松，想吃到有意义的回归，就越需要更宽的偏离才值得出手。

3. **高频 pairs 的“参数选择”本身就是 alpha 工程的一部分。**
   不是先有 alpha、再随便套一个 2σ；很多时候 **threshold 选错，alpha 直接从正变负**。

## 3. 为什么这轮值得排在前面
这篇虽然还是 pairs，但它和我们最近那些 “再找一个新 spread / 新 pair selector” 的材料不一样：

- 它服务的是 **raw alpha 本体**，不是外围 filter；
- 它碰的是 **entry / execution 骨架**，不是又加一个解释变量；
- 它天然适合 desk 当前最关心的 `1m / 3m / 5m / 15m`，因为作者底层就是 minute 级数据；
- 它可以直接拆成完整策略：
  - 什么 pair 能进池？
  - 用多宽阈值触发？
  - 什么时候 rebalance / 平仓？
  - 成本上限多高还能活？

如果问“为什么这篇比继续补一个新 filter 更值得”，答案很直接：**因为它还在 raw alpha 的主轴上，而且碰的是决定会不会交易的那一刀。**

## 4. 策略拆解（按 desk 可落地口径）
### 4.1 论文原版 alpha
- **主题类型：raw alpha**
- **基础 alpha：** pair 两腿的相对偏离会回归均衡权重
- **执行形式：** threshold rebalancing
- **方向属性：** relative-value / mean reversion
- **原论文更接近：** 两腿都持有、偏离后卖强买弱、把组合拉回等权

这点要说清：**论文原版不是最经典的 market-neutral long-short spread shell，而是“等权 pair 被价格拉歪以后做阈值再平衡”。**

### 4.2 desk 版的两个可落地方向
#### A. 论文 faithful 版（先复原作者）
- 标的：先从高流动性的 `alt/BTC` 或可合成 `alt/BTC` 的现货序列开始
- 初始：pair 内两腿等 BTC notional
- 信号：
  - 计算组合权重差或两腿总价值比；
  - 用 rolling 特征喂给 RF，得到阈值桶 `T_bucket`；
  - 当价值比超过 `1 + T_bucket`，触发 rebalance
- 退出：回到等权后视为一次回归完成；或按固定检查点统计累计利润
- sizing：pair 内等权，组合层限制同时激活 pair 数
- risk：pair 断相关、波动跳升、成交深度不足时停用

#### B. perp-neutralized 版（更适合我们 desk）
- 标的：Binance / Hyperliquid / Bybit 的高流动 perp pair
- 信号：把论文的“价值比偏离”翻译成 **residual / ratio gap 超阈值**
- 交易：
  - winner leg 做空，loser leg 做多；
  - 名义金额按 beta-neutral 或 volatility-neutral 对冲
- 退出：
  - gap 回到中性区；
  - timeout；
  - 相关性断裂 / 残差继续扩张到 hard stop
- 成本：手续费 + 滑点 + funding 全都记进去

翻成人话：**论文给的是“阈值怎么选”，不是强迫我们照抄现货-BTC rebalancing 壳。alpha 可以保留，外壳可以换成更适合 perp desk 的 long-short 版本。**

## 5. 这篇对 `1m / 3m / 5m / 15m` 的具体启发
### 5.1 不要一上来共享一个固定 band
对 short-cycle desk，最直接的误区就是：
- `5m` 用 `1.5σ`
- `15m` 也用 `1.5σ`
- 所有 pair 也用 `1.5σ`

这篇几乎可以视作对此的直接反例：**pair 的最优 trigger 宽度和其统计特征是绑定的，不该被压成一个公共常数。**

### 5.2 可以先从“阈值桶”而不是“精确阈值”开始
这是很实用的工程化思想。论文没有强求精确预测 `17%` 还是 `18%`，而是先把阈值做成：
- 二分类：`(0,15%]` / `(15%,30%]`
- 三分类：`(0,10%]` / `(10%,20%]` / `(20%,30%]`
- 四分类：`(0,7.5%]` / `(7.5%,15%]` / `(15%,22.5%]` / `(22.5%,30%]`

对我们也一样：**先把 trigger 学成 bucket，往往比直接回归一个连续值更稳。**

### 5.3 它也能服务更常规的 z-score pairs
即便 desk 最后不用论文这种“价值比阈值再平衡”写法，这篇也仍然有用：
- 你完全可以把 RF 预测出来的 bucket，映射成不同的 `entry z`、`stop z`、`max hold`；
- 本质不变：**pair-state → threshold regime**。

## 6. 最小可复现实验（建议口径）
### 实验 1：先做论文 faithful 复现
- 数据：Binance 现货逐分钟 `ALT/BTC` 或由 `ALT/USDT`、`BTC/USDT` 合成 `ALT/BTC`
- 宇宙：先从 `20~30` 个流动性最高的币开始，不必一上来 50 个全上
- formation：按月滚动计算
  - mean / variance / skewness / kurtosis / VaR / corr
- 标签：在 formation 月内穷举 `T = 1%...30%`
- 策略：下一月按 RF 预测阈值桶做 threshold rebalance
- 频率：
  - 先跑 `15m` decision clock
  - 再看 `5m`
  - 有活口再下沉 `3m / 1m`

### 实验 2：再做 perp-neutralized 便携版
- 数据：Binance / Hyperliquid perp `1m` mid 或 mark
- spread：ratio gap / hedge residual / beta-adjusted residual 三选一
- threshold：
  - baseline A：固定 `entry z`
  - baseline B：按 corr 桶手工分层
  - candidate：RF 预测 threshold bucket
- 目标：比较 **固定阈值 vs corr 分层阈值 vs RF 阈值桶** 三者 post-cost 表现

## 7. 下一步怎么测（必须）
1. **先做 paper-faithful 版，不要直接魔改。** 先确认“阈值桶预测”本身有没有增益，再谈 perp-neutral 化。
2. **先做 bucket，不要先做 continuous regression。** 这篇已经说明分类比精确点预测更稳。
3. **至少要有三组对照：**
   - 单一固定阈值；
   - 只按 corr 桶分层的手工阈值；
   - RF 预测阈值桶。
4. **把 `15m` 和 `5m` 分开训练/验证。** 不要偷懒把一个模型横跨所有频率。
5. **必须显式记成本。** 论文用的是 `0.1%` fee；我们实盘最少也要扫 `8 / 12 / 16 / 20 bps` pair round-trip，再加 funding。
6. **组合层必须管 overlap。** 很多 pair 会共用同一条腿，否者看起来是多 pair，实际是一把币暴露。
7. **看这几个核心指标：** post-cost expectancy、turnover、median hold、timeout 占比、pair overlap、相关性失效后的 drawdown。

## 8. 我现在的判断
这篇最值得我们拿去测的，不是“ML 很强”，而是：

> **高频 pairs 里，threshold selection 不是附属超参，而是 alpha 本体的一部分。**

如果后续复现成立，它对 desk 的实际意义会很直接：
- 不再拿一个公共 `entry z` 硬套所有 pair；
- 先把 pair 分成几类，再给不同的 trigger 宽度；
- 把“什么时候该宽、什么时候该窄”这件事从拍脑袋，升级成一个可训练的 admission / execution layer。

## 9. 风险与保留意见
- 论文原壳更像 **threshold rebalance**，不是最标准的 market-neutral long-short，对我们 desk 需要做一层壳体翻译。
- 作者用的是 **BTC 报价 pair**；如果转到 USDT perp，协整结构、交易费、funding 都会变。
- RF 的优势目前来自这篇论文的样本设计；离样本后是否仍稳，要看我们自己的 2024–2026 OOS。
- 这篇解决的是 **threshold selection**，不是 pair selection 全部问题，不能替代 cointegration / Hurst / copula 等 admission 层。

## 10. 来源
1. **Bağcı, M., & Kaya Soylu, P. (2025). _The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms_. Computational Economics.**
   - Venue: `Computational Economics`
   - DOI: `10.1007/s10614-025-10958-5`
   - Readable URL: `https://doi.org/10.1007/s10614-025-10958-5`
   - PDF URL: `https://link.springer.com/content/pdf/10.1007/s10614-025-10958-5.pdf`
   - Repo URL: **未见 paper-specific public repo**

2. **Crossref metadata**
   - URL: `https://api.crossref.org/works/10.1007/s10614-025-10958-5`

3. **OpenAlex metadata**
   - URL: `https://api.openalex.org/works?filter=doi:https://doi.org/10.1007/s10614-025-10958-5`
