# 别把这份 2026 repo 继续读成 breakout：代码里真正活下来的，是「200-bar Donchian overshoot fade × 10bps breach」BTC 15m raw alpha

- 时间：2026-04-01 01:13 UTC
- 类型：2026 GitHub repo `README.md` + `notebooks/04_breakout_strategy.py` + `notebooks/05_breakout_extension.py` + `notebooks/06_pairs_strategy.py` + `notebooks/07_pairs_strategy_vol_filter.py` + `report/tables/*.csv` source audit
- 主题标签：raw-alpha/single-asset/mean-reversion/donchian/overshoot-fade/high-vol-admission/threshold/btc/binance/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：仓库源码 + 回测表格 + 失败对照（lead-lag / pairs）
- 主题类型：raw alpha
- 基础 alpha：当 BTC `15m` 收盘价显著穿出过去 `200` 根 Donchian 区间后，做 **过度延伸后的回归**；赚的不是 breakout continuation，而是 **极端偏离回到区间内部** 的均值回复。高波动只是 admission layer，不是 alpha 本体。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次为什么选它
先回答一句：**这篇东西的 base alpha 是什么？**

答案很清楚：

> **single-asset intraday overextension mean reversion**。
> 具体说，就是 BTC 在 `15m` 上向上/向下显著穿出一个很长的历史区间后，下一段更容易先往区间里回，而不是立刻继续顺着突破方向跑。

它不是 filter，也不是纯执行优化，更不是“看 breakout 名字就默认 trend”。
这份 repo 里最值得 desk 抄的，反而是一条 **可独立交易、带完整出入场与成本口径的单币均值回复 raw alpha**。

更关键的是，它不是拍脑袋挑出来的。repo 自己先测了三条线：

1. **BTC→ETH/DOGE lead-lag**：基本没显著性；
2. **BTC–ETH pairs**：样本内还能看，样本外被成本打穿；
3. **BTC 单币 Donchian 极端偏离回归**：样本外反而还活着。

这很适合当前 desk：不是再补一个共享 filter，而是补一条 **原生 15m、公开数据可复现、完整策略骨架清楚** 的 raw alpha。

## 2. 先把 repo 真正在说什么讲明白
主来源：

1. **Sidney Yin (2026)**  
   *COMP0051 Algorithmic Trading Coursework*  
   - Venue: GitHub coursework repo  
   - DOI: N/A  
   - Readable URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>  
   - Repo URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>

repo 表面上把其中一条模块叫作 `breakout_strategy`，但代码实际上写的是：

- `upper_band = rolling_max(200).shift(1)`
- `lower_band = rolling_min(200).shift(1)`
- `long_entry = close < lower_band`
- `short_entry = close > upper_band`

也就是：

- 跌破过去 `200` 根低点 -> **做多**
- 突破过去 `200` 根高点 -> **做空**

这不是 trend-following breakout；这是 **Donchian overshoot fade**。

而且 baseline 版本已经带了一个很朴素但有用的 admission：

- `rolling_vol = std(ret, 50)`
- 只有当 rolling vol 高于样本内 `60%` 分位数时才允许入场。

翻成人话：

> **不是“安静区间的小假突破”去做回归，而是专抓高波动里真正甩出区间的那种 overextension。**

## 3. 这条线为什么比 repo 里其他路线更值得进池
### 3.1 lead-lag 这条线，在这份 repo 里其实已经被否掉了
`conditional_returns.csv` 给的 BTC→ETH / BTC→DOGE 条件前瞻收益几乎都不显著：

- BTC 上涨后，ETH `1-bar` 前瞻均值只有 `-0.8934 bps`，t-stat `-0.9292`；
- BTC 上涨后，DOGE `3-bar` 前瞻均值 `1.5082 bps`，t-stat `1.3315`；
- BTC 下跌后的 ETH/DOGE 各种 `1~3 bar` 前瞻收益，p-value 也都远不显著。

`cross_correlations.csv` 也很直白：

- `lag 0` 同步相关很高（BTC→ETH `0.865996`；BTC→DOGE `0.770541`）；
- `lag ±1~4` 基本都在零附近。

也就是说，这个 repo 自己给的证据更像在说：
**别再把“BTC 先动、alts 跟随”默认当 15m 可收费 raw alpha。**

### 3.2 pairs 也不是这份 repo 里真正的幸存者
`pairs_summary.csv` 里只有 BTC–ETH 真正通过 cointegration：

- Engle–Granger `p = 0.0065`
- spread ADF `p = 0.0015`
- half-life `392.37 bars`，约 `98.09 小时`

但落到真实交易规则和 `5 bps` 成本后，`pairs_performance.csv` 的样本外结果并不好：

- **样本外 net PnL = `-2000.32 USD`**
- **样本外 Sharpe = `-1.2971`**
- `28` 笔交易，平均每笔 `-71.7 USD`

说明这份 repo 里，**统计上 cointegrated** 不等于 **短周期交易后还能剩下净边**。

### 3.3 真正活下来的，是单币极端偏离回归
repo 的 `breakout_extension_comparison.csv` 反而给出很清楚的答案：

#### Baseline：200-bar 区间外侧直接反手 + 高波动 admission
- OOS net PnL：`9260.84 USD`
- OOS Sharpe：`1.5113`
- OOS trades：`36`
- OOS win rate：`61.11%`

#### Test A：在 baseline 上再加 `10 bps` breach threshold
- OOS net PnL：`9872.83 USD`
- OOS Sharpe：`1.6722`
- OOS trades：`35`
- OOS win rate：`62.86%`

#### Test B：再进一步改成 `20%~80%` 中间波动带过滤
- OOS net PnL：`-9406.37 USD`
- OOS Sharpe：`-2.2350`
- OOS win rate：`44.12%`

这个对 desk 非常重要：

> **最值钱的不是“多加 filter”，而是“极端偏离本身 + 轻量 threshold”。**
> 过度精致的 regime band 反而把 alpha 自己掐死了。

## 4. 我会把它怎么定性
这条线的正确分层应该是：

- **raw alpha 本体**：Donchian 区间外的短周期过度延伸回归
- **有效 confirmation**：`10 bps` 额外穿透阈值
- **admission / filter**：只在较高波动时入场（rolling vol > 60th pct）
- **反例提醒**：不要把“中等波动才做”当真理，repo 的 OOS 结果已经告诉你这层会伤害 alpha

所以它是 **raw alpha 主体清楚、filter 只是辅助** 的好题，而不是“一个需要挂靠别的主信号的共享 gate”。

## 5. 直接抄成 desk 语言：完整策略骨架长什么样
### 策略定义
- 标的：BTC（先用 Binance `BTCUSDT` spot 或 perp）
- 频率：原生 `15m`
- 家族：single-asset mean reversion
- 成本假设：先从 `5 bps` all-in 开始

### Entry
取 `05_breakout_extension.py` 里样本外更优的 **Test A**：

- `upper_band = max(close, 200).shift(1)`
- `lower_band = min(close, 200).shift(1)`
- `rolling_vol = std(ret, 50)`
- `vol_filter = rolling_vol > in-sample 60th percentile`
- **Long**：`close < lower_band * (1 - 0.001)`
- **Short**：`close > upper_band * (1 + 0.001)`

也就是：

- 不只是刚碰到区间边界；
- 要 **真正多走 10 bps** 才承认是足够 extreme 的 overshoot。

### Exit
source 规则很简单：

- 出现反向极端信号则平仓；
- 或者最多持有 `40` 根 `15m` bar（约 `10 小时`）。

第一版 desk 化时，我会保留这个骨架，不急着加太多复杂出场。

### Sizing
source 用的是固定 `100,000 USD` gross notional。

真正落到 desk，建议第一版改成：

- 单笔风险按 `rolling 50-bar vol` 做 volatility targeting；
- 或者至少把 notional 设成 `target_sigma / rolling_vol` 的反比；
- 但别在第一轮就把 sizing 优化得比信号还复杂。

### Risk / cost
source 的成本模型是：

- 每次仓位变化按 `5 bps` 计费；
- `+1 -> -1` 这种翻向按两次交易算；
- 没有假装自己能零摩擦成交。

这点很重要，因为 pairs 那条线正是被成本打穿的。

## 6. 为什么这条 alpha 对 5m / 3m / 1m 也有研究价值
虽然 repo 原生是 `15m`，但它对短周期 desk 仍然很实用，因为它回答的是一个更一般的问题：

> **当价格以“足够极端”的方式离开一个慢窗口区间时，下一段到底更像 continuation 还是 snap-back？**

这个问题完全可以向下迁移。

### 迁移到 5m 的两种最小口径
#### A. 保持“时钟长度”不变
把 source 的 `15m` 配置平移到 `5m`：

- `N=200` -> `600 bars`（仍约 50 小时）
- `VOL_WINDOW=50` -> `150 bars`
- `MAX_HOLD=40` -> `120 bars`
- `threshold = 10 bps` 保持不变

这测的是：**同样 2 天左右慢窗下，5m 更细粒度执行能不能把均值回复吃得更干净。**

#### B. 保持“bar 数”不变
直接在 `5m` 继续用：

- `N=200`
- `VOL_WINDOW=50`
- `MAX_HOLD=40`

这测的是：**更快的 micro-overshoot 有没有自己的独立 alpha。**

我会优先先跑 A，再跑 B。因为 A 更像 source faithful transfer，B 更像新 alpha 分支。

## 7. 这条线最值得 desk 学的，不只是结果，还有“别乱加过滤器”
repo 给了一个很少见但很实用的结论：

- baseline 已经能活；
- 再加一个轻量 `10 bps` threshold，OOS 更好；
- 但继续加“只做中等波动、不做太低也不做太高”的双边 vol band，结果直接转负。

这说明当前这条 alpha 更像：

- 需要 **真正 extreme 的位移**；
- 允许 **高波动里的 overreaction**；
- 不需要一个看起来更“精致”的 volatility regime theory。

翻成人话就是：

> **别把 entry 做得比 alpha 还聪明。**
> 如果市场已经给了你“跑出 200-bar 区间还多走 10 bps”的极端信息，就别再用漂亮但过拟合的 vol band 去替市场做第二层否决。

## 8. 我对这条线的判断
我会把它放进当前研究池，而且优先级不低，原因有四个：

1. **raw alpha 很清楚**：不是 filter、不是解释卡；
2. **原生就是 15m**：和当前 desk 默认频段一致；
3. **完整策略组件齐全**：entry / exit / cost 都可直接抄；
4. **repo 内部已经做了失败对照**：lead-lag、pairs 都没它诚实。

如果这轮还要继续补 raw alpha 素材池，我宁愿先补这种：
**简单、极端、成本后仍有机会活的单币回归**，
而不是再写一个听起来更 fancy 的 shared gate。

## 9. 下一步怎么测
我建议直接按三阶段跑，别再停在“看起来挺合理”。

### Phase A：source-faithful reproduction（先 15m）
- 市场：Binance `BTCUSDT` spot + perp 各跑一遍
- 周期：`15m`
- 规则：
  - `N=200`
  - `VOL_WINDOW=50`
  - `vol > 60th pct`
  - `threshold=10 bps`
  - `MAX_HOLD=40`
- 成本：`3 / 5 / 8 / 10 bps`
- 输出：
  - OOS Sharpe / net PnL / trade count / win rate
  - per-trade expectancy
  - 持有期分布

**第一问只看一件事：5 bps 以上它还活不活。**

### Phase B：transfer to 5m
跑两组转译：

- **Clock-preserving**：`600 / 150 / 120`
- **Bar-preserving**：`200 / 50 / 40`

然后比较：

- threshold 还要不要固定 `10 bps`
- 是否应该改成 `k × ATR` 或 `k × rolling sigma`
- OOS 是否从“单币回归”滑成“纯噪声反手”

### Phase C：做成可实盘 admission 模块
若 15m/5m 都还能活，再加三层现实化：

1. **funding veto**：perp 逆势仓是否被 funding 吃掉；
2. **session split**：亚洲/欧洲/美盘哪个时段 snap-back 更强；
3. **maker/taker split**：边界外 10 bps 的 alpha，实际还能留多少给执行。

## 10. 我最想优先验证的 3 个假设
### 假设 1：真正关键的不是 Donchian 本身，而是“极端穿透”
也就是：

- `touch band` 可能不够；
- `breach by 10 bps` 才比较像可收费 alpha；
- 这层可能比你额外叠 3 个 filter 都更值钱。

### 假设 2：这条线在高波动里反而更好，不该过早做双边 vol 剔除
repo 的 Test B 已经给了负面证据。

desk 要验证的，是不是：

- 高波动 = alpha 的燃料；
- 而不是“越规整的 regime 越安全”。

### 假设 3：这条线更适合 BTC 单币，不要急着横向扩到一篮子 alts
因为这份 repo 里：

- lead-lag 没显著；
- pairs 被成本打穿；
- 真正 surviving 的反而是 BTC 自己。

所以第一轮别贪多，先把 BTC 单币打透。

## 11. 公开数据与最小复现口径
### 数据源
1. **Binance public klines**  
   - 标的：`BTCUSDT` spot / perpetual  
   - 公开性：公开可得  
   - 更新频率：分钟级 / 历史批量可拉

2. **Binance public taker flow / aggTrades（可选）**  
   - 用途：后续判断 overshoot 后的反手执行是否值得 maker 化  
   - 公开性：公开可得

### 最小可复现实验口径
- bar：`15m` 先跑，`5m` 次之
- 信号：按 repo 原始 Donchian + vol + threshold
- 成本：固定 bps all-in
- 输出：
  - total net PnL
  - OOS Sharpe
  - trade count
  - holding bars
  - cost / gross 比例

## 12. 来源
1. **Sidney Yin (2026). _COMP0051 Algorithmic Trading Coursework_. GitHub repository.**  
   - Venue: GitHub / coursework repo  
   - DOI: N/A  
   - Readable URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>  
   - Repo URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>

2. **Source files used in this digest**  
   - `notebooks/04_breakout_strategy.py`  
   - `notebooks/05_breakout_extension.py`  
   - `notebooks/06_pairs_strategy.py`  
   - `notebooks/07_pairs_strategy_vol_filter.py`  
   - `report/tables/breakout_extension_comparison.csv`  
   - `report/tables/pairs_performance.csv`  
   - `report/tables/pairs_summary.csv`  
   - `report/tables/conditional_returns.csv`  
   - `report/tables/cross_correlations.csv`

3. **Binance public market data**  
   - 用途：BTC `15m/5m` 最小复现  
   - 公开性：公开可得  
   - 更新频率：分钟级 / 历史批量可拉