# 别把这份 2023 market-neutral repo 只读成 seasonality 课堂作业：对 short-cycle desk，更该先测的是「same-clock after-hours loser-bounce × regular-hours winner-follow」
- 时间：2026-04-08 13:31 UTC
- 类型：GitHub repo source audit + 本地复算
- 主题类型：raw alpha
- 基础 alpha：同一 UTC 时段内，工作日 after-hours 做横截面反转，regular-hours 做横截面动量
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / intraday / time-of-day / momentum / mean-reversion / market-neutral / session
- 证据类型：工程经验（repo source audit + 公共数据本地复算）

## 1. 这次看了什么
看的是 MateoPedro 的 2023 GitHub repo **StatArb / Market-Neutral Crypto Strategy**，核心材料是 `README.md` 和 `Project .ipynb`。它不是在讲“全天统一一个因子”，而是把 **同一个币在不同 UTC 时段的横截面效应拆开看**：工作日 `14:00–21:00 UTC` 偏向动量，工作日其余时段偏向反转。为避免只抄 README，我又按 repo 逻辑，用 Binance US 公共 `1h` K 线对 `BTC/ETH/ADA/BNB/XRP/DOT/MATIC/SOL/LTC/AVAX` 在 `2022-06-30 ~ 2023-07-15` 做了一次本地复算。

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值钱的点，不是“crypto 有日内季节性”，而是 **同样的横截面排序，在不同 clock bucket 里应该切不同方向：after-hours 更像反转，regular-hours 更像动量。**
- **一句话证明方式**：作者把每个小时拆成独立 bucket，只用“过去若干天同一小时的平均收益”做排名，再做 market-neutral long-short 回测；我本地复算后，`252×24` 年化口径得到约 **16.65% 年化收益 / 8.21% 年化波动 / Sharpe 2.03**，和 repo README 的 **16.7% / 8.22% / 2.03** 基本对齐。
- after-hours 反转 sleeve 的最优短窗更短：本地复算里 **2-day lookback Sharpe 2.44**，高于 **1-day 的 2.07**，说明“夜盘追尾太猛的 loser，次日同一时段更容易反弹”。
- regular-hours 动量 sleeve 更吃中短窗延续：`9~21` 天里，**10-day lookback Sharpe 2.67** 最强，`9-day` 也有 **2.44**，说明活跃时段的信息扩散更像延续而不是立刻回吐。
- repo 的组合不是简单 50/50。我的复算里，最终外层权重大约 **after-hours reversal 53.2% / regular-hours momentum 46.8%**；也就是说，这不是“二选一”，而是一个 **session router**。
- 最值得复用的点不是参数本身，而是 **same-clock ranking** 这层结构：不要把所有 `5m/15m` bar 混在一起排序，先按 UTC bucket 切开，再看每个 bucket 更像 continuation 还是 fade。

## 3. 为什么和当前项目有关
这和 `momentum` 当前主线很贴，因为它提供的是一个**可直接落地的 raw alpha 骨架**，而不是抽象解释：
1. 它天然服务 `1m/3m/5m/15m`，因为 short-cycle 本来就强依赖 clock effect；
2. 它能把我们已有的 trend / reversal / volume 因子改造成 **session-conditional 版本**；
3. 它属于 desk 目前缺的那类东西：**不是再找一个全新指标，而是把“什么时候该追、什么时候该反手”写成统一路由器。**

## 3.5 策略拆解（必填）
- 方向属性：横截面（market-neutral）
- 基础 alpha：同一 UTC bucket 的横截面收益排序在 regular-hours 做 continuation，在 after-hours 做 reversal
- regime：工作日 + `regular-hours(14:00–21:00 UTC)` / `after-hours(其余时段)` 双时段路由
- filter / veto：只做 top-liquid universe；周末先单独剥离；单 bucket 样本不足时不交易
- risk / sizing / execution overlay：横截面去均值归一权重；内层 sleeve 用历史 Sharpe/方差分配；总组合做 gross cap、单币权重上限、round-trip 成本假设

## 4. 可复刻的最小实验
**研究假设**：crypto 的横截面排序信号不是全天同号；活跃时段更适合追强，非活跃时段更适合抄过度回撤。

**最小定义（建议直接上 15m）**：
- universe：Binance/OKX top 12–20 个 USDT perp
- bar：`15m`
- bucket：按 `UTC 15m` 时段拆成 96 个 same-clock bucket
- after-hours sleeve：对每个 bucket，算过去 `1~2` 天同 bucket 平均收益，**做 loser-long / winner-short**
- regular-hours sleeve：对 `14:00–21:00 UTC` bucket，算过去 `8~12` 天同 bucket 平均收益，**做 winner-long / loser-short**
- holding：只持有当前 bucket 一根 bar，下一同类 bucket 再重新排名
- cost：先用 `8~10bps` round-trip taker 成本；同时记录 maker 化后的改善空间

**先看两项指标**：
1. post-cost Sharpe / return per bucket；
2. positive bucket ratio（不是只看总收益，先看是不是大多数时段都同向）。

## 5. 风险与保留意见
- repo 样本只到 `2023-07`，而且是 Binance US `1h` 数据；直接迁到 2026 主流 perp，稳定性要重验。
- 这类 same-clock 规则非常怕 **样本稀疏 + 多重检验**：96 个 `15m` bucket 很容易过拟合，所以第一轮必须先做 “regular-hours vs after-hours” 粗路由，而不是一上来逐 bucket 精调。
- 时段效应容易和流动性、币种轮换、事件时钟混在一起；如果只在小币有效，容量会很差。
- 周末 crypto 微结构经常变形，建议第一轮先**工作日-only**，周末单独做 OOS，不要混回训练样本里。

## 6. 来源
- MateoPedro. (2023). *Market-Neutral Crypto Strategy* (GitHub repository).
- Readable URL: `https://github.com/MateoPedro/StatArb`
- Repo URL: `https://github.com/MateoPedro/StatArb`
- Audited files: `README.md`, `Project .ipynb`
- Local replication data: Binance US public `1h` klines (`BTCUSDT, ETHUSDT, ADAUSDT, BNBUSDT, XRPUSDT, DOTUSDT, MATICUSDT, SOLUSDT, LTCUSDT, AVAXUSDT`; `2022-06-30 ~ 2023-07-15`)
