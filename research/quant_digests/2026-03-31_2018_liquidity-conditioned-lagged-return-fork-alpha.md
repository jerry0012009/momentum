# 别把“前一日收益”只读成小币反转：这篇 2021 IRFA 论文对 desk 更该先测的是「liquidity-conditioned lagged-return fork」——液态币做 continuation，尾部币再谈 reversal

- 时间：2026-03-31 20:18 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/liquidity-conditioned/momentum/reversal/lagged-return/relative-value/binance/spot/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：2021 *International Review of Financial Analysis* 开放获取文章页 + Crossref/OpenAlex 元数据 + Binance Spot 公开 daily/15m 本地 transfer check

- 主题类型：raw alpha
- 基础 alpha：上一日（或上一段）收益率本身就是信号，但**交易方向取决于流动性分层**——低流动性更像反转，高流动性更像动量
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料是 **Adam Zaremba, Mehmet Huseyin Bilgin, Huaigang Long, Aleksander Mercik, Jan J. Szczygielski (2021)** 的论文 **_Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_**。

这篇东西对 desk 最有价值的地方，不是“crypto 有反转”这句大话，而是它把更细的一层说清了：

**同一个 lagged-return 信号，在不同流动性桶里，方向可能是反的。**

翻成人话：别把“昨天涨得多 / 跌得多”当成一个全市场统一信号。小而不流动的币更可能走短反转；大而可交易的币，反而更容易延续。

## 2. 核心结论
- 论文用 **2015–2021、3600+ coins** 的日频样本，指出一个很强的预测量：**last day’s return**。
- 在作者的大样本里，**前一日跌得多的币，下一日显著跑赢前一日涨得多的币**；也就是 headline 上更像短反转。
- 但作者同时强调：**这个效应强烈依赖 liquidity**。
- **最大、最可交易的那一小撮币，并不是反转，而更像 daily momentum。**
- 这意味着对我们 desk 来说，最值得复现的不是“统一做 loser rebound”，而是：
  1. **高流动性桶**先测 continuation；
  2. **低流动性桶**再单独测 reversal；
  3. 不要把两个桶混着做。

## 3. 为什么和当前项目有关
这篇论文补的是当前素材池里一条很实用的 raw alpha 主线：

- 它不是 breakout / funding / basis / pairs 的变体；
- 它是一个**可以独立下单的横截面 alpha**；
- 而且它天然带一个非常关键的 **desk 读法分叉器**：
  **同一个 return-sort，不同 liquidity bucket 要用不同方向。**

这和我们最近已经收的多条 XS / relative-value 线很搭：以后再看到 `winner-vs-loser`、`factor sleeve rotation`、`leader-follower` 之类东西，都不该默认全市场同号，而要先问一句：

**这个信号在高流动性桶和低流动性桶，方向一致吗？**

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对强弱 / liquidity-conditioned fork
- 基础 alpha：`lagged_return_rank`
- regime：`liquidity_rank`
- filter / veto：上币未满 90 天剔除；稳定币/锚定币剔除；极端点差/异常成交量剔除；事件/公告 blacklist
- risk / sizing / execution overlay：按 `ADV × inverse vol` 限仓；next-bar 执行；按 round-trip cost 分层；对 perp 版额外加 funding / basis 拥挤 veto

## 4. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha =“上一段收益率排序”本身；但不是固定做反转或固定做动量，而是先按 liquidity 分桶，再决定到底 follow 还是 fade。**

所以它不是 filter，不是 overlay，而是一条可以直接写成完整策略的 raw alpha，只不过要先做 **sign selection**。

## 5. 本地 transfer check：当前 Binance 可交易宇宙，先看到的是 liquid continuation，不是 tail reversal
我用 Binance Spot 公共数据做了两层很小的 transfer check。

### 5.1 Daily cross-section quick check
样本口径：
- **198 个 Binance USDT spot symbols**
- 时间：**2025-07-24 ~ 2026-03-30**
- 信号：前一日收益率横截面排序
- 流动性：`ADV20` 横截面分位

结果：
- **全样本 loser-minus-winner = -6.5 bps/day**
- **高流动性桶（top 10% ADV20）winner-minus-loser = +6.1 bps/day**
- **Top-20 当前最活跃样本 winner-minus-loser = +26.8 bps/day**

这说明至少在**当前 Binance 可交易、而且偏主流的现货宇宙**里，论文里那条“大样本小币短反转”并没有直接迁过来；
但**高流动性 continuation** 是能看到 transfer 痕迹的。

### 5.2 15m desk proxy check
再往 desk 频率靠一步：
- 宇宙：Binance 当前 **top-20 高流动性 USDT spot symbols**
- 频率：`15m`
- 信号：过去 **24h return rank**（96 根 15m）
- 观察窗口：最近 **1000 根 15m bar**

结果：
- **next 1h winner-minus-loser ≈ +1.0 bps**
- **next 4h winner-minus-loser ≈ +11.6 bps**
- 样本切片数：**888**

这组数还远远不是可上线回测，但已经足够说明：
**把“高流动性 lagged-return continuation”降采样到 15m，不像空想。**

## 6. 对 desk 更有价值的重读方式
所以这篇 paper 最值得 intake 的，不是 headline 上那句“crypto 短反转”，而是下面这句：

**lagged return 不是单号信号，而是 liquidity-conditioned fork。**

对我们当前 desk，更实用的先后顺序应该是：
1. **先做高流动性 momentum fork**：更贴近 Binance / perp 主战场，也更容易压住成本；
2. **再补低流动性 reversal fork**：但这需要更广的小币宇宙、更严格的上市年龄/成交门槛，否则容易把 listing noise 和垃圾流动性误判成 alpha；
3. 同一个信号不要跨桶硬合并。

## 7. 怎么把它落成完整策略
### 7.1 第一版：高流动性 continuation（优先）
- Universe：rolling `ADV20` 排名前 20%~30% 的 spot/perp 币
- Signal：`ret_24h_rank`
- Entry：每根 `15m` bar，对 top bucket 做 `long winners / short losers`
- Exit：持有 `4h`（16 bars）或 rank 回到中性区
- Sizing：`inverse vol × ADV cap`
- Cost：先跑 `2 / 6 / 10 bps` 三档 round-trip

### 7.2 第二版：低流动性 reversal（降级）
- Universe：扩到更广的小币池，但必须加 `listing_age >= 90d`
- Signal：同样用 `ret_24h_rank`
- Entry：只在低流动性桶做 `long losers / short winners`
- Exit：`1d` 或 `z/rank mean-revert` 就走
- 风险重点：点差、跳空、可交易性、下架/异常公告风险

## 8. 下一步怎么测
最小可执行实验直接写成下面这版：

1. **Universe**：Binance/Bybit/OKX 可做空的高流动性 perp，先取 20~40 个符号；
2. **Bar**：`15m`（主），`5m`（加速版）；
3. **Signal**：`ret_24h_rank = close_t / close_{t-96} - 1`；
4. **Gate**：只保留 `liquidity_rank >= 0.8` 的 continuation fork；
5. **Trade rule**：next-bar 做 `long top 20% / short bottom 20%`；
6. **Exit**：持有 `4h` / `8h`，或 rank 回到 `40%~60%` 中性带；
7. **Sizing**：`target_vol` + `ADV` 上限 + 单币权重 cap；
8. **Friction ladder**：round-trip `2 / 6 / 10 / 14 bps`；
9. **False-positive check**：剔除 funding/basis 极端拥挤时段，看 alpha 是否仍活着。

如果这版在 `15m` 上 after-cost 还能活，再下钻到 `5m`；
如果连 `15m` 都站不住，就别急着把论文里的“反转/动量”故事硬搬到实盘。

## 9. 风险与局限
- 论文的大样本包含大量**更小、更差、更不流动**的币；当前 Binance 宇宙不一定复现那条 reversal。  
- 我这次 transfer check 是**现货公开数据 proxy**，还没把 perp funding、借币、冲击成本完整放进去。  
- Top-liquidity continuation 目前只说明“方向值得测”，不代表已经有稳定净值。  
- 低流动性 reversal 很容易和 **listing drift / pump-and-dump / survivorship bias** 混在一起。

## 10. 这次最值得记住的一句话
**别再问 lagged return 到底是动量还是反转；先问它落在什么 liquidity bucket。**

## 11. 来源
1. **Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_. International Review of Financial Analysis, 78, 101908.**  
   DOI: `10.1016/j.irfa.2021.101908`  
   Readable URL: https://www.sciencedirect.com/science/article/pii/S1057521921002349?via%3Dihub  
   Repo URL: 无公开 repo（本次主材料为论文）
2. **Crossref metadata**: https://api.crossref.org/works/10.1016/j.irfa.2021.101908
3. **OpenAlex metadata / abstract**: https://api.openalex.org/works?search=Up%20or%20down%3F%20Short-term%20reversal%2C%20momentum%2C%20and%20liquidity%20effects%20in%20cryptocurrency%20markets
4. **Binance Spot API docs**: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints
5. 本地 artifacts：
   - `reports/artifacts/quant_digests/liquidity_regime_daily_reversal_momentum_20260331.csv`
   - `reports/artifacts/quant_digests/liquidity_conditioned_intraday_momentum_15m_20260331.csv`
