# 别把 `liquidation-hunter` 只读成“顺着瀑布追”：对 short-cycle crypto desk，更该先测的是「liquidation shock × OI unwind → 30m exhaustion fade」这条 raw alpha

- 时间：2026-04-18 22:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main.py` + `config.yaml`）+ Binance USDⓈ-M `5m` public-data portability probe（8 majors，近 `14d`）
- 主题类型：raw alpha
- 基础 alpha：**当 `5m` 出现“价格单边急冲 + OI 同步明显回落 + 成交额放大”这类强制去杠杆/挤仓代理事件后，继续追同方向未必划算；更像值得在接下来 `15m~30m` 做反向 exhaustion fade**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（先做单资产事件驱动版，再扩到 cross-sectional router）
- 主题标签：raw-alpha / single-asset / event-driven / liquidation / open-interest / forced-deleveraging / exhaustion / mean-reversion / fade / binance-perpetual / 5m / 15m / 30m / repo / public-data / cost / risk
- 证据类型：仓库规则框架 + 公共 API 最小移植快检

先回答 base alpha：**能答清。**
这次不是把 repo 原样照抄成“追 liquidation cascade continuation”，而是把它拆开后，挑出**更适合我们 desk 的旁支**：

> **极端去杠杆事件本身是 raw alpha 触发器，但在 Binance `5m` 公共数据口径下，它更像 `30m` 内的 exhaustion fade，而不是继续追单边。**

这符合你这轮给的灵活口径：
- 不要求必须复刻仓库 headline；
- 只要 repo / paper 里的某个分支更适合 `1m/3m/5m/15m` 最小实验，就值得单独拎出来；
- 而且这次它依然是 **raw alpha**，不是硬包装成 filter。

---

## 1. 这次看了什么
主来源是一个 2026 新仓库：

- **Authors / Maintainer：** `wilsontiger2222`
- **Year：** 2026
- **Title：** `liquidation-hunter`
- **Venue：** GitHub repository
- **DOI：** 无
- **Readable URL：** <https://github.com/wilsontiger2222/liquidation-hunter>
- **Repo URL：** <https://github.com/wilsontiger2222/liquidation-hunter>
- **实际审计文件：**
  - <https://raw.githubusercontent.com/wilsontiger2222/liquidation-hunter/master/README.md>
  - <https://raw.githubusercontent.com/wilsontiger2222/liquidation-hunter/master/main.py>
  - <https://raw.githubusercontent.com/wilsontiger2222/liquidation-hunter/master/config.yaml>

### 1.1 仓库原始主张
repo 的原始想法很直白：
- funding 很偏；
- OI 在涨、价格却没顺着走；
- 价格靠近 liquidation cluster；
- 那就顺着预期 cascade 方向去追。

它在 `README.md` 里给的是典型 continuation 叙事：
- `funding_rate > threshold`
- `open_interest_delta > X% in last 4h`
- `price approaching liquidation cluster within 1.5%`
- 然后开仓，`TP` 打在 liquidation cluster center，`SL` 紧一些，`timeout` 用分钟数控制。

`main.py` 也说明它不是纯概念 README，而是已经搭了一个可运行骨架：
- funding signal
- OI divergence signal
- liquidation cluster signal
- signal aggregator
- paper / live / alert executor

但我不打算把它原样照抄进 desk，原因很简单：
**repo 里真正最值钱的不是“追瀑布”四个字，而是它提醒你：强制去杠杆本身是一个可以切成不同交易相位的事件源。**

---

## 2. 为什么这轮仍把它定成 raw alpha，而不是 overlay
因为这次研究对象不是“用 liquidation 数据给别的策略做 veto”。
这次真正拿出来测试的 alpha 本体是：

> **当市场刚刚被迫去杠杆、短窗价格走得太急，且 OI 明显同步收缩时，下一段 `15m~30m` 更容易走 exhaustion fade。**

这里的方向信号本身来自事件，不是来自别的母策略，所以它属于 raw alpha。

更具体地说：
- `trigger`：极端 `5m` shock + OI unwind + volume expansion
- `entry`：反向接 event
- `exit`：固定持有 `15m/30m/60m`，或加 price reversion / VWAP 回归条件
- `risk`：shock 延续过深即止损，事件过旧即失效

这已经是一套完整交易语言，不只是风险附属层。

---

## 3. 用人话讲，这个 alpha 在抓什么
如果一个 `5m` bar 同时出现三件事：

1. **价格冲得很急**：说明短时情绪和订单流都极端；
2. **OI 明显下掉**：说明不是“新仓追进去”，而是有人被迫减仓/爆仓/挤出去；
3. **成交额放大**：说明这根 bar 不是冷清时段的假动作，而是真有大量成交换手；

那这更像什么？

更像：
- 一段去杠杆释放已经发生；
- 最容易赚钱的那一段单边，可能已经被吃掉；
- 后面更值得做的，不一定是追，而是等一小段后**反手接回摆**。

翻成人话：

> **不是“看见爆仓就继续追”，而是“看见爆仓 + OI 掉得厉害，就开始怀疑：这波是不是已经把最好赚的那截走完了”。**

这跟单纯看大阴线/大阳线不一样。
多了 `OI unwind` 这层，意思从“价格大动”变成“价格大动，而且伴随仓位被挤掉”。
后者更接近 **forced deleveraging exhaustion**，而不是正常趋势延续。

---

## 4. 最小实验怎么做的
为了先回答“这东西在我们 desk 的 `5m/15m` 口径上像不像样”，我没去追完整 liquidation heatmap，而是先用**Binance 公共可得**的数据做一个最小代理实验。

### 4.1 数据源
全部公开可得，无需私有 key：
- `fapi/v1/klines`：Binance USDⓈ-M `5m` K 线
- `futures/data/openInterestHist`：Binance USDⓈ-M `5m` OI 历史

### 4.2 更新频率
- K 线：`5m`
- OI hist：`5m`

### 4.3 标的
8 个液态主流 perp：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`
- `BNBUSDT`
- `XRPUSDT`
- `DOGEUSDT`
- `ADAUSDT`
- `LINKUSDT`

### 4.4 样本区间
- 近 `14d`
- bar 频率：`5m`

### 4.5 事件定义（当前最小口径）
对每个 symbol 的每根 `5m` bar：
- `abs(ret_5m)` 进入自己过去 288 根（约 1 天）的 **90% 分位以上**；
- `oi_value_chg` 落在过去 288 根的 **20% 分位以下**（也就是 OI value 明显掉）；
- `quote_volume_zscore > 0`（成交额至少高于近期均值）。

满足三条，就把它记成一根 **liquidation-like forced-unwind event**。

我故意先不用“真 liquidation feed”，因为：
- 这轮目标是先做 desk 可快速复现的最小实验；
- Binance 公开 OI + K 线已经足够回答 first verdict；
- 若 first verdict 成立，再接更细的 liquidation heatmap / force-order feed 也不迟。

### 4.6 产物路径
这轮实验文件已经落在：
- `reports/artifacts/quant_digests/2026-04-18_liq_oi_unwind_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_liq_oi_unwind_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_liq_oi_unwind_portfolio.json`

---

## 5. 关键结果：追同方向不太行，30m 反手更像样
先看组合层：

### 5.1 全样本（8 majors，42 个事件）
`portfolio.json` 里的聚合结果：
- 事件数：`42`
- 平均当根 shock：`-16.72 bps`
- 平均 OI value 变化：`-36.18 bps`
- 平均 volume z-score：`2.05`
- **顺着事件方向持有 15m：`+0.99 bps`**
- **顺着事件方向持有 30m：`-13.99 bps`**
- **顺着事件方向持有 60m：`-2.04 bps`**
- 顺势 30m 胜率：`26.2%`

这串数的直译很清楚：

> **事件后立刻再追 15m，几乎没 edge；追 30m 明显偏负。反过来看，就是做 30m exhaustion fade 的 gross first verdict 反而更像样。**

如果把 `signed_30m_bps = -13.99` 翻译成反向交易：
- **fade 30m 的均值约 `+13.99 bps` gross**；
- **fade 30m 胜率约 `73.8%`**。

这已经足够支撑“值得进入研究池继续做 cost-aware 细化”。

### 5.2 上冲事件 vs 下砸事件
把事件拆成上涨挤空和下跌砍多：

#### 上冲事件（12 个）
- 平均当根 shock：`+33.19 bps`
- 平均 OI value 变化：`-23.76 bps`
- 顺势 30m：`-14.74 bps`
- 换成 fade：**`+14.74 bps`**
- fade 30m 胜率：`75%`

#### 下砸事件（30 个）
- 平均当根 shock：`-36.68 bps`
- 平均 OI value 变化：`-41.16 bps`
- 顺势 30m：`-13.70 bps`
- 换成 fade：**`+13.70 bps`**
- fade 30m 胜率：`73.3%`

也就是说：
- 不管是往上挤还是往下踩；
- 只要像 forced-unwind event；
- **30m 维度都更像反手，不像追单边。**

这点对 desk 很有用，因为它把复杂故事压成一句很能执行的话：

> **遇到 OI 掉得快的极端 bar，先别兴奋追方向，先把它当成“去杠杆释放已发生”的 exhaustion 候选。**

### 5.3 单币层不完全一致，但负向追单边是主基调
`summary.csv` 里最有代表性的例子：
- `XRPUSDT all`：顺势 30m `-31.66 bps`
- `ADAUSDT all`：顺势 30m `-31.31 bps`
- `ETHUSDT all`：顺势 30m `-16.08 bps`
- `SOLUSDT all`：顺势 30m `-13.23 bps`
- `BTCUSDT all`：顺势 30m `-19.54 bps`

也有例外：
- `BNBUSDT down`：顺势 30m `+10.96 bps`
- `LINKUSDT up`：顺势 30m `+41.07 bps`

这说明它更像什么？

更像：
- **适合先做 cross-sectional router / symbol veto**；
- 不宜一上来就假设“所有币、所有 shock 都反手”；
- 但作为组合层 first verdict，已经很清楚：**“继续追”不是默认最优。**

---

## 6. 它和当前 `1m / 3m / 5m / 15m` desk 的关系
### 6.1 最自然的主战场是 `5m -> 15m/30m`
这次 public-data 版最顺手的映射是：
- 用 `5m` bar 定义事件；
- 在接下来 `15m` / `30m` 做 fade；
- `60m` 只作为延长持有的参考，不是首选。

所以它跟当前短周期关系最直接的是：
- `5m`：事件探测层
- `15m`：第一阶段均值回摆窗口
- `30m`：当前看起来最像样的 gross pocket

### 6.2 `1m / 3m` 可以怎么接
如果后面补到更细数据：
- `1m` liquidation prints
- 更细 OI snapshot
- order-book refill / spread re-tighten

那可以把当前 `5m` 事件拆成两阶段：
1. `1m/3m` 观察冲击是否已进入衰竭区；
2. `5m` 再正式下 fade。

也就是说，这篇笔记不是只能服务 `5m/15m`，它也能向更快频率扩展，只是当前 first probe 先用 `5m` 做最小可复现实验。

---

## 7. 为什么它比继续补一个纯 filter 更值得
因为这轮我们优先级里，raw alpha 要高于 shared filter / overlay。
而这个主题满足三点：

1. **base alpha 清楚**：forced-unwind exhaustion fade；
2. **公开数据能复现**：Binance `5m` K 线 + OI hist 就能先测；
3. **可以直接落地完整策略**：entry / exit / sizing / risk / cost 都能写清楚。

换句话说，它不是“某条 alpha 的辅助阀门”，而是**事件驱动型均值回归 raw alpha**，而且跟 liquidation / crowding / leverage 这类 crypto 原生结构直接相关，值得进素材池。

---

## 8. 可以直接落地的最小策略草案
下面这版我觉得已经够 desk 化：

### 8.1 事件触发
在 `5m` 上，对候选 universe（先从 8 majors 开始）：
- `abs(ret_5m) >= rolling q90`
- `oi_value_chg <= rolling q20`
- `quote_volume_z >= 0`

### 8.2 方向
- 如果事件 bar 是大涨：做空 fade
- 如果事件 bar 是大跌：做多 fade

### 8.3 入场
先测 3 个版本：
- **A. close-entry**：事件 bar 收盘反手进
- **B. 1-bar delay**：等下一根 `5m` 再进
- **C. micro-confirm**：只有下一根没继续扩张、或已经出现 wick / volume deceleration 才进

### 8.4 出场
先做最简单的固定持有：
- `15m`
- `30m`
- `60m`

目前 first verdict 最优先看 `30m`。

后面再测更实盘化的版本：
- 到达事件 bar 中点/VWAP 回归即止盈
- 若继续沿事件方向扩张 `0.6~0.8 x event_range` 则止损
- 若 `30m` 内未回摆则强平

### 8.5 仓位
- baseline：等权单笔风险
- 进阶：按 `event_abs_ret × oi_drop_strength` 做 scale
- 更保守：只做 top-liquidity symbols，或按 cost bucket 递减

### 8.6 成本
这轮 first probe 还没正式扣交易费和冲击成本，所以现在只能说：
- **gross first verdict 值得继续做**；
- 真正能不能上线，要看 `taker+taker` 还是 `maker+taker` 之后剩多少。

对 8 个 majors 来说：
- 若能做成 `maker in + taker out`，30m pocket 还有希望；
- 若只能双边 taker，部分币可能被吃掉。

---

## 9. 当前这条 alpha 的最大风险
### 9.1 它可能混进“真趋势起点”
不是每次 OI 掉都代表行情结束。
有些时候是：
- 旧仓被清掉；
- 新趋势才刚开始；
- 后面继续单边。

这也是为什么 `BNB`、`LINK` 里还能看到 continuation pocket。

### 9.2 5m OI hist 太粗
我们现在用的是 `5m` OI 历史，不是逐笔 liquidation。
所以它本质是**forced-unwind proxy**，不是精确清算流。
这没问题，但一定要在文档里说清楚，不要装成“真 liquidation 地图策略”。

### 9.3 跨 symbol 异质性明显
从 `summary.csv` 看，币种差异不小。
因此更像：
- 先做 `BTC/ETH/SOL/XRP/ADA` 重点观察；
- 再把 `BNB/LINK` 这类 continuation 例外拿出来单独建 bucket。

---

## 10. 下一步怎么测
这里必须具体，不然这篇 digest 就只是一段观点。

### 10.1 先做 cost-aware 正式回测
目标：确认 30m fade 是否在 majors 上扣费后还站得住。

最小实验：
- universe：先 `BTC/ETH/SOL/XRP/ADA`
- bar：`5m`
- entry：事件 bar close 反手
- exit：`30m` 固定持有
- cost：
  - taker+taker
  - maker+taker
  - 再加 1~2 档额外滑点 stress

输出：
- gross / net mean bps
- win rate
- turnover
- 按 symbol / side / UTC 时段分组

### 10.2 把 event 强度离散化
目标：回答“是不是越像 forced liquidation，fade 越稳”。

把事件按三维强度分 bucket：
- `abs(ret_5m)` 分位
- `oi_drop` 分位
- `volume_z` 分位

看：
- 最极端 decile 是否明显更好；
- 是否存在“太弱没 edge、太强也别追”的甜区。

### 10.3 测 1-bar delay 是否优于当根反手
目标：减少接飞刀。

要比较：
- 事件收盘立即反手
- 延后 1 根 `5m`
- 只在下一根未创新扩张时反手

如果 delay 版只少赚一点均值，却能显著压回撤，那就更接近 production。

### 10.4 接更细的 liquidation / order-book 数据
目标：把“代理事件”升级成更像 crypto 原生结构的版本。

后续可补：
- 交易所 liquidation prints / force-order feed（若可得）
- order-book spread / refill / depth collapse
- funding snapshot

届时把当前 alpha 拆成：
- **raw alpha**：forced-unwind exhaustion fade
- **filter**：book refill / spread normalization / funding crowding

这样会比一上来追求“大而全”更稳。

---

## 11. 结论
这轮最重要的结论不是“liquidation 很重要”这种空话，而是：

> **从 2026 新仓库 `liquidation-hunter` 往 desk 口径重读后，更值得先测的不是 cascade continuation，而是 `5m` 强冲击 + OI unwind 后的 `30m` exhaustion fade。**

当前 public-data first verdict：
- 8 个 majors、近 14 天、42 个事件；
- 顺势追 `30m` 平均 **`-13.99 bps`**，胜率 **`26.2%`**；
- 反过来做 fade，大致是 **`+13.99 bps gross`**，胜率 **`73.8%`**。

所以这轮结论很明确：
- **主题类型：raw alpha**
- **base alpha：forced-unwind exhaustion fade**
- **能独立复现：能**
- **能直接落完整策略：能**

它已经够资格进入后续复现与实盘候选池，但下一步必须尽快补：
- net cost
- symbol bucket
- entry delay
- 更细 liquidation / microstructure confirmation

在这几项没补完前，它是个**值得继续推进的 raw alpha 候选**，但还不该直接当成通杀全币种的 production 默认模板。
