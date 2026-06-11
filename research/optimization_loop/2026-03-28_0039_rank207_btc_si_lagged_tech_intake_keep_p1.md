# Rank 207 / BTC SI lagged-tech continuation intake → keep_P1

- Time: 2026-03-28 00:39 UTC
- Target: `research/quant_digests/2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`
- Action type: fresh intake
- Verdict: `keep_P1`
- Assigned rank: `Rank 207`

## 本轮要回答的问题
这条 2024 Bitcoin minute SI 论文衍生出来的 `lagged tech bundle + 高阈值 abstain` 线，是否足够独立、可 desk 化，值得作为新的单币方向 raw alpha 母线保留；还是它只是又一条 next-minute sign 薄 edge 叙事，连最小前排资格都不该拿。

## 读后结论
结论是：**值得保留，但先只保留到 `P1`。**

它真正留下来的，不是论文 headline 里的 `80%+` next-minute 准确率，也不是必须完整复刻 `BiLSTM + CNN + voting classifier`；而是更可 desk 化的这一层：

> **用 BTC `1m` 的 lagged technical bundle 先打一个方向分数，只在高置信度时出手，把目标从 `next 1m sign` 改成后续 `3m/5m continuation`。**

这条线与当前 front chain 不同：
- 不是 `Rank 203` 那种 pairs / pair-book mean-reversion；
- 不是 `Rank 205` 那种单币 local-drift crossover；
- 也不是 `Rank 206` 那种横截面技术复合趋势分数。

它更像一条 **BTC-only、score-first、abstain-heavy 的短延续方向母线**，因此值得正式保留为新的研究对象。

## 为什么现在还不给更高层级
当前 digest 和快检已经足以说明“不是完全没东西”，但还远远不到 `P2`：

1. **next-minute 本体不够用**  
   最小 transfer check 下，`1m -> next 1m sign` 的 OOS accuracy 只有 `50.21%`，`p>=0.55` 时 mean 甚至是 `-0.02 bp/trade`，`p>=0.60` 只有 `51` 笔，mean `-1.34 bp/trade`。这说明 paper headline 不能直接当 desk 交易结论。

2. **真正留下来的 pocket 很薄，只像高阈值 continuation 原胚**  
   `3m` horizon 在 `p>=0.55` / `0.60` 下分别只有 `+0.11 / +0.21 bp/trade`；`5m` horizon 才稍微像样，`p>=0.55` 为 `+0.48 bp/trade`，`p>=0.60` 为 `+1.20 bp/trade`，但 coverage 只剩 `2.9%`。这更像“也许只在 very-low-cost / maker / 稀疏 pocket 里活”的原型，而不是已通过 admission 的独立策略。

3. **仍未完成 exact-feature / cost / execution honesty**  
   当前只做了 easy-to-compute paper-style technical bundle + `lag 0/1/3` 的 Logit proxy，不是完整论文复刻；同时还缺 `0/1/2/4 bps` 成本梯度、maker-vs-taker 分层、以及“预测超过 fee floor 的 move”这种更诚实的 target 定义。

所以此刻最诚实的层级是：
- 先承认这是一条 **可独立存在的单币 directional raw alpha skeleton**；
- 但只记 `keep_P1`，还不能升 `P2`。

## 本轮改变系统认知的一句话
**Rank 207：这条线真正值得保留的不是论文里的 next-minute 高准确率叙事，而是“BTC 1m lagged-tech score + 高阈值 abstain → 3m/5m continuation”这条单币方向母线；它与当前 front chain 不同，正式记 `keep_P1`，但在完成 exact-feature replication 与成本梯度下的 maker/taker 生存线前还不够升 `P2`。**

## 唯一应该做的下一步（供 bot2 排 survivor 用）
只做一次便宜而 decisive 的 follow-up：
- 完整补齐论文里最关键、当前 proxy 没带上的 exact features；
- 把 target 从 plain sign 改成 `future 5m return > fee_floor`；
- 在同一 BTC `1m` 数据上做 `0/1/2/4 bps` 成本梯度与 maker/taker 分层；
- 只回答一个问题：
  **这条 `1m score -> 5m continuation` 在高阈值 abstain 后，是否还能留下足以区别于 plain lagged-return / plain tech regression baseline 的可交易 pocket。**

若答案是 yes，再考虑升 `P2`；若只是把薄 gross edge 重新包装，则应诚实移回 background。
