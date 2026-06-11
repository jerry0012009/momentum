# 别把这份 Binance options repo 只读成 Telegram 报警器：对 short-cycle desk，更该先测的是「European lower-bound breach × perp hedge-to-expiry」这条 event-driven raw alpha
- 时间：2026-04-11 23:12 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：`European option ask` 若低于其最基础的 `intrinsic lower bound`，可买入被低估的 call/put，并用同标的 perp 做反向对冲，赚取到期保底价值或价差回补；对应两条壳分别是 `long call + short perp` 与 `long put + long perp`。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：options / relative-value / stat-arb / lower-bound / perpetual-hedge / same-venue / binance / event-driven
- 证据类型：工程证据（repo README + source audit）+ Binance 官方 public API live probe

## 1. 这次看了什么
这次看的是 GitHub 仓库 **senyka0 / binance-options-arbitrage**。仓库表面上像个“发现期权套利并发 Telegram 提醒”的小脚本，但它真正值得 desk intake 的，不是提醒器外壳，而是它把一条**非常基础、但可直接交易化**的 options raw alpha 写成了最小执行闭环：

- 扫描 Binance 同所 USDT 结算 European options；
- 找 `call ask < S - K` 或 `put ask < K - S` 这类 lower-bound breach；
- 发现后直接下期权单，同时用同标的 perpetual futures 做对冲；
- 默认只看近到期（`max_hold = 7d`）并要求最小边际（`min_pct = 1`）。

比起很多需要三腿、四腿、跨 venue 转仓的 crypto options 想法，这条线更朴素：**先只抓“单个 option 相对 underlying/perp 已经便宜到低于内在价值下界”的事件。**

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得抄的不是提醒器，而是把 textbook 级 `European lower bound` 变成了同所、可扫描、可下单的 event-driven raw alpha。
- **一句话证明方式：** 源码里直接按两条条件扫单：
  - 若 `strike < underlying` 且 `underlying - (strike + call_ask) > 0`，则视为 **call 被低估**，执行 `buy call + sell perp`；
  - 若 `strike > underlying` 且 `(strike - put_ask) - underlying > 0`，则视为 **put 被低估**，执行 `buy put + buy perp`。

把 payoff 写开就知道它不是“猜方向”，而是 **relative-value / no-arb floor trade**：

### 2.1 Call 壳
若在入场时满足 `S0 - K - C > 0`，做：
- long 1 call
- short 1 perp

到期时组合 payoff 为：
- 若 `ST >= K`：`(ST - K) + (S0 - ST) = S0 - K`
- 若 `ST < K`：`0 + (S0 - ST) > S0 - K`

所以 gross payoff 下界就是 `S0 - K`，只要入场成本 `C` 小于 `S0 - K`，就有正的静态边际。

### 2.2 Put 壳
若在入场时满足 `K - P - S0 > 0`，做：
- long 1 put
- long 1 perp

到期时组合 payoff 为：
- 若 `ST <= K`：`(K - ST) + (ST - S0) = K - S0`
- 若 `ST > K`：`0 + (ST - S0) > K - S0`

gross payoff 下界就是 `K - S0`。只要 put ask 便宜到低于这个 floor，就不是“看跌赌方向”，而是**被动捡 static mispricing**。

## 3. 为什么和当前项目有关
这条线和当前 desk 很相关，原因是它虽然来自期权，但本质上是：

1. **base alpha 很清楚**：不是波动故事，不是希腊值故事，而是 `option ask < intrinsic floor` 的可执行相对价值错价；
2. **天然适合短周期监控**：信号触发是 quote/event-driven，不需要等日频因子；`1m/3m/5m` 的角色是扫描和进场，不是硬把慢变量伪装成逐 bar 预测；
3. **同 venue 更像 desk 工具**：期权腿和 perp 腿都在 Binance，同结算资产 USDT，少了跨所转仓和资产搬运；
4. **能直接落完整策略**：entry、hedge、hold horizon、size、risk、exit、cost，全都能写清楚。

它和我们 4 月 11 日前面做过的 `same-expiry synthetic future × listed future parity gap` 不是一回事。那条线本质是 **call/put 组合出来的 synthetic future** 去对比 listed future；这条线更原始，甚至不用先拼 synthetic，只看**单腿 option 相对标的下界是否直接失真**。

## 3.5 策略拆解（必填）
- 方向属性：options / relative-value / stat-arb / event-driven
- 基础 alpha：`option ask` 低于 `intrinsic lower bound`
- 主题定位：**raw alpha**，不是 filter / regime / overlay
- 做多壳：
  - `call underpriced`: `long call + short perp`
  - `put underpriced`: `long put + long perp`
- 触发条件：
  - `g_call = (perp_bid - K - call_ask) / perp_mid`
  - `g_put  = (K - put_ask - perp_ask) / perp_mid`
  - 只有 `g_call` 或 `g_put` 超过成本缓冲时入场
- exit：
  - 基线版：持有到 option expiry
  - desk 版：gap 回补到阈值内先平；或剩余到期时间 < 指定窗口强平
- sizing：按期权盘口可成交张数和 perp 最小下单单位做 clip，优先 small notional 多次进场
- risk：期权腿流动性、perp funding、剩余到期时间、盘口跳空、腿间未同步成交
- 成本：期权 taker/maker、perp fee、funding、滑点、可能的 basis 漂移

## 4. 代码级最有价值的地方
### 4.1 它没有绕远路，直接扫最基本的错价
`optionArb.py` 的核心逻辑非常直白：
- 拉 futures 价格；
- 拉 options 链；
- 按 strike 和当前标的价判断 call/put 哪些合格；
- 对满足 lower-bound breach 的合约，再查一遍 depth，确认 top ask 还在；
- 若边际大于 `min_pct`，就直接执行两腿。

这类 repo 的价值不在“代码高级”，而在它提醒我们：
> 有些最值得收进素材池的 alpha，不需要先做复杂表面拟合，而是先把**最基础的 no-arb floor** 做成 scanner。

### 4.2 但源码也暴露出一个关键工程问题：原始接口已过时
仓库里用的是：
- `https://www.binance.com/bapi/eoptions/v1/public/eoptions/exchange/tGroup?...`
- `https://www.binance.com/bapi/eoptions/v1/public/eoptions/market/depth?...`

我本轮复核时，这组接口已返回：
- `code: 10000`
- `message: "Please upgrade to the latest version"`
- `data: None`

也就是说，**这条 alpha 不是失效了，而是 repo 的数据接法过期了。**
对 desk 真正有用的动作，不是把它丢掉，而是把 scanner 迁到 Binance 官方 `eapi`：
- `eapi/v1/exchangeInfo`
- `eapi/v1/ticker`
- `eapi/v1/depth`
- `eapi/v1/index`

## 5. Binance 官方 public live probe：这条线现在有没有票？
我用 Binance 官方 `eapi` 做了一个最小 live probe，范围限定为：
- 标的：`BTCUSDT / ETHUSDT / BNBUSDT`
- 只看 `7d` 内到期的 option
- 只看已经有 ask 的 ITM call / OTM put（即可能触发 lower-bound 壳的那些）

### 5.1 本轮结果（2026-04-11 23:06 UTC）
- `BTCUSDT`：有 ask 的候选 `47` 个，**0 个真正 breach**；最接近的是 `BTC-260412-72500-C`，gap 仍为 **`-0.212%`**。
- `ETHUSDT`：有 ask 的候选 `20` 个，**0 个真正 breach**；最接近的是 `ETH-260412-2300-P`，gap 为 **`-0.404%`**。
- `BNBUSDT`：有 ask 的候选 `38` 个，**0 个真正 breach**；最接近的是 `BNB-260412-605-C`，gap 为 **`-0.250%`**。

对应 order book 顶层报价也做了复核：
- `BTC-260412-72500-C`：best ask `730`, best bid `550`
- `ETH-260412-2300-P`：best ask `25.0`, best bid `8.0`
- `BNB-260412-605-C`：best ask `5.4`, best bid `4.3`

### 5.2 这说明什么
- **这条 alpha 不是 always-on**，更像 event-driven 稀疏票；
- 同所 Binance 盘口目前不算离谱，至少在这次快照里还没出现“肉眼可捡”的 lower-bound breach；
- 但最接近 breach 的几个点只差 `20~40 bps` 量级，说明它更像：
  - 盘口短暂真空时触发；
  - 大波动 / 流动性抽干 / 临近到期时出现；
  - 必须做连续 scanner，而不是一次性静态截图。

## 6. 对 short-cycle desk 的正确落地方式
别把它理解成“拿周频期权去做慢策略”。它更合理的姿势是：

- **信号时钟**：`1m` 扫描，必要时更快；
- **入场时钟**：一旦 breach 出现，优先在 `1m/3m` 内完成两腿成交；
- **监控时钟**：`1m/3m/5m` 持续盯 gap 是否回补；
- **持有上限**：到期前 or `max_hold <= 7d`；
- **策略本体**：event-driven raw alpha；
- **短周期的职责**：quote monitoring + fast execution + early close，不是把 options 慢变量伪装成 bar-by-bar directional predictor。

## 7. 最小可复现实验（下一步怎么测）
### 7.1 实验口径
先不要接私有下单，先做 public-only replay / live paper scan：

1. 每 `1m` 拉一次：
   - `eapi/v1/exchangeInfo`
   - `eapi/v1/ticker`
   - `eapi/v1/depth`
   - `eapi/v1/index`
   - `fapi/v1/ticker/bookTicker`（若要更 execution-aware 地用 perp bid/ask）
2. 只保留：
   - 剩余到期时间 `< 7d`
   - call: `K < S`
   - put: `K > S`
   - option best ask 存在，且 top-of-book qty 足够做最小 notional
3. 定义两个 score：
   - `score_call = (perp_bid - K - call_ask)/perp_mid`
   - `score_put = (K - put_ask - perp_ask)/perp_mid`
4. entry 条件先试三档：
   - `> 0.30%`
   - `> 0.50%`
   - `> 0.80%`
5. exit 两套并行：
   - **expiry exit**：拿到 option expiry
   - **gap close exit**：score 回落到 `< 0.10%` 就平

### 7.2 最先看 5 个指标
- `signals/day`
- `fillable rate`（两腿顶层盘口够不够）
- `gross edge bps at entry`
- `net edge after fee + funding`
- `time-to-close / time-to-expiry`

### 7.3 必须先加的现实过滤器
- `funding buffer`：perp 若需持有数天，funding 不能忽略
- `basis buffer`：perp 不是现货，近到期时仍会有 basis 漂移
- `depth symmetry`：期权腿和 perp 腿都要过最小成交量
- `quote staleness`：option 深度更新慢时，先不做
- `same-expiry crowding veto`：临近结算最后几小时单独分层，不要和普通时段混为一谈

## 8. 风险与保留意见
- 这不是纯 textbook spot-option arbitrage；repo 实际用的是 **perp hedge**，所以会引入 funding / basis / 盯市路径风险。
- 若 option 和 perp 两腿不能同步成交，短时方向暴露会非常大。
- Binance options 的可成交深度未必稳定，很多看起来“有价差”的点，真实能成交的 size 可能极小。
- 越临近到期，breach 越可能出现，但盘口也越容易抽干。
- 因为原 repo API 已过时，真正复现前，第一步不是回测，而是**先重写数据抓取层**。

## 9. 一句话结论
> 这份仓库最值得 desk 抄的，不是“Binance options 报警器”，而是把 `European option lower bound` 变成了**同所、近到期、可被 `1m/3m/5m` scanner 驱动的 event-driven raw alpha**；本轮 live probe 首判目前 **0 违例**，但最近的几档只差 `20~40bps`，说明它值得做成长期常驻监控，而不是一次性读完就算。

## 10. 来源
1. **senyka0** (2023). *binance-options-arbitrage*. GitHub Repo.  
   - Repo URL: `https://github.com/senyka0/binance-options-arbitrage`
   - Readable URL: `https://github.com/senyka0/binance-options-arbitrage`
   - 关键文件：`README.md`, `optionArb.py`

2. **Robert C. Merton** (1973). *Theory of Rational Option Pricing*. *The Bell Journal of Economics and Management Science*.  
   - DOI: `10.2307/3003143`
   - DOI URL: `https://doi.org/10.2307/3003143`
   - 用途：给这条 lower-bound / no-arb 壳提供经典理论地基。

3. **Binance Options / Futures Public API**（本轮 live probe 实际使用）  
   - `https://eapi.binance.com/eapi/v1/exchangeInfo`
   - `https://eapi.binance.com/eapi/v1/ticker`
   - `https://eapi.binance.com/eapi/v1/depth`
   - `https://eapi.binance.com/eapi/v1/index`
   - `https://fapi.binance.com/fapi/v1/ticker/bookTicker`
