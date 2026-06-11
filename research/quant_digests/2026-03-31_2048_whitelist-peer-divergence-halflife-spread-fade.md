# 别把 Hyperliquid peer-pairs 继续写成“泛 pairs bot”：这份 2024/2025 GitHub repo 更该先测的是「whitelist peer-divergence × half-life-gated spread fade」，但要先修 96-bar 口径

- 时间：2026-03-31 20:48 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/peer-cluster/whitelist/cointegration/spread-zscore/half-life/hyperliquid/binance/15m/5m/1m/3m/repo/public-data/cost/execution
- 证据类型：2024/2025 GitHub 仓库 `README.md` + `docs/SERVER_ASSET_WHITELIST.md` + `docs/SERVER_POSITION_MANAGEMENT.md` + `docs/SERVER_ORDER_EXECUTION.md` + `server/src/utils/assetMappings.ts` + `server/src/analysis/correlationAnalyzer.ts` + `server/src/strategies/pairsCorrelationStrategy.ts` source audit + Binance USDⓈ-M Perpetual 公开 `15m` proxy quick check

- 主题类型：raw alpha
- 基础 alpha：同一白名单生态/风格簇里的高相关资产，若 `spread = price_B - beta * price_A` 偏离其均值超过阈值，就做 **long laggard / short leader** 的配对回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是论文，而是一份仍在更新的 Hyperliquid 配对交易仓库：**Andrew Wilkinson / Privateer Capital（GitHub repo，2024 创建，2025 仍有 push）**。

它最值得 desk intake 的地方，不是“又一个 pairs trading repo”，而是它把问题收窄成了更可执行的一种版本：

**先手工限定一个“同生态/同风格”的白名单，再只在这些 peer 里找高相关、短 half-life 的 spread 偏离。**

翻成人话：
不是全市场瞎搜 cointegration，而是先承认很多可交易 alpha 根本不是“任意两币之间”的，而是 **同类币之间的相对错位**。

仓库白名单里包含的就是这种思路：`ETH / ARB / OP / STRK / CELO / MNT / AAVE / ENA / LINK / UNI / MKR / CRV / PENDLE ...`。这比“全市场 pair search”更贴近 desk 真正会下手的短周期 relative-value lane。

## 2. 核心结论
从 repo 和代码本身，能直接提炼出 5 个关键点：

1. **base alpha 很清楚**：
   - 先估 `beta`；
   - 再算 `spread = price_B - beta * price_A`；
   - 计算 spread z-score；
   - 当 `|z| > 2.5` 时，做 **rich leg short / cheap leg long**。

2. **它不是纯 pairs 筛选器，而是完整执行骨架**：
   - pair 质量：相关系数阈值 `0.95`；
   - mean reversion 过滤：`half-life` 必须落在 `6~15` 个 bar；
   - sizing：双腿等美元；
   - asset overlap protection：一个资产不能同时出现在多个打开的 pair 里；
   - execution：IOC → 更宽 IOC → GTC 三层回退。

3. **它的价值不在“找到很多 pair”，而在“只做很少但更像真同类的 pair”**。
   这和 desk 当前需要的素材池是对得上的：
   不是再堆一个抽象 stat-arb 名词，而是补一条能直接落到 `5m / 15m` perp 的 raw alpha lane。

4. **repo 自带一个很重要的实现层提醒**：
   `pairsCorrelationStrategy.ts` 里写着：
   `minDataPoints: 96 // 1 week of 15-minute snapshots`

   但 96 根 `15m` bar 实际上只有 **24 小时**，不是 1 周。
   这不是注释小错，而是会直接改变 pair discovery、half-life 估计、信号密度的口径问题。

5. **所以这份材料最该先测的，不是“repo 回测收益率”，而是：**
   **同一白名单 peer-cluster 内，short half-life spread fade 到底是不是一条能稳定产出、且不被成本秒杀的 raw alpha。**

## 3. 为什么和当前项目有关
它和我们这轮 intake 目标高度匹配：

- 它是 **raw alpha**，不是纯 filter；
- 它不是围着 breakout/retest 内循环，而是补 **pairs / stat-arb / relative-value** 的一条明确主线；
- 它能直接拆成 `entry / exit / sizing / risk / cost`；
- 它默认就适合 desk 常用的 `5m / 15m`，往 `3m / 1m` 压缩也有自然路径；
- 它用的输入数据是 **公开可得价格数据**，复现门槛低。

更关键的是，它不是那种“paper headline 很大，但落地只剩风格解释”的材料。这里的 base alpha 本身就能独立下单。

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：`peer_spread_zscore`
- regime：`same-ecosystem whitelist + short half-life`
- filter / veto：`corr >= 0.95`、`6 <= half_life <= 15`、资产不重叠、低流动性腿剔除、事件币剔除
- risk / sizing / execution overlay：双腿等美元；单 pair 使用可用保证金固定比例；max open pairs；round-trip 成本分层；单腿成交失败必须 rollback

## 4. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 同一白名单 peer pair 的 spread z-score 偏离；当同类资产之间的相对价格错位拉大到极端，就做回归。**

所以它不是 filter，不是 overlay，而是一条可以独立写成完整策略的 raw alpha。

## 5. Repo audit：真正值得 desk 拿走的不是“pairs”两个字，而是这套白名单 + half-life 读法
### 5.1 Pair discovery 不是任意两币，而是白名单 peer cluster
`assetMappings.ts` 和白名单文档给出的宇宙，本质上是一组“同类风险资产”：
- L1 / infra：`ETH / CELO / MNT ...`
- L2：`ARB / OP / STRK / BLAST`
- DeFi / rates / beta proxies：`AAVE / ENA / LINK / UNI / MKR / CRV / PENDLE / GMX / LDO`

这个设计的好处是：
**先用主观先验把 pair search 限到“本来就可能一起动”的东西，再让统计量只负责判断有没有暂时错位。**

这比全市场 cointegration 暴力扫描更像 desk 真会采用的做法。

### 5.2 代码里给出的 entry 骨架非常直接
`pairsCorrelationStrategy.ts` 的核心逻辑可以翻成：

1. 用 rolling window 估计 pair 的相关性、hedge ratio、spread 均值/波动、half-life；
2. 只保留：
   - `corr >= 0.95`
   - `6 <= half_life <= 15`
3. 实时算当前 spread z-score；
4. 若 `z > 2.5`：认为 `B` 相对 `A` 偏贵，做 **long A / short B**；
5. 若 `z < -2.5`：认为 `B` 相对 `A` 偏便宜，做 **short A / long B**。

这套定义足够清楚，完全能独立复现。

### 5.3 execution / sizing 倒是比很多 toy repo 诚实
仓库不是停在“信号生成”那一步，而是把很多真实交易会踩的坑也写出来了：

- 默认 `tradeSizePercent = 0.5`，即用 **50% 可用保证金** 开一组 pair；
- `maxPositions = 4`；
- 双腿按美元尽量配平，允许误差压到 **5% 以下**；
- 最小单腿订单价值 **$10**；
- 执行失败时，采用 **pair integrity rollback**：如果一条腿成了、另一条腿没成，第一条腿要立刻平掉；
- 下单回退：**IOC 0.5% 滑点 → IOC 2% → GTC 5%**。

这意味着它不是 paper-only idea，而是真在往“能活着执行”靠。

### 5.4 但 lookback 口径现在是 repo 最大的不确定项
最值钱的 audit 结论反而是一个很朴素的问题：

`96` 根 `15m` bar 被写成了 “1 week”。

实际不是。

这会带来三个直接后果：
1. pair discovery 可能变得过短，容易把短暂共同波动错判成稳定关系；
2. half-life 估计会更抖；
3. signal density 可能被放大或扭曲。

**所以这条 alpha 要不要进研究池，不该先问“repo 有没有 dashboard”，而该先问 `96 vs 672` 的信号结构差多少。**

## 6. Binance 15m proxy quick check：alpha 不是假的，但口径极敏感
我用 Binance USDⓈ-M Perpetual 公开 `15m` K 线，在 repo 白名单可映射的 12 个币上做了最小快检。

样本口径：
- 宇宙：`ETH / ARB / OP / STRK / CELO / AAVE / ENA / LINK / UNI / MKR / CRV / PENDLE`
- 频率：`15m`
- 当前窗口对比：`96 bars` vs `672 bars`
- rolling quick check：最近 `1500` 根 `15m` bar 里，对每个 pair 做 `672-bar` 估计

### 6.1 先看最关键的复现问题：`96 bars` 和 `672 bars` 根本不是一回事
在同一时点上：
- 若按 repo 代码里的 **96-bar** 口径（实际上只有 24h），**当前 0 个 pair** 同时满足 `corr >= 0.95` 且 `6 <= half-life <= 15`；
- 若按更像“1 周”的 **672-bar** 口径，当前能留下 **3 个 pair**：
  - `ARB/CRV`
  - `ARB/LINK`
  - `LINK/CRV`

这已经足够说明：
**这条 alpha 的第一优先级不是调 z-score，而是先把 lookback 定义说清楚。**

### 6.2 当前这 3 个可交易候选，并没有出现 live 极端错位
在 `672-bar` 口径下，当前最强的 z-score 也只有：
- `LINK/CRV`: `|z| ≈ 1.09`
- `ARB/CRV`: `|z| ≈ 0.66`
- `ARB/LINK`: `|z| ≈ 0.52`

也就是说：
**现在这个时点，pair gate 有，但 entry 没到。**

这是好事——它说明这不是那种“随时都在乱发信号”的伪均值回复框架。

### 6.3 历史滚动里，`ARB/CRV` 是这批 peer pair 里最像样的一组
对最近 `829` 个 rolling `672-bar` 窗口（约 8.6 天的判定序列）统计：

- `ARB/CRV` 有 **298** 个窗口满足 gate，占比 **35.9%**；
- 其中 `|z| >= 2.5` 的原始信号窗口有 **34** 个，占全部窗口约 **4.1%**；
- 如果把相邻簇状信号去重成独立 episode，只剩 **5 次**，说明它不是高频狂刷型，而是 **少量 cluster shock** 型机会。

这类 alpha 的味道很明确：
不是“每小时都有新单”，而是 **平时等，冲击来时抓 relative-value 回归**。

### 6.4 但它更像“先压缩一截”，不一定在 15m 内完整回到均值
对这 5 个去重后的 `ARB/CRV` signal episode，再看未来 `10` 根 bar（约 2.5h）：

- **80%** 的 episode 在 10 bars 内至少压回 **0.5σ**；
- **60%** 的 episode 在 10 bars 内压回至少 **1.0σ**；
- 但只有 **20%** 的 episode 能在 `15` 根 bar 内真正回到 `|z| <= 0.5` 或翻过零轴。

翻成人话：
**它不是那种“一触发马上 V 回”的 ultra-fast pair trade。更像先吃一段 spread 压缩，再决定要不要继续等 full reversion。**

这对 desk 很关键，因为它直接决定：
- exit 应不应该等到回均值；
- 还是应该先吃 `0.75σ ~ 1.25σ` 的第一段压缩。

## 7. 对 desk 更有价值的重读方式
所以这份 repo 最值得 intake 的，不是“有个 pairs engine”，而是下面这条更窄、更实盘的读法：

**别做全市场任意 pair mean reversion；先做 whitelist peer-cluster divergence。**

也就是：
- `ARB/OP/STRK` 这种 L2 同类组；
- `AAVE/UNI/MKR/CRV/LINK/PENDLE` 这种 DeFi beta 组；
- 必要时再加 `ETH` 这类大 beta anchor。

然后只在这些组里做：
- 高相关；
- 短 half-life；
- 极端 z-score；
- 非重叠资产；
- 成本后还能活。

这比“广撒网 pairs”更贴近短周期 desk，也更利于之后做实盘组件拆解。

## 8. 怎么把它落成完整策略
### 8.1 第一版：15m peer-divergence baseline
- Universe：同 venue 可做空 perp，按人工白名单分 peer buckets
- Discovery window：
  - `15m` 主版：**672 bars**
  - `5m` 加速版：**2016 bars**
- Pair gate：
  - `corr >= 0.95`
  - `6 <= half_life <= 15`
  - 过去 7 天成交额 / OI / spread 达标
- Entry：`|z| >= 2.5` 时 next-bar 进场，做 `long laggard / short leader`
- Exit：
  - 主出场：`|z| <= 0.5`
  - 快速止盈版：先落袋第一段压缩，`abs(z_entry) - abs(z_now) >= 1.0`
  - 时间止损：`1.5 × half_life` 或 `12 bars` 取较大
- Hard stop：`|z|` 扩到 `4.0` 或 pair gate 失效（相关性/half-life 坏掉）

### 8.2 Sizing / risk / cost
- Sizing：双腿等美元；单 pair 先别照 repo 直接上 `50%` 保证金，desk baseline 改成 **10%~15% available margin/pair** 更合理
- Overlap：同一资产只允许出现在 1 个活跃 pair 中
- Max positions：先限 **2~3 个 pair**
- Cost ladder：round-trip `2 / 6 / 10 / 14 bps`
- Execution：
  - 先做 taker-only 模拟；
  - 再试 maker-one-leg / taker-one-leg；
  - 任何单腿成交失败必须 rollback

## 9. 下一步怎么测
最小实验建议直接做这 5 件事：

1. **先复现 repo 真实口径差异**：同样的白名单、同样的阈值，比较 `96 vs 672`（15m）和 `288 vs 2016`（5m）的 pair 数、信号数、after-cost PnL。  
2. **做 bucket 内 pair search，而不是全宇宙 search**：先限定 `L2`、`DeFi beta` 两个 bucket，看 bucket 内 alpha 是否明显强于 unrestricted pair scan。  
3. **把 exit 拆成两段**：
   - `full reversion to |z|<=0.5`
   - `first compression >=1.0σ`
   比较哪个更适合 `5m / 15m`。  
4. **把 z-threshold 做成网格**：`2.0 / 2.5 / 3.0`，看信号密度和净值的 trade-off。  
5. **把 execution 单独测掉**：同一信号在 `taker/taker` 与 `maker/taker` 下，盈亏差多少；如果 edge 只剩纸面统计，不要急着升级到实盘。

## 10. 风险与局限
- 这次主材料是 repo，不是正式论文；统计定义要靠 source audit 自己补全。  
- Binance 只是 public-data proxy，真实落地还要看 Hyperliquid/Bybit/OKX perp 的盘口深度、撮合、资金费率与最小下单单位。  
- 当前快检说明 **lookback 极敏感**，所以任何“这个 pair 很稳”的结论都必须先绑定窗口长度。  
- `ARB/CRV` 这类幸存者 pair 目前更像 **shock-compression**，不是稳定 full mean reversion；如果出场定义错了，很容易把 paper alpha 变成 execution 噪音。  
- repo 默认 `50%` 可用保证金/组 的 sizing 对 desk 来说偏猛，不能原样照抄。

## 11. 这次最值得记住的一句话
**别把短周期 pairs 理解成“任意两币找协整”；对 desk 更值钱的，往往是白名单 peer-cluster 里的那种短 half-life 错位。**

## 12. 来源
1. **Andrew Wilkinson / Privateer Capital (2024 repo, 2025 latest push). _Privateer Capital_. GitHub repository.**  
   Readable URL: https://github.com/ADWilkinson/privateer-capital  
   Repo URL: https://github.com/ADWilkinson/privateer-capital
2. **Privateer Capital README / architecture / scheduling**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/README.md
3. **Privateer Capital whitelist docs**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/docs/SERVER_ASSET_WHITELIST.md
4. **Privateer Capital position management docs**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/docs/SERVER_POSITION_MANAGEMENT.md
5. **Privateer Capital order execution docs**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/docs/SERVER_ORDER_EXECUTION.md
6. **Privateer Capital source: asset whitelist mapping**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/server/src/utils/assetMappings.ts
7. **Privateer Capital source: pair strategy / correlation analysis**  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/server/src/analysis/correlationAnalyzer.ts  
   Readable URL: https://raw.githubusercontent.com/ADWilkinson/privateer-capital/main/server/src/strategies/pairsCorrelationStrategy.ts
8. **Binance USDⓈ-M Futures API Docs**  
   Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
9. 本地 artifacts：
   - `reports/artifacts/quant_digests/privateer_peer_pair_scan_15m_20260331.csv`
   - `reports/artifacts/quant_digests/privateer_arb_crv_signal_followthrough_15m_20260331.csv`
