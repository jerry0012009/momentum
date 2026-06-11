# 2026-04-07 13:42 UTC — fresh intake first verdict: ratio-band corr/vol pairs repo -> background

## 对象
- 来源：`research/quant_digests/2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md`
- 主题：`EMA-band ratio spread × corr/vol gate × 双腿对冲执行`
- repo：`dzenanh/crypto-derivative-trading-engine`

## 本轮要回答的问题
这条对象是否已经形成了**独立于既有 pairs / stat-arb 家族**的可迁移 raw alpha 壳，足以给出 `keep_P1`；还是本质上仍是老式 ratio-band pairs 教程的工程化复述，应直接回到 background。

## 结论
**本轮 first verdict：不进 P1，直接 `background / P0`。**

一句话版：这份 repo 的价值主要在于把 `ratio mean reversion + corr/vol gate + 双腿执行` 写成了可运行工程壳，但它没有压出独立于既有 pairs/stat-arb 家族的新 raw alpha 主语；核心仍是教科书式 ratio-band spread 回归的实现复述，而不是新的可迁移 pocket。

## 为什么这次不留在前排
### 1) alpha 主体并不新
源码主语非常直接：
- `asset1 / asset2` ratio spread 偏离 EMA / band 后做均值回归；
- 再加 `corr > 0.8` 与 `volatility > 0.001` 两个过滤器；
- 执行端做双腿开平与翻仓。

这能证明“它是完整策略壳”，但**不能证明它是新 alpha 家族**。`ratio-band MR + pair gate` 本身就是旧 pairs/stat-arb 的标准骨架，不足以单独占一个新的 survivor 名额。

### 2) gate 和执行层属于实现完善，不是独立 pocket
- `corr gate` 只是约束 pair 仍像 pair；
- `vol gate` 只是避免 spread 过死；
- `moneyAmount/2` 分腿、mark price 算数量、翻仓先平后开，都是合理执行细节。

这些让对象更“可跑”，但它们没有把 raw alpha 从旧 pairs 骨架里拉出来，更多是把老方法包装得更完整。

### 3) repo 自己也没有给出足以改写认知的 after-cost / cross-pair / time-stability 证据
当前证据仍停在：
- 2021 年旧市场结构；
- 默认 pair（`RSRUSDT/SXPUSDT`）案例；
- 没有严肃的手续费/滑点/翻仓损耗后审计；
- 没有证明这套壳在更广泛 pair 宇宙里形成稳定独立 pocket。

因此它更适合被当作**旧 pairs 家族的一个实现样本**，而不是当前前排要保留的“新对象”。

## 对系统认知的改变
- 这条 intake 不是“发现了新的 pairs raw alpha”；
- 它只是再次确认：`ratio MR` 家族常见的增补模块可以是 `corr gate + vol gate + 双腿执行`；
- 这类内容以后若再次出现，默认应优先并入现有 pairs/stat-arb 背景知识，而不是轻易占用前排 fresh/survivor 资源。

## runtime verdict
- verdict: `background / P0`
- rank: `none`（未达到 `keep_P1`，不分配正式 Rank）
- cycle impact: 当前 fresh intake 第一条对象已诚实收口，不进入 survivor / P2 / P3。
