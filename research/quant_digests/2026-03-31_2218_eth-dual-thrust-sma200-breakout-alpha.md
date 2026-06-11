# 别把这份 2026 新 repo 只当“又一个 breakout 排行榜”：对 desk 更该先测的是「3-day adaptive range breakout × SMA200 bull gate」ETH 单币完整 raw alpha，而且执行优先 5m、不要先上 15m

- 时间：2026-03-31 22:18 UTC
- 类型：2026 GitHub 新仓库 `README.md` + `docs/strategies/dual_thrust.md` + `research/phase_13_dual_thrust_cusum.py` + `docs/results/14_final_rankings.md` + Binance USDⓈ-M Perpetual 公开 `5m/15m` 本地 transfer check
- 主题标签：raw-alpha/trend/breakout/dual-thrust/adaptive-range/sma200/regime-gate/eth/single-asset/binance-perpetual/5m/15m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub 仓库 source audit + Binance USDⓈ-M Perpetual 公共数据最小 transfer check

- 主题类型：raw alpha
- 基础 alpha：**前 3 日自适应波动区间定义出的上沿突破，在 bull regime 下更容易延续；对 desk 更可交易的第一版是 ETH long-only breakout，而不是对称多空 breakout。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是论文，而是一份刚创建并持续更新的 2026 GitHub 新仓库：**`timrecursify/trading-strategies`**。repo 自己做的是一轮很硬的系统化筛选：
- `70,000+` 次回测；
- `16` 个 research phases；
- Binance USDT-M `BTC/ETH` 永续 `1m` 数据；
- 覆盖约 `6.3` 年；
- 结论里直接把 **ETH Dual Thrust + SMA200** 排到全项目第一。

对我们现在这条 desk 主线，它有价值，不是因为“又找到一个 breakout”，而是因为它提供了一条**可独立站住、规则非常完整、而且跟最近几篇 pairs / basis / cross-venue intake 不重复**的 directional raw alpha：

**用过去 3 天的自适应区间去定义今天的 breakout trigger，只在长期 bull regime 做向上突破，并把 entry / exit / stop / cost shell 都说清楚。**

更关键的是，我顺手核了源码后发现：
**repo 的最优版并不是很多人脑补的“对称多空 breakout”，而更接近 `bull regime 下只做 long breakout`。**
这点对我们 desk 很重要，因为它让这条线从“老派对称通道策略”变成了一个更贴近 crypto 长期偏多结构的可执行原型。

## 2. 为什么这次值得进研究池
结合最近学习进展，我们这两天已经补了很多：
- funding / basis / spot-perp / perp-perp carry；
- cross-venue same-underlier arb；
- pairs / cointegration / basket stat-arb；
- 以及一些 lead-lag / loser basket / cross-sectional 方向。

这些 intake 很有用，但也有一个现实：
**如果素材池长期只补 relative-value / carry / pairs，而不继续补“能单独下场”的 directional raw alpha，后面组合时会越来越像只有 hedge legs、没有主发动机。**

这份新 repo 值得补，正因为它满足了本轮更高优先级要求：
1. **base alpha 说得清**，不是 filter 伪装成 alpha；
2. **完整策略壳齐全**，entry / exit / risk / cost 都能直接写；
3. **是 2026 新 repo**，不是把旧 breakout baseline 又翻出来炒冷饭；
4. **和当前项目已有 breakout 主线能形成“新证据 vs 老模板”对照**，但又不需要重新回到老 breakout 内循环。

翻成人话：
这不是让 bot7 再去死磕“裸 breakout 有没有用”，而是把一个**更诚实、更自适应、更像完整交易系统的 breakout 原型**补进 raw alpha 素材池。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 当市场处在 bull regime 时，价格一旦向上突破“由过去 3 天波动范围定义的自适应 trigger”，后续更容易出现日内延续。**

所以它本质上是：
- `trend`
- `momentum`
- `breakout`
- `single-asset directional raw alpha`

但不是：
- 单纯固定 Donchian 上轨；
- 纯 session bias；
- 也不是“无脑多空对称突破”。

对我们最重要的重读是：
**repo 里最值得拿走的不是“Dual Thrust 这个名字”，而是“adaptive range breakout + bull-only admission”这层结构。**

## 4. 核心来源
### 4.1 主仓库
- **Author / Owner**：`timrecursify`
- **Year**：2026（repo 创建于 `2026-03-25`，最近 push `2026-03-31`）
- **Title**：*Crypto Futures Day Trading Research*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL / Repo URL**：https://github.com/timrecursify/trading-strategies

### 4.2 这次实际重点看的文件
- `README.md`
- `docs/strategies/dual_thrust.md`
- `research/phase_13_dual_thrust_cusum.py`
- `docs/results/14_final_rankings.md`

### 4.3 本地最小快检数据源（公开可得）
- Binance USDⓈ-M Perpetual klines：`https://fapi.binance.com/fapi/v1/klines`
- 数据公开性：完全公开，无需私有 key 就能先做最小实验
- 更新频率：秒级时间戳，聚合到 `5m / 15m` 足够

## 5. repo 里最该拿走的硬点
### 5.1 这不是静态 breakout，而是自适应区间 breakout
repo 的 Dual Thrust 不是简单 `rolling_high(n)`：

先对过去 `N=3` 天计算：
- `HH = max(high)`
- `HC = max(close)`
- `LC = min(close)`
- `LL = min(low)`
- `range = max(HH - LC, HC - LL)`

然后当天 trigger：
- `buy_trigger = today_open + K * range`
- `sell_trigger = today_open - K * range`
- 其中最优参数是 `K = 0.5`

这层设计的意义很直接：
**触发门槛会跟最近几天波动状态一起伸缩，而不是像固定通道那样在扩波和缩波时都用同一把尺子。**

### 5.2 repo 真正的赢家不是“对称突破”，而是带 bull gate 的 long breakout
`research/phase_13_dual_thrust_cusum.py` 里最值得注意的一点是：
- 当 `regime=None` 时，策略允许上下双边 breakout；
- 当 `regime='sma200'` 或 `regime='sma50'` 时，代码只保留 **long breakout**，short side 不再开。

也就是说，repo 排名第一的那条线，实质上更像：
**`昨日 close > SMA200` 时，才允许做今日上破的 long breakout。**

这对 desk 的启发比“又一个 breakout”重要得多：
- 原始 alpha 是突破延续；
- `SMA200` 不是附属装饰，而是把它从“噪音突破机”改造成“只在对的环境做多”的 admission gate；
- 第一版根本没必要对称地把 short side 一起带上。

### 5.3 这是少数把完整交易壳写得很清楚的 directional repo
repo 给出的最优版参数非常完整：
- `Pair = ETHUSDT`
- `N = 3`
- `K = 0.5`
- `Entry window = 07:00 ~ 16:00 UTC`
- `Stop loss = 1.0%`
- `Time exit = 16:00 UTC`
- `Regime filter = Price > SMA200`
- `Risk per trade = 2% of account`
- `Max leverage = 10x`
- 成本模型：taker `0.04%` + slippage `0.01%` per side，即 **round-trip 10 bps**

这基本已经不是“研究灵感”，而是接近完整执行规范。

## 6. repo headline 里最值得记下来的数字
按 repo 的 `README` / `final rankings`：
- `70,000+` backtests
- `6.3` 年 ETH/BTC 永续分钟级样本
- 最优策略：**ETH Dual Thrust (N3 K0.5 SMA200)**
- **年化固定仓位收益约 `+39%`**
- **最大回撤 `12.4%`**
- **Return / Drawdown = `19.63`**
- **总交易数 `488`**
- **胜率 `35.5%`**

这里面最有信息量的不是胜率，而是：
- 低胜率但高盈亏比 / 好回撤；
- 跨 `6+` 年还能站住；
- 在 repo 自己那套统一成本壳下仍排第一。

## 7. 本地最小 transfer check：压到 desk 常用 `5m/15m` 后，先别急着把 15m 当默认执行
我做了一个非常粗但方向足够的 public-data proxy：
- 标的：Binance USDⓈ-M `ETHUSDT`
- 样本：最近约 `210` 天
- 规则：
  - 前一日 `close > SMA200`
  - 用前 `3` 天 daily `HH/HC/LC/LL` 算 `range`
  - 当日 `07:00 UTC` 的 open 作为 anchor
  - `buy_trigger = open + 0.5 * range`
  - 只做 long breakout
  - 止损 `1%`
  - `16:00 UTC` 时间止盈/止损退出
  - 成本按 **round-trip 10 bps**

### 7.1 5m proxy：虽然交易数不多，但至少像个可交易原型
最近约 `210` 天的 `5m` proxy：
- trades：**7**
- win rate：**85.7%**
- avg raw：**`+118.55 bps / trade`**
- avg net：**`+108.55 bps / trade`**
- total net：**`+7.60%`**
- stop rate：**14.3%**
- profit factor：**7.91**

这不是正式验证，但足够说明：
**这条线压到 5m 执行后，没有立刻被成本打死。**

### 7.2 15m proxy：最近样本直接掉到成本线下方
同样规则压到 `15m`：
- trades：**7**
- win rate：**42.9%**
- avg raw：**`+1.56 bps / trade`**
- avg net：**`-8.44 bps / trade`**
- total net：**`-0.59%`**
- stop rate：**57.1%**
- profit factor：**0.87**

翻成人话：
**同样一条日内 breakout 骨架，15m 对这个策略来说已经太钝。**
它不是“不存在 alpha”，更像是：
- signal 可以日频定义；
- 但执行不能粗到 15m bar-close；
- 否则触发与止损都会被颗粒度扭坏。

### 7.3 对 desk 的直接结论
如果要把这条线收进当前素材池，**第一版不要写成“15m breakout strategy”**。
更诚实的写法应该是：

**`1d regime + daily adaptive trigger` 定义 alpha，`5m` 负责执行，`1m/3m` 只负责微调入场，不负责重新发明信号。**

## 8. 它和当前 `momentum` 主线怎么接
这条线跟项目内已有的 breakout / trend 学习有连接，但不等于回到老内循环：

### 8.1 它比老式裸 Donchian 更像一个完整原型
当前主线地图里我们已经知道：
- 裸 breakout 容易被噪音打爆；
- direction filter 很关键；
- 触发层和方向层最好拆开。

而这份 repo 给的正好是一个更鲜明的实例：
- **direction layer = SMA200 bull gate**
- **trigger layer = adaptive 3-day range breakout**
- **risk layer = 1% hard stop + 16:00 time exit**

### 8.2 它可以作为 trend/breakout 家族的“新证据卡”，不是继续围绕旧模板炼丹
当前 backlog 已经明确：
- 旧 Donchian breakout 更适合保留成触发模板；
- 不宜再围绕旧 baseline 微调内循环。

所以这次 intake 的正确定位不是“继续调 breakout”，而是：
**补一张新的 raw alpha 证据卡，让未来的 breakout/trend 研究不只靠项目内旧模板，而是有外部新 repo 的完整壳做对照。**

## 9. 怎么把它拆成完整策略
### 9.1 Entry
第一版先忠实：
1. `yesterday_close > SMA200_yesterday`
2. 计算前 `3` 日 `range = max(HH-LC, HC-LL)`
3. `buy_trigger = open_0700 + 0.5 * range`
4. 只要 `07:00~16:00 UTC` 期间第一次上破 trigger，就开 long
5. 当天只允许一笔，不反手、不重进

### 9.2 Exit
保持朴素：
1. `1%` stop
2. `16:00 UTC` 强平 time exit
3. 第一版先别叠加 trailing stop，避免把 repo 核心改散

### 9.3 Sizing
repo 给的是：
- `2% account risk`
- `1% stop`
- 允许最高 `10x`

对 desk 第一版更建议：
- 先做 fixed-risk / fixed-notional 两套；
- 再看 vol-target 版是不是改善 tail；
- 不要一上来就把 sizing 和信号缠死。

### 9.4 Risk / Cost
至少保留：
- 单日只打一枪；
- `07:00~16:00 UTC` 固定窗口；
- round-trip 成本先按 `10 bps`，再做 `6 / 10 / 14 bps` 梯度；
- 出现 `gap-through-stop` 时单独记坏样本，不要假装都能按止损价走。

## 10. 对 `1m / 3m / 5m / 15m` 的正确映射
### 10.1 `5m`：当前最自然的执行频率
这次 quick check 已经很说明问题：
- `5m` 至少还能留下正的 after-cost proxy；
- 触发、持有、止损都还没被 bar 粒度扭坏。

### 10.2 `15m`：更适合做 falsification card，不适合当第一版执行层
当前 proxy 里：
- `15m` 平均每笔只剩 `+1.56 bps` raw；
- 成本后直接转负；
- stop rate 飙到 `57.1%`。

所以 `15m` 在这条线上更像：
- 用来证明“别把 coarse execution 当成策略本体”；
- 而不是默认落地版本。

### 10.3 `1m / 3m`：先做 refinement，不做主信号
可以做的，是：
- breakout 后 `1~2` 根确认；
- 或 breakout 后的 micro pullback re-entry；
- 或者滑点 / gap-through-stop 的更细口径估算。

但不建议第一步就把整套信号改写成 1m 级噪音系统。

## 11. 局限与风险
1. **这是 repo-based 结论，不是正式论文。**
2. **我这次 public-data transfer check 的样本很小，只有 7 笔交易。** 只能当 first verdict，不能当正式 admission。
3. **repo 只覆盖 BTC/ETH，不能自动外推到 alt。**
4. **bull gate 很可能是核心，不应轻易删掉。** 一旦删 gate，可能又退回 generic breakout 噪音机。
5. **execution granularity 很敏感。** 同样规则压到 15m 就已经明显失真。

## 12. 我建议的“下一步怎么测”
### 实验 A：faithful 5m baseline
- 标的：`ETHUSDT perp`
- 时间：至少最近 `2~3` 年
- 规则：完全忠实 repo 的 `N=3 / K=0.5 / SMA200 / 1% stop / 16:00 exit`
- 成本：`6 / 10 / 14 bps`
- 目标：确认这条线在我们自己的执行口径下，after-cost 还剩多少

### 实验 B：`5m` vs `3m` execution refinement
- signal 仍保持 daily trigger 不变
- 只比较：
  - `5m first-touch entry`
  - `3m first-touch entry`
  - `5m breakout-confirmed-by-next-bar-close`
- 目标：判断 edge 是来自更细执行，还是来自“不要太迟钝”

### 实验 C：gate 对照，不要默认去掉 SMA200
- 对比：
  - no gate
  - `SMA200`
  - `EMA slope`
  - `BTC regime / market breadth` gate
- 目标：确认 bull gate 是不是这条线真正的 alpha partner，而不是可有可无的装饰

### 实验 D：ETH vs BTC vs liquid majors falsification
- 先测 `ETH / BTC / SOL`
- 不是为了强行扩 universe，而是确认 repo 里“ETH consistently stronger than BTC”这件事，在短周期执行映射下还站不站得住

## 13. 一句话结论
这份 2026 `trading-strategies` repo 对 desk 最有价值的，不是再证明一次“breakout 可能有效”，而是给出了一条更诚实的完整 raw alpha 壳：

**`3-day adaptive range breakout × SMA200 bull gate` 的 ETH 日内延续，第一版应该按 `daily signal + 5m execution` 来测，而不是把它粗暴写成 15m 对称 breakout。**

## 14. 来源链接
1. **timrecursify (2026). _Crypto Futures Day Trading Research_. GitHub repository.**
   - Venue: GitHub
   - DOI: 无
   - Readable URL: https://github.com/timrecursify/trading-strategies
   - Repo URL: https://github.com/timrecursify/trading-strategies.git

2. **`docs/strategies/dual_thrust.md`**
   - Readable URL: https://github.com/timrecursify/trading-strategies/blob/main/docs/strategies/dual_thrust.md

3. **`research/phase_13_dual_thrust_cusum.py`**
   - Readable URL: https://github.com/timrecursify/trading-strategies/blob/main/research/phase_13_dual_thrust_cusum.py

4. **`docs/results/14_final_rankings.md`**
   - Readable URL: https://github.com/timrecursify/trading-strategies/blob/main/docs/results/14_final_rankings.md

5. **Binance USDⓈ-M Perpetual Klines API**
   - Readable URL: https://fapi.binance.com/fapi/v1/klines
