# 别把这篇 2022 NAJEF 论文只读成“crypto 日内既有动量也有反转”：对 short-cycle desk，更该先测的是「UTC hour-pair signed lag map × continuation/fade 切换」完整 raw alpha

- 时间：2026-04-04 07:56 UTC
- 类型：2022 *The North American Journal of Economics and Finance* 论文摘要 / Introduction / Section snippets（ScienceDirect）+ Crossref / Semantic Scholar metadata + Binance 公共 `5m/15m` 数据可得性快检
- 主题类型：raw alpha
- 基础 alpha：**同一 UTC 日内，较早时段的收益会对较晚时段收益产生可学习的“带符号预测”——有些 hour-pair 是 continuation，有些是 reversal；真正可交易的不是“统一做动量”或“统一做反转”，而是 `source hour -> target hour` 的 signed lag map。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/intraday/time-of-day/hour-pair/signed-lag-map/continuation/reversal/single-asset/btc/eth/ltc/xrp/5m/15m/3m/1m/paper/public-data/cost/risk
- 证据类型：论文证据 + 元数据 + 公共行情可移植性快检

## 1. 先回答这轮最重要的一句：base alpha 是什么？

> **base alpha 不是“情绪/流动性/宏观过滤”，也不是“单纯说市场既可能动量也可能反转”。**
>
> **它是：同一 UTC 日内，某个较早 hour-slot 的收益，对某个较晚 hour-slot 的收益，存在稳定但带符号的预测关系；符号为正时做 continuation，符号为负时做 fade。**

翻成人话：

- 不要把 BTC 日内信号写成一条全时段统一规则；
- 更像是一个 **24×24 的“时段对时段”有符号 lead/lag 图谱**；
- 有些口袋该顺着打，有些口袋该反着打；
- `jump / liquidity / FOMC` 更适合作为这条 raw alpha 的 **gate / veto**，而不是 alpha 本体。

这也是这轮值得写的原因：

1. **它是 raw alpha，不是解释型综述；**
2. **它不依赖难拿外部数据，公开 OHLCV 就能复现主干；**
3. **它和最近 intake 里偏多的 pairs / carry / repo shell 不同，补的是更基础的单币 intraday alpha 家族。**

## 2. 这篇论文到底说了什么

主材料：

1. **Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao (2022)**, *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*, **The North American Journal of Economics and Finance**, 62, 101733.  
   DOI: `10.1016/j.najef.2022.101733`  
   Readable URL: `https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833`
2. SSRN working-paper metadata mirror：`10.2139/ssrn.4080253`

基于 Semantic Scholar 摘要 + ScienceDirect 页面可读内容，这篇文章的关键信息够我们做一个很清楚的 desk 化转译：

### 2.1 论文样本与频率
- **资产**：Bitcoin 为主，另做 ETH / LTC / XRP 稳健性检查
- **样本区间**：**2013-03-03 至 2020-05-31**
- **原始频率**：**5 分钟**
- **主分析频率**：**小时收益**，并补做 **half-hour** 稳健性检查

### 2.2 论文的核心发现
1. **crypto 日内回报可预测，而且不是单一符号。**
   - 同一日内，较早小时收益对较晚小时收益，既可能是 **正向延续**，也可能是 **反向回吐**。
2. **这种 predictability 会被 regime 明显影响。**
   - 论文明确写到：在 **无大跳跃（no jump）**、**无 FOMC 发布**、**低流动性** 子样本里，这种日内可预测性更强。
3. **不只 BTC。**
   - 这种现象在 **ETH / LTC / XRP** 上也能看到。
4. **经济价值不只是 t-stat。**
   - 论文写明：基于这些 intraday predictors 的 **timing strategy**，比 `always-long` / `buy-and-hold` 等基准更有经济价值。

### 2.3 论文给我们的理论解释
- **正向 continuation**：更接近 **late-informed investors** / 信息扩散慢
- **负向 reversal**：更像 **对非基本面信息的过度反应 + 过度自信**

对 desk 来说，这一点很关键：

> **同样都是“上一段涨了”，下一段到底该追还是该反手，不是看一条统一规则，而是要看它发生在什么 UTC 时段、对应哪个 target 时段、当下是否处在 jump / FOMC / 高流动性破坏区。**

## 3. 为什么这轮值得优先进入研究池

如果只把论文读成“crypto 日内既有动量也有反转”，那基本没有研究价值，因为这句话太宽。

真正值得 intake 的，是下面这个 desk 读法：

> **把论文改写成一条可以直接下手的完整 raw alpha：`UTC hour-pair signed lag map`。**

也就是：

- source hour = 较早时段
- target hour = 较晚时段
- 在滚动窗口里估计 `source -> target` 的符号和强度
- **符号 > 0**：target hour 做 continuation
- **符号 < 0**：target hour 做 fade
- `jump / FOMC / 高流动性`：默认当 veto / risk cut，不当 alpha 本体

为什么这比继续补一个普通 filter 更值钱？

1. **它本身就是 raw alpha。**
2. **它天然能拆成完整策略四件套：entry / exit / sizing / risk / cost。**
3. **它和 `1m/3m/5m/15m` 的关系非常直接。**
   - 论文虽主要在小时级别做图谱；
   - 但我们的执行完全可以压缩到 `15m`，甚至在 `5m` 做更细的进出场。

## 4. 我们该怎么 desk 化：别直接做 96×96，而是先做“1H 图谱 + 15m 执行壳”

如果粗暴把 `15m` 拆成 96 个 slot，再做 96×96 lag map，第一版很容易过拟合。

更稳的读法是：

### 4.1 第一层：先学 **1H signed lag map**
- 用 `5m` K 线聚合成 1H 收益；
- 在每个滚动训练窗里，学习：
  - `r_hour[s] -> r_hour[t]` 的符号；
  - 是否具备最基本的稳定性（sign stability / OOS hit ratio / t-stat）；
- 最后得到一个 **24×24 的有向带符号图谱**。

### 4.2 第二层：再用 **15m 做执行压缩**
- 真正下单不一定等整小时结束才做；
- 可以在 target hour 的前 `15m` / 前 `30m` 进入，尾段退出；
- 这样既保留论文的小时级结构，又让执行更贴近 short-cycle。

### 4.3 第三层：把论文里的 regime 发现当成 gate
- `jump veto`
- `FOMC veto`
- `too-liquid / too-fast tape veto`

也就是说：

> **alpha 主体是 signed lag map；regime 组件只负责决定“今天这个时段对时段口袋，还要不要开”。**

## 5. 策略拆解（按 entry / exit / sizing / risk / cost 写清）

## 5.1 Universe
第一版不要铺太宽：
- 主线：`BTCUSDT perp`
- 稳健性：`ETHUSDT / LTCUSDT / XRPUSDT`
- 如果 BTC 站得住，再扩到 top liquid majors

## 5.2 Signal（raw alpha 主体）
定义：
- `r_s(d)` = 第 `d` 天 source hour `s` 的收益
- `r_t(d)` = 同一天较晚 target hour `t` 的收益，`t > s`

在滚动窗口内估计：
- `beta_{s,t}` 的符号
- `t-stat_{s,t}`
- OOS hit ratio / OOS R² 是否至少不为负

交易规则：
- 若 `beta_{s,t} > 0`，则 source hour 出现显著正收益时，target hour 顺着做；显著负收益时也顺着做空
- 若 `beta_{s,t} < 0`，则 source hour 出现显著正收益时，target hour 反着做空；source hour 显著负收益时，target hour 反着做多

第一版不要把所有 pair 都交易，先做 pocket selection：
- 只保留历史上 **稳定过门槛** 的 `s -> t` pair
- 每天最多只开 `1~3` 个 target pockets

## 5.3 Entry
第一版给三种最小实现：

### 方案 A：最像论文的“整小时版”
- source hour 收完后才确认信号；
- 到 target hour 开始时入场；
- 最适合先做 replication sanity check。

### 方案 B：`15m` 压缩执行版
- source hour 结束确认信号；
- 在 target hour 的前 `15m` 入场；
- 若 target pocket 通常集中在 hour 开头，抓前段；否则也可改成前 `30m` 分批。

### 方案 C：`5m` 提前埋伏版
- 仅对最稳定 pocket 使用；
- 在 source hour 临近结束时，若 source return 已过阈值，可提前在 target 前 `5m` 小仓试探；
- 但这只适合第二轮，不建议作为首测。

## 5.4 Exit
- 默认 **time-stop**：持有到 target pocket 结束
- 备选：
  - `1h` pocket：持有 `1h`
  - `15m` 压缩执行：持有 `15m~45m`
  - 若盘中反向波动超过 `k * sigma_target`，提前止损
- 第一轮不要加太多花哨 trailing，先保留最干净的 timing shell

## 5.5 Sizing
- 基础仓位：按 `target-hour realized vol` 做 inverse-vol sizing
- pair 权重：按历史 `|t-stat_{s,t}|` 或 OOS hit ratio 缩放
- 组合层：
  - 单 pocket 上限 `20% gross`
  - 单日总 gross 上限 `100%`
  - 同向连续 pocket 不叠太满，避免把 hour-pair alpha 误放大成全天方向赌注

## 5.6 Risk / Veto
这部分要直接继承论文发现：
- **jump veto**：若 source hour 内出现异常大波动 / wick / realized jump，默认减仓或不做
- **FOMC veto**：FOMC 窗口前后几小时先关掉
- **high-liquidity / hyper-fast tape veto**：论文发现低流动性更强，所以极高参与度区间别默认 edge 更大
- **slot crowding cap**：某些 UTC 时段若长期只在单一周几/单一市场状态赚钱，要单独检查是否过拟合

## 5.7 Cost
- 先跑 `2 / 4 / 6 / 8 bps` round-trip ladder
- 因为这条线持有期短、开平明确，**cost cliff** 会比日频策略更重要
- 若 `15m` 执行版在 `6 bps` 后全灭，就不要急着下钻 `5m`

## 6. 与 `1m / 3m / 5m / 15m` 的关系：别硬把论文伪装成逐根信号

这篇论文主干是 **小时级 intraday pocket**，所以对 short-cycle 的正确映射是：

- **1H**：学结构
- **15m**：做主执行壳
- **5m / 3m**：只用于更细的入场和减滑点
- **1m**：默认只当 execution layer，不建议直接拿来重新学整张 lag map

也就是说：

> **这不是“每根 1m K 线都能独立产生 alpha”的材料。**
>
> **它更像是：先识别今天 UTC 日内哪些时间口袋更容易 continuation，哪些更容易 reversal，再用 15m/5m 去执行。**

这点很重要，能避免把一个本来清楚的小时级 alpha，误做成一团高维噪音。

## 7. 最小可复现实验（第一周就能做）

### 7.1 实验 1：BTC 小时图谱复刻
目的：先验证论文主干在当前交易所数据上是否还活着。

- 数据：Binance spot / perp `5m` K 线聚合成 `1h`
- 训练：滚动 `90d / 180d`
- 输出：
  1. `24×24` signed lag map
  2. 正向 pocket 数量 vs 反向 pocket 数量
  3. 每个 pocket 的 OOS hit ratio / post-cost bps

**通过条件：** 至少出现少数稳定 pocket，而不是全图随机翻转。

### 7.2 实验 2：1H 图谱 + 15m 执行
目的：确认 short-cycle 可交易性，而不是只剩论文味道。

- 对实验 1 中最稳定的 `3~5` 个 pocket：
  - 在 target hour 前 `15m` 或开头 `15m` 入场
  - 持有到 target hour 结束
- 对照：
  1. 整小时开平
  2. 15m 压缩执行
  3. 不分 pocket、统一做 momentum 的愚蠢基线

**通过条件：** 15m 执行版至少不比整小时版差很多，且明显优于“全时段统一追涨杀跌”。

### 7.3 实验 3：gate 是否真有用
目的：把论文里的 regime 发现变成 desk 可落地 veto。

对实验 2 的最佳版本，分四组：
1. 无 gate
2. `jump veto`
3. `FOMC veto`
4. `jump + FOMC + high-liquidity veto`

**通过条件：** gate 至少能改善以下一项：
- post-cost Sharpe
- worst day
- hit ratio
- turnover / bps captured

### 7.4 实验 4：跨币稳健性
- BTC 站住后，再复用同一 hour-pair 学法到 ETH / LTC / XRP
- 不要求同一张图谱；反而要看：
  - 哪些币 continuation pockets 更多
  - 哪些币 reversal pockets 更多

这能帮助后续做 **asset-specific intraday map**，而不是全市场统一参数。

## 8. 这轮最关键的“下一步怎么测”

1. **先做 BTC `1h` signed lag map 复刻。**
   - 不要一上来就 96×96；
   - 先把论文主干复现到当前交易所数据上。
2. **再做 `15m` 压缩执行，不要直接把 5m 当 alpha 频率。**
   - `5m` 优先当 execution layer，不当 discovery layer。
3. **一定要显式检验“正口袋”和“反口袋”是否都存在。**
   - 如果最后只剩单边 continuation，那说明你把论文最有价值的部分做丢了。
4. **gate 要后加，别先拿 gate 掩盖 alpha。**
   - 先看 raw alpha 自己能不能活；
   - 再看 `jump / FOMC / liquidity` 能不能让它更干净。
5. **重点看 cost cliff，不要只看 win rate。**
   - 这条线持有短、换手快，成本是第一杀手。

## 9. 风险与保留意见

- **我们拿到的是摘要 + Introduction + section snippets，不是全文表格。**
  - 所以这轮更适合产出一个 **desk 化 hypothesis note**，而不是冒充已完成逐表复刻。
- **论文样本止于 2020-05。**
  - crypto 微结构后来变了很多，所以必须做当下数据再验证。
- **小时 pocket 很容易受交易所 / UTC 定义影响。**
  - 不同 venue 的成交活动高峰不同，最好 spot / perp 都做一遍。
- **同类信号存在 data-mining 风险。**
  - 这就是为什么第一版必须先做 pocket selection + OOS sign stability，而不是把整张图都拿去交易。

## 10. 来源

1. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance, 62, 101733.**
   - DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: `https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833`
   - DOI URL: `https://doi.org/10.1016/j.najef.2022.101733`
2. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). SSRN working-paper entry.**
   - DOI: `10.2139/ssrn.4080253`
   - Readable URL: `https://doi.org/10.2139/ssrn.4080253`
3. **Binance Spot REST API Docs**
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`
4. **Binance USDⓈ-M Futures REST API Docs**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本轮结论（给后续 replication 排序）

- **一句话结论：** 这篇 2022 论文最值得 desk 拿走的，不是“crypto 日内也有动量/反转”这句空话，而是 **`UTC hour-pair signed lag map` 这条可直接做成完整策略的 raw alpha 主体**。
- **主题归类：** `raw alpha`
- **优先级：** 中高
- **最值得先做的版本：** `BTC 1H pocket discovery -> 15m 执行压缩 -> jump/FOMC/liquidity veto`
- **如果第一轮验证失败，最可能的问题：** 不是时间口袋思路错，而是当前 venue / 当前年代下，旧 pocket 已迁移，需要重新学习新的 slot map。

## 12. 本地产物
- `research/quant_digests/2026-04-04_0756_signed-hourpair-lagmap-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_0756_signed-hourpair-lagmap-alpha.html`
