# Rank 314 — ORCA tradability-aware cluster pairs first verdict: keep_P1

- 时间：2026-04-03 17:30 UTC
- 对象：`research/quant_digests/2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
- 执行动作：fresh intake first verdict
- 结论：`keep_P1`
- 正式 Rank：`314`

## 这一步回答的问题
这条线是否只是又一篇 generic pairs / coint / z-score 方法论摘要，还是已经形成可单独 desk 化的 raw alpha 主语？

本轮结论：**可以独立成题，先留在 `P1`。**

## 为什么不是 generic pairs 换皮
本篇真正独立的主语，不是“spread 会回归均值”这件老事，而是：

> 把 `pair formation / pair admission` 从“高相关 / 高相似 / 先过 cointegration”改写成“更像 OU、half-life 更合适、crossing density 更够、残差更稳定”的 `tradability-aware admission layer`。

这和常见 generic pairs 线的最小可检验差异已经足够明确：
1. **研究对象不在 entry/exit 花活，而在 pair admission 目标函数本身**；
2. digest 给出了公开可复现的最小实验壳：Binance Futures 公共 `15m`、12 个主流 USDT perp、66 个 pair、训练/测试拆分、half-life + OOS zero-cross sanity check；
3. 本地 sanity check 已经给出清楚的 desk 启发：`corr > 0.88` 的 pair 不少，但同时满足较快 half-life 与足够 crossing 的 pair 很少，说明 **高相关排序和可交易排序不是一回事**。

## 为什么先不升 P2
虽然独立主语成立，但当前证据还停在 **“pair admission 值得单独研究”**，还没到 admission-ready：
- 目前本地快检主要证明的是 `high corr != tradable spread`；
- 还没有在统一交易壳下，直接把 `top-corr pairs` vs `top tradability-score pairs` 做成净后对照；
- 也还没有在项目固定的 `5m/15m`、固定成本口径、walk-forward 口径下给出 clean replication artifact。

所以这一步最诚实的结论不是 `P0`，也不是直接 `P2`，而是：
- **保留为 `keep_P1`**；
- 后续唯一 survivor follow-up 应聚焦在一件事：
  - 用统一 execution shell，直接比较 `top-corr` 与 `top tradability-score` 两套 pair admission，在 `5m/15m` + 固定成本下是否真的提升 `pnl/turn`、holding efficiency、stop-hit ratio、pair replacement frequency`。

## 对 runtime 的影响
- 分配正式 `Rank 314`
- `Fresh intake slot` 更新为本对象，first verdict = `keep_P1`
- `Surviving candidate slot` 切换为 `Rank 314`，并保留 1 次最小 follow-up 预算

## 一句话 result
`Rank 314` first verdict 完成：对象的独立主语成立于 `tradability-aware / OU-like pair admission`，且本地 `15m` sanity check 已给出与 generic top-corr pair mining 的最小可检验区分，因此先进入 `keep_P1`。
