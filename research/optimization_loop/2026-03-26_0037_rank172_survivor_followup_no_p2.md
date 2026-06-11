# Rank 172 / MBSA Markowitz basket raw alpha — survivor 唯一 follow-up 收口

- 时间：2026-03-26 00:37 UTC
- 执行角色：bot3
- 依据：`docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan` 第 1 项 —— 对 `Rank 172 / MBSA Markowitz basket raw alpha` 做 survivor 唯一一次 decisive follow-up，只回答“把候选 spread 家族喂入 top-N Markowitz 篮子后，在更慢再平衡与更真实 friction ladder 下，是否仍保留足以进入 P2 的可复制净边”

## 本轮补了什么
这轮没有再重复论文 headline，也没有直接开放式续写 `keep_P1`，而是补了两类和 admission 最相关的执行现实证据：

1. **读取上一轮 intake 的 Binance `15m` proxy 结果**：
   - `top-2 + Markowitz-smoothed + 4h rebalance` 在 **0 bps** 下约 `+9.30% / Sharpe 2.61`
   - 到 **2 bps** 时只剩 **`-0.21% / Sharpe 0.03`**，基本已经贴地
   - 到 **4 bps** 时变成 **`-8.89% / Sharpe -2.54`**，明确失效
2. **对现有 `spread_weights_markowitz.csv` 做组合层换手诊断**（新产物：`mbsa-markowitz-basket-probe_20260326_0037_weight_diagnostics.json`）：
   - 平均活跃 spread 数约 **1.50**，活跃 bar 占比 **82.0%**
   - 平均每个 `15m` bar turnover 约 **0.0766**
   - 真正发生再平衡时，平均 turnover 约 **1.39**，中位数约 **1.09**，最大到 **2.00**
   - 主导 spread 在再平衡点上的切换率约 **77.8%**

## 结论怎么读
这组 follow-up 已经足够回答 survivor 问题：

**Rank 172 当前保留下来的只是“多条 spread 需要 cost-aware 篮子管理”这个研究骨架，但还没证明存在一个在更真实 crypto 执行摩擦下可复制、可部署的 moving-band spread family edge，因此不升 `P2`。**

更直白一点：
- 这条线不是完全没东西；Markowitz 篮子层相对 naive equal-weight 确实有改善。
- 但改善幅度太薄，薄到在当前 proxy 下 **2 bps 只剩近似打平、4 bps 直接穿透为负**。
- 更关键的是，组合并没有呈现“少数稳定 spread 被低频持有”的形态，而是呈现 **高活跃率 + 再平衡时大幅换仓 + 主导 spread 高频切换** 的形态；这更像一个**对执行摩擦极敏感的研究原型**，而不是已经足够诚实进入 `P2 admission` 的候选。

## 为什么不是 promote_P2
按 policy，survivor 唯一 follow-up 要回答的是“更慢再平衡与更真实 friction 下还有没有足够净边”。本轮答案是否定的，原因有三：

1. **更真实 friction 口径不够过关**：`4h rebalance` 已经不是很快，但 `2 bps` 只剩贴地，`4 bps` 明确失效。
2. **edge 主要还停留在组合层修饰，不是可复用 spread family 的厚净边**：提升主要体现为“比 naive 少亏一点”，不是“留下明确可部署净收益”。
3. **执行画像不诚实**：高 active 占比 + 再平衡点高 turnover + 主导 spread 高频切换，说明它仍依赖较频繁的持仓替换；这与“先找到一组稳健 moving-band family，再用 Markowitz 做低频管理”的 deployable 叙事并不一致。

## 本轮 verdict
**Rank 172 / MBSA Markowitz basket raw alpha：survivor follow-up 完成，不升 `P2`，退出前排并回到 background pool；当前证据只支持把它保留为“stat-arb spread family 的 cost-aware basket 管理骨架”，不支持把它当成已具备可部署净边的 P2 候选。**

## 回写对象
- `Surviving candidate slot`：清空
- `Background pool`：新增最新 parked 为 `Rank 172`
- `cycle_plan[1]`：写入 result + `done`

## 新产物
- `reports/artifacts/quant_digests/mbsa-markowitz-basket-probe_20260326_0037_weight_diagnostics.json`
