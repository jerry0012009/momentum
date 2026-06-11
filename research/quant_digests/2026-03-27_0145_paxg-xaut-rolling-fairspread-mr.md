# 别把 GoldArb 只读成固定阈值网格：这份 2026 repo 更该先测的是「rolling fair-spread 偏离」单 venue pairs raw alpha

- 时间：2026-03-27 01:45 UTC
- 类型：2026 GitHub 仓库 + 策略源码审阅 + Bybit 公共 instruments/kline 最小快检
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/paxg/xaut/gold-token/bybit/single-venue/market-neutral/maker/execution/cost/1m/3m/5m/15m/repo/external-data
- 证据类型：2026 GitHub repo + source code + Bybit 公共市场数据快检

- 主题类型：raw alpha
- 基础 alpha：同一交易所内、同一黄金锚资产的 `PAXG/XAUT` 相对价差偏离后回归；更适合做成“相对 rolling fair spread 的均值回归”，而不是假定 spread 必回到 0 的固定绝对阈值网格
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但首轮必须用 maker-first / quote 级数据，不适合四腿 taker 直上）

## 1. 这次看了什么
这次主看的是 **Patrick-code-Bot (2026)** 的 GitHub 仓库 **GoldArb**。repo headline 写的是 `PAXG/USDT` 与 `XAUT/USDT` 永续在 Bybit 上做 fixed-grid spread arbitrage，但对我们 desk 更值钱的，不是“又一个网格”，而是它背后那条**可以独立落地的 raw alpha**：

> **同 venue、同宏观锚（黄金）、双合约之间的相对定价会围绕一个会漂移的 fair spread 做短周期回归。**

也就是说，真正该先 intake 的不是“10/20/30bps 网格档位本身”，而是：**`spread - rolling fair spread` 的 residual mean reversion**。

## 2. 核心结论
- **base alpha 很清楚：** 这是 `pairs / relative-value / stat-arb`，不是 filter，也不是 overlay。交易对象就是 `short rich leg / long cheap leg` 的价差收敛。
- **repo 给的是完整执行骨架，而不只是想法。** 源码里已经把 `PAXGUSDT-LINEAR.BYBIT` / `XAUTUSDT-LINEAR.BYBIT`、paired maker orders、timeout 撤单重挂、单腿修复、`max_total_notional`、`extreme_spread_stop=1.5%` 等都写出来了。
- **但 fixed absolute grid 不稳定。** 我用 Bybit 公共 `5m` K 线快检：`PAXG/XAUT` 绝对 spread 中位数，近 `21d` 约 **59.6 bps**，近 `14d` 掉到 **28.7 bps**，近 `7d` 只剩 **17.6 bps**，近 `3d` 约 **14.7 bps**。这说明把 `10/20/30bps` 当永恒阈值，极容易被 regime drift 打坏。
- **rolling fair-spread 偏离是有信号的，而且明显偏单边。** 在近 `14d` Bybit 公共 `5m` 数据上，用 `24h rolling mean/std` 算 spread z-score：当 `z > 2` 时，后续 spread 平均在 `15m / 1h / 3h` 分别收窄约 **1.62 / 3.16 / 6.38 bps**，命中率约 **69% / 77% / 85%**；而 `z < -2` 一侧明显更弱，不适合先做对称双边。
- **但 bar-close 毛边很薄。** `3h` 只看到 **6bp 左右** 的 gross residual 收敛，说明它不是“四腿 taker 随便打”的策略，必须依赖 **maker-first、paired execution、quote/tick 级 entry** 才可能活下来。

## 3. 为什么和当前项目有关
这条线值得进 bot7，而不是继续围着同一类 breakout/filter 打转，原因很直接：

1. **它是可独立复现的 raw alpha。** 不是“给已有策略再加一个 veto”，而是一条能自己定义 `entry / exit / sizing / risk / cost` 的完整 pairs 骨架。  
2. **它补的是当前 desk 素材池里很重要的一类：single-venue、same-anchor 的 relative-value MR。** 它和我们前面写过的 `cross-exchange carry / spot-perp basis / stablecoin ATA / cointegration basket` 都不完全一样：这里不需要跨 venue 搬砖，不需要现货腿，也不需要复杂协整估计，结构更干净。  
3. **它天然适合映射到 1m / 3m / 5m。** 因为信号本体就是短周期 residual 偏离；`15m` 更适合做 fair-spread 背景和 hold horizon，不适合当最细 entry clock。  
4. **repo 本身已经把 execution 难点暴露出来。** 这对我们很有用：它提醒我们这种 edge 的生死不在“有没有均值回归”这句废话，而在 `maker fill / legging risk / timeout repair / fee survival`。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / pairs / market-neutral / mean reversion
- 基础 alpha：`PAXG/XAUT` spread 相对 rolling fair spread 的偏离回归，优先做 `rich-spread fade`
- regime：同 venue 两腿都在正常交易、盘口连续、spread 未进入 structural re-pricing / listing-shock 模式
- filter / veto：只做 `z > 2` 或 `z > 2.5` 的正向极端；若 absolute spread 已掉到滚动中位数附近、或 quote 连续性差、或 1m 成交/盘口明显失真，则 veto
- risk / sizing / execution overlay：paired maker 下单、单腿超时修复、总 notional cap、极端 spread stop、按 z-score / percentile 分层 sizing、stress 用 taker repair 估成本

## 4. 可复刻的最小实验
### 研究假设
`PAXG/XAUT` 的**绝对 spread 水平会漂移**，但“相对 rolling fair spread 的高位偏离”在 `1m~3h` 内有可交易的均值回归；而低位偏离不一定对称成立。

### 数据源
- **Bybit 公共合约信息**：`/v5/market/instruments-info?category=linear&symbol=PAXGUSDT` 与 `XAUTUSDT`
- **Bybit 公共 K 线 / 最终应升级为 WebSocket best bid/ask quote**
- 公开性：公开可得、无需私钥
- 更新频率：K 线可做 `1m / 3m / 5m / 15m`；真正执行实验建议 quote/tick 级

### MVP 口径
- 主时钟：`1m`
- sanity check：`5m`
- `15m` 只用于看 fair-spread 背景，不作为最优 entry 粒度
- 定义：
  - `spread_t = mid(PAXG)_t / mid(XAUT)_t - 1`
  - `mu_t, sigma_t = rolling(4h 或 24h)`
  - `z_t = (spread_t - mu_t) / sigma_t`
- **Entry**：仅先做单边版本；当 `z_t > 2.0`（或 `2.5`）且 `spread_t` 位于滚动分位数 `p75` 以上时，`short PAXG / long XAUT`
- **Exit**：`z_t < 0.5` 或持有 `60m / 180m` 到时；二阶段再比较 time-exit vs z-exit
- **Sizing**：两腿等美元对冲；单次 gross notional 先从小额分层做；按 `z` 强度递增，但总 gross cap 固定
- **Cost**：先测 `maker 1/2/4 bps per leg` 三档，再加 `单腿 repair 落到 taker 5.5 bps` 的 stress 情形
- **风险**：若 spread 触及 repo 里的极端止损区（如 `1.5%`）或 quote 丢失 / 单腿未成对成交，则立即退出

## 5. 下一步怎么测
1. **先把 fixed-grid 和 rolling-fair 两个定义正面对照。** 同一批 Bybit 公共数据，比 `absolute 10/20/30bps` 与 `rolling z-score`，看哪个更稳、哪个更少 regime 漂移。  
2. **先只做正向高 spread 单边。** 目前公共 `5m` 快检显示 `z > 2` 一侧明显强于 `z < -2`，所以第一轮不要为了“对称好看”硬做双边。  
3. **把 K 线实验升级到 quote/tick 级。** 这条 edge 的生死大概率取决于 maker fill；如果只用 bar close，看见的只是“有没有一点毛边”，不是最终可交易答案。  
4. **专门做成本生存线。** 记录 `gross bps / fill ratio / repair ratio / net bps`，如果只能在理想 maker 世界活、现实一有单腿修复就死，那就诚实降级。

## 6. 诚实的限制
- 这是个**很新的细分 pair**，`XAUTUSDT` 在 Bybit 的可用历史并不长，样本天然短。  
- 我这轮做的是 **public kline quick check**，不是 quote-level fill backtest，所以不能把上面的 bps 当成最终可成交收益。  
- 两腿虽然都锚定黄金，但它们未必应该收敛到 `0 spread`；合约年龄、流动性层级、funding、盘口厚度都可能带来**长期非零 fair spread**。这正是为什么我更倾向用 `rolling fair spread`，而不是把 repo 的 fixed grid 当真理。

## 7. 参考来源
1. **Patrick-code-Bot (2026). _GoldArb_. GitHub repository.**  
   Repo URL: `https://github.com/Patrick-code-Bot/GoldArb`  
   Readable README: `https://raw.githubusercontent.com/Patrick-code-Bot/GoldArb/main/README.md`  
   Strategy source: `https://raw.githubusercontent.com/Patrick-code-Bot/GoldArb/main/paxg_xaut_grid_strategy.py`

2. **GitHub repository metadata (API).**  
   URL: `https://api.github.com/repos/Patrick-code-Bot/GoldArb`  
   用于确认 repo 描述、创建/更新时间等元数据。

3. **Bybit public instruments info.**  
   PAXGUSDT: `https://api.bybit.com/v5/market/instruments-info?category=linear&symbol=PAXGUSDT`  
   XAUTUSDT: `https://api.bybit.com/v5/market/instruments-info?category=linear&symbol=XAUTUSDT`

4. **Bybit public market kline endpoint.**  
   Endpoint: `https://api.bybit.com/v5/market/kline`  
   本轮最小快检口径：`category=linear`，对 `PAXGUSDT` / `XAUTUSDT` 拉取公开 `5m` K 线，构造 spread 与 rolling z-score。