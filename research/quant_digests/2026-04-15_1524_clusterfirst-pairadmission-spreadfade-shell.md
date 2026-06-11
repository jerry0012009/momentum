# 别把这份 2022 unsupervised pairs repo 只读成普通 cointegration：对 short-cycle desk，更该先拆的是「cluster-first pair admission × spread fade」这条 raw alpha 壳

- 时间：2026-04-15 15:24 UTC
- 类型：2022 GitHub repo source audit（`README.md` + `strategies/AutoPairsTrading/__init__.py`）+ Binance USDⓈ-M `1h` public-data portability probe
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cluster-first/pair-admission/agglomerative-clustering/pca/adf/kalman/hedge-ratio/spread-zscore/binance-perpetual/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo 源码规则 + 公共历史 K 线 portability probe

- 主题类型：raw alpha
- 基础 alpha：**cointegrated spread mean reversion；真正有增量的旁支不是“spread 会回归”这句老话，而是“先用 return-surface clustering 缩小候选池，再在簇内做 ADF/hedge-ratio 选对”的 pair admission 机制。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么

### 主来源（repo）
- **Authors / Owner：** `jinczing`
- **Year：** repo latest visible commit `2022-12-22`
- **Title：** *Cryptocurrency Pairs Trading via Unsupervised Learning*
- **Venue：** GitHub repo
- **DOI：** N/A
- **Readable URL：** <https://github.com/jinczing/crypto-pairs-trader>
- **Repo URL：** <https://github.com/jinczing/crypto-pairs-trader>
- **README 可见结论：** naive cointegration baseline `Sharpe 0.47 / annualized return 8%`，clustering-based 版本 `Sharpe 1.89 / annualized return 50.44%`

### 本轮自建 probe 产物
- 汇总：`reports/artifacts/quant_digests/2026-04-15_clusterfirst_pairs_probe_summary.json`
- 小时级事件流：`reports/artifacts/quant_digests/2026-04-15_clusterfirst_pairs_probe_hourly.csv`

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 被筛选出来的 cointegrated pair 的 spread mean reversion。**

翻成人话：
- 它本体不是趋势，不是 funding，也不是横截面 winner/loser 排名；
- 它本体仍然是最经典那条 **relative-value / stat-arb raw alpha**：
  1. 找两条价格行为足够接近、但短期会偏离的币；
  2. 估计 hedge ratio；
  3. 当 spread 偏到极端时做反向；
  4. 等 spread 回到中枢就走。

这轮真正值得写的新增量，在于 repo 没把“pair 从哪来”留空，而是给了一套 **先聚类、再筛 cointegration、再滚动重选** 的 admission 机制。也就是说：
> **alpha 本体 = spread fade；增量部件 = cluster-first pair admission。**

所以它不是 filter，不是 overlay，而是一条 **可以直接写成 entry / exit / sizing / 风控的 raw alpha 壳**。

## 3. 为什么这轮还值得写，而不是把它归到“又一篇 pairs”

如果只是“再来一篇 spread z-score fade”，这轮不值得写。

这轮值得进池，原因在 3 点：

1. **它补的是“pair discovery loop”，不是只补一条 pair 本身。**  
   之前很多 pairs 主题默认 pair universe 已经给定；这份 repo 给的是：
   - 怎么把币先分簇；
   - 怎么在簇内做 candidate ranking；
   - 怎么每 `30d` 重新选对。

2. **它只用公开 K 线就能跑。**  
   不依赖私有订单流、不依赖昂贵数据商，复现门槛低，适合 desk 快速做最小实验。

3. **它天然适合 desk 做“慢 admission + 快 execution”拆分。**  
   pair selection 可以留在 `1h` 甚至更慢；真正的入场、减仓、stale-leg veto、冲击过滤，可以下沉到 `15m / 5m`。

所以这轮真正可吸收的，不一定是 repo 原版 shell 整体照搬，
而是：
> **把 cluster-first admission 当成 pairs/stat-arb book 的前置选对层。**

## 4. repo 里到底写了什么

## 4.1 先聚类，再在簇里找 pair
`strategies/AutoPairsTrading/__init__.py` 的第一层不是直接枚举全市场 pair，而是先做 feature clustering：

- 交易所：`Binance Perpetual Futures`
- 基础频率：`1h`
- universe：外部 `universe_symbols` 文件
- 特征构造：
  - 先算 `24h` price change；
  - 再对多个窗口做 rolling mean；
  - 源码窗口从 `1d` 一路拉到约 `171d`（`24*i, i=1..171 step 10`）
- 然后做：
  - 标准化；
  - `PCA` 降维；
  - `AgglomerativeClustering`（complete linkage，默认 `6` 簇）

翻成人话：
> 它不是“谁跟谁看着像就配对”，而是先按多窗口收益轮廓把币分到行为相近的簇里，再在小池子里做 pair selection。

这对 desk 的价值很直接：
- 降低全市场乱配对；
- 少做 sector 无关、风格不搭的 pair；
- 让 pair admission 更像一个系统化模块，而不是人工灵感。

## 4.2 簇内 pair ranking：OLS hedge ratio + ADF p-value
簇内每一对候选，repo 做的是：

1. 对两腿价格做线性回归；
2. 取回归残差当 spread；
3. 用 `ADF` p-value 给 pair 排序；
4. 选最优且 **symbol 不重叠** 的 pair；
5. 最多保留 `3` 对。

也就是说，repo 的 pair selection 不是“相关性大就上”，而是更接近：
> **行为先相似，再看 spread 站不站得住 mean-reverting 统计检验。**

## 4.3 pair 不是永久的，默认每 30 天重选一次
源码里：
- `period = 30`
- 到期后重新 `reevaluate_pairs()`

这点很关键，因为 crypto pair 关系很容易漂移：
- narrative 换了；
- 板块轮动换了；
- 流动性变了；
- 上币/退市变了。

因此这份 repo 真正提供的是：
> **动态 pair universe，而不是固定 pair 名单。**

## 4.4 交易逻辑很朴素：spread 偏离 ±2σ 入场，回到中枢出场
交易层不花哨，但完整：

- spread 维护：
  - 初始化 `KalmanFilter`
  - 在线更新 `beta/intercept`
- 信号层：
  - `bb_window = 24*7`（约 7 天小时级）
  - 当 spread `> mean + 2σ`：做空 spread
  - 当 spread `< mean - 2σ`：做多 spread
- 出场层：
  - 当 spread 穿越均值附近（源码里用 sign flip / zero-cross）就平仓

这意味着它不是只给 pair selection，
而是给了一条完整 raw alpha 壳：
- admission
- hedge ratio
- entry
- exit
- 重新选对

## 4.5 sizing 很粗，但足够说明这真的是完整策略，不是概念 README
repo 默认：
- 每腿仓位大致按 `balance / 6` 分配；
- hedge ratio 在 sizing 里没有完全严肃地打进去；
- 风控更多是结构性平仓，而不是精细的成本/容量控制。

所以它不是 production-ready，
但也不是一句“pairs trading 很酷”的空壳。

## 5. 我做的 Binance USDⓈ-M `1h` 最小 portability probe：选对逻辑能复现，但当前 direct shell first verdict 偏负

## 5.1 数据与口径
- **数据源：** Binance USDⓈ-M public `/fapi/v1/klines`
- **公开性：** 完全公开 REST
- **更新频率：** `1h`
- **样本：** `2025-12-16 16:00 UTC` 到 `2026-04-15 15:00 UTC`，共 `2880` 根小时 bar
- **可交易活跃子集：** `AAVE / COMP / CRV / SNX / SUSHI / UNI / YFI`
- **walk-forward 口径：**
  1. 用最近 `60d` 训练；
  2. 未来 `30d` 测试；
  3. 每 `30d` 重做一次 clustering + pair ranking；
  4. 每个测试窗最多保留 `2` 对不重叠 pair；
  5. 训练期用 OLS beta，测试期用 `7d` z-score；
  6. entry=`±2σ`，exit=`0-cross`；
  7. 成本先用较轻但不离谱的近似：**每次腿变动 `4 bps`**。

注意：
- 这不是 repo 精确复刻；
- 但足够回答一个更重要的问题：
> **这套 cluster-first admission × spread fade，在今天 active Binance perp universe 上还能不能顺手跑起来？**

## 5.2 先记最重要的 6 个数

- gross total return：约 **`-10.37%`**
- net total return：约 **`-11.00%`**
- gross Sharpe：约 **`-1.52`**
- net Sharpe：约 **`-1.63`**
- max drawdown：约 **`-15.38%`**
- trade events：约 **`35`** 次腿变动事件

两段测试窗里，选出来的 pair 分别是：
- `2026-02-14 → 2026-03-16`：`CRV-SNX`、`AAVE-SUSHI`
- `2026-03-16 → 2026-04-15`：`AAVE-COMP`、`CRV-YFI`

一句话结论：
> **pair discovery 这件事是能复现的，但 direct shell 迁到当前 liquid-major-ish DeFi perp 子集上，first verdict 偏负。**

## 5.3 这组数真正说明了什么

### 结论 1：repo 最值钱的部分，可能不是交易壳，而是 admission layer
如果这轮 probe 连 pair 都选不出来，那就没什么好说的。
但现在不是这样：
- clustering 能稳定把 pair pool 缩出来；
- ADF ranking 能挑出看上去合理的 DeFi 对；
- 问题主要出在 **直接交易壳** 的 portable performance。

所以真正可复用的部分更像：
> **cluster-first pair admission，是一块可插拔组件；原版 spread fade 壳，不应直接抬进 production 候选池。**

### 结论 2：当前 active universe 比 repo 当年的候选池更窄
repo 里原始 universe 有不少今天已经不在 Binance USDⓈ-M 活跃交易的符号：
- `BAL`
- `DODO`
- `LRC`
- `MKR`
- `REN`

这意味着：
- 原 repo 的 pair ecology，今天已经变了；
- 你现在能跑的只是残余活跃子集；
- cluster admission 还在，但 alpha 密度可能已经被 universe 变化削弱。

### 结论 3：short-cycle desk 不该把它理解成“又一条现成 pair alpha”
更诚实的 desk 读法应该是：
- **base alpha** 仍是 spread MR；
- **真正新增量** 是 pair admission；
- **正确用法** 是拿 admission 去喂更强的 spread/trade engine，而不是照抄原壳。

## 6. 这条线对 `1m / 3m / 5m / 15m` 的正确定位

## 6.1 它服务短周期 desk 的方式，不是把 selection 本身压到 1m
最合理的拆法是：

- **selection layer（慢）：** `1h / 4h / daily` 更新 cluster + pair list
- **signal layer（中）：** `15m` 做 spread z-score / residual excursion
- **execution layer（快）：** `5m / 1m` 做 stale-leg、盘口深度、滑点和 maker/taker 选择
- **risk layer：** 遇到单腿异常拉升、funding 扭曲、盘口抽空就 veto

也就是说，它对 short-cycle desk 的意义不是“高频选 pair”，而是：
> **给你一个更系统化的 pair admission 前置层。**

## 6.2 所以这轮主题仍然算 raw alpha，但当前 priority 不该太高
为什么仍算 raw alpha？
- 因为 base alpha 很清楚，就是 spread mean reversion；
- repo 也给了完整 entry / exit / sizing 壳。

为什么 current priority 不该太高？
- 因为 public-data first probe 偏负；
- 说明这条壳不该直接排进“先做 production replication”的第一梯队。

更合理的结论是：
> **主题合格，部件有价值，但现阶段更像“pairs book 的 reusable admission module”，不是现成 alpha winner。**

## 7. 风险与保留意见

1. **repo 的成绩大概率强依赖当时 universe。**  
   当前活跃子集缩水后，pair 结构已经变了。

2. **probe 不是精确复刻。**  
   我这里为了快速判断 portability，做了简化版 walk-forward，而不是完整还原 Jesse 环境与在线 Kalman 状态机。

3. **原 repo sizing 很粗。**  
   若真上 desk，至少要补：
   - gross exposure cap
   - beta-neutral sizing
   - 单腿极端偏离 kill-switch
   - funding / fee / slippage 更真实口径

4. **这条线很容易被误读成“pairs 永远有用”。**  
   实际上，这轮恰恰说明：
   - pair admission 可以保留；
   - 直接 spread fade 壳未必还好用。

## 8. 我给这轮主题的结论

> **这是一个合格的新 raw alpha 主题，但当前真正值得 desk 吸收的，不是“照抄 2022 clustering-based pairs shell”，而是“cluster-first pair admission”这块模块化组件。**

更具体地说：
- **值得进研究池**，因为 base alpha 清楚、复现门槛低、源码完整；
- **值得保留 admission 逻辑**，因为它给了 pairs/stat-arb book 一个比“全市场乱扫 pair”更系统的入口；
- **不值得直接升成当前优先 production shell**，因为这轮 public-data portability first verdict 偏负。

## 9. 下一步怎么测

按优先级，我建议直接做这 5 步：

1. **把 selection 和 trading engine 分开评估**  
   先固定这套 clustering admission，只替换交易壳：
   - 传统 z-score fade；
   - OU / s-score；
   - microprice / OBI 辅助入场；
   看问题到底出在 pair list，还是出在交易壳。

2. **做 `15m` execution 版，而不是继续全靠 `1h` 触发**  
   `1h` 负责选 pair，`15m` 负责：
   - 更细的 spread 极值确认；
   - stale-leg veto；
   - maker-first / taker-fallback。

3. **把 clustering admission 和“纯 ADF 全市场扫 pair”做 head-to-head**  
   直接比较：
   - pair 稳定性
   - 未来 30d half-life
   - gross/net Sharpe
   - turnover
   看 clustering 到底提供了多少真实增量。

4. **扩成 sector-aware universe，而不是只看剩下的老 DeFi 币**  
   下一版不要只盯 `AAVE/COMP/CRV/SNX/SUSHI/UNI/YFI`，应扩到：
   - DeFi 一组
   - L1/L2 一组
   - meme 一组
   - exchange / infra 一组
   看 cluster-first admission 在更大 universe 下是否反而更有价值。

5. **把 funding / liquidity veto 接上去**  
   对 pair 两腿补 3 个 veto：
   - funding gap 突然扭曲；
   - 单腿成交额骤降；
   - 单腿 `5m` 冲击超过阈值。  
   这一步最可能把“统计上像 pair、交易上却很脏”的假机会筛掉。
