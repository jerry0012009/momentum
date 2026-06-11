# Rank 262：percentile-entry cointegration spread mean reversion fresh intake 首判为 keep_P1
- 时间：2026-03-30 22:11 UTC
- 执行轮次：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`percentile-entry cointegration spread mean reversion`
- 结论：**`Rank 262 / percentile-entry cointegration spread mean reversion` 完成 fresh intake 首判：保留为 `keep_P1`，并锁定为当前唯一 survivor。**

## 为什么不是直接升 P2
这条 thesis/digest 已经给出完整且可复现的 pairs raw alpha 骨架：
- 主语清楚：`cointegration pair selection + percentile-entry + mean-cross exit` 的 crypto pairs spread MR；
- 骨架完整：有 `formation / trading / entry / exit / sizing / cost`；
- desk 迁移方向清楚：可直接落到 liquid universe、`3m/5m/15m`、并做 `±2σ vs percentile` 对照。

但它当前还缺一块决定是否进入 `P2 admission` 的最小关键信息：
- 论文 headline 主要建立在 **378 个可 short 小币现货/保证金 universe**；
- 对 desk 更关键的不是“论文总体有效”，而是 **把 universe 收缩到 liquid-major / desk-feasible pair 之后，这条 alpha 是否仍保留足够的触发密度与成本后边际**；
- 这意味着它已经超过“背景材料”，但还没到“可直接做 admission”的程度。

因此最诚实的首判不是 `drop`，也不是直接 `promote_P2`，而是：
**先记为 `keep_P1`，再用唯一一次 survivor follow-up 去回答 `liquid desk universe` 下的可承载性。**

## 本轮对系统认知的改变
`percentile-entry cointegration spread mean reversion` 不只是泛 pairs 综述；它已经构成一条独立、完整、可复现的 raw alpha skeleton，值得进入前排继续做一次便宜但 decisive 的 survivor follow-up。不过它的真正 admission 门槛不在论文是否完整，而在 `liquid-major / desk-feasible` 收缩后是否还保留足够 alpha 密度，因此本轮先定为 `keep_P1` 而非直接升 `P2`。

## 建议给 survivor follow-up 的唯一问题
优先直接回答这一句：
> 当 universe 从 thesis 的广泛小币样本收缩到 `Binance/OKX/Bybit` 可承载的 liquid pair，并补上基础 friction / max-hold 之后，`cointegration + percentile-entry + mean-cross exit` 是否仍保留可重复出现的成本后 MR 边际？

若答案是肯定的，则下一步应 `promote_P2`；若只在小币尾部样本里好看、换到 desk-feasible universe 后明显塌缩，则应在 survivor follow-up 后直接收口回 `background/P0`。
