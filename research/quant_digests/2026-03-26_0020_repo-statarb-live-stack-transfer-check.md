# 别把 live stat-arb 仓库直接搬成 desk alpha：这份 2026 新 repo 更该先拆的是「cointegration spread + 流动性上限 + 日内 throttle」完整骨架
- 时间：2026-03-26 00:20 UTC
- 类型：2026 GitHub 新仓库 + 代码级 source audit + README 披露 live results + Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**cointegration / beta-hedged spread 偏离均值后的回归；repo 里真正的 base alpha 不是 Telegram、不是 MySQL、也不是 daily guard，而是 `spread = log(A) - β log(B)` 的 z-score 均值回归**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/zscore/beta-hedged/liquidity-cap/daily-throttle/execution-stack/bybit/binance/15m/5m/repo
- 证据类型：GitHub repo 代码证据 + README live results + 本地公共数据快检

> 先回答 base alpha：**这是 raw alpha，而且是很标准的 pairs / stat-arb raw alpha。** repo 最值钱的不是“又一个会做 cointegration 的脚本”，而是它把一条 desk 真会用到的完整链条写全了：**选对 → z-score 入场 → beta-hedged sizing → chunked execution → 日内风控 throttle → 失效退出**。这比只抄论文 headline 更适合当前阶段，因为 desk 现在缺的不只是“再找一条 spread”，还缺“找到之后怎么诚实地上机”。

## 1. 这次看了什么
这轮主线不是论文，而是一份非常新的工程仓库：

1. **Anton Velychko (GitHub owner: `velychkoanton-stack`, repo created 2026-03-20), _statistical_arbitrage_trading_system_V1_**
2. 核心文件：
   - `selection/SQL-DB-Coint-upd-6.py`
   - `selection/SQL-DB-Stat-upd-5.py`
   - `execution/Level_2_CFT_bot_07-12-2025.py`
   - `execution/daily_guard_2.py`
3. README 还附了作者自报的 **Bybit live results（2025-06 ~ 2025-11）**。

一句话讲人话：
- 这不是“教你什么是 pairs”的教学 notebook；
- 它是一个 **早期 production-oriented** 的 crypto stat-arb 交易栈；
- 所以它对 desk 最有价值的部分，不是 abstract alpha，而是：**一条 pair mean-reversion 策略在真实系统里到底要补哪些 execution / sizing / guardrail 组件**。

这也符合当前学习进展：
- 最近 intake 已经补了很多 `pairs / stat-arb / relative-value` 思路；
- 但很多来源更偏“选对/信号”或“某个单独 filter”；
- 这份 repo 难得把 **entry / exit / sizing / risk / cost / orchestration** 都摆在明面上，适合当完整策略骨架卡片。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 值得 intake 的不是“cointegration 本身又被证明一次”，而是它把 `z-score spread raw alpha` 补成了一条可部署的完整链：**用 cointegration 选对、用 ±2 z-score 开仓、用 beta + 流动性 cap 控腿权重、用分块下单减少腿风险，再用日内 PnL throttle 和失效条件把系统收住**。
- **一句话说它怎么证明：** 证据不是学术显著性检验，而是 **代码规则 + README 披露 live 结果 + 我用 Binance 公共 `15m` 数据做的最小 transfer check**。

更具体地说：
1. 选对层：`SQL-DB-Coint-upd-6.py` 先算 hedge ratio、spread、z-score、ADF、p-value、Hurst。
2. 信号层：执行脚本里把 **`|z| >= 2`** 当作入场门槛，正 z 做 `short A / long B`，负 z 反过来。
3. sizing 层：不是机械 1:1，而是 **beta-normalized + 5m 成交额 cap + 最低单腿 notional**。
4. 风控层：不仅有单对 exit，还有 **daily guard**：
   - `PnL <= -3%` 当天停机；
   - `PnL >= 1%` 先触发 throttle，之后 TP target 按 `1% -> 2% -> 4% ...` 递增。
5. 执行层：不是一把梭，而是双腿 **chunked open / chunked close**，腿失败时还尝试 unwind。

## 3. 3 个关键数据点
1. **README 自报 live 成绩不差。** 2025-06 到 2025-11，作者写的是：**704 笔交易、64.6% 胜率、Profit Factor 1.22、收益 35%、最大回撤 -4.36%**。  
2. **代码里的入场规则很明确。** 执行脚本直接写了：**`z_score_upper_threshold = 2`、`z_score_lower_threshold = -2`**；这不是“概念性 stat-arb”，而是已经冻结到生产阈值的规则。  
3. **我用 Binance Futures 公共 `15m` 数据做的最小 transfer check 很诚实：只筛出 1 对。** 在 `BTC/ETH/SOL/XRP/ADA/DOGE/LINK/LTC` 八个高流动币里，按 repo 近似口径（train ADF `< -2.5`、p `< 0.1`、近 200 根最小 quote volume `> 10m USDT`）只留下 **`ETHUSDT-SOLUSDT`**；它在最近 `499` 根 `15m` 测试段上，**毛收益约 -0.37%，加 repo-like 成本后约 -2.30%，24 笔交易，胜率 45.8%，单笔均值约 -7.7 bps**。

## 4. 为什么和当前短周期 desk 有关
### 4.1 它服务的是哪类 raw alpha
- 分类：**pairs / stat-arb / relative-value / mean-reversion raw alpha**
- 不是：
  - 纯 filter
  - 纯 overlay
  - 纯 execution 工具箱

### 4.2 它补的是素材池哪块缺口
最近我们已经有很多“pair spread 可能会回归”的 intake，但还经常缺三块：
1. **两腿该怎么配权，不然一腿太胖；**
2. **真实开平仓时怎么避免单腿裸奔；**
3. **当日内状态变坏时怎么 throttle / stop，而不是继续机械开仓。**

这份 repo 恰好把这三块都补了，所以它比又一篇只讲 pair selection 的论文更适合这轮当主 digest。

## 5. 策略拆解（按完整策略卡写）
### 5.1 方向属性
- market-neutral / relative-value / pairs stat-arb

### 5.2 基础 alpha
- `spread = log(A) - β log(B)` 或价格层面的 `A - βB`
- 当 spread 偏离其历史中枢，赌的是 **reversion to mean**

### 5.3 entry
- repo 执行脚本硬编码：**`|z| >= 2` 才开仓**
- `z > 2`：`sell asset1 / buy asset2`
- `z < -2`：`buy asset1 / sell asset2`

### 5.4 exit
repo 里不是只靠一个条件退出，而是多条并行：
1. **z-score 过零**：`previous_z` 与 `last_z` 异号时平仓；
2. **PnL 到 TP/SL**：pair 级盈利/亏损阈值触发；
3. **时间上限 + 失去 cointegration**：持仓超过 `HL` 对应时长，且 cointegration flag 失效时退出；
4. **极端 z 风险**：达到 stop band 且 cointegration 丢失时退出；
5. **daily guard**：日内亏损超阈值时，不只是关一笔，而是直接封当天 bot。

### 5.5 sizing
repo 最值得偷的不是 `β` 本身，而是 **`beta_norm + 流动性 cap`**：
- 先找两腿中 **较低 5m 成交额** 的那一腿作为 controller；
- controller exposure 不超过 `min(base exposure, 该腿 5m cap)`；
- 另一腿按 `beta_norm` 扩展，但如果超 cap，就把两腿一起缩小；
- 最后还设置 **单腿最小 notional = 500 USDT**。

这其实是在回答 desk 上最现实的问题：**pair 不是算出 β 就完了，腿太细的时候再漂亮的 z-score 也会被 execution 吃掉。**

### 5.6 risk / overlay
- **单对层**：TP / SL / z-stop / timeout / lost-cointegration exit
- **日内层**：
  - `loss_stop_pct = 3.0`：到 `-3%` 直接 block 当天
  - `profit_lock_pct = 1.0`：到 `+1%` 开始 throttle，下一档 TP target 翻倍
- **系统层**：死锁重试、DB claim、pair-level bot allocation，避免多个 bot 抢同一对

### 5.7 execution / cost
- 双腿不是 simultaneously full-send，而是 **固定 USDT chunk 轮流成交**
- 若一腿失败，脚本会尝试 unwind 另一腿
- 这是 repo 很实用的一点：它默认承认 **两腿执行不同步是主要风险源之一**

## 6. 代码里最值得直接偷的 5 个细节
1. **ADF + p-value + Hurst 不是只做研究展示，而是写回数据库供执行层用。** 这让“统计关系是否还活着”变成运行时状态，而不是离线报告。  
2. **beta 不是只拿来中性化，还会进入 sizing。** 代码把 `beta_norm` clamp 在 `0.8 ~ 1.2`，避免极端 β 把一腿放到不可交易。  
3. **controller-leg 由低流动性腿决定。** 这是非常 desk 化的选择：不是让大腿说了算，而是让最脆弱那条腿先决定总仓。  
4. **日内 guard 是 throttle-first，不是只有 stop-only。** 达到日内盈利后先缩仓，而不是直接把系统关掉。  
5. **chunked execution + failure unwind** 很适合拿来服务我们后续的 5m 切片执行层，即使 raw alpha 最后不直接用这个 repo 的 signal。  

## 7. 本地最小快检：这套 repo-style pairs 逻辑搬到 Binance `15m`，还能活吗？
我做的是一个 **很小、很诚实的 transfer check**，不是 faithful 复刻：

- 数据：Binance USDⓈ-M Futures 公共 `15m` K 线  
- 标的：`BTC / ETH / SOL / XRP / ADA / DOGE / LINK / LTC`  
- 样本：最近 `1500` 根 `15m` bar；前 `1000` 根训练，后 `499` 根测试  
- 选对：train 段 OLS `β` + ADF `< -2.5` + p `< 0.1` + 近 `200` 根最小 quote volume `> 10m USDT`  
- 信号：repo 核心口径近似版：`|z| >= 2` 入场，`z` 过零退出，超 `24` 根超时退出，`|z| >= 3.2` 风险退出  
- 成本：用 repo 风格的双腿执行现实，粗略记成 **每次开/平各 4 bps 的 pair bundle 成本**

### 7.1 结果怎么读
1. **可交易候选并不多。** 28 个两两组合里，满足基本 cointegration + 流动性过滤的只有 **1 对：`ETH-SOL`**。  
2. **这对在 `15m bar-close taker` 上并不赚钱。**  
   - 0 成本：**-0.37%**  
   - 开/平各 2 bps/腿（合并成 bundle 后近似）：**-1.34%**  
   - 开/平各 4 bps bundle：**-2.30%**  
3. **换手有点高。** 499 根测试 bar 内做了 **24 笔**，中位持有只有 **1 根 15m bar**。这说明短周期上最容易发生的，不是“均值回归不来”，而是 **回归太快、边太薄、成本先吃掉**。

### 7.2 这组快检的结论
- **好消息：** repo 拆出来的“完整策略骨架”是有学习价值的；
- **坏消息：** 直接把它当成 Binance `15m bar-close pairs alpha`，目前看不成立；
- **最诚实的 desk 定位：**
  - raw alpha 本体是成立的候选家族；
  - 但短周期 transfer 需要更强的 pair admission、更慢的 rebalance、更细的执行切片；
  - 所以当前更该 intake 的，是 **它的 full-stack 组件设计**，而不是盲信它的 live headline 可以直接迁移。

## 8. 现在该怎么放进研究池
我的判断：**值得进池，但标签要写对。**

不是“这就是新一代 15m 可直接上线的 pairs alpha”，而是：
- **raw alpha**：cointegration spread mean reversion
- **更高价值的借鉴点**：
  1. pair discovery 到 execution 的完整链路  
  2. `beta_norm + liquidity cap` 的 sizing 逻辑  
  3. chunked pair execution  
  4. daily guard / throttle 机制

也就是说，它更像一张 **“完整策略工程骨架卡”**，而不是一张 **“已通过短周期 transfer 的 alpha 卡”**。

## 9. 下一步怎么测
1. **先别扩 universe，先把 pair admission 变严。** 在现有 high-liquidity majors 上补：rolling half-life、spread volatility bucket、quote-depth threshold、maker-fill proxy。  
2. **把 signal 和 execution 拆开测。** 继续保留 `15m` 做 pair selection / regime，改成 `5m` 做 execution slicing，看 chunked close/open 能不能把成本压回去。  
3. **把 repo 的 sizing 真正 desk 化。** 下一轮应显式 A/B：
   - fixed 1:1 notional  
   - β-neutral  
   - β-neutral + low-leg liquidity cap  
   看哪一层真的在减少回撤/腿风险。  
4. **加 no-trade band。** repo 现在更像 `|z|>=2` 就上；短周期上建议加 `entry>=2.2 / re-entry cooldown / min expected spread edge > fee budget`。  
5. **补“当日 throttle 后是否还开新仓”的实验。** 它可能不是纯风险模块，而是直接影响 turnover 与 PnL 分布。  
6. **如果这条线要进入实盘素材池，先从 `15m selection + 5m execution + majors only` 开始。** 不要一上来就幻想全币种 pairs 广撒网。

## 10. 风险与保留意见
- README 里的 live results 目前属于作者自报，我没有独立核验完整成交明细与净值曲线来源。  
- 仓库缺少 DB schema、配置、credential 与完整工作层，所以它更像 **可审计骨架**，不是一键可跑项目。  
- 我做的 Binance 快检是 **desk-oriented proxy**，不是 faithful 复现 Bybit live 系统。  
- 当前 transfer 为负，不代表 pairs 这条线无效；更像说明：**短周期 crypto pairs 的胜负手不在“会不会 z-score”，而在 admission + execution + cost governance。**

## 11. 来源
1. **Anton Velychko (GitHub owner), 2026, _statistical_arbitrage_trading_system_V1_**  
   - Venue：GitHub repository  
   - DOI：无  
   - Readable URL：`https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1`  
   - Repo URL：`https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1`  
   - README raw：`https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/main/README.md`
2. **Binance Developers – USDⓈ-M Futures Kline / Candlestick Data**  
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 12. 本地产物
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/summary.json`
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/pair_results.csv`
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/aligned_prices.csv`
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/basket_nav.csv`
