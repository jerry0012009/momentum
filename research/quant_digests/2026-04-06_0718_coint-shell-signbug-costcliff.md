# 别把这份 2026 新 repo 只当 Binance testnet demo：对 short-cycle desk，更该先测的是「cointegration spread mean reversion × verify-and-retry 执行壳」这条 raw alpha——但源码当前有 sign / threshold 两处硬伤
- 时间：2026-04-06 07:18 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `qstrat/constants.py` + `qstrat/libs/stats.py` + `qstrat/libs/strategy.py` + `qstrat/backtesting.py` + `backtest_log.txt`）+ Binance Futures testnet 公共 `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegration spread mean reversion（`ETHUSDT` vs `LINKUSDT` 价差偏离后的回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/zscore/order-verification/drawdown-killswitch/binance-futures/testnet/eth-link/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 工程证据（源码可读）+ 本地 portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `cointegration spread mean reversion`。**
> 但这轮真正值得 intake 的，不是把它当“又一条 pairs z-score”，而是把它看成一个**开源、最近、带 execution / verification / drawdown shell 的 raw-alpha 工程底座**。只是源码当前至少有 3 处硬伤：**entry threshold 配置不一致、z-score 方向疑似写反、cointegration admission 过松**，所以它现在更像“值得修的策略壳”，还不是能直接抄上线的成品。

## 1. 这次看了什么，为什么这轮值得写它
这轮主看：

1. **ssanin82 (2026). _strat-test-cointegration_. GitHub repository.**
   - Repo URL：`https://github.com/ssanin82/strat-test-cointegration`
   - Readable URL：`https://github.com/ssanin82/strat-test-cointegration`
   - Venue / DOI：无（GitHub repo）
2. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**
   - DOI：`10.2307/1913236`
   - Readable URL：`https://doi.org/10.2307/1913236`
3. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). _Pairs Trading: Performance of a Relative-Value Arbitrage Rule_. Review of Financial Studies.**
   - DOI：`10.1093/rfs/hhj020`
   - Readable URL：`https://doi.org/10.1093/rfs/hhj020`

这轮值得写它，不是因为我们缺第 N 条 pairs 论文，而是因为它补的是一个当前很缺的东西：

- **最近、开源、可直接跑的 end-to-end shell**：不只是信号，还包括 order placement、verify-and-retry、backtest harness、drawdown kill-switch；
- **和 desk 当前需求直接对齐**：可以把已有多篇 pairs / stat-arb digest，从“论文卡”推进到“可跑 baseline”；
- **但又足够诚实**：这份 repo 自己就暴露了一个很典型的现实问题——`repo headline alpha != 可上线 alpha`。源码看完以后，你会发现它最值钱的不是“ETH/LINK 有 edge”，而是“哪些工程层能留，哪些实现必须先修”。

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**这份 2026 repo 真正值得 desk intake 的，是「cointegration spread raw alpha + execution / verification / drawdown shell」这套完整骨架；但就当前源码状态看，直接照抄会把本该做 mean reversion 的东西，写成方向可疑、阈值混乱、成本后明显失血的半成品。**

### 一句话它怎么证明
我这轮不是只看 README，而是直接交叉了：
- `README.md`：写的是 `1h` 级 `ETH/LINK` cointegration + z-score spread trading；
- `qstrat/constants.py`：发现默认 `SIGNAL_TRIGGER_THRESHOLD = 0.02`，和 README 口径明显不一致；
- `qstrat/libs/stats.py` + `qstrat/libs/strategy.py`：发现 spread 定义是 `series1 - hedge_ratio * series2`，但当 `z-score > 0` 时，策略却下 **long symbol1 / short symbol2**，这和经典 spread-fade 的方向相反；
- `backtest_log.txt`：repo 自带样本里只完成了 **1 笔完整交易**，总 PnL **`+236.83 USDT`**、最大回撤 **`3.53%`**，但日志里同时出现 **order verification incomplete**；
- 我再补了一轮 Binance Futures testnet 公共 `markPriceKlines` 的 `5m/15m` portability probe：
  - `5m` 上，`|z|>=2` 事件 **87 次**，中位数 **`6.5` bars** 回到 `|z|<0.5`；
  - `15m` 上，`|z|>=2` 事件 **93 次**，中位数 **`6.0` bars** 回到 `|z|<0.5`；
  - 但一个最朴素的 `2σ -> 0.5σ / max 12 bars / 4 bps per leg` 非重叠事件策略，`10k` 名义资金下依然是 **`5m: -917.5 USDT`、`15m: -795.6 USDT`**。

翻成人话就是：

> **repo 展示了“spread 会回”的影子，但当前开源实现还没把这点 edge 变成成本后能活下来的策略。**

## 3. 这篇东西最值钱的 4 个点
### 3.1 base alpha 很清楚：就是 cointegration spread mean reversion，不是 filter，不是综述
这点先说死：
- `stats.py` 里用 `statsmodels.tsa.stattools.coint` 做 cointegration 检验；
- 用 OLS hedge ratio 构造 `spread = series1 - hedge_ratio * series2`；
- 用 `21` bar rolling z-score 做偏离度；
- `README` 和 `backtest_log` 也都在讲“spread 偏离后等待回归”。

所以它不是 regime、不是 overlay，**它本体就是 raw alpha**。

### 3.2 这份 repo 的真正价值，不是 pair 选择，而是 execution shell
它开源给出的可复用部分，反而比信号本身更值钱：

1. **verify-and-retry order shell**
   - 下完双腿之后会验证是否真的成交到目标方向；
   - 失败会进入 retry / partial verification；
   - 这比很多只会给你一个信号 notebook 的 repo 强得多。
2. **drawdown kill-switch**
   - 常量里给了 `DRAWDOWN_LIMIT_PCT = 90`；
   - `main.py` / `backtesting.py` 都把 kill-switch 接进去了。
3. **production/backtest 统一接口**
   - live 走 gateway，backtest 走 mock gateway；
   - 对 desk 来说，这种壳比单篇论文更容易转成自己的 baseline。

也就是说，它最适合服务的是：
> **把我们已经积累的一堆 pairs / stat-arb raw alpha，先包进一套最小可执行壳。**

### 3.3 但源码审计的结论也很明确：当前实现有 3 处硬伤，不能直接抄
#### 硬伤 1：threshold 口径不一致
- `README` 口径是：`z-score > 2` 才触发；
- `constants.py` 当前实际写的是：`SIGNAL_TRIGGER_THRESHOLD = 0.02`。

这不是小数点误差，这是**交易频率和噪声暴露会差一个数量级**的问题。

#### 硬伤 2：z-score 方向疑似写反
- `stats.py` 先算：`spread = symbol1 - hedge_ratio * symbol2`；
- 理论上如果 `z-score > 0`，说明 spread 偏高，经典 pairs 写法应是：**short symbol1 / long symbol2**；
- 但 `strategy.py` 当前写的是：`signal_side == positive -> BUY symbol1, SELL symbol2`。

也就是：
> **当前 repo 对正 z-score 的处理，更像“追 spread 扩张”，不是“赌 spread 回归”。**

除非作者后面对 spread 定义另有反向语义，否则这就是一个必须先修的 sign 问题。

#### 硬伤 3：cointegration admission 太松
`stats.py` 里 admission 条件写的是：
- `p_value < 0.5`
- `coint_t < critical_value`

`p < 0.5` 这种门槛，基本不够当 admission gate。对 short-cycle desk，更现实的做法至少应该是：
- `p < 0.05` 或更严格；
- 再加 `half-life / zero-cross / spread vol / turnover budget` 这些二级 admission。

### 3.4 portability probe 给出的 desk 结论很现实：gross 有，但先别幻想 5m 直接上线
我补了一轮最小 transfer check，用的是：
- 数据源：Binance Futures testnet 公共 `markPriceKlines`（无需授权）
- 标的：`ETHUSDT` / `LINKUSDT`
- 频率：`5m`、`15m`
- 样本：各 `1500` 根 bar
- spread：静态 OLS beta
- signal：rolling `21` bar z-score

先看事件层：
- `5m`：`87` 次 `|z|>=2` 事件，事件后中位 **`6.5` bars** 回到 `|z|<0.5`；
- `15m`：`93` 次事件，中位 **`6.0` bars** 回到 `|z|<0.5`。

这说明 **spread 回归 pocket 是有的**。

但一上最朴素的可交易骨架：
- entry：`|z| >= 2`
- exit：`|z| < 0.5` 或 `12 bars time-stop`
- sizing：`10k` 名义资金，双腿各 `50%`
- fee：`4 bps / leg`

结果就很直接：
- `5m`：**`62` 笔**，gross **`+74.49 USDT`**，net **`-917.51 USDT`**；
- `15m`：**`64` 笔**，gross **`+228.43 USDT`**，net **`-795.57 USDT`**。

如果把 entry 拉到更保守的 `3σ`：
- `5m`：gross **`+34.94`**，net **`-125.06`**；
- `15m`：gross **`+65.82`**，net **`-94.18`**。

这组数的含义非常清楚：

> **15m 明显比 5m 更接近“能活”的方向，但 naked z-score 本身还不够，必须靠更严 entry / 更强 admission / 更低成本 / 更少重试 才有机会。**

## 4. 为什么和当前项目直接相关
它和当前项目的关系，不在于“我们还缺一篇 pairs digest”，而在于：

1. **它补的是 runnable baseline，而不是纯概念。**
2. **它能服务至少 3 类现有 raw alpha**：cointegration pairs、cluster residual MR、same-underlier relative-value MR。
3. **它把工程问题暴露得很完整**：方向映射、threshold 配置、admission 宽松、verification friction、cost cliff。

这正好适合当前 desk 的阶段：
- 不是再收藏一条 headline alpha；
- 而是把已有素材池压成一个更诚实的 baseline runner。

## 4.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value mean reversion
- 基础 alpha：cointegration spread 偏离后的回归
- entry：rolling z-score 偏离达到阈值后，做 **spread-fade**（注意：repo 当前 sign 需要先校正）
- exit：`|z|` 回到较低阈值，或 time-stop 触发
- sizing：双腿各占名义资金 `50%`，beta-hedged；当前 repo 默认 `10x` leverage
- risk：drawdown kill-switch、active-order / active-position 检查、order verification
- cost：双腿四笔 legs 的手续费 / 滑点 / retry friction 必须显式入账；当前 portability probe 已经说明 **这是第一性约束，不是附属项**

## 5. 给 desk 的最小可落地版本
如果只想把这份 repo 变成 desk 可用的第一版，不要直接照抄，先做这 6 个修正：

1. **修正 sign**
   - `z > +entry`：先按经典 spread-fade 写成 `short symbol1 / long beta*symbol2`
   - `z < -entry`：`long symbol1 / short beta*symbol2`
2. **把 threshold 拉回正常区间**
   - `entry ∈ {2.0, 2.5, 3.0}`
   - `exit ∈ {0.5, 1.0}`
3. **重写 admission**
   - `p < 0.05`
   - minimum zero-cross
   - half-life ceiling
   - ADV / spread vol / cost bucket
4. **先从 `15m` 开始，不先上 `5m`**
   - 这轮 probe 已经显示 `15m` 更接近 gross 可用；
   - `5m` 更像成本压力测试桶。
5. **保留 repo 的 execution shell**
   - verify-and-retry
   - dual-leg position check
   - kill-switch
6. **显式记账 retry cost / maker-taker cost / slippage**
   - 不然回测会系统性高估。

## 6. 下一步怎么测（这轮最重要）
### 6.1 先测什么
做一个最小 A/B/C：

1. **A = corrected-sign baseline**
   - `15m`
   - `2.0 / 2.5 / 3.0σ` entry
   - `0.5 / 1.0σ` exit
   - `8 / 12 / 16 bars` time-stop
2. **B = A + stricter admission**
   - `p < 0.05`
   - half-life ceiling
   - zero-cross floor
3. **C = B + repo execution shell**
   - verification retry
   - daily drawdown governor
   - order-state audit

### 6.2 最小实验口径
- **数据**：Binance Futures 公共 `markPriceKlines`
- **频率**：先 `15m`，再 `5m` 当 stress test
- **标的池**：先从高流动 `BTC/ETH/SOL/LINK/BNB` 里滚动选 pair，不要只绑死 `ETH/LINK`
- **walk-forward**：`train 30d / test 7d`
- **hedge ratio**：rolling OLS / TLS 都试
- **成本**：至少跑 `4 / 8 / 12 bps` round-trip 等价三档
- **输出**：gross/net pnl、Sharpe、trade count、avg hold、zero-cross hit ratio、verification fail ratio、retry 次数、cost 占 gross 比例

### 6.3 第一轮最该看什么结果
这轮别问“最终收益最大化”，先回答 4 个问题：

1. **修正 sign 以后，gross 是否显著改善？**
2. **`15m 3σ` 能不能在合理 fee 下接近 break-even / 小幅转正？**
3. **verification / retry 到底是在救策略，还是在扩大 friction？**
4. **pair admission 做严格以后，trade count 下降多少、单位交易 edge 提升多少？**

## 7. 先别自嗨的风险
1. **repo 自带 backtest 样本太薄。** `backtest_log.txt` 里只完成了 1 笔完整交易，不能把 `+236.83 USDT` 当成有效验证。
2. **当前源码存在实现歧义。** threshold、sign、admission 三块都需要先审再跑。
3. **ETH/LINK 只是单 pair。** 它可以当 smoke test，但不能代表 pair book。
4. **testnet mark price 不等于真实可成交价格。** 实盘里只会比这里更贵，不会更便宜。

## 8. 这轮最值得记住的 desk 化结论
如果只记一句：

> **这份 2026 新 repo 值得 intake 的不是“ETH/LINK 圣杯”，而是 `cointegration raw alpha + execution shell` 这套可修底座；但就当前源码和 portability probe 看，先修 sign / threshold / admission，再谈上线。**

再补一句更贴当前短周期：

> **第一轮别上 `5m`，先拿 `15m` 做 corrected-sign + stricter-admission 的最小实验；`5m` 目前更像成本压力测试，不像主战场。**

## 9. 来源
1. **ssanin82 (2026). _strat-test-cointegration_. GitHub repository.**
   - Repo URL：`https://github.com/ssanin82/strat-test-cointegration`
   - Readable URL：`https://github.com/ssanin82/strat-test-cointegration`
   - 这轮直接审阅：`README.md`、`qstrat/constants.py`、`qstrat/libs/stats.py`、`qstrat/libs/strategy.py`、`qstrat/backtesting.py`、`backtest_log.txt`
2. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica, 55(2), 251–276.**
   - DOI：`10.2307/1913236`
   - Readable URL：`https://doi.org/10.2307/1913236`
3. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). _Pairs Trading: Performance of a Relative-Value Arbitrage Rule_. Review of Financial Studies, 19(3), 797–827.**
   - DOI：`10.1093/rfs/hhj020`
   - Readable URL：`https://doi.org/10.1093/rfs/hhj020`
4. **Binance Futures testnet public `markPriceKlines`（本轮 portability probe）**
   - 公开性：公开可拉、无需鉴权
   - 更新频率：按交易所 bar 频率滚动更新
   - 最小复现实验口径：`ETHUSDT/LINKUSDT`，各 `1500` 根 `5m/15m` mark-price bars，rolling `21` bar z-score，`2σ/2.5σ/3σ` entry，`0.5σ/1.0σ` exit，`12` bar time-stop，双腿各 `50%` 名义资金，显式计入每 leg 手续费
