# 别把这份 2026 Polymarket×Deribit 仓只读成“概率计算器”：对 short-cycle desk，更该先拆的是「Deribit 终值概率 vs Polymarket 日度二元价格偏离」这条 relative-value raw alpha

- 时间：2026-04-17 21:14 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `docs/mathematical_theory.md` + `scripts/backtest.py` + `data_collector/collector.py` + `scripts/market_utils.py` + bundled CSV sample/backtest rerun）
- 主题类型：raw alpha
- 基础 alpha：**同一个 BTC 日度终值事件** 在两个公开市场里会被定出不一致的风险中性概率：Deribit 期权面可抽出 `Q(BTC 到期高于某价)`，Polymarket 的 `UP/DOWN` token 直接给出二元事件价格；当两者偏离超过交易成本与滑点，而且 Polymarket 盘口能成交，就做 `long cheap probability / short rich probability` 的跨 venue relative-value / stat-arb。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / prediction-market / options / relative-value / stat-arb / cross-venue / digital-probability / polymarket / deribit / btc / 1m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + repo bundled data rerun + public API 可得性审计

## 1. 这次看了什么
- **Author / Maintainer**：`djienne`（GitHub）
- **Year**：2026
- **Title**：`POLYMARKET_UP_DOWN_DERIBIT_STRATEGY`
- **Venue / Type**：GitHub repo
- **Readable URL**：<https://github.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY>
- **Repo URL**：<https://github.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY>
- **Repo metadata**：创建于 `2026-02-11`，最近更新 `2026-04-17`，当前 `18` stars

先把 **base alpha** 说清楚：

> **不是“Deribit 能不能预测 BTC 方向”本身，而是“Deribit 期权面抽出来的风险中性终值概率”和“Polymarket 同一终值事件的二元市场价格”之间，是否会出现可交易的跨 venue 概率错价。**

这就是一条标准的 `relative-value / stat-arb / raw alpha`：
- 交易对象不是裸 BTC 方向；
- 交易对象也不是单边 options carry；
- 交易对象是 **同一事件概率在两个市场里的价差**。

对当前 desk 来说，这个主题值钱的地方在于：
1. 它补的是最近 digest 相对少见的 **prediction-market × options** 交叉资产层；
2. 它不是纯解释型 overlay，而是能明确写出 `entry / exit / cost / latency / sizing` 的完整壳；
3. 它虽然事件到期是“日度”，但 **信号刷新与订单簿刷新** 明确能映射到 `1m / 5m / 15m` 的短周期研究节奏。

## 2. repo 里真正可继承的 alpha 是什么
### 2.1 用人话翻译整个机制
repo 做的事情并不神秘，可以压缩成三步：

1. 去 Deribit 抓 BTC 期权链，拟合波动率曲面；
2. 从曲面里抽出 **BTC 到某个未来时点高于 / 低于某个参考价** 的风险中性概率；
3. 去 Polymarket 找当天对应的 BTC `UP / DOWN` 市场，比较市场价格和模型概率，若有足够 edge 就交易。

所以它的交易本体不是“看涨/看跌 BTC”，而是：

> **比较 Deribit 的数字期权隐含概率，与 Polymarket 的 YES/NO token 价格有没有错位。**

这本质上和我们之前做过的：
- funding spread,
- basis dislocation,
- same-underlier spread fade,
- lead-lag catch-up

属于同一大类：**同一底层经济对象，在两个定价层之间是否脱节。**

### 2.2 为什么它算 raw alpha，不是 filter
因为这里的信号本体就是：
- `model_prob_up` vs `poly_prob_up`
- `model_prob_down` vs `poly_prob_down`
- 进一步压缩成 `edge_up = model / market`、`edge_down = model / market`

只要边际收益大于：
- Polymarket 买卖价差
- 手续费 / 摩擦
- 延迟造成的 stale quote 风险

这就是可以单独交易的一条 alpha，不依附于别的方向信号。

## 3. 代码里最关键的可落地结构
### 3.1 repo 明确把“概率错价”写成可回放的数据流
`data_collector/collector.py` 里，作者没有停留在 notebook 级 demo，而是把 live 数据流拆成三条：

- **Probabilities**：每 `5` 分钟跑一次模型，产出 `model_prob_up/down`、`poly_prob_up/down`、`edge_up/down`
- **Orderbook**：每 `1` 分钟抓一次 Polymarket CLOB 最优 bid/ask
- **Deribit options**：每 `5` 分钟抓一次完整 BTC options chain

这三条流刚好对应 desk 最关心的三件事：
1. 你到底有没有 alpha；
2. 你能不能成交；
3. 你的 alpha 来源有没有被 options surface 本身推翻。

### 3.2 repo 已经给出了完整的 entry 语言
`scripts/backtest.py` 的核心不是简单比较概率差，而是直接围绕“能否下单”写：

- 从 `probabilities.csv` 读取 `model_prob` / `poly_prob` / `edge`
- 从 `orderbook.csv` 读取当时真实可成交的 bid/ask
- 进场优先用 orderbook ask，而不是用理论概率代替成交价
- 支持：
  - `take profit`
  - `trailing stop`
  - `stop loss`
  - `latency_minutes`
  - `friction`
  - `min_time_remaining_hours`
  - `position sizing`

这点很关键：

> 很多 repo 只证明“模型概率”和“市场概率”有差；这份 repo 则往前走了一步，开始问“如果真按盘口成交，这个差还能剩多少”。

### 3.3 它把 base alpha 写得非常“desk 化”
repo 不是拿绝对价差，而是用比率：
- `edge_up = model_prob_up / poly_prob_up`
- `edge_down = model_prob_down / poly_prob_down`

这样做的好处是：
- `0.10` 对 `0.15` 和 `0.60` 对 `0.65` 的经济意义不同；
- 用比率更容易表达“市场低估了多少概率”；
- 更适合后面做连续型 threshold / ranking / sizing。

## 4. 对 short-cycle desk 最有价值的不是“模型多高级”，而是“跨市场错价”
repo README 和数学文档里最显眼的是：
- SSVI
- Breeden-Litzenberger
- Monte Carlo
- Heston fallback

这些当然重要，但对我们 desk 真正值钱的不是“曲面拟合本身”，而是：

> **Deribit 期权面已经把 BTC 某个日终事件怎么定价写出来了；Polymarket 则把同一事件重新报价了一遍。**

只要这两边的语言能对齐，这就是一条很像数字期权 / 预测市场之间的 stat-arb 线。

换句话说，repo headline 看起来像“概率计算器”，但对我们更重要的读法是：
- **Deribit = 更连续、更成熟的概率曲线**
- **Polymarket = 更离散、更容易短暂失真的事件盘口**

当两者不同步，就有原材料可拆。

## 5. 本轮最小证据：repo bundled 数据足以证明它不是空故事
我没有把它当成“README 讲得好听”就收录，而是把 repo 拉到本地，直接重跑它自带的数据样本。

### 5.1 bundled 数据覆盖了真实的短周期采集节奏
repo 自带：
- `data_collector/results/probabilities.csv`
- `data_collector/results/orderbook.csv`

从样本里读到：
- `probabilities.csv` 共 **456** 条记录
- 覆盖 **7** 个不同日度 barrier/market
- 时间范围约为 **2026-03-03 ~ 2026-03-08**
- `orderbook.csv` 共 **932** 条 orderbook 快照
- Polymarket top-book spread 中位数约 **$0.01**，`p90` 约 **$0.02`

人话：
> 它不是只抓了一两次 snapshot 来讲故事，而是真的按分钟级、五分钟级连续采样过一段时间。

### 5.2 按 README 给的参数重跑 backtest，结果说明“是 alpha 壳，不是现成印钞机”
我直接用 repo README 里的示例参数重跑：
- `alpha-up = 2.40`
- `alpha-down = 1.80`
- `floor-up = floor-down = 0.35`
- `tp = 0.40`
- `trail-activation = 0.20`
- `trail-distance = 0.15`
- 默认 `latency = 2 min`
- 默认 `friction = 1.5% per side`

回放结果：
- 总交易数：**5**
- 胜率：**80%**
- `TP` 命中：**2**
- `trailing stop`：**1**
- 到期赢：**1**
- 到期亏：**1**
- 最终资本：**$98.83**（从 `$100` 起）
- 总收益：**-1.2%**

这组数字怎么解读最合理？

不是说“这条线没用”，而是说：
1. repo 的 **base alpha 真存在**，因为确实会触发、确实能在盘口上成交、也确实出现盈利单；
2. 但当前 bundled 样本还不足以证明参数已经 production-ready；
3. 它更像一条 **明确可复现、但阈值和风险壳仍需重新调参** 的完整策略母板。

### 5.3 当前样本显示：这条 repo 更偏 `DOWN` 侧 pocket，而不是上下对称
我顺手扫了 bundled `edge` 分布：
- 在 README 这套门槛下，`UP` 侧基本 **没有有效信号行**
- `DOWN` 侧能触发的信号行大约 **4** 次
- 所有实际交易也全部发生在 `DOWN` token 这一侧

这很像什么？

> **Polymarket 的 BTC 日度二元市场，在 repo 当前样本里，更常见的是“下跌概率被低估”而不是“上涨概率被低估”。**

这不一定是长期真理，但它给 desk 一个很重要的 first verdict：
- 别先假设这条 alpha 多空对称；
- 第一轮 follow-up 应该先把它当 **downside event-probability mispricing** 来测。

## 6. 它和 `1m / 5m / 15m` 的关系怎么理解
很多人一看到“到期事件概率”就会误以为这是低频题。

其实不对。更准确的理解是：

- **事件结算频率**：日度
- **信号刷新频率**：`1m` orderbook + `5m` model refresh
- **执行与风控频率**：完全可以放在 `1m / 5m / 15m`

所以对 short-cycle desk：
- `1m`：抓 Polymarket 盘口是否 stale、是否有 micro-jump、是否已经被吃掉
- `5m`：重算 Deribit-implied probability，形成主信号
- `15m`：做 time-stop / regime hold / risk review

也就是说：

> 这不是“逐 bar 预测 BTC return”的 alpha，而是“逐分钟检查同一事件概率有没有被错价”的 alpha。 

这仍然完全服务于短周期量化研发。

## 7. 为什么这条线比再补一个普通 filter 更值得
因为它直接服务于当前 desk 的原材料池扩容：

1. **raw alpha 属性明确**：不是附属 filter，而是可单独开仓的概率错价；
2. **公开数据可拿**：Deribit public API + Polymarket public API/CLOB；
3. **结构上可迁移**：今天是 BTC daily `UP/DOWN`，后面也可扩到别的事件市场；
4. **天然带 execution 研究价值**：这种题目不会停留在“算一个指标”，而会逼你正视 latency、book depth、quote decay。

对于 desk 来说，这类主题比再加一个“解释为什么趋势更强/更弱”的 filter 更像真正的新素材。

## 8. 这条线今天就能怎么写成完整策略
### 8.1 Entry
最小版本可以直接这样写：

1. 每 `5m` 重算一次 `model_prob_up/down`
2. 每 `1m` 刷一次 Polymarket bid/ask
3. 对 `UP` 和 `DOWN` 分别算：
   - `edge_ratio = model_prob / market_ask_prob`
   - `edge_bps = model_prob - market_ask_prob - friction_buffer`
4. 只有当以下同时满足时进场：
   - `edge_ratio >= threshold`
   - `edge_bps >= min_abs_gap`
   - `time_remaining_hours >= 2`
   - orderbook spread <= 上限
   - best ask size >= 最小成交量
   - 模型最近一次拟合质量达标（如 SSVI/Heston 标志正常）

### 8.2 Exit
至少三种 exit 必须一起存在：

1. **Edge close**：`model_prob - market_mid` 回落到近 `0`
2. **Time stop**：离结算越近，若 edge 不再扩张就强制平
3. **Book deterioration**：盘口 spread 扩大或挂单深度掉太多，提前撤退

repo 已经给了：
- fixed TP
- trailing stop
- stop loss
- expiry settlement

我们真正要补的是：
- **event-time decay aware exit**
- **stale-quote 失效退出**
- **模型质量异常退出**

### 8.3 Sizing
别直接按“账户百分比”无脑下，先做两层：

- **per-trade notionals**：单笔不超过当时 top-book 可吃量的一定比例
- **per-day event cap**：同一市场同一天不做过多翻手，避免被 prediction market 的薄 book 把 edge 吃没

### 8.4 Cost
这类 alpha 的核心不是手续费，而是：
- 买到的 ask 是否 stale
- 平仓能否回到 bid
- 中间 book 是否迅速收敛

所以成本模型至少要拆成：
1. 显式手续费；
2. bid/ask spread；
3. 1~2 分钟 latency slippage；
4. 一边成交、另一边没成交的 quote drift 风险。

## 9. 风险与保留意见
### 9.1 repo 的“概率模型强”不等于真实世界一定有 alpha
Deribit 抽出来的是 **风险中性概率**，不是物理世界概率；
Polymarket token 里还会混入：
- 平台摩擦
- 用户结构偏差
- event microstructure 噪声

所以这条线真正赚的不是“预测未来”，而是：

> **两个市场对同一事件的风险中性定价暂时不同步。**

### 9.2 bundled 样本不够大
当前 only：
- 7 个 market
- 5 笔交易

足够证明“能交易、能回放、不是空壳”，但远远不够给 production verdict。

### 9.3 它本质上是跨 venue 盘口策略
这意味着两个主要死法：
1. 你看到 edge 时，Polymarket 盘口已经变了；
2. 你只能在 Polymarket 这一端成交，但 Deribit 概率那边并没有真正给出足够稳定的偏离。

所以 follow-up 的重点不该再是“换个更 fancy 的 vol 模型”，而是 **验证 edge 的可成交寿命**。

## 10. 下一步怎么测（这一段最重要）
### A. 先做 `1m book-age / edge half-life` 研究
直接把 repo 的 collector 再扩一列：
- `edge_at_t`
- `edge_at_t+1m`
- `edge_at_t+2m`
- `fillable_size`

先回答一个很现实的问题：

> **有 edge 的时候，它能活几分钟？**

如果 `1m` 内就基本消失，这条线就更像 automation / low-latency pocket；如果能活到 `5m`，就很适合 desk 当前节奏。

### B. 先聚焦 `DOWN` 侧，不要多空对称浪费样本
当前 bundled evidence 已经提示：
- `DOWN` 侧比 `UP` 侧更像有效 pocket

所以下一轮不要平均分配注意力，优先测：
- `DOWN market only`
- `UP/DOWN asymmetric threshold`
- `edge_down` 的 rank / threshold / persistence

### C. 做“模型 edge × 盘口质量”双阈值，而不是只看概率差
最小实验矩阵：
1. `edge_ratio` 阈值：`1.05 / 1.10 / 1.15 / 1.20`
2. `spread` 上限：`1c / 2c / 3c`
3. `latency`：`0 / 1 / 2 / 5 min`
4. `time-to-expiry`：`>2h / >4h / >8h`
5. 输出：`trade_count / fillability / gross / net / half-life`

### D. 明确 desk 版最小实盘壳
建议先做：
- `5m` 模型刷新
- `1m` 盘口轮询
- `15m` 风控 review
- 只做 BTC daily `DOWN`
- 只在 `edge_ratio >= 1.1` 且 `spread <= 2c` 时下单
- `2h` time-stop + `edge_close` 联合退出

如果这套最小壳都站不住，再谈更复杂的 surface 细节没有意义。

## 11. 和当前研究池的关系
这条线最像是对以下方向的补充，而不是替代：
- funding / basis relative-value
- pairs / stat-arb
- prediction-market stale quote
- options-implied event pricing

一句话总结：

> **它把“同一经济事件的跨市场错价”从 funding/basis 空间，扩展到了 Deribit digital-probability vs Polymarket binary-price 空间。**

这就是它进入研究池的理由。

## 12. 来源
1. GitHub repo：`djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY`  
   <https://github.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY>
2. README 直链：  
   <https://raw.githubusercontent.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY/main/README.md>
3. Mathematical theory：  
   <https://raw.githubusercontent.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY/main/docs/mathematical_theory.md>
4. Backtest script：  
   <https://raw.githubusercontent.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY/main/scripts/backtest.py>
5. Collector script：  
   <https://raw.githubusercontent.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY/main/data_collector/collector.py>
6. Market utils：  
   <https://raw.githubusercontent.com/djienne/POLYMARKET_UP_DOWN_DERIBIT_STRATEGY/main/scripts/market_utils.py>
7. Repo bundled data（路径说明）：
   - `data_collector/results/probabilities.csv`
   - `data_collector/results/orderbook.csv`
