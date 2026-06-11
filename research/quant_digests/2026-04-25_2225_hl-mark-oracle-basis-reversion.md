# 别把这个 Hyperliquid 回测仓只读成“又一个 basis 看板”：对 short-cycle crypto desk，更该先拆的是「mark-vs-oracle 极端溢价回归」这条 raw alpha
- 时间：2026-04-25 22:25 UTC
- 类型：GitHub repo source audit（`README.md` + `src/strategies/basis_reversion.py` + `src/engine/backtest.py` + `run_backtest.py`）
- 主题类型：raw alpha
- 基础 alpha：perp mark price 相对 oracle price 的短时极端偏离会向公允值回归（basis dislocation mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / basis / mark-oracle / mean-reversion / hyperliquid / 1m / 3m / 5m / 15m
- 证据类型：工程经验

## 1. 这次看了什么
看的是 `andreaambrosio/hype-backtesting`（GitHub，2026）。这份仓里真正值得 short-cycle desk 拿来拆的，不是“Hyperliquid 上也能做 funding / momentum”，而是一个更原始、也更像微观结构 alpha 的分支：**当 perp 的 mark 相对 oracle 偏得太离谱时，做它向 oracle 回归。**

## 2. 核心结论
- 这条策略的 base alpha 很干净：不是预测大趋势，也不是赌 funding 方向，而是赌**短时错误定价会回补**。对我们 desk 来说，它更接近 `relative value / microstructure stat-arb`，不是传统 breakout 或 retest。
- repo 里这条 `Basis Dislocation Reversion` 是全仓最佳分支：在作者的 `90d`、`1h` Hyperliquid 数据上，回测给出约 `+3.88%` return、`4.52` Sharpe、`299` 笔交易、`15.69%` max DD。数字本身先别神化，但至少说明：作者不是只写故事，而是把它放进统一成本和风控框架里和别的 alpha 一起比。
- 策略定义也足够可落地：代码里默认要求 `|premium|` 同时超过固定阈值 `50bps` 与过去 `100` 根样本绝对 premium 的 `95%` 分位，出场看三件事——压缩回 `10bps`、持仓超过 `60` bars、或继续恶化到 `200bps` 止损。也就是：**entry/exit/risk 都是明确写死的，不是“看到图觉得会回”。**
- 仓位不是固定一把梭。repo 会按偏离幅度放大仓位，但 capped 在 `25%` equity；如果当前 premium 是入场阈值的 2~3 倍，才放更大。这个设计很适合我们后续下沉到 `1m/3m/5m`：**edge 出现在极端时，就别对普通级别错位给同样仓位。**
- 真正值得借的不是作者那组回测收益，而是研究姿势：**把 basis 拆成“mark/oracle 偏离”而不是笼统“资金费/期现价差”**。这让它天然更适合超短线，因为 oracle 锚点和偏离修复本身就是分钟级、甚至秒级现象。

## 3. 为什么和当前项目有关
`momentum` 这边最近已经积累了不少 trend / cross-sectional / pairs / funding / basis 素材，但 **mark-vs-oracle 这种更贴近撮合层的 relative-value raw alpha 还不够多**。这条线的价值在于：
- 它是可独立成立的 raw alpha，不需要先依附某条趋势主线；
- 它能直接补 desk 的 `stat-arb / relative value / execution-aware` 素材池；
- 就算最终不单独上线，也很适合给 funding/basis/carry 体系当 execution veto：**当 mark 已经离 oracle 太远时，不要追单；等错位修回后再做。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 均值回复
- 基础 alpha：perp mark 与 oracle 的极端偏离回归
- regime：薄深度、短时冲击、单边扫盘后更容易出现；深度恢复、价差重新锚定后 edge 变弱
- filter / veto：只做绝对 premium 超过固定阈值且超过滚动高分位的极端事件
- risk / sizing / execution overlay：按偏离幅度缩放仓位、设置最大持有时长、继续恶化即止损；实盘上应优先 maker-first / 分批平仓

## 4. 可复刻的最小实验
- 研究假设：`1m` 或 `3m` 上，Hyperliquid perp 的 `mark-oracle premium` 一旦进入滚动极端区间，未来 `3~20` 根 bar 的 signed return 会向 oracle 方向回归。
- 可计算定义：
  - `premium_bps = (mark_price - oracle_price) / oracle_price * 10000`
  - 当 `abs(premium_bps) > max(30~50bps, rolling_q95(abs(premium_bps), 96~288 bars))` 时开仓；
  - `premium_bps > 0` 做空，`premium_bps < 0` 做多；
  - 出场看 `abs(premium_bps) < 5~10bps`、`max_hold=5/10/20 bars`、或继续扩大到 `1.5~2x` 入场阈值。
- 最小回测切口：先跑 Hyperliquid 上最液体的 `BTC / ETH / SOL`，周期优先 `1m` 与 `3m`，再映射到 `5m/15m` 做更保守版本；样本先拿最近 `60~90d`。
- 最该先看：`net bps/trade`、`median holding bars`；其次看 `positive-event ratio` 与 `cost-to-edge ratio`。

## 5. 风险与保留意见
- 当前 repo 先用 `1h` 数据讲故事，这对真正的短时 dislocation 来说偏粗；如果下沉到 `1m`，结果很可能比 README 更难看，也更诚实。
- 这条 alpha 对执行很敏感。错位修复通常发生得快，若 taker fee + slippage 太高，edge 会被迅速吃掉。
- oracle 本身不是神谕真值，只是更平滑的锚。极端事件里，mark 偏离也可能反映真实信息，而不只是噪音；所以必须保留 time-stop 和 widening-stop。
- Hyperliquid 有平台特定性。能不能迁移到 Binance/Bybit/OKX，要看是否能拿到足够可靠的 mark/index/oracle 口径，而不是默认可移植。

## 6. 来源
- Andrea Ambrosio. (2026). *hype-backtesting*. GitHub.
  - Repo URL: `https://github.com/andreaambrosio/hype-backtesting`
  - README: `https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/README.md`
  - Strategy code: `https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/src/strategies/basis_reversion.py`
  - Backtest runner: `https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/run_backtest.py`
