# Rank 205 / par-local-drift crossover intake → keep_P1

- Time: 2026-03-27 23:29 UTC
- Target: `research/quant_digests/2026-03-27_1424_par-local-drift-crossover-alpha.md`
- Action type: fresh intake
- Verdict: `keep_P1`
- Assigned rank: `Rank 205`

## 本轮要回答的问题
这条 2023 AIMS PAR local-drift crossover 线，是否足够独立、可 desk 化，值得作为一个新的单币方向性母策略留在前排继续做一次便宜而决定性的 follow-up；还是它只是已有 trend/breakout 线的复杂换壳。

## 读后结论
结论是：**值得保留，但先只保留到 `P1`。**

它留下来的核心不是“多项式自回归”这个实现细节，而是：

> **价格相对 rolling local drift / prediction line 的 buffered crossover，会触发一段可延续的单币 directional move；持仓直到反向 crossover 再 flip。**

这和当前前排的几条主线不同：
- 不是横截面 short-horizon reversal；
- 不是 pairs mean-reversion；
- 不是 carry / calendar / clock pocket；
- 也不等同于简单前高前低 breakout。

它更像一条 **single-asset local-drift continuation / crossover** 母线，具备独立入池价值。

## 为什么先不给更高层级
目前还不够直接升 `P2`，主要因为缺三件关键事：
1. **成本诚实性不足**：论文没有把手续费/滑点/执行方式建模清楚；
2. **基线归因未做干净**：还没回答它相对 `EMA crossover / Donchian / plain return-sign continuation` 到底新增了多少 alpha；
3. **参数/资产泛化仍偏弱**：论文只覆盖 4 个主流币，窗口和 buffer 有明显 per-asset tuning 痕迹。

所以现在最诚实的层级不是 `P2 admission`，而是：
- 先承认它是一个**可独立存在的 raw alpha skeleton**；
- 再给它 **1 次 survivor follow-up**，只回答“它到底是不是比简单 trend baseline 更有新增信息”这个唯一关键问题。

## 本轮改变系统认知的一句话
**Rank 205：这条线保留下来的不是 paper 里的 PAR 包装，而是“rolling local drift / prediction line 的 buffered crossover + opposite-flip”这条可独立交易的单币方向性母策略；它不同于当前 front chain，足以正式记 `keep_P1`，但在完成与简单 trend baseline 的同窗长同成本对照前还不够升 `P2`。**

## 唯一应该做的下一步（供 bot2 排 survivor 用）
只做一次便宜 follow-up：
- 在 `BTC/ETH` 的 `1m`（可加 `5m` 压缩版）上，
- 用统一成本口径，
- 把 `rolling polynomial/local-drift line + buffered crossover + opposite flip`
  与 `EMA crossover`、`Donchian breakout`、`N-bar sign continuation` 放到同一框架对照。

若它在至少一个主币 / 一个 bar 级别下仍表现出**成本后不差于 baseline 且具更稳的 long/short 非对称性或更低 whipsaw**，再考虑升 `P2`；否则应诚实移回 background。
