# 别把跨币种 order-book 仓库只读成 ML demo：更该先测的是「BTC 盘口压力极端、ETH 盘口反向/迟钝」1m/3m cross-crypto raw alpha
- 时间：2026-03-26 09:50 UTC
- 类型：2026 GitHub 新仓库 + Binance Spot 公共 `1m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：当 `BTC` 盘口压力 / taker-flow 明显单边，而 `ETH` 同时段盘口或 taker-flow 仍反向、且价格跟随不足时，`ETH` 在后续 `1m/3m` 存在向 `BTC` 方向补动的 cross-crypto lead-lag pocket
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-crypto/lead-lag/microstructure/order-book/order-flow/relative-value/stat-arb/btc/eth/1m/3m/5m/repo/external-data/binance
- 证据类型：仓库证据 + 公共数据代理快检

> 先回答 base alpha：**这不是 filter，也不是单纯模型工程。base alpha 就是“BTC 的盘口/成交流状态先动，ETH 还没完全跟上时，ETH 会在极短持有窗里补动”的 cross-crypto lead-lag raw alpha。**

## 1. 这次看了什么
主线材料是一份很新的 GitHub 仓库：

- **solalbaudoincs (2026), _IFCOG / ifcob: Information Flow in Crypto Order-Books_**

它的 headline 看起来像“做一个 XBT/ETH 的 order-book 预测框架”，但对我们 desk 真正有价值的不是模型名字，而是它把一句可交易的话说清楚了：

**用 `BTC/XBT` 的盘口特征去预测 `ETH` 的未来极短收益。**

更关键的是，这不是停在 feature importance 的 explainability notebook。仓库已经把完整骨架搭出来：
1. 原始 order-book 预处理
2. `imbalance / slope / liquidity ratio / volume` 特征生成
3. `XBT -> ETH` 的预测目标定义
4. 模型训练与性能报表
5. 事件驱动回测引擎
6. 明确 entry/exit 的策略类

所以它不是“又一个微观结构概念展示”，而是**可以直接翻译成 desk 最小实验的 raw alpha skeleton**。

## 2. 一句话核心结论
- **一句话结论**：这份仓库最值得 intake 的，不是“随机森林能不能多提几点准确率”，而是 **BTC 盘口压力极端、ETH 盘口还反着或没跟上时，ETH 后面 1~3 分钟会补动** 这条高强度 cross-crypto raw alpha。
- **一句话它怎么证明**：仓库直接把 `XBT` 的盘口特征拿去预测 `ETH` 未来 `200ms` 方向，并且给了策略类；我再用当前 Binance 公开 `1m` K 线里的 taker-buy proxy 做了一个便宜版 sanity check，看这条边压粗后还能不能留下影子。

## 3. 仓库里最值钱的，不是模型名，而是这 4 个可搬走的部件
### 3.1 它明确在做「一个币的盘口 → 另一个币的未来收益」
仓库 README 写得很直接：目标是研究 **multiple cryptocurrencies 的 order-books**，用一个币的盘口特征（如 `bid-ask imbalance`、`depth shifts`）去预测另一个币的短期收益，并做 out-of-sample backtest。

这点很关键，因为它把主题从“单资产方向预测”升级成了 **cross-asset information flow**，更贴近我们 desk 现在想补的 lead-lag / relative-value 素材池。

### 3.2 特征不是抽象 embedding，而是可直接落地的盘口量化因子
仓库当前直接列出了：
- `bid-ask-imbalance-5-levels`
- `V-bid-5-levels` / `V-ask-5-levels`
- `slope-bid-5-levels` / `slope-ask-5-levels`
- `avg-250ms-of-slope-*`
- `avg-250ms-of-liquidity-ratio-5-levels`

也就是说，这条 alpha 的原始形态并不复杂：
**盘口偏斜、深度斜率、流动性倾斜、以及这些量在短窗口上的持续性。**

### 3.3 它已经把 alpha 写成了完整策略骨架，而不只是分类器
`Mateo2StartStrategy` 的逻辑非常直接：
- 用 `XBT` 特征做预测；
- 若模型给出正向信号，则买入 `0.01 ETH`；
- 并在 `200ms` 后自动程序化卖出。

这说明仓库作者自己也没有把它当纯解释型项目，而是默认：
**这条边应该被写成短持有、事件驱动、快进快出的完整策略。**

### 3.4 它顺手也告诉我们：这条边寿命很短，别乱拉长 horizon
仓库里一个更像样的目标是：
- `avg-10ms-of-mid-price-itincreases-after-200ms-with-threshold-5`

对应的 `perf.json` 给出：
- 样本量 `363,537`
- 正类支持数 `12,244`（约 `3.37%`）
- 正类 **recall ≈ 60.5%**
- 正类 **precision ≈ 10.2%**
- 总体 **accuracy ≈ 80.8%**

这不代表“直接实盘躺赚”，但至少说明：
**在稀有事件 pocket 里，`BTC` 盘口对 `ETH` 的 200ms 方向确实有可检出的信息。**

更重要的是，仓库的 `500ms` 目标几乎塌掉：
- 正类支持数只有 `56 / 363,537`
- 正类 recall `0`

这句对 desk 非常值钱：
**这条 edge 不是 horizon 越长越香，反而很可能只能在极短窗存活。**

## 4. 公共 `1m` 代理快检：压粗以后，这条边还剩多少影子？
我没有去伪装成“已经完整复刻 order-book”。第一轮只做一个更便宜、更容易大规模跑的代理实验：

### 4.1 公开数据源
- Binance Spot `BTCUSDT` / `ETHUSDT` 公共 `1m` klines
- 时间窗：最近约 `5000` 根 `1m` bar（约 `3.5` 天）
- 可直接从公开 API 拿到，无需私有数据库

### 4.2 代理特征
因为没有真 `L2` 深度流，我先拿 K 线里的 taker-buy 字段做代理：
- `ofi_proxy = (2 * taker_buy_quote - quote_volume) / quote_volume`
- `qv_z = zscore(quote_volume, 240)`
- 同时看 `BTC` 与 `ETH` 的 `ofi_proxy` 是否方向相反

### 4.3 事件定义
触发事件需要同时满足：
1. `BTC qv_z > 1`
2. `|BTC ofi_proxy| > 0.25`
3. `sign(BTC ofi_proxy) != sign(ETH ofi_proxy)`
4. `ETH` 当根收益绝对值 `< 0.5 * BTC` 当根收益绝对值

直白翻译：
**BTC 这根 bar 明显有大单边 taker 压力，但 ETH 盘口/成交方向还没对齐，而且价格也没怎么跟。**

### 4.4 快检结果
在这段最近样本里，共得到 **13 个事件**。以 `BTC` 冲击方向为基准看 `ETH` 后续 signed move：

- **未来 `1m`**：hit rate **61.5%**，平均 **+0.55 bps**，中位数 **+1.13 bps**
- **未来 `3m`**：hit rate **69.2%**，平均 **+2.67 bps**，中位数 **+2.40 bps**
- **未来 `5m`**：hit rate **61.5%**，平均 **+3.32 bps**，中位数 **+2.08 bps**
- 事件发生时，同根 `BTC-ETH` signed gap 中位数约 **2.78 bps**

### 4.5 这组数字怎么读
- **有影子，但样本稀。** 它不像 always-on alpha，更像 stress pocket / event pocket。
- **压成 `1m` 代理后，最像还能活的是 `3m` 持有窗。** 这和仓库里“edge 很短，不要乱拉长”的结论是同方向的。
- **公共代理仍然是弱版证据。** 真正值钱的部分还是 `L2` 深度、盘口 slope、250ms persistence，而不是 `1m` K 线本身。

## 5. 为什么这条线和当前 desk 直接相关
过去 24 小时里，我们 intake 了不少：
- pairs / distance / basis / parity 的 mean reversion
- CEX/DEX 价格发现
- 单资产 LOB directional timing

这篇的补位点在于：
**它不是单资产 LOB，也不是低频 BTC→alt basket，而是“cross-crypto、microstructure、极短 hold”的 lead-lag raw alpha。**

换句话说，它补的是：
- `1m / 3m` 更高强度 alpha 池
- `BTC -> ETH` 的跨币种信息流
- raw alpha 本体，而不是单纯 filter / overlay

## 5.5 策略拆解（必填）
- 方向属性：cross-crypto / lead-lag / microstructure directional alpha
- 基础 alpha：`BTC` 盘口压力与 `ETH` 盘口/价格尚未同步时，`ETH` 往往向 `BTC` 方向补动
- entry：
  - 原仓库版：`BTC` 特征模型给出正向 `ETH` 信号时，立即做 `ETH`
  - desk 代理版：当 `BTC` 的 `ofi / volume` 极端、`ETH ofi` 反向或迟钝、且 `ETH` 当根价格跟随不足时，下一根做 `ETH` 同向补动
- exit：
  - 原仓库版：`200ms` 自动平仓
  - desk 第一轮：优先先测 `1m / 3m` 固定持有；若保留 edge，再回到 `10s / 30s / 90s / 180s` 更细粒度
- sizing：按 `|BTC ofi_proxy|`、`qv_z`、`ETH gap bps` 分 bucket；只在高分位事件里开仓
- risk / veto：
  - 若 `BTC` 自己下一秒/下一分钟反转，立即 kill
  - 若 `ETH` 同步已完成（gap 已回补超 `70%`），不追
  - 若估计毛边不足覆盖 taker fee + slip，则 veto
- execution / cost：
  - 双腿版可做 `long lagger / short leader` beta-neutral
  - 单腿验证版先做 `ETH` 单腿，先确认信号存在，再决定要不要上双腿与 maker/taker 优化

## 6. 下一步怎么测（这篇最重要）
### 6.1 不要继续停在 K 线代理，下一轮直接上真 `L2`
最小正式复现建议：
- **数据源**：Binance public depth / bookTicker / aggTrades（公开可得）
- **标的**：`BTCUSDT`, `ETHUSDT`
- **粒度**：`100ms / 250ms / 1s`
- **窗口**：最近 `7~14` 天先够

### 6.2 先测 3 组最关键的信号，而不是一口气堆模型
1. `BTC imbalance shock`
2. `BTC slope shock`
3. `BTC signal - ETH signal` 的 cross-book divergence

也就是先看：
**到底是 BTC 自己的单边压力最有用，还是 BTC-ETH 的盘口差分更有用。**

### 6.3 先测 4 个 horizon
- `10s`
- `30s`
- `60s`
- `180s`

理由很简单：
仓库已经暗示 `200ms` 还能看到东西，而 `500ms` 目标定义一改就可能塌掉；desk 版不能默认 `5m` 是最优，要用更细窗先把寿命曲线画出来。

### 6.4 评估指标别只看 accuracy
必须至少看：
- `event count / day`
- `signed bps per event`
- `hit rate`
- `net bps`（`fee`, `fee+0.5tick`, `fee+1tick` 三档）
- `gap-close ratio`
- `leader reversal conditional loss`

## 7. 我现在的判断
**这条线值得进入研究池，而且属于 raw alpha，不该降级成纯 filter。**

但它当前最合理的定位不是：
- “立刻做成 5m 主策略”；

而是：
- 对 `1m / 3m`：高强度 cross-crypto event-driven alpha 候选
- 对更长周期：如果压粗后 edge 很薄，就把它退化成 entry timing / execution component

简化成一句话：
**这份仓库真正给我们的不是一个现成模型，而是一条很清楚的假设：BTC 盘口先动、ETH 还没同步时，ETH 的补动值得被单独当成一条短寿命 raw alpha 去测。**

## 8. 风险与保留意见
- 当前仓库的性能报表是分类性能，不是稳定的成本后 PnL；不能把 `accuracy` 直接当收益。
- 正类事件本来就稀少，所以样本外最怕 regime shift 与 class imbalance。
- 我做的 Binance `1m` 快检只是廉价代理，不是对仓库真 `L2` 设计的完整 replication。
- 如果后续真 `L2` 复现发现 edge 只活在极少数 stress pocket，它仍然是 raw alpha，但更适合 event-trade，而不是 always-on engine。

## 9. 来源
1. **solalbaudoincs. (2026). _IFCOG / ifcob: Information Flow in Crypto Order-Books_. GitHub repository.**
   - Venue：N/A
   - DOI：N/A
   - Readable URL：https://github.com/solalbaudoincs/ifcob
   - Repo URL：https://github.com/solalbaudoincs/ifcob
2. **仓库 README（项目概览）**
   - URL：https://raw.githubusercontent.com/solalbaudoincs/ifcob/main/README.md
3. **仓库策略实现：`Mateo2StartStrategy`**
   - URL：https://raw.githubusercontent.com/solalbaudoincs/ifcob/main/strategies/mateo_2_start.py
4. **仓库性能文件：200ms 目标**
   - URL：https://raw.githubusercontent.com/solalbaudoincs/ifcob/main/predictors/mateo/target-avg_10ms_of_mid_price_itincreases_after_200ms_with_threshold_5_depth-3_nest-100/perf.json
5. **仓库性能文件：500ms 目标**
   - URL：https://raw.githubusercontent.com/solalbaudoincs/ifcob/main/predictors/mateo/target-price_increase_next_500ms_with_10_threshold_depth-3_nest-100/perf.json
6. **Binance Spot API（`BTCUSDT` / `ETHUSDT` 公共 `1m` K 线）**
   - URL：https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000
   - URL：https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1m&limit=1000
