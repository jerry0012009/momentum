# 别把这份 2026 stat-arb repo 只读成“图聚类作业”：对 short-cycle desk，更该先保留的是「去市场模态后的同簇偏离 → 向 cluster composite 回归」这条 raw alpha

- 时间：2026-04-17 14:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `stat_arb/reporting/FINAL_REPORT.md` + `stat_arb/pca/market_mode.py` + `stat_arb/graphs/knn_graph.py` + `stat_arb/clustering/sponge.py` + `stat_arb/signals/cluster_deviation.py` + `stat_arb/backtest/walk_forward.py`）+ Binance USDⓈ-M `15m` portability probe（9 majors，20 folds）
- 主题类型：raw alpha
- 基础 alpha：**先用 PCA 去掉整市场共振，再把相关性相近的币分到同簇；如果某个币相对自己簇的 composite return 明显跑过头/落后，就赌它向簇均值回归，而不是赌整市场方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / stat-arb / relative-value / cluster-deviation / pca / market-mode-removal / signed-graph / sponge / mean-reversion / cross-sectional / binance-perpetual / 15m / 5m / repo / public-data / cost / risk
- 证据类型：GitHub repo 实现 + repo 自带 walk-forward 报告 + 本地 public-data portability probe

## 1. 这次看了什么
主材料是一个今年的新仓：

- **Author / Maintainer：** `Aroesler1`
- **Year：** 2026 创建，2026-04 仍有更新
- **Title：** *Crypto-Stat-Arb*
- **Venue：** GitHub repo（含数据清洗、PCA 去市场模态、signed k-NN graph、SPONGE/BNC 聚类、walk-forward backtest、成本敏感性分析）
- **DOI：** N/A
- **Readable URL：** <https://github.com/Aroesler1/Crypto-Stat-Arb>
- **Repo URL：** <https://github.com/Aroesler1/Crypto-Stat-Arb>

先把一句话讲清楚：

> **这份仓最值钱的地方，不是“用了 SPONGE / signed graph 很花哨”，而是它把一条相当清楚的 raw alpha 写成了完整壳：`去市场模态后的 cluster-relative 偏离，随后更容易向 cluster composite 回归。`**

也就是说，这轮该 intake 的不是“聚类技术”本身，而是：
- 先把全市场一起涨跌的那一层拿掉；
- 再在相似币组成的小簇里找“谁相对同伴跑偏了”；
- 最后做 **underperformer long / outperformer short** 的相对价值均值回复。

## 2. 核心结论
### 2.1 一句话结论

> **这是一条可以独立成型的 stat-arb raw alpha：`market-mode removal + cluster admission + deviation fade`。repo 的图聚类、beta neutral、turnover cap，本质上都是在帮这条 alpha 从“想法”变成“可回测策略”。**

### 2.2 一句话它是怎么证明的

> **repo 自带的 daily low-cap walk-forward OOS（2024-05 ~ 2025-05）里，最佳配置 `Cluster Deviation + SPONGE k=3` gross Sharpe 到 `3.27`、break-even cost 到 `54.2 bps`；我又把核心逻辑迁移到 Binance USDⓈ-M `15m` 9 个 liquid majors 上做 20 个 rolling folds，结果显示 raw signal 还活着，但 taker 成本几乎把它全吃光。**

### 2.3 为什么值得进素材池
- 它是 **raw alpha**，不是纯 filter：基础赌注就是“相对偏离会回归”；
- 它给的是 **完整策略壳**：entry / exit / neutralization / leverage / turnover / cost sensitivity 都写出来了；
- 它补的是最近 digest 相对少的一类：**cluster-level relative value/stat-arb**，不是又一篇 funding 或单资产 shock fade。

## 3. repo 里最值钱的 3 层结构
### 3.1 第一层：先去掉 market mode，只留下“相对跑偏”
`stat_arb/pca/market_mode.py` 里先对 cross-section returns 做 PCA，只拿第一主成分当“市场模态”，再把它从每个币的收益里减掉。

翻成人话：

> **如果今天全市场一起涨，那不是你要的 alpha；真正要的是“在大家一起涨这件事之外，哪个币相对同簇多涨了/少涨了”。**

这一步很关键，因为不去 market mode，后面的“均值回复”很容易只是把市场 beta 当成 alpha。

### 3.2 第二层：signed k-NN graph + SPONGE，不是噱头，而是 pair admission 的升级版
repo 没抱死固定 pairs，而是：
- 用 residual return correlation 建图；
- 保留 k 近邻边；
- 用 signed graph clustering（SPONGE / BNC / Signed Spectral）分簇。

我的读法：

> **这比“先手搓 1 对 BTC/ETH 再看 spread”更像 cluster-first admission。它在做的是：先找一小群行为相近的币，再在群内做 relative value。**

所以它不是 pair trade 的换皮，而是 **pair admission 的更泛化版本**。

### 3.3 第三层：Cluster Deviation 才是最该保留的主信号
最值得抄的不是简单 z-score pair，而是 `ClusterDeviationStrategy`：
- 对每个 cluster 先算 composite return；
- 再算单币相对 composite 的 deviation；
- 对 deviation 做 rolling sum + rolling z-score；
- **负 z-score 做多、正 z-score 做空**；
- 再做 dollar neutral / leverage cap / turnover cap。

这条信号对 short-cycle desk 的翻译很直白：

> **不是问“这币自己该涨还是该跌”，而是问“这币相对它该一起行动的那一簇，是不是跑偏了”。**

## 4. repo 自带证据，我最关心哪几个数
`stat_arb/reporting/FINAL_REPORT.md` 里最值得记住的是：
- **最佳配置：** `Strategy 2 (Cluster Deviation) + SPONGE k=3`
- **Gross Sharpe：** `3.27`
- **25 bps 成本下 Net Sharpe：** `1.76`
- **25 bps 年化收益：** `29.2%`
- **50 bps 成本下 Net Sharpe：** 仍约 `0.24`
- **Break-even cost：** `54.2 bps`
- **ETH beta / PC1 beta：** 约 `0.02 / 0.00`

这说明作者不是只给“alpha intuition”，而是已经把：
- factor neutral
- turnover
- cost ladder
- rolling OOS
都接进去了。

## 5. 我补的 Binance `15m` portability probe
### 5.1 数据源、公开性、实验口径
- **数据源：** Binance USDⓈ-M 公共 `fapi/v1/klines`
- **公开性：** 公开可得
- **更新频率：** `15m`
- **标的：** `BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX/LINK`
- **样本：** `2026-02-15 ~ 2026-04-16` 有效 OOS 段，`20` 个 rolling folds
- **训练 / 测试：** `14d` train + `3d` test，滚动重训
- **实现：** 仍保留 repo 的核心骨架：`PCA 去 market mode -> residual corr kNN graph -> SPONGE 3 clusters -> cluster deviation z-score -> gross 1.5x -> turnover cap`
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-17_clusterdeviation_binance15m_probe.py`
  - `reports/artifacts/quant_digests/2026-04-17_clusterdeviation_binance15m_probe_summary.json`
  - `reports/artifacts/quant_digests/2026-04-17_clusterdeviation_binance15m_probe_cost_sensitivity.csv`

### 5.2 关键数字
先说 raw signal：
- **gross ann return：** 约 `26.10%`
- **gross ann vol：** 约 `11.24%`
- **gross Sharpe：** 约 `2.32`
- **gross max drawdown：** 约 `-4.19%`

但短周期 desk 真正该盯的是成本后：
- **avg turnover / bar：** 约 `19.41%`
- **active bar ratio：** 约 `32.27%`
- **break-even cost：** 只有约 `0.49 bps`
- **2 bps 成本：** ann return 约 `-1.15%`，Sharpe 约 `-1.00`
- **4 bps 成本：** ann return 约 `-2.56%`，Sharpe 约 `-2.21`
- **8 bps 成本：** ann return 约 `-5.40%`

我的结论很明确：

> **在 Binance majors 的 `15m` taker 口径下，这条 alpha 不是“没信号”，而是“signal gross 活着，但周转太快，费后几乎立刻死”。**

## 6. 对我们 desk 的正确读法
### 6.1 为什么这轮仍归到 `raw alpha`
因为 base alpha 可以一句话说清：

> **同簇相对偏离会回归。**

PCA、图聚类、neutralization、turnover cap 都是把 raw alpha 包装成更可交易的策略层，而不是 alpha 本体。

### 6.2 和当前 `1m / 3m / 5m / 15m` 的关系
- **15m taker baseline：** 当前 first verdict 偏负，不建议直接照抄；
- **5m / 15m maker-first 或低摩擦内部撮合：** 还有继续测的价值；
- **1m / 3m：** 若周转更高，必须先解决 execution，不然大概率更快死于成本；
- **更合适的方向：** 把它当 **shared relative-value engine**，服务 cluster 内择时 / veto / size tilt，而不是裸全时段高频轮转。

### 6.3 它服务于哪些 raw alpha 家族
这条思路最直接服务于：
1. **stat-arb / relative value**：cluster deviation fade 本身就是 alpha；
2. **pairs 的 admission 升级版**：先从 pair 扩成 cluster，再做相对偏离；
3. **cross-sectional mean reversion**：不是简单 loser-winner，而是先做结构化分组再反打。

## 7. 策略拆解（必填）
- **方向属性：** 横截面 / 相对价值 / 均值回复
- **基础 alpha：** 去市场模态后的同簇偏离向 cluster composite 回归
- **regime：** 高同步单边 trend、cluster 结构不稳定、市场相关性重排时，易失效
- **filter / veto：** 只做高 cohesion cluster、只做极端 z-score、避开高 funding / 高 event bar、只在 cluster 稳定窗口内开仓
- **risk / sizing / execution overlay：** dollar neutral、PC1/ETH neutral、gross leverage cap、turnover cap、maker-first / passive rebalance、cluster concentration cap

## 8. 下一步怎么测
这轮已经给出 first verdict，下一步别再测“同一版参数细抠”，而该做 3 个更决定性的实验：

1. **降周转版本**
   - 把 cluster 重训频率从 `3d` 改为 `7d` 或 `14d`
   - 只保留 `|z|` 最大的 top-1 / top-2 偏离腿
   - 看 break-even cost 能不能从 `<1 bps` 抬到至少 `4~6 bps`

2. **执行层改写版本**
   - 不是 bar close taker，而是 `maker-first / passive rebalance / partial fill`
   - 重点看：gross alpha 留存多少、turnover 能降多少、实际 fill 风险是否把 edge 再吃掉

3. **cluster stability gate**
   - 只在训练窗内 cluster cohesion 为正、且 noisy cluster 不占主导时开仓
   - 我这轮 20 folds 里，不少 cluster cohesion 仍偏负，这很像 admission 质量问题，而不是 signal 定义本身错了

最该先看两个指标：
- **break-even cost 能否提升到真实可交易区间**
- **trade count / active bar ratio 降下来后，gross Sharpe 还能保留多少**

## 9. 风险与保留意见
- 这条 alpha 在 repo 里主要跑的是 **daily low-cap**，我这次压到 `15m` liquid majors，本来就属于高难度迁移；
- 当前 probe 还不是完整实盘执行仿真，没有盘口冲击和挂单成交约束；
- cluster method 的亮点很大，但 short-cycle 下真正的瓶颈可能不是 clustering，而是 **cost / turnover / execution**；
- 所以对 desk 来说，这轮最合理的口径不是“可直接上线”，而是：
  - **值得保留为 raw alpha 素材池**
  - **但短周期 taker 直译版先判负**

## 10. 来源
- Aroesler1. (2026). *Crypto-Stat-Arb*. GitHub.
  - Readable URL: <https://github.com/Aroesler1/Crypto-Stat-Arb>
  - Repo URL: <https://github.com/Aroesler1/Crypto-Stat-Arb>
  - Key files: <https://raw.githubusercontent.com/Aroesler1/Crypto-Stat-Arb/main/stat_arb/reporting/FINAL_REPORT.md>, <https://raw.githubusercontent.com/Aroesler1/Crypto-Stat-Arb/main/stat_arb/pca/market_mode.py>, <https://raw.githubusercontent.com/Aroesler1/Crypto-Stat-Arb/main/stat_arb/graphs/knn_graph.py>, <https://raw.githubusercontent.com/Aroesler1/Crypto-Stat-Arb/main/stat_arb/clustering/sponge.py>, <https://raw.githubusercontent.com/Aroesler1/Crypto-Stat-Arb/main/stat_arb/signals/cluster_deviation.py>
- Binance USDⓈ-M Futures Market Data API.
  - Klines doc: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
