# 别把这份 2026 crypto stat-arb repo 只读成“又一个 cointegration pair 模板”：对 short-cycle crypto desk，更该先保留的是「同簇 cointegrated spread fade × Hurst regime gate × hub concentration cap」这条完整 raw alpha 壳
- 时间：2026-04-23 03:47 UTC
- 类型：GitHub repo audit / 最小 portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegrated pair spread 偏离后的均值回复（spread z-score fade）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / Hurst / Kalman / clustering / concentration-cap / Binance / 15m / 5m / repo / public-data / cost / risk
- 证据类型：repo 规则拆解 + Binance USDⓈ-M public-data portability probe

## 1. 这次看了什么
这次看的不是论文，而是 2026 GitHub 仓库 **Jing-Lavinia / Pairs-Trading**。它的价值不在“又做了一次 pair spread fade”，而在于把一条 **可实盘化的 pairs/stat-arb 策略壳** 写得很完整：
- 先用 **PCA + DBSCAN** 把结构相近的币分到同簇，降低 pair search space；
- 再做 **Engle-Granger cointegration + half-life** 筛选；
- 用 **Kalman filter** 跟踪动态 hedge ratio；
- 用 **rolling Hurst exponent** 只在更像均值回复的状态里放行；
- 最后配上 **threshold grid search、time stop、hub-stock concentration cap、full cost accounting**。

如果只盯着 repo headline 的 `1H` 回测收益，会错过它对我们更值钱的那部分：**它把“pair fade 怎么变成一个完整策略壳”说清楚了**。

## 2. 先回答：这篇东西的 base alpha 是什么？
一句话：**base alpha 就是 cointegrated spread 的均值回复**。

也就是：
- 先找两条长期共同漂移、但短期会偏离的价格序列；
- 当 spread 偏离均值太远时，做相对价值回归；
- spread 回到中枢、或者失真继续扩大、或者拖太久没回，就退出。

所以这篇东西不是纯 filter，不是纯 overlay。**它本体就是 raw alpha**；Hurst / clustering / concentration cap 只是让这条 raw alpha 更像可交易策略，而不是课堂练习。

## 3. 核心结论
- 这份 repo 的主线很适合当前 desk，因为它补的正是我们需要的 **pairs / stat-arb 完整策略壳**，而不是又一个只给开平仓、不管 admission 和组合拥挤的简化脚本。
- repo 自报的 `1H` 严格 OOS 结果是：**Sharpe 3.77 / CAGR 92.15% / MaxDD -3.37% / 16 对 active pairs / taker+slippage 4.5 bps per leg**。这些数字不能直接外推到 `5m/15m`，但至少说明作者不是只写了个玩具扫描器。
- 我做了一个更贴 desk 的 **Binance USDⓈ-M portability probe**（8 个 liquid majors，`15m/5m`，pair 简化版）：
  - **15m 全对平均**：不加 gate 约 **-1.06 bps/笔 net**；加 `H < 0.60` 后约 **-1.17 bps/笔 net**，说明在 `15m` 上，**不是所有 pair 都值得做**，更重要的是 pair selection。
  - **15m 亮点 pair：`LINKUSDT/AVAXUSDT`**，加 gate 后约 **+22.14 bps/笔 net**、**75% win rate**、累计约 **+1416.7 bps**；这说明这条 alpha 在短周期上并没有死，只是需要选对 pair。
  - **5m 全对平均**：不加 gate 约 **-12.09 bps/笔 net**；加 gate 后改善到约 **-9.73 bps/笔 net**。也就是说 **Hurst gate 对高频噪声有帮助，但单靠 gate 还不够覆盖成本**。
  - **5m 的正 pocket** 依然存在：比如 `BNBUSDT/AVAXUSDT` 在 gate 后约 **+12.86 bps/笔 net**，`SOLUSDT/AVAXUSDT` 约 **+9.26 bps/笔 net**，`XRPUSDT/AVAXUSDT` 约 **+8.63 bps/笔 net**。
- 这给我们的直接启示不是“整个 universe 直接上线”，而是：**把它当成“pair discovery + regime gating + concentration control”的壳，再往 liquid cluster、maker/taker、pair ranking 上继续加约束。**

## 4. 为什么和当前项目直接相关
当前 desk 已经积累了不少单资产 trend / reversal / carry 方向的素材，但 **pairs / stat-arb** 这条线更容易遇到两个实盘问题：
1. pair 太多，容易 over-search；
2. 单个强节点（例如 ETH / BNB 一类）会在组合里被过度复用，最后看起来是多对分散，实际上是同一个风险因子被放大。

这份 repo 恰好把这两个问题都正面写进去了：
- **同簇 pair discovery**：先缩小搜索空间，再做 cointegration；
- **hub-stock cap**：不给任何一个币同时挂太多活跃 pair。

对 short-cycle desk 来说，这比“又一个 z-score=2 开仓、0 平仓”的 pair 教程更有用，因为它更接近 **真实组合部署**。

## 5. repo 里最值得搬的，不是 headline，而是这 5 个部件

### 5.1 同簇预筛：别让 pair search 失控
repo 先对 1H log returns 做：
- `StandardScaler`
- `PCA(5)`
- `DBSCAN(eps=15, min_samples=2)`

然后只在**同一个 cluster label** 里做后续 pair 检验。这个动作不是 alpha 本体，但很实用：
- 它降低搜索空间；
- 它让 pair 更像“同驱动、短期失衡”；
- 它减少那种表面 cointegrated、实际基本不该配的胡乱组合。

对我们来说，可以把它翻成更轻量的 short-cycle 版本：
- `15m` 用最近 `20~30d` returns；
- `5m` 用最近 `5~10d` returns；
- 先聚成若干 liquid sub-cluster，再只在 cluster 内做 pair ranking。

### 5.2 cointegration + half-life：先确保这不是随机价差
repo 的第二层 admission 是：
- Engle-Granger `p <= 0.05`
- `half-life` 在 `[4h, 48h]`

这背后的想法很朴素：
- 太快回去的 spread，多半没有 enough room 覆盖成本；
- 太慢回去的 spread，不像适合短周期 desk 的交易对象。

这个约束对 `15m/5m` 特别重要，因为短周期最怕的不是“没信号”，而是**看起来像 alpha，实际上只是高噪音 + 高周转**。

### 5.3 Kalman hedge ratio：别把配比当常数
repo 用 Kalman filter 跟踪动态 `gamma_t`，而不是把 hedge ratio 固定死。这个点我们其实已经在别的 digest 里见过，但这份 repo 把它自然嵌进了完整 shell：
- 先在 pair 级别做 cointegration admission；
- 再在 bar-by-bar 执行时用动态对冲比更新 spread。

这对 crypto 尤其合理，因为相关币之间的 beta 漂移比股票 pair 更快。

### 5.4 Hurst gate：它不是 alpha，本质是“别在趋势态里做 fade”
repo 用 rolling Hurst exponent，当 **`H < 0.60`** 才允许开新仓。

这层东西不该伪装成主 alpha，本质上它是：
- 服务于 **spread fade** 这条 raw alpha 的 **regime gate**；
- 目的是在 spread 已经进入趋势化/崩坏阶段时，别继续按“会回归”假设硬接。

从我这次最小 probe 来看，这层 gate 的效果是：
- **在 `5m` 平均层面确实改善了结果**，说明它在更吵的频段有一定过滤价值；
- 但它**不能单独拯救坏 pair**，所以它更像“第二层 admission”，不是第一优先级。

### 5.5 hub cap：这是最像实盘组件、也最容易被忽略的一层
repo 明确写了：**任何单币最多参与 3 对 active pairs**。

这看起来像小细节，实际上非常 desk-friendly：
- 避免 ETH / BNB / BTC 成为“伪分散组合”的共同风险源；
- 避免某个 cluster 的单点事件把整个组合一起带崩；
- 让 pair book 更像真正 diversified relative-value book。

这层在我们后续真做 multi-pair deployment 时，重要性可能不低于 entry threshold 本身。

## 6. 我自己的最小 portability probe 做了什么
为了不只停留在 repo README，我做了一个简化 probe：
- 资产：`BTC/ETH/SOL/BNB/XRP/DOGE/LINK/AVAX`；
- 数据：Binance USDⓈ-M public klines；
- 周期：`15m`（近 `120d`）+ `5m`（近 `45d`）；
- 训练/测试：前 `60%` 做 pair discovery，后 `40%` 做 OOS 风格测试；
- 预筛：相关性 + OU slope 显著性 + half-life 区间；
- 交易规则：`|z| >= 2` 入场，`|z| <= 0.5` 止盈，`|z| >= 4` 止损，`1.5 × half-life` time stop；
- 成本：粗扣 **18 bps round-trip**（两条腿 × 进出场）。

这里我没有完全复刻 repo 的 PCA+DBSCAN、Kalman 动态 beta、full walk-forward weekly refresh；所以它是 **portability probe**，不是 repo 的一比一 reproduction。但已经足够回答一个关键问题：

> 这条 raw alpha 迁到 `15m/5m` 后，是完全死掉，还是还有可筛选的正 pocket？

结论是：**还有 pocket，但不能无脑全做。**

## 7. 研究结论该怎么落地成 desk 版本
如果把这份东西翻成我们更可执行的 desk 版本，我会这样拆：

### 7.1 alpha 本体
- **alpha**：cointegrated pair spread 的 z-score fade；
- `z > +entry`：short spread；
- `z < -entry`：long spread；
- spread 回到中枢附近就平。

### 7.2 admission / regime
- 只在同 cluster 内选 pair；
- 只做 `half-life` 落在可交易区间的 pair；
- 只在 `H < h_max` 时允许新开仓；
- 只保留最近窗口仍稳定、且近窗成本前 edge 没掉到 0 以下的 pair。

### 7.3 sizing / risk / execution
- 每对固定 gross notional，再用动态 hedge ratio 缩第二腿；
- 每个 ticker 的 active pair 数设硬上限；
- 每个 cluster 的总 gross 曝险设软上限；
- `5m` 默认先按 taker 成本测，如果 taker 不过，再评估 maker-first / passive exit 是否能翻正。

## 8. 风险与保留意见
- repo headline 结果来自 **1H + 近 46 天 OOS**，样本并不长；不能因为 Sharpe 漂亮就默认它在 `5m/15m` 也同样成立。
- 我这次 probe 已经显示：**全 universe 平均值很容易被成本吃掉**。这意味着真正决定成败的，不是“要不要做 pairs”，而是 **pair ranking / cluster admission / fee model / 退出方式**。
- `AVAX/LINK/XRP/BNB/SOL` 这类组合在 probe 里反复出现，可能是真 pocket，也可能只是最近窗口碰巧活跃；要防止过拟合到短样本。
- 如果未来下沉到 `3m/1m`，单靠 Hurst gate 大概率不够，得同步引入 **maker/taker 分层、queue priority、最小价差覆盖** 这些执行级约束。

## 9. 来源
### 主要来源
- **Author**: Jing-Lavinia
- **Year**: 2026
- **Title**: *Crypto Statistical Arbitrage — 1H Pairs Trading System*
- **Venue**: GitHub repository / README
- **DOI**: N/A
- **Readable URL**: `https://github.com/Jing-Lavinia/Pairs-Trading`
- **Repo URL**: `https://github.com/Jing-Lavinia/Pairs-Trading`
- **README raw URL**: `https://raw.githubusercontent.com/Jing-Lavinia/Pairs-Trading/main/README.md`

### 本地最小实验
- Probe script: `reports/artifacts/quant_digests/2026-04-23_hurstgate_pairs_probe.py`
- Pair summary: `reports/artifacts/quant_digests/hurstgate_pairs_probe_pair_summary_2026-04-23.csv`
- Aggregate summary: `reports/artifacts/quant_digests/hurstgate_pairs_probe_agg_2026-04-23.csv`
- Trade log: `reports/artifacts/quant_digests/hurstgate_pairs_probe_trades_2026-04-23.csv`

## 10. 下一步怎么测
下一步别再泛泛测“全市场 pairs 有没有 edge”，而是直接做这 5 个最小实验：
1. **cluster-first pair ranking**：先固定 liquid universe，在 `15m` 上比较“全 pair 搜索” vs “同簇 pair 搜索”的净收益、成交数、pair 稳定度。
2. **gate ablation**：对每个候选 pair 分别比较 `no gate / Hurst gate / volatility gate / Hurst+vol`，看谁真能改善净 bps/笔，而不是只减少交易。
3. **hub-cap 组合实验**：把 `max active pairs per ticker` 设为 `1 / 2 / 3`，测组合层面的 drawdown 与 cluster concentration。
4. **execution realism**：把 `15m` 正 pocket（优先 `LINK/AVAX`、`BNB/AVAX`、`SOL/AVAX`）拉进 maker/taker 双版本，先回答“edge 是策略本身，还是 taker 成本假设太重”。
5. **下沉频段前先做 pocket-only**：如果要测 `5m -> 3m`，不要全 universe 下沉，先只拿近窗稳定的 `2~4` 对做 OOS 滚动，看正 pocket 能不能保留，而不是让噪音把整个结论冲掉。
