# 别把这篇 2025 copula pairs 论文只读成“又一个配对交易方法”：对 short-cycle desk，更该先测的是「cointegrated spread-pair copula mispricing × 10% entry / 10% close」这条 raw alpha

- 时间：2026-04-15 20:10 UTC
- 类型：2025 *Financial Innovation* 论文全文 source audit（期刊 DOI 元数据 + arXiv 全文 + arXiv LaTeX source）
- 主题类型：raw alpha
- 基础 alpha：**先在 Binance `USDT-M` 小时级主流币里筛出两条 `BTC` 锚定、且彼此稳定相关的 cointegrated spread；当 copula 条件概率同时指向“spread1 被低估 / spread2 被高估”（或反过来）时，做多被低估 spread、做空被高估 spread，等两边 mispricing 一起回到 `0.5±10%` 附近就平仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但更自然的落地方式是 **`1h` 状态层 + `15m/5m` 执行层**，不要硬伪装成逐根 `1m` 主方向信号
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/copula/cointegration/kendall-tau/btc-anchor/spread-pair/mispricing-index/binance-usdtm/hourly/15m/5m/paper/fulltext/cost/risk
- 证据类型：paper full-text audit

## 1. 这次看了什么
这轮主看的是：

- **Authors：** Masood Tadi, Jiří Witzany
- **Year：** 2025（online `2025-01-13`）
- **Title：** *Copula-based trading of cointegrated cryptocurrency Pairs*
- **Venue：** *Financial Innovation*
- **DOI：** `10.1186/s40854-024-00702-7`
- **Readable URL：** <https://arxiv.org/abs/2305.06961>
- **Paper URL：** <https://doi.org/10.1186/s40854-024-00702-7>
- **Repo URL：** N/A（未发现作者公开代码仓）

我这次没有把它读成“copula 在 pairs 里也能用”的泛方法论文，而是先问一句：

> **它的 base alpha 到底是什么？**

答案是清楚的：

> **这不是单一 spread z-score fade，而是“两个 BTC 锚定、可交易的 stationary spreads 之间的相对错位”——当 copula 条件概率显示其中一条 spread 被低估、另一条被高估时，做一多一空，赌的是二者关系回归，而不是单腿价格方向。**

这点很重要，因为它让这篇东西属于我们当前明确想补的那一类：
- `pairs / stat-arb / relative value`
- base alpha 能说清
- entry / exit / threshold / formation / trading window 都给了
- 可以独立复现，不需要私有数据

## 2. base alpha 先说清楚
论文的组合方式不是直接找“哪两只币最像”，而是先固定一个公共锚：`BTCUSDT`。

对每个候选 altcoin `i`，先构造：

- `S^i_t = BTCUSDT_t - β^i * P^i_t`

然后：
1. 用 **EG**（Engle-Granger）或 **KSS**（非线性 unit-root）筛 cointegrated spread；
2. 对这些 spread 按 **Kendall's tau** 排名；
3. 选出排名最靠前的两条 spread `S1, S2`；
4. 对 `S1, S2` 的边际分布做拟合，再用 copula 拟合联合依赖；
5. 在交易周里用条件概率 `h^{1|2}, h^{2|1}` 生成信号。

论文给出的开平仓规则非常明确：

### 开仓
- 若 `h^{1|2} < α1` 且 `h^{2|1} > 1-α1`：
  - **long `S1`，short `S2`**
- 若 `h^{1|2} > 1-α1` 且 `h^{2|1} < α1`：
  - **short `S1`，long `S2`**

### 平仓
- 若 `|h^{1|2}-0.5| < α2` 且 `|h^{2|1}-0.5| < α2`：
  - **close both**

实证里：
- **`α2` 固定为 `10%`**
- **最优 `α1` 也是 `10%`**

翻成人话就是：
- 不是看到普通偏离就冲；
- 要等到 copula 判定两条 spread 的相对关系已经偏到足够极端；
- 一旦两个 conditional mispricing 都回到“接近公平”的中区，就收口。

所以这条 alpha 本体很明确：
> **copula-implied relative mispricing between two stationary spreads**。

这不是 overlay，也不是纯 filter；它本身就是一条 pairs/stat-arb raw alpha。

## 3. 为什么它值得进当前研究池
### 3.1 它补的是 raw alpha，不是旁路解释层
当前 intake 最想补的是：
- mean reversion
- cross-sectional / relative value
- stat-arb / pairs

这篇正好落在这三项交集里，而且和“普通 z-score pair fade”不同，它多了一层：

- **不是只看 spread 离均值多远**；
- 而是看 **两条 spread 联合分布下谁相对谁更错位**；
- copula 允许依赖结构带有 **非线性 / 尾部 / 非对称** 特征。

这对 crypto 特别合理，因为：
- alt-coin 之间经常不是稳定线性关系；
- 真正的错位常常出现在尾部、异方差、波动急变时；
- 简单 Pearson / 单 spread z-score 容易把“结构性变形”误当信号。

### 3.2 它不是只能停留在论文 headline
就算我们不完全照搬论文的“BTC 锚定 + 两条 spread + copula family 全量扫描”大流程，里面也能拆出更适合 desk 的旁支：

1. **pair admission layer**：
   - EG/KSS + Kendall tau 先做 pair/spread 候选筛选
2. **signal layer**：
   - copula conditional mispricing 替代传统 z-score 入场
3. **execution layer**：
   - `15m/5m` 做排队和更便宜的 legging
4. **veto layer**：
   - 只在 liquidity / funding / spread cost 足够友好的时段开仓

也就是说，它不只是“一个 paper result”，而是一整套可拆件的 raw-alpha 素材。

## 4. 论文里最值得记的硬信息
### 4.1 数据口径
论文用的是：
- **Binance USDT-M futures**
- **20 个币种**
- **小时级收盘价**
- 时间区间：**`2021-01-01` 到 `2023-01-19`**

### 4.2 formation / trading 结构
每个 cycle：
- **3 周 formation**
- **1 周 trading**
- 一共 **104 个滚动 cycle**

这点很关键。它不是 static pair once-and-for-all，而是：
> **每周都重新选最可交易的 spread 组合。**

这对 short-cycle desk 很有启发，因为我们也不该把 pairs universe 当静态名单。

### 4.3 成本口径
论文明确说：
- 默认按 **market order** 执行
- 参考 Binance USDT-M：
  - **maker fee = `0.02%`**
  - **taker fee = `0.04%`**
- 实证结果已将 **transaction fees** 计入

它没把策略包装成“无摩擦统计套利”，这一点是加分项。

### 4.4 结果里最有用的三组数字
在 **EG test** 版本、`α1 = 0.10`、`α2 = 0.10` 时：
- **Total Return = `76.2%`**
- **Annualized Return = `37.1%`**
- **Annualized Sharpe = `0.97`**
- **Max Drawdown = `-35.6%`**
- **RoMaD = `2.14`**

在 **KSS test** 版本、`α1 = 0.10` 时：
- **Total Return = `72.3%`**
- **Annualized Return = `35.3%`**
- **Annualized Sharpe = `0.93`**
- **Max Drawdown = `-34.0%`**

对照组：
- **BTC buy-and-hold 年化回报 = `-17.0%`，Sharpe = `-0.23`**
- **20 币等权 buy-and-hold 年化回报 = `14.4%`，Sharpe = `0.15`**

论文自己的结论也很明确：
- **最佳 entry threshold 是 `α1 = 0.10`**；
- threshold 再放宽，交易更多，但风险上去、收益并没有同步改善。

这对我们很重要，因为它提示：
> **极端度门槛过宽，并不等于更好；很多“更多交易”其实只是更多噪音。**

## 5. 这条策略为什么算“可直接落地完整策略”
因为它五件套都齐：

### Entry
- copula conditional mispricing 触发
- `α1` 明确给定并可网格化测试

### Exit
- 双边 mispricing 同时回到 `0.5±α2`
- `α2` 明确给定

### Sizing
- 论文按 spread 结构给了 `β` 比例映射到实际 `P1/P2`
- 实盘可直接转成 `notional-neutral` 或 `vol-neutral`

### Risk
- formation/trading 分离
- 每周重选 pair
- threshold 控制 signal 密度

### Cost
- market-order fee 已写明
- 至少不是“零成本幻觉”

当然，它也不是无脑 production-ready：
- 论文样本区间偏旧；
- 默认频率是 `1h`；
- 没有我们真实 desk 会关心的 legging slippage / funding / OI veto / capacity 上限。

但作为 **raw alpha skeleton**，它是完整的。

## 6. 对 short-cycle desk 的正确迁移姿势
这里最容易犯错的是：

> 把这篇 `1h` pairs/stat-arb 论文硬翻译成 `1m` 主方向信号。

这不对。

更合理的落地是：

### 6.1 主状态层：`1h`
保留论文原意：
- 用 `1h` 数据做 formation / cointegration / copula 拟合；
- 每小时更新一次 mispricing state；
- 每周滚动更新候选 pair/spread。

### 6.2 执行层：`15m / 5m`
当 `1h` 状态层发出入场信号后：
- 在 `15m` 上观察 spread 是否继续扩张还是开始钝化；
- 在 `5m` 上做 legging 顺序与成交优化；
- 如果两个腿的盘口/冲击成本不对称，可延迟较贵那条腿。

### 6.3 veto / overlay
再叠我们已经熟悉的 veto：
- funding 极端时避免把 carry 冲突当纯 pairs；
- OI / volume shock 太强时避免逆着结构 break 做 fade；
- 流动性不足时降级或跳过。

所以它与 `1m/3m/5m/15m` 的关系不是“论文直接给了这些周期”，而是：
> **raw alpha 在 `1h`，short-cycle 负责把它做得更可执行。**

## 7. 最小可复现实验怎么做
### 7.1 先做哪一版
先做 **Binance 永续主流币 universe**，别一开始就混 spot / 多 venue。

建议第一版：
- universe：`BTC, ETH, BNB, LTC, ETC, BCH, XRP, LINK, EOS, ADA, TRX ...` 中的 liquid majors
- bar：`1h` 主状态
- execution child：`15m`
- formation/trading：先照抄 **`21d formation + 7d trading`**

### 7.2 具体流程
1. 以 `BTC` 为 anchor，对每个 alt 构造 BTC-anchored spread；
2. 在 formation window 上做 EG / KSS；
3. 对通过筛选的 spread 计算 Kendall tau；
4. 选出 top-2 spread；
5. 对两条 spread 的边际分布与 copula family 做 AIC 选择；
6. 在 trading week 内实时更新 `h^{1|2}, h^{2|1}`；
7. 用：
   - `α1 ∈ {0.10, 0.15, 0.20}`
   - `α2 = 0.10`
   做入场/平仓；
8. 在 `15m` 上补执行：
   - next-bar entry
   - passive-vs-aggressive legging
   - max-等待时间

### 7.3 必做对照组
至少跑这四组：
1. **单 spread z-score fade**
2. **双 spread + simple percentile trigger**
3. **双 spread + Gaussian copula**
4. **双 spread + family-selected copula**

因为这轮最重要的问题不是“pairs 能不能赚钱”，而是：
> **copula conditional mispricing 相比传统 spread z-score，到底多带来了多少信息。**

### 7.4 先看哪些指标
优先看：
- `net bps / trade`
- `trade count / week`
- `pair turnover`
- `gross exposure overlap`
- `legging slippage`
- `time-to-close`
- `MDD`
- `funding spillover`（若两腿 funding 方向长期不对称）

别第一眼只看 Sharpe。

## 8. 下一步怎么测
### 下一步 1
先做一个 **论文忠实版 baseline**：
- `1h`
- `21d formation + 7d trading`
- `BTC` 锚定
- EG + Kendall tau
- `α1=0.10, α2=0.10`

### 下一步 2
只改一个维度：
- 把 execution 从论文的 market-order 版，改成 **`15m` child execution**，看净收益有没有改善。

### 下一步 3
再测试 “short-cycle 迁移版” 是否成立：
- `7d formation + 1d trading`
- `3d formation + 1d trading`
- 但 **pair selection 仍在 `1h` 做**，别过早把 formation 压扁到 `5m`。

### 下一步 4
加我们自己的 veto：
- `|funding spread|` 太大时跳过
- OI shock 过大时跳过
- 执行腿一侧盘口不足时跳过

### 下一步 5
如果 baseline 还活着，再考虑：
- 把 `BTC` 单 anchor 扩成 `BTC/ETH` 双 anchor；
- 或者从 top-2 spread 扩到 top-k 候选做 validation ranking。

## 9. 风险与保留意见
- **样本期偏旧。** `2021~2023` 对今天的 perp 结构未必直接可迁。
- **小时级信号天然不该伪装成逐 bar 高频方向。**
- **论文虽计手续费，但没把现代 perp microstructure 成本算满。**
- **BTC 锚定可能既是优点也是偏置。** 它简化了选择，但也可能错过非-BTC 结构关系。
- **copula family 搜索很容易过拟合。** 实盘落地时，family 数量和重估频率都该控住。

## 10. 来源
- Tadi, M., & Witzany, J. (2025). *Copula-based trading of cointegrated cryptocurrency Pairs*. *Financial Innovation*. DOI: `10.1186/s40854-024-00702-7`  
  Paper URL: <https://doi.org/10.1186/s40854-024-00702-7>
- Tadi, M., & Witzany, J. (2023). *Copula-Based Trading of Cointegrated Cryptocurrency Pairs*. arXiv: `2305.06961`  
  Readable URL: <https://arxiv.org/abs/2305.06961>
- arXiv source package used for full-text audit and rule/table extraction: <https://arxiv.org/e-print/2305.06961>

## 11. 本地产物
- Digest：`research/quant_digests/2026-04-15_2010_copula-spreadpair-mispricing-alpha.md`
