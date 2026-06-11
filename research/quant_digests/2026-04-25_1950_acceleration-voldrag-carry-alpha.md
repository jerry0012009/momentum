# 别把这份 2026 多因子 repo 只读成“Millennium 风格包装”：对 short-cycle crypto desk，更该先拆的是「acceleration minus vol-drag carry」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：横截面里，**短窗价格加速度更强、但波动拖累更小**的币，下一小段时间更容易继续相对跑赢；可写成 `ret_10 - 0.5*ret_30 - 0.3*vol20` 的 cross-sectional carry proxy。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

**先回答 base alpha 是什么：** 不是“多因子全都要”，而是很具体的一条 `raw alpha`：**短窗加速度相对中窗斜率更陡、且 realised vol drag 更小的币，更容易在下一段继续相对占优。**

## 1. 为什么这条线值得单独拎出来

今天已经连续写了不少 `pairs / xs reversal / funding` 近邻题；这份 2026 repo `takahashi3899/crypto-multifactor-strategy` 真正对我们 desk 有补充价值的，不是它把 `momentum/value/carry/quality` 全部塞进一个“机构风格”壳，而是其中那条更容易映射到 `15m/5m` 的 **carry proxy**：

> `carry = short-term slope - 0.5 * medium-term slope - 0.3 * realised vol`

翻成人话：
- 只看“涨了多少”不够；
- 更想要的是 **最近这段加速在变强**；
- 但如果这股加速是靠高噪声、高抖动硬拉出来的，就要打折；
- 所以它本质上是一个 **acceleration-without-too-much-chaos** 的横截面 raw alpha。

这和我们今天已经写过的 `loser→winner fade / pair z-score fade / funding dislocation` 不一样：它更像 **单腿 cross-sectional continuation**，可作为 raw alpha 素材池里一条新的“相对强弱但不等于裸动量”的分支。

## 2. 来源与我实际读到的东西

### Repo
- **Author / Year / Title**: `takahashi3899` / 2026 / *crypto-multifactor-strategy*
- **Venue**: GitHub repository
- **DOI**: N/A
- **Readable URL**: <https://github.com/takahashi3899/crypto-multifactor-strategy>
- **Repo URL**: <https://github.com/takahashi3899/crypto-multifactor-strategy>

### 本轮审计文件
- `README.md`
- `factors.py`
- `signals.py`
- `config.py`
- `portfolio.py`
- `risk.py`

### Repo 里和本主题最相关的硬信息
1. **carry proxy 定义**（`factors.py`）
   - `short_slope = pct_change(10)`
   - `medium_slope = pct_change(30)`
   - `vol_drag = rolling_std(20) * sqrt(252)`
   - `carry = short_slope - 0.5 * medium_slope - 0.3 * vol_drag`
2. **组合层默认口径**（`config.py`）
   - `n_longs = 5`
   - `long_only = True`
   - `target_vol_annual = 15%`
   - `max_single_weight = 25%`
   - `fee_per_trade = 10bps`
   - `slippage = 10bps`
3. **overlay 不是主题本体**
   - `signals.py` 里还有 regime gate（bull/neutral/bear 标量 `1.0 / 0.6 / 0.2`）
   - `risk.py` 里有 vol target、drawdown hard stop、correlation penalty

所以这篇东西如果按我们 desk 的优先级来拆，最值得保留的是：
- **alpha 本体**：`acceleration minus vol-drag carry`
- **风控壳**：top-N long-only + vol target + turnover/position cap
- **不要先抱死的部分**：value/quality proxy、慢频 regime、多因子平均

## 3. desk 化改写：怎么把它翻成 `15m/5m` 研究题

repo 原始口径偏日频/周频；但 carry 公式本身并不依赖低频专属数据，所以能直接压到更短周期：

### short-cycle desk 版本
- **Universe**：12 个 liquid majors（BTC / ETH / SOL / BNB / XRP / DOGE / ADA / AVAX / LINK / DOT / LTC / UNI）
- **Bar**：`15m`
- **Signal**：
  - `ret_10 = close_t / close_{t-10} - 1`
  - `ret_30 = close_t / close_{t-30} - 1`
  - `vol20 = std(ret_1, 20 bars)`
  - `carry_proxy = ret_10 - 0.5 * ret_30 - 0.3 * vol20 * sqrt(96*365)`
- **Cross-sectional action**：按每根 bar 的 `carry_proxy` 做横截面排序
- **可交易读法**：
  1. top-N long-only router
  2. top-minus-bottom market-neutral sleeve
  3. `1h parent -> 15m child` 的 candidate ranking / admission

我更偏向先把它当 **top-N long-only router**，而不是马上做 top-bottom 对冲。原因很简单：短周期 crypto 的横截面对冲，腿数一多，turnover 会先把 edge 吃掉。

## 4. 本地 portability probe（Binance USDⓈ-M public, 约最近 6000 根 15m bar）

### 数据口径
- 市场：Binance USDⓈ-M perpetual public klines
- 资产：`BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT/XRPUSDT/DOGEUSDT/ADAUSDT/AVAXUSDT/LINKUSDT/DOTUSDT/LTCUSDT/UNIUSDT`
- 长度：约 `6000` 根 `15m` bars，约 `62.5` 天
- 回测口径：下一根收益；成本先粗扣 **one-way 4bps** taker（按换手计）

### Probe A：每根 15m 直接 rebalance，top-3 long-only
- 平均 gross：约 **`+0.105 bps/bar`**
- 平均 turnover：约 **`14.14%/bar`**
- 粗扣成本后平均 net：约 **`-0.461 bps/bar`**
- gross Sharpe：约 **`0.80`**

### Probe B：每根 15m 直接 rebalance，top-3 minus bottom-3
- 平均 gross：约 **`+0.058 bps/bar`**
- 平均 turnover：约 **`16.63%/bar`**
- 粗扣成本后平均 net：约 **`-0.607 bps/bar`**
- gross Sharpe：约 **`1.20`**

### Probe C：每 `4` 根（1h）才更新一次持仓，top-3 long-only
- 平均 gross：约 **`+0.113 bps/bar`**
- 平均 turnover：约 **`7.76%/bar`**
- 粗扣成本后平均 net：约 **`-0.198 bps/bar`**
- gross Sharpe：约 **`0.86`**

### Probe D：每 `4` 根（1h）更新一次，top-3 minus bottom-3
- 平均 gross：约 **`+0.101 bps/bar`**
- 平均 turnover：约 **`9.17%/bar`**
- 粗扣成本后平均 net：约 **`-0.265 bps/bar`**
- gross Sharpe：约 **`2.12`**

## 5. 这些数该怎么读

先说结论：**alpha 本体不是假的，但 default taker 交易太贵。**

更具体地说：

1. **carry proxy 在短周期上有方向感**
   - 四组口径全是 gross 正值；
   - 说明“短窗加速度强、但 vol drag 小”的币，下一段相对更强，这件事本身没死。

2. **top-bottom 并没有自动比 long-only 更好**
   - market-neutral 看起来更“专业”，但 short-cycle crypto 里多一条腿就多一层摩擦；
   - 当前 probe 下，`top-bottom` 的 gross Sharpe 更高，但 net 更差。

3. **降低 rebalance 频率比加复杂 overlay 更值得先做**
   - 从每根换仓改成每小时换仓，gross 没明显变差；
   - 但 turnover 从 `14.14%` 压到 `7.76%`，net 亏损明显收窄；
   - 这说明这条线真正的瓶颈是 **换手**，不是“信号不对”。

所以我不建议把这份 repo 先读成“多因子框架教学”；对我们更值钱的读法是：

> **先把 carry proxy 当一条 raw alpha 排名器，再决定怎么把它塞进更省摩擦的执行壳。**

## 6. 它在策略树里属于哪一层

### 它是什么
- **raw alpha**：是
- **shared filter / regime**：不是主身份，但可以挂接
- **risk overlay**：不是主身份，但 repo 附带这层壳

### 它服务哪类交易
- 最适合：
  - `15m` top-N relative-strength rotation
  - `1h parent -> 15m / 5m child` admission
  - long-only alpha sleeve 的 router / allocator
- 不太适合：
  - 高成本 taker 的频繁 top-bottom stat-arb
  - 没有 maker/queue edge 的极短换手版本

## 7. 最小可复现实验，下一步怎么测

别再往 repo 那套“全因子全风险全优化”里加戏，下一步直接做最小实验：

### 实验 1：只保留这条 alpha，本体单测
- `15m`，12 个 liquid majors
- 每小时更新一次
- `score = ret_10 - 0.5*ret_30 - k*vol20`
- 扫 `k ∈ {0.1, 0.2, 0.3, 0.4}`
- 输出：gross / net bps、turnover、hit-rate、top1/top2/top3 差异

### 实验 2：改成 parent-child 执行
- `1h` 上算横截面 carry rank
- 只在 `15m` 上找低冲击入场（例如 pullback 进，不追最强 bar）
- 持有 `4/8/12` 根 `15m`
- 看能否把 turnover 再压一截，而不显著损失 gross

### 实验 3：做“只做 long，不做 short”的诚实对照
- 这条线的 short leg 很可能只是把摩擦放大器接上去；
- 所以应该明确比较：
  - top1 / top2 / top3 long-only
  - top-bottom 对冲
  - top-only + BTC beta hedge

### 实验 4：加一个最便宜的 veto，而不是大而全 regime
先不要搬 repo 的 whole regime stack，只加 1 个最便宜的 veto：
- 当 universe 横截面 dispersion 太低时，不开仓；
- 或当 top1 与 top3 的 score spread 太窄时，不换仓；
- 核心目的是 **减少无谓轮动**，不是解释世界。

## 8. 这篇对当前 desk 的实际价值

我会把这条线放进 **“可继续复验的 raw alpha 素材池”**，但不会直接升成主策略。原因是：

- **优点**：
  - 是条清楚、可复现、可独立运行的 raw alpha；
  - 不依赖 funding / basis / 外部数据；
  - 很适合给 `15m` 横截面 rotation 做新排序器。
- **缺点**：
  - 眼下 default taker 成本下还不够厚；
  - 直接 top-bottom 会被 turnover 和腿数拖死；
  - repo 的“多因子 + 大量 overlay”容易掩盖真正该测的东西。

**一句话结论：** 这份 repo 真正值得 desk 留样的，不是“Millennium 风格多因子壳”，而是其中那条 **`acceleration minus vol-drag carry` 横截面 raw alpha**；当前在 Binance `15m` 上仍有 gross edge，但更适合先做 **低换手 long-only router / 1h→15m parent-child admission**，而不是直接拿 taker top-bottom 硬上。
