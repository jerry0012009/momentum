# synthetic futures carry substitution fresh intake first verdict: background / P0

- Time: 2026-04-07 04:03 UTC
- Object: `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `background / P0`

## Why this changed system belief
这条对象**不是假策略**，但在当前 intake 口径下，它还不足以被当成一条独立于既有 funding / basis / curve carry 家族的新主语保留到 `P1`。

核心原因有三点：

1. **主语仍然是旧 carry 家族，不是新的 raw alpha 原语。**
   digest 自己已经承认它的关键零件来自 `funding differential`、`basis mean reversion`、`cross-venue funding differential`、`futures curve / calendar spread`。所谓 `synthetic future vs listed perp carry gap`，更像是把这些旧 carry 组件桥接成一个执行框架，而不是引入一个新的、此前未覆盖的错价主语。

2. **当前最像“desk packaging”，不像独立 alpha 分离。**
   repo 确实把 `entry / exit / sizing / risk / cost` 壳写得比较完整，也给了 `preferred long venues / preferred short venues` 这类 desk-friendly 默认腿结构；但这更说明它是一个可部署的 carry implementation shell，而不是证明“carry substitution”本身已经独立于旧 funding/basis 家族并产生新 edge。

3. **最关键的收益归因仍未被独立切开。**
   digest 明确承认：README 的高 Sharpe / 高收益是 `Phase 3` 整体书架结果，不是 `synthetic_futures.py` 单独 attribution。也就是说，当前并没有被压清的决定性证据证明：
   - 真正值钱的是 `cheap synthetic future vs expensive carry carrier` 这层替代价差，
   - 而不是旧有 `funding spread / basis reversion / calendar spread` 在组合框架里的再表述。

## First verdict
**结论：`background / P0`。**

这不是说以后永远不能 reopen，而是说按本轮 `fresh intake first verdict` 的标准，它还没有把“独立主语”压到足以占用前排：
- 可执行性强，成立；
- desk 化表达强，成立；
- 但**独立于既有 carry/basis 家族的新对象身份，不成立**。

因此本轮不分配新 Rank，不进入 `Surviving candidate slot`，直接回 `Background pool`。

## Slot consequence
- 不分配 Rank
- 不进入 `Surviving candidate slot`
- 作为旧 carry 家族的实现桥接证据保留在 `Background pool`

## What would be required to reopen later
如果以后要 reopen，这一条至少要补出一个当前没有的 decisive 证据：
- 独立 attribution：把 `synthetic carry substitution` 与普通 `funding differential / basis / calendar spread` 分开复算；
- 证明 after-cost 优势主要来自“替代载体错价”本身，而不是旧 carry 信号的组合收益；
- 或给出一个明确缩域版本（例如只在某个 venue pair / dated future lane 上）显示它是独立 pocket，而不是泛 carry 打包。
