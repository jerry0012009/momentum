# 别把这份 Hummingbot Hyperliquid repo 只当 generic EMA 练手：更值得先拆的是「top-1 流动性轮换 × EMA 趋势 × hard exits」单币全策略骨架
- 时间：2026-03-28 07:04 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：单币趋势跟随（fast/slow EMA crossover）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/single-asset/trend/momentum/ema/liquidity-rotation/funding-veto/vol-veto/hard-exit/risk-sizing/hyperliquid/1m/3m/5m/15m/repo
- 证据类型：工程经验

## 1. 这次看了什么
看了 `dronebassan/Hyperliquid-Trading-Bot` 这个 2026 新仓库，重点不是 README 里的“systematic trading bot”口号，而是源码里已经把 **选币、入场、出场、仓位、日内 kill switch** 写成了一个能直接 desk 化改造的骨架：先在 `BTC/ETH/SOL` 里按 **深度优先、点差次之** 选出 `TOP_N=1` 的交易对，再用 fast/slow EMA 决定方向，最后用 funding / vol / trend veto 决定是否放行。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得复用的不是“EMA crossover”本身，而是它把一条很普通的趋势 alpha，整理成了 **可最小复现、可快速加成本、可继续插 gate 的完整交易壳**。
- **一句话证明方式：** 结论主要来自源码级拆解，而不是回测宣传：参数、过滤条件、止盈止损、持有时长和仓位上限都在代码里明牌。
- raw alpha 本体非常干净：`ema_fast > ema_slow` 做多，反之做空；采样频率 `5s`，配置对应的大致有效窗口约是 **10 分钟 vs 22 分钟** 的短趋势跟随。
- 真正有 desk 价值的是配套治理：**每 5 分钟重做一次流动性筛选**，要求每侧最少 `10,000 USD` 深度、点差不超过 `20 bps`，只交易当下最干净的那 1 个标的。
- 代码把风险边界写得很实：`0.5%` 止损、`0.8%` 止盈、`30 分钟` 超时退出、`180 秒` cooldown、`50 USD` 日内亏损 kill switch；这比很多“只有信号、没有退出”的 repo 更适合进入复现池。
- 但要诚实：repo 自带 backtest 文档明确承认 **没有真实滑点、手续费、funding 完整建模**，所以它现在更像 **raw alpha + risk shell**，还不是可直接上实盘的完成品。

## 3. 为什么和当前项目有关
当前 `momentum` 主线虽然已经积累了不少 cross-sectional / pairs / carry 思路，但对 **单币短趋势 full-stack baseline** 的工程壳仍然不够固定。这个 repo 的价值，正好不是“证明趋势策略神奇有效”，而是替我们把几件经常被分开讨论的东西先焊在一起：**流动性准入、方向信号、entry veto、hard exit、risk cap**。对 desk 来说，这意味着我们可以先用一条很朴素的单币趋势 alpha 建一个统一试验台，再把已有的 `jump veto / funding crowding / volatility regime / execution cost ladder` 接进去做增量检验。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 单币 / 轻度轮换
- 基础 alpha：fast EMA 上穿 slow EMA 做多，下穿做空
- regime：更适合有持续短趋势、且短时 realized vol 不过热的环境
- filter / veto：流动性 `top-1` 轮换、`|funding| <= 8 bps`、短窗波动率上限、最小趋势强度门槛
- risk / sizing / execution overlay：按风险预算反推 notional，`0.5%` SL、`0.8%` TP、`30m` time exit、`180s` cooldown、`50 USD` 日内 kill switch；但 **cost 仍需外接**

## 4. 可复刻的最小实验
- **研究假设：** 在 `1m / 3m / 5m` crypto perp 上，单币短趋势策略的 first failure mode 不一定是方向错，而可能是 **选错交易标的 + 进在 funding/vol 过热时段 + 缺少硬退出**。
- **一个可计算定义：** 每分钟在 `BTC/ETH/SOL/XRP/DOGE` 等高流动 perp 中按 `depth_rank - spread_penalty` 选 `top1`；信号用 `EMA(10m) > EMA(22m)` 做多、反向做空；若 `|funding_8h| > 8bps` 或过去 `5m` realized vol 超阈值则不进场；出场按 `-50bps / +80bps / 30m / signal flip` 四选一。
- **最小回测切口：** `Binance 或 Hyperliquid` 公共数据，先跑最近 `45~90d`；先做 `1m` 基线，再压缩到 `3m`，最后检查 `5m` 是否因反应过慢而失去 edge。
- **最该先看 2 个指标：** `after-cost expectancy per trade` 与 `blocked-vs-allowed entry attribution`。如果 veto 只是在砍 trade count，却没提升单笔净收益，就别把过滤层神化。

## 5. 风险与保留意见
- 这不是论文，也不是严谨历史回测框架；它更像一个写得相对清楚的工程原型。
- 公开 universe 只有 `BTC/ETH/SOL`，容量与风格暴露都偏窄；直接照搬很可能只是在赌 beta。
- 代码里用了 paper-trade mid-price 假设，真实做市队列、冲击、手续费和 funding 侵蚀都还没进来。
- `trend_ok / vol_ok / funding_ok` 现在是硬阈值；下一步更值得测的是 **把它们从 hard veto 改成分层 size rule**，看是否比“全开/全关”更稳。

## 6. 来源
- dronebassan. (2026). `Hyperliquid-Trading-Bot`. GitHub repository.
- Repo URL: `https://github.com/dronebassan/Hyperliquid-Trading-Bot`
- README: `https://github.com/dronebassan/Hyperliquid-Trading-Bot/blob/main/README.md`
- Strategy code: `https://github.com/dronebassan/Hyperliquid-Trading-Bot/blob/main/strategies/hyperliquid_momentum.py`
- Config: `https://github.com/dronebassan/Hyperliquid-Trading-Bot/blob/main/strategies/hyperliquid_momentum_config.json`
- Backtest methodology note: `https://github.com/dronebassan/Hyperliquid-Trading-Bot/blob/main/docs/backtests/methodology.md`
