# 别把这份 2026 策略集只读成股票 API：对 short-cycle desk，更该先测的是「normalized cluster deviation × next-bar snapback」这条 raw alpha
- 时间：2026-04-08 13:58 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/strategies/stocks/mean_reversion_cluster.py`）+ Binance Spot public `15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：同簇资产相对均值路径的归一化离差回归（cluster-relative mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / cross-sectional / relative-value / stat-arb / cluster / zscore / 15m / 5m / 3m / 1m / repo / public-data / cost / risk
- 证据类型：工程经验 + 公共数据 portability probe

## 1. 这次看了什么
看的是 `ThewindMom/151-trading-strategies` 里 `Strategy 3.9: Mean-Reversion (Cluster)`：源码默认把一组相关资产的价格矩阵求 `cluster_mean`，再对每个资产的 `asset - cluster_mean` 做 z-score，`entry_zscore=2.0` 反向开仓、`exit_zscore=0.5` 平仓。它表面上是股票 sector API，但对 crypto desk 真正有价值的不是“原样抄 price-level”，而是把它改写成**归一化路径离差**的短周期 raw alpha。

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值钱的不是“cluster 平均价”本身，而是“先把同簇资产放到同一条归一化路径上，再做离差 snapback”。
- **一句话证明方式**：证据来自两层——先做源码审计确认规则极简、可独立复现；再用 Binance 公共 `15m` 数据对 `ETH/BNB/SOL/XRP/DOGE` 做最小 portability probe。
- repo 原版逻辑很简单：`lookback=60`，对每个资产的离差序列算均值/标准差，`z>2` 做空、`z<-2` 做多、`|z|<0.5` 平仓。这个壳已经足够完整，缺的是 crypto 版归一化与成本层。
- 直接拿**原始价格**做 cluster mean 在 crypto 横截面很危险，因为 `DOGE` 和 `ETH` 的价格单位天生不可比；更合理的是在滚动窗口里先转成累计 log-return 路径，再比较相对 cluster 的偏离。
- 我用 Binance 最近 `1000` 根 `15m` 公共 bar 做了一个轻量 probe：若用 `24` 根窗口、每根都做“long 最低 z / short 最高 z”，下一根均值约 **+0.611 bps/trade**（`t≈0.965`, `n=974`）；窗口拉到 `48` 根时，下一根约 **+0.698 bps/trade**（`t≈1.037`, `n=950`）。
- 但把持有期拉到 `4` 根后，`24` 根窗口变成 **-0.277 bps/trade**，`48` 根窗口变成 **-0.425 bps/trade**；说明这更像**很快收口的 snapback**，不是能慢慢抱的 swing MR。
- 阈值也未显示“越极端越好”：`24` 根窗口下，要求 `|z|>1` 只剩 **77** 笔，均值约 **+0.326 bps/trade**；对 desk 来说，先做**宽进场 + 小仓位 + 快 time-stop**，比追求稀疏大离差更像第一版。

## 3. 为什么和当前项目有关
这条线直接补的是 **raw alpha 素材池**，而且属于我们现在缺口更大的 `mean reversion / relative value / stat-arb` 家族，不是又一个 breakout/filter。相比只做双腿 pairs，它把对象从“单对”放宽到“相关簇里的离群点”，更适合 crypto 里经常一起跑、偶尔单腿失衡的板块（L1、exchange token、meme、AI、DeFi）。更重要的是，刚才的 probe 已经给出一个 desk 级判断：**如果要做，优先做 1-bar/2-bar 的快收口，不要默认 1h 级抱仓。**

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回复
- 基础 alpha：资产相对同簇归一化路径的 z-score 离差回归
- regime：簇内相关性仍高、但单腿出现短时 idiosyncratic overshoot
- filter / veto：只做 top-liquid 成员；事件币/上新币/大额清算时 veto；簇内相关性掉到阈值下时停机
- risk / sizing / execution overlay：按 `|z|` 和簇内波动缩仓；单簇名义敞口封顶；双腿尽量 maker-ish 或至少同步成交；默认 `1~2` 根 time-stop

## 4. 可复刻的最小实验
- 研究假设：在相关 alt 簇里，单腿短时超涨/超跌，相对 cluster 均值会比 outright 趋势更快回归。
- 可计算定义：对每个簇成员，在滚动 `24/48` 根里把 log-return 累加成归一化路径；`spread_i = path_i - mean(path_cluster)`；`z_i = (spread_i[-1] - mean(spread_i)) / std(spread_i)`；做 `long argmin(z)`、`short argmax(z)`，或仅在 `|z|>0.5/1.0` 时入场。
- 最小回测切口：Binance/OKX top-liquid perp；先手工定义 `3~5` 个主题簇（如 `ETH/BNB/SOL/AVAX/ADA`），基线跑 `15m`，再下钻到 `5m/3m`。
- 最该先看：**成本后 expectancy/trade**、**holding decay（1/2/4 bar）**。如果 `1 bar` 最强、`4 bar` 明显转负，就应把它当快收口 alpha，而不是中周期配对。

## 5. 风险与保留意见
- repo 原版直接对**原始价格**求 cluster mean，移植到 crypto 前必须先做归一化，否则很容易只是价格量纲幻觉。
- 上面的 probe 还是**pre-cost**，也没加 funding、冲击、双腿不同步成交；0.6~0.7 bps/trade 这种量级，如果全 taker，很可能直接被吃光。
- cluster 定义本身也会过拟合：主题簇、滚动相关簇、成交量簇，三者表现可能差很多；真正该优化的是**簇生成和成交方式**，不是先暴力调 z-score。

## 6. 来源
- ThewindMom. (2026). *151 Trading Strategies API*. GitHub.
  - Repo URL: `https://github.com/ThewindMom/151-trading-strategies`
  - Readable URL: `https://github.com/ThewindMom/151-trading-strategies/blob/main/src/strategies/stocks/mean_reversion_cluster.py`
- 相关源码要点：`lookback=60`、`entry_zscore=2.0`、`exit_zscore=0.5`，对每个资产计算 `spread = asset - cluster_mean` 的当前 z-score，并给出反向信号。
