# 别把这份 2026 多币 bot 只读成“RSI 教学脚本”：对 short-cycle desk，更该先测的是「oversold panic fade × hard stop / fixed TP」这条单资产 mean-reversion raw alpha
- 时间：2026-04-17 20:24 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `BinanceAlgoTrader.py` + `backtester_rsi.py` + `optimizer.py` + GitHub API metadata）+ Binance Spot 公共 `1m/5m/15m` portability probe（BTC/ETH/SOL/BNB，各 1000 bars）
- 主题类型：raw alpha
- 基础 alpha：当单币短窗 RSI 跌入极端超卖（repo 默认 `RSI(14) < 30`）时，价格常出现一段可收割的技术性反弹；做法是**在 oversold panic 时逆向买入**，并用 `RSI > 70`、`-2%` stop、`+6%` take-profit 三选一退出。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给 entry / exit / 仓位 / 状态持久化 / 交易日志；成本建模与跨资产治理需补）
- 主题标签：raw-alpha / single-asset / mean-reversion / rsi / oversold / panic-fade / fixed-stop / fixed-tp / multi-coin / btc / eth / sol / bnb / 1m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + Binance 公共行情最小迁移快检

## 1. 为什么这轮选它
这轮优先级不是再补一个 filter，而是补一条**base alpha 一句话能说清楚**、并且真的带有完整交易壳的 raw alpha。

我最后选的是 GitHub 仓库 **panthu13147 / Python-Crypto-Algo-Trader**：
- 创建时间：2026-01-02
- 最近更新时间：2026-04-16
- stars：1
- 结构很轻，但不是只有 README——有 live bot、单独 RSI backtester、以及一个很粗糙但可读的 optimizer。

先把 base alpha 说人话：

> **这不是“RSI 指标有用吗”的空话；它真正下注的是：单币在短窗 panic oversold 后，常有一段可以用硬 stop / 固定 TP 收割的反弹。**

它和 4 月 13 日已经 intake 过的那份 **Wilder-RSI breakout × ADX/EMA trend shell** 不是一回事：
- 那篇是 **顺势 breakout / momentum**；
- 这篇是 **逆向 oversold mean reversion**；
- 前者赌延续，后者赌恐慌后的技术反弹。

所以它虽然也叫 RSI，但这轮不算撞题，补的是**另一条 raw alpha 家族**。

## 2. repo 里真正可复用的 alpha 是什么
### 2.1 README 说的是“RSI Mean Reversion”，源码里交易本体也确实一致
`BinanceAlgoTrader.py` 的主逻辑非常直白：

- 交易标的：`BTC / ETH / SOL / BNB`
- 主周期：`1m`
- 指标：手算 `RSI(14)`
- 开仓：`RSI < 30`
- 平仓三选一：
  - `RSI > 70`
  - `pnl <= -2%`
  - `pnl >= +6%`
- 名义仓位：每次固定 `100 USDT`
- 状态层：`bot_state.json`
- 结果层：`trade_history.csv`

也就是说，这个 repo 的贡献不是“提出了新因子”，而是把一个**非常朴素的 panic fade alpha**包装成了可运行的最小完整系统：
- signal
- execution
- stop
- take-profit
- state persistence
- trade ledger

这对 desk 的价值，在于它是个**可快速 first verdict 的完整壳**。

### 2.2 base alpha 用一句话压缩
这条 alpha 可以压成一句：

> **短窗 RSI 极端超卖，不一定代表趋势继续崩；在不少场景里，它更像局部流动性挤压后的反弹入口。**

注意这里的 alpha 本体是：
- **单资产短窗 mean reversion**；
不是：
- 横截面 relative value；
- pairs spread 回归；
- funding / basis carry；
- regime gate。

这点很重要，因为它满足了本轮“先回答 base alpha 是什么”的硬要求。

## 3. 源码里最值得 desk 继承的部分
### 3.1 它给的是完整 raw alpha 壳，不是只有 entry 条件
很多轻量仓库只有：
- 一个 entry 规则；
- 没有状态；
- 没有真实的退出治理；
- 没有 trade log。

这份 repo 虽然简单，但至少把下面几件事都串起来了：

1. **多币轮询扫描**：同一主逻辑扫 `BTC/ETH/SOL/BNB`；
2. **仓位持久化**：重启后还能知道自己是不是在仓位里；
3. **硬风控**：`-2%` stop；
4. **盈利实现**：`+6%` TP；
5. **事件退出**：`RSI > 70`；
6. **交易留痕**：CSV ledger。

如果把它当成 desk 的 intake，对应的正确读法不是“照抄上线”，而是：

> **把它当作单资产 oversold panic fade 的最小母板。**

### 3.2 它的退出层比 entry 更值得保留
repo 最容易被忽略的地方，不是 `RSI < 30`，而是它给了三个互相竞争的 exit：
- 过热退出（`RSI > 70`）
- 止损退出（`-2%`）
- 止盈退出（`+6%`）

这意味着它不是纯“均值回归指标脚本”，而是已经在回答：
- 什么时候承认错了？
- 什么时候把反弹兑现？
- 什么时候等到过热再走？

对 short-cycle desk 来说，这种**完整策略壳**本身就有研究价值。

### 3.3 但 repo 的 RSI 实现并不够“交易级”
源码里 RSI 是用简单 rolling mean 算的：
- 不是 Wilder smoothing；
- 没有 warmup 治理；
- 没有 intrabar / next-bar execution 区分；
- 没有 fees / slippage / borrow / funding 的显式成本层。

另外，`optimizer.py` 甚至不是针对同一条 RSI alpha，而是去扫 `SMA short / SMA long / stop loss` 组合，说明 repo 在研究设计上并不严谨。

所以它更像：
- **低门槛 raw alpha 母板**，
而不是：
- 可直接相信的 production research。

## 4. public portability probe：这条 alpha 对 `1m / 5m / 15m` 还有没有活口
为了不把 README 空话当证据，我按 repo 的核心逻辑做了一个最小迁移快检：

### 4.1 快检口径
- 数据源：Binance Spot 公共 `klines`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 周期：`1m / 5m / 15m`
- 样本：每个标的每个周期最近 `1000` bars
- 规则：
  - `RSI(14) < 30` 开多
  - `RSI > 70` 或 `-2% stop` 或 `+6% TP` 平仓
- 成本假设：单边 `5 bps fee + 3 bps slippage`，round-trip 共 `16 bps`

注意：
这不是完整 walk-forward，也不是论文级 backtest；它只是用来回答一句最重要的话：

> **这条 raw alpha 在 desk 默认频段上，是一眼就死，还是至少还有 pocket 可聊？**

### 4.2 `1m`：基本不值得直接照抄
最近 `1000` 根 `1m` bars 的结果：

- `BTC`：12 笔，胜率 **41.7%**，平均每笔 **-0.7 bps**，累计 **-0.10%**
- `ETH`：10 笔，胜率 **30.0%**，平均每笔 **-10.9 bps**，累计 **-1.09%**
- `SOL`：9 笔，胜率 **44.4%**，平均每笔 **-2.7 bps**，累计 **-0.26%**
- `BNB`：9 笔，胜率 **11.1%**，平均每笔 **-15.6 bps**，累计 **-1.40%**

一句话结论：

> **1m 直译版大体已经被摩擦吃掉，尤其 ETH / BNB 明显偏负。**

这很符合直觉：
- oversold 信号在 `1m` 上太密；
- 噪声和手续费占比太高；
- 没有更强的 microstructure / event gate 时，很容易变成无效抄底。

### 4.3 `5m`：BTC / ETH / BNB 出现正 pocket，但不是全市场通杀
最近 `1000` 根 `5m` bars 的结果：

- `BTC`：13 笔，胜率 **76.9%**，平均每笔 **+14.2 bps**，累计 **+1.85%**
- `ETH`：14 笔，胜率 **57.1%**，平均每笔 **+15.4 bps**，累计 **+2.14%**
- `SOL`：13 笔，胜率 **61.5%**，平均每笔 **-8.6 bps**，累计 **-1.15%**
- `BNB`：14 笔，胜率 **71.4%**，平均每笔 **+6.7 bps**，累计 **+0.94%**

这一档最值得注意：
- `BTC / ETH` 不是只有 gross 正，而是**扣了 16 bps round-trip 后仍有正 pocket**；
- `SOL` 明显掉队；
- `BNB` 虽然仍正，但 edge 较薄。

所以更诚实的说法是：

> **它不是“多币通用 alpha”，而更像 major coin 的局部 panic fade 壳。**

### 4.4 `15m`：BTC / ETH 比 `1m` 更像能活，但资产分化依然明显
最近 `1000` 根 `15m` bars 的结果：

- `BTC`：12 笔，胜率 **75.0%**，平均每笔 **+21.3 bps**，累计 **+2.53%**
- `ETH`：13 笔，胜率 **69.2%**，平均每笔 **+20.4 bps**，累计 **+2.52%**
- `SOL`：12 笔，胜率 **50.0%**，平均每笔 **-7.1 bps**，累计 **-0.98%**
- `BNB`：12 笔，胜率 **58.3%**，平均每笔 **-8.7 bps**，累计 **-1.12%**

这说明什么？

1. **从 1m 提到 5m/15m，噪声显著下降；**
2. `BTC / ETH` 的 oversold panic fade 仍然有 pocket；
3. `SOL / BNB` 没有同步跟上，说明这不是“资产无关”的稳定 alpha。

## 5. 这轮 digest 的真正结论
如果必须只用一句话总结：

> **这份 repo 真正值得 desk intake 的，不是“RSI 指标”本身，而是“major coin 上的 oversold panic fade + 硬 stop / 固定 TP”这条完整 raw alpha 壳；1m 直译基本不行，但 5m/15m 的 BTC / ETH 仍有继续深挖价值。**

再翻成人话：
- 不要把它当“全市场自动抄底机器人”；
- 也不要因为它简单就直接忽略；
- 它更像是一个**能快速形成 first verdict 的单资产 MR baseline**。

## 6. 它和当前 desk 素材池的关系
这条线对当前项目有直接补充价值，原因有三：

### 6.1 它补的是单资产 MR，而不是又一条 pairs / funding / options
最近 intake 里，
- pairs / stat-arb / funding / options / prediction-market 已经很密；
- 单资产、可独立落地、带完整 exit 壳的 **plain mean reversion** 反而不算多。

这份 repo 补的是：
**最朴素、最易 first verdict 的单资产 panic fade。**

### 6.2 它能作为很多复杂 alpha 的 baseline 对照组
后续若你要测：
- liquidation shock fade
- order-flow panic fade
- whale unwind bounce
- OI/volume shock fade

都很适合先拿这条简单规则当 baseline：

> **如果连 plain RSI panic fade 都打不过，那复杂事件层大概率也只是“讲了个更贵的故事”。**

### 6.3 它还能拆成更适合 desk 的模块
repo 自带的完整壳可以拆成三层：

1. **base alpha**：oversold panic fade
2. **risk shell**：`-2% stop / +6% TP`
3. **universe layer**：只做 major / 只做高流动性币

这正好符合当前 desk 喜欢的拆法：
- alpha 本体讲清楚；
- overlay / veto 后加；
- 先做最小实验，再谈复杂化。

## 7. 如果今天就把它 desk 化，应该怎么改
### 7.1 Entry：别再用裸 `RSI < 30` 扫全市场
最先该测的不是参数微调，而是**更少但更诚实的 admission**：

- 只做 `BTC / ETH`
- 只在 `5m / 15m`
- 入场条件改成：
  - `RSI(14) < 30`
  - 当根真实波动不超过过去 `N` 根 `p90`（避免接飞刀）
  - 成交量不低于 rolling 中位数（避免死流动性）

### 7.2 Exit：把固定 `+6%` 改成更短周期的现实口径
repo 的 `+6% TP` 放在 `1m` 上很不 desk。
对 `5m / 15m` 更合理的先测法是：
- `1.0~1.5 ATR` 止盈
- `0.8~1.0 ATR` 止损
- 或 `time-stop = 6 / 12 / 24 bars`

因为我们真正想知道的是：

> **panic fade 的回补能不能在有限 bars 内兑现，而不是等一个过大的固定百分比。**

### 7.3 Universe：先接受“不是所有币都适合”
这轮快检已经给了很明确的提醒：
- `BTC / ETH` 相对更像有 edge；
- `SOL / BNB` 至少在最近这段样本里并不稳定。

所以别把它做成全币扫描器先上；
正确顺序应该是：
- `BTC` baseline
- `ETH` 对照
- 其他币做 out-of-universe negative control

## 8. 下一步怎么测（必须给）
### 最小实验 A：major-only panic fade
- 标的：`BTCUSDT / ETHUSDT`
- 周期：`5m / 15m`
- 规则：沿用当前 base alpha
- 退出：改成 `ATR-stop + time-stop` 双版本
- 目的：确认 edge 来自 alpha 本体，还是来自 repo 那个不现实的 `+6%` TP

### 最小实验 B：admission layer 是否真有用
在 A 的基础上，逐个加：
1. 成交量门槛
2. 大阴线 / 长上影 veto
3. realized vol 分位过滤

目的不是炼丹，而是回答：

> **这条 alpha 到底死在信号质量，还是死在“什么时候不该接”。**

### 最小实验 C：和事件型 panic fade 对照
把它和当前素材池里的：
- liquidation cascade panic fade
- OI×volume shock fade
- downside outlier fade

放到同一评估口径下比较：
- trade count
- mean trade bp
- post-cost cum return
- max adverse excursion

若 plain RSI panic fade 都能接近事件型，那说明：
- 复杂事件层的增量有限；
若事件型明显更强，才说明复杂数据真的买来了额外信息。

## 9. 风险与失效方式
这条 alpha 最容易死在三种地方：

1. **单边趋势日**：oversold 不是反弹，而是趋势继续扩张；
2. **微观摩擦**：`1m` 级别的 edge 先被 fee / slippage 吃光；
3. **资产泛化失败**：major 能活，不代表山寨也能活。

所以当前阶段的正确定位不是“production-ready”，而是：

> **一个值得放进素材池的、可独立复现的单资产 MR baseline。**

## 10. 来源信息
### Repo
- panthu13147 (2026), **Python-Crypto-Algo-Trader**
- Repo URL: <https://github.com/panthu13147/Python-Crypto-Algo-Trader>
- README raw: <https://raw.githubusercontent.com/panthu13147/Python-Crypto-Algo-Trader/main/README.md>
- Core file raw: <https://raw.githubusercontent.com/panthu13147/Python-Crypto-Algo-Trader/main/BinanceAlgoTrader.py>
- Backtester raw: <https://raw.githubusercontent.com/panthu13147/Python-Crypto-Algo-Trader/main/backtester_rsi.py>
- Optimizer raw: <https://raw.githubusercontent.com/panthu13147/Python-Crypto-Algo-Trader/main/optimizer.py>

### Public data used in this digest
- Binance Spot public klines: <https://data-api.binance.vision/api/v3/klines>
- 公开性：公开可得
- 更新频率：按所选 bar 周期更新（本轮使用 `1m/5m/15m`）
- 最小可复现实验口径：`BTC/ETH/SOL/BNB`，最近 `1000` bars，`RSI(14)<30` 入场，`RSI>70/-2%/+6%` 退出，round-trip `16 bps` 成本

## 11. 一句话结论
**这份 2026 新 repo 最值得保留的，不是“RSI 指标课”，而是「major-coin oversold panic fade × hard stop / fixed TP」这条完整 raw alpha 壳：`1m` 直译基本不行，但 `5m/15m` 的 BTC / ETH 还有继续做 first-verdict / clean-replication 的价值。**
