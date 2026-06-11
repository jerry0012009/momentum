# 别把 `binance_grid_trader` 只读成“挂机网格”：对 short-cycle crypto desk，更该先回答的是「bounded-range oscillation × one-step ladder capture」这条 raw alpha 壳到底适不适合 `5m/15m`
- 时间：2026-04-21 19:50 UTC
- 类型：GitHub / repo source audit + Binance public-data range-occupancy probe
- 主题类型：raw alpha
- 基础 alpha：在一个预先定义的价格区间内，价格会反复围绕局部公平价来回摆动；策略不是猜方向，而是用分层买卖单去连续收割“走一格又走回来”的一阶均值回复
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：single-asset / mean-reversion / grid / ladder / range-trading / maker-first / Binance / 5m / 15m
- 证据类型：repo 工程骨架 + public-data first probe

## 1. 这次看了什么
这轮主来源是 GitHub 仓库 **51bitquant / binance_grid_trader**。它表面上像“老派现货/合约网格 bot”，但如果按我们 desk 的 intake 口径重读，真正该先问的不是“网格能不能挂机赚钱”，而是：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 bounded-range oscillation mean reversion。**
>
> 也就是：只要价格还在某个已知区间里来回摆，单次摆动常常足够走完至少一格；策略就靠下方挂买、上方挂卖，反复吃“回到上一格”的小额回复，而不是押单边趋势。

来源与关键代码：
- **Repo**：51bitquant (ongoing), *Binance Grid Trader*
- **Repo URL**：<https://github.com/51bitquant/binance_grid_trader>
- **Readable URL**：<https://github.com/51bitquant/binance_grid_trader/blob/master/README.md>
- **关键代码**：
  - `gridtrader/trader/strategies/future_grid_strategy.py`
  - `gridtrader/trader/strategies/spot_grid_strategy.py`
  - `main_futures_script.py`
  - `main_spot_script.py`

## 2. repo 里真正可交易的壳是什么
这份 repo 的骨架非常直接：
- 用户先给定 `upper_price / bottom_price / grid_number`
- 系统算出 `step_price = (upper - bottom) / grid_number`
- 当前价附近只保留有限层数的挂单，靠 `max_open_orders` 控制两侧挂单深度
- 买单成交后，自动在上一格挂对应卖单；卖单成交后，自动在下一格挂对应买单
- 现货版额外做了余额检查和“离盘口太远就撤单”的保护；期货版则更像纯对称中性网格

翻成人话，就是：
1. 先假设“这一段不是趋势，是箱体”；
2. 再把箱体切成很多小台阶；
3. 每次只赚一格，不试图吃整段波段；
4. 真正的大敌不是信号缺失，而是**价格离开箱体后继续单边走**。

所以这不是 trend / breakout alpha，而是一个**完整的 range-MR shell**：
- 入场：挂在局部价差台阶上
- 出场：回到相邻上一格/下一格
- sizing：`order_volume × max_open_orders`
- risk：区间上/下边界 + 撤单逻辑
- cost：天然高度依赖 maker/taker 结构

## 3. 为什么它值得进研究池
它虽然不新，但对我们当前 desk 仍有两点价值：

### 3.1 它是少数能直接落成完整策略的 raw alpha 壳
很多 repo 只给信号，不给出场；这份网格仓反过来，**信号几乎就等于出场机制本身**。这对 `1m/3m/5m` 很重要，因为短周期里很多 edge 不是“方向猜得准”，而是“能不能稳定把小回复装进交易壳里”。

### 3.2 它天然提醒我们：grid 不是 alpha-free lunch，而是“卖趋势、买震荡”
也就是说，grid 本体能否活，不取决于它会不会挂单，而取决于：
- 设的区间是不是对的
- 每一格够不够厚
- 趋势 breakout 来时止损/停机够不够快

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 区间均值回复
- 基础 alpha：bounded-range oscillation × one-step ladder capture
- regime：横盘 / 低到中等单边强度、价格仍留在已定义区间内
- filter / veto：超出区间、波动突然放大、连续单边 bucket 跳跃过多时应停机
- risk / sizing / execution overlay：`order_volume`、`max_open_orders`、maker-first、突破边界即撤单/减仓/平仓

## 4. 我们自己的 public-data first probe
我这轮没直接硬做整套成交仿真，而是先用 Binance public data 做了一个更适合 grid 的快检：
**看“过去 24h 区间”对 `5m/15m` 是否足够稳定，以及一旦 break，损伤有多大。**

probe 口径：
- 市场：Binance Spot `BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`5m`、`15m`
- 样本：最近约 `2500` 根 bar / symbol
- 设定：用过去 `24h` rolling high-low 当动态箱体，`grid_number = 40`
- 指标：
  - `in_range_pct`：价格留在箱体里的占比
  - `avg_step_bps`：一格大约多厚
  - `bucket_cross_per_day`：一天大约能跨几格
  - `breakout drift`：一旦离开箱体，后面几个 bar 最远还能顺着走多远

摘要文件：
- `reports/artifacts/quant_digests/2026-04-21_grid_range_probe_summary.csv`

核心数字：
- **5m** 下，`BTC / ETH / SOL` 的 `in_range_pct` 约 **98.3% / 99.0% / 97.9%**
- 同样 `5m`、`40` 格设定下，平均单格厚度约 **8.45 / 11.36 / 11.42 bps**
- 但一旦发生 breakout，`5m` 的 `p90` 顺势延伸仍有 **90 / 101 / 122 bps**；到 **15m**，`p90 breakout drift` 更扩大到 **133 / 187 / 166 bps**

一句话结论：

> **箱体内的小回复很密，但 breakout 的伤害是“很多格一起赔回去”；所以 grid 可以是 raw alpha 壳，但绝不能当成无条件 always-on。**

这也解释了为什么 grid 更适合作为：
- `1m/3m/5m` 的 maker-ish range sleeve
- 或 `15m` 上先做 regime admission，再把执行下沉到更细周期

而不适合直接拿 `15m` K 线裸跑。

## 5. 为什么和当前项目有关
这轮最有价值的，不是“我们也去做一个老网格机器人”，而是补齐一个此前研究池里相对少见的完整壳：
- 它属于 **single-asset mean reversion**，但不是 RSI/BB 那种点状反打
- 它强调的是 **持续小幅回摆的交易壳设计**
- 它和我们已有的 panic-bounce / oversold fade / basis MR 不同，补的是 **range inventory harvesting** 这一块

对当前 desk，更合适的读法是：
1. 先别把它当“主策略”；
2. 先把它当 **震荡 regime 专用 sleeve**；
3. 再去验证它能不能和 trend sleeve 做开关互补。

## 6. 下一步怎么测
最小实验建议直接做三步：
1. **Regime gate**：先用 `ADX / rolling drift / breakout-count` 把 bar 分成 range vs trend；
2. **Child execution**：只在 range 段运行 `5m` parent grid，并把挂单执行细化到 `1m` 或 `bookTicker`；
3. **成本梯度**：至少比较 `maker 1bps / maker 2bps / taker 4bps+` 三档，看单格厚度还能剩多少。

最先该看的不是收益曲线，而是两件事：
- `grid capture / breakout loss` 比值
- `停机是否足够快，能不能防止单次趋势把前面小利润全吞掉`

如果这两件事不过线，就说明它更适合作为 overlay / 子执行框架，而不是 standalone 主 alpha。

## 7. 风险与保留意见
- 这类 repo 最大的问题不是代码复杂，而是**区间设定太主观**；上/下边界错了，整个策略就会从“收震荡”变成“逆趋势硬扛”。
- 我这轮 probe 只做了“区间占用率 + breakout 伤害”的 first verdict，**还不是完整成交级回测**。
- 真实可交易性极度依赖手续费和挂单成交率；若大部分成交被迫吃 taker，edge 会被迅速打穿。
- 因此当前更稳妥的判断是：**这条线值得入池，但优先级应是“range sleeve / maker-first execution shell”，不是直接升成 `15m` 主策略。**

## 8. 来源
- 51bitquant. *Binance Grid Trader*. GitHub repository.
- Repo URL: <https://github.com/51bitquant/binance_grid_trader>
- README: <https://github.com/51bitquant/binance_grid_trader/blob/master/README.md>
- Raw code:
  - <https://raw.githubusercontent.com/51bitquant/binance_grid_trader/master/gridtrader/trader/strategies/future_grid_strategy.py>
  - <https://raw.githubusercontent.com/51bitquant/binance_grid_trader/master/gridtrader/trader/strategies/spot_grid_strategy.py>
