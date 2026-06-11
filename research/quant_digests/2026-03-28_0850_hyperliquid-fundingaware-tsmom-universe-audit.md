# 别把这份 Hyperliquid TSMOM repo 只当传统 trend bot：更值得先测的是「多窗口 TSMOM × funding 惩罚 × edge gate」完整 raw alpha，但必须先修 universe/OI 口径
- 时间：2026-03-28 08:50 UTC
- 类型：2025 GitHub 仓库 + 源码审阅 + Hyperliquid 公共 API live snapshot
- 主题类型：raw alpha
- 基础 alpha：多窗口 time-series momentum（每个币看最近多段收益 z-score，正则做多、负则做空）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / time-series / perpetual / hyperliquid / funding / inverse-vol / vol-target / execution / cost
- 证据类型：工程经验 + 仓库代码证据 + 公共数据快照

## 1. 这次看了什么
看的是 Gajesh2007 的 GitHub 仓库 `momentum-trading`（创建 2025-10-03，最近 push 2025-10-14，9 stars），以及其 `signals/engine.py`、`risk/engine.py`、`data/loader.py`、`config/*.yaml`。这不是单纯“追涨 bot”，而是一个已经把 `signal / funding / sizing / liquidity cap / cost gate / execution` 串起来的 perp TSMOM 骨架。

Repo URL: https://github.com/Gajesh2007/momentum-trading

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：`s_raw = mean(zscore(多窗口收益))`，然后按符号做多/做空，是标准但可落地的 raw alpha，不是纯 filter。
- 仓库最值钱的不是“再证明趋势有效”，而是把 short desk 真正关心的几层都接上了：方向性 funding 惩罚、`w ~ s_adj / sigma`、组合年化波动目标 15%、单币上限 5%、`edge >= 2.5x~3x friction`、ATR 止损、ALO/TWAP/Market 三套执行。
- repo 自带两个可直接迁移的快实验模板：`1h` 版用 `[6,24,72]` 小时 lookback；`4h` 版想做更慢的 swing。但对我们 desk，更应该先把它 desk 化成 `15m` 的多窗口 TSMOM，再测 funding penalty 是否真能在成本后留下净边。
- 代码里有两个必须先修的口径问题。第一，`get_universe()` 直接拿 `openInterest >= 5,000,000` 过滤，但 Hyperliquid 的 `openInterest` 是币本位数量，不是 USD；我用公共 API 现场快照看到：按 repo 原写法只剩 6 个币过阈值，而把 `OI` 先乘 `midPx` 转成 USD 后会变成 12 个，并把 BTC / ETH / SOL 拉回 universe。第二，`4h_swing.yaml` 里 `lookbacks: [24,96,240]` 的注释写成 `24h/4d/10d`，但代码按“bar 数”解释，实际对应的是 `4d/16d/40d`；不修这个，复现实验会以为自己在测 4h alpha，其实测得更慢。

## 3. 为什么和当前项目有关
它和 `momentum` 当前阶段非常贴：不是继续围绕 breakout 形态内循环，而是补一条能直接进素材池的完整 raw alpha。更重要的是，它把 `raw alpha / funding overlay / risk sizing / execution cost` 的边界拆得很清楚，适合作为后续把趋势、carry、执行层分开评估的母版。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：多窗口收益 z-score 的 time-series momentum
- regime：高流动性 perp universe；优先在 funding 不极端、交易成本可控时启用
- filter / veto：方向性 funding penalty；`edge >= 2.5x~3x friction`；流动性/OI 过滤
- risk / sizing / execution overlay：inverse-vol sizing、组合 vol target、单币 cap、ATR stop、maker-first ALO、超大单 TWAP、kill switch

## 4. 可复刻的最小实验
- 研究假设：在 `15m` perp 上，`多窗口 TSMOM + directional funding penalty + edge gate` 会比裸 `TSMOM` 有更好的成本后收益/换手比。
- 数据：Hyperliquid 或 Binance 永续 `15m` K 线 + 小时 funding（公开 API 可拿）；universe 先用 `dayNtlVlm >= 10M` 且 `OI_USD >= 5M`，不要直接复用 repo 的原始 OI 过滤。
- 信号：先做 faithful transfer：把 repo `1h` 的 `[6,24,72]` 小时 lookback 改成 `15m` 的 `[24,96,288]` bars；`s_raw` 为三段收益 rolling z-score 平均，`s_adj` 再扣同方向 funding。
- 交易：每 15 分钟收盘后再平衡；`w_raw = s_adj / sigma`，再做 vol target；若 `edge < 2.5 x (fee + slippage)` 则跳过；sign flip 或 ATR(14)*2 止损出场。
- 对照组至少做 4 个：`裸 TSMOM` / `+ funding penalty` / `+ edge gate` / `+ universe 修正`。先看 `post-cost return、turnover、positive-asset ratio、max drawdown`，不要先卷参数。

## 5. 风险与提醒
- 这个 repo 目前更像“完整骨架”而不是已验证 alpha；没有公开、可信的长期实盘绩效。
- funding 用的是 predicted funding，实盘要区分“预测值”和“真正收付值”。
- Hyperliquid 当前按 repo 默认阈值 universe 太窄，若直接照搬，最后可能只是在几只 meme/perp 上做集中押注。
- 若落到 `5m/15m`，maker 占比和滑点模型会比 repo README 里写得更关键。

## 6. 来源
- Gajesh (2025), Momentum Trading Strategy w/ HyperLiquid on EigenCompute, GitHub repo: https://github.com/Gajesh2007/momentum-trading
- 仓库关键文件：`momentum_trading/signals/engine.py`、`momentum_trading/risk/engine.py`、`momentum_trading/data/loader.py`、`config/test_fast.yaml`、`config/4h_swing.yaml`
- Moskowitz, Ooi, Pedersen (2012), Time Series Momentum, Journal of Financial Economics, DOI: https://doi.org/10.1016/j.jfineco.2011.11.003 , Readable URL: https://docs.lhpedersen.com/TimeSeriesMomentum.pdf
- Park et al. (2025), Designing funding rates for perpetual futures in cryptocurrency markets, arXiv, DOI: https://doi.org/10.48550/arXiv.2506.08573 , Readable URL: https://arxiv.org/abs/2506.08573
