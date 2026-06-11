# Rank 230 / return × relative-volume XS momentum — fresh intake 首判 keep_P1

- Time: 2026-03-28 23:36 UTC
- Target: `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `230`

## What changed
这条对象留下来的不是“再来一篇 generic XS momentum repo”，而是一个更具体、可 desk 化拆开的命题：**plain return ranking 之外，`return × relative-volume` 可能是一条独立的横截面动量特征家族；但在当前 desk 的短周期实现里，它还更像 feature / gate 候选，而不是已经能独立站住的 standalone alpha。**

## Why it is not P2 yet
1. digest 自带的更长 `Binance Spot 15m` extended transfer check 已经把最关键的现实约束说死：最佳 pocket（约 `k=24, maL=48, rebalance=16 bars`）只有 `+0.09 bps/bar` gross，扣 `4 bps` 后转成约 `-0.09 bps/bar`，`final equity` 约 `0.97x`；这离 admission-ready 的短周期独立 raw alpha 还差一截。
2. 这条线当前最强证据主要来自 **日频/周频 repo 语境**，而不是已经在 intraday / exchange-friction 口径里跑出可直接复用的净后 pocket；把 repo 的 OOS blend 或 weekly sleeve 直接当成当前 desk 可执行边界，会把 portfolio layer 和 alpha 本体混在一起。
3. 研究卫生本身虽然加分，但不是层级升级证据：`same-bar utopic -> lagged realistic` 从高 Sharpe 掉回普通可用，说明它是个诚实的研究对象；但“诚实”不等于“当前就足够强到升 P2”。
4. 当前 runtime 里已经有多个近邻 XS momentum 对象在前后排：`jump-veto` 线已进入 `connected_runner_live`，`Rank 229` 也在 `Active P2`；若没有一条明确的、会改变层级的新 decisive blocker/解除项，就不该把这条 rel-volume 线直接抬到 admission 前排。

## Why it still deserves keep_P1
1. 主题本体清楚且独立：它保留下来的核心不是周频 blend，而是 **`return × relative-volume` 这条可复用特征骨架**，和 plain XS momentum、jump-veto、inverse-vol、sentiment gate 都不是同一个东西。
2. digest 已经给出很具体的诚实下一步：不是继续在当前 `15m spot` 口袋上磨小数点，而是直接回答 **它到底是 standalone alpha，还是 plain XS momentum 的增强器 / 质量过滤器**。
3. 这条线有明确的唯一 follow-up 方向：去更适合保留净边的实现口径里，比较 `plain XS momentum`、`XS momentum × rel-volume gate`、以及 `XS momentum + rel-volume` 线性组合，直接看 rel-volume 是不是唯一值得保留的增量件。

## Minimal honest next follow-up
若进入 survivor，唯一一次便宜 follow-up 应直接回答：
- 在更贴近执行现实且更可能保住净后 edge 的口径里（优先 `top-liquidity perp/spot`, `4h/8h cadence`, 成本 `1/2/4/6 bps` ladder），`return × relative-volume` 到底能否以 **独立对象** 留下稳定正 pocket；
- 还是说它只能作为 **plain XS momentum 的 quality gate / second feature** 才有价值；
- 若后一种答案更像真的，就应把 survivor 结论写成“feature family 成立，但 standalone 不成立”，然后退出前排，不再硬抬 `P2`。

## Runtime implication
- 正式分配 `Rank 230`。
- 层级定性为 `P1`，**不直接升 `P2`**。
- 当前 `Surviving candidate slot` 为空，因此这条对象应成为新的 survivor，并保留 **1 次** 最小 decisive follow-up 预算。

## Result sentence
`Rank 230 / return × relative-volume XS momentum` fresh intake 完成并保留为 `keep_P1`：它留下来的是一条可复用的 `return × relative-volume` 横截面动量特征骨架，但当前更长的 Binance spot `15m` 检查显示最佳 pocket 也只是很薄 gross、扣 `4 bps` 后转负，因此它暂时更像 feature / gate 候选，不够直接升 `P2`。