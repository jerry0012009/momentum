# 别把 BTC→ALT lead-lag 继续写成泛泛“山寨会跟”：这篇 2026 开放获取论文更该先测的是「低成交 laggard 的 1~3 分钟 delayed catch-up」完整 raw alpha
- 时间：2026-03-27 03:16 UTC
- 类型：2026 Asia-Pacific Financial Markets 开放获取论文（全文 PDF 可读）+ Binance Spot 公共 `1m` 本地 quick check
- 主题类型：raw alpha
- 基础 alpha：当 BTC 在 `1m` 上先发生冲击时，低成交/低即时响应的 alt 往往不会在当分钟完全反映，而会在随后 `1~3` 分钟出现 delayed catch-up；因此更适合做 **liquidity-ranked laggards 跟随 / 对冲式 relative-value**，而不是把所有 alt 一把梭同向打包
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-crypto/lead-lag/liquidity-delay/trade-count/isi/laggard-ranking/relative-value/stat-arb/btc/alt/1m/3m/5m/15m/binance/paper/external-data
- 证据类型：开放获取论文证据（全文 PDF 可读）+ 本地公共数据快检

## 1. 这次看了什么
先回答 base alpha：**不是“BTC 带 alt”这句老话；真正能进研究池的是——当 BTC 先动时，哪些低成交 alt 在当分钟明显欠反应，并在接下来 `1~3` 分钟补动。这个“欠反应 → catch-up”本身就是可做的 raw alpha。**

主材料是：
- **Tomoki Kurihara, Takuji Matsumoto (2026), _Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy_, Asia-Pacific Financial Markets.**

这篇东西值得写，不是因为我们缺第 N 篇 lead-lag，而是因为它给了一个比“谁先动谁后跟”更 desk 化的切口：

1. **它把 delay 和 liquidity 直接绑在一起。** 不是所有 alt 都慢，而是 **低 trade count** 的 alt 更容易慢。  
2. **它直接给了完整交易框架。** 不是只做相关性分析，而是继续往下做了 `entry / hold` 的 LightGBM 决策、阈值搜索、手续费入账、样本外比较。  
3. **它天然贴近 `1m / 3m`。** 论文主口径就是 `1m`，并且明确写到大中市值币基本同步，真正留下 pocket 的是小币、低成交币、滞后几分钟的那一层。  

这正好符合当前 desk 的 intake 偏好：继续补 **可独立复现、能直接写成完整策略** 的 raw alpha，而不是继续把 cross-market 题材只当 shared gate 或解释层。

## 2. 核心结论
- **一句话核心结论：** 这篇 2026 论文最该偷的，不是“BTC 领先 alt”这句废话，而是：**用成交频度 / 即时响应度把 alt 分层后，真正可交易的是“低响应 laggards 的分钟级 delayed catch-up”，而不是 always-on 的全市场跟随。**
- **一句话它怎么证明：** 作者用 Binance `1m` 收盘价与 trade count，先证明 `trade count` 越低、立即响应越弱、延迟越明显；再用 BTC 和 ALT 的 `t-1` 收益做 LightGBM 的 `entry / hold` 二分类模型，在样本外比较 lag strategy 与 buy-and-hold。

这轮最关键的 8 个数据点：
1. **数据频率：** 全文主分析使用 **Binance 公共 `1m` 数据**。  
2. **大样本 liquidity 假设检验：** Bull regime 覆盖 **369** 个币，Bear regime 覆盖 **381** 个币。  
3. **trade count 与即时响应 ISI 的相关性：** Bull 为 **`0.561`**，Bear 为 **`0.483`**；两边 t 值分别 **`12.987` / `10.740`**，p 值都 **`< 1e-16`**。翻成人话：**成交越活跃，越同步；成交越稀，越容易慢半拍。**  
4. **Granger 因果方向：** 文中纳入的所有 ALT 对，`BTC(t-1) -> ALT(t)` 都在 5% 水平显著；例如 Bull regime 下 **BTC→GNO 的 F 统计量 `2109.444`**、**BTC→QKC 为 `706.515`**。  
5. **反向因果大多不成立：** 大部分 `ALT -> BTC` 不显著，说明这条线不是“大家互相拖动”，而更像 **BTC 单向向外扩散**。  
6. **VAR 结果：** 小币里 **QKC / PIVX** 对 `BTC(t-1)` 的回归系数都在 **`0.1+`**；而大/中市值币大多只有 **`0.05` 以下**。  
7. **交易成本假设：** 论文把手续费设为 **`0.02%` 单边**，高于 Binance 文中给出的最低可行水平 **约 `0.0175%`**，算是偏保守。  
8. **阈值搜索结果：** 最优 `hold threshold` 在不同 regime 下都落在 **`-0.0001`**；`entry threshold` 在 Bull/Crash 为 **`0.0000`**、Sideways 为 **`0.0001`**。翻成人话：**更优的是“容易进、谨慎出”，而不是每根一分钟都来回翻。**

论文附录给出的样本外累积收益对比也挺直接：
- **Bear 子样本：** `QKC -9% -> +116%`、`BIFI -6% -> +96%`、`PIVX -12% -> +69%`（buy-and-hold vs lag strategy）。  
- **Bull 子样本：** `PIVX +7% -> +81%`、`QKC +7% -> +59%`、`BIFI +1% -> +49%`。  
- 但 **ETH / LTC** 在同一套参数下反而不亮眼，说明这不是“拿大币也一样能吃”的普适方向因子，而更像 **低流动性 laggard pocket**。

## 2.5 这次最值钱的 desk 读法
如果只是照抄 headline，这篇会被读成“BTC 对 alt 有高频传导”。这没什么意义。

更值得 desk 拿走的 side branch 是：

**把“是否值得交易”从资产类别判断，改成“当下这只 alt 的 trade count / immediate sensitivity 是否足够差”，只在最慢的 laggards 上出手。**

也就是：
- 不是默认所有 alt 都跟；
- 不是把 BTC 冲击只拿来给别的策略做门禁；
- 而是直接构造一个 **liquidity-ranked laggard alpha**：
  - leader = BTC
  - follower universe = 可交易 alt
  - edge = 同一分钟欠反应 + 接下来 `1~3` 分钟补动
  - ranking = 低 trade count / 低 ISI / 高 underreaction score 优先

这比最近若干篇“leader 先动，basket 后动”的主题更具体，因为它多了一个 **谁更慢** 的可量化排序轴。

## 3. 为什么和当前项目直接相关
- 它是 **raw alpha**，不是 filter。  
- 它直接服务于当前更该继续补的池子：`cross-sectional / relative-value / stat-arb / lead-lag`。  
- 它和最近学习轨迹是对齐的：当前 digest 默认要优先补 **可直接写成完整策略的 raw alpha**，尤其是能映射到 `1m / 3m / 5m / 15m` 的东西；这篇正好就是 `1m` 原生、`3m` 可承接、`5m` 可做聚合验证。  
- 它也比继续讲“BTC 先动，alt 会跟”更值钱，因为它多给了一层 **liquidity / responsiveness ranking**，更接近真正可执行的 alpha 提纯。

## 3.5 策略拆解（必填）
- 方向属性：cross-crypto / relative-value / lead-lag / stat-arb
- 基础 alpha：BTC 先发生 `1m` 冲击后，低成交、低即时响应的 alt 在当分钟欠反应，并在接下来 `1~3` 分钟补动
- regime：优先在 **BTC 有明显短周期冲击**、且 follower 仍有成交但并不拥挤的时段开机；纯横盘噪声时降级
- filter / veto：
  - 只做有稳定成交、盘口没塌掉的币
  - 避开极端新闻、单币异常上新/下架、盘口点差异常拉宽
  - 若 alt 已在当前分钟同步反应到位，则不追
- risk / sizing / execution overlay：
  - 优先做 **long laggard / short β·BTC** 的对冲式版本，避免把市场 beta 误当 alpha
  - 仓位按 follower 波动、trade count 分位和盘口冲击限额缩放
  - 低成交币默认更有 edge，但也更容易被滑点吃掉，所以 notional cap 必须更严格
- entry：
  1. 计算 `BTC 过去 1m return`
  2. 只在 `|ret_BTC|` 处于滚动高分位时开信号（比如过去 3~7 天的 top 5%~10%）
  3. 对每只 alt 计算 `underreaction_score = beta_i * ret_BTC - ret_ALT_current`
  4. 再乘一层 `laggard_score`（如 trade count 低分位 / 低 ISI / 历史 lag 稳定度）
  5. `long` 同向欠反应最明显的 laggards；若做 market-neutral，则 `short β·BTC` 或做最弱 vs 最快的 long-short pair
- exit：首轮先测固定持有 `1m / 2m / 3m / 5m`；若 `3m` 后 edge 已衰减，别硬拖到 `15m`
- cost：
  - maker 假设先测 `2 / 4 / 6 bps round-trip`
  - crossed/taker 再测 `6 / 10 / 14 bps`
  - 低成交小币额外叠加 impact veto

## 4. 本地 quick check：Binance Spot 最近 3 天 `1m` transfer
为了避免完全停在 paper 里，我补了一个最小快检：
- **数据源：** Binance Spot 公共 `1m` klines（含 `trade_count`）
- **口径：** 最近约 `3` 天、`4319` 根 `1m` bar、`BTCUSDT` 对 `15` 个 alt
- **指标：**
  - `corr0 = corr(ret_BTC_t, ret_ALT_t)`
  - `corr_lag1 = corr(ret_BTC_t, ret_ALT_{t+1})`
  - `ISI_proxy = corr0 - mean(corr_lag1...lag5)`

3 个最关键结果：
1. **`log(trade_count_total)` 与 `ISI_proxy` 的相关系数是 `0.881`。** 这和论文 H2 的方向完全一致：**越活跃越同步，越冷门越慢。**  
2. **高流动性币几乎同步：** `ETHUSDT` 的 `corr0 = 0.894`，而 `corr_lag1 = -0.021`；`XRPUSDT` 的 `corr0 = 0.797`，`corr_lag1 = 0.018`。  
3. **低流动性币更像 delayed pocket：** `QKCUSDT` 的 `corr0 = 0.024`、`corr_lag1 = 0.100`；`CITYUSDT` 的 `corr0 = 0.020`、`corr_lag1 = 0.070`；`BIFIUSDT` 的 `corr0 = 0.052`、`corr_lag1 = 0.100`。这说明 **有些币不是“不跟”，而是“当分钟不跟、下一分钟才补”。**

这轮 quick check 的意义不在于直接证明可交易净值，而在于先回答一个 admission 级问题：**论文说的“低 trade count → 更慢”在最近 Binance 公开数据上是不是还活着？目前看，方向是活的。**

本地产物：
- `reports/artifacts/quant_digests/price_transmission_btc_alt_20260327_local_check.csv`

## 5. 可复刻的最小实验
**公开性 / 数据源 / 更新频率：**
- 数据源：Binance Spot 或 Futures 公共 kline API
- 是否公开可得：是
- 最小更新频率：`1m`
- 可映射周期：
  - `1m`：原始信号形成
  - `3m`：最自然的 monetization 窗口
  - `5m`：聚合后的稳健 transfer 验证
  - `15m`：更适合做“是否还有残留扩散”的否证，不适合假装它是主 formation clock

**第一版最小实验建议：**
- leader：`BTCUSDT`
- followers：先做两组
  - 高流动性对照：`ETH / XRP / DOGE / ADA / LTC`
  - 低流动性实验组：`QKC / CITY / BIFI / PIVX / GNO`
- signal：
  1. `BTC 1m return` 超过滚动分位阈值
  2. `alt current-minute return` 同向但反应不足，或完全未反应
  3. `trade_count` 位于该币自身滚动低分位，或该币历史 `lag score` 较差
- position：
  - baseline A：`long laggard / short BTC beta`
  - baseline B：同组内 `long 最慢 / short 最快`
- hold：`1m / 2m / 3m / 5m`
- 核心输出：
  1. `avg gross bps / trade`
  2. `break-even round-trip cost`
  3. `hit rate`
  4. `delay persistence by liquidity bucket`
  5. `capacity proxy = signal count × median trade_count`

## 6. 下一步怎么测（必须）
1. **先把 universe 分桶，不要上来全市场。** 这篇 paper 最大价值就在 liquidity layering；下一步应先按 `trade_count` 分五档，看 edge 是否只活在最慢一两档。  
2. **把“低 liquidity”从静态标签改成动态标签。** 同一只币在不同时间段 trade count 差别很大；实盘更该用 rolling `trade_count percentile`，而不是永远写死“小币名单”。  
3. **优先验证 `1m -> 2m/3m`，不要先跑 `15m`。** 如果 `3m` 内都没钱，说明这条线已经降级成 paper edge；若 `1m` 太快、`5m` 还残留，再考虑 bar 化。  
4. **把方向版和对冲版分开测。** 很多“看起来赚钱”的结果，最后只是 BTC beta 跟涨，不是独立 alpha；所以必须比较 `裸做 alt` vs `long alt / short β·BTC`。  
5. **把成本分成两层。** 一层是统一交易费，另一层是小币冲击 / 点差；如果只有在忽略 impact 时才盈利，这条线只能留在素材池。  
6. **做 ETH 作为替代 leader 的对照。** 论文结尾也点了这一点：有些小币可能受 ETH 影响不小。若 `ETH -> alt` 比 `BTC -> alt` 更稳，desk 应该直接换 leader，不要对 BTC 叙事恋战。

## 7. 风险与保留意见
- 这篇 paper 的 raw alpha 很像样，但**主要受益对象是低流动性小币**；这天然带来容量、冲击成本和可做空性问题。  
- 论文策略是 **long-only / 持有状态机** 风格，更像“利用滞后做时点选择”；我们 desk 更可能落成 **对冲版 relative-value**，所以 transfer 不能直接照搬收益率。  
- 论文的样本集中在特定事件期：`2024-02/03` Bull、`2024-06/07` Bear、`2024-08/09` Sideways、`2025-01/03` Crash；它不是全年无差别扫描。  
- 低 liquidity 本身既是 edge 来源，也是 execution 毒药；如果实盘只能下很小 notional，这条线更适合作为 **高强度 pocket alpha**，而不是主容量引擎。  
- quick check 只验证了“delay 方向还在”，**没有验证 post-cost alpha 一定成立**；下一步必须老老实实做 costed hold-window test。

## 8. 来源
1. **Kurihara, T., & Matsumoto, T. (2026). _Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy_. Asia-Pacific Financial Markets.**  
   - DOI: <https://doi.org/10.1007/s10690-026-09589-z>  
   - Readable URL: <https://link.springer.com/article/10.1007/s10690-026-09589-z>  
   - PDF: <https://link.springer.com/content/pdf/10.1007/s10690-026-09589-z.pdf>  
   - Repo URL: `N/A（未见作者公开代码仓）`
2. **Binance Spot API – Kline/Candlestick Data / Exchange Info.**  
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>  
   - Exchange Info: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information>  
   - Repo URL: `N/A`

## 9. 本地产物
- `research/quant_digests/2026-03-27_0316_btc-alt-liquidity-ranked-delay-alpha.md`
- `reports/artifacts/quant_digests/price_transmission_btc_alt_20260327_local_check.csv`
