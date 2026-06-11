# Rank 314 — ORCA tradability-aware cluster pairs survivor follow-up: promote_P2

- 时间：2026-04-03 18:08 UTC
- 对象：`Rank 314 / ORCA tradability-aware cluster pairs`
- 执行动作：survivor 唯一一次 follow-up
- 结论：`promote_P2`

## 这一步回答的问题
在统一 execution shell 下，`top tradability-score pairs` 相比 `top-corr pairs`，是否已经不只是“方法论上更像可交易 spread”，而是在 desk 口径里也能形成可复现的净后改进？

本轮结论：**是，够资格升到 `P2`。**

## 本轮执行壳
- 数据：本地已有 Binance perp `30d` 缓存
- 统一宇宙：只保留同时具备完整 `5m/15m` 历史的 8 个标的：`ADA/AVAX/BNB/BTC/DOGE/ETH/LTC/SUI`
- 候选 pairs：上述宇宙内、来自 `2026-04-03_orca_pairs_sanity.csv` 的 28 个 pair
- walk-forward：
  - `5m`: `15d train + 5d test`，2 个窗口
  - `15m`: `10d train + 5d test`，4 个窗口
- 统一交易壳：train 期估 `beta + half-life`；test 期用固定阈值 spread MR shell（entry `|z|>=2`、exit `|z|<=0.5`、stop `|z|>=3.5`、max hold `min(2*half-life, window cap)`）
- 固定 roundtrip 成本：`5m = 8bps`，`15m = 6bps`

## 核心结果
见 artifact：`reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/summary.csv`

### 5m
- `top_corr`: net return `0.186484`，`14` turns，`133.203 bps/turn`，avg hold `177.55` bars，stop-hit `0.0`
- `top_tradability`: net return `0.277151`，`28` turns，`98.982 bps/turn`，avg hold `99.975` bars，stop-hit `0.0`

解释：`tradability-score` 在 `5m` 上把累计净后回报抬高了约 `+48.6%`，同时把平均持有缩短约 `43.7%`；虽然单笔 `pnl/turn` 低于 `top_corr`，但 turnover 更健康，累计净后更高。

### 15m
- `top_corr`: net return `0.244820`，`24` turns，`102.008 bps/turn`，avg hold `49.962` bars，stop-hit `0.0`
- `top_tradability`: net return `0.294181`，`37` turns，`79.508 bps/turn`，avg hold `34.667` bars，stop-hit `0.027`

解释：`tradability-score` 在 `15m` 上也维持正向净后优势，累计净后约高 `+20.2%`，平均持有缩短约 `30.6%`；代价是单笔效率略降，并引入极少量 stop-hit。

## 为什么这不是单一 pair / 单一窗口偶然
`pair_selection_windows.csv` 显示，`top_tradability` 的入选 pair 在多个窗口里发生变化，但收益并不是由单一 pair 独占：
- `5m` 两个窗口的 tradability 组合几乎完全不同（Jaccard `0.1111`），但两窗都能维持比 `top_corr` 更高的累计净后；
- `15m` 四个窗口里，tradability 组合持续在 `AVAX/SUI`、`BTC/AVAX`、`ETH/LTC`、`BNB/SUI`、`ADA/LTC` 等不同 pair 间轮换，仍然整体跑出更高累计净后；
- 相反，`top_corr` 组合高度集中在 `BTC-ETH / ETH-BNB / BTC-BNB` 这些 classic majors，pair book 更稳定，但净后累计回报反而较低。

所以这条线的有效性，不是“某一个神 pair 特别能打”，而是：

> 把 pair admission 从“谁最相关”改写成“谁更容易形成更快、更可反复兑现的 spread 回归”，确实改变了 book 的净后表现结构。

## 这一步的诚实保留
这次升 `P2`，不是说它已经 ready 进 `P3`。当前仍有两个明显缺口：
1. `top_tradability` 的 **pair replacement stability 明显更差**：
   - `5m` Jaccard `0.1111` vs `top_corr` `0.6667`
   - `15m` Jaccard `0.1799` vs `top_corr` `0.5873`
   这说明 admission layer 更像“高轮换 alpha book”，而不是稳定白名单。
2. 单笔 `pnl/turn` 仍低于 classic `top_corr`，优势主要来自 **更快周转 + 更高累计净后**，因此下一步必须验证 turnover / slippage / replacement friction 是否会吃掉这层优势。

## P2 应该怎么继续
下一轮 `P2` 不该再问“它是不是 distinct idea”，而该问：
- 优势是否能在更诚实的 pair replacement / refresh cadence 下保住；
- admission score 是否该加上更强的 stability / turnover penalty；
- `tradability-score` 的增益究竟来自 faster half-life、crossing density，还是某类 alt-heavy pocket 的条件化暴露。

## 对 runtime 的影响
- `Rank 314` 从 `Surviving candidate slot` 升入 `Active P2`
- survivor follow-up 预算用尽
- 当前系统认知改写为：`tradability-aware / OU-like pair admission` 已经在统一 `5m/15m` 固定成本 walk-forward 壳下，对 classic `top-corr` pair admission 形成可复现净后优势，但伴随更高 pair replacement churn，因此进入 `P2` 做 admission-layer honesty / turnover-friction exit work

## 一句话 result
`Rank 314` 的 survivor 唯一一次 follow-up 已经把命题从“高相关不等于可交易”推进到 desk 口径：在统一 `5m/15m`、固定成本、walk-forward 壳下，`top tradability-score pairs` 相比 `top-corr pairs` 持续跑出更高累计净后回报与更短持有期，因此本轮应直接 `promote_P2`，而不是继续停留在 `P1`。
