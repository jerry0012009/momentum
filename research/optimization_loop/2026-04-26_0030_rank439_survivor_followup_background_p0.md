# Rank 439 / smooth-path attention-lag continuation router — survivor follow-up to background/P0

- Time: 2026-04-26 00:30 UTC
- Target: `Rank 439 / same-window cumulative return × smooth-path continuation / jump-path exhaustion router`
- Step type: `survivor follow-up`
- Verdict: `background/P0`

## What I checked
按 state 要求，只做唯一一次最小 portability / honesty 检查：
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 数据：Binance perpetual public `15m` klines，各 `1000` 根
- 观察窗：过去 `8` 根 `15m`
- 持有窗：未来 `2` / `4` 根
- 控制方式：先按过去 `8` 根的 `abs(cumret)` 与 realized vol (`sqrt(sum(r^2))`) 分成联合 bucket，再在每个 bucket 内比较 `path efficiency` 最高三分之一（smooth）与最低三分之一（jump）
- 检查口径：看“顺着过去方向的未来收益”（aligned continuation）是否 smooth 显著优于 jump

## Core result
控制 move size 与 realized vol 后，`smooth path` **没有**在 majors 上保留出稳定的 continuation 优势；相反，pooled 结果中 smooth 组的 aligned continuation 均值还略差于 jump 组：

- pooled future `2` bars：smooth `-2.70 bps` vs jump `-0.93 bps`，差值 `-1.77 bps`
- pooled future `4` bars：smooth `-3.57 bps` vs jump `-2.37 bps`，差值 `-1.19 bps`

分资产看也不支持“可迁移的 smooth continuation / jump exhaustion router”主语：
- `BTC`：只有 `4-bar` 正向 continuation 的多头半边略有改善，但空头半边与 `2-bar` 不一致
- `ETH`：结果接近噪声，long/short 与 `2/4-bar` 方向不稳
- `SOL`：多头半边反而更像 `jump > smooth`

## Why this changes system belief
Rank 439 在 fresh intake 阶段还能成立，是因为它把 attention 机制压缩成了一个便宜可测的价格路径主语；但 survivor 这一步的唯一 blocker 就是：

> `path smoothness` 是否独立于单纯 vol / noise proxy，并且能在 majors 上形成最小 portability。

这一步现在已经得到否定答案。至少在最便宜、最诚实的 majors / 15m / control-for-move-size-and-vol 口径下，它没有留下稳定的、值得继续升级到 `P2` 的 continuation-vs-exhaustion 分流。既然 survivor 预算只有这一次，就不应再把它留在前排继续找解释。

## Runtime consequence
- `Rank 439` 用完 survivor 唯一 follow-up 预算。
- 结论收口为 `background/P0`，不升 `P2`。
- `Surviving candidate slot` 应释放为 `none`。
- 本轮只完成当前 front-slot 小点，不改写后续排班顺序。 
