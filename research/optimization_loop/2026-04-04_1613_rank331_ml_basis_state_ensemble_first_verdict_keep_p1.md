# Rank 331 / ml-basis-state-ensemble-alpha — fresh intake first verdict (`keep_P1`)

- Time: 2026-04-04 16:13 UTC
- Target: `research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
- Action: 对这条 `spot-perp basis state × funding-pressure × delta-neutral flip` fresh intake 做 first verdict
- Verdict: `keep_P1`
- Rank assigned: `331`

## 为什么这轮能诚实给 `keep_P1`
这条对象的主语已经足够独立清楚，不是“ML ensemble 很厉害”这种空叙事，而是：

> 用 `basis level / z-score / basis momentum / funding pressure / ETH cross-basis` 等状态变量去预测未来几小时 basis drift / reversion，再切换 `long basis = long perp + short spot` 或 `short basis = short perp + long spot` 的 delta-neutral 头寸。

对本轮 first verdict 来说，它已经满足了 `keep_P1` 所需的最小壳：

1. **basis state definition 已明确**  
   digest 已把 `basis / basis_zscore / basis_change / funding_pressure / eth_basis / ethbtc_ratio` 这些核心状态变量拆清楚，说明这条东西不是单纯 carry，也不是机械 z-score MR。

2. **long-basis vs short-basis switch 已明确**  
   对象明确区分：预测未来 basis 上行时做 `long basis`，预测未来 basis 下行时做 `short basis`；核心收益来源是 basis widening / convergence 本身，而不是裸方向暴露。

3. **entry / exit / sizing / cost shell 已成型**  
   digest 已把 repo 中的 `conviction threshold / exit threshold / 12h max hold / 5% drawdown stop / fee+slippage` 提炼出来，并给出 desk 版最小迁移壳：`15m discovery + 5m execution`、固定美元 notional、双腿成本、funding shock / basis gap / liquidity veto。

4. **sign-audit risk 已被明确暴露，不是被忽略**  
   这条对象最大的风险点也已经被诚实指出：根目录 `main.py` 与 `robbie/main.py` 在交易方向实现上不一致，存在 canonical sign 定义写反的可能。它是明确 blocker，但不是“对象主语不存在”；更像 survivor follow-up 里必须先做的第一道 clean-room 审计。

## 为什么现在还不能直接升 `P2`
虽然它已经是合格的 raw-alpha 候选，但当前证据仍停在 source audit / shell reconstruction，尚未完成最小 replication：

- 还没有 `15m` clean-room sign audit；
- 还没有 `basis-only` vs `basis+funding` 的最小增量检验；
- 还没有成本后方向准确率 / post-cost edge 的第一轮 desk 读数。

所以这一步最诚实的结论是：

> **它值得保留为正式 `P1` survivor，但还不到直接升 `P2` 的程度。**

## 唯一 follow-up 应该做什么
按 policy，这条 survivor 只配拿 **1 次** 最小 decisive follow-up。最有杠杆的下一步不是继续泛泛补论文，而是：

1. 选定 `robbie/` 版本为 canonical shell 候选；
2. 对 `root main.py` vs `robbie/main.py` 做 `long basis / short basis / target label / PnL sign / funding cashflow` 的 clean-room sign audit；
3. 在 `15m discovery` 粒度上确认：这条线到底是在做 widening continuation、convergence MR，还是只是代码符号不一致导致的假 edge。

如果这一步通过，它才有资格进 `P2 admission`。

## Result sentence
`Rank 331`：`spot-perp basis state × funding-pressure × delta-neutral flip` 已具备独立 raw-alpha 主语、明确的 long/short basis 切换和最小 `15m discovery + 5m execution` 实验壳，因此本轮正式首判 `keep_P1` 并进入 `Surviving candidate slot`；当前唯一 decisive blocker 收敛为 canonical sign audit 尚未完成。

## Files touched
- `docs/BOT2_BOT3_STATE.md`
- `research/optimization_loop/2026-04-04_1613_rank331_ml_basis_state_ensemble_first_verdict_keep_p1.md`
