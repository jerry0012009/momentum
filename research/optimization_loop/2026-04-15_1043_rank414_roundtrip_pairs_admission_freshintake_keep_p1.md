# Rank 414 fresh intake — roundtrip regime-stable pairs admission first verdict（keep_P1）

- 时间：2026-04-15 10:43 UTC
- 对象：`research/quant_digests/2026-04-15_0844_roundtrip-regimestable-pairs-admission.md`
- 本轮动作：按统一执行现实主义口径做 conditional fresh intake first verdict；重点检查该对象是否具备可迁移的费后稳健性线索，并锁定单一最小 honesty blocker。

## 执行与证据
- 复核源码（外部只读）：
  - `Pairs_Screening.py`（raw）显示该对象是 **pair admission filter**，核心权重为：`RT frequency(30) + beta smoothness(10) + WRS(20) + regime stability(25) + ADF(5)`；并非单纯相关性/ADF。
- 复核输出样本（外部只读）：
  - `pairs_screen_v5_top50.csv`（raw）前排 pair 普遍具备：
    - `RT_Annual_Freq` 约 `6.9~10.1`
    - `RT_Completion` 约 `0.55~0.66`
    - 多数 `Regime_Active=4/4`
  - 说明其 admission 排序确实优先“可反复完成 round-trip”的交易质量，不是只挑统计相似度。

## 最小 honesty 子检查（execution realism）
- 该仓给出的仍是 **daily 级筛选分**，没有直接产出统一 `t+2` 入场与 `4/6/8bps` 成本下的 post-cost PnL 证据；
- 因此本轮不把它误判成可直接上线策略，只把它保留为 `P1 admission-layer candidate`，等待唯一 follow-up 去验证“接入现有 15m pairs shell 后是否仍有费后增益”。

## first verdict
**结论：`keep_P1`，并分配正式 `Rank 414`。**

一句会改变系统认知的话：
> `Rank 414` 不是新的 pairs alpha 本体，而是值得保留的交易质量 admission 层：其 round-trip/regime 稳定性排序在源码与样本表中成立，但是否能在统一 `t+2 + 4/6/8bps` 的 15m 执行口径下产生费后增益仍需一次唯一 follow-up 决断。

## survivor 唯一 blocker（已锁定）
- 唯一 blocker：**把 `Rank 414` 接入现有 15m pairs shell 后，与 naive（相关性+ADF）在同一执行与成本口径下做 head-to-head，对比是否仍有稳定 post-cost uplift（至少在 OOS 口径不劣化）。**
