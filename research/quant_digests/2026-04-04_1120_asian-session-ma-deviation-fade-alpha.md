# 别把这份 2025/2026 DB 驱动 repo 只读成工程脚手架：对 short-cycle desk，更该先测「HL-aware cointegration z-score pairs mean reversion × beta-hedged sizing」这条完整 raw alpha

- 时间：2026-04-04 11:20 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `selection/SQL-DB-Coint-upd-6.py` + `selection/SQL-DB-Stat-upd-5.py` + `execution/Level_2_CFT_bot_07-12-2025.py` + `execution/daily_guard_2.py`）+ Binance Spot 公共 `5m` recent-window portability probe（`BTCUSDT/ETHUSDT`, `ETHUSDT/SOLUSDT`, `BTCUSDT/SOLUSDT`, 近120天）
- 主题类型：raw alpha
- 基础 alpha：**对通过 cointegration 筛选的配对，做 spread z-score 极值回归（`|z|` 扩张开仓、回归中线平仓）的 market-neutral pairs/stat-arb。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/cointegration/zscore/hl-aware/beta-hedge/daily-guard/bybit/binance/5m/15m/1m/3m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据最小便携性快检

## 1. 先回答一句：base alpha 是什么？

**base alpha = 配对 spread 的均值回复。**

具体就是：先用协整与平稳性把“能配对”的资产筛出来，再在 `z-score` 偏离足够大时做反向双腿，等 spread 回到中线（或触发风险条件）就平仓。

这不是 filter，也不是 overlay；它本身就是一条可独立运行的 raw alpha。

## 2. 这份 repo 里，完整策略部件是否齐全？

结论：**齐全（在它的原生 DB + bot 架构里）**。

### 2.1 Entry（入场）

从 `execution/Level_2_CFT_bot_07-12-2025.py` 可以直接读到：
- 选对阶段要求 `ADF <= -2.9`、`p-value <= 0.05`、`Hurst <= 0.45`；
- 且 `ABS(last_z_score)` 需过 HL 相关门槛（`2/2.5/3/3.5` 分段），并小于上限 `5`；
- 执行触发是 `last_z_score >= 2` 或 `<= -2`；
- `z>0` 时 short spread（卖 leg1 买 leg2），`z<0` 时 long spread（买 leg1 卖 leg2）。

### 2.2 Exit（出场）

同一执行脚本里有多重退出：
- `z-score` 穿 0（主回归退出）；
- 浮盈/浮亏达到 pair 级 TP/SL 百分比；
- `|z| >= 6` 且协整丢失（stop-loss）；
- 超过 HL 时限且协整丢失（timeout exit）。

### 2.3 Sizing / Risk

- `calculate_dynamic_leverage()` 做 beta-hedged 头寸配平；
- `beta_norm` 被 clamp 到 `[0.8, 1.2]`，并按 5m 交易额 cap 分配双腿暴露；
- 每腿最小名义暴露 `500 USDT`，总杠杆上限 `5x`；
- `daily_guard_2.py` 有日内盈利节流与日损停机（默认 `DAILY_TP=1%`, `DAILY_SL=3%`）。

> 这意味着它不是“只会发信号”，而是完整覆盖了 entry/exit/sizing/risk。

## 3. 120 天 `5m` 公共数据快检（最小 portability）

我用 Binance Spot 公共 `5m` close 做了一个最小口径快检：
- 配对：`BTC-ETH`, `ETH-SOL`, `BTC-SOL`
- 规则：rolling z-score(96 bars)；`|z|` 上穿 `2` 开仓；统计回归到 `z=0` 的命中

关键结果：
1. **信号密度不低**：约 `9.2 ~ 10.0` 次/天（按 pair）
2. **短时回归不强**：`2h` 内回归到 0 的命中率约 `27.8% ~ 29.7%`
3. **更像“慢回归”**：`8h` 内回归命中率升到 `86.3% ~ 88.0%`

解释：
- 这条 alpha 在 `5m` 上并非不触发，但半衰期偏慢；
- 更像“多小时回归”而不是 `1m` 级别快进快出 scalp。

## 4. 对当前 desk 的意义

- 它直接补的是我们要持续补的 **pairs/stat-arb raw alpha 素材**；
- 而且比“只讲配对方法”的材料更可用：执行和风控结构已经给出来了；
- 但若要适配 `1m/3m/5m/15m` 的短周期研发，重点应放在**回归速度分层**，不是盲目加频。

## 5. 下一步怎么测（可直接排进实验队列）

### 实验 A：HL-aware 阈值 vs 固定 2σ
- 对照组：固定 `|z|>=2`
- 实验组：按 HL 分段门槛（repo 思路：`2/2.5/3/3.5`）
- 看：`2h/4h/8h` 回归命中、净 bps/trade、日均换手

### 实验 B：短周期迁移（5m→3m/1m）
- 不改 alpha 定义，只改采样与持有时钟
- 先验证：信号密度是否上升但净值质量下降（典型 cost trap）

### 实验 C：成本梯度
- round-trip 成本至少跑 `6/10/14 bps`
- 目标不是找“最优参数”，而是找“成本后还能活”的 pair bucket

### 实验 D：执行 veto
- 加入 `5m` 成交额下限与盘口冲击代理（避免低流动 pair）
- 验证是否能提升短窗口（2h~4h）命中质量

## 6. 风险与保留意见

- 仓库是“legacy + 架构展示”形态，缺少完整 schema/配置，直接一键运行并不现实；
- README 的 live 绩效（`704` 笔、`64.6%` 胜率、`PF 1.22`）需独立复核，不应直接当可迁移结论；
- 公共 spot 快检与其 bybit perp 实盘口径并不完全同构，仍需在 perp 成本口径下做二次确认。

## 7. 来源

1. **Velychko, A. (2025/2026). _statistical_arbitrage_trading_system_V1_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1`  
   - Repo URL: `https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1`

2. **Repo source files used in this digest**  
   - README: `https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/HEAD/README.md`  
   - Selection: `https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/HEAD/selection/SQL-DB-Coint-upd-6.py`  
   - Stats/Leveling: `https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/HEAD/selection/SQL-DB-Stat-upd-5.py`  
   - Execution: `https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/HEAD/execution/Level_2_CFT_bot_07-12-2025.py`  
   - Daily guard: `https://raw.githubusercontent.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/HEAD/execution/daily_guard_2.py`

3. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). _Pairs Trading: Performance of a Relative-Value Arbitrage Rule_. Review of Financial Studies.**  
   - DOI: `10.1093/rfs/hhj020`  
   - Readable URL: `https://doi.org/10.1093/rfs/hhj020`

4. **Binance Spot API (public kline data used in portability probe)**  
   - Docs: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`  
   - Endpoint: `https://api.binance.com/api/v3/klines`
