# Hyperliquid whale-trade convergence continuation alpha

- 主题类型：raw alpha
- 基础 alpha：公开交易流里，**同方向的大额 aggressor 交易 / 可追踪钱包群聚** 往往不是噪音，而是短时信息冲击；若 5 分钟内出现多名“高分钱包”在同一资产同向出手，后续 `1m/3m/5m` 更值得先押 continuation，而不是先做 fade。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

> 一句话先定性：这不是“看见 whale 就跟单”的段子版 copy trading；更像是把 **公开钱包地址 + 大单门槛 + 5 分钟同向收敛 + 组合风险壳** 拼成一条可直接上最小实验的短周期 raw alpha。

## 1. 为什么这轮值得写

这轮我优先选它，不是因为又来了一个“多策略 bot”，而是因为这份 **2026 新仓库** 里真正最适合 desk 的，不是 funding sniper，也不是 liquidation rider，而是 **Whale Tracker** 这条可以独立拆出来跑的 raw alpha：

1. **base alpha 说得清**：大额 aggressor trade / 高分钱包同向聚集 → 短时 continuation。
2. **公开可拿数据**：Hyperliquid 公共 WebSocket `trades` 流直接给 `coin / side / px / sz / time / users`，其中 `users` 就是买卖双方地址。
3. **策略壳完整**：repo 里不仅有 entry，还有 confidence、sizing、TP/SL、相关性桶限额、反向信号平仓。
4. **时间尺度天然贴近 desk**：事件级触发 + `300s` 收敛窗，本来就是 `1m/3m/5m` 语境，不需要硬把日频论文掰成分钟线。

所以，这轮它比继续补一个纯 filter / 纯 veto 更值钱。

---

## 2. 本次主源与证据类型

### 主源 A：2026 GitHub 仓库（核心）
- **Authors / Maintainer**: CShear
- **Year**: 2026
- **Title**: *ref-perp-bot*
- **Venue / DOI**: GitHub repo / N.A.
- **Readable URL**: <https://github.com/CShear/ref-perp-bot>
- **Repo URL**: <https://github.com/CShear/ref-perp-bot>
- **本次重点审阅文件**:
  - `README.md`
  - `hlbot/strategies/whale_tracker.py`
  - `hlbot/strategies/combiner.py`
  - `hlbot/execution/executor.py`
  - `hlbot/config.py`
  - `.env.example`

### 主源 B：Hyperliquid 官方 WebSocket 文档（数据公开性）
- **Author**: Hyperliquid Docs
- **Year**: 2026 访问版本
- **Title**: *Websocket*
- **Venue / DOI**: Hyperliquid Docs / N.A.
- **Readable URL**: <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket>
- **用途**: 确认 `wss://api.hyperliquid.xyz/ws` 可公开订阅 `trades`，适合作最小实验数据入口。

### 辅助地基（微观结构为什么有可能成立）
1. **Easley, López de Prado, O’Hara (2012)**, *Flow toxicity and liquidity in a high-frequency world*, *Review of Financial Studies*, DOI: `10.1093/rfs/hhs053`.
2. **Wen, Perez, Livan, Caccioli (2023/2024 working-paper line)**, *Cross-Market Intraday Time-Series Momentum*, SSRN readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4080253>.

> 这里地基不是说“whale wallet = 必赚”，而是说：**短时订单流本来就会携带信息，而且跨账户/跨参与者的同向聚集，通常比单笔 isolated print 更有意义。**

---

## 3. Repo 里真正可拿来做 alpha 的部分

## 3.1 原始触发：不是所有 trade，都算 whale activity

`hlbot/strategies/whale_tracker.py` 里的核心阈值非常直接：

- `WHALE_TRADE_MIN_USD = 50_000`
- `SIGNAL_SCORE_THRESHOLD = 0.6`
- `CONVERGENCE_WINDOW = 300` 秒
- `CONVERGENCE_BOOST = 0.15`

也就是说，单笔交易要先过 **$50k notional**，而且发起方地址必须已经在 tracked whales 里，且该地址得分 `>= 0.6`，才会生成原始信号。

这个设计有两个好处：

1. 先过滤掉大量“小地址大惊小怪”。
2. 把策略重心从“绝对大单”改成“**历史上更值得信的人打出来的大单**”。

这比单纯看 `sz` 或单次 liquidation event 更像一个可持续 raw alpha admission layer。

## 3.2 真正值钱的是“同向收敛”，不是孤立巨单

repo 不是机械地“见大单就追”，而是额外统计：

- 同一资产 `coin`
- 同一方向 `side`
- 过去 `300s`
- 出现了多少个**不同钱包**

若 `convergence > 1`，就给 signal confidence 再加 `+0.15`，上限到 `0.95`。

这一步非常像我们 desk 更关心的东西：

> **不是单个账户一脚踹出去，而是多个独立账户 / 多次可归因大单，在很短时间内把同一方向确认出来。**

这比很多“单点 whale alert”更接近可以复现的短周期 alpha。

## 3.3 钱包分数不是拍脑袋，是可滚动更新的

repo 的 wallet score 机制虽然简陋，但足够形成最小可用版本：

- 新钱包发现门槛：`累计成交额 > $500k` 且 `trade_count > 5`
- 初始保守分：`min(volume / 5_000_000, 0.7)`
- 已跟踪钱包分数会缓慢衰减：`score *= 0.98`
- 最近 24h 有活跃 whale activity，再给 `+0.02 * count`，最多 `+0.1`

这意味着 repo 默认承认一个现实：

> **whale 不是静态白名单，而是动态 ranking。**

对 desk 来说，这很重要，因为真正该测的不是“神秘地址列表”，而是 **地址分层 + 活跃度再加权** 这套 admission stack。

---

## 4. 这条策略怎么落成完整交易规则

下面把 repo 里分散的逻辑合并成我们真正能跑的完整策略。

## 4.1 Entry

### Long entry
满足以下条件时开多：
1. 公共 trade stream 中出现 `size_usd >= 50k` 的买向 aggressor trade；
2. 买方地址在 tracked whales 中；
3. 该钱包 `score >= 0.6`；
4. 过去 300 秒内，同资产同方向 distinct whale 数量越多越好；若 `>1`，confidence 再加 `0.15`；
5. 资产不违反组合相关性桶约束。

### Short entry
同理，卖向 whale trade 触发开空。

## 4.2 Confidence

repo 里的原式：

```text
size_factor = min(size_usd / 100k, 1.5)
confidence = min(whale_score * (0.5 + 0.3 * size_factor), 0.9)
if convergence > 1:
    confidence += 0.15  (cap at 0.95)
```

翻成人话：
- 钱包越靠谱，分越高；
- 单笔 notional 越大，分越高；
- 多名 whale 同向收敛，再抬一档；
- 不是线性加仓，而是先映射成 confidence。

## 4.3 Sizing

repo 不是固定满仓，而是 Kelly-ish：

- `bankroll = 1000`
- `max_position_pct = 0.05`
- `min_order_notional = 10`
- `size = min(max_size * confidence^2, avg_suggested, max_size)`
- 且组合里同一 correlation group 的总暴露不能超过 **15% bankroll**。

这对我们很有借鉴意义：

> 这种“confidence²” sizing，天然抑制中低质量事件冲动开仓，更适合 event-driven raw alpha。

## 4.4 Exit / risk

repo 已经给了完整壳：

- 默认杠杆：`3x`
- `stop_loss_pct = 3%`
- `take_profit_pct = 6%`
- 若出现 **反向高置信原始信号**（`confidence > 0.6`），可提前平仓
- 若 unrealized loss 超过 **8% 当前 notional**，触发保护性退出
- 同资产已有仓位则不重复开

注意：
这套 TP/SL 更像通用 shell，**alpha 本体其实在 entry admission**。对 `1m/3m/5m` 实盘化时，TP/SL 大概率要缩窄，不然 holding period 会被拉太长。

---

## 5. 为什么它对 `1m / 3m / 5m / 15m` 真有关系

## 5.1 这条 alpha 天生属于分钟级 event-driven continuation

它不是日频钱包追踪，也不是慢 carry。

它的原始输入是：
- 实时 trade prints
- 地址级参与者信息
- 300 秒内的收敛计数

所以它天然适合：
- `1m`: 事件触发后的第一根 / 前三根 bar continuation
- `3m`: 降低噪音、保留冲击扩散
- `5m`: 最像 repo 默认设计语言
- `15m`: 更适合当持仓管理框架，不适合做首触发主频

## 5.2 它服务的不是“形态学 breakout”，而是信息流 alpha

这也是这轮值得收进素材池的地方。

base alpha 不是：
- retest
- breakout 形态
- RSI 超买超卖

而是：
- **公开钱包身份 + 大额 aggressor flow + 多账户同向收敛**

这能补充 desk 当前 raw alpha 池，不会只是旧 breakout 家族内循环。

---

## 6. 快速 sanity check：公开 live tape 上，这个阈值是不是死的？

我做了一个极小的公开 live probe：

- 数据源：Hyperliquid 公共 `trades` WebSocket
- 资产：`BTC / ETH / SOL`
- 观察时长：约 `20.48s`
- 口径：完全按 repo 的 `>= $50k` whale 门槛去数
- 结果文件：
  - `reports/artifacts/quant_digests/whale_tracker_liveprobe_20260401_0323/summary.csv`
  - `reports/artifacts/quant_digests/whale_tracker_liveprobe_20260401_0323/meta.json`

### 结果摘要
- BTC：`74` 笔 trade，最大单笔约 `$44.1k`，**0** 笔过 whale 门槛
- ETH：`58` 笔 trade，最大单笔约 `$22.5k`，**0** 笔过门槛
- SOL：`36` 笔 trade，最大单笔约 `$166.4k`，**1** 笔过门槛，且为 **buy**
- 合计：`168` 笔 trade 里，只有 `1` 笔过 `$50k`，占比约 **0.6%**

### 这说明什么
这不是 alpha 验证，只是 cadence sanity check。

结论很清楚：
1. **$50k 门槛是稀疏触发，不是高频信号**；
2. 稀疏是好事——更像 event-driven 高 conviction，而不是随时都能开仓的噪音策略；
3. 若扩到 `DOGE/WIF/PEPE` 这类低价高活跃币，门槛可能要改成 **按 ADV / top-book depth / coin-specific percentile**，否则容易“只在 majors 上活着”。

---

## 7. 真正值得 desk 复现的版本

repo 原版更像一个 live skeleton。对我们来说，更该复现的是下面这个 desk 版：

## 7.1 Desk 版最小可复现实验（推荐）

### Universe
- 先从 Hyperliquid 最活跃的 `BTC / ETH / SOL / HYPE / DOGE / PEPE / WIF` 开始
- 只保留最近 30d 成交额、trade count 足够的币

### Event definition
对每个 coin 的每笔 trade，计算：
- `trade_notional_usd`
- aggressor side
- buyer/seller wallet
- 同地址最近 7d / 30d PnL proxy（如果能从链上或公开成交回推）
- 同方向 distinct whales in last 300s
- 同方向 whale notional sum in last 300s

### Alpha trigger（第一版）
开多条件：
1. `trade_notional_usd >= coin_specific_threshold`
2. `wallet_score >= q80`
3. `same_side_distinct_whales_300s >= 2`
4. `same_side_whale_notional_300s >= q90`
5. 事件后第一分钟 mid 没有立刻反向吞没

开空同理。

### Exit
- `TP = +0.6% ~ +1.2%` 分层测试
- `SL = -0.3% ~ -0.6%` 分层测试
- `max_holding = 5 / 15 / 30 min`
- 若出现反向 whale convergence，立即平

### Cost
- taker-only 与 maker-entry / taker-exit 两套都测
- 单边至少假设 `3~6 bps`，不要拿理想费率自我催眠

## 7.2 更 desk-friendly 的两条改写

### 改写 A：把绝对 `$50k` 改成 coin-specific 百分位
直接测：
- `trade_notional >= rolling q99` 或 `q99.5`

好处：
- 避免 BTC/ETH 与小币用同一绝对门槛，导致小币永远没信号。

### 改写 B：把“单 wallet 触发”升级成“群聚冲击分数”
例如：

```text
whale_shock_score
= z(trade_notional_sum_300s_same_side)
+ z(distinct_wallet_count_300s_same_side)
+ z(repeat_wallet_intensity)
- z(opposite_side_rebuttal_60s)
```

这比简单 `convergence>1` 更适合做 cross-asset ranking。

---

## 8. 它最可能怎么失效

要提前诚实。

## 8.1 地址不等于“聪明钱”
有些地址只是内部转移、做市对敲、清算相关流，不是信息交易。
所以钱包分数必须滚动更新，不能迷信固定白名单。

## 8.2 大单打印可能是冲击末端，不是起点
尤其在 memecoin 上，大单常常是最后一脚而不是开始。
所以最好加：
- event 后 `10s/30s/60s` 未被完全反向吞没
- 或价差 / slippage / top-book depletion 约束

## 8.3 组合相关性会让“多币同向开仓”看起来很爽，实际上全是同一笔 beta
repo 用 correlation bucket cap 处理这件事，这是对的。
如果 desk 复现时只看单笔 alpha 而不做组内限额，最后很容易把同一轮市场 beta 当成多次独立胜利。

## 8.4 费率与冲击成本是第一杀手
这种事件驱动 continuation，最怕：
- 你看到时已经晚了
- taker 再 taker 后 edge 被吃光

所以必须区分：
- **信号有无方向性**
- **扣完冲击和手续费后还能不能活**

前者成立，不代表后者成立。

---

## 9. 和当前素材池的关系

这篇最有价值的地方，是它补的是 **“公开身份流 + 大单群聚 continuation”** 这条 raw alpha 分支，而不是继续围绕：

- breakout 形态
- RSI/BB 均值回复
- 传统 pairs z-score
- 单纯 funding / basis carry

它与我们已有材料的关系更像：
- 可与 `liquidation cascade` 方向验证互补
- 可与 `order-flow / imbalance` 做共振评分
- 可与 `funding crowding` 做持仓时长调节

但本体依然是 raw alpha，不是 filter 假装 alpha。

---

## 10. 结论

如果把这份 2026 repo 整体阅读，很容易把注意力放在“多策略 bot”。
但对短周期 desk，真正该先拿走的，是里面 **Whale Tracker** 这一支：

> **公开钱包地址 + 大额 aggressor trade + 5 分钟同向收敛 → 事件驱动 continuation alpha。**

它的优点是：
- 数据公开可拿；
- base alpha 讲得清；
- 与 `1m/3m/5m` 天然匹配；
- repo 已给出最小完整策略壳；
- 可以很快拆成更适合 desk 的 coin-specific / shock-score 版本。

我的判断：
**值得进入复现池，而且优先级不低。**
但第一轮别急着做“盲目 whale 跟单”，而是先把它改写成 **coin-normalized whale shock continuation**，并严格核算 taker cost 与事件后吞没率。

---

## 11. 下一步怎么测（直接执行版）

### Step 1：先做数据层
抓 Hyperliquid 公共 trade stream，持续记录至少 7 天：
- `coin, side, px, sz, time, buyer, seller`
- 生成每币种的 `trade_notional` 分位数
- 生成地址活跃度 / 胜率 / 持续性 proxy

### Step 2：先测最小 raw alpha，不加太多花活
只测：
- `same_side_distinct_whales_300s >= 2`
- `trade_notional >= q99`
- 按事件后 `1m / 3m / 5m / 15m` forward return 分 bucket 看 continuation

### Step 3：再加成本与执行
分三套：
1. signal close-to-mid（理想）
2. taker-on-close
3. maker-entry / taker-exit

### Step 4：最后才加 wallet score
先验证“群聚是否有 edge”，再验证“高分钱包是否进一步抬升 edge”。
不要一上来就做复杂 wallet 评分，把问题搅在一起。

---

## 12. 本文关键信息卡

- **主题类型**：raw alpha
- **基础 alpha**：whale aggressor flow convergence continuation
- **最适合频率**：`1m / 3m / 5m`
- **公开数据源**：Hyperliquid public WebSocket `trades`
- **最小实验**：`>=q99` 大单 + `300s` 同向 distinct-wallet 收敛，对比后续 `1/3/5/15m` continuation
- **本地文件**：`research/quant_digests/2026-04-01_0325_hyperliquid-whale-trade-convergence-alpha.md`
- **live probe artifact**：`reports/artifacts/quant_digests/whale_tracker_liveprobe_20260401_0323/summary.csv`
