# 别把这份 2025 Bybit C++ 做市 repo 只读成示例工程：对 short-cycle desk，更该先测的是「min-spread floor × laddered quotes × inventory skew × drift-cancel」这条完整 maker raw alpha

- 时间：2026-04-04 10:16 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `src/strategy.cpp` + `src/main.cpp` + `src/trading_helper.cpp` + `.env.example`）+ Bybit V5 公开接口复现实验口径映射
- 主题类型：raw alpha
- 基础 alpha：**不是猜方向，而是持续在盘口两侧挂被动单，赚取 bid-ask spread / maker edge；当库存偏向一边时，用 inventory skew、TP、stop、gross cap 和 drift-cancel 把“赚点差”这件事变成可控的完整策略。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/liquidity-provision/market-making/maker/bybit/perpetual/laddered-quotes/inventory-skew/drift-cancel/funding-aware-pnl/execution/microstructure/repo/public-data/1m/3m/5m/15m/cost/risk
- 证据类型：repo 源码证据 + 交易所公开数据复现实验口径

## 1. 这次看了什么

这轮我刻意**不继续补 pairs / carry / OFI / 单币反转**，而是补一条素材池里同样必须长期保留的家族：

> **maker / liquidity provision raw alpha。**

原因很简单：

- 最近 intake 里，pairs、cross-sectional、carry、single-asset mean reversion 都已经有不少新卡；
- 但如果没有一批**可独立复现的做市 raw alpha 壳**，整个短周期素材池其实还是偏“主动吃单方向交易”；
- 而这份 repo 的价值恰好不在“新奇”，而在于它把 **entry / refresh / inventory / TP / SL / PnL / funding / gross exposure guard** 都写出来了。

所以这轮选它，不是因为它“最 fancy”，而是因为它非常符合当前优先级：

> **它是一条能独立复现、也能直接落成完整策略壳的 raw alpha。**

## 2. 先回答最重要的一句：base alpha 是什么？

一句话版：

> **base alpha 就是：在有足够可赚点差时，用被动双边挂单赚 spread；如果库存偏了，就缩一侧、放另一侧，同时用 TP / stop / gross cap 控住 adverse selection 和库存爆炸。**

换成人话：

1. 先看最优买一卖一和实时 spread；
2. 如果当前 spread 够宽，就围着 mid 两侧分层挂单；
3. 被成交后，不赌大方向，而是继续靠另一侧报价和 TP 把库存慢慢卸掉；
4. 如果 mid 漂得太快、库存太偏、总敞口太大，就收缩甚至暂停报价。

所以这条主题非常清楚：

- **不是** filter
- **不是** regime gate
- **不是**纯 execution 优化
- **而是**一条完整的 maker raw alpha

## 3. repo 真正给了哪些完整策略部件

### 3.1 Entry / Quote engine：它不是“挂一笔试试”，而是完整的双边分层做市

`src/strategy.cpp` 里，核心报价逻辑是：

- 用 Bybit linear perp orderbook 的 best bid / ask 算 `mid`
- 当前 live spread 若太窄，就用最小 floor 顶住：
  - `target_spread_bps = max(min_spread_bps, live_spread_bps * spread_factor)`
- 默认参数里：
  - `BYBIT_MIN_SPREAD_BPS = 0.2`
  - `BYBIT_SPREAD_FACTOR = 1.0`
  - `BYBIT_LADDER_LEVELS = 3`

也就是说，第一层想法不是“预测涨跌”，而是：

> **盘口只要还能留出一点 edge，就按层数在两侧排队吃 spread。**

而且 repo 不是单层挂单，而是默认每侧 `3` 层 ladder。这个点很重要，因为它直接决定：

- 不是只赌最优一档成交；
- 而是在 mid 周围构建一个简化版流动性曲线；
- 对短周期 desk，这已经是完整策略壳，不只是一个 snippet。

### 3.2 Inventory skew：repo 给的不是“均匀双边挂”，而是库存感知报价

这份材料最值钱的一点之一，是它没有把做市写成“永远等量双边挂”。

源码里：

- `net_qty = long_size - short_size`
- 若 `|net_qty| > max_net_qty`：
  - 太长 → 直接停 bid
  - 太短 → 直接停 ask
- 若还没超上限：
  - 只缩偏仓那一侧的报价量
  - 而且最小仍保留到约 `20%`

默认配置里：

- `BYBIT_MAX_NET_QTY = 100`

翻成人话：

> **它的 alpha 不是“始终双边收租”，而是“尽量双边收租，但不为收租把自己堆成单边风险仓”。**

这让它从一个示例 bot，变成了**可 desk 化的 maker alpha 壳**。

### 3.3 Exit：TP、stop、gross cap 都给了，已经不是半成品

这份 repo 的退场层也写得很完整：

- 若净多头存在，就在 mid 上方挂 TP sell
- 若净空头存在，就在 mid 下方挂 TP buy
- 默认：`BYBIT_TP_SPREAD_BPS = 0.5`
- 默认 stop：`BYBIT_STOP_LOSS_BPS = -1`（即默认关闭）
- 还有限制总敞口的 `BYBIT_GROSS_NOTIONAL_CAP`

这几个部件拼起来以后，结构非常清楚：

- **entry**：按实时 spread 做双边 ladder quote
- **exit**：库存存在时用 TP 卸仓
- **risk**：库存上限 + gross notional 上限 + optional stop

也就是说：

> **它已经不是“有信号、没策略”；而是完整到可以直接拿来改成回测器输入的策略定义。**

### 3.4 Refresh / Cancel：它还把 stale quote 问题显式写进去了

`src/main.cpp` 里还有一个对 short-cycle 很关键的细节：

- 主循环约每 `1s` 执行一次
- 若 mid 相比上一轮移动超过 `2` 个 tick
- 就 `cancel_all` 后重新报价

源码里的口径是：

- `drift_threshold_ticks = 2.0`
- `sleep_for(1 second)`

这很重要，因为 maker alpha 最怕的不是“没挂上”，而是：

> **挂着旧价，结果被新信息反向成交。**

repo 至少把这个问题正面写出来了，而不是假装“被动成交=天然有 edge”。

### 3.5 Cost / PnL：它没有忽略 funding 和 fees

README 和 `src/main.cpp` / `src/trading_helper.cpp` 还给了另外一个很像样的地方：

- private websockets 监听 execution / position
- 跟踪 realized / unrealized PnL
- 单独累计 fee
- 还把 funding 也算进净值

这意味着它的“收益”定义不是拍脑袋，而是更接近真实 desk 视角：

> **净 capture = realized spread - fee ± funding ± inventory mark-to-market。**

这对 perpetual maker 策略尤其关键。

## 4. 这条主题为什么值得进当前研究池

最近学习进展里，我们已经连续补了很多：

- pairs / cointegration / OU
- carry / funding / basis
- cross-sectional high-momentum
- single-asset mean reversion
- OFI / VWAP pressure / microstructure directional alpha

这些都重要，但它们大多偏：

- 主动吃单
- 赌方向
- 或者赌 spread reversion

而这份 repo 补的是另一条独立家族：

> **不靠方向预测先赚第一层 alpha，而是靠流动性供给本身赚钱。**

所以它的价值不只是“又一份 repo”，而是：

- 给当前素材池补了 **maker / liquidity provision** 这条支线；
- 和已有的 trend / MR / pairs / carry 家族**相关性可能更低**；
- 即使最终独立收益不够厚，也能沉淀成执行与库存管理层的通用组件。

## 5. 这份 repo 最值钱、也最该警惕的地方

### 5.1 值钱的地方：它真的是完整策略壳，不只是片段

我会把它归入“高可复现度 repo”的原因，是它已经给了：

- 标的：Bybit linear perpetuals
- 数据：public orderbook + private execution/position
- 报价：spread floor + ladder
- 风险：inventory skew + max net + gross cap
- 退出：TP + optional stop
- 记账：fee / funding aware PnL

也就是说，如果现在要做最小复现，不需要先脑补半套规则。

### 5.2 最该警惕的地方：默认参数薄得吓人，极容易被 adverse selection 吃掉

repo 默认配置里最醒目的数字其实不是“稳”，而是“薄”：

- 最小 spread floor：`0.2 bps`
- TP：`0.5 bps`
- 刷新节奏：`1s`
- drift cancel：`2 ticks`

换句话说：

> **这更像“尽量把 very thin maker edge 收干净”的工程模板，而不是已经证明 robust 的 production alpha。**

如果你把它直接理解成“0.2bps spread floor 就能长期赚钱”，那基本是在骗自己。真正的敌人是：

- queue position
- refresh latency
- stale quote 被选中成交
- fee tier / rebate 差异
- 行情快时 inventory 来不及卸

所以这条材料的正确读法不是“参数可直接抄”，而是：

> **结构可以先抄，edge 厚度必须重测。**

### 5.3 一个小但很说明问题的细节：README 和 `.env.example` 口径不完全一致

README 里提到：

- 默认 symbol 可用 `SUIUSDT` 做低 notional 测试

但 `.env.example` 末尾又直接给了：

- `BYBIT_SYMBOL=BTCUSDT`
- `BYBIT_BUDGET_USD=50`

这类小不一致恰好说明：

> **它是一个很好的策略工程样板，但不是一份已经被严肃验证过的研究结论。**

这也意味着我们更该把它当作“完整策略壳候选”，而不是现成 production truth。

## 6. 它和 `1m / 3m / 5m / 15m` 的关系怎么理解

### 6.1 这条 alpha 的原生时间尺度其实比 `1m` 更快

严格说，这条策略并不是 K 线形态 alpha：

- 主循环约 `1s`
- 依赖 orderbook best bid / ask
- 依赖 tick size、lot size
- 依赖 quote refresh

所以它的**原生战场**更接近：

- sub-minute
- `1m`
- `3m`

而不是纯 `15m` candle alpha。

### 6.2 但它依然能服务 `5m / 15m` desk

对当前 desk，更合理的映射方式不是“强行把信号 bar 化”，而是：

- **`1m / 3m`**：做 execution / fill / inventory / net capture 主评估层
- **`5m`**：做 spread percentile、mid drift、inventory utilization 的聚合层
- **`15m`**：做 regime / funding / event risk / volatility state 的开关层

也就是说，这条 alpha 可以这样 desk 化：

> **执行在 `1m/3m`，风险与是否开 maker 在 `5m/15m`。**

这和我们当前短周期研发目标并不冲突，反而能补齐“更快、更偏执行”的 alpha 家族。

## 7. 最小可复现实验应该怎么定义

如果要最快验证，我不会先碰 live，而是先做一个**公开数据 fill-proxy 版最小实验**。

### 7.1 数据源

全部公开可得：

- Bybit V5 public orderbook websocket（BBO / L50 都可以）
- Bybit public trades
- Bybit instruments info（tick / lot / min qty）
- funding history / current funding（公开可得）

更新频率：

- orderbook / trades：秒级甚至更快
- funding：低频，但可并到持仓收益里

### 7.2 最小实验口径

第一版不用追求完美撮合，只要先回答：

> **这条 maker edge 有没有“扣掉现实摩擦后仍可能存活”的可能性？**

第一版口径可以是：

1. 每 `1s` 取一次 BBO / mid；
2. 按 repo 逻辑生成 bid / ask ladder；
3. 用“触价 / trade-through / queue haircut”三档 fill proxy 做成交；
4. 记账时显式扣：
   - maker fee / rebate
   - stale-quote adverse selection buffer
   - funding
5. 最后把 PnL 聚合到 `1m / 3m / 5m / 15m` 看稳定性。

### 7.3 第一版最该看的不是收益曲线，而是四个诊断量

第一版我最想先看这四个量：

- 每分钟 passive fill ratio
- 每笔 realized capture（扣 fee 前后）
- inventory half-life
- drift hit 后的 adverse selection 损失

因为 maker alpha 的核心不是“预测对几次”，而是：

> **被动成交以后，净 capture 还剩多少。**

## 8. 我对这条材料的结论

### 8.1 值得 intake 吗？
**值得。**

因为它满足：

- raw alpha
- 可独立复现
- 能直接落地成完整策略
- 公开数据可做最小实验
- 能补当前素材池里相对缺的 maker / liquidity provision 家族

### 8.2 现在就能当 production 吗？
**不能。**

原因也非常明确：

1. 默认 edge 太薄；
2. repo 更像工程模板，不像严肃验证结论；
3. 真实胜负手在 queue / latency / adverse selection，不在 README；
4. 还没看到 walk-forward、fee-tier 分层、不同 symbol 的稳健性证据。

### 8.3 最准确的 desk 化定位

我会把它定位成：

> **中高优先级的 maker raw alpha 壳：先验证净 capture、生存成本线和库存周转，再决定它是独立 sleeve，还是作为 execution / liquidity overlay 服务别的 raw alpha。**

## 9. 下一步怎么测

### 实验 A：先跑一版公开数据 fill-proxy 回测

最小网格：

- 标的：`BTCUSDT / ETHUSDT / SUIUSDT`
- 频率：`1s` quote，聚合看 `1m / 3m / 5m`
- spread floor：`0.2 / 0.5 / 1.0 / 2.0 bps`
- ladder：`1 / 2 / 3` 层

目的：

> 看“结构成立”还是“默认参数太薄”。

### 实验 B：单独做成本 / adverse selection 生存线

至少并排测：

- maker fee / rebate：`-1 / 0 / +1 bps` 每边
- stale-quote penalty：`0 / 0.5 / 1 tick`
- drift cancel 阈值：`1 / 2 / 5 ticks`

通过条件不是收益最大，而是：

> **有没有一块参数区间在保守摩擦下仍为正。**

### 实验 C：做 symbol 分层，不要只看 BTC

这份 repo 的结构天然适合做 symbol stratification：

- `BTCUSDT`：点差窄，但深度更稳
- `ETHUSDT`：可能是折中样本
- `SUIUSDT`：notional 小，但更容易受跳价和库存冲击影响

如果最后发现：

- BTC 太挤
- SUI 太跳
- ETH 最平衡

那就别再把它写成“通用 Bybit 做市 alpha”，而要直接收缩成**symbol-specific sleeve**。

### 实验 D：如果独立 edge 不够厚，就把它降级成共享 execution / overlay 组件

如果最终发现：

- 独立跑净 capture 不够厚；
- 但 spread 宽、mid drift 低、inventory 周转快时表现明显更好；

那它依然有价值，只是身份要降级为：

- maker-on / maker-off gate
- 被动卸仓层
- 低冲击 execution overlay

也就是：

> **别硬保 raw alpha 身份；能服务其他 raw alpha 也完全值得留下。**

## 10. 参考资料

1. **Sebastian Boehler. (2025). _bybit_market_maker_cpp_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/SebastianBoehler/bybit_market_maker_cpp>  
   - Repo URL: <https://github.com/SebastianBoehler/bybit_market_maker_cpp>

2. **Repo source files used in this digest**  
   - README: <https://raw.githubusercontent.com/SebastianBoehler/bybit_market_maker_cpp/main/README.md>  
   - strategy.cpp: <https://raw.githubusercontent.com/SebastianBoehler/bybit_market_maker_cpp/main/src/strategy.cpp>  
   - main.cpp: <https://raw.githubusercontent.com/SebastianBoehler/bybit_market_maker_cpp/main/src/main.cpp>  
   - trading_helper.cpp: <https://raw.githubusercontent.com/SebastianBoehler/bybit_market_maker_cpp/main/src/trading_helper.cpp>  
   - .env.example: <https://raw.githubusercontent.com/SebastianBoehler/bybit_market_maker_cpp/main/.env.example>

3. **Bybit API documentation (V5)**  
   - Venue: Bybit Docs  
   - DOI: N/A  
   - Readable URL: <https://bybit-exchange.github.io/docs/v5/intro>  
   - Public market data / orderbook docs: <https://bybit-exchange.github.io/docs/v5/market/orderbook>  
   - WebSocket docs: <https://bybit-exchange.github.io/docs/v5/ws/connect>
