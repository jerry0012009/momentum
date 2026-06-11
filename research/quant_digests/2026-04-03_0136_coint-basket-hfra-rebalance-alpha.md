# 别把这篇 2024 *Financial Innovation* 论文只读成“高频再平衡配置建议”：对 short-cycle desk，更该先测的是「cointegrated basket equal-weight drift × threshold rebalance」这条完整 relative-value raw alpha

- 主题类型：raw alpha
- 基础 alpha：多资产 cointegrated basket 内部的**相对强弱偏离均值回归**；当篮子里某些腿的当前市值权重显著跑离等权目标时，卖出超配腿、买入低配腿，把组合重新拉回目标权重
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-03 01:36 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/relative-value/stat-arb/basket-rebalancing/multi-asset/cointegration/equal-weight/threshold-rebalance/high-frequency/portfolio-size/regime-split/binance/btc-quoted/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2024 Springer 开放获取全文（article + tables）/ OpenAlex + Crossref metadata

## 1. 这次看了什么

这轮选它，不是因为我们缺“又一个 pairs 阈值故事”，而是因为它把 **pairs rebalancing** 往前推进了一步：

- 不再只做 `2-leg pair`
- 而是做 **3-leg / 5-leg cointegrated basket**
- 直接比较 **不同 trend / volatility regime** 下，篮子大小与高频再平衡收益之间的关系
- 还给了一个很硬的 production 启发：**1 分钟再平衡壳本身就能独立活成 raw alpha，不必先等 fancy spread model 才开工**

对我们 desk 来说，这比再补一个“某个形态在某个窗口下更好”更值钱，因为它补的是一块还没系统写进池子的能力：

> **从 pair mean reversion 升级到 basket relative-value rebalancing。**

## 2. 为什么这轮值得做它

先回答任务里最重要的那句：**这篇东西的 base alpha 是什么？**

答：**篮子内部相对涨跌失衡后的权重回归。**

更直白一点：

1. 先拿一组共同走势足够稳定的币，组成一个 `3~5` 腿篮子；
2. 初始时各腿等权；
3. 运行中，某些腿涨得更快、某些腿掉得更多，组合权重开始偏离；
4. 当偏离超过阈值 `T`，就卖出“超配”的腿、买入“低配”的腿；
5. 吃的是 **relative-value / stat-arb / mean reversion**，不是方向判断。

所以它不是 filter，不是 overlay，也不是纯 portfolio management。**alpha 本体就在“偏离后回补”这一步。**

这轮优先它，还有 3 个现实原因：

- **它是完整策略，不是半句话。** entry / rebalance / threshold / fee / portfolio size 都给了。
- **它能直接扩充 raw alpha 素材池。** 我们最近已经补了很多 `pair shell`，这篇补的是 **multi-asset basket shell**。
- **它天然适合 `1m / 3m / 5m / 15m` 最小实验。** 只要公开 K 线就能先复现，不依赖私有订单流或付费因子。

## 3. 论文信息

- **Authors**: Mahmut Bağcı, Pınar Kaya Soylu
- **Year**: 2024
- **Title**: *Optimal portfolio selection with volatility information for a high frequency rebalancing algorithm*
- **Venue**: *Financial Innovation*
- **DOI**: `10.1186/s40854-023-00590-3`
- **Readable URL**: https://link.springer.com/article/10.1186/s40854-023-00590-3
- **DOI URL**: https://doi.org/10.1186/s40854-023-00590-3
- **Repo URL**: 无独立公开 repo；正文说明附录含 `Rebalancing_Algorithm.m` 伪代码 / Matlab 脚本

## 4. 论文到底做了什么

### 4.1 数据与样本

- 交易所：**Binance**
- 标的：**40 个 BTC 计价 crypto-assets**（如 `AAVE/BTC`, `ADA/BTC`, `ETH/BTC` 等）
- 频率：**1 分钟 close price**
- 样本：**2021 年逐月**数据，用于六类趋势 / 波动 regime 对照
- 长样本验证：**2021-01-01 ~ 2023-04-30（28 个月）**
- 手续费假设：**0.1% taker fee**
- 阈值扫描：**1% ~ 20%**，步长 **1%**

作者把样本分成 6 类：

- up-trend with high volatility
- up-trend with low volatility
- down-trend with high volatility
- down-trend with low volatility
- no-trend with high volatility
- no-trend with low volatility

并且先做 Johansen cointegration test，再把 HFRA（high-frequency rebalancing algorithm）应用到 `2`、`3`、`5` 腿组合上。

### 4.2 HFRA 的策略壳是什么

它的壳很朴素，但正因为朴素，才适合 desk 先复现：

- 起始时篮子内各腿**等权**；
- 记每条腿当前总价值为 `TV_i = price_i × quantity_i`；
- 若任意两腿之间的**价值偏离比例**高于阈值 `T`，则：
  - 卖出当前更贵 / 更超配的腿；
  - 买入当前更便宜 / 更低配的腿；
  - 使相关腿重新回到**平均价值**；
- 成本按 `0.1% taker` 扣除。

翻成人话：

> **不是预测谁会涨，而是承认“同一个篮子内部会短暂失衡”，然后持续把它拉回等权。**

这个思路对 short-cycle desk 很重要，因为它比“先定义一条复杂 spread，再设 z-score”更通用：

- pair 能做
- 3 腿能做
- 5 腿也能做
- 后面再叠加 beta-neutral、sector-neutral、microstructure veto 都很自然

## 5. 最重要的 desk 启发：这不是 pairs 的重复，而是把 raw alpha 壳扩成 basket

如果只看标题，很容易把这篇当成“高频再平衡算法 + 组合配置建议”。

但对我们真正有价值的，不是“portfolio size 多大更优”这个结论本身，而是它明示了下面这条 alpha 链条：

1. **先找到 cointegrated basket**，不必局限于双腿；
2. **以等权为锚**，而不是以某条单独 spread 为锚；
3. **把权重漂移**当作错价代理；
4. **用 threshold rebalance** 吃掉内部强弱回归；
5. 再根据 volatility / trend 决定该不该放大篮子、降低门槛、或收缩风险。

这比普通 pairs 更适合当前 desk 的一个点在于：

- pairs 往往卡在“到底该配哪两条腿”
- basket shell 则允许你先把**同主题 / 同 beta / 同风格**的 `3~5` 个币先装进一个容器，再做内部均值回归

换句话说，**这篇补的不是一个更 fancy 的 signal，而是一个更宽的 raw-alpha 容器。**

## 6. 关键证据

### 6.1 高波动上行期：篮子越大，HFRA 越赚钱

论文在 `up-trend + high volatility` 组上的结果非常激进，但方向很清楚：

- `2` 腿组合平均利润：**151.5%**
- `3` 腿组合平均利润：**156.06%**
- `5` 腿组合利润：**160.46%**

也就是说，在作者定义的高波动上行环境里，**从 pairs 扩到 basket，不是稀释 alpha，反而是放大 HF rebalance shell 的收益承载力。**

### 6.2 低波动上行期：仍赚钱，但“加腿数”的边际收益变小

`up-trend + low volatility`：

- `2` 腿平均利润：**18.23%**
- `3` 腿平均利润：**18.51%**
- `5` 腿利润：**18.70%**

这组数字的意义不是“18% 一定能复现”，而是：

> **低波动时，basket shell 还能活，但“扩大篮子”不再带来很强的额外收益。**

所以如果我们要把这条线迁到 `5m / 15m`，就不该默认“篮子越大越好”，而应该把 **realized vol / dispersion** 先当 gate。

### 6.3 高波动下跌期：还是会亏，但更多腿能减少亏损

`down-trend + high volatility`：

- `2` 腿平均亏损：**-25.20%**
- `3` 腿平均亏损：**-24.07%**
- `5` 腿亏损：**-23.04%**

这说明一个很实用的事实：

- **basket shell 不是自动免疫方向风险**；
- 但在坏 regime 里，**加腿数能削弱亏损斜率**。

这对实盘映射很关键：

- 上行高波下可以放开 gross；
- 下行高波下不要简单关机，而是优先 **收缩单篮子仓位 / 提高触发阈值 / 增加 beta hedge**。

### 6.4 无趋势环境：靠高频回补吃小 edge，但不能期待大肉

`no trend + high volatility`：

- `2` 腿平均：**-0.63%**
- `3` 腿平均：**0.43%**
- `5` 腿：**1.70%**

`no trend + low volatility`：

- `2` 腿平均：**1.67%**
- `3` 腿平均：**1.80%**
- `5` 腿：**1.88%**

翻成人话：

- 没有明确趋势时，这条壳还能磨出一点点边；
- 但它更像**小而稳定的内在回补 edge**，不该拿它当爆发型 alpha。

### 6.5 长样本对照：1m HFRA 明显胜过普通 TR / PR

作者把五个大市值 BTC 计价资产（`ADA/BTC`, `BNB/BTC`, `DOGE/BTC`, `ETH/BTC`, `XRP/BTC`）组成 5 腿组合，做了 **28 个月**长样本对照：

- **HFRA**：**1435.01%**
- **TR**：**935.04%**
- **PR**：低于 HFRA，且不同日/周/月/季/年重平衡频率之间没有稳定优势

同时作者还给出两个很有 desk 味道的结果：

- **1 分钟数据 > 2 分钟数据 > 5 分钟数据**
- Fisher–Pitman permutation test 支持 **HFRA 显著优于 TR / PR**

这组证据很重要，因为它说明：

> **不是“再平衡”这件事天然赚钱，而是“足够高频地捕捉篮子内错位”才是 edge 来源。**

## 7. 这篇 paper 对 desk 最值得拿走的，不是原文回报率，而是 4 个可拆组件

### 7.1 组件 A：把 pair shell 升级成 basket shell

我们最近库里已经有很多：

- pair spread z-score
- OU fade
- copula mispricing
- microprice / OBI veto pairs

这篇真正该补进来的是：

> **multi-asset equal-weight drift rebalance**

也就是：

- 不再只问“这两条腿是否回归”
- 改成问“这个篮子内部谁暂时跑太快 / 太慢了”

这能直接服务：

- sector basket（L1、公链、meme、AI、DeFi）
- beta 相近资产簇
- 由聚类 / PCA / coint shortlist 生成的 3~5 腿容器

### 7.2 组件 B：trend / vol 不是信号本体，但能当很强的 regime gate

这篇的 headline 不是 gate，但结果已经非常明确地暗示：

- **高波动上行**：最适合放大 HFRA
- **低波动**：edge 还在，但别指望放大腿数就线性增益
- **高波动下行**：需要收缩风险，不能把 rebalancing 当防空仓 shield

所以落地时最自然的做法是：

- raw alpha 还是 `equal-weight drift rebalance`
- regime gate 用：
  - basket realized vol 分位数
  - basket drift sign / BTC beta sign
  - dispersion / cross-sectional range

### 7.3 组件 C：腿数本身是风险收益旋钮

论文在多个 regime 下都给出同一个方向：

- 高频且高波时，**更多腿**通常更有利；
- 低波时，更多腿只是轻微改善；
- 坏 regime 里，更多腿更像**减亏器**而不是提收益器。

所以 desk 第一版不该只 sweep `threshold`，还该 sweep：

- `2` / `3` / `5` 腿
- 同 sector vs 跨 sector
- equal-weight vs beta-neutral

### 7.4 组件 D：continuous rebalance 是一个独立可测的 exit 设计

很多 stat-arb 回测默认都写成：

- 开仓一次
- 等均值回归
- 平仓一次

但这篇的壳更接近：

- **持续监控**
- **偏离就回补**
- **不必等待 flat-to-flat round trip**

这对 `1m / 3m` 很有启发：

- 某些 basket alpha 的 edge，可能不是单次完整 round-trip；
- 而是靠多次小回补，把内部失衡不断 harvest 掉。

## 8. 映射到 `1m / 3m / 5m / 15m` 的最小可复现实验

### 8.1 可独立复现的 raw alpha 版本

**Universe**
- Binance / Bybit / OKX 上成交最活跃的 `20~30` 个 perp
- 第一版优先按主题分篮子：L1、meme、DeFi、beta-high alt、payment coins

**Basket 构造**
- 每天或每 4h 做一次 shortlist：
  - 过去 `3~7` 天相关性高
  - 过去 `3~7` 天 Johansen / Engle-Granger 至少不过分差
  - 波动 / 成交额接近
- 从 shortlist 中取 `3` 腿或 `5` 腿组成候选篮子

**锚点**
- 目标权重先用最朴素的 **equal weight**
- 后续再对照：beta-neutral / vol-target weight

**信号 / 触发**
- 每条腿当前权重：`w_i = notional_i / basket_nav`
- 目标权重：`w* = 1 / N`
- 偏离度：`d_i = w_i - w*`
- 若 `max(|d_i|)` 超过阈值 `T`：
  - short 超配腿
  - long 低配腿
  - 把偏离拉回到 `w*` 或部分回补到 `w* ± ε`

**退出**
- 版本 A：完全照 paper，continuous rebalance，不强制 flat
- 版本 B：偏离回落至 `T/3` 时 flatten
- 版本 C：到 funding 时钟 / UTC session 边界统一 flatten

**成本**
- maker：单边 `2~4 bps`
- taker：单边 `5~8 bps`
- paper 参考：**10 bps taker**

**仓位 / 风险**
- 单篮子 gross 先固定
- 单腿 notional cap 与成交额 / open interest 挂钩
- 若篮子对 BTC 残余 beta 过大，则：
  - 缩杠杆
  - 或加一条 BTC hedge

### 8.2 真正值得 desk 先测的参数矩阵

先别一上来就卷复杂优化，第一版只扫 4 维：

1. **频率**：`1m / 3m / 5m / 15m`
2. **篮子大小**：`2 / 3 / 5` 腿
3. **阈值**：`1% ~ 12%`（perp 先从更紧区间起步，再扩到 `20%`）
4. **regime gate**：
   - `realized vol > median` vs `<= median`
   - `basket drift > 0` vs `<= 0`

这样能很快回答 3 个核心问题：

- basket shell 是否真的比 pair shell 更稳？
- 高频优势在 perp 上是否还能保留到 `3m / 5m`？
- 高波上行这个 gate 是否真的能放大净值斜率？

## 9. 下一步怎么测

### 实验 1：pair shell vs 3-leg / 5-leg shell 正面对照

- 同一 universe
- 同一成本口径
- 同一阈值集合
- 比较 `2 / 3 / 5` 腿的：
  - net pnl
  - turnover
  - per-trade edge
  - drawdown

如果 3-leg / 5-leg 明显优于 2-leg，说明这篇最值钱的不是“再平衡”而是**篮子化**。

### 实验 2：continuous rebalance vs flat-to-flat

- A：偏离超阈值就回补到等权，持续持有
- B：偏离超阈值开仓，回到 `T/3` 才平仓

这一步能回答：

> 我们的 alpha 更像“持续收割内部错位”，还是“少数几次完整 round-trip”？

### 实验 3：高波动上行 gate 是否真有用

把所有样本按：

- basket realized vol 分位数
- basket drift sign

切成四象限，观察：

- 高 vol + 上行
- 高 vol + 下行
- 低 vol + 上行
- 低 vol + 下行

若 paper 的方向在 perp 上也成立，就可以把 `high vol + uptrend` 变成明确的放量 gate。

### 实验 4：equal-weight vs beta-neutral

paper 用的是 equal-weight。对实盘 perp，我们必须补一组：

- equal-weight
- rolling beta-neutral
- vol-target equal-risk

若 equal-weight 已经足够强，说明 raw alpha 很干净；若 beta-neutral 明显改善，说明 paper 的 published gross 有相当一部分其实夹着共同方向暴露。

### 实验 5：sector basket 优先级

按主题分 4 组先跑：

- L1 basket
- meme basket
- DeFi basket
- beta-high alt basket

这一步很关键，因为 basket shell 最怕“装进去的是风格完全不同的东西”，导致所谓回补只是噪音。

## 10. 风险与可移植性提醒

### 10.1 论文是 BTC 计价现货，不是我们常做的 USDT perp

这意味着：

- 原文里的相对强弱，本质上是**相对于 BTC 的表现差**；
- 直接迁到 USDT perp 后，公共美元 beta 会更重；
- 如果不做 beta 控制，容易把“篮子内相对错位”错读成“整体 alt beta 起伏”。

### 10.2 论文里超高收益不能直接当 production 预期

像 `1435.01%` 这类长样本数字，只能当：

- 证明 HF basket rebalance 这条路**不只是概念**；
- 不能当我们在 perp 上能直接复刻的预期回报。

### 10.3 “没有通用最优阈值”本身就是结论

论文最后还明确说了：

- **不存在可事先固定的通用最佳 threshold**；
- 最优阈值和波动之间也没有简单稳定映射。

所以落地时不要想偷懒地全市场统一一个 `T`。

更合理的做法是：

- 每个 basket 独立 sweep
- 每个 regime 分开看
- 每个频率独立估计

## 11. 一句话结论

如果最近几篇 digest 已经把 `pair shell` 补得差不多了，那这篇 2024 *Financial Innovation* 最值得 intake 的，不是“高频再平衡也能赚钱”这句废话，而是：

> **把 cointegrated pair 扩成 `3~5` 腿 basket，用 equal-weight drift 当错价代理，再用 threshold rebalance 连续 harvest 内部强弱回归。**

这是一条**可独立复现、可直接落地、且非常适合 `1m / 3m / 5m / 15m` 的完整 raw alpha 壳**。

## 12. 参考来源

1. **Bağcı, M., & Kaya Soylu, P. (2024).** *Optimal portfolio selection with volatility information for a high frequency rebalancing algorithm*. **Financial Innovation**. DOI: `10.1186/s40854-023-00590-3`  
   - Readable URL: https://link.springer.com/article/10.1186/s40854-023-00590-3
2. **OpenAlex metadata** for DOI `10.1186/s40854-023-00590-3`（作者、年份、摘要、venue）
3. **Crossref metadata** for DOI `10.1186/s40854-023-00590-3`

## 13. 落地文件与页面

- Digest：`research/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.html`
