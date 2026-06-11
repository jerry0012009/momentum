# 别把 pairs 组合构建只当“去重”：这篇 2024 论文更值得先测的是「maximum-weight matching pair book + spread 均值回归」完整 raw alpha 骨架
- 时间：2026-03-27 17:48 UTC
- 类型：2024 arXiv 全文 + Binance Futures 公共 `15m` 本地 transfer check
- 主题类型：raw alpha
- 基础 alpha：**cointegration spread 的均值回归；matching 不是 alpha 本体，而是把同一套 pairs raw alpha 从“重仓少数公共腿”改造成“低重叠、低集中度”的 pair book 构造器。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/graph/matching/portfolio-construction/concentration/cost/binance/perpetual/15m/paper
- 证据类型：论文全文 + 本地公共数据最小迁移快检

> 先回答 base alpha：**这是 raw alpha，不是单纯 filter。** 真正赚钱的底层仍是 `cointegration spread mean reversion`；这篇 paper 的新意在于：不要再把 pair book 做成一堆共享同一条腿的“伪分散”组合，而是用 **maximum-weight matching** 选出 **不共享资产** 的一组 pairs，把同一条 raw alpha 做得更像一个可控、可扩容、可上 desk 的组合。

## 1. 这次看了什么
这次主看：

1. **Khizar Qureshi, Tauhid Zaman (2024)**, *Pairs Trading Using a Novel Graphical Matching Approach*, arXiv / Applications (stat.AP), Statistical Finance (q-fin.ST).  
   - DOI: `10.48550/arXiv.2403.07998`  
   - Readable URL: `https://arxiv.org/abs/2403.07998`  
   - HTML: `https://arxiv.org/html/2403.07998v1`
2. 论文文中提到的代码仓库：  
   - Repo URL: `https://github.com/kai-trading-bot/pair/`  
   - 备注：当前公开访问看起来已不可用/404，先把它当论文附带的 stale repo 线索，不作为主要证据。
3. 本地 transfer check：
   - 数据源：Binance Futures 公共 K 线 API（公开可得）
   - 标的：`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK, LTC, AVAX, TRX, DOT, BCH, ETC, APT, SUI` 对应 `USDT` perp
   - 频率：`15m`
   - 形成窗 / 交易窗：`60d formation + 10d trade`，滚动 `5` 个窗口
   - 产物：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/`

这篇 paper 的 headline 是：**pairs 组合若直接按 cointegration 强度排序，很容易反复押在同一批公共腿上，导致表面上 pair 数很多，实际上组合方差、换手和单腿风险都偏高。**

对我们 desk 来说，最值钱的不是“graph theory 很新”，而是：
- raw alpha 仍然清楚；
- entry/exit/sizing/risk/cost 都能拆出来；
- 而且它补的正是我们最近 pairs / stat-arb 素材池里相对少写的一层：**pair-book construction / capacity / concentration control**。

## 2. 核心结论
- **一句话核心结论：** 这篇东西最该落地的不是“图匹配”这个名词，而是 **`cointegration spread mean reversion + no-overlap pair book`** 这条完整 skeleton。
- **一句话它怎么证明：** 论文在 S&P 500 2017-2023 样本里显示，matching 版 pair book 相比“直接拿 top cointegrated pairs”基线，**gross Sharpe `1.23` vs `0.48`、net cumulative return 约 `+65%` vs `-26%`，且 turnover 更低、单股票集中度更低。**

但 desk 化之后更重要的诚实读法是：
1. **matching 修的是“组合构造错误”，不是凭空创造新的 spread alpha；**
2. 如果候选图里本来混入很多弱 pair，硬做“全覆盖不重叠”，可能会把一些很强但共享核心腿的 pair 拆掉；
3. 所以它更像一个 **pairs raw alpha 的 portfolio-construction layer**，而不是一个脱离 spread 自身质量的万能增强器。

## 3. 3 个关键数据点
1. **论文原始结果很硬。** 在作者的 S&P 500 日频回测里：
   - matching 策略 gross Sharpe **`1.23`**，基线只有 **`0.48`**；
   - net cumulative return 约 **`+64.7% / +66.3%`**，基线约 **`-26.2% / -13.4%`**；
   - matching 组合 net max drawdown 约 **`-8.0%`**，显著小于市场 **`-19.5%`**。
2. **我在 Binance `15m` 的滚动最小迁移快检里，matching 的“结构修正”是明显成立的。** 最近 `5` 个滚动窗口中：
   - 平均组合集中度：**`1.0` vs `3.6`**（matching 永远每个资产只出现一次）；
   - 平均覆盖资产数：**`16.0` vs `9.4`**；
   - 平均 pair turnover changes：**`22.85` vs `28.00`**。  
   也就是说，**它确实把 pair book 从“公共腿堆叠”改成了“真分散”。**
3. **但 short-cycle 迁移目前还没过 first verdict。** 在同一批 `15m` 简化 z-score 测试下：
   - matching gross cumret **`+3.4%`**，baseline **`+9.1%`**；
   - 考虑简化成本后，matching net cumret **`-6.3%`**，baseline **`-3.6%`**；
   - matching median pair half-life 约 **`169` bars**，baseline 约 **`129` bars**。  
   这说明：**matching 把 book 结构修对了，但在我们这版 15m proxy 里，还没把“更慢的 spread + 更低重叠”转成净 alpha 优势。**

## 4. 为什么和当前短周期 desk 有关
### 4.1 它服务的是哪类 raw alpha
- 分类：**pairs / stat-arb / relative-value / mean-reversion raw alpha**
- 不是：
  - 纯 filter
  - 纯 regime
  - 纯组合优化而没有交易规则

### 4.2 它补的是素材池哪块缺口
最近几篇 pairs / stat-arb digest 已经补了：
- spread 定义
- anti-persistence / threshold gate
- dynamic sizing
- PCA residual / factor residual

但还缺一类很实际的问题：
> **如果很多最强 pair 都共享同一条主腿，book 到底该怎么组？**

这篇 paper 的价值就在这里：
- 它不是在讲一个抽象风控故事；
- 它是在讲 **raw alpha 组合化以后为什么会变坏**；
- 以及如何用一个明确可复现的算法，把这件事做成工程组件。

如果后面 desk 继续扩 pairs / stat-arb 素材池，这一层迟早都要补。

## 5. desk 化后的最小策略草图
## 5.1 形成窗与 pair selection
先做最小可复现版本：

- 频率：`15m`
- 宇宙：流动性最好的 `12~20` 个 `USDT` perpetual
- formation：滚动 `45~60d`
- 对每个 pair 跑：
  - `log(P_j) = μ + β log(P_i) + ε`
  - 对残差 `ε` 做单 lag `ADF`
- 图构造：
  - 节点 = 资产
  - 边 = pair
  - 边权 = `-ADF t-stat`（越大表示越强均值回归候选）
- 选边：
  - **matching 版**：maximum-weight matching
  - **baseline 对照**：按 `p-value` 直接取 top pairs

### 5.2 entry / exit
paper 给了两个触发器：
- `z-score`：标准化残差超过阈值就开仓
- `q-score`：用分位数而不是标准差做稳健归一化，并按离群程度整数分档加权

对 short-cycle desk，建议先这样落地：
- **entry**：`|z| >= 1.0 ~ 1.5` 或 `|q| >= 1` 开仓
- **direction**：spread 高于均衡就 short spread，低于均衡就 long spread
- **exit**：
  - `z` / `q` 回到 `0` 附近平仓；
  - 或设置 `max holding bars = 16 / 24 / 32`；
  - 或加 time-stop，避免慢速残差拖死资金占用

### 5.3 sizing
- pair 内部按 `β` 做 dollar hedge；
- pair 之间先 equal-risk / inverse-vol；
- matching 版本天然可以把名义权重摊得更匀，因为不会反复压在同一条主腿；
- 若改用 `q-score`，可以把极端离群 pair 的权重向上分档，但必须设单 pair cap。

### 5.4 risk / veto
必须加：
1. **half-life 上限。** 过慢的 pair 不适合 `5m/15m` desk。先卡 `half-life <= 96~192 bars`。  
2. **波动/成交筛选。** 低流动性 alt pair 很容易让 ADF 看起来“很美”。  
3. **事件 veto。** 上线前要把币种大级别公告、上币/下币、极端 funding、异常 basis 单列剔除。  
4. **book concentration 监控。** 即便用 matching，也要看 sector / beta exposure 是否实际上又被“同类资产”重合。  
5. **成本压力测试。** 这条线天生怕换手，必须分开跑 maker / taker / mixed execution。

### 5.5 cost
本轮 quick check 先用的是**很粗的简化 friction proxy**，不能当最终成本结论。
正式版至少要跑：
- maker-dominant：`2 / 3 / 4 bps` round-trip
- mixed：`4 / 6 / 8 bps`
- taker-heavy：`8 / 10 / 12 bps`

如果 matching 只是在 gross 上修风险、但净后仍输给 overlap baseline，就说明：
- 要么 pair admission 太松；
- 要么 holding 太短、没等到更慢的 spread 回归；
- 要么 short-cycle desk 根本不该强求 full matching，而该做 **partial matching / capped overlap**。

## 6. 本地 transfer check 读法（要诚实）
我这次快检只想回答一个问题：
> **把 paper 的 matching pair-book 思路搬到 crypto `15m`，会不会立刻变成更好的短周期净策略？**

当前答案是：**不会立刻。**

我拿 Binance Futures 公共 `15m` 数据，用 `60d formation + 10d trade` 滚动 `5` 个窗口，做了一个极简版 z-score spread 回测。结果显示：
- matching 的确把集中度、覆盖度、turnover 结构修好了；
- 但在这个版本里，**baseline 选到的 pair 更强、更快，哪怕更重叠，短窗 gross 反而更高；**
- 成本后两边都没活下来，只是 matching 更像“慢而干净”，baseline 更像“强但挤”。

所以这篇的正确定位不是：
- “已经证明 15m 可直接上线”；
而是：
- **证明了 pairs alpha 的 book construction 是一层真实存在、而且可复现的 engineering lever。**

## 7. 下一步怎么测
按优先级继续往下做：

1. **先把 z-score 版本升级成 paper 更像的 `q-score + integer sizing`。**  
   现在的 proxy 太粗，容易把慢 spread 与 outlier-sensitive std 归一化混在一起。
2. **不要对全宇宙直接 full matching。**  
   先用更强的 admission layer 缩图：
   - `ADF p-value`
   - half-life
   - residual vol
   - 流动性 / funding / basis 稳定性  
   然后再在候选图上做 matching。
3. **做 partial-overlap / capped-degree 对照。**  
   不是只能二选一：
   - baseline = 任意重叠
   - full matching = 完全不重叠  
   中间还可以测：`max degree <= 2` 或 `same leader leg capped at 2`。
4. **把 holding period 拉开再看。**  
   当前 matching 选出的 pair median half-life 更长，说明它可能不该硬塞进纯 `15m` 快周转；要补跑：
   - `15m` 入场 + `4h/8h/1d` 持有
   - `5m` 触发但 `1h+` 持有
5. **做 sector / community-aware matching。**  
   对 crypto 来说，“不共享资产”还不够，最好再加：
   - L1/L2/meme/DeFi 分组
   - funding state / beta bucket
   - same-cluster 限额  
   避免匹配器为了去重，硬把风格完全不对的 pair 拼进去。
6. **正式执行版一定要比较三套 book：**  
   - top-`K` overlap baseline  
   - full matching  
   - capped-overlap hybrid  
   然后统一看 `gross / net / turnover / concentration / exposure / borrow-capacity proxy`。

> **最该先测的正式版本：** `Binance perp 15m`, `60d formation`, `ADF + half-life admission`, 在候选图上比较 `full matching` 与 `max-degree<=2 hybrid`，交易层用 `q-score` 而不是简化 z-score，holding 至少拆 `1h / 4h / 8h` 三档。若 hybrid 明显优于 full matching，就把这篇 paper 吸收成 **pairs book governance module**，而不是把“完全不重叠”当教条。

## 8. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-27_1748_graph-matching-pairbook-meanreversion.md`
- quick check 产物目录：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/`
- 窗口结果：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/window_metrics.csv`
- 汇总：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/summary.json`
- 最新一期 matching pair 列表：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/latest_matching_pairs.csv`
- 最新一期 baseline pair 列表：`reports/artifacts/quant_digests/graph_matching_pairs_20260327/latest_baseline_pairs.csv`

## Sources
1. **Qureshi, K., & Zaman, T. (2024). _Pairs Trading Using a Novel Graphical Matching Approach_. arXiv.**  
   - Venue: arXiv / stat.AP / q-fin.ST  
   - DOI: `10.48550/arXiv.2403.07998`  
   - DOI URL: `https://doi.org/10.48550/arXiv.2403.07998`  
   - Readable URL: `https://arxiv.org/abs/2403.07998`  
   - HTML URL: `https://arxiv.org/html/2403.07998v1`
2. **Binance Futures Public Klines API**（本地最小迁移快检数据源）  
   - API docs: `https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data`  
   - 示例：`https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`
3. **Paper-cited repo clue**  
   - `https://github.com/kai-trading-bot/pair/`（当前公开访问疑似失效，待后续核实是否迁移/私有化）
