# 别把这份 2026 Binance Futures HFT repo 只读成执行工程：对 short-cycle desk，更该先测的是「cointegration spread fade × microprice/OBI veto」这条完整 raw alpha
- 时间：2026-04-04 04:16 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `data_loader.py` + `analyzer.py` + `optimizer.py` + `fix_strategies.py` + `main.cpp` + `strategies.json`）
- 主题类型：raw alpha
- 基础 alpha：**cointegrated spread 偏离均衡后向均值回归**；repo 里真正能给我们 desk 直接复现的，不是“低延迟 C++ 引擎”本身，而是 `spread z-score fade` 这条 raw alpha，再叠一层 `microprice / OBI` 的执行 veto
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / cointegration / microprice / order-book-imbalance / binance-futures / top-liquid-universe / zscore / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo（研究层 + 执行层都有）+ 代码参数细读 + GitHub API metadata

**先回答 base alpha：这篇东西的 base alpha 很清楚，就是 `cointegrated spread mean reversion`。`microprice / OBI` 不是 alpha 本体，而是一个“别在最差盘口状态硬追进去”的执行过滤层。也正因为 base alpha 能说清，它才配当本轮主 digest，而不是一篇泛泛的 microstructure 综述。**

## 1. 这次看了什么
这轮主看的是一个 2026 年的新 repo：

1. **SamarthChaudhary-22 (2026), _Crypto_Stat-Arb_HFT_Model_**  
   - Venue：GitHub repository  
   - Authors：`SamarthChaudhary-22`（GitHub owner）  
   - Repo URL：<https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>  
   - GitHub API metadata：`created_at = 2026-01-18`，`pushed_at = 2026-02-05`，默认分支 `main`  
   - 本轮重点读的文件：
     - `README.md`
     - `data_loader.py`
     - `analyzer.py`
     - `optimizer.py`
     - `fix_strategies.py`
     - `strategies.json`
     - `main.cpp`

2. 这份 repo 的结构很像我们 desk 真会用到的两层壳：
   - **研究层（Python）**：拉 Binance Futures 公共数据、筛 pair、优化阈值
   - **执行层（C++）**：订阅 `!bookTicker`、用 microprice 和 OBI 做准入、走 Binance Futures 下单

为什么这条线值得写？因为我们最近虽然已经积累了不少 pairs / stat-arb 素材，但很多材料要么偏论文、要么偏 dashboard、要么只讲 pair admission。**这份 repo 的稀缺性在于：它把 raw alpha、entry/exit、执行 veto、风险熔断都放进了同一条链路里。**

## 2. 这份 repo 真正值钱的不是“低延迟”，而是它把 raw alpha 和 execution veto 接起来了
先翻成人话：

> repo 真正可迁移的核心，不是“42 微秒 / 4~7ms RTT”这些工程口径，而是：
> 1) 先在 liquid perp universe 里找会回归的 spread；
> 2) 当 spread 偏离到极端 z-score 时做 fade；
> 3) 但只有在盘口没有明显继续朝你不利方向失衡时才放行。

这和“纯配对回归”相比，多了一层很实用的 short-cycle desk 思维：
- **alpha 本体**：spread 会回
- **执行 veto**：但不是每次看到 `|z| >= 2` 都立刻做，先看盘口是否太 toxic

这条结构对 `1m / 3m / 5m / 15m` 都有意义，因为它把策略拆成了两个可以独立实验的部件：
- `raw alpha`: spread fade
- `filter / veto`: microprice / OBI

## 3. 代码里能直接拿走的策略骨架
### 3.1 Universe 和原始数据口径
`data_loader.py` 直接定义了研究入口：
- 数据源：**Binance USDⓈ-M Futures 公共 API**
- 频率：`1m`
- 回看：`365` 天
- 宇宙：按 `quoteVolume` 选 **top 50 liquid USDT-M pairs**

这点很关键：它不是拿一个小样本 pair 做漂亮故事，而是明确从**可交易 universe**出发。对于我们 desk，最容易移植的做法就是把这个 universe 缩成：
- `top 15~25` 流动性最稳定 perp
- 先避开新币、memecoin、上新不久的合约

### 3.2 Pair admission 的硬门槛
`analyzer.py` 的筛选非常朴素但够实用：
- 先把 `1m` close **resample 成 `1h`**，提高筛选速度
- `MIN_CORRELATION = 0.85`
- `P_VALUE_THRESHOLD = 0.05`
- `MAX_HALF_LIFE = 240`（最大 4 小时）
- `MIN_OVERLAP_HOURS = 1000`

也就是说，repo 的 admission 逻辑不是“看着像一对就上”，而是：
1. 先要足够相关；
2. 再跑 OLS hedge ratio；
3. 再做 ADF；
4. 最后要求 half-life 不要太慢。

对我们 desk，这条线最值得抄的不是具体数字，而是顺序：

> **先做“会不会回、回得够不够快”的 admission，再做 entry。**

### 3.3 Entry / exit / stop 的 baseline 很清楚
`optimizer.py` 和 `main.cpp` 拼起来后，baseline 壳基本是：
- rolling window：`30 / 60 / 120 / 240 / 360` 分钟
- entry z：`1.5 / 2.0 / 2.5 / 3.0`
- exit z：`0 / 0.25 / 0.5`
- stop z：`4 / 5 / 8`
- 费用 proxy：`FEE_PCT = 0.0012`（约 `12bps`）

而 live C++ 版本最后写死成：
- `Z_ENTRY = 2.0`
- `Z_EXIT = 0.5`
- `BET_SIZE = 1000.0`

这基本就是一个完整的 raw alpha baseline：
- `z > +2`：short spread
- `z < -2`：long spread
- `z` 回到 `±0.5`：平仓

### 3.4 Microprice / OBI 这层，不该被误读成“另一条 alpha”
`main.cpp` 从 Binance `!bookTicker` 取：
- best bid / ask price
- bid / ask volume

然后构造：
- **microprice**：`(BidPrice * AskVol + AskPrice * BidVol) / (BidVol + AskVol)`
- **OBI**：`(bidVol - askVol) / (bidVol + askVol)`

这层逻辑最有意思的地方在于：**它不是拿 OBI 来预测方向，而是用它给 spread fade 做 veto。**

但代码里的阈值其实很温和：
- `OBI_LONG_THRESHOLD = -0.2`
- `OBI_SHORT_THRESHOLD = 0.2`

对应到入场条件：
- `z > 2` 时，只要 leg1 不是特别 bid-heavy、leg2 不是特别 ask-heavy，就允许 short spread
- `z < -2` 时，只要 leg1 不是特别 ask-heavy、leg2 不是特别 bid-heavy，就允许 long spread

所以更准确的翻译不是“OBI 强确认”，而是：

> **别在盘口已经明显继续对你不利时，硬做这笔 spread fade。**

这非常像我们 desk 该用的执行 veto，而不是主 alpha。

## 4. 这份 repo 为什么适合当前 desk，而不是继续围着旧 breakout / retest 内循环
因为它直接扩 raw alpha 素材池，而且还是一条能独立落地完整策略的 raw alpha：
- 不是单纯 filter
- 不是纯解释型综述
- 不是“再讲一次为什么配对有效”
- 而是一个可直接拆成 `entry / exit / sizing / risk / cost / execution veto` 的**完整 relative-value shell**

尤其对当前 desk，价值在三点：

1. **raw alpha 清楚**：spread mean reversion
2. **执行组件清楚**：microprice / OBI veto
3. **最小实验很快**：先不用 tick 级，把它压缩成 `15m signal + 5m execution veto` 就能先跑 baseline

也就是说，这一篇不是在补“pairs 的概念课”，而是在补：

> **如何把一个本来容易停留在论文层的 pairs alpha，变成 short-cycle 可执行组件。**

## 5. 这份 repo 的最大问题：它给了完整思路，但 as-is 其实并不算干净可运行
这恰恰是这篇 digest 最值得记住的地方：**思路值得抄，代码不能盲抄。**

### 5.1 Pipeline 存在明显断裂
`main.cpp` 读取 `strategies.json` 时，期待字段有：
- `leg1`
- `leg2`
- `hedge_ratio`
- `mean`
- `std_dev`

但 `optimizer.py` 默认输出的是：
- `leg1`
- `leg2`
- `hedge_ratio`
- `window_minutes`
- `entry_z`
- `exit_z`
- `stop_z`

也就是说：**优化器输出和 live engine 读取字段不匹配。**
repo 里额外放了一个 `fix_strategies.py` 去补 `mean / std_dev`，这说明作者自己也踩到了这条管线断点。

对我们 desk，这个 bug 的启发反而很实用：

> 不要把 pair selection、threshold optimization、live execution 混成一锅；三层产物要有明确 schema。

### 5.2 Research frequency 和 execution frequency 之间有“频率断层”
repo 的研究链路是：
- 用 `1m` 数据下载
- 用 `1h` 数据筛 pair
- 再回到 `1m / tick` 级执行

这不是不能做，但有个很现实的问题：
- 你在 `1h` 上看到的协整关系，未必天然能承受 tick 级噪音
- 你在 `1m` 上设的 `z=2`，也未必和 `1h` 上筛出来的 half-life 完全一致

所以这条线更适合 desk 的改法是：
- `15m` 做 pair admission + primary signal
- `5m / 1m` 做 execution veto

而不是直接把 `1h admission -> tick execution` 原封不动搬过来。

### 5.3 当前输出 pair 里有不少“看起来不够 institutional”的组合
repo 自带的 `strategies.json` 里虽然吐出了 `22` 组候选，但很多 pair 很明显偏杂：
- `1000PEPEUSDT / FARTCOINUSDT`
- `DOGEUSDT / HYPEUSDT`
- `AVAXUSDT / DOGEUSDT`（hedge ratio 还高到 `104.97`）
- `HYPEUSDT / NEARUSDT`

这不代表 alpha 一定没用，但说明：
- 如果直接按 top-50 quote volume 扫，**容易扫进叙事噪声很重的新币 / meme 对**
- 对 short-cycle desk，先从 `BTC / ETH / SOL / XRP / ADA / DOGE / LINK / LTC / BNB` 这种主流腿开始更稳

## 6. desk 视角下，这条策略应该怎么拆
### 6.1 策略类型归类
- 主题类型：`raw alpha`
- 基础 alpha：`cointegration spread mean reversion`
- filter / veto：`microprice / OBI`
- 风险层：position stop / portfolio kill switch

### 6.2 完整落地版本该长什么样
如果把 repo 翻译成 desk 版，我会建议这样落：

- **Universe**：Binance / Bybit / Hyperliquid 上流动性最稳的 `10~20` 个 perp
- **Admission**：
  - rolling correlation > 某阈值
  - EG/ADF 过检
  - half-life 不能太慢
  - funding / listing age / liquidity 稳定性过检
- **Signal**：
  - residual / spread z-score fade
- **Execution veto**：
  - live OBI 不要明显逆风
  - spread widening 过快时不追
  - 单腿滑点超预算则取消
- **Sizing**：
  - beta-neutral 或 residual-vol-neutral
  - 每对 pair 设 notional cap
- **Risk**：
  - `z-stop`
  - `time stop`
  - single-pair drawdown cap
  - global kill switch
- **Cost**：
  - maker/taker fee
  - 双腿滑点
  - funding
  - legging risk

## 7. 最小实验：先别做 tick 级幻觉，先做这 3 步
### 第一步：先验证 raw alpha，不带 OBI
先在 `15m` 上做一版干净 baseline：
- 宇宙：`10~20` 个主流 perp
- scan window：近 `30~60d`
- entry：`|z| >= 2`
- exit：`|z| <= 0.5`
- stop：`|z| >= 4`
- time stop：`min(4h, 1.5 × estimated half-life)`
- cost：至少显式扣 `双腿手续费 + 2~4 ticks 滑点 proxy + funding`

目标不是做漂亮收益，而是先回答：
- 哪些 pair 真有回归；
- 哪些只是看起来 cointegrated，但 hold 太久、成本吃光。

### 第二步：再把 OBI / microprice 当 veto 层加进去
如果 `15m` baseline 过关，再上 `5m / 1m` 的盘口层：
- 只在 raw signal 已经触发时才看 OBI
- 不把 OBI 当独立方向 alpha
- 先测它能否：
  - 降低止损占比
  - 缩短持有时间
  - 改善 fill quality

也就是说，这里要测的是：

> **OBI 能不能把“同样的 spread fade”变得更能成交、更少挨打。**

### 第三步：做 live paper，而不是直接 production
因为这类策略最容易在 paper 上好看、上线后死在：
- 双腿不同步
- 某一腿盘口突然抽干
- funding / basis regime 突变
- pair relationship 在事件时段失效

所以最合理的下一步不是“马上实盘”，而是：
1. `15m` 历史 baseline
2. `5m/1m` live paper 执行 veto
3. 最后才是 production sizing

## 8. 对 `1m / 3m / 5m / 15m` 的具体建议
- **`15m`**：最适合做 primary signal  
  因为 spread 回归在这个频段更容易和成本拉开一点点距离。

- **`5m`**：最适合做执行与 time management  
  例如更早减仓、盘口不对劲就 veto、或者把 time stop 切细。

- **`3m / 1m`**：更像 execution layer，不建议一开始就拿来当主信号层  
  否则很容易把本来能做的 pairs alpha，压成一条被噪音和滑点吃死的伪 HFT 策略。

## 9. 一句话结论
这份 2026 repo 最值得我们 desk 收进研究池的，不是“C++ HFT 引擎”这个表层，而是：

> **把 `cointegration spread mean reversion` 这条 raw alpha，明确拆成 `admission -> z-score entry/exit -> microprice/OBI veto -> kill switch` 的完整策略壳。**

它的优点是：raw alpha 清楚、组件齐、能快速做最小实验；
它的缺点也同样清楚：repo as-is 有 pipeline bug，pair universe 也偏脏，不能直接照搬。

但对当前 short-cycle desk，这恰好是好事：**它不是要我们抄答案，而是给了一套很适合继续提纯成 production 组件的 raw alpha 母板。**

## 10. 下一步怎么测（直接执行版）
1. **先做主流腿基线池**：`BTC/ETH/SOL/XRP/ADA/DOGE/LINK/LTC/BNB`，滚动 `30~60d` 做 admission。  
2. **先跑纯 spread fade baseline**：`15m` 入场信号，显式扣双腿成本与 funding。  
3. **再测盘口 veto 增量**：接 live `bookTicker`，比较“有 / 无 OBI veto”的：
   - 胜率
   - 止损占比
   - 平均持有时间
   - 真实可成交比例
4. **最终只留下两类组件**：
   - 可独立赚钱的 spread raw alpha
   - 对 raw alpha 有明确增益的 execution veto

## Sources
1. SamarthChaudhary-22 (2026), **Crypto_Stat-Arb_HFT_Model**, GitHub repository.  
   - Repo: <https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>
2. Engle, R. F., & Granger, C. W. J. (1987), **Co-integration and Error Correction: Representation, Estimation, and Testing**, *Econometrica*, 55(2), 251-276.  
   - DOI: <https://doi.org/10.2307/1913236>
3. Binance USDⓈ-M Futures public market data docs / endpoints used by repo (`ticker/24hr`, `klines`, `!bookTicker`, `positionRisk`).  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api>
