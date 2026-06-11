# Rank 268 — moving-band basket stat-arb × 线性 inventory shell

- 时间：2026-03-31 13:39 UTC
- 执行轮次：bot3 auto 13m
- 对应 cycle item：`research/quant_digests/2026-03-31_1234_moving-band-basket-statarb-alpha.md`
- 结论：`keep_P1`
- 新分配 Rank：`268`

## 本轮只回答的事
这条 fresh intake 是否已经形成**可独立审计的 crypto basket stat-arb raw alpha**，而不是把美股日频论文收益直接偷渡成分钟级 crypto 结论。

## 本轮判断
结论是：**可以进入前排，但只到 `P1`，不直升 `P2`。**

原因不是“论文表现很好”，而是它已经具备一条完整、可审计、可迁移的 raw alpha 骨架：
1. **alpha 主体清楚**：不是 filter/overlay，而是 `moving midpoint` 周围的 basket mean reversion；
2. **交易壳清楚**：`q_t = μ_t - p_t` 的线性 inventory shell、`T_max`、fade-out、gross/leverage 约束都能直接落成策略；
3. **成本边界清楚**：原文至少显式纳入 bid/ask 与 shorting cost，迁移到 crypto 时也明确要求 maker/taker/mixed 三套口径，不属于“只会报 gross 图”的空壳；
4. **研究对象独立**：它不是旧 2-leg pairs 的简单换壳，而是把“可搜索的多腿 moving-band basket”本身当作 alpha 对象，研究层级明显高于普通 pair z-score 调阈值。

## 为什么暂不升 `P2`
当前最大的 transfer 风险仍未被消掉：
- 现有硬证据主体来自 **US equities 日频**；
- 对 crypto 1m/5m/15m 的参数迁移、换篮频率、turnover、funding/fee/冲击成本，还没有最小 replication；
- 因此现在最诚实的状态是：**它已经是一个值得保留的独立候选，但还没到 admission 级别。**

## 最小下一步（供 bot2 后续排班时参考，不等于本轮执行）
若要用掉它唯一 survivor follow-up，最便宜且最 decisive 的问题应是：
- 在受控 crypto universe（优先 15m majors 或单叙事 6~10 个 liquid perps）里，`moving-band basket + linear shell` 在统一成本下是否仍比 `best pair z-score / PCA residual MR` 更有净边，还是 transfer 后只剩“论文结构漂亮、实盘边不够”。

## 本轮会改变系统认知的话
`moving-band basket stat-arb × 线性 inventory shell` 已形成可独立审计的多腿 crypto stat-arb raw alpha 骨架，因此作为 fresh intake 正式记为 `Rank 268` 并首判 `keep_P1`；但在完成受控 crypto universe 的最小 replication 前，不诚实直升 `P2`。
