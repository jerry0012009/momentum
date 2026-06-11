# 别把这个 2026 crypto bot 只读成“情绪拼盘”：对 short-cycle crypto desk，更该先拆的是「量价失衡 × OI 堆积 × funding 极端 × top-trader 持仓偏移」这条 pre-pump raw alpha
- 时间：2026-04-23 17:10 UTC
- 类型：GitHub repo source audit（`README.md` + `strategies/signal_scanner.py` + `hybrid_trader.py`）
- 主题类型：raw alpha
- 基础 alpha：横截面里那些**价格还没明显动，但成交量异常、OI 上升、funding / top-trader L/S 开始偏到 squeeze 方向**的币，更容易在后续短窗出现方向性爆发；交易上就是做一条 `pre-pump / pre-squeeze anomaly score`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / anomaly-score / pre-pump / squeeze / funding / open-interest / long-short-ratio / volume / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程证据

## 1. 这次看了什么
这次看的是 `NikoSAN02/crypto-trading-bot` 里**还没被前面 digest 单独拆过**的一条分支：`strategies/signal_scanner.py`，并补看了 `hybrid_trader.py` 里它是怎么被接成可交易壳的。

这个分支和 repo 里已经写过的 funding carry 不一样。它不是赚 funding，也不是低频情绪择时；它想做的是一条**横截面 directional anomaly alpha**：
- `volume anomaly`：量放出来了，但价格还没怎么动，怀疑有人在提前装货；
- `funding extremes`：持仓已经开始拥挤，可能会挤出 squeeze；
- `OI divergence`：OI 上升但价格没怎么走，像是在“蓄力”；
- `top-trader long/short ratio`：大户仓位方向开始转；
- `Fear & Greed`：只是一层全市场低频修正，不该被误认成主 alpha。

所以这轮的 base alpha 能说清楚：**主信号不是 Fear & Greed，而是横截面里的“未爆发先拥挤”异常分数。**

## 2. 核心结论
- 这条线可以归类为 **raw alpha**，不是纯 filter。因为真正驱动 entry 的，是**单币种横截面异常分数**，而不是全市场风险闸门。
- 它最有价值的地方不是“多因子越多越好”，而是把一条短周期 desk 真能先做 MVP 的思路写成了明确规则：
  - volume 权重 `0.25`
  - funding 权重 `0.25`
  - OI 权重 `0.20`
  - top-trader L/S 权重 `0.15`
  - Fear & Greed 权重 `0.15`
- repo 里已经给出了第一版 admission 口径：
  - `composite_score >= 65` 才允许进场（`hybrid_trader.py`）
  - `>80` 视为 `STRONG_BUY`（`signal_scanner.py`）
  - `daily volume >= $5M`
  - `24h price change` 不能已经过热（`abs(change) <= 20%`）
  - 至少 `2` 个非默认子信号同时有效
- 它不是“逐根 1m 信号”。更诚实的定位是：**`1h` 刷新的 cross-sectional anomaly parent signal + `15m/5m` child execution**。这对当前 desk 仍然有用，因为很多短周期 raw alpha 本来就该分成「慢一点的 admission」和「快一点的执行」。

## 3. 为什么和当前项目有关
当前 bot7 需要继续补 raw alpha 素材池，尤其是 `cross-sectional / relative value / stat-arb / pairs / squeeze` 这些不是单纯 breakout/retest 的方向。

这份代码正好补的是另一个家族：**横截面异常领先信号**。它不是在问“这根 K 线是不是突破”，而是在问：
> 哪些币现在看起来像还没走出来，但仓位、量能、拥挤度已经开始偏了？

这类思路和 desk 现有素材库互补：
- 可以直接当一条 `long-only` 或 `long-short` 的 raw alpha；
- 也可以给后面的 breakout / momentum 策略做 admission router；
- 还可以跟 funding / liquidation / basis 类策略共用一套拥挤度侧的数据层。

## 3.5 策略拆解（必填）
- 方向属性：横截面 directional anomaly / squeeze-capture
- 基础 alpha：**volume-price dislocation + OI build-up + crowded-positioning shift**，即市场在价格尚未大幅扩散前，已经出现“量先来、仓位先挤、价格后跟”的蓄势结构
- regime：更适合高流动、可做空、perp 数据完整的币；横盘后放量、拥挤开始积累时更有意义
- filter / veto：
  - `volume_usd >= 5M`
  - `abs(24h move) <= 20%`，避免已经追到末端
  - 至少 `2` 个真实信号，不接受“全是默认 50 分”
  - 若 `Fear & Greed` 极端贪婪，可降杠杆而不是硬开大
- risk / sizing / execution overlay：
  - repo 里 directional tier 用 `3x` 杠杆
  - 单笔 `margin <= $25`，notional 约 `<= $75`
  - 止损 `5%`，止盈 `10%`
  - 至少持有 `2h`
  - `4h` 后若价格仍弱（如 `< -2%`）可提前走
  - `24h` 后若没赚到 `1%` 走 time exit

## 4. 源码里最值得直接抄下来的规则
### 4.1 Volume anomaly：不是看“量大”，而是看“量大但价没怎么动”
`scan_volume()` 用 Binance `24hr` ticker 做一个很朴素但很 desk-friendly 的 proxy：
- 先筛 `USDT` 对、日成交额 `>= $1M`
- 对高流动币，如果**价格变化还很小**，但量已经很大，就给更高分
- 额外 bonus 条件：`abs(price_change_pct) < 2` 且 `volume_usd > $50M`

翻成人话就是：**不是追已经飞掉的币，而是找“量先明显起来、但价格还没 fully expand”的币。**

### 4.2 OI divergence：不是 trend confirmation，而是“蓄力未释放”
`scan_open_interest()` 拉 Binance futures `openInterestHist` 的 `1h × 24` 序列。
源码最有用的不是复杂建模，而是这个 admission：
- 若 `oi_change_pct > 5%`
- 且 `abs(price_change_pct) < 2%`
- 直接打高分（`70 + oi_change_pct` 上限 100）

这其实就是一句话：**OI 在堆，但价格还没走，说明杠杆仓位在挤进来 yet move 未完成。**

### 4.3 Funding extremes：把拥挤方向翻译成 squeeze 候选
`scan_funding()` 用 Binance `premiumIndex`：
- funding 很负：仓位偏空，做多分数更高，假设更容易 short squeeze
- funding 很正：仓位偏多，分数下降，提示 long squeeze 风险

这里最关键的不是 funding 本身，而是：**funding 在这条线里不是 carry alpha，而是 crowding proxy。**

### 4.4 Top-trader L/S：不看散户口径，优先看更“聪明的钱”
`scan_long_short_ratio()` 用 Binance `topLongShortPositionRatio` 的 `1h × 24`：
- `current_ratio < 0.8` 且 `ratio_change > 0.1` → 认为 smart money 正在转多，给高分
- `current_ratio > 2.0` 且 `ratio_change < -0.1` → 认为 smart money 开始撤退，给低分

这比只看总持仓净多空更像一个**方向性 confirmation**。

## 5. 我对这条 alpha 的判断
### 5.1 为什么它够格当 raw alpha
因为这里的主问题不是“市场风险大不大”，而是**在同一时间横截面里，哪些币更可能先动起来**。这已经是 alpha ranking 问题了。

更具体地说，它做的是：
1. 同时刻扫描一批币；
2. 给每个币一个 `0~100` 的 anomaly score；
3. 只交易 top bucket；
4. 再用 `5m/15m` 选择执行位置。

这和纯 overlay 的差别很大。overlay 只会说“今天全体减仓”；而这条线会说“今天只做 A/B/C，不做 D/E/F”。

### 5.2 为什么它又不能被吹成逐根快频 alpha
因为 repo 里的几个关键数据源天生偏慢：
- OI / top-trader L/S 用的是 `1h`
- Fear & Greed 是日频
- volume 是 `24h` 聚合

所以更诚实的 desk 落地方式应该是：
- **parent signal：每小时或每 15 分钟刷新一次横截面分数**
- **child execution：在 `15m` 或 `5m` 上找 pullback / micro-break / spread acceptable 的点位进**

也就是说，这条线最适合当**cross-sectional admission alpha**，而不是 pretending 自己是逐笔 order-flow engine。

## 6. 可复刻的最小实验
### 6.1 MVP 口径
先别一上来复刻五路全开。第一版最小实验直接测这个三因子骨架：
- `Volume dislocation score`
- `OI build-up score`
- `Funding squeeze score`

先把 `Fear & Greed` 去掉，避免低频日值污染；`top-trader L/S` 可当第二阶段增强项。

### 6.2 一个 desk 更实用的最小定义
每小时刷新一次 universe（如 `BTC, ETH, SOL, XRP, DOGE, ADA, LINK, AVAX, LTC, BCH, PEPE, WIF, APT, SUI`）：
- `vol_score`: 最近 `24h` 成交额分位数高，但 `24h` 涨跌幅绝对值低
- `oi_score`: 最近 `24h` OI 变化高，但对应 price change 小
- `fund_score`: funding 更偏负的一侧给更高做多分，偏正的一侧给更高做空分

然后：
- 做多篮子：`composite >= 70`
- 做空篮子：若把 funding / L/S 方向反转后得到低分极端，也可测 `composite <= 30`
- 执行层：只在 `15m` pullback 或 `5m` micro-breakout 后入场
- 持有层：先测 `2h / 4h / 8h`

### 6.3 最该先看的指标
- top decile vs median 的未来 `1h / 2h / 4h` 收益差
- `score bucket` 单调性
- 做多 top-N、做空 bottom-N 的 market-neutral spread
- 成本后 hit-rate / payoff ratio
- 子信号 ablation：去掉 `funding` 或 `OI` 后，edge 掉多少

## 7. 风险与保留意见
- `Fear & Greed` 明显是低频 overlay，不该占到 `0.15` 这么高的固定权重；搬到 desk 上我会先把它降成 **regime gate / sizing adjuster**。
- `24h volume` + `24h change` 这种 proxy 太粗，真实复刻时更该换成 `1h rolling volume / intraday RVOL / VPIN-like imbalance`。
- `OI` 与 `top-trader L/S` 都来自交易所特定口径，跨 venue 可比性有限，所以第一版最好限定单 venue universe。
- 这条线容易在“已经很热的币”上变成追涨杀跌，所以 repo 里加的 `abs(24h move) <= 20%` 和 `>=2 个真实信号` 是必要的，不是可有可无。

## 8. 下一步怎么测
最值得先做的不是把 repo 原封不动搬进来，而是：
1. 用 Binance public data 先做一个**去掉 Fear & Greed 的三因子 parent score**；
2. 在 `15m` 上测 `score top bucket` 的未来 `1/2/4` bar continuation；
3. 再把 execution 拆成两版对照：`next-bar open` vs `5m micro-breakout admission`；
4. 若 long-only 有 edge，再补 `bottom bucket` 反向分数，看能不能做成 long-short market-neutral basket；
5. 最后才决定 `top-trader L/S` 和 `Fear & Greed` 是该升格进 alpha，还是只留在 sizing / regime。

## 9. 来源
- NikoSAN02. (2026). *crypto-trading-bot*. GitHub repository.
  - Repo URL: `https://github.com/NikoSAN02/crypto-trading-bot`
  - Readable URL: `https://github.com/NikoSAN02/crypto-trading-bot/blob/main/README.md`
- Key source files:
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/strategies/signal_scanner.py`
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/hybrid_trader.py`
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/strategies/sentiment_engine.py`
- Public data endpoints referenced by repo:
  - Binance Spot 24hr ticker: `https://api.binance.com/api/v3/ticker/24hr`
  - Binance Futures premium index: `https://fapi.binance.com/fapi/v1/premiumIndex`
  - Binance Futures OI history: `https://fapi.binance.com/futures/data/openInterestHist`
  - Binance Futures top-trader L/S ratio: `https://fapi.binance.com/futures/data/topLongShortPositionRatio`
  - Alternative.me Fear & Greed: `https://api.alternative.me/fng/?limit=7`
