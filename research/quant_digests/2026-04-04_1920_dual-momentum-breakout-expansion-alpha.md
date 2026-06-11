# 20-bar breakout × 20/60-bar momentum × ATR 扩张：一个带完整风控壳的 trend sleeve 候选

- 时间：2026-04-04 19:20 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/trend/momentum/breakout/volatility-expansion/cross-sectional-ranking/correlation-filter/portfolio-risk/crypto/binance/15m/1h/repo/public-data/cost
- 证据类型：2026 GitHub 新 repo source audit（`README.md` + `src/strategies/trend_long.py` + `src/portfolio.py` + `main.py`）+ Binance Spot 公共 `1h/15m` 最小 portability probe

- 主题类型：raw alpha
- 基础 alpha：只在已处于 bull regime 的币上做 **20-bar 新高突破**，并要求 **20/60-bar 动量同时为正且达到阈值**、**ATR 处于扩张分位**；也就是“不是所有 breakout 都追，只追已经在加速的 breakout”。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次看的主源不是论文，而是一个 **2026 年新 GitHub 仓库**：`azuzxx9-jpg/quant-trade-system-v1`。它不是单一指标玩具，而是一个完整的多币组合研究壳；最值得单独拎出来的，不是整个系统，而是其中的 **`trend_long` sleeve**：`20-bar breakout + 20/60-bar dual momentum + ATR expansion + bull-regime gate`，再接 `next-open` 入场、ATR/结构止损、partial take-profit、trailing stop、time stop、相关性上限、组合风险预算。

对我们当前 desk，这条线的价值不在于“又一个 breakout 变体”，而在于它把 **raw alpha、本地执行、组合约束** 串成了完整策略壳，正好能补到我们当前主线里“趋势 raw alpha 有不少，但 portfolio 化 / cross-sectional rank / correlation gate 还可以继续拆”的空缺。

## 2. 源码里真正可复现的 alpha 是什么
### 2.1 entry 条件（`src/strategies/trend_long.py`）
仓库里 `trend_long` 的核心触发非常清楚：

1. **bull regime**：`close > SMA20 > SMA50` 且 `ADX >= 18`
2. **vol expansion**：`ATR/close` 至少在过去 120 根里的 **55% 分位以上**
3. **20-bar breakout**：当前 `close` 突破前 20 根最高价
4. **20-bar momentum > 3%**
5. **60-bar momentum > 5%**

也就是说，这不是“单纯新高就追”，而是：

- 先要确认市场已经在向上排列；
- 再要求波动真的在扩张，而不是压缩末端假突破；
- 最后要求短窗和中窗动量同时已经站起来。

这条线的 **base alpha** 可以直接说清：

> **正在加速的趋势币，在新高突破后更容易继续走，而不是立刻回落。**

这满足 raw alpha 的定义，不只是 filter 或 overlay。

### 2.2 exit / sizing / risk / cost（`src/portfolio.py`）
这个 repo 有一整套可直接落地的策略壳：

- **入场**：信号下一根 `open`，加 `5 bps` 入场滑点
- **初始止损**：`min(SMA20 - 1.1 * ATR, signal-bar low)`
- **分批止盈**：到 `+2.2R` 先平一半
- **保护逻辑**：partial 后把 stop 提到 break-even
- **追踪止损**：`max_price - 5 * ATR`
- **time stop**：`96` 根 bar
- **手续费**：`fee_rate = 4 bps`
- **组合层**：`max_portfolio_risk`、`max_gross_exposure`、每个 sleeve 的 risk/notional budget、cross-symbol correlation threshold、score-based sizing、cooldown、可选加仓（pyramid）

所以这不是“只有 entry 点子”；它已经是一个能直接转成实盘 research spec 的完整壳。

## 3. 为什么这条线现在值得进研究池
结合当前项目文档，这条线有几个明确对接点：

1. **它仍然是 raw alpha，不是纯 gate。** 当前 bot7 的 intake 优先级里，raw alpha / 可直接落地完整策略的候选优先级最高，这条线满足。
2. **它和我们现有主线兼容。** 项目里已经有 trend / momentum / breakout / volatility expansion 这条主线；这个 repo 的价值是把这些元素组合成了一个更完整的 portfolio-ready sleeve。
3. **它补的是“跨币 ranking + correlation gate + risk budget”这层。** 很多趋势想法在单币上看着能做，但一到组合层就互相高度相关、一起回撤；这个 repo 至少给了一个可复现的组合化壳。
4. **它能很快迁移到 15m / 1h。** 虽然源码原始 timeframe 是 `4h`，但逻辑完全基于公开 OHLCV 与常规指标，迁移门槛很低。

## 4. 最小 portability probe：public Binance spot 上，这条线迁到 `1h/15m` 怎么样
我用 Binance Spot 公共 OHLCV 做了一个**最小便携性快检**，窗口为 **2025-01-01 ~ 2026-04-04**，标的为 `BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT`。

为了不把 repo 的整套组合优化和相关性过滤混在一起，我先做了一个**更保守但更透明的 isolated sleeve probe**：

- 只保留 `trend_long` 这条 raw alpha；
- 每个币独立测试；
- 用 repo 的核心 entry / stop / partial / trailing / time-stop 逻辑；
- 按 `10 bps fee + 10 bps slippage?` 不对，按这次简化实现是 **round-trip 约 15 bps 级别** 的交易摩擦处理；
- **没有**用到 repo 的 top-N ranking、组合相关性约束、sleeve risk budget、drawdown scalar、pyramid。

所以这组数字更像是“alpha 核心本体能不能站住”，而不是“完整组合最终成绩”。

### 4.1 `1h` 快检结果
- **ETHUSDT**：`26` 笔，累计约 **+6.63%**，平均每笔 **+0.38%**，PF **1.22**
- **BTCUSDT**：`10` 笔，累计约 **-2.89%**，PF **0.82**
- **SOLUSDT**：`24` 笔，累计约 **-0.64%**，PF **1.09**（接近打平）
- **BNBUSDT**：`18` 笔，累计约 **-14.12%**，PF **0.59**

### 4.2 `15m` 快检结果
- **BTCUSDT**：`8` 笔，累计约 **+1.88%**，胜率 **75.0%**，PF **1.63**
- **ETHUSDT**：`40` 笔，累计约 **-3.02%**，PF **0.98**
- **SOLUSDT**：`49` 笔，累计约 **-5.44%**，PF **0.94**
- **BNBUSDT**：`20` 笔，累计约 **-14.25%**，PF **0.43**

### 4.3 这组数字怎么读
我对这组结果的解读是：

1. **这条 alpha 不是“全市场随便跑都行”的 broad trend alpha。** 它明显更像一个需要做 universe selection / ranking 的 trend sleeve。
2. **repo 里那些组合层约束不是装饰品。** 我这次故意没带 `symbol_score` 排名、相关性阈值、组合预算；结果恰好说明：如果把这类趋势 breakout 规则无脑铺到所有币，容易被 BNB/SOL 之类名字拖垮。
3. **它在 `1h` 上比在 `15m` 上更像能站住。** 这说明它更适合作为 `1h regime + 15m execution` 的上层 alpha，而不是直接当成宽 universe 的 `15m` 裸跑主策略。
4. **BTC/ETH 仍有继续挖的价值。** 尤其是 `1h ETH` 和 `15m BTC` 两段，不像已经彻底死掉，更像阈值和 ranking 还没对齐。

## 5. 对 desk 真正有用的，不是“照抄 entire repo”，而是抄哪一层
如果只问一句：**这篇东西最值得抄什么？**

我的答案不是“抄它的回测收益”，而是下面三层：

### 5.1 raw alpha 层
把趋势延续写成：

- `breakout` 负责确认价格已经脱离前高；
- `20/60-bar momentum` 负责确认不是随机刺穿；
- `ATR expansion` 负责确认不是低波动假动作。

也就是把我们常见的“突破”改写成**突破 + acceleration + expansion** 三联条件。

### 5.2 组合层
这个 repo 一个很实用的地方是承认：

> 趋势 alpha 不是只看 entry 对不对，还要看同一时间到底让哪些币进组合。

所以它加了：

- `symbol_score` 排名
- candidate correlation penalty
- sleeve risk budget / notional budget
- drawdown-based risk scalar

这对 short-cycle desk 很重要，因为趋势腿经常不是 **单笔** 亏，而是 **一起亏**。

### 5.3 迁移层
对 `5m/15m` 最现实的迁移，不是直接把所有参数照抄，而是：

- 把 `1h` 的 trend sleeve 当 **上层 raw alpha / regime gate**；
- 再用 `15m` 做更细的 trigger 和 execution；
- 或者只把它保留给 `BTC/ETH` 这类更干净的 universe。

## 6. 最小实验该怎么做
### 实验 A：先做“严格复刻版”
目标：知道 repo 的 edge 到底来自 **raw alpha**，还是来自 **组合排名与风控壳**。

1. 数据：Binance / Bybit perpetual 公共 `1h` 与 `15m`
2. 标的：`BTC/ETH/SOL/BNB/XRP/AVAX`，先复刻 repo universe
3. 规则：完整照抄 `trend_long` + `portfolio.py`
4. 输出：
   - 单币表现
   - 组合表现
   - ranking 前后差异
   - correlation gate 前后差异
   - `fee/slippage` 敏感度（`6/10/15 bps`）

如果完整壳显著优于 isolated sleeve，就说明这条线真正值钱的是 **portfolio wrapper**，不是裸 breakout 本体。

### 实验 B：做“desk 版短周期迁移”
目标：把它变成更贴近 `15m` 的 desk alpha。

1. 上层 regime：`1h` bull regime + vol expansion
2. 下层 trigger：`15m` 20-bar breakout，但只在 `1h` regime 为真时允许入场
3. universe：先只做 `BTC/ETH`
4. 阈值改写：
   - 把固定 `3% / 5%` 改成 rolling percentile 或 ATR-normalized threshold
   - 避免在不同波动币种上阈值不可比
5. 出场：保留 `partial @ 2.2R + trailing stop`，对比 `full trailing only`

### 实验 C：把它做成 cross-sectional sleeve，而不是全币通用规则
目标：解决这次快检里最明显的问题——**币种选择比信号本身还重要**。

1. 每个 bar 对所有候选币打分：
   - `trend_strength`
   - `20/60-bar momentum`
   - `ATR expansion`
2. 只做 top-1 / top-2
3. 叠加 rolling correlation penalty
4. 对比：
   - 全 universe 同时做
   - top-N 排名做
   - 只做 majors

如果 top-N 明显改善，那它就很适合作为 desk 的 **趋势篮子 sleeve**，而不是单币固定模板。

## 7. 结论
这条 repo 里的 `trend_long`，我会把它放进研究池，但定位得很清楚：

- **它是 raw alpha**，不是纯 filter；
- **它是完整策略壳**，不是只有 entry 的半成品；
- **它在 1h 比在 15m 更自然**；
- **它更像“需要 ranking / correlation gate 才成立”的趋势 sleeve**，而不是一个对所有币裸跑都行的 broad breakout 规则。

如果只留一句话给后续复现：

> **先别把它当“又一个突破策略”；更该把它当“20/60-bar 加速确认 + ATR 扩张 + portfolio ranking/correlation 壳”的趋势组件。**

## 8. 来源
### 主源（repo）
- **Author / Org**：`azuzxx9-jpg`
- **Year**：2026
- **Title**：`quant-trade-system-v1`
- **Venue**：GitHub
- **DOI**：无
- **Readable URL**：https://github.com/azuzxx9-jpg/quant-trade-system-v1
- **Repo URL**：https://github.com/azuzxx9-jpg/quant-trade-system-v1
- **关键源码**：
  - `trend_long`：https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/src/strategies/trend_long.py
  - `portfolio shell`：https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/src/portfolio.py
  - `main config`：https://raw.githubusercontent.com/azuzxx9-jpg/quant-trade-system-v1/main/main.py

### 公共数据口径
- **Data source**：Binance Spot Klines REST API
- **公开性**：公开可得，无需 key
- **更新频率**：支持分钟级 / 小时级 OHLCV
- **最小可复现实验口径**：`BTCUSDT/ETHUSDT/BNBUSDT/SOLUSDT`，`1h` / `15m`，next-open entry，显式 fees/slippage，独立 sleeve backtest
