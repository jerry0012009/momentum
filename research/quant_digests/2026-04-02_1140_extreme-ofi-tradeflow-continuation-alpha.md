# 别把 OFI 只放进 HFT 教科书：对 crypto short-cycle desk，更该先测的是「extreme trade-flow z-score × next-5m continuation」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：**同一标的的极端订单流不平衡（trade-flow / OFI proxy）会在极短时间内继续推着价格走一小段**；翻成人话，就是“如果这一分钟里主动买盘/卖盘明显失衡，接下来几分钟价格往往还会顺着冲一下”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-02 11:40 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `Order_Flow_Imbalance.ipynb`）+ 2014 *Journal of Financial Econometrics* 微观结构经典论文 grounding + Binance USDⓈ-M `1m` public taker-flow proxy 最小快检
- 主题标签：raw-alpha/microstructure/ofi/order-flow-imbalance/trade-flow/continuation/single-asset/binance/okx/btc/eth/sol/1m/3m/5m/15m/repo/paper/public-data/cost/execution
- 证据类型：repo-first（raw alpha 明确）+ classic-paper grounding + public-data portability probe

## 1. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：极端订单流失衡 → 极短期价格延续。**

不是“盘口很热闹”这种解释性结论；真正能交易的是：

> **把一段很短时间里的 signed trade flow 做标准化，只有在失衡足够极端时才顺着做，赌接下来 `1s ~ 5m` 还有 residual continuation。**

所以这轮它属于 **raw alpha**，不是 filter / regime / overlay。

---

## 2. 为什么这轮值得写它
最近 digest 池里已经有：
- cross-asset lead-lag OFI
- maker / inventory skew
- pairs / residual mean reversion
- binary market / funding / basis

但 **“同一标的自身 trade-flow 失衡 → 后续几分钟 continuation”** 这条最朴素、最底层的 microstructure raw alpha，反而没有单独写成一篇 repo-first digest。

这轮值得 intake 的原因有四个：

1. **raw alpha 本体很清楚。**
   - 不是拿 OFI 去给别的策略当 confirmation；
   - 它自己就能独立下单。
2. **能直接服务 `1m / 3m / 5m` 高强度实验。**
   - 这比很多慢频论文更容易当周做完最小实验。
3. **repo 里已经把“信号 → threshold → accounting → inventory cap”串起来了。**
   - 虽然原版还不够上桌，但不是只给一张相关性图。
4. **它能给现有 desk 一个很实用的底层组件。**
   - 可单独做 alpha；
   - 也可给 breakout / lead-lag / execution veto 提供 microstructure admission layer。

如果问：**它为什么比继续补一个 filter 更值得？**
答案是：
**因为它本身就是一条可下注的 raw alpha，不是门卫。**

---

## 3. 这次看的主来源

### 3.1 主来源：2026 新 repo（主）
- **Author / Year**: Grant Reed, 2026
- **Title**: *Testing Order Flow Imbalance in Bitcoin Markets*
- **Venue**: GitHub repository / notebook research project
- **DOI**: N/A
- **Readable URL**: https://github.com/grantreed1/Crypto-Order-Flow-Imbalance
- **Repo URL**: https://github.com/grantreed1/Crypto-Order-Flow-Imbalance
- **实际看的文件**:
  - `README.md`
  - `Order_Flow_Imbalance.ipynb`

### 3.2 理论地基：经典微观结构论文（辅）
- **Authors / Year**: Rama Cont, Arseniy Kukanov, Sasha Stoikov, 2014
- **Title**: *The Price Impact of Order Book Events*
- **Venue**: *Journal of Financial Econometrics*
- **DOI**: `10.1093/jjfinec/nbt003`
- **Readable URL**: https://doi.org/10.1093/jjfinec/nbt003
- **Repo URL**: N/A

### 3.3 最小 portability probe 数据源（公开可得）
- **Venue**: Binance USDⓈ-M Futures public kline API
- **Readable URL**: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
- **公开性**: 全公开
- **更新频率**: `1m`
- **可映射周期**: `1m / 3m / 5m / 15m`

---

## 4. repo 里最值钱的，不是“OFI”这个词，而是它把 raw alpha 壳子跑通了
这份 repo 的价值，不在“又一个 microstructure 名词”，而在它把一条基础但真实的 raw alpha 链条写出来了：

1. **把 trade side 变成 signed quantity**
2. **按极短窗口累积 trade flow**
3. **winsorize 掉极端大单噪音**
4. **rolling z-score 标准化**
5. **回归到 forward return 上估 beta**
6. **只在预测收益超过动态阈值 `j` 时交易**
7. **做 inventory-capped accounting**

翻成人话：
**它不是“看到买盘多就机械追”；而是先把极短期买卖失衡转成 standardized signal，只在最极端一小撮时刻顺着打。**

这就让它和“泛泛而谈订单簿压力”的材料不一样——它已经有了一个最小可交易外壳。

---

## 5. 代码级拆解：这条 alpha 在 repo 里怎么成型

### 5.1 数据层：六个 venue，2025-05，超过 2100 万条 trade
notebook 用的是 **2025-05 的 BTC-USDT trade 数据**，跨：
- `OKX`
- `GATE_IO`
- `COINBASE`
- `DERIBIT`
- `BITSTAMP`
- `BINANCE`

关键数：
- 总 trade 条数：**21,295,823**
- OKX 量占比：**64.90%**
- GATE_IO 量占比：**29.09%**
- Binance 样本只有 **1 天**，但仍有数百万笔顺序交易

Deribit 还专门做了合约单位归一：
- inverse futures 按 `$10 / contract` 折算成 BTC 数量

这一步很重要：
**作者不是在抽象讨论 OFI，而是在处理真实 venue 数据口径差异。**

### 5.2 特征层：trade-flow 而不是整本 order book 事件流
预处理函数 `preprocess_data()` 的核心是：

- `signed_qty = +qty / -qty`
- 在 `tau_str` 窗口上滚动求和，得到 `trade_flow_raw`
- 对 raw flow 做 **1% / 99% winsorization**
- 再用 **100 个 rolling window** 算 z-score

repo 默认起点：
- `tau = 100ms`

但后面 sweep 说明：
- **太短的 tau 很容易被噪音打爆**
- 真正像样的是把 flow 聚合到更宽的几秒级窗口

也就是说，这条线真正可用的不是“tick 级有神奇预测力”，而是：
**持续几秒的同向 aggressor flow 才更像可交易压力。**

### 5.3 目标层：直接回归 forward return
`generate_signals()` 做的不是分类器，而是最朴素的一条线：

- 先算 future price
- 目标是 `forward_return`
- 训练 / 测试按时间顺序 **40% / 60%** 切分
- 用 **LinearRegression** 拟合 `trade_flow -> forward_return`
- 得到 beta 后，在 OOS test set 上预测 `predicted_return`
- 只在 `|predicted_return| > j_threshold` 时交易

动态阈值 `j_threshold` 的设计很关键：
- 它不是固定 bps 门槛；
- 而是按 predicted return 的绝对值分位数，控制 target participation。

翻成人话：
**不是每个 OFI 都追，只追最极端那一层。**

### 5.4 accounting 层：repo 已经承认 inventory 才是真问题
`calculate_accounting()` 的核心假设：
- 每次按 `sign(predicted_return)` 决定买卖
- 默认 transaction cost：**0.5 bps / transaction**（`0.00005`）
- 有 `max_inventory_limit = 10`

这个 accounting engine 暴露出一件很真实的事：

> **entry alpha 不是主要问题；真正的问题是没有 exit logic 时，inventory 会把你拖死。**

也就是说，这份 repo 的研究价值不是“已经可上线”，而是它把最该解决的失败点明牌写出来了。

---

## 6. notebook 里最有信息量的结果

### 6.1 participation sweep：极端太稀、太宽又滥，适中的参与率更好
在 OKX 上，作者先用：
- `tau = 100ms`
- `T = 1s`

得到：

| target participation | threshold j | Net P&L |
|---|---:|---:|
| 0.5% | 0.0148% | **-$134,138** |
| 1% | 0.0122% | **-$518,880** |
| 5% | 0.0074% | **-$43,734** |
| 10% | 0.0055% | **+$393,253** |
| 20% | 0.0034% | **+$471,709** |

这组结果说明：
- 极端中的极端并不一定最好；
- 太窄会把样本量压没；
- 适度放宽到 **10%~20% participation**，反而更稳定。

### 6.2 tau sweep：几百毫秒太噪，几秒级 flow 才像东西
在 OKX 上扫 `tau`：

| tau | Net P&L | Trades |
|---|---:|---:|
| 10ms | **-$168,338** | 26,331 |
| 50ms | **-$192,390** | 26,462 |
| 100ms | **-$43,734** | 26,597 |
| 500ms | **+$125,136** | 25,763 |
| 1s | **+$57,690** | 25,782 |
| 5s | **+$382,660** | 22,657 |
| 10s | **+$254,259** | 21,781 |

这基本把 desk translation 说透了：
**真正值得试的不是超短 `10~100ms` 噪音 OFI，而是 `500ms ~ 5s` 这种“持续性 aggressor pressure”。**

### 6.3 horizon sweep：1 秒还有 edge，5 秒以后衰减很快
在最优 `tau = 5s` 下，扫预测 horizon：

| horizon | Net P&L | Avg P&L / Trade |
|---|---:|---:|
| 1s | **+$382,660** | **+$16.89** |
| 5s | **-$284,294** | **-$15.89** |
| 10s | **-$300,427** | **-$16.04** |
| 30s | **-$156,212** | **-$17.02** |
| 60s | **-$239,863** | **-$18.74** |

核心结论非常直接：
**原版信号的预测力几乎只活在最前面的极短一小段。**

这就是为什么它适合被 desk 改写成：
- `1m` 上形成 signal；
- `3m / 5m` 上做 sparse hold；
- 而不是拿去做 15m 大级别主趋势壳。

### 6.4 cross-venue：只有 OKX 真正赚钱，Binance 勉强为正，其余全亏
在“golden config”下（`tau=5s`, `T=1s`, participation `15%`）：

| Exchange | Beta | Trades | Participation | Net P&L |
|---|---:|---:|---:|---:|
| OKX | 0.000023 | 75,513 | 12.59% | **+$575,712** |
| GATE_IO | 0.000032 | 84,462 | 14.08% | **-$89,412** |
| COINBASE | 0.000034 | 40,177 | 14.75% | **-$150,631** |
| DERIBIT | 0.000011 | 3,803 | 10.23% | **-$5,629** |
| BITSTAMP | 0.000057 | 614 | 14.91% | **-$401,670** |
| BINANCE | 0.000021 | 79,043 | 13.17% | **+$7,119** |

这说明：
**这条 alpha 明显有 venue-specific microstructure 依赖。**

如果硬把 OKX 参数无脑平移到所有 venue，基本就是 overfit 自杀。

### 6.5 beta stability：高流动 venue 稳，稀疏 venue 飘
notebook 的 beta stability 分析显示：
- Binance variation：**3.0%**
- OKX variation：**8.6%**
- GATE_IO variation：**9.4%**
- Coinbase variation：**12.1%**
- Deribit variation：**63.4%**
- Bitstamp variation：**95.9%**

所以这条线不是完全 statistical fluke；
但它要求：
- **高流动**
- **连续成交**
- **稳定 trade-flow 结构**

低流动场景下，beta 会直接漂掉。

---

## 7. 最大的问题不在 alpha，而在 exit / inventory / scaling
repo 自己已经把最危险的点写得很清楚。

### 7.1 capped 版本也不算舒服
OKX capped 版本：
- Gross P&L：**+$585,392**
- Net P&L：**+$575,712**
- Fees：**$9,680**
- Max Drawdown：**-$1,245,464**

也就是说：
**赚了 57.6 万，但最大回撤 124.5 万。**

这不是 production-ready，只能算“entry alpha 有东西，但持仓管理很烂”。

### 7.2 去掉库存上限会直接炸穿
OKX capped vs uncapped：

| Metric | Capped | Uncapped |
|---|---:|---:|
| Executed trades | 75,513 | 90,000 |
| Final inventory | 8.75 BTC | **643.06 BTC** |
| Net P&L | +575,712 | +785,718 |
| Max Drawdown | **-1.25M** | **-62.39M** |
| Fees | 9,679.71 | 13,777.01 |

这组数字的意义很简单：
**别被更高的 net P&L 骗了；uncapped 版本本质上是拿方向性爆仓风险换出来的。**

所以对 desk 而言，这篇材料最重要的 take-away 不是“OFI 好厉害”，而是：

> **OFI entry 可以进研究池，但必须立刻和 inventory cap、timeout exit、re-entry cooldown 一起测。**

---

## 8. 我补的 Binance public 最小快检：这条线搬到 `1m / 3m / 5m` 后，只有“极端那一层”还有点像样
为了避免这轮变成纯 notebook 摘抄，我补了一版 **公开可得的 desk-portability probe**。

### 8.1 实验口径（简化，不是严格复现）
- 数据源：Binance USDⓈ-M public `1m` klines
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 样本：各自最近 **1500 根 `1m` bar**
- OFI proxy：
  - `imbalance_ratio = (2 * taker_buy_base_volume - total_volume) / total_volume`
- 标准化：
  - rolling **30-bar z-score**
- 交易规则：
  - `z > threshold` 做多
  - `z < -threshold` 做空
  - 否则空仓
- 评估：看 `next 1m / 3m / 5m / 15m` signed return

> 这不是 trade-level OFI replication；它更像“公开 1m 数据能不能先看到影子”的 portability probe。

### 8.2 最有信息量的结果
把三个标的合在一起看：

#### threshold = 1.5
- active ratio：**12.9%**
- next-1m gross：**-0.14 bps**
- next-3m gross：**+0.23 bps**
- next-5m gross：**+1.74 bps**
- next-15m gross：**-0.90 bps**

#### threshold = 2.0
- active ratio：**2.9%**
- next-1m gross：**+0.99 bps**
- next-3m gross：**+0.84 bps**
- next-5m gross：**+3.99 bps**
- next-15m gross：**+2.74 bps**

按单币看，在 `threshold = 1.5` 下：
- ETH next-5m：**+2.47 bps**
- SOL next-5m：**+2.96 bps**
- BTC next-5m：**-0.17 bps**

### 8.3 这组数字说明什么
说明三件事：

1. **raw alpha 在公开粗粒度数据上不是完全消失。**
   - 极端 taker-flow 之后，`3m ~ 5m` 仍能看到一点 continuation 影子。
2. **只有最极端一层才值得继续测。**
   - `threshold = 2.0` 时虽然样本变少，但 gross 才开始接近可讨论区间。
3. **它非常吃 execution。**
   - 如果按粗略 **4 bps round-trip taker** 去想，`threshold = 2.0` 的 next-5m **+3.99 bps gross** 基本只是贴着 breakeven。

所以，这条线更像：
- maker / passive / hybrid 执行有戏；
- 粗暴 taker 很容易被成本吃平。

---

## 9. 对当前 desk，更合理的读法是什么
这篇材料最容易被误读成：
- “哦，OFI 能预测价格，那就直接追。”

更合理的 desk 读法其实是：

### 9.1 它是 raw alpha，不是 filter
因为入场逻辑本身已经闭环：
- 观测 trade-flow 失衡
- 标准化
- 只有极端事件触发
- 直接下注后续 continuation

### 9.2 但 repo 原版不是完整策略
为什么顶部字段我写“**不可直接落地完整策略**”？
因为它至少缺三件 production 必需品：
1. **明确 exit**
2. **re-entry / cooldown**
3. **更真实的交易成本与滑点**

所以它当前更像：
**清楚、可复现、值得继续 desk 化的 raw alpha 壳子。**

### 9.3 对 `1m / 3m / 5m / 15m` 的映射
- **1m**：适合做 signal formation / admission
- **3m / 5m**：最值得先测 hold horizon
- **15m**：更像 filter 或 upper-layer aggregation，不像原生主壳

也就是说：
**别把它当 15m 主信号；把它当 1m 生成、3~5m 兑现的 microstructure impulse，更合理。**

---

## 10. 如果把它改成 desk 版，应该怎么补全 entry / exit / sizing / risk / cost

### 10.1 Entry
第一版建议：
- universe：`BTC / ETH / SOL / BNB` 起步
- 用真实 trade data 时：
  - `tau = 1s / 3s / 5s`
- 用公开 1m bar proxy 时：
  - `zscore window = 30 / 60`
- 只在 `|z| >= 2.0` 时入场
- 信号方向跟随 OFI 方向

### 10.2 Exit
别用 repo 的“没反向就一直扛”。
第一版应该直接测：
- fixed holding：`1 / 3 / 5 bars`
- timeout exit：最多持有 `5m`
- signal decay exit：`|z| < 0.5` 提前平
- 默认 **不 instant flip**，先 flat 再等下一次 admission

### 10.3 Sizing
- 单次风险仓位按近端 realized vol 缩放
- 单币 gross cap
- 组合 gross cap
- 连续同向触发不要线性加码，最多做一层 pyramiding 或完全禁加码

### 10.4 Risk
- inventory cap 必做
- 连续亏损 / 连续高波动时做 kill-switch
- 当 bar spread proxy / trade count 太差时 veto
- 对 BTC / ETH 和小币分开参数，不要共用一套阈值

### 10.5 Cost
至少做三档：
1. **maker optimistic**
2. **hybrid realistic**
3. **taker pessimistic**

这条 alpha 的生死线基本不在信号，而在成本。

---

## 11. 它和现有素材池的关系
这条线最有价值的地方，在于它能补现有池子的一个底层层级：

- `cross-asset lead-lag OFI`：看 leader 的 flow 去打 follower
- `order-book delta vote`：看多源 microstructure 共振
- `this digest`：**直接看单标的自身 extreme trade-flow continuation**

所以它不是前两篇的重复，而更像更底层的 building block：

> **先确认“自身流动性冲击有没有短延续”，再决定是否叠加跨资产 lead-lag、盘口结构或执行层 veto。**

这对 desk 很重要，因为它能回答一句基础问题：
**我们看到的 microstructure alpha，到底是“本币自身冲击”还是“跨币传播”的次级反应？**

---

## 12. 一句话结论
如果只带走一句话，我会带走这句：

**别把 OFI 只放进 HFT 教科书；对 crypto short-cycle desk，更该先测的是「极端 trade-flow z-score 触发后的 3~5 分钟 continuation」这条最朴素的 microstructure raw alpha。**

它的优点是：
- base alpha 清楚；
- 独立可复现；
- 和 `1m / 3m / 5m` desk 直接相连。

它的现实约束也同样清楚：
- **repo 原版 exit 太差；**
- **inventory 风险巨大；**
- **execution / cost 很可能比 signal 本身更关键。**

所以它该进研究池，但应以：
**extreme-only + timeout exit + strict inventory cap + realistic cost ladder**
继续推进，而不是把 notebook 原样当答案。

---

## 13. 下一步怎么测（直接执行版）
1. **先做真实 trade-level `1s / 3s / 5s` OFI 复现**：只跑 `BTC / ETH / SOL`，不要一上来全市场。
2. **把 exit 明确化**：扫 `hold 1 / 3 / 5m`、`|z|` 回落平仓、`timeout exit` 三套。
3. **把 threshold 做 sparse 化**：优先测 `|z| >= 2.0 / 2.5`，不要让 active ratio 超过 `3%~8%`。
4. **把成本从第一天就写进实验**：maker / hybrid / taker 三档；如果 taker 全死，别硬说能做。
5. **分币种测 portability**：BTC、ETH、SOL 分开回测，别假设同一阈值通吃。
6. **把它接到现有 lead-lag 研究上**：先测 own-flow alpha，再测“只有 own-flow 和 cross-asset flow 同向时才放行”的组合版本。

---

## 14. 文件信息
- 文件路径：`research/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.html`
