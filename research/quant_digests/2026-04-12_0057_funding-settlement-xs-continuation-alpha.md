# 别把这份 2026 GitHub funding-boundary repo 只读成 latency benchmark：对 short-cycle desk，更该先测的是「funding rank dispersion × settlement-bar continuation（long high / short low）」这条 raw alpha

- 时间：2026-04-12 00:57 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `streams.py` + `main.py` + `analyze_latency.py` + `short_order.py`）+ Binance USDⓈ-M `fundingRate / 5m / 15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**在 funding 结算边界，横截面上“更贵”的 perp（更高 funding）会在接下来一个 `5m/15m` bar 里继续相对跑赢“更便宜”的 perp（更低 funding）；更适合 desk 的第一落点不是单币追单，而是 `long highest-funding bucket / short lowest-funding bucket` 的 event-time relative-value book。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/carry/funding/settlement-boundary/event-time/perpetuals/binance/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据 portability probe

## 1. 这次看了什么
这次主材料是一个很新的 GitHub repo：

- **Author / owner:** `wangshaofu`
- **Year:** 2026
- **Title:** `LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps`
- **Venue:** GitHub repository
- **Repo URL:** <https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps>
- **Readable README:** <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/README.md>
- **Repo created:** `2026-02-19T09:15:18Z`
- **Repo pushed:** `2026-02-20T17:06:23Z`
- **DOI:** N/A

README 给它的自我描述很直白：

> **Measures WebSocket delivery latency around funding rate settlement times on Binance USD-M Futures, with the goal of identifying a viable short entry price at settlement.**

但源码比 README 更有意思：

- `streams.py` 里不是泛泛地盯全市场，而是直接把 **funding boundary** 当成特殊时刻；
- 它会从全市场 mark price stream 持续更新 funding，挑出 `funding_rates[symbol] < -0.003` 的合约；
- `main.py` 会在 **结算前 30 秒** 启动 60 秒 logging session；
- `analyze_latency.py` 再把结算前后几秒的 **bid、latency、trade volume** 画出来；
- `short_order.py` 则说明作者其实在尝试把这个 boundary pocket 进一步落成真实下单脚本。

也就是说，这份 repo 真正值钱的，不是“某个神秘阈值”，而是它把一个对 short-cycle 很关键的事实写死了：

> **funding settlement 本身就是一个可交易的 event-time pocket。**

不过 repo 还有个很重要的信号：**它的 side 叙事并不稳定。**

- README 说目标是找 `short entry price at settlement`；
- 但 `streams.py` 实际又在盯 **most negative funding / below -0.003** 的合约；
- 这说明作者也还没把“到底该顺着 funding 做，还是反着 funding 做”彻底讲明白。

对我们 desk，这反而是好事：

> **repo 已经告诉你“结算边界值得交易”；剩下更值得做的，是把方向问题改写成更鲁棒的横截面 raw alpha，而不是执着于单币单边。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的，不是 filter，也不是纯执行层：

> **funding-ranked cross-sectional continuation at settlement**。

翻成人话：

- 到 funding 结算时刻，市场已经把一部分拥挤程度写进了 funding rate；
- 如果横截面上有些合约 funding 明显更高、另一些明显更低，那么在结算后紧接着的第一个 `5m/15m` bar，强弱分化往往不会马上消失；
- 更像出现的是：
  - **高 funding 那一边继续相对强；**
  - **低 funding 那一边继续相对弱；**
- 所以 desk 更适合先测：
  - **long highest-funding bucket**
  - **short lowest-funding bucket**
  - 持有 1 个 event bar（`5m` 或 `15m`）

它属于：
- `raw alpha`
- `cross-sectional / relative-value`
- `carry / crowding / event-time continuation`

而不是：
- 慢频宏观 regime 注释；
- 只能做解释、不能下单的 funding 故事；
- 单纯 execution overlay。

## 3. repo 真正适合 desk 拿走的，不是“某个币在结算瞬间怎么打”，而是“结算边界要用横截面读”
如果机械照着 README 走，你很容易把它理解成：

- funding 极端；
- 结算到了；
- 找一个更好的短线打点；
- 单币直接 short / long。

但从 desk 的角度，这个读法有两个问题：

1. **单币方向不稳。**
   - 同样是 funding 极值，不同币、不同 beta、不同流动性状态下，结算后的方向并不一致。
2. **repo 已经暴露出自己也没把方向讲干净。**
   - README、负 funding threshold、short entry 脚本，这三者并不是一条很自洽的单边叙事。

因此更 desk 化、也更适合 `5m/15m` 快速复现的改写方式是：

> **把 settlement boundary 当成统一触发时刻，把 funding 当成横截面排序变量，然后做 relative-value。**

这比“继续猜单币应该 short 还是 long”更像一个可迭代、可扩 universe、可控 beta 的 raw alpha 素材。

## 4. 本地 portability probe：结算后到底该怎么读 funding 排序？
本轮我直接用 Binance USDⓈ-M 公共数据做了一个最小 event-time probe。

### 4.1 数据口径
- **Funding source:** `https://fapi.binance.com/fapi/v1/fundingRate`
- **Price source:** `https://fapi.binance.com/fapi/v1/klines`
- **Universe:** `BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / BNBUSDT / ADAUSDT / LINKUSDT`
- **Sample:** `2026-02-01` 到 `2026-04-12` UTC
- **Event definition:** 每个 funding settlement timestamp
- **Horizon:** settlement 后第一个 `5m` bar、以及第一个 `15m` bar

### 4.2 信号定义
对每个 funding 结算时刻：

1. 把 universe 内所有币按 **当前 funding rate** 排序；
2. 取 **最高 quartile** 做多，**最低 quartile** 做空；
3. 记下一根 `5m` 或 `15m` bar 的相对收益；
4. 先看等权 bucket 组合，再看最极端 `1v1`（最高 funding vs 最低 funding）做对照。

翻译成一句话就是：

> **结算时刻做一笔 very-short-horizon 的 funding rank long-short。**

### 4.3 结果先说结论
结论很明确：

> **比起单币猜方向，这条线更像“横截面 continuation / relative-value”问题。**

因为：
- bucket 版是正的；
- `1v1` 极端版明显更弱；
- 说明这更像 **排序分层** 的 edge，而不是“只抓最贵和最便宜各 1 个”的彩票打法。

## 5. 这轮最值得记住的 5 个数
Artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/funding_settlement_xs_continuation_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/funding_settlement_xs_continuation_series_2026-04-12.csv`

### 5.1 全样本 `5m`：bucket 组合已经是正的
- 事件数：**211** 个 funding settlement
- 策略：**long top funding quartile / short bottom funding quartile**
- 平均收益：**`+2.16 bps / event`**
- 中位数：**`+1.67 bps`**
- 胜率：**57.3%**

### 5.2 全样本 `15m`：比 `5m` 更肥
- 事件数：**211**
- 同样的 quartile long-short
- 平均收益：**`+3.42 bps / event`**
- 中位数：**`+1.98 bps`**
- 胜率：**55.9%**

这说明第一落点更像：

> **不是超快 `1m` 抢针，而是 funding 结算后下一个 `15m` 的 relative-value continuation。**

### 5.3 dispersion 越大，`5m` 结果更像 first lane
如果只保留 funding 横截面差距最大的那一档（`funding_spread >= 0.000226305`，也就是约 **2.26 bps** 的 funding spread）：

- `5m` 事件数：**53**
- 平均收益：**`+2.89 bps / event`**
- 中位数：**`+4.52 bps`**
- 胜率：**64.2%**

这个数很关键，因为它说明：

> **不是所有结算都值得做；真正更像 alpha 的，是 funding dispersion 足够大的结算。**

### 5.4 `15m` 高 dispersion 也仍为正
- `15m` 事件数：**53**
- 平均收益：**`+3.86 bps / event`**
- 中位数：**`+2.12 bps`**
- 胜率：**54.7%**

所以如果要先选一个主战周期，当前我会优先：
- **`15m`** 看 gross bps 更厚；
- **`5m`** 在强 dispersion 档更适合做第一段确认或更快 time-stop。

### 5.5 最极端 `1v1` 反而不如 bucket
- 全样本 `5m 1v1`：**`+1.29 bps`**，胜率 **52.6%**
- 全样本 `15m 1v1`：**`+1.50 bps`**，胜率 **53.1%**

这说明这条线暂时不该被读成：

> “只抓 funding 最极端的那两个币。”

而更该被读成：

> **“让 funding 排序先把横截面切层，再做 bucket relative-value。”**

## 6. 为什么这轮值得做，而不是继续补另一条旧 funding fade
因为这条线补的是一个**不同维度**的 raw alpha：

1. **不是单资产 funding fade。**
   - 已有池子里已经有 `funding spike × range fade`、`funding extreme × band fade`、`basis-funding gap convergence` 这些更偏单资产/双腿/单侧均值回归的东西。
2. **它是 event-time 的横截面 relative-value。**
   - 交易的是 funding 排序后的强弱分化，不是“某个币 funding 高就空”。
3. **它更贴近 desk 的短周期执行。**
   - 直接映射到 `5m/15m`；
   - 不需要先把 spot/perp、quarterly/perp、options/perp 那套重腿框架搬进来。
4. **它能扩充 raw alpha 素材池。**
   - 尤其补的是 `cross-sectional / carry / relative-value / event-driven` 交叉区，而不是又一条泛化 filter。

## 6.5 策略拆解（必填）
- 方向属性：**横截面 / relative-value / event-time continuation / market-neutral-ish**
- 基础 alpha：**funding 结算时刻，高 funding bucket 在下一根短周期 bar 里继续相对跑赢低 funding bucket**
- regime：
  - 更适合 **流动性足、funding 真有层次差** 的 majors + liquid alts universe；
  - funding 长时间贴零、横截面几乎没分层时应默认降级。
- filter / veto：
  - 只在 funding settlement 时刻触发；
  - `funding_spread` 至少过某个门槛（当前 first cut 可先试 **`>= 2.26 bps`**）；
  - universe 只保留高流动标的；
  - 可额外 veto：极端新闻、单边爆仓、盘口断层、临近重要宏观时点。
- execution / risk / sizing：
  - 入场：结算时刻对应的下一根 `5m` 或 `15m` bar open；
  - 出场：固定持有 1 根 event bar；
  - sizing：等权 bucket，或按近窗 realized vol / ADV 逆波动缩放；
  - risk：单币上限、bucket 最大集中度、dispersion 不足不交易；
  - cost：优先低费率账户、maker/被动成交、或至少别把它假装成全 taker 厚边策略。

## 7. 最小可执行版本
### 7.1 第一版策略壳
- **Universe：** `BTC / ETH / SOL / XRP / DOGE / ADA / LINK`（`BNB` 可先排除，因为 funding 常贴零，排序信息量差）
- **Trigger：** 每个 funding settlement timestamp
- **Ranker：** 当期 funding rate
- **Book：**
  - long top quartile
  - short bottom quartile
- **Entry：** 结算对应 bar open
- **Exit：** 1 根 `15m` 后平仓（并平行对照 `5m`）
- **Sizing：** 等权或 inverse-vol
- **No-trade gate：** funding spread 小于阈值不做

### 7.2 为什么先不做单边版
因为本轮 probe 已经给了一个很清楚的提示：

- 单币按 funding sign 去猜方向，表现很乱；
- 比如 summary 里有些币在 top-decile funding 上偏 continuation，有些又完全相反；
- 这恰恰说明：
  - **单边方向不是这轮最稳的东西；**
  - **横截面 rank book 才是更自然的第一落点。**

## 8. 它和 `1m / 3m / 5m / 15m` 的关系该怎么理解
这条线当前最合理的落点不是 `1m`。

更像：
- **触发时钟** 来自 funding settlement；
- **最小交易 bar** 先看 `5m`；
- **更成熟的 first lane** 当前反而是 `15m`。

所以：
- `1m / 3m`：更适合作为 execution 优化层，去改进入场点和滑点；
- `5m`：适合作为更快止盈/止损和 confirmation；
- `15m`：当前更像 raw alpha 的主承载周期。

## 9. 下一步怎么测
这轮必须继续往下走的 6 件事：

1. **正式扣成本。**
   - 这条线的 gross edge 只有 `2~4 bps/event`，非常成本敏感；
   - 下一步必须把 maker/taker、双腿滑点、借由 bucket 扩腿后的成交冲击一起扣进去。
2. **把 `BNB` 这种长期贴零 funding 的币从主 universe 里剔掉。**
   - 否则 funding rank 会被“零附近噪音排序”污染。
3. **做流动性分层。**
   - `majors-only`、`majors + liquid alts`、`full alt bucket` 三档分开跑，别假装全 universe 一个性质。
4. **把结算前 30 秒/10 秒的微结构加回来。**
   - 这正是 repo 原本在干的事；
   - 可以把 `1m/3m` 层留给 execution：看结算前是否 already front-run、是否该推迟到下一分钟再进。
5. **加入 premium / basis / OI 联合 gate。**
   - funding 只是 crowding 的一个写法；
   - 若 settlement 同时伴随 premium 回落或 OI 方向确认，edge 可能会更干净。
6. **做 rank persistence。**
   - 看 funding rank 在结算后是否还维持 1~2 个 observation；
   - 如果高 funding 很快归零，那 alpha 可能只值一根 `5m`；
   - 如果 persistence 强，`15m` 甚至 `2-bar hold` 才可能有更厚收益。

## 10. 风险与保留意见
- **这是一条 gross edge 很薄的策略。**
  - 没有低成本执行，就别自欺欺人。
- **样本只有约 70 天。**
  - 211 个结算事件不算少，但离 production 结论还差得远。
- **当前 universe 还偏人工。**
  - 后面要用稳定流动性过滤，而不是随手挑 8 个币长期不动。
- **repo 更偏 microstructure logging，不是现成回测论文。**
  - 这轮真正值钱的是：repo 把 settlement boundary 标成了特殊时刻；alpha 本体是我们基于公共数据把它翻译成了横截面 relative-value 版本。
- **不能把它误读成“funding 高就追多、funding 低就追空”的单边圣杯。**
  - 当前证据支持的是 **bucket long-short**，不是单币单边万能方向。

## 11. 来源
1. **wangshaofu (2026). _LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps_. GitHub repository.**
   - Repo URL: <https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps>
   - Readable README: <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/README.md>
   - Key files used:
     - <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/streams.py>
     - <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/main.py>
     - <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/analyze_latency.py>
     - <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/short_order.py>
   - Venue: GitHub
   - DOI: N/A
2. **Binance USDⓈ-M public APIs**
   - Funding history: <https://fapi.binance.com/fapi/v1/fundingRate>
   - Futures klines: <https://fapi.binance.com/fapi/v1/klines>
3. **Local portability artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/funding_settlement_xs_continuation_summary_2026-04-12.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/funding_settlement_xs_continuation_series_2026-04-12.csv`
