# 别把 PCA 只当老教材因子分解：对 crypto short-cycle desk，更该先测的是「eigenportfolio residual s-score fade」这条 cross-sectional raw alpha

- 主题类型：raw alpha
- 基础 alpha：**先用 rolling PCA 剥掉市场共同因子，再对单币 residual 做 OU / s-score 均值回归交易**；翻成人话，就是“不是盯某一对 coin 的 spread，而是先把全市场共振拿掉，再抓单币相对篮子偏离后的短周期回归”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 11:24 UTC
- 类型：2026 GitHub 新 repo source audit（`README.txt` + `src/pca_engine.py` + `src/residual_model.py` + `src/ou_estimator.py` + `src/s_score.py` + `src/strategy.py` + `src/backtester.py` + `main.py`）+ 2010 *Quantitative Finance* 经典论文元数据 + Binance USDⓈ-M `15m` 本地最小 sanity check
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/mean-reversion/pca/eigenportfolio/residual/ou/s-score/market-neutral/binance-perpetual/top-basket/15m/5m/3m/1m/repo/paper/public-data/cost
- 证据类型：repo-first（完整策略骨架）+ classic-paper grounding + public-data quick check

## 1. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：cross-sectional residual mean reversion。**

不是“PCA 可以解释市场结构”这种研究口号；真正能交易的是：

> **先用前两条主成分把一篮子币的共同波动剥掉，再去抓某个币相对这两个公共因子的异常偏离；当偏离过大，就赌它往篮子均值方向回。**

所以它是 **raw alpha**，而不是 filter / regime / overlay。

---

## 2. 为什么这轮值得写它
最近 digest 池里已经有很多：
- 单币 microstructure
- cointegration pairs
- funding / basis / carry
- cross-market lead-lag

但 **“全市场 residualized 之后再做 cross-sectional mean reversion”** 这条线，反而没有被系统地写进素材池。

这轮值得 intake 的原因有四个：

1. **它是完整 raw alpha 壳子，不是解释性材料。**
   - 从 entry 到 exit 到 sizing 都能直接写出来；
2. **它扩的是 raw alpha 素材池，不是继续给 breakout 找 confirmation。**
   - 而且服务的是 `cross-sectional / relative value / stat-arb` 主线；
3. **它和现有 pairs 方向互补。**
   - pairs 先选一对；
   - 这条是先看整个 universe，再找“谁偏离了公共因子”；
4. **它对 `5m / 15m` 的 desk transfer 很自然。**
   - PCA / residual / OU 这些东西在 1m 上也能做，但更像高噪状态下的 fast admission；
   - 真正容易先做出像样最小实验的，是 `5m / 15m`。

如果问：“它为什么比继续补一篇 filter 更值？”
答案很简单：
**因为它本身就是一条可以独立下注的 alpha，而不是拿来给别的策略当门卫。**

---

## 3. 这次看的主来源

### 3.1 主来源：2026 新 repo（主）
- **Owner / Year**: sophie-lan, 2026（repo 最近更新 2026-03-04；首次提交 2025-12-01）
- **Title**: `crypto-pca-statarb`
- **Venue**: GitHub repository
- **DOI**: N/A
- **Readable URL / Repo URL**: https://github.com/sophie-lan/crypto-pca-statarb
- **实际看的文件**:
  - `README.txt`
  - `src/pca_engine.py`
  - `src/residual_model.py`
  - `src/ou_estimator.py`
  - `src/s_score.py`
  - `src/strategy.py`
  - `src/backtester.py`
  - `main.py`

### 3.2 理论地基：经典论文（辅）
- **Authors / Year**: Marco Avellaneda, Jeong-Hyun Lee, 2010
- **Title**: *Statistical arbitrage in the US equities market*
- **Venue**: *Quantitative Finance*
- **DOI**: `10.1080/14697680903124632`
- **Readable URL**: https://doi.org/10.1080/14697680903124632
- **Working-paper DOI**: `10.2139/ssrn.1153505`
- **Repo URL**: N/A

### 3.3 最小实验数据源（公开可得）
- **Venue**: Binance USDⓈ-M Futures public klines API
- **Readable URL**: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
- **公开性**: 全公开、无需付费 key（市场数据）
- **可映射周期**: `1m / 3m / 5m / 15m`

---

## 4. repo 里最值钱的，不是“PCA”两个字，而是完整的 residual mean-reversion pipeline
这份 repo 的价值，不在于它说了一个大家都知道的词：PCA。
真正值钱的是它把一条完整的 alpha 链条写实了：

1. **rolling PCA 因子构建**
2. **单币对前两因子的回归残差**
3. **残差积分过程的 OU 参数估计**
4. **s-score 打分**
5. **阈值开平仓**
6. **组合回测**

翻成人话：
**不是先拍脑袋找一对 coin 的价差，而是先让全市场自己长出两个共同因子，再看哪几个币相对这个共振框架偏得最离谱。**

这比“手工 pairs shortlist + z-score fade”更像一条可批量化、可扩 universe 的 stat-arb 主线。

---

## 5. 代码级拆解：这条 raw alpha 到底怎么成型

### 5.1 PCA 层：先把共振因子提出来
`src/pca_engine.py` 里最关键的参数是：
- **window_size = 240**
- **min_valid_ratio = 0.8**
- 每个时点取 **当前 universe** 的 token，回看过去窗口
- 对 log returns 做标准化后，在 **相关系数矩阵** 上做 PCA
- 只取 **前两个主成分**
- 再把 eigenvector 按波动率缩放，构成 **eigenportfolio weights**

repo 默认数据是：
- **hourly 价格**
- **top-40 token universe**
- 测试区间：`2021-09-26` 到 `2022-09-25`

这意味着原 repo 的原始时间尺度是：
- `240` 小时滚动窗，约 **10 天**；
- 40 币 universe；
- 每小时更新一轮 PCA / residual / signal。

对 desk 的翻译就是：
**先做“全市场共同运动”的压缩，再做单币相对偏离，而不是直接拿原始价格硬做 mean reversion。**

### 5.2 Residual 层：不是看绝对收益，而是看“剥离因子后的 idiosyncratic move”
`src/residual_model.py` 对每个 token 做：

`r_i = beta0 + beta1 * F1 + beta2 * F2 + eps_i`

也就是：
- `F1 / F2` 是第一、第二 PCA factor return；
- `eps_i` 才是单币相对公共因子的残差。

实现细节：
- 仍然用 `240` 窗口；
- 最少样本 `30`；
- ridge 正则 `1e-5`；
- 最终 residual 会再次去均值。

这一步是整条 alpha 的灵魂：
**它交易的不是“币涨多了会跌”，而是“币相对市场共振涨太多/跌太多，可能会回”。**

### 5.3 OU / s-score 层：把 residual 变成“可交易偏离分数”
`src/ou_estimator.py` 先把 residual 累积成 `X_t = cumsum(eps)`，再拟合：

`X_{t+1} = a + b * X_t + error`

若 `0 < b < 1`，再换成 OU 参数：
- `kappa`
- `m`
- `sigma_eq`

然后 `src/s_score.py` 用：

`s = (X_t - m) / sigma_eq`

也就是说，**s-score 不是普通 z-score，而是“相对 OU 平衡点的标准化偏离”。**

这对 short-cycle desk 的意义是：
- 你不只是看 spread 偏得多不多；
- 还在看“它相对自身回归结构偏得有多远”。

### 5.4 Trading rule：repo 已经给出开平仓阈值
`src/strategy.py` 默认参数：
- `s_bo = 1.25`：开多阈值（`s <= -1.25`）
- `s_so = 1.25`：开空阈值（`s >= +1.25`）
- `s_bc = 0.75`：多头平仓阈值（`s >= -0.75`）
- `s_sc = 1.0`：空头平仓阈值（`s <= +1.0`）
- `trade_size = 1.0`

翻成人话：
- 偏得够离谱才开；
- 回到没那么离谱就收；
- 多空平仓阈值还有一点非对称。

这已经是一条 **完整 raw alpha 策略骨架**，不是只给你一个因子图表。

### 5.5 回测器也暴露了最核心的现实问题：repo 默认没算成本
`README.txt` 明写：
- **Transaction costs and slippage are not modelled**
- 默认假设 **perfect execution at hourly close prices**

这件事非常重要。
因为这类 residual mean reversion 策略最容易出现的情况就是：

> **gross 有 edge，net 被 turnover 吃掉。**

所以这条线能不能进实盘，不取决于“PCA 很高级”，而取决于：
- 交易频率能不能压下来；
- maker / passive fill 能不能吃到；
- 组合是否能做 beta-neutral / factor-neutral；
- 是否能只交易最极端的几只，而不是全篮子频繁翻。

---

## 6. 这条 alpha 为什么是 raw alpha，而不是 filter
因为它的入场逻辑本身已经闭环了：

1. 提取公共因子；
2. 找单币 residual 偏离；
3. 用 OU / s-score 判断偏离是否够极端；
4. 直接开仓赌回归。

它不是：
- “先有 breakout，再用它决定要不要追”；
- 也不是“先有趋势策略，再拿它缩仓位”。

它自己就是一条完整下注逻辑。

所以分类上应该放在：
**raw alpha / cross-sectional / relative-value / stat-arb / mean reversion**

而不是 filter / overlay。

---

## 7. 对当前 desk，更值得拿走的不是 hourly 原样复刻，而是这三个 desk 化改写
repo 用的是 hourly；我们真正该拿走的是下面三个 desk 化方向：

### 7.1 `15m`：第一优先的移植层
这条线最自然的第一站其实是 `15m`：
- 噪音比 `1m` 小；
- 还保留足够短的 mean-reversion 半衰期；
- 执行和成本更有机会活下来。

### 7.2 `5m`：如果想更快，要先做 sparse + cooldown
`5m` 可以做，但别直接把 hourly repo 粗暴降采样：
- 需要更稀疏的 admission；
- 需要 cooldown；
- 需要只交易绝对值最大的 `top-k |s|`；
- 需要更强的 vol / spread / liquidity gate。

### 7.3 `1m / 3m`：更像 fast admission layer，而不是整篮子主壳
在 `1m / 3m` 上直接全篮子滚动翻仓，很容易死于：
- fees
- queue position
- micro-noise
- residual estimation instability

所以更合理的是：
- 用 `1m / 3m` 做 admission / refresh；
- 真正持仓决策落到 `5m / 15m`；
- 或只做最极端的 1~2 个名字。

---

## 8. 我做的 Binance `15m` 最小 sanity check：raw alpha 有影子，但 turnover 明显是第一杀手
为了避免这轮变成纯 repo 摘抄，我补了一版 **repo-inspired 的公开数据 existence check**。

### 8.1 实验口径（简化版）
- 数据源：Binance USDⓈ-M public klines
- 周期：`15m`
- 标的：`BTC, ETH, BNB, SOL, XRP, DOGE, ADA, SUI`
- 长度：最近 **1500 根 15m bars**（约 `2026-03-17` 到 `2026-04-02`）
- 做法：
  1. rolling `240` bars PCA（取前 2 因子）
  2. 单币对因子回归取 residual
  3. residual 累积后拟合 OU
  4. 用 repo 默认 `±1.25` s-score 开仓思路
  5. 等权组合持有下一根 bar

> 注意：这不是严格复现 repo，也不是 production backtest；只是为了回答一句：**这条壳子在公开 15m 数据上有没有“先活一下”的迹象。**

### 8.2 最关键的结果
我认为最有信息量的 5 个数字是：

1. **样本可交易观测数：1258**
2. **active ratio：82.7%**
3. **成本前 cumulative return：+4.77%**
4. **成本前年化 Sharpe：4.03**
5. **若按每个 active bar 粗加 `5 bps` 成本，累计直接掉到 `-37.7%`**

另外，把“新开仓事件”单独拿出来看：
- **avg next-1-bar markout：+1.19 bps**
- **avg next-3-bar markout：-0.22 bps**

### 8.3 这组数字说明什么
说明两件事同时成立：

#### A. raw alpha 不是假的
如果完全没东西，gross 不会先站起来。
所以“公共因子剥离后做 residual fade”这条路，**有继续研究价值**。

#### B. 但当前壳子过于密，执行会先把你杀掉
active ratio `82.7%` 基本已经说明：
- 它不是一个可以粗暴 taker 化的 alpha；
- 必须做 turnover compression；
- 必须做 sparse ranking；
- 必须重新设计 entry / re-entry / hold / close；
- 必须严肃做 cost ladder。

所以它不是“明天可上线”，但它是：
**值得继续拆成更适合 desk 的 residual stat-arb 素材。**

---

## 9. 对 short-cycle desk，真正该落地成哪版策略
我建议别照抄 repo 的“全 universe 全时点同强度翻仓”，而是改成下面这版。

### 9.1 Universe
先用最液体的 `8~20` 个永续：
- `BTC, ETH, SOL, BNB, XRP, DOGE, ADA, SUI` 起步
- 后面再扩到 top20 USDT perps

### 9.2 Sampling
- 主版本：`15m`
- 快版本：`5m`
- `1m / 3m` 只做 admission / refresh，不直接当主回测壳

### 9.3 Factor / residual
- PCA 因子数先固定 `2`
- 比较两种窗长：
  - **bar-count 继承**：`240 bars`
  - **time-span 继承**：如果从 hourly 的 240h 等价迁到 15m，则是 `960 bars`
- 单币 residual 仍然先用线性回归

### 9.4 Entry
不要全篮子同时上，先做：
- 每个 bar 只选 `top-k` 的 `|s|`（例如 `k=2~4`）
- 只在 `|s| >= 1.5 / 1.75 / 2.0` 才入场
- 若 coin 的 spread / vol / liquidity 不达标，则 veto

### 9.5 Exit
比 repo 更适合 desk 的版本：
- `s` 回到 `|s| < 0.5` 平仓
- 或固定持有 `1 / 2 / 4` 根 `15m` bar
- 或加 `cooldown`，避免刚平就反向重开
- 默认不要 instant flip，先 flat 再等下一轮信号

### 9.6 Sizing
- 按 `|s|` 或 residual vol 做分级，不要固定 `1.0`
- 组合层面做 gross cap
- 最好做 market / factor neutral，避免变成偷渡 beta

### 9.7 Cost
至少做三层：
- maker optimistic
- hybrid realistic
- taker pessimistic

因为这条线最怕的不是预测不准，而是 **预测太频繁**。

---

## 10. 它和现有 pairs / XS / stat-arb 素材池的关系
这条线的价值，在于它能补足一个很实用的中间层：

- **pairs**：先选一对，再赌两者回归
- **cross-sectional mean reversion**：先排序，再赌输家回归 /赢家回落
- **PCA residual stat-arb**：先提取共同因子，再赌 idiosyncratic 偏离回归

所以它既不是老式 pairs 的重复，也不是普通 loser-winner reversal 的重复。
它更像：

> **用“全市场共同因子剥离”来提高 mean reversion 命中的纯度。**

这很适合进入我们当前的 `cross-sectional / relative-value / stat-arb` 素材池。

---

## 11. 失败模式与要避开的坑

### 11.1 把 gross edge 当可交易 edge
这条线最容易犯的错就是：
- 看到 gross 好看；
- 忘了 turnover 可能直接毁掉 net。

### 11.2 把 hourly 参数原样砸进 `5m`
从 `1h` 下放到 `5m / 15m`，不是简单改 interval。
窗长、阈值、cooldown、holding 都要重估。

### 11.3 不做 neutralization
如果不控制市场 beta，最后可能只是：
- 牛市里多一堆“看起来低估”的币；
- 熊市里空一堆“看起来高估”的币。

### 11.4 让 universe 太杂
低流动、小币、跳价大、盘口差的标的会把 residual 估计搞脏。
第一轮一定要先做高流动篮子。

---

## 12. 一句话结论
如果只带走一句话，我会带走这句：

**别把 PCA 只当“老教材因子分解”；对 crypto short-cycle desk，更值得快检的是「先剥掉全市场共振，再做单币 residual s-score fade」这条 cross-sectional raw alpha。**

它的优点是：
- raw alpha 清楚；
- 完整策略骨架现成；
- 能直接扩充 stat-arb / relative-value 素材池。

它的现实约束也同样清楚：
- **gross 可能有 edge，net 很可能先死于 turnover。**

所以它该进研究池，但应该以 **sparse / cost-aware / neutralized** 的 desk 版本继续推进，而不是把 repo 原样当答案。

---

## 13. 下一步怎么测（直接执行版）
1. **先做 `15m` 正式最小实验**：top20 USDT perps，比较 `240 bars` vs `960 bars` 两种窗长继承方式。
2. **把 entry 改成 sparse ranking**：每根 bar 只交易 `top-2 / top-4 |s|`，并扫 `|s|` 阈值 `1.5 / 1.75 / 2.0`。
3. **固定回答成本问题**：maker / hybrid / taker 三档 cost ladder，别只看 gross。
4. **做 neutralization ablation**：
   - 不中性化
   - dollar-neutral
   - beta-neutral / factor-neutral
5. **检查持有期真半衰期**：比较 `next-1 / next-2 / next-4 bars`，确认它是不是只活一根 bar。
6. **如果 15m 有戏，再下放到 5m**；若 5m turnover 爆炸，就把 `1m / 3m` 限定成 admission / refresh 层，而不是主壳。

---

## 14. 文件信息
- 文件路径：`research/quant_digests/2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.html`
